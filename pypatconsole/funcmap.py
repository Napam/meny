'''
This module primarily conatins a the construct_funcmap
function. The function constructs the dictionary that contains
the console cases. The dictionary keys consists of a range of integers
and the values are the cases (which are functions).
'''

from inspect import isfunction, getmodule, unwrap, getmembers
from types import FunctionType, ModuleType, GeneratorType
from typing import Dict, Iterable, Union, Callable, List, Optional, Tuple
import re
from pypatconsole.config import _CASE_TITLE, _DEFINITION_ORDER

def _get_case_name(func: FunctionType) -> str:
    '''
    TODO: Update docstring
    '''
    # Unwrap in case the function is wrapped
    func = unwrap(func)
    
    if _CASE_TITLE in func.__dict__:
        return func.__dict__[_CASE_TITLE]
    else:
        return func.__name__


def construct_funcmap(funcs: Iterable[FunctionType], decorator: Optional[FunctionType]=None) -> Dict[str, Tuple[str, Callable]]:
    '''
    Parameters
    ------------
    funcs: Iterable[FunctionType]
    decorator: optional, a decorator to decorate all case functions 

    Returns
    --------
    Returns dictionary to be used in console interface

    Keys of dictionary are enumeration 1, 2, 3 ... for interface.
    Each item is a tuple with first element as description of case, 
    second element is the function itself:
    ('Scrape OSEBX', function object)
    '''
    if not isinstance(funcs, Iterable): 
        raise TypeError(f'Unsupported type for functions: got {type(funcs)}')
    
    func_map: Dict[str, Tuple[str, FunctionType]] = {}

    if decorator is not None:
        for i, func in enumerate(funcs, start=1):
            func_map[str(i)] = (_get_case_name(func), decorator(func))
    else:
        for i, func in enumerate(funcs, start=1):
            func_map[str(i)] = (_get_case_name(func), func)

    return func_map


if __name__ == '__main__':
    pass