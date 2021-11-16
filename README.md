# Meny

A simple and sexy way to make an console interface

![If you see this text, then the gif is broken](https://media.giphy.com/media/SKUrfvxzbXkQ80gdMM/giphy.gif)
(the gif is a bit outdated at the moment)

## Table of contents

1. <a href="#how-to-setup">How to setup</a>
2. <a href="#note-for-windows-users">Note for Windows users</a>
3. <a href="#how-to-implement">How to implement</a>
    1. <a href="#simple-examples">Simple examples</a>
    2. <a href="#case-names">Case names</a>
    3. <a href="#special-cases">Special cases</a>
    4. <a href="#frontend-and-usage">Frontend and usage</a>
    5. <a href="#arguments">Arguments</a>
    6. <a href="#programmatic-arguments">Programmatic Arguments</a>
    7. <a href="#nested-cases">Nested cases</a>
    8. <a href="#return-values">Return values</a>
    9. <a href="#what-if-i-want-to-define-functions-without-having-them-displayed-in-the-menu">What if I want to define functions without having them displayed in the menu?</a>
    10. <a href="#optional-decorator">Optional: Decorator</a>
4. <a href="#why">Why</a>

# How to setup

First install the package with the command (make sure you have Python 3.7 or higher)

```
pip install meny
```

Then you can import `meny` in Python. The most central functions in this package are `meny.menu` and `meny.title`, which will be covered below.

This package has only been tested on Windows 10 and Ubuntu (18.04, 20.04) with Python 3.7, 3.8, and 3.9

## Note for Windows users

An original goal for this was to rely on built in Python packages only, which it does, for unix systems. This package requires the `curses` library to be available in order to use the "fancy frontend" (seen in the gif). It is built in the Linux and Mac installations, but not in Windows. meny will still work without `curses` as it also ships with a simple frontend that only uses the built in `print` function.

A way to get `curses` for Windows is to install `windows-curses`:
`pip install windows-curses`

I use Windows personally and `windows-curses` has worked fine so far. The `windows-curses` source code is availabe on github and [can be found here](https://github.com/zephyrproject-rtos/windows-curses).

# How to implement

Simply implement the cases (as functions) in a Python file, then to initialize the interface you simply use the `menu` function at the bottom

```python
from meny import menu

            .
            .
            .

menu(locals(), title=' Main menu title here ')
```

The `locals()` function is a Python built-in function which returns a dictionary with variable names as keys and the corresponding objects as values from the local scope. You can import whatever modules, classes and functions you want in the file without them interfering with the functions defined your file. The order of the cases is by definition order.

The function signature of `menu` along with its docstring is as follows:
Factory function for the CLI class. This function initializes a menu.
<a href="docstring"></a>

> <br/>
>
> ```python
> def menu(
>    cases: Union[Iterable[FunctionType], Dict[str, FunctionType], ModuleType],
>    title: Optional[str] = None,
>    *,
>    case_args: Optional[Dict[FunctionType, tuple]] = None,
>    case_kwargs: Optional[Dict[FunctionType, dict]] = None,
>    decorator: Optional[FunctionType] = None,
>    frontend: Optional[str] = None,
>    on_blank: Optional[str] = None,
>    on_kbinterrupt: Optional[str] = None,
>    once: Optional[bool] = None,
>    return_mode: Optional[bool] = None,
> ) -> Dict[str, Any]:
> ```
>
> ## Parameters
>
> -   `cases`: can be
>
>     -   a dictionary where keys are functions names and values are functions
>     -   an iterable of functions
>     -   a module containing functions
>
> -   `title`: title of menu
>
> -   `cases_args`: dictionary with function as key and tuple of positional arguments as values
>
> -   `cases_kwargs`: dictionary with function as key and dict of keyword arguments as values
>
> -   `once`: If you want menu to return after a a single choice.
>
> -   `on_blank`: What to do the when given blank input. Available options are:
>
>     -   `"return"`, will return to parent menu
>     -   `"pass"`, does nothing. This should only be used for the root menu.
>
> -   `on_kbinterrupt`: Behavior when encountering KeyboardInterrupt exception when the menu is running.
>     If `"raise"`, then will raise `KeyboardInterrupt`, if `"return"` the menu returns.
>
> -   `decorator`: Decorator to applied for all case functions.
>
> -   `frontend`: specify desired frontend:
>
>     -   `"auto"`: Will try to use fancy frontend if curses module is available, else
>         use simple frontend (default)
>     -   `"fancy"`: Use fancy front end (if on Windows, install
>         windows-curses first or Python will not be able to find the required
>         `"curses"` package that the fancy frontend uses)
>     -   `"simple"`: Use the simple (but compatible with basically everything) frontend
>
> -   `return_mode`: the dictionary structure to be returned after the menu is done running. Only effective
>     menu is root menu, as nested menus will use root's. Return mode options are:
>     -   `"flat"`: This is the default. Returns dictionary with function names (as `str`)
>         as keys, and their return values as values (if they are ran), if not their names
>         will not be in the dictinary (see examples). The downside of this return mode is if you have
>         nested menus, where the nested menus reuse function names that the parent menus have. The
>         parent menus may overwrite the return values from the nested menus.
>     -   `"tree"`: Returns a nested dictionary structure, representing the structure of nested menus
>         (if you have that).
>
> ## Returns
>
> Dictionary where functions names (strings) are keys, and values are anything. Represents return
> values of case functions.
>
> ## Examples
>
> ```python
> >>> def returnsOne():
> ...     def returnsOne():
> ...         return "1"
> ...     menu(locals())
> ...     return 1
> ...
> >>> def returnsTwo():
> ...     return 2
> ...
> >>> returns = menu(locals(), return_mode="flat") # Assume we have entered all cases
> { "returnsOne": 1, "returnsTwo": 2, }
> >>> returns = menu(locals(), return_mode="tree") # Assume we have entered all cases
> {
>    "returnsOne": {
>        "returnsOne": {
>            "return": "1"
>        }
>        "return": 1
>    },
>    "returnsTwo": {
>        "returns": 2
>    },
> }
> >>> returns["returnsOne"]["returnsOne"]["return"]
> '1'
> ```
>
> <br/>

## Simple examples

Say we are editing console.py

```python
from random import randint
from time import sleep
import meny

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

def random_integer():
    print(randint(0,9))
    sleep(1)

meny.menu(locals(), title=' Main menu ')
```

will result with this when running: `python console.py`:

```
-------------- Main menu ---------------
1. fizzbuzz
2. random_integer

Input:
```

You then specify which case you want to run by entering the input number as the first token. The tokens after (delimited by space) will be passed to the case function as positional arguments. The argument tokens will be evaluated as Python literals.

## Case names

By default it will use the function names as the case names. However you can use the `meny.title` decorator to apply a title that will be used instead:

```python
from random import randint
from time import sleep
import meny

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

meny.menu(locals(), title=' Main menu ')
```

Which will produce:

```
-------------- Main menu ---------------
1. FizzBuzz!
2. Get random integer

Input:
```

## Special cases

Entering `..` is equivalent to just pressing enter with an empty input. I implemented this because I just had
a habit of writing `..` to "change directory" to the previous directory.

Entering `q` will exit the menu interface.

Entering `h` will display this text that explains the special cases.

Enter `-1` or any integer will "reverse" the choices, such that you take the last choice. This is inspired by Python lists where you can index like `list[-1]`

## Frontend and usage

There are two frontends implemented; the simple frontend and the fancy frontend. The selection of frontend will be selected based on the detected operating system. One can pass the choice of frontend: `menu(..., frontend="auto")`. The possible choices are

-   `auto`: Will try to use the fancy front end (using `curses`) by checking if the `curses` module
    is available, else use simple frontend.
-   `simple`: Use simple frontend, should work on all systems since it is completely based on the
    build in print function. Use by typing the corresponding key (e.g. 1) to the displayed cases and press enter.
-   `fancy`: Use fancy frontend, will raise `ImportError` if `curses` is unavailable. The fancy
    frontend is "fancy" as in it gives visual indicators on what you are doing, and also adds
    the the ability to traverse the options using the arrow keys.

It possible to override the default frontend throughout the Python program by doing

```python
import meny
meny.set_default_frontend("auto") # auto, fancy, or simple
```

as opposed to specifying the choice of frontend for every `meny.menu(..., frontend="...")` call.

## Arguments

The cases can take arguments as well!

```python
import meny
from time import sleep

def addints(a, b):
    print(a+b)
    sleep(1)

def appendstrings(a, b):
    print(a+b)
    sleep(1)

# Type hints won't interfere with meny, and will actually be displayed when using the fancy frontend
@meny.title("Print elements and their types")
def displaylist(a: list):
    [print(f'Element {i}: {elem}, type: {type(elem)}') for i, elem in enumerate(a)]
    sleep(1)

meny.menu(locals(), title=' Main menu ')
```

Then simply give the arguments along with the choice:

```
-------------- Main menu ---------------
1. addints
2. appendstrings
3. Print elements and their types


Input: 1 60 9

69
```

```
Input: 2 "cat and dog" mathemathics

cat and dogmathemathics
```

```
Input: 3 ['cat', 69, 420.0]

Element 0: cat, type: <class 'str'>
Element 1: 69, type: <class 'int'>
Element 2: 420.0, type: <class 'float'>
```

## Programmatic Arguments

You can supply arguments programmtically to your case functions:

```python
import meny

def programmatic_args(a, b, c, d):
    print(a, b, c, d)
    sleep(1)

case_args = {programmatic_args: (1, 2)}
case_kwargs = {programmatic_args: {"d": 4, "c": 3}}
meny.menu(locals(), case_args=case_args, case_kwargs=case_kwargs)
```

Functions that takes arguments programmatically cannot take arguments through the cli, that is you cannot both supply programmatic arguments as well as arguments through the cli. In that case the menu will raisa a
MenuError.

## Nested cases

If you want to implement nested cases, then you can simply reuse the menu function in the function scope.

```python
from meny import menu

def parent():
    def child1():
        pass

    def child2():
        pass

    menu(locals(), title= ' Title here ')
menu(locals(), title=' Main menu ')
```

You can create another module for the other cases and pass them as well:

```python
from meny import menu
import other_cases

def samplecase():
    '''Foo'''
    menu(other_cases, title= ' Title here ')
menu(other_cases, title= ' Main menu ')
```

or you can give a list of functions, which will enable you to force the ordering of the cases as well:

```python
import meny

def parent2():
    def child1():
        pass

    def child2():
        pass

    meny.menu([subcase2, subcase1], title= ' Title here ')
meny.menu(locals(), title=' Main menu ')
```

## Return values

The menu will store the return values of the case functions (if have entered the cases). The usage
is explained in the <a name="#docstring">docstring</a>.

## What if I want to define functions without having them displayed in the menu?

Easy! Simply apply the `meny.ignore` decorator on functions to make `meny` ignore them. You can also create a class of static methods to hide functions within a class since classes will be ignored by `meny` anyways. This problem is also naturally avoided if just specifies the functions manually either using a `dict` or `list`.

```python
import meny
@meny.ignore
def ignored():
    pass
```

## Optional: Decorator

To enforce a common behavior when entering and leaving a case within a menu, you give a decorator to the `menu` function. However, it is important that the decorator implements the `__wrapped__` attribute (this is to handle docstrings of wrappers as arguments for wrapped functions). Generally, it should look like this

```python
import sleep
from functools import wraps

def case_decorator(func):
    '''Decorator to enforce commmon behavior for cases'''
    @wraps(func) # VERY IMPORTANT TO WRAP FUNCTIONS TO ENSURE THAT
                 # case_wrapper.__wrapped__ is set properly
    def case_wrapper(*args, **kwargs):
        '''Verbosity wrapper'''
        print('Yeah! Going in!')
        sleep(1)
        retobj = func(*args, **kwargs)
        print('Woah! Going out!')
        sleep(1)
        return retobj
    return case_wrapper
```

It can then easily be applied to all functions like so:

```python
from meny import menu
from case_decorator import case_decorator

# A lot of cases here

menu(locals(), decorator=case_decorator)
```

# Why

Sometimes you want to have a simple console interface so you can do things step by step. I specifically
designed meny to be good at creating menus from existing code with the least interference.
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

Sometimes I don't want to run everything at once. Maybe I just want to backup data instead of doing all everything. `meny` will enable a very quick implementation of a console.
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

## Control your Google Compute VM

```
----------------GCE-----------------
1. SSH to personal instance
2. SSH to project instance
3. start/stop personal instance (0 to stop, 1 to start, 2 to restart)
4. start/stop project instance (0 to stop, 1 to start, 2 to restart)
5. Get status personal instance
6. Get status project instance
7. Other instance control

Entering blank returns to parent menu
Input:
```
