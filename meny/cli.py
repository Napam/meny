import argparse
import sys
from pathlib import Path
from .menu import menu
from .menylogger import getLogger, INFO
from .utils import _get_module_cases
import importlib.util
import importlib.machinery
import traceback
import pprint
import string
import re
import json
import subprocess
import shutil
import platform
import signal

logger = getLogger("meny.cli", INFO)


def resolve_path(file: str) -> Path:
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(path)
    else:
        return path.resolve()


def load_module_from_path(path: Path):
    sys.path.append(str(Path(path).parent))
    loader = importlib.machinery.SourceFileLoader(f"__meny_module_{path.stem}", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    sys.path.pop()
    return module


def menu_from_python_code(filepath: Path, repeat: bool):
    try:
        module = load_module_from_path(filepath)
    except Exception as e:
        logger.error("".join(traceback.TracebackException.from_exception(e).format()))
        logger.error(f"Something went wrong when attempting to import \x1b[33m{filepath}\x1b[0m")
        logger.error(f"Received error: {e}")
        logger.error(f"Please ensure that \x1b[33m{filepath}\x1b[0m contains valid Python code")
        sys.exit(1)

    cases = _get_module_cases(module)
    if len(cases) == 0:
        logger.info(f"There are no defined functions in \x1b[33m{filepath}\x1b[0m")
        sys.exit(1)

    return menu(cases, f"Functions in {filepath}", once=not repeat, return_mode="flat")


class MenyTemplate(string.Template):
    default_arg = r"[\w ]*"
    delimiter = "@"
    pattern = fr"""
    @(?:
      (?P<escaped>@)         | # Escape sequence of two delimiters
      (?P<named>\w+)         | # delimiter and a Python identifier
      {{(?P<braced>\w+=?{default_arg})}} | # delimiter and a braced identifier
      (?P<invalid>)            # Other ill-formed delimiter exprs
    )
    """


def get_casefunc(command: str, executable: str):
    parse_template = MenyTemplate(command)
    arg_components = []
    signature_components = []
    for _, named, braced, _ in re.findall(parse_template.pattern, command):
        if named:
            arg_components.append(f"{named}={named}")
            signature_components.append(f"{named}: str")
            continue

        if not braced:
            continue

        if "=" in braced:
            braced, default = braced.split("=")
            signature_components.append(f"{braced}: str='{default}'")
        else:
            signature_components.append(f"{braced}: str")

        arg_components.append(f"{braced}={braced}")

    signature_components = list(dict.fromkeys(signature_components))
    arg_components = list(dict.fromkeys(arg_components))
    signature = ", ".join(signature_components)
    args = ", ".join(arg_components)

    # Remove default argument from command string
    template = MenyTemplate(re.sub(fr"@{{(\w+)={MenyTemplate.default_arg}}}", r"@{\1}", command))
    if executable is not None:
        executable = f"'{executable}'"

    ns = {}
    txt = f"def f({signature}): subprocess.call(template.safe_substitute({args}), shell=True, executable={executable})"
    exec(txt, {**globals(), **locals()}, ns)

    return ns["f"], txt


def menu_from_json(filepath: Path, repeat: bool, executable: str):
    with open(filepath, "r") as f:
        try:
            spec = json.load(f)
        except Exception as e:
            logger.error(f"Error when parsing {filepath}: {e}")
            sys.exit()

    def _menu_from_json(spec: dict, menutitle: str):
        once = not repeat or spec.get("__repeat__", False)
        cases = {}
        for title, command_or_dict in spec.items():
            if isinstance(command_or_dict, str):
                cases[title] = get_casefunc(command_or_dict, executable)[0]
            if isinstance(command_or_dict, dict):
                cases[title] = _menu_from_json(command_or_dict, menutitle=title)
        return lambda: menu(cases, title=menutitle, once=once)

    return _menu_from_json(spec, filepath.name)()


def cli():
    parser = argparse.ArgumentParser(prog="meny", description="Start a meny on a specified Python file or JSON")

    parser.add_argument("file", type=str, nargs=1, help="A python or json file to start a menu on")
    parser.add_argument(
        "-r",
        "--repeat",
        help="Dont exit meny after running a case. If used on JSON it is equivalent to set the __repeat__ "
        "flag on the objects of all levels",
        action="store_true",
    )
    parser.add_argument(
        "-e",
        "--executable",
        help="Shell program to run the commands in a given json file."
        " Only effective when creating menus from json files."
        " Will attempt to use 'bash' for Unix systems, and "
        "'powershell' for Windows. Else will default to whatever "
        "Python chooses (usually 'sh' and 'cmd' for Unix and Windows respectively)",
    )

    args = parser.parse_args()

    file = args.file[0]
    try:
        filepath = resolve_path(file)
    except FileNotFoundError:
        logger.error(f"Could not find \x1b[33m{file}\x1b[0m")
        sys.exit(1)

    try:
        signal.signal(signal.SIGINT, lambda *args, **kwargs: None)
        if filepath.suffix == ".json":
            if platform.system() == "Windows":
                executable = shutil.which("powershell")
            else:
                executable = shutil.which("bash")
            returnDict = menu_from_json(filepath, args.repeat, args.executable or executable)
        else:
            returnDict = menu_from_python_code(filepath, args.repeat)
            values = list(returnDict.values())
            if len(values) == 1 and values[0] is not None:
                pprint.pprint(values[0])
            elif len(values) > 1:
                pprint.pprint(returnDict)
            else:
                sys.exit(1)
    except Exception as e:
        # Handle curses error when SIGINT. This way is cross platform for the people who doesn't have curses
        if "no input" == str(e):
            pass
        else:
            raise e

    sys.exit(0)
