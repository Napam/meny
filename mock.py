'''
Mock file 
'''

import inspect
from types import FunctionType
import numpy as np
from shlex import shlex

def wrappy(func):
    def wrap(*args, **kwargs):
        return func(*args, **kwargs)
    wrap.__wrapped__ = func
    return wrap

@wrappy
@wrappy
def a(s: str, x: int, y: float, z: list, i: dict, j: tuple, k: set):
    print(locals())

input_string = "'cat and dog' 1 2 [1,'a','b'] {'1':1,'2':2} (1,2,3) {'a','b',1}"
input_string = '"cat and dog" 1 2 [1,"a","b"] {"1":1,"2":2} (1,2,3) {"a","b",1}'

# input_string = input()

def input_splitter(argstring: str):
    '''
    Split string
    '''
    # Doing it this way instead of using shlex.split will
    # not remove quote symbols in dicts and lists and whatever 
    shlexysmexy = shlex(argstring)
    shlexysmexy.whitespace_split=True
    return [token for token in shlexysmexy]

# print(input_splitter("1 'cat and dog' 1 2 [1,'a','b'] {'1':1,'2':2} (1,2,3) {'a','b',1}"))
def handle_args(func, argstring):
    argsspec = inspect.getfullargspec(inspect.unwrap(func))
    args = argsspec.args
    argtypes = argsspec.annotations

    n_args = len(args)
    n_typed = len(argtypes)

    # Special proceedures for special classes
    special_cases = {
        str: lambda x: str(x.strip("\"\'")), # Removes outer " or ' characters
        tuple:eval, 
        list:eval, 
        dict:eval,
        set:eval
    }

    print(input_splitter(argstring))
    arglist = [] 
    for arg, type_ in zip(input_splitter(argstring), argtypes.values()):
        if type_ in special_cases:
            print(type_, arg,':',end=' ')
            arglist.append(special_cases[type_](arg))
            print(arglist[-1])
        else:
            arglist.append(type_(arg))

    # print(arglist)
    return arglist

a(*handle_args(a, input_string))


