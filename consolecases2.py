'''
File containing cases for console interface

Each case should be a function.
The ordering of the cases in the console interface
will be by the function names. So a() will be 
first then b() etc.

Name of cases in console interface will be first line of 
docstring

Feel free to import whatever
'''
from random import randint
from time import sleep

def case1():
    '''
    Print a large random integer 
    '''
    print(randint(1e3, 1e9))
    sleep(0.5)

def case2():
    '''
    Print money
    '''
    print('$$$ Mula $$$')
    sleep(0.5)
