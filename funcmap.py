from inspect import getmembers, isfunction, getmodule
from types import ModuleType
from typing import Union
from collections import Iterable

def __docstring_firstline(func):
    '''Get first line of docstring of func'''
    return func.__doc__.strip().split('\n')[0]

def print_funcmap(func_map):
    '''
    Prints a func_map dictionary

    Items should be tuples with first elements as descriptions
    and second elements as function objects
    '''
    for key, tup in func_map.items():
        print(key + '.', tup[0])  

def __get_module_cases(module):
    # Get all functions defined in module
    funcs = getmembers(module, lambda f: True if isfunction(f) and getmodule(f) == module else False) 
    # getmembers return a tuple with the func names as first element and function object as second
    # unpack dat shit yo
    funcs = [f[1] for f in funcs]
    return funcs

def construct_funcmap(cases: Union[ModuleType, list], other_cases: list=None, decorator: 'Decorator'=None):
    '''
    Input
    -----
    cases: 

    if given a module: module containing functions that serves as cases a user can pick from terminal interface. 
    the module should not implement any other functions. 
    
    if given a list: will simply use function in list as cases.

    First line of docstring becomes case description
    ALL CASES MUST CONTAIN DOCSTRINGS

    other_cases: optional, list of other additional cases (functions). These functions will simply be appended
    to the end of an already existing list. 

    decorator: optional, a decorator to decorate all case functions 

    IMPORTANT: All case functions must have docstrings 

    Returns
    -------
    Returns dictionary to be used in console interface

    Keys of dictionary are enumeration 1, 2, 3 ... for interface.
    Each item is a tuple with first element as description of case, second element
    is the function itself:
    ('Scrape OSEBX', function object)
    '''
    if type(cases) == ModuleType:
        funcs = __get_module_cases(cases)
    elif type(cases) == list:
        funcs = cases
    else:
        raise TypeError('Unsupported type for cases')

    # Append other functions if specified
    if other_cases != None:
        funcs = funcs + other_cases

    func_map = {}

    if decorator != None:
        for i, func in enumerate(funcs, start=1):
            func_map[str(i)] = (__docstring_firstline(func), decorator(func))
    else:
        for i, func in enumerate(funcs, start=1):
            func_map[str(i)] = (__docstring_firstline(func), func)

    return func_map