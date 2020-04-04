'''
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
        \'''docstring1\'''
        pass

    def subcase2():
        \'''docstring\'''
        pass

    menu([subcase1, subcase2], title= ' Title here ')
'''

# To enable import from parent folder
from time import sleep
import consolecases_nested
from pypatconsole import menu 

def case1(n: int=20, waittime: float=0.1):
    '''
    FizzBuzz!

    When you get the urge to fizz your buzz 
    if you know what I mean
    '''
    for i in range(n+1):
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
        sleep(waittime)

def case2(a: str, b: str):
    '''
    Append two strings
    '''
    print(a+b)
    sleep(0.5)

def case3():
    '''
    A nested menu 

    This nested menu loads cases from a module
    '''
    menu(consolecases_nested, title=' Nested! ')

def case4():
    '''
    Math menu

    This nested menu gets the cases from a user defined list.
    '''
    def subcase1(x: float, y: float):
        '''
        Multiply two floats
        '''
        print(x*y)
        sleep(0.5)

    def subcase2(x: float, y: float):
        '''
        Divide two floats
        '''
        if y == 0:
            print("You can't divide by zero!!!")
            sleep(0.5)
            return 

        print(x/y)
        sleep(0.5)
    menu([subcase1, subcase2], title=' Quick maths ')

def case5():
    '''
    Even another nested menu

    This menu obtains the nested case functions by 
    sending the return value of locals() into menu()
    '''
    def subcase1():
        '''
        Print triangle
        '''
        for j in range(10):
            print('*' * j)

        sleep(0.5)

    def subcase2():
        '''
        Print rectangle
        '''
        for i in range(10):
            print('#' * 10)

        sleep(0.5)

    menu(locals(), title=' Shapes ')

menu(locals(), main=True, blank_proceedure='pass')