from random import randint
from time import sleep
import meny

meny.set_default_frontend("simple")

@meny.title("FizzBuzz!")
def fizzbuzz():
    for i in range(21):
        stringy = ''

        fizz = i % 3 == 0
        buzz = i % 5 == 0

        if fizz:
            stringy = stringy + 'Fizz'
        if buzz:
            stringy = stringy + 'Buzz'
        if not (fizz or buzz):
            stringy = i

        print(stringy)
        sleep(0.1)

@meny.title("Get random integer")
def random_integer():
    print(randint(0,9))
    sleep(1)

def add_ints(a, b):
    print(a+b)
    sleep(1)

def append_strings(a, b):
    print(a+b)
    sleep(1)

# Type hints won't interfere with meny, and will actually be displayed when using the fancy frontend
@meny.title("Print elements and their types")
def print_types_in_list(a: list): 
    [print(f'Element {i}: {elem}, type: {type(elem)}') for i, elem in enumerate(a)]
    sleep(1)


def programmatic_args(a, b, c, d):
    print(a, b, c, d)
    sleep(1)

case_args = {programmatic_args: (1, 2)}
case_kwargs = {programmatic_args: {"d": 4, "c": 3}}
meny.menu(locals(), title=' Main menu ', case_args=case_args, case_kwargs=case_kwargs)