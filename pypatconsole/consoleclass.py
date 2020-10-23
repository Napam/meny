'''
Contains the command line interface (CLI) class, along its factory function:
menu()
'''

from time import sleep
import pypatconsole.consolestrings as strings
import pypatconsole.consoleconfig as ccng 
from pypatconsole.funcmap import (construct_funcmap, print_funcmap, 
                                 _docstring_firstline)
from pypatconsole.consolecommon import (clear_screen, input_splitter, 
                                        list_local_cases, print_help)
from typing import List, Union, Callable, Dict, Optional
from inspect import getfullargspec, unwrap, signature
from types import ModuleType

def logo_title(title: str) -> None:
    '''Prints logo title'''
    print("{:-^40s}".format(title))

def show_cases(funcmap: dict, title=strings.LOGO_TITLE) -> None:
    '''Prints function map prettily with a given title'''
    logo_title(title)
    print_funcmap(funcmap)

def enter_prompt(msg: str=strings.ENTER_PROMPT) -> str:
    '''Prints enter prompt message and than returns input()'''
    print(msg, end=': ')
    return input()

def exit_program(*args, **kwargs) -> None:
    '''
    Exit program
    '''
    print(strings.EXIT_MSG)
    sleep(ccng.MSG_WAIT_TIME)
    clear_screen()
    exit()

# Strategy method for special cases
# Cases that are not special are e.g. int, since you can directly
# use int() as a function
__SPECIAL_ARG_CASES = {
    str: lambda x: str(x.strip("\"\'")), # Removes outer " or ' characters
    tuple:eval, 
    list:eval, 
    dict:eval,
    set:eval
}

def _handle_arglist(func: Callable, arglist: list) -> List:
    '''
    Handles list of strings that are the arguments 
    The function turns the strings from the list into 
    their designated types (found from function signature).
    '''
    # Unwrap in case the function is wrapped
    func = unwrap(func)
    argsspec = getfullargspec(func)
    args = argsspec.args
    argtypes = argsspec.annotations

    if len(args) > len(argtypes):
        raise NotImplementedError(f'Missing typehints in {unwrap(func)}')

    if len(arglist) > len(args):
        # TypeError will be caught and handled
        raise TypeError(f'Got too many arguments, should be {len(args)}, but got {len(arglist)}')

    # Special proceedures for special classes
    typed_arglist = [] 
    for arg, type_ in zip(arglist, argtypes.values()):
        if type_ in __SPECIAL_ARG_CASES:
            typed_arglist.append(__SPECIAL_ARG_CASES[type_](arg))
        else:
            typed_arglist.append(type_(arg))

    return typed_arglist

def _error_info(error: Exception, func: Callable) -> None:
    '''
    Used to handle error for cases

    Error: E.g. ValueError

    func: Function with docstring
    '''
    print(strings.ERROR_INDICATOR)
    print(f'Selected case: "{_docstring_firstline(func)}"')
    print(error)
    print(f'Function signature: {signature(func)}')
    print()
    print(strings.INPUT_WAIT_PROMPT_MSG)
    input()

class CLI:
    '''
    Command Line Interface class 
    '''
    def __init__(self, cases, title: str=strings.LOGO_TITLE, 
                 blank_proceedure: Union[str, Callable]='return', 
                 decorator: Optional[Callable]=None):
        '''
        Input
        -----
        cases: 

        if given a module: module containing functions that serves as cases a 
        user can pick from terminal interface. the module should not implement
        any other functions. 
        
        if given a list: will simply use function in list as cases.

        First line of docstring becomes case description
        ALL CASES MUST CONTAIN DOCSTRINGS

        title: String to print over alternatives 

        blank_proceedure: What to do when given blank input (defaults to 
                          stopping current view (without exiting)). See 
                          docstring for menu() for more info.
        '''
        self.funcmap = construct_funcmap(cases, decorator=decorator)
        self.title = title

        if blank_proceedure == 'return':
            self.blank_hint = strings.INPUT_BLANK_HINT_RETURN
            self.blank_proceedure = self.__return_to_parent
        elif blank_proceedure == 'pass':
            self.blank_hint = strings.INPUT_BLANK_HINT_PASS
            self.blank_proceedure = self.__pass
        elif blank_proceedure == 'exit':
            self.blank_hint = strings.INPUT_BLANK_EXIT
            self.blank_proceedure = exit_program
        else:
            self.blank_proceedure = blank_proceedure

        # Special options
        self.special_cases = {
            '..':self.__return_to_parent,
            'q':exit_program,
            'h':print_help
        }

    def __return_to_parent(self):
        self.active = False
    
    def __pass(self):
        pass

    def _handle_case(self, casefunc: Callable, inputlist: List[str]):
        try:
            if inputlist:
                # Raises TypeError if wrong number of arguments 
                casefunc(*_handle_arglist(casefunc, inputlist))
            else:
                # Will raise TypeError if casefunc() actually 
                # requires arguments
                casefunc()
        except TypeError as e:
            _error_info(e, casefunc)

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

                # Empty string will evulate to False
                if self.blank_hint: 
                    print(self.blank_hint)
                
                inputstring = enter_prompt(strings.ENTER_PROMPT)

                # Pressing enter without specifying enables if test
                clear_screen()
                if not inputstring:
                    self.blank_proceedure()
                    continue

                # Tokenize input
                inputlist: List[str] = input_splitter(inputstring)
                # Get case
                case = inputlist.pop(0)

                # If case starts with '-', indicates reverse choice (like np.ndarray[-1])
                if case.startswith('-'):
                    try:
                        case = str(len(self.funcmap) + int(case) + 1)
                    except ValueError:
                        pass

                if case in self.funcmap:
                    # Obtain case function from funcmap and 
                    # calls said function. Recall that items are 
                    # (description, function), hence the [1]
                    casefunc = self.funcmap[case][1]
                    self._handle_case(casefunc, inputlist)
                elif case in self.special_cases:
                    # Items in special_cases are not tuples, but the 
                    # actual functions, so no need to do [1]
                    casefunc = self.special_cases[case]
                    self._handle_case(casefunc, inputlist)
                else:
                    print(strings.INVALID_TERMINAL_INPUT_MSG)
                    sleep(ccng.MSG_WAIT_TIME)

        except KeyboardInterrupt:
            # Ensures proper exit when Kbinterrupt
            exit_program()
    
def menu(cases: Union[List[Callable], Dict[str, Callable], ModuleType], 
         title: str=strings.DEFAULT_TITLE, blank_proceedure: Union[str, Callable]='return', 
         decorator: Optional[Callable]=None, run: bool=True, main: bool=False):
    '''
    Factory function for the CLI class. This function initializes a menu. 

    Parameters
    ------------
    cases: Can be output of locals() (a dictionary) from the scope of the cases 
           
           Or a list functions 

           Or a module containing the case functions

    title: title of menu

    blank_proceedure: What to do the when given blank input. Can be user defined
                      function, or it can be a string. Available string options
                      are:
                      
                      'return', will return to parent menu, if you are at main
                      menu, this will exit the program

                      'pass', does nothing. This should only be used for the 
                      main menu

                      'exit', exits the program

    decorator: Decorator for case functions

    run: To invoke .run() method on CLI object or not.

    main: Tells the function whether or not the menu is the main menu (i.e. the 
          first menu) or not. This is very import to specify when you give a 
          dictionary (e.g. the return value of locals()).

    Returns
    --------
    CLI (Command Line Interface) object. Use .run() method to activate menu. 
    '''
    if type(cases) == list:
        cases_to_send = cases
    elif type(cases) == dict:
        cases_to_send = list_local_cases(cases)
        # If this menu is the first menu initialized, and is given the locally
        # defined functions, then must filter the functions that are defined 
        # in __main__
        if main:
            cases_to_send =\
                [c for c in cases_to_send if c.__module__ == '__main__']
            blank_proceedure='pass'

    elif type(cases) == ModuleType:
        cases_to_send = cases
    else:
        raise TypeError('Invalid type')

    cli = CLI(cases=cases_to_send, title=title, 
              blank_proceedure=blank_proceedure, decorator=decorator)
    if run:
        cli.run()
    
    return cli