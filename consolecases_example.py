'''
Example module for nested cases 
'''
from random import randint
from time import sleep

def case1(a: list):
    '''
    Print elements in list and their types
    '''
    [print(f'Element {i}: {elem}, type: {type(elem)}') for i, elem in enumerate(a)]
    sleep(1)

def case2():
    '''
    Get money
    '''
    print('$$$$$$')
    sleep(0.5)
