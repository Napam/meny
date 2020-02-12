'''
Run this file to run console 
'''
from time import sleep
import consolestrings as strings
import consoleconfig as ccng 
from funcmap import construct_funcmap, print_funcmap
from consolecommon import clear_screen, input_splitter
from typing import Union, Callable
from inspect import getfullargspec, unwrap, signature

def logo_title(title: str):
    '''Prints logo title'''
    print("{:-^40s}".format(title))

def show_cases(funcmap: dict, title=strings.LOGO_TITLE):
    '''Prints function map prettily with a given title'''
    logo_title(title)
    print_funcmap(funcmap)

def enter_prompt(msg: str=strings.ENTER_PROMPT):
    '''Prints enter prompt message and than returns input()'''
    print(msg, end=': ')
    return input()

def exit_program():
    '''
    Exit program
    '''
    print(strings.EXIT_MSG)
    sleep(ccng.MSG_WAIT_TIME)
    clear_screen()
    exit()

__SPECIAL_ARG_CASES = {
    str: lambda x: str(x.strip("\"\'")), # Removes outer " or ' characters
    tuple:eval, 
    list:eval, 
    dict:eval,
    set:eval
}

def _handle_arglist(func, arglist):
    '''
    Handles list of strings that are the arguments 
    The function turns the strings from the list into 
    their designated types (found from function signature).
    '''
    argsspec = getfullargspec(unwrap(func))
    args = argsspec.args
    argtypes = argsspec.annotations

    if len(arglist) > len(args):
        raise TypeError(f'Got too many arguments, should be {len(args)}, but got {len(arglist)}')

    # Special proceedures for special classes
    typed_arglist = [] 
    for arg, type_ in zip(arglist, argtypes.values()):
        if type_ in __SPECIAL_ARG_CASES:
            typed_arglist.append(__SPECIAL_ARG_CASES[type_](arg))
        else:
            typed_arglist.append(type_(arg))

    return typed_arglist

def _error_info(error, func):
    print(strings.ERROR_INDICATOR)
    print(error)
    print(f'Function signature: {signature(func)}')
    sleep(ccng.MSG_WAIT_TIME*2)

class CLI:
    '''
    Command Line Interface class 
    '''
    def __init__(self, cases, title: str=strings.LOGO_TITLE, blank_proceedure: Union[str, Callable]='return', 
                decorator: Callable=None):
        '''
        Input
        -----
        cases: 

        if given a module: module containing functions that serves as cases a user can pick from terminal interface. 
        the module should not implement any other functions. 
        
        if given a list: will simply use function in list as cases.

        First line of docstring becomes case description
        ALL CASES MUST CONTAIN DOCSTRINGS

        title: String to print over alternatives 

        blank_proceedure: What to do when given blank input (defaults to stopping current view (without exiting))
        '''
        self.funcmap = construct_funcmap(cases, [exit_program], decorator)
        self.title = title

        if blank_proceedure == 'return':
            self.blank_proceedure = self.__return_to_parent
        elif blank_proceedure == 'exit':
            self.blank_proceedure = exit_program
        else:
            self.blank_proceedure = blank_proceedure

    def __return_to_parent(self):
        self.active = False

    def run(self):
        '''
        Main function for console interface
        '''
        self.active = True
        try:
            while self.active:
                clear_screen()
                show_cases(self.funcmap, self.title)

                # Get key to func map
                print()
                print('Entering blank returns/exits')
                inputstring = enter_prompt(strings.ENTER_PROMPT)

                # Pressing enter without specifying enables if test
                clear_screen()
                if not inputstring:
                    self.blank_proceedure()
                    continue

                inputlist = input_splitter(inputstring)
                case = inputlist.pop(0)
                
                # Obtain case function from funcmap and 
                # calls said function. Recall that items are 
                # (description, function), hence the [1]
                if case in self.funcmap:
                    casefunc = self.funcmap[case][1]
                    try:
                        if inputlist:
                            # Raiseses TypeError if wrong number of arguments 
                            casefunc(*_handle_arglist(casefunc, inputlist))
                        else:
                            # Will raise TypeError if casefunc() actually requires arguments
                            casefunc()
                    except TypeError as e:
                        _error_info(e, casefunc)

                else:
                    print(strings.INVALID_TERMINAL_INPUT_MSG)
                    sleep(ccng.MSG_WAIT_TIME)

        except KeyboardInterrupt:
            # Ensures proper exit when Kbinterrupt
            exit_program()
    