'''
Common stuff for console stuff
'''
import os 
from inspect import isfunction
from typing import Union, Callable
from types import ModuleType

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

def nested_menu(cases: Union[list, dict, ModuleType], title: str=' Title ', 
                blank_proceedure: Union[str, Callable] ='return', 
                decorator=None, run: bool=True):
    '''
    For conveinience when creating nested menus. Simply give the required argument, then the
    function will initialize another menu. The menu structure will follow the same paradigm 
    as for any other cases. 

    Input
    ------
    cases: should be locals() from where this function is called

    title: title of menu

    blank_proceedure: blank_proceedure: What to do when given blank input (defaults to stopping current view (without exiting))

    decorator: Whether to decorate functions

    run: To run menu instantly or not

    Return:
    --------
    CLI (Command Line Interface) object. Use .run() method to activate menu. 
    '''
    if type(cases) == list:
        cases_to_send = cases
    elif type(cases) == dict:
        cases_to_send = list_local_cases(cases)
    elif type(cases) == ModuleType:
        cases_to_send = cases
    else:
        raise TypeError('Invalid type')

    # TODO: Think over import cycle
    from consoleobject import CLI

    CLIobject = CLI(cases=cases_to_send, title=title, blank_proceedure=blank_proceedure, 
                    decorator=decorator)
    if run:
        CLIobject.run()
    
    return CLIobject


