'''
Example module for nested cases 
'''
from time import sleep

def print_elements_and_types(a: list):
    [print(f'Element {i}: {elem}, type: {type(elem)}') for i, elem in enumerate(a)]
    sleep(1)

