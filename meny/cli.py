import argparse
import sys
from pathlib import Path
from typing import Union
from .menu import menu
from .menylogger import getLogger, INFO
from .utils import _get_module_cases
import importlib.util
import traceback

logger = getLogger("meny.cli", INFO)


def resolve_path(file: str) -> Path:
    path = Path(file)
    if not path.exists():
        raise FileNotFoundError(path)
    else:
        return path.resolve()


def load_module_from_path(path: Union[Path, str]):
    sys.path.append(str(Path(path).parent))
    spec = importlib.util.spec_from_file_location(f"_meny_module_{path.stem}", str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    sys.path.pop()
    return module


def cli():
    parser = argparse.ArgumentParser(
        prog="Meny", description="Start a meny on a specified Python file"
    )

    parser.add_argument("pythonfile", type=str, nargs=1, help="a python file to start a menu on")
    parser.add_argument(
        "-r",
        "--repeat",
        help="dont exit meny after running a case",
        action="store_true"
    )

    args = parser.parse_args()

    file = args.pythonfile[0]
    try:
        filepath = resolve_path(file)
    except FileNotFoundError as e:
        logger.error(f"Could not find \x1b[33m{file}\x1b[0m")
        exit()

    try:
        module = load_module_from_path(filepath)
    except AttributeError as e:
        logger.error("".join(traceback.TracebackException.from_exception(e).format()))
        logger.error(f"Something went wrong when attempting to import \x1b[33m{filepath}\x1b[0m")
        logger.error(f"Received error: {e}")
        logger.error(f"Please ensure that \x1b[33m{filepath}\x1b[0m contains valid Python code")
        exit()

    cases = _get_module_cases(module)
    if len(cases) == 0:
        logger.info(f"There are no defined functions in \x1b[33m{filepath}\x1b[0m")
        exit()

    menu(cases, f"Functions in {file}", once=not args.repeat)
