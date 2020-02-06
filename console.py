import consolestrings as strings
import time 
import consoleconfig as ccng 
import consolecases
from os import system
from funcmap import construct_funcmap, print_funcmap
from consolecommon import clear_screen

def logo_title(title: str):
    '''Prints logo title'''
    print("{:-^40s}".format(title))

def start_menu(funcmap: dict):
    '''Prints function map prettily'''
    logo_title(strings.LOGO_TITLE)
    print_funcmap(funcmap)

def enter_prompt():
    '''Prints enter prompt message and than returns input()'''
    print(strings.ENTER_PROMPT, end=' ')
    return input()

def case_decorator(func):
    '''Decorator to enforce commmon behavior for cases'''
    def wrapboi(*args, **kwargs):
        clear_screen()
        retobj = func(*args, **kwargs)
        time.sleep(ccng.CASE_EXIT_WAIT_TIME) 
        return retobj

    # "Inherit" docstring
    wrapboi.__doc__ = func.__doc__
    return wrapboi

def exit_program():
    '''
    Exit program
    '''
    print(strings.EXIT_MSG)
    time.sleep(ccng.MSG_WAIT_TIME)
    clear_screen()
    exit()

def main_interface():
    '''
    Main function for console interface
    '''
    print(strings.START_MSG)
    funcmap = construct_funcmap(consolecases, [exit_program], case_decorator)
    
    run = 1
    try:
        while run:
            clear_screen()
            start_menu(funcmap)

            # Get key to func map
            command = enter_prompt()  

            # Pressing enter without specifying input exits program
            if not command:
                clear_screen()
                exit_program()

            clear_screen()
            if command in funcmap:
                funcmap[command][1]()
            else:
                print(strings.INVALID_TERMINAL_INPUT_MSG)
                time.sleep(ccng.MSG_WAIT_TIME)

    except KeyboardInterrupt:
        # Ensures proper exit when Kbinterrupt
        exit_program()

if __name__ == '__main__':
    main_interface()
    