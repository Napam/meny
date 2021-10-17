"""
Common stuff for console stuff
"""
import os
import re
from meny import config as cng
from inspect import isfunction
from types import FunctionType
from typing import Any, Callable, Container, Dict, List
from meny import strings

# *Nix uses clear, windows uses cls
__CLEAR_COMMAND = "cls" if os.name == "nt" else "clear"

RE_ANSI = re.compile(
    r"\x1b\[[;\d]*[A-Za-z]"
)  # Taken from tqdm source code, matches escape codes

RE_INPUT = re.compile("\w+|\[.*?\]|\{.*?\}|\(.*?\)|\".*?\"|'.*?'")


def _assert_supported(arg: Any, paramname: str, supported: Container):
    """
    Assert if argument is supported by checking if 'arg' is in 'supported'

    Example
    --------
    >>> _assert_supported("cat", "animal", ("dog", "rabbit"))
    AssertionError: Got unsupported argument for parameter "animal". Available options are: ('dog', 'rabbit')
    """
    assert arg in supported, (
        'Got unsupported argument for parameter "'
        + strings.YELLOW
        + paramname
        + strings.END
        + f'". Available options are: {supported}'
    )


def set_default_frontend(frontend: str):
    _assert_supported(frontend, "frontend", ("simple", "fancy", "auto"))
    cng.DEFAULT_FRONTEND = frontend


def clear_screen() -> None:
    """Obvious"""
    os.system(__CLEAR_COMMAND)


def list_local_cases(locals_: Dict[str, Callable]) -> List[FunctionType]:
    """
    Parameters
    -------------
    locals_: return value of locals()

    Returns a list of functions. Orders are whatever is from locals() or globals(). Python parses
    top down, and inserts the functions in a dictionary. CPython's dict implementation in Python 3.6
    iterates through dict items in insertion order. As of Python 3.7 said behavior become a
    standard for Python. Thus the functions should come ib definition order.

    See:
    https://softwaremaniacs.org/blog/2020/02/05/dicts-ordered/
    """
    return [pairs[1] for pairs in list(locals_.items()) if isfunction(pairs[1])]


def input_splitter(argstring: str) -> List[str]:
    """
    Split string
    """
    return RE_INPUT.findall(argstring)


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
