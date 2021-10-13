"""
Common stuff for console stuff
"""
import os
from inspect import isfunction, isclass, getmro
from types import FunctionType, DynamicClassAttribute
from typing import Callable, List, Dict, Union
from shlex import shlex
from functools import wraps
from .decorator import _DEFINITION_ORDER
from math import inf

# *Nix uses clear, windows uses cls
__CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"

def clear_screen() -> None:
    """Obvious"""
    os.system(__CLEAR_COMMAND)


def list_local_cases(locals_: Dict[str, Callable], main: bool = False) -> List[Callable]:
    """
    Parameters
    -------------
    locals_: return value of locals()

    Returns a list of functions sorted alphabetically by function names.
    """
    functions = [pairs[1] for pairs in list(locals_.items()) if isfunction(pairs[1])]
    functions.sort(key=lambda f: f.__dict__.get(_DEFINITION_ORDER, inf))
    return functions


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