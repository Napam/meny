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

from pypatconsole import menu

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

# To enable import from parent folder
from time import sleep
import cases_nested
import pypatconsole as ppc
from pypatconsole import menu

ppc.config.default_frontend = "auto"  # Set default frontend here


@ppc.case("FizzBuzz!")
def case1(n: int = 10, waittime: float = 0.1):
    """
    When you get the urge to fizz your buzz
    if you know what I mean
    """
    for i in range(n + 1):
        stringy = ""

        fizz = i % 3 == 0
        buzz = i % 5 == 0

        if fizz:
            stringy = stringy + "Fizz"
        if buzz:
            stringy = stringy + "Buzz"
        if not (fizz or buzz):
            stringy = i

        print(stringy)
        sleep(waittime)


@ppc.case("Append two strings")
def case2(a: str, b: str):
    print(a + b)
    sleep(0.5)


@ppc.case("A nested module menu")
def case3():
    """
    This nested menu loads cases from a module
    """
    menu(cases_nested, title=" Nested! ")


@ppc.case("Math menu")
def case4():
    """
    This nested menu gets the cases from a user defined list.
    """

    @ppc.case("Multiply two floats")
    def subcase1(x: float, y: float):
        print(x * y)
        sleep(0.5)

    @ppc.case("Divide two floats")
    def subcase2(x: float, y: float):
        if y == 0:
            print("You can't divide by zero!!!")
            sleep(0.5)
            return

        print(x / y)
        sleep(0.5)

    menu(locals(), title=" Quick maths ")


@ppc.case("Even another nested menu")
def case5():
    """
    This menu obtains the nested case functions by
    sending the return value of locals() into menu()
    """

    @ppc.case("Print triangle")
    def subcase1():
        for j in range(10):
            print("*" * j)

        sleep(0.5)

    @ppc.case("Print rectangle")
    def subcase2():
        for i in range(10):
            print("#" * 10)

        sleep(0.5)

    @ppc.case("Print list")
    def subcase3(a: list):
        print(a)
        sleep(0.5)

    menu(locals(), title=" Shapes ")


@ppc.case("Programmatic arguments")
def case6(a, b, c, d):
    print(a, b, c, 4)
    sleep(0.5)


def just_function_name(arg: str = "Hello World"):
    print("This function does not use ppc.case decorator and therefore the menu only shows the name")
    print(f'Also, here is the input: "{arg}"')
    print("Press enter to return")
    input()


if __name__ == "__main__":
    case_args = {case6: (1, 2)}
    case_kwargs = {case6: {"d": 4, "c": 3}}
    menu(locals(), main=True, case_args=case_args, case_kwargs=case_kwargs)
