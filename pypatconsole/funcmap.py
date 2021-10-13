'''
This module primarily conatins a the construct_funcmap
function. The function constructs the dictionary that contains 
the console cases. The dictionary keys consists of a range of integers
and the values are the cases (which are functions). 
'''

from inspect import isfunction, getmodule, unwrap, getmembers
from types import FunctionType, ModuleType
from typing import Dict, Union, Callable, List, Optional, Tuple
import re
from .decorator import _CASE_TITLE, _DEFINITION_ORDER

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


def construct_funcmap(funcs: List[Callable], decorator: Optional[Callable]=None) -> Dict[str, Tuple[str, Callable]]:
    '''
    Parameters
    ------------
    TODO: Update docstring
    TODO: Refactor module function extraction out of funcmap module
    
    cases: if given a module: module containing functions that serves as 
           cases a user can pick from terminal interface. the module should
           not implement any other functions. 
    
           if given a list: will simply use function in list as cases.

           First line of docstring becomes case description
           ALL CASES MUST CONTAIN DOCSTRINGS

    other_cases: optional, list of other additional cases (functions).
                 These functions will simply be appended to the end of 
                 an already existing list. 

                 IMPORTANT: All case functions must have docstrings 

    decorator: optional, a decorator to decorate all case functions 

    Returns
    --------
    Returns dictionary to be used in console interface

    Keys of dictionary are enumeration 1, 2, 3 ... for interface.
    Each item is a tuple with first element as description of case, 
    second element is the function itself:
    ('Scrape OSEBX', function object)
    '''
    if not isinstance(funcs, (list, tuple)): # Maybe check for iterable instead?
        raise TypeError(f'Unsupported type for cases container: got {type(funcs)}')
    
    func_map: Dict[str, Tuple[str, Callable]] = {}

    if decorator is not None:
        for i, func in enumerate(funcs, start=1):
            func_map[str(i)] = (_get_case_name(func), decorator(func))
    else:
        for i, func in enumerate(funcs, start=1):
            func_map[str(i)] = (_get_case_name(func), func)

    return func_map


if __name__ == '__main__':
    pass