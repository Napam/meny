'''
Common stuff for console stuff
'''
import os 
from inspect import isfunction

__CLEAR_COMMAND = 'cls' if os.name == 'nt' else 'clear'
def clear_screen():
    '''Obvious'''
    os.system(__CLEAR_COMMAND)

def list_local_cases(locals_):
    '''
    Input: is the return value of locals()
    
    Returns a list of functions sorted alphabetically by function names. 
    '''
    name_func_pairs = sorted(list(locals_.items()), key= lambda x: x[0])
    return [pairs[1] for pairs in name_func_pairs if isfunction(pairs[1])]

