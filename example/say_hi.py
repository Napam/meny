"""
Meant to illustrate usage of meny terminal command on 
a script with functions that has arguments
"""

def say_hi(n: int):
    """Say 'hi' n times"""
    for i in range(n):
        print('hi')

def greet(name: str):
    print("Hello " + name)