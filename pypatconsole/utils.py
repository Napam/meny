"""
Common stuff for console stuff
"""
import os
import re
from inspect import isfunction
from shlex import shlex
from types import FunctionType
from typing import Callable, Dict, List, Union

# *Nix uses clear, windows uses cls
__CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"

RE_ANSI = re.compile(
    r"\x1b\[[;\d]*[A-Za-z]"
)  # Taken from tqdm source code, matches escape codes


def clear_screen() -> None:
    """Obvious"""
    os.system(__CLEAR_COMMAND)


def list_local_cases(locals_: Dict[str, Callable]) -> List[Callable]:
    """
    Parameters
    -------------
    locals_: return value of locals()

    Returns a list of functions. Orders are whatever is from locals() or globals(). Python parses
    top down, and inserts the functions in a dictionary. CPython's dict implementation in Python 3.6
    iterates through dict items in insertion order. As of Python 3.7 said behavior become a
    standard for Python.

    See:
    https://softwaremaniacs.org/blog/2020/02/05/dicts-ordered/
    """
    return [pairs[1] for pairs in list(locals_.items()) if isfunction(pairs[1])]


def input_splitter(argstring: str) -> List[str]:
    """
    Split string
    """
    # Doing it this way instead of using shlex.split will
    # not remove quote symbols in dicts and lists and whatever
    shlexysmexy = shlex(argstring)
    shlexysmexy.whitespace_split = True
    return [token for token in shlexysmexy]


def print_help(*args, **kwargs) -> None:
    print(
        """
        To exit or return from console: Enter q

        To return to parent menu: Enter blank (press enter without giving input)
                                  or enter '..'. If you are in main menu, this 
                                  will exit the program as well. 

        Press enter to exit help screen
        """
    )
    input()


if __name__ == "__main__":
    pass
