![badge](https://github.com/Napam/meny/actions/workflows/pushpull.yml/badge.svg)
![badge](https://github.com/Napam/meny/actions/workflows/publish.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/meny.svg)](https://badge.fury.io/py/meny)

# Meny

Meny is a super light weight framework for creating CLI menus. (the gif is a bit outdated at the moment)

![If you see this text, then the gif is broken](https://media.giphy.com/media/SKUrfvxzbXkQ80gdMM/giphy.gif)

### Imagine this:
1. You have implemented some functions in some Python file (regardless of the intention of creating a CLI menu).
1. Then you realize it would be nice to have a CLI interface to call said functions.

Today is your lucky day! Because Meny is especially designed for this scenario! (which I have encountered surprisingly many times, hence this package). Just install and import `meny` and do
```
meny yourfile.py
```
You can also use `meny` programmatically as a package, of which this README will cover most of its usage.

### But why exactly this package?
There already exists python packages to do so, but seemingly all of them require you to *refactor* your code in order to use them, and you need to *learn* how to use their APIs, which is kind of annoying since you just want an convenient interface for your functions. You don't want to spend even more to time to learn yet another library, let alone refactor your code for a CLI menu. With `meny` you can use the command `meny` or add `meny.menu(locals())` to the bottom of your Python file and you are good to go.

Of course, this package can do much more which you can see below, but its intention is to cover the "It would be nice to just have a cli menu for my functions now, but its too much effort to make / learn another library" scenario, which I believe it does well.

## Table of contents

1. <a href="#_meny_setup">How to setup</a>
2. <a href="#_meny_noteWindows">Note for Windows users</a>
3. <a href="#_meny_commandlineInterfcae">Command-line Interface</a>
4. <a href="#_meny_programmaticInterface">Programmatic interface</a>
    1. <a href="#_meny_simpleExamples">Simple examples</a>
    2. <a href="#_meny_caseNames">Case names</a>
    3. <a href="#_meny_frontend">Frontend and usage</a>
    4. <a href="#_meny_specialCases">Special cases</a>
    5. <a href="#_meny_arguments">Arguments</a>
    6. <a href="#_meny_progArguments">Programmatic Arguments</a>
    7. <a href="#_meny_nested">Nested cases</a>
    8. <a href="#_meny_return">Return values</a>
    9. <a href="#_meny_ignore">What if I want to define functions without having them displayed in the menu?</a>
    10. <a href="#_meny_decorator">Optional: Decorator</a>
5. <a href="#_meny_realExamples">Real examples</a>

# How to setup <a id="_meny_setup"></a>

First install the package with the command (make sure you have Python 3.7 or higher)

```
pip install meny
```

Then you can import `meny` in Python. This will make `meny` available in your shell. For programmatic use the most central functions in this package are **`meny.menu`** and **`meny.title`**, which will be covered below.

This package has been tested on Windows 10, Windows 11, MacOS (idk which version that was), and Ubuntu (18.04, 20.04, 22.04) with Python 3.7, 3.8, 3.9, 3.10

## Note for Windows users <a id="_meny_noteWindows"></a>

TL;DR: If you want to have the fancy frontend (like in the gif) do

```
pip install windows-curses
```

An original goal for this package was to rely on built-in Python packages only, which it does, for Linux and Mac. This package requires the `curses` library to use the fancy frontend. It is built-in with CPython for Linux and Mac installations but not in Windows. `meny` will still work without `curses` as it also ships with a simple frontend that only uses the built-in `print` function.

A way to get `curses` for Windows is to install `windows-curses`:
`pip install windows-curses`

I use Windows personally and `windows-curses` has worked fine so far. The `windows-curses` source code is availabe on github and [can be found here](https://github.com/zephyrproject-rtos/windows-curses).

# Command-line interface <a id="_meny_commandlineInterface"></a>
As mentioned above, you can do `meny your_python_file.py` in your terminal and it will parse the file and present its functions. For example you have the file `os_example.py`:
```python
import platform

def print_os():
    operating_system = platform.system()
    print(f"Your operating is {platform.system()}")
    return operating_system
```
Then you can do
```
meny print_os
```
and you will see
```
---- Functions in os_example.py ----
1. print_os
```
If you select `print_os`, the function will be executed and you will see its output and also return value in your terminal:
```
Your operating system is Linux
'Linux'
```

# Programmatic Interface <a id="_meny_programmaticInterface"></a>

Simply implement the menu cases (as functions) in a Python file, then to initialize the interface you simply call the `menu` function after you have defined your functions.

```python
from meny import menu

            .
            .
            .

menu(locals(), title=' Main menu title here ')
```

The `locals()` function is a Python built-in function that returns a dictionary with variable names as keys and the corresponding objects as values from the local scope. You can import whatever modules, classes, and functions you want in the file without them interfering with the functions defined in your file. The order of the cases is by definition order.

The function signature of `menu` along with its docstring is as follows:
Factory function for the CLI class. This function initializes a menu.
<a id="_meny_docstring"></a>

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
>    return_mode: Optional[str] = None,
> ) -> Dict[str, Any]:
> ```
>
> ## Parameters
>
> -   `cases`: can be
>
>     -   `Dict[str, FunctionType]`: a dictionary where keys are functions names and values are functions
>     -   `Iterable[FunctionType]` an iterable of functions
>     -   `ModuleType`: a module containing functions
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
>         as keys, and their return values as values (if they have been called), if not their names
>         will not be in the dictionary (see examples). The downside of this return mode is if you have
>         nested menus, where the nested menus reuse function names in from parent menus. The
>         parent menus may overwrite the return values from the nested menus.
>     -   `"tree"`: Returns a nested dictionary structure, representing the structure of nested menus
>         (if you have that).
>
> ## Returns
>
> `Dict[str, Any]`: Dictionary where functions names are keys, and values are anything. Represents return
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
> >>> returns = menu(locals(), return_mode="flat") # Assume we have entered all cases and returned
> { "returnsOne": 1, "returnsTwo": 2, }
> >>> returns = menu(locals(), return_mode="tree") # Assume we have entered all cases and returned
> {
>    "returnsOne": {
>        "returnsOne": {
>            "return": "1"
>        },
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

## Simple examples <a id="_meny_simpleExamples"></a>

Say we are editing `console.py`

```python
from random import randint
from time import sleep
import meny

# fizzbuzz() and random_integer() are just examples, you can make whatever you want :)

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

## Frontend and usage <a id="_meny_frontend"></a>

There are two frontends implemented; the simple frontend and the fancy frontend. The selection of frontend will be selected based on the detected operating system. One can pass the choice of frontend: `menu(..., frontend="auto")`. The possible choices are

-   `auto`: Will try to use the fancy front end (using `curses`) by checking if the `curses` module is available, else use simple frontend.
-   `simple`: Use simple frontend, should work on all systems since it is completely based on the built-in print function. Use by typing the corresponding key (e.g. 1) to the displayed cases and press enter.
-   `fancy`: Use fancy frontend, will raise `ImportError` if `curses` is unavailable. The fancy frontend is "fancy" as in it gives visual indicators on what you are doing, and also adds the ability to traverse the options using the **arrow keys**.

It is possible to override the default frontend throughout the Python program by doing

```python
import meny
meny.set_default_frontend("auto") # auto, fancy, or simple
```

as opposed to specifying the choice of frontend for every `meny.menu(..., frontend="...")` call.

## Case names <a id="_meny_caseNames"></a>

By default, it will use the function names as the case names. However, you can use the `meny.title` decorator to apply a title that will be used instead:

```python
from random import randint
from time import sleep
import meny

# fizzbuzz() and random_integer() are just example functions, you can make anything you want.

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

## Special cases <a id="_meny_specialCases"></a>

Entering `..` is equivalent to just pressing enter with an empty input. I implemented this because I just had
a habit of writing `..` to "change directory" to the previous directory.

Entering `q` will exit the menu interface.

Entering `h` will display this text that explains the special cases.

Enter `-1` or any integer will "reverse" the choices, such that you take the last choice. This is inspired by Python lists where you can index like `list[-1]`

Entering `r` will restart the *whole* Python program. This is usefull when debugging such that one can easily refresh code changes.

## Arguments <a id="_meny_arguments"></a>

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

## Programmatic Arguments <a id="_meny_progArguments"></a>

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

Functions that takes arguments programmatically cannot take arguments through the cli, that is you cannot both supply programmatic arguments as well as arguments through the cli. In that case the menu will raisa a MenuError.

## Nested cases <a id="_meny_nested"></a>

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

## Return values <a id="_meny_return"></a>

The menu will store the return values of the case functions (if you have entered the cases). The usage
is explained in the <a href="#_meny_docstring">docstring</a>.

## What if I want to define functions without having them displayed in the menu? <a id="_meny_ignore"></a>

Easy! Simply apply the `meny.ignore` decorator on functions to make `meny` ignore them. You can also create a class of static methods to hide functions within a class since classes will be ignored by `meny` anyways. This problem is also naturally avoided if just specifies the functions manually either using a `dict` or `list`.

```python
import meny
@meny.ignore
def ignored():
    pass
```

## Optional: Decorator <a id="_meny_decorator"></a>

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

# Real examples <a id="_meny_realExamples"></a>
Here are some applications that I have implemented using `meny`:

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
