# PyPat-Console
Simple but sexy framework for console interface 


# What to run
```
# For Windows/Mac
python console.py

# For Linux
python3 console.py
```
There are sample functions implemented. 

# How to implement
Simply implement the cases (as functions) in consolecases.py. You can import whatever you want in there. You will need to implement docstrings to every case. The first line of of text in the docstring will be used as the description in the console interface. 

The order of the cases is alphabetically sorted by the function name. 

The rest of the code will automatically integrate the function to the console interface without you needing to worry about anything.

For example implementing this in consolecases.py:
```python
from random import randint
from time import sleep

def case1():
    '''
    FizzBuzz!

    When you get the urge to fizz your buzz 
    if you know what I mean
    '''
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

def case2():
    '''
    Print a small random integer 
    '''
    print(randint(0,9))
    sleep(0.5)
```

will result with this when running ```python console.py```:

```
-------------- Main menu ---------------
1. FizzBuzz!
2. Print a small random integer
3. Exit program

Entering blank returns/exits
Enter choice:
```

## Nested cases
If you want to implement nested cases, then simply import 
the CLI (command line interface) class from consoleobject.py:
```python
from consoleobject import CLI
```
then you can either create another module for the nested cases:
```python
import other_cases

def samplecase():
    '''Foo'''
    CLI(other_cases, title= ' Title here ').run()
```

or you can give a list of functions:

```python
def samplecase():
    '''Bar'''
    def subcase1():
        '''docstring1'''
        pass

    def subcase2():
        '''docstring2'''
        pass

    CLI([subcase1, subcase2], title= ' Title here ').run()
```

## Optional: Decorator
The case functions are decorated to enforce a common behavior of all cases. For example that the program should wait a little when exiting a case function. The decorator can be changed in consoledecorator.py

# Why
Sometimes you want to have a simple console interface so you can do things step by step. 
Here are some applications:

## Stock data pipeline
Data scraping and data cleaning pipeline for stock data
```
------------- Mulababy420 --------------
1. Update all data
2. Obtain Oslo Bors quotes and returns
3. Scrape Oslo bors HTML files
4. Scrape Yahoo Finance
5. Backup current data
6. Exit program
Enter choice: 
```
Sometimes I don't want to run everything at once. Maybe I just want to backup data instead of doing all everything. This framework will enable a very quick implementation of a console. 
Without the console I would need to find the right file to run (and maybe comment things out first as well). The console organizes everything into one place. 

## Database interface
```
------BergenDB------
1. Log rent
2. Log power
3. Print table
4. Plot table
5. Commit changes
6. Discard changes
7. Exit
```
I log my rent and power bills in a SQL database. I have made a Python API to manage the database, and I just do everything through the interface. No need to script anything or write any SQL queries.