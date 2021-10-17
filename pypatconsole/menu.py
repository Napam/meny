"""
Contains the command line interface (CLI) class, along its factory function:
menu()
"""

import enum
import re
from ast import literal_eval
from inspect import (getfullargspec, getmembers, getmodule, isfunction,
                     signature, unwrap)
from time import sleep
from types import FunctionType, ModuleType
from typing import Callable, Dict, Iterable, List, Optional, Union

import pypatconsole.config as cng
import pypatconsole.strings as strings
from pypatconsole.config import _CASE_IGNORE
from pypatconsole.funcmap import _get_case_name, construct_funcmap
from pypatconsole.utils import (RE_ANSI, clear_screen, input_splitter,
                                list_local_cases, print_help)


def raise_interrupt(*args, **kwargs) -> None:
    """
    Raises keyboard interrupt
    """
    raise KeyboardInterrupt


class MenuError(Exception):
    """
    Custom exception for console related stuff since I dont want to catch too many exceptions
    from Python.
    """


class MenuQuit(Exception):
    """
    For exiting all console instances
    """


def _handle_args(func: Callable, args: Iterable) -> List:
    """
    Handles list of strings that are the arguments using ast.literal_eval. 

    E.g. return is [1, "cat", 2.0, False]
                   int  str   float  bool
    """
    # Unwrap in case the function is wrapped
    # TODO: Update this to use inspect.signature
    func = unwrap(func)
    argsspec = getfullargspec(func)
    params = argsspec.args

    if len(args) > len(params):
        raise MenuError(
            f"Got too many arguments, should be {len(params)}, but got {len(args)}"
        )

    typed_arglist = [None] * len(args)
    try:
        for i, arg in enumerate(args):
            typed_arglist[i] = literal_eval(arg)
    except (ValueError, SyntaxError) as e:
        raise MenuError(f"Got arguments: {args}\n"
                        f"But could not evaluate argument at position {i}:\n\t {arg}") from e
    return typed_arglist


def _error_info_case(error: Exception, func: Callable) -> None:
    """
    Used to handle error for cases

    Error: E.g. ValueError

    func: case function
    """
    selected_case_str = (
        f'Selected case: "{strings.YELLOW+_get_case_name(func)+strings.END}"\n'
        f'Case function: "{strings.YELLOW+str(func)+strings.END}"\n'
        f"Function signature: {signature(func)}"
    )
    lenerror = max(map(len, str(error).split("\n")))
    lenerror = max(lenerror, max(map(len, RE_ANSI.sub("", selected_case_str).split("\n"))))
    print(strings.BOLD + strings.RED + f"{' ERROR ':#^{lenerror}}" + strings.END)
    print(selected_case_str)
    print(f'{f" Error message ":=^{lenerror}}')
    print(error)
    print(f'{f"":=^{lenerror}}')
    print()
    print(strings.INPUT_WAIT_PROMPT_MSG)
    input()


def _error_info_parse(error: Exception):
    lenerror = max(map(len, str(error).split("\n")))
    print(strings.BOLD + strings.RED + f"{' ARGUMENT PARSE ERROR ':#^{lenerror}}" + strings.END)
    print(f'{f" Error message ":=^{lenerror}}')
    print(error)
    print(f'{f"":=^{lenerror}}')
    print()
    print(strings.INPUT_WAIT_PROMPT_MSG)
    input()


class Menu:
    """
    Command Line Interface class
    """

    # Menu depth counter to keep track of how many nested menus are running. This will work across
    # modules since Python modules doubles as singletons.
    _depth: int = 0

    def __init__(
        self,
        cases: Iterable[FunctionType],
        title: str = strings.LOGO_TITLE,
        on_blank: Union[str, Callable] = "return",
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

        on_blank: What to do when given blank input (defaults to
                          stopping current view (without exiting)). See
                          docstring for menu() for more info.

        See menu function for more info
        """
        assert on_kbinterrupt in (
            "raise",
            "return",
        ), "Invalid choice for on_kbinterrupt"
        self.funcmap = construct_funcmap(cases, decorator=decorator)
        self.title = title
        self.on_kbinterrupt = on_kbinterrupt
        self.case_args = case_args
        self.case_kwargs = case_kwargs

        if self.case_args is None:
            self.case_args = {}
        if self.case_kwargs is None:
            self.case_kwargs = {}

        if on_blank == "return":
            self.on_blank = self._deactivate
        elif on_blank == "pass":
            self.on_blank = self._pass
        else:
            raise ValueError("Invalid choice of on_blank")

        # Special options
        self.special_cases = {
            "..": self.on_blank,
            "q": self._quit,
            "h": print_help,
        }

        if frontend == "auto":
            self._frontend = self._menu_simple
            try:
                import curses

                self._frontend = self._menu_curses
            except ImportError:
                pass

        elif frontend == "fancy":
            self._frontend = self._menu_curses
        elif frontend == "simple":
            self._frontend = self._menu_simple
        else:
            raise ValueError(
                f"Got unexpected specification for frontend: {self._frontend}"
            )

    def _deactivate(self):
        self.active = False

    def _quit(self):
        raise MenuQuit

    def _pass(self):
        pass

    def _handle_case(self, casefunc: Callable, args: List[str]):
        args = self.case_args.get(casefunc, ()) # Programmatic args
        kwargs = self.case_kwargs.get(casefunc, {}) # Programmatic kwargs

        try:
            if args or kwargs:  # If programmatic arguments
                if args:
                    raise MenuError(
                        "This function takes arguments progammatically"
                        " and should not be given any arguments"
                    )
                casefunc(*args, **kwargs)
            elif args:  # If user arguments
                # Raises TypeError if wrong number of arguments
                casefunc(*_handle_args(casefunc, args))
            else:  # No arguments
                # Will raise TypeError if casefunc() actually
                # requires arguments
                casefunc()
        # TODO: Should I catch TypeError? What if actual TypeError occurs?
        #       Maybe should catch everything and just display it in big red text? Contemplate!
        except (TypeError, MenuError) as e:
            _error_info_case(e, casefunc)

    def _menu_simple(self) -> str:
        # Import here to fix circular imports
        from pypatconsole import simple_interface

        return simple_interface.interface(self)

    def _menu_curses(self) -> str:
        # Import here to fix circular imports
        try:
            from pypatconsole import curses_interface
        except ImportError as e:
            raise ImportError(
                f"Got error :\n\t{e}\n"
                "This is probably caused by inability to import the 'curses' module.\n"
                "The curses module should be a built-in for Unix installations.\n"
                "Windows does not have 'curses' by default, suggested fix:\n\t"
                f"pip install windows-curses\n"
                "windows-curses adds support for the standard Python curses module on Windows."
            ) from e

        return curses_interface.interface(self)

    def _menu_loop(self):
        """
        Menu loop
        """
        while self.active:
            inputstring: str = self._frontend()

            clear_screen()
            if (not inputstring) or inputstring == "\n":
                self.on_blank()
                continue

            # Tokenize input
            try:
                inputlist: List[str] = input_splitter(inputstring)
            except ValueError as e:  # E.g. missing closing quotation or something
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
        Initialized menu loop
        """
        self.active = True
        Menu._depth += 1
        try:
            self._menu_loop()
        except KeyboardInterrupt:
            if self.on_kbinterrupt == "raise":
                self._deactivate()
                raise  # "Propagate exception"
            elif self.on_kbinterrupt == "return":
                print()
                return
        except MenuQuit:
            if Menu._depth > 1:
                raise
        finally:
            Menu._depth -= 1


def __get_module_cases(module: ModuleType) -> List[Callable]:
    """Get all functions defined in module"""
    inModule = lambda f: isfunction(f) and (getmodule(f) == module)
    return [func for func in vars(module).values() if inModule(func)]


def menu(
    cases: Union[Callable, Iterable[Callable], Dict[str, Callable], ModuleType],
    title: str = strings.DEFAULT_TITLE,
    on_blank: str = "return",
    on_kbinterrupt: str = "raise",
    decorator: Optional[Callable] = None,
    run: bool = True,
    case_args: Optional[Dict[Callable, tuple]] = None,
    case_kwargs: Optional[Dict[Callable, dict]] = None,
    frontend: Optional[str] = None,
):
    """¨
    TODO: Update docstring for newapi branch

    Factory function for the CLI class. This function initializes a menu.

    Parameters
    ------------
    cases: Can be output of locals() (a dict) from the scope of the cases

           Or an iterable functions

           Or a module containing the case functions

    title: title of menu

    on_blank: What to do the when given blank input. Available options are:
             'return', will return to parent menu

             'pass', does nothing. This should only be used for the main menu.

    on_kbinterrupt: Behavior when encountering KeyboardInterrupt exception when the menu is running.
                    If "raise", then will raise KeyboardInterrupt, if "return" the menu exits, and
                    returns.

    decorator: Decorator for case functions

    run: To invoke .run() method on CLI object or not.

    cases_args: Optional[Dict[Callable, tuple]], dictionary with function as key and tuple of
                positional arguments as values

    cases_kwargs: Optional[Dict[Callable, dict]], dictionary with function as key and dict of
                  keyword arguments as values

    frontend: str, specify desired frontend:
                    "auto": Will try to use fancy frontend if curses module is available, else
                            use simple frontend
                    "fancy": Use fancy front end (if on Windows, install
                             windows-curses first or Python will not be able to find the required
                             "curses" package that the fancy frontend uses)
                    "simple": Use the simple (but compatible with basically everything) frontend
    Returns
    --------
    CLI (Command Line Interface) object. Use .run() method to activate menu.
    """
    if isinstance(cases, ModuleType):
        cases_to_send = __get_module_cases(cases)
    elif isinstance(cases, dict):
        cases_to_send = list_local_cases(cases)
        # If this menu is the first menu initialized, and is given the locally
        # defined functions, then must filter the functions that are defined
        # in __main__

        moduleName: Union[str, None] = cases.get("__name__", None)
        if moduleName == "__main__":
            cases_to_send = [
                case for case in cases_to_send if case.__module__ == "__main__"
            ]

    elif isinstance(cases, Iterable):
        cases_to_send = cases
    else:
        raise TypeError(f"Invalid type for cases, got: {type(cases)}")

    cases_to_send = filter(lambda case: _CASE_IGNORE not in vars(case), cases_to_send)

    if frontend is None:
        frontend = cng.default_frontend

    cli = Menu(
        cases=cases_to_send,
        title=title,
        on_blank=on_blank,
        on_kbinterrupt=on_kbinterrupt,
        decorator=decorator,
        case_args=case_args,
        case_kwargs=case_kwargs,
        frontend=frontend,
    )
    if run:
        cli.run()

    return cli
