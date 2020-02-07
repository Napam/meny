'''
Example module for nested cases 
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
