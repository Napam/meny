"""
Common stuff for console stuff
"""
import os
import re
from meny import config as cng
from inspect import getmodule, isfunction
from types import FunctionType, ModuleType
from typing import Any, Container, Dict, List
from meny import strings

# *Nix uses clear, windows uses cls
_CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"

RE_ANSI = re.compile(r"\x1b\[[;\d]*[A-Za-z]")  # Taken from tqdm source code, matches escape codes

RE_INPUT = re.compile("[\w.-]+|\[.*?\]|\{.*?\}|\(.*?\)|\".*?\"|'.*?'")


def _assert_supported(arg: Any, paramname: str, supported: Container):
    """
    Assert if argument is supported by checking if 'arg' is in 'supported'

    Example
    --------
    >>> _assert_supported("cat", "animal", ("dog", "rabbit"))
    AssertionError: Got unsupported argument for parameter "animal". Available options are: ('dog', 'rabbit')
    """
    assert arg in supported, (
        f'Got unsupported argument "'
        + strings.YELLOW
        + str(arg)
        + strings.END
        + '" for parameter "'
        + strings.YELLOW
        + paramname
        + strings.END
        + f'".\nAvailable options are: {supported}'
    )


def set_default_frontend(frontend: str):
    """Options: (simple, fancy, auto)"""
    _assert_supported(frontend, "frontend", ("simple", "fancy", "auto"))
    cng.DEFAULT_FRONTEND = frontend


def set_default_once(once: bool):
    """True or False"""
    _assert_supported(type(once), "once", (bool,))
    cng.DEFAULT_ONCE = once


def clear_screen() -> None:
    """OS independent terminal clear"""
    os.system(_CLEAR_COMMAND)


def _extract_and_preprocess_functions(dict_: Dict[str, FunctionType]) -> List[FunctionType]:
    """
    Parameters
    -------------
    dict_: Dict[str, FunctionType])

    Extract functions from dictionary. Will also add the dictionary key to the function vars
    (i.e. the __dict__ attribute)

    Python parses top down, and inserts the functions in a dictionary. CPython's dict implementation
    in Python 3.6 iterates through dict items in insertion order. As of Python 3.7 said behavior
    become a standard for Python. Thus the functions should come in definition order.

    See:
    https://softwaremaniacs.org/blog/2020/02/05/dicts-ordered/
    """
    funcs = []
    for key, val in dict_.items():
        if isfunction(val):
            vars(val)[cng._DICT_KEY] = key
            funcs.append(val)
    return funcs


def input_splitter(argstring: str) -> List[str]:
    """
    Split string
    """
    return RE_INPUT.findall(argstring)


def _get_module_cases(module: ModuleType) -> List[FunctionType]:
    """Get all functions defined in module"""
    inModule = lambda f: isfunction(f) and (getmodule(f) == module)
    return [func for func in vars(module).values() if inModule(func)]


if __name__ == "__main__":
    import subprocess

    subprocess.call(["python3", "example/cases.py"])
