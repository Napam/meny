'''
Run this file to run console 
'''
from time import sleep
import consolestrings as strings
import consoleconfig as ccng 
from funcmap import construct_funcmap, print_funcmap
from consolecommon import clear_screen
from typing import Union, Callable

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

class CLI:
    '''
    Command Line Interface class 
    '''
    def __init__(self, cases, title: str=strings.LOGO_TITLE, blank_proceedure: Union[str, Callable]='return', 
                decorator: Callable=None):
        '''
        Input
        -----
        module: module containing functions that serves as cases a user can pick from terminal interface.
                The module should not implement any other functions

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
                command = enter_prompt(strings.ENTER_PROMPT)  

                # Pressing enter without specifying enables if test
                clear_screen()
                if not command:
                    self.blank_proceedure()
                    continue

                # Obtain case function from funcmap and 
                # calls said function. Recall that items are 
                # (description, function), hence the [1]
                if command in self.funcmap:
                    self.funcmap[command][1]()
                else:
                    print(strings.INVALID_TERMINAL_INPUT_MSG)
                    sleep(ccng.MSG_WAIT_TIME)

        except KeyboardInterrupt:
            # Ensures proper exit when Kbinterrupt
            exit_program()
    