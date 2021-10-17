"""
How to implement:

Each case should be a function.
The ordering of the cases in the console interface
will be by the function definition orders.

Name of cases in menu interface will be the function names by default. One can specify alternative
titles by using the meny.case decorator

Feel free to import whatever

If you want to implement nested cases, then simply reuse the main function

Example
--------
from meny import menu

# Then you can either create another module with the nested cases:

import cases_nested

menu(cases_nested, title= ' Title here ').

or you can give a list functions:

def case3():
    def subcase1():
        pass

    def subcase2():
        pass

    meny.menu([subcase1, subcase2], title= ' Title here ')
"""

from time import sleep

import meny

import cases_nested

meny.set_default_frontend("fancy")


@meny.title("FizzBuzz!")
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
    sleep(1)


@meny.title("Append two strings")
def appendstrings(a: str, b: str):
    print(a + b)
    sleep(1)


@meny.title("A nested module menu")
def nestedmodulemenu():
    """
    This nested menu loads cases from a module
    """
    meny.menu(cases_nested, title=" Nested! ")


@meny.title("Math menu")
def mathmenu():
    """
    This nested menu gets the cases from a user defined list.
    """

    @meny.title("Multiply two floats")
    def multiply(x: float, y: float):
        print(x * y)
        sleep(1)

    @meny.title("Divide two floats")
    def divide(x: float, y: float):
        if y == 0:
            print("You can't divide by zero!!!")
            return

        print(x / y)
        sleep(1)

    meny.menu(locals(), title=" Quick maths ")


@meny.title("Even another nested menu")
def anothernested():
    """
    This menu obtains the nested case functions by
    sending the return value of locals() into meny.menu()
    """

    @meny.title("Print triangle")
    def triangle():
        for j in range(10):
            print("*" * j)
        sleep(1)

    @meny.title("Print rectangle")
    def rectangle():
        for i in range(10):
            print("#" * 10)
        sleep(1)


    @meny.title("Print list")
    def printlist(a: list):
        print(a)
        sleep(1)

    meny.menu(locals(), title=" Shapes ")

@meny.title("Programmatic arguments")
def programmatic(a, b, c, d):
    print(a, b, c, 4)
    sleep(1)


def just_function_name(arg: str = "Hello World"):
    print("This function does not use ppc.case decorator and therefore the menu only shows the name")
    print(f'Also, here is the input: "{arg}"')
    print("Press enter to return")
    input()


def simple_func(a=1, b: str="2", c=3.0):
    print(a, b, c)
    sleep(1)


if __name__ == "__main__":
    case_args = {programmatic: (1, 2)}
    case_kwargs = {programmatic: {"d": 4, "c": 3}}
    meny.menu(locals(), case_args=case_args, case_kwargs=case_kwargs)
