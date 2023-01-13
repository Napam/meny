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

logger = getLogger("meny.cli", INFO)


def resolve_path(file: str) -> Path:
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(path)
    else:
        return path.resolve()


def load_module_from_path(path: Path):
    sys.path.append(str(Path(path).parent))
    loader = importlib.machinery.SourceFileLoader(f'__meny_module_{path.stem}', str(path))
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

    return menu(cases, f"Functions in {filepath}", once=not repeat, return_mode='flat')


class MenyTemplate(string.Template):
    delimiter = "@"


def get_casefunc(command):
    template = MenyTemplate(command)
    params = [named or braced for _, named, braced, _ in re.findall(template.pattern, command)]
    signature = ",".join(params)
    args = ",".join(f"{arg}={arg}" for arg in params)

    ns = {}
    txt = f"def f({signature}): subprocess.call(template.safe_substitute({args}), shell=True)"
    exec(txt, {**globals(), **locals()}, ns)

    return ns['f']


def menu_from_json(filepath: Path):
    with open(filepath, 'r') as f:
        try:
            spec = json.load(f)
        except Exception as e:
            logger.error(f"Error when parsing {filepath}: {e}")
            sys.exit()

    def _menu_from_json(spec: dict):
        cases = {}
        for title, command_or_dict in spec.items():
            if isinstance(command_or_dict, str):
                cases[title] = get_casefunc(command_or_dict)
            if isinstance(command_or_dict, dict):
                cases[title] = _menu_from_json(command_or_dict)
        return lambda: menu(cases, once=not spec.get("__repeat__", False))

    return _menu_from_json(spec)()


def cli():
    parser = argparse.ArgumentParser(
        prog="meny", description="Start a meny on a specified Python file or JSON"
    )

    parser.add_argument("file", type=str, nargs=1, help="a python or json file to start a menu on")
    parser.add_argument(
        "-r",
        "--repeat",
        help="dont exit meny after running a case",
        action="store_true"
    )

    args = parser.parse_args()

    file = args.file[0]
    try:
        filepath = resolve_path(file)
    except FileNotFoundError:
        logger.error(f"Could not find \x1b[33m{file}\x1b[0m")
        sys.exit(1)

    if filepath.suffix == ".json":
        returnDict = menu_from_json(filepath)
    else:
        returnDict = menu_from_python_code(filepath, args.repeat)
        values = list(returnDict.values())
        if len(values) == 1 and values[0] is not None:
            pprint.pprint(values[0])
        elif len(values) > 1:
            pprint.pprint(returnDict)
        else:
            sys.exit(1)

    sys.exit(0)
