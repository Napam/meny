"""
Contains the command line interface (CLI) class, along its factory function:
menu()
"""
from ast import literal_eval
from collections import deque
from inspect import getfullargspec, getmodule, isfunction, signature, unwrap
from time import sleep
from types import FunctionType, MappingProxyType, ModuleType
from typing import Any, Dict, Iterable, List, Optional, Union

from meny import config as cng
from meny import strings as strings
from meny.funcmap import _get_case_name, construct_funcmap
from meny.utils import (
    RE_ANSI,
    _assert_supported,
    _extract_and_preprocess_functions,
    clear_screen,
    input_splitter,
    print_help,
)


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


def _handle_args(func: FunctionType, args: Iterable[str]) -> List:
    """
    Handles list of strings that are the arguments using ast.literal_eval.

    E.g. return is [1, "cat", 2.0, False]
                   int  str   float  bool
    """
    # Unwrap in case the function is wrapped
    func = unwrap(func)
    argsspec = getfullargspec(func)
    params = argsspec.args

    if len(args) > len(params):
        raise MenuError(f"Got too many arguments, should be {len(params)}, but got {len(args)}")

    typed_arglist = [None] * len(args)
    try:
        for i, arg in enumerate(args):
            typed_arglist[i] = literal_eval(arg)
    except (ValueError, SyntaxError) as e:
        raise MenuError(
            f"Got arguments: {args}\n" f"But could not evaluate argument at position {i}:\n\t {arg}"
        ) from e
    return typed_arglist


def _error_info_case(error: Exception, func: FunctionType) -> None:
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

    _stack: List[dict] = []
    _curr_case: Optional[FunctionType] = None

    def __init__(
        self,
        cases: Iterable[FunctionType],
        title: str,
        once: bool,
        on_blank: str,
        on_kbinterrupt: str,
        frontend: str,
        decorator: Optional[FunctionType] = None,
        case_args: Optional[Dict[FunctionType, tuple]] = None,
        case_kwargs: Optional[Dict[FunctionType, dict]] = None,
    ):
        """
        Input
        -----
        cases: Iterable of case functions

        title: String to print on top

        on_blank: what to do on empty string (press enter without any input)

        See docstring of menu function for more info
        """
        _assert_supported(on_kbinterrupt, "on_kbinterrupt", ("raise", "return"))
        _assert_supported(on_blank, "on_blank", ("return", "pass"))
        _assert_supported(frontend, "frontend", ("simple", "fancy", "auto"))

        self.funcmap = construct_funcmap(cases, decorator=decorator)
        self.title = title
        self.once = once
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

        self._return_handler = self._handle_return_tree

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

    def _deactivate(self):
        self.active = False

    def _quit(self):
        raise MenuQuit

    def _pass(self):
        pass

    def _handle_return_flat(self, casefunc, returnval):
        if returnval is not None:
            self._returns[casefunc.__name__] = returnval

    def _handle_return_tree(self, casefunc, returnval):
        if returnval is not None:
            # Menu._curr = {"return": returnval}
            # Menu._returns[casefunc.__name__] = Menu._curr
            pass

    def _handle_case(self, casefunc: FunctionType, args: List[str]):
        """
        Responsibilities:\
            call given casefunc with correct arguments,\
            handle return values,\
            Menu._curr_case
        """

        Menu._curr_case = casefunc
        programmatic_args = self.case_args.get(casefunc, ())
        programmatic_kwargs = self.case_kwargs.get(casefunc, {})
        try:
            if programmatic_args or programmatic_kwargs:  # If programmatic arguments
                if args:
                    raise MenuError(
                        "This function takes arguments progammatically"
                        " and should not be given any arguments"
                    )
                returnval = casefunc(*programmatic_args, **programmatic_kwargs)
            elif args:
                # Raises TypeError if wrong number of arguments
                returnval = casefunc(*_handle_args(casefunc, args))
            else:
                # Will raise TypeError if casefunc() actually requires arguments
                returnval = casefunc()

            # Menu._stack[-1]["return"] = returnval

        # TODO: Should I catch TypeError? What if actual TypeError occurs?
        #       Maybe should catch everything and just display it in big red text? Contemplate!
        except (TypeError, MenuError) as e:
            _error_info_case(e, casefunc)

    def _menu_simple(self) -> str:
        # Import here to fix circular imports
        from meny import simple_interface

        return simple_interface.interface(self)

    def _menu_curses(self) -> str:
        # Import here to fix circular imports
        try:
            from meny import curses_interface
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

            if self.once:
                self._deactivate()

    def _reset(self):
        Menu._returns.clear()
        Menu._curr_case = None

    def run(self) -> Dict:
        """
        Responsibilities:\
            call menu loop,\
            handle MenuQuit and KeyboardInterrupt,\
            push first stack,\
            pop stack,\
            count depth
        """
        self.active = True
        if len(Menu._stack) == 0:
            Menu._stack.append({})
        else:
            old_scope = Menu._stack[-1]
            next_scope = old_scope.get(Menu._curr_case.__name__, {})
            old_scope[Menu._curr_case.__name__] = next_scope
            Menu._stack.append(next_scope)

        try:
            self._menu_loop()
        except KeyboardInterrupt:
            if self.on_kbinterrupt == "raise":
                self._deactivate()
                raise
            elif self.on_kbinterrupt == "return":
                print()
        except MenuQuit:
            if len(Menu._stack) > 1:
                raise
        finally:
            scope = Menu._stack.pop()

        return scope


def _get_module_cases(module: ModuleType) -> List[FunctionType]:
    """Get all functions defined in module"""
    inModule = lambda f: isfunction(f) and (getmodule(f) == module)
    return [func for func in vars(module).values() if inModule(func)]


def build_menu(
    cases: Union[Iterable[FunctionType], Dict[str, FunctionType], ModuleType],
    title: Optional[str] = None,
    once: Optional[bool] = None,
    on_blank: Optional[str] = None,
    on_kbinterrupt: Optional[str] = None,
    decorator: Optional[FunctionType] = None,
    case_args: Optional[Dict[FunctionType, tuple]] = None,
    case_kwargs: Optional[Dict[FunctionType, dict]] = None,
    frontend: Optional[str] = None,
) -> Menu:
    """
    This is a factory for the Menu class to reduce boilerplate.
    See docstring in menu() below
    """
    if isinstance(cases, ModuleType):
        cases_to_send = _get_module_cases(cases)
    elif isinstance(cases, dict):
        cases_to_send = _extract_and_preprocess_functions(cases)
        # If this menu is the first menu initialized, and is given the locally
        # defined functions, then must filter the functions that are defined
        # in __main__

        moduleName: Union[str, None] = cases.get("__name__", None)
        if moduleName == "__main__":
            cases_to_send = [case for case in cases_to_send if case.__module__ == "__main__"]

    elif isinstance(cases, Iterable):
        # Looks kinda stupid, but it reuses the code, which is nice
        cases_to_send = _extract_and_preprocess_functions({case.__name__: case for case in cases})
    else:
        raise TypeError(f"Invalid type for cases, got: {type(cases)}")

    cases_to_send: Iterable[FunctionType]

    cases_to_send = filter(lambda case: cng._CASE_IGNORE not in vars(case), cases_to_send)

    if once is None:
        once = cng.DEFAULT_ONCE

    return Menu(
        cases=cases_to_send,
        title=title or strings.DEFAULT_TITLE,
        once=once,
        on_blank=on_blank or cng.DEFAULT_ON_BLANK,
        on_kbinterrupt=on_kbinterrupt or cng.DEFAULT_ON_INTERRUPT,
        decorator=decorator,
        case_args=case_args,
        case_kwargs=case_kwargs,
        frontend=frontend or cng.DEFAULT_FRONTEND,
    )


def menu(
    cases: Union[Iterable[FunctionType], Dict[str, FunctionType], ModuleType],
    title: Optional[str] = None,
    once: Optional[bool] = None,
    on_blank: Optional[str] = None,
    on_kbinterrupt: Optional[str] = None,
    decorator: Optional[FunctionType] = None,
    case_args: Optional[Dict[FunctionType, tuple]] = None,
    case_kwargs: Optional[Dict[FunctionType, dict]] = None,
    frontend: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Factory function for the CLI class. This function initializes a menu.

    Parameters
    ------------
    cases: a dictionary where keys are functions names and values are functions\
           Or an iterable of functions\
           Or a module containing functions

    title: title of menu

    once: If you want menu to return after a a single choice. 

    on_blank: What to do the when given blank input. Available options are:\
        'return', will return to parent menu\
        'pass', does nothing. This should only be used for the main menu.

    on_kbinterrupt: Behavior when encountering KeyboardInterrupt exception when the menu is running.\
                    If "raise", then will raise KeyboardInterrupt, if "return" the menu returns.

    decorator: Decorator to applied for all case functions.

    cases_args: Optional[Dict[FunctionType, tuple]], dictionary with function as key and tuple of
                positional arguments as values

    cases_kwargs: Optional[Dict[FunctionType, dict]], dictionary with function as key and dict of
                  keyword arguments as values

    frontend: str, specify desired frontend:\
                    "auto": Will try to use fancy frontend if curses module is available, else\
                            use simple frontend (default)\
                    "fancy": Use fancy front end (if on Windows, install\
                             windows-curses first or Python will not be able to find the required\
                             "curses" package that the fancy frontend uses)\
                    "simple": Use the simple (but compatible with basically everything) frontend
    Returns
    --------
    Dictionary where functions names (strings) are keys, and values are anything. Represents return 
    values of case functions.
    """
    cli = build_menu(**locals())
    return cli.run()


if __name__ == "__main__":
    import subprocess

    subprocess.call(["python3", "example/cases.py"])
