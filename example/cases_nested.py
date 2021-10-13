'''
Example module for nested cases 
'''
from time import sleep
import pypatconsole as ppc

@ppc.case("Huehue1")
def print_elements_and_types(a: list):
    [print(f'Element {i}: {elem}, type: {type(elem)}') for i, elem in enumerate(a)]
    sleep(1)

@ppc.case("Huehue2")
def print_elements_and_types2(a: list):
    [print(f'Element {i}: {elem}, type: {type(elem)}') for i, elem in enumerate(a)]
    sleep(1)

