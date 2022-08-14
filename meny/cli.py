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


def cli():
    parser = argparse.ArgumentParser(
        prog="meny", description="Start a meny on a specified Python file"
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
        sys.exit(1)

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

    returnDict = menu(cases, f"Functions in {file}", once=not args.repeat, return_mode='flat')
    values = list(returnDict.values())
    if len(values) == 1 and values[0] is not None:
        pprint.pprint(values[0])
    elif len(values) > 0:
        pprint.pprint(returnDict)
    else:
        sys.exit(1)

    sys.exit(0)
