"""
This module primarily conatins a the construct_funcmap
function. The function constructs the dictionary that contains
the console cases. The dictionary keys consists of a range of integers
and the values are the cases (which are functions).
"""

from inspect import unwrap
from types import FunctionType
from typing import Callable, Dict, Iterable, Optional, Tuple

from meny.config import _CASE_TITLE, _DICT_KEY


def _get_case_name(func: FunctionType) -> str:
    """
    First unwraps function (if wrapped in decorators). Assumes that wrapped functions has the
    __wrapped__ attribute (which will be handled by using functools.wraps). Then returns case
    title if set, else just function name
    """
    funcvars = vars(unwrap(func))
    return funcvars.get(_CASE_TITLE, False) or funcvars.get(_DICT_KEY, False) or func.__name__


def construct_funcmap(
    funcs: Iterable[FunctionType], decorator: Optional[FunctionType] = None
) -> Dict[str, Tuple[str, FunctionType]]:
    """
    Parameters
    ------------
    funcs: Iterable[FunctionType]
    decorator: optional, a decorator to decorate all case functions

    Returns
    --------
    Returns dictionary to be used in console interface

    Keys of dictionary are enumeration 1, 2, 3 ... for interface.
    Each item is a tuple with first element as name of case,
    second element is the function itself:
    ('Scrape OSEBX', function object)
    """
    if not isinstance(funcs, Iterable):
        raise TypeError(f"Unsupported type for functions: got {type(funcs)}")

    if decorator is None:
        decorator = lambda f: f

    return {str(i): (_get_case_name(func), decorator(func)) for i, func in enumerate(funcs, start=1)}


if __name__ == "__main__":
    import subprocess

    subprocess.call(["python3", "example/cases.py"])
