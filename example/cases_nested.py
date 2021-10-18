"""
Example module for nested cases 
"""
from time import sleep

import meny


def print_elements_and_types(a: list):
    [print(f"Element {i}: {elem}, type: {type(elem)}") for i, elem in enumerate(a)]
    sleep(1)


def nested_module_menu():
    def abacus():
        print("ABACUS!")
        sleep(1)

    meny.menu(locals())
