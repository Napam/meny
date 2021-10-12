"""
Common stuff for console stuff
"""
import os
from inspect import isfunction, isclass, getmro
from types import FunctionType, DynamicClassAttribute
from typing import Callable, List, Dict, Union
from shlex import shlex
from functools import wraps

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
    name_func_pairs = sorted(list(locals_.items()), key=lambda x: x[0])
    return [pairs[1] for pairs in name_func_pairs if isfunction(pairs[1])]


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

def getmembers(object, predicate=None):
    """
    Copy paste from Python's built in inspect module, with some changed 
    code. Most important is that this removes the sorting on names


    Default docstring:
    Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate.
    """
    if isclass(object):
        mro = (object,) + getmro(object)
    else:
        mro = ()
    results = []
    processed = set()
    names = dir(object)
    # :dd any DynamicClassAttributes to the list of names if object is a class;
    # this may result in duplicate entries if, for example, a virtual
    # attribute with the same name as a DynamicClassAttribute exists
    try:
        for base in object.__bases__:
            for k, v in base.__dict__.items():
                if isinstance(v, DynamicClassAttribute):
                    names.append(k)
    except AttributeError:
        pass
    for key in names:
        # First try to get the value via getattr.  Some descriptors don't
        # like calling their __get__ (see bug #1785), so fall back to
        # looking in the __dict__.
        try:
            value = getattr(object, key)
            # handle the duplicate key
            if key in processed:
                raise AttributeError
        except AttributeError:
            for base in mro:
                if key in base.__dict__:
                    value = base.__dict__[key]
                    break
            else:
                # could be a (currently) missing slot member, or a buggy
                # __dir__; discard and move on
                continue
        if not predicate or predicate(value):
            results.append((key, value))
        processed.add(key)
    return results


if __name__ == "__main__":
    pass