'''
Example module for nested cases 
'''
from random import randint
from time import sleep
from tqdm import tqdm

def case1():
    '''
    Print a large random integer 
    '''
    print(randint(1e3, 1e9))
    sleep(0.5)

def case2():
    '''
    Get money
    '''
    print('Getting fat stacks:')
    for i in tqdm(range(100)):
        sleep(0.01)
