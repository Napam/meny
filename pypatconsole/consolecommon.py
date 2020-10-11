'''
Common stuff for console stuff
'''
import os 
from inspect import isfunction
from typing import Callable, List, Dict
from shlex import shlex

# *Nix uses clear, windows uses cls
__CLEAR_COMMAND = 'cls' if os.name == 'nt' else 'clear'

def clear_screen() -> None:
    '''Obvious'''
    os.system(__CLEAR_COMMAND)

def list_local_cases(locals_: Dict[str, Callable], main: bool=False) -> List[Callable]:
    '''
    Parameters
    -------------
    locals_: return value of locals()
    
    Returns a list of functions sorted alphabetically by function names. 
    '''
    name_func_pairs = sorted(list(locals_.items()), key=lambda x: x[0])
    return [pairs[1] for pairs in name_func_pairs if isfunction(pairs[1])]

def input_splitter(argstring: str) -> List[str]:
    '''
    Split string
    '''
    # Doing it this way instead of using shlex.split will
    # not remove quote symbols in dicts and lists and whatever 
    shlexysmexy = shlex(argstring)
    shlexysmexy.whitespace_split=True
    return [token for token in shlexysmexy]

def print_help(*args, **kwargs) -> None:
    print(
        '''
        To exit console: Enter q or press Ctrl+c

        To return to parent menu: Enter blank (press enter without giving input)
                                  or enter '..'. If you are in main menu, this 
                                  will exit the program as well. 

        Press enter to exit help screen
        '''
    )
    input()


if __name__ == '__main__':
    # print(list_local_cases(locals()))
    print(locals())
