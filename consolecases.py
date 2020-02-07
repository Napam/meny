'''
File containing cases for console interface

Each case should be a function.
The ordering of the cases in the console interface
will be by the function names. So a() will be 
first then b() etc.

Name of cases in console interface will be first line of 
docstring

Feel free to import whatever
'''
from random import randint
from time import sleep

def case1():
    '''
    Print a random integer
    '''
    print(randint(0,9))

def case2():
    '''
    Print Hello World
    '''
    print('Hello world!')

def case3():
    '''
    FizzBuzz!

    When you get the urge to fizz your buzz
    '''
    for i in range(21):
        stringy = ''

        fizzcase = True if i % 3 == 0 else False
        buzzcase = True if i % 5 == 0 else False
        
        if fizzcase:
            stringy = stringy + 'Fizz'
        if buzzcase:
            stringy = stringy + 'Buzz'
        if not (fizzcase or buzzcase):
            stringy = i

        print(stringy) 
        sleep(0.1)

