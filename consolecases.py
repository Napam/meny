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
from importlib import reload
import sys 

def a_sample_case1():
    '''
    Get a random integer
    '''
    print(randint(0,9))
    sleep(0.5)

def a_sample_case2():
    '''
    Print Hello World
    '''
    print('Hello world!')
    sleep(0.5)
