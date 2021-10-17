"""
How to implement:

Each case should be a function.
The ordering of the cases in the console interface
will be by the function names. So a() will be 
first then b() etc.

Name of cases in console interface will be first line of 
docstring

Feel free to import whatever

If you want to implement nested cases, then simply import 
reuse the main function

from meny import menu

then you can either create another module with the nested 
cases:

menu(consolecases_nested, title= ' Title here ').

or you can give a list functions:

def case3():
    def subcase1():
        '''docstring1'''
        pass

    def subcase2():
        '''docstring'''
        pass

    menu([subcase1, subcase2], title= ' Title here ')
"""

from functools import wraps
from time import sleep

import meny
from meny import menu

import cases_nested

meny.config.default_frontend = "fancy"  # Set default frontend here


@meny.case("FizzBuzz!")
def fizzbuzz(n: int = 10, waittime: float = 0.1):
    """
    When you get the urge to fizz your buzz
    if you know what I mean
    """
    for i in range(n + 1):
        stringy = ""

        fizz = i % 3 == 0
        buzz = i % 5 == 0

        if fizz:
            stringy += "Fizz"
        if buzz:
            stringy += "Buzz"
        if not (fizz or buzz):
            stringy = i

        print(stringy)
        sleep(waittime)


@meny.case("Append two strings")
def appendstrings(a: str, b: str):
    print(a + b)


@meny.case("A nested module menu")
def nestedmodulemenu():
    """
    This nested menu loads cases from a module
    """
    menu(cases_nested, title=" Nested! ")


@meny.case("Math menu")
def mathmenu():
    """
    This nested menu gets the cases from a user defined list.
    """

    @meny.case("Multiply two floats")
    def multiply(x: float, y: float):
        print(x * y)

    @meny.case("Divide two floats")
    def divide(x: float, y: float):
        if y == 0:
            print("You can't divide by zero!!!")
            return

        print(x / y)

    menu(locals(), title=" Quick maths ")


@meny.case("Even another nested menu")
def anothernested():
    """
    This menu obtains the nested case functions by
    sending the return value of locals() into menu()
    """

    @meny.case("Print triangle")
    def triangle():
        for j in range(10):
            print("*" * j)


    @meny.case("Print rectangle")
    def rectangle():
        for i in range(10):
            print("#" * 10)


    @meny.case("Print list")
    def printlist(a: list):
        print(a)

    menu(locals(), title=" Shapes ")

@meny.case("Programmatic arguments")
def programmatic(a, b, c, d):
    print(a, b, c, 4)


def just_function_name(arg: str = "Hello World"):
    print("This function does not use ppc.case decorator and therefore the menu only shows the name")
    print(f'Also, here is the input: "{arg}"')
    print("Press enter to return")
    input()

import time 
@meny.ignore
def wait(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        time.sleep(0.5)
    return wrapper

def lolfunc(a=1, b: str="2", c=3.0):
    print(a, b, c)


if __name__ == "__main__":
    case_args = {programmatic: (1, 2)}
    case_kwargs = {programmatic: {"d": 4, "c": 3}}
    menu(locals(), case_args=case_args, case_kwargs=case_kwargs, decorator=wait)
    # menu([lolfunc], case_args=case_args, case_kwargs=case_kwargs, decorator=wait)
