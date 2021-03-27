"""
Contains the command line interface (CLI) class, along its factory function:
menu()
"""

from time import sleep
import pypatconsole.strings as strings
import pypatconsole.config as cng
from pypatconsole.funcmap import construct_funcmap, _docstring_firstline
from pypatconsole.utils import clear_screen, input_splitter, list_local_cases, print_help
from typing import List, Tuple, Union, Callable, Dict, Optional
from inspect import getfullargspec, unwrap, signature
from types import ModuleType
from ast import literal_eval
import platform
import re

_PLATFORM = platform.system()
RE_ANSI = re.compile(r"\x1b\[[;\d]*[A-Za-z]")  # Taken from tqdm source code, matches escape codes

def raise_interrupt(*args, **kwargs) -> None:
    """
    Raises keyboard interrupt
    """
    raise KeyboardInterrupt


# Strategy method for special cases
# Cases that are not special are e.g. int, since you can directly
# use int() as a function
_SPECIAL_ARG_CASES = {
    str: lambda x: str(x.strip("\"'")),  # Removes outer " or ' characters
    tuple: literal_eval,
    list: literal_eval,
    dict: literal_eval,
    set: literal_eval,
}


class ConsoleError(Exception):
    """Custom exception for console related stuff"""


def _handle_arglist(func: Callable, arglist: list) -> List:
    """
    Handles list of strings that are the arguments
    The function turns the strings from the list into
    their designated types (found from function signature).

    E.g. return is [1, "cat", 2.0, False]
                   int  str   float  bool
    """
    # Unwrap in case the function is wrapped
    # TODO: Update this to use inspect.signature
    func = unwrap(func)
    argsspec = getfullargspec(func)
    args = argsspec.args
    argtypes = argsspec.annotations

    if len(args) > len(argtypes):
        raise NotImplementedError(f"Missing typehints in {func}")

    if len(arglist) > len(args):
        raise ConsoleError(f"Got too many arguments, should be {len(args)}, but got {len(arglist)}")

    # Special proceedures for special classes
    typed_arglist = []
    try:
        for arg, type_ in zip(arglist, argtypes.values()):
            if type_ in _SPECIAL_ARG_CASES:
                casted = _SPECIAL_ARG_CASES[type_](arg)
                assert isinstance(casted, type_), "Argument evaluated into wrong type"
                typed_arglist.append(casted)
            else:  # For cases such as int and float, which naturally handles string inputs
                typed_arglist.append(type_(arg))

    except (ValueError, AssertionError, SyntaxError) as e:
        raise ConsoleError(
            f'Could not cast argument "{arg}" into type "{type_}"\n'
            f"Got {type(e).__name__}:\n\t{e}"
        )

    return typed_arglist


def _error_info_case(error: Exception, func: Callable) -> None:
    """
    Used to handle error for cases

    Error: E.g. ValueError

    func: Function with docstring
    """
    selected_case_str = f'Selected case: "{strings.YELLOW+_docstring_firstline(func)+strings.END}"'
    lenerror = max(map(len, str(error).split("\n")))
    lenerror = max(lenerror, len(RE_ANSI.sub("", selected_case_str)))
    print(strings.BOLD + strings.RED + f"{' ERROR ':#^{lenerror}}" + strings.END)
    print(selected_case_str)
    print(f'{f" Error message ":=^{lenerror}}')
    print(error)
    print(f'{f"":=^{lenerror}}')
    print(f"Function signature: {signature(func)}")
    print()
    print(strings.INPUT_WAIT_PROMPT_MSG)
    input()


def _error_info_parse(error: Exception):
    lenerror = max(map(len, str(error).split("\n")))
    print(strings.BOLD + strings.RED + f"{' PARSE ERROR ':#^{lenerror}}" + strings.END)
    print(f'{f" Error message ":=^{lenerror}}')
    print(error)
    print(f'{f"":=^{lenerror}}')
    print()
    print(strings.INPUT_WAIT_PROMPT_MSG)
    input()


class CLI:
    """
    Command Line Interface class
    """

    def __init__(
        self,
        cases,
        title: str = strings.LOGO_TITLE,
        blank_proceedure: Union[str, Callable] = "return",
        on_kbinterrupt: str = "raise",
        decorator: Optional[Callable] = None,
        case_args: Optional[Dict[Callable, tuple]] = None,
        case_kwargs: Optional[Dict[Callable, dict]] = None,
        frontend: Optional[str] = "auto",
    ):
        """
        Input
        -----
        cases:

        if given a module: module containing functions that serves as cases a
        user can pick from terminal interface. the module should not implement
        any other functions.

        if given a list: will simply use function in list as cases.

        First line of docstring becomes case description
        ALL CASES MUST CONTAIN DOCSTRINGS

        title: String to print over alternatives

        blank_proceedure: What to do when given blank input (defaults to
                          stopping current view (without exiting)). See
                          docstring for menu() for more info.
        """
        self.funcmap = construct_funcmap(cases, decorator=decorator)
        self.title = title
        self.on_kbinterrupt = on_kbinterrupt
        self.case_args = case_args
        self.case_kwargs = case_kwargs

        if self.case_args is None:
            self.case_args = {}
        if self.case_kwargs is None:
            self.case_kwargs = {}

        if blank_proceedure == "return":
            self.blank_hint = strings.INPUT_BLANK_HINT_RETURN
            self.blank_proceedure = self._return_to_parent
        elif blank_proceedure == "pass":
            self.blank_hint = strings.INPUT_BLANK_HINT_PASS
            self.blank_proceedure = self._pass
        else:
            self.blank_proceedure = blank_proceedure

        # Special options
        self.special_cases = {"..": self._return_to_parent, "q": raise_interrupt, "h": print_help}

        if frontend == "auto":
            if _PLATFORM == "Windows":
                self._frontend = self._menu_simple
            elif _PLATFORM in ("Linux", "Darwin"):
                self._frontend = self._menu_curses
        elif frontend == "fancy":
            self._frontend = self._menu_curses
        elif frontend == "simple":
            self._frontend = self._menu_simple
        else:
            raise ValueError(f"Got unexpected specification for frontend: {self._frontend}")

    def _return_to_parent(self):
        self.active = False

    def _pass(self):
        pass

    def _handle_case(self, casefunc: Callable, inputlist: List[str]):
        args = self.case_args.get(casefunc, ())
        kwargs = self.case_kwargs.get(casefunc, {})

        try:
            if args or kwargs:  # If programmatic arguments
                if inputlist:
                    raise TypeError(
                        "This function takes arguments progammatically"
                        " and should not be given any arguments"
                    )
                casefunc(*args, **kwargs)
            elif inputlist:  # If user arguments
                # Raises TypeError if wrong number of arguments
                casefunc(*_handle_arglist(casefunc, inputlist))
            else:  # No arguments
                # Will raise TypeError if casefunc() actually
                # requires arguments
                casefunc()
        except (TypeError, ConsoleError) as e:
            _error_info_case(e, casefunc)

    def _menu_simple(self) -> str:
        # Import here to fix circular imports
        from pypatconsole import simple_interface

        return simple_interface.interface(self)

    def _menu_curses(self) -> str:
        # Import here to fix circular imports
        from pypatconsole import curses_interface

        return curses_interface.interface(self)

    def _menu_loop(self):
        """
        Menu loop
        """
        while self.active:
            inputstring: str = self._frontend()

            clear_screen()
            # Empty string to signal "return"
            if (not inputstring) or inputstring == "\n":
                self.blank_proceedure()
                continue

            # Tokenize input
            try:
                inputlist: List[str] = input_splitter(inputstring)
            except ValueError as e:  # Missing closing quotation or something
                _error_info_parse(e)
                continue

            # Get case
            case = inputlist.pop(0)

            # If case starts with '-', indicates reverse choice (like np.ndarray[-1])
            if case.startswith("-"):
                try:
                    case = str(len(self.funcmap) + int(case) + 1)
                except ValueError:
                    pass

            if case in self.funcmap:
                # Obtain case function from funcmap and
                # calls said function. Recall that items are
                # (description, function), hence the [1]
                casefunc = self.funcmap[case][1]
                self._handle_case(casefunc, inputlist)
            elif case in self.special_cases:
                # Items in special_cases are not tuples, but the
                # actual functions, so no need to do [1]
                casefunc = self.special_cases[case]
                self._handle_case(casefunc, inputlist)
            else:
                print(strings.INVALID_TERMINAL_INPUT_MSG)
                sleep(cng.MSG_WAIT_TIME)

    def run(self):
        """
        Runs menu loop within try except KeyboardInterrupt
        """
        self.active = True
        try:
            self._menu_loop()
        except KeyboardInterrupt:
            if self.on_kbinterrupt == "raise":
                self._return_to_parent()
                raise KeyboardInterrupt  # "Propagate exception"
            elif self.on_kbinterrupt == "return":
                print()
                return


def menu(
    cases: Union[List[Callable], Dict[str, Callable], ModuleType],
    title: str = strings.DEFAULT_TITLE,
    blank_proceedure: Union[str, Callable] = "return",
    on_kbinterrupt: str = "raise",
    decorator: Optional[Callable] = None,
    run: bool = True,
    main: bool = False,
    case_args: Optional[Dict[Callable, tuple]] = None,
    case_kwargs: Optional[Dict[Callable, dict]] = None,
    frontend: Optional[str] = None,
):
    """
    Factory function for the CLI class. This function initializes a menu.

    Parameters
    ------------
    cases: Can be output of locals() (a dictionary) from the scope of the cases

           Or a list functions

           Or a module containing the case functions

    title: title of menu

    blank_proceedure: What to do the when given blank input. Can be user defined
                      function, or it can be a string. Available string options
                      are:

                      'return', will return to parent menu

                      'pass', does nothing. This should only be used for the
                      main menu

    decorator: Decorator for case functions

    run: To invoke .run() method on CLI object or not.

    main: Tells the function whether or not the menu is the main menu (i.e. the
          first ("outermost") menu) or not. This is very import to specify when you give a
          dictionary (e.g. the return value of locals()).

    cases_args: Optional[Dict[Callable, tuple]], dictionary with function as key and tuple of
                positional arguments as values

    cases_kwargs: Optional[Dict[Callable, dict]], dictionary with function as key and dict of
                  keyword arguments as values

    frontend: str, specify desired frontend:
                    "auto": fancy frontend for Linux and Darwin, simple front end for Windows
                    "fancy": Will try to use fancy front end (if on Windows, install
                             windows-curses first or Python will not be able to find the required
                             "curses" package that the fancy frontend uses)
                    "simple": Use the simple (but compatible with basically everything) frontend
    Returns
    --------
    CLI (Command Line Interface) object. Use .run() method to activate menu.
    """
    if isinstance(cases, list):
        cases_to_send = cases
    elif isinstance(cases, dict):
        cases_to_send = list_local_cases(cases)
        # If this menu is the first menu initialized, and is given the locally
        # defined functions, then must filter the functions that are defined
        # in __main__
        if main:
            cases_to_send = [c for c in cases_to_send if c.__module__ == "__main__"]

    elif isinstance(cases, ModuleType):
        cases_to_send = cases
    else:
        raise TypeError("Invalid type")

    if main:
        blank_proceedure = "pass"
        on_kbinterrupt = "return"

    if frontend is None:
        frontend = cng.default_frontend

    cli = CLI(
        cases=cases_to_send,
        title=title,
        blank_proceedure=blank_proceedure,
        on_kbinterrupt=on_kbinterrupt,
        decorator=decorator,
        case_args=case_args,
        case_kwargs=case_kwargs,
        frontend=frontend,
    )
    if run:
        cli.run()

    return cli
