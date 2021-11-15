"""
Contains the command line interface (CLI) class, along its factory function:
menu()
"""
from time import sleep
from types import FunctionType, ModuleType
from typing import Any, Callable, Dict, Iterable, List, Optional, Union

from meny import config as cng
from meny import strings
from meny.funcmap import construct_funcmap
from meny.utils import (
    _assert_supported,
    _extract_and_preprocess_functions,
    _get_module_cases,
    clear_screen,
    input_splitter,
)
from meny.infos import _error_info_parse, print_help
from meny.exceptions import MenuQuit


def raise_interrupt(*args, **kwargs) -> None:
    """
    Raises keyboard interrupt
    """
    raise KeyboardInterrupt


def _quit():
    raise MenuQuit


def _menu_simple(instance) -> str:
    # Import here to fix circular imports
    from meny import simple_interface

    return simple_interface.interface(instance)


def _menu_curses(instance) -> str:
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

    return curses_interface.interface(instance)


class Menu:
    """
    Command Line Interface class
    """

    _return: Optional[dict] = None
    _depth: int = 0
    _return_mode: Optional[str] = None

    def __init__(
        self,
        cases: Iterable[FunctionType],
        title: str,
        *,
        case_args: Optional[Dict[FunctionType, tuple]] = None,
        case_kwargs: Optional[Dict[FunctionType, dict]] = None,
        decorator: Optional[FunctionType] = None,
        frontend: str,
        on_blank: str,
        on_kbinterrupt: str,
        once: bool,
        return_mode: str,
    ):
        """
        Input
        -----
        cases: Iterable of case functions

        title: String to print on top

        on_blank: what to do on empty string (press enter without any input)

        See docstring of menu function for more info
        """
        assert cases, "Given argument for cases is falsey, is it empty?"
        _assert_supported(on_kbinterrupt, "on_kbinterrupt", ("raise", "return"))
        _assert_supported(on_blank, "on_blank", ("return", "pass"))
        _assert_supported(frontend, "frontend", ("simple", "fancy", "auto"))
        _assert_supported(return_mode, "return_mode", ("flat", "tree"))

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
            self.on_blank = lambda: None

        # Special options
        self.special_cases = {
            "..": self.on_blank,
            "q": _quit,
            "h": print_help,
        }

        if frontend == "auto":
            self._frontend = _menu_simple
            try:
                import curses

                self._frontend = _menu_curses
            except ImportError:
                pass

        elif frontend == "fancy":
            self._frontend = _menu_curses
        elif frontend == "simple":
            self._frontend = _menu_simple

        if Menu._return_mode is None:
            Menu._return_mode = return_mode

        if Menu._return_mode == "flat":
            from meny.casehandlers import _FlatHandler

            self._case_handler: Callable = _FlatHandler()
        elif Menu._return_mode == "tree":
            from meny.casehandlers import _TreeHandler

            self._case_handler: Callable = _TreeHandler()

    def _deactivate(self):
        self.active = False

    def _menu_loop(self):
        """
        Menu loop
        """
        while self.active:
            inputstring: str = self._frontend(self)

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
                self._case_handler(self, casefunc, inputlist)
            elif case in self.special_cases:
                # Items in special_cases are not tuples, but the
                # actual functions, so no need to do [1]
                casefunc = self.special_cases[case]
                self._case_handler(self, casefunc, inputlist)
            else:
                print(strings.INVALID_TERMINAL_INPUT_MSG)
                sleep(cng.MSG_WAIT_TIME)

            if self.once:
                self._deactivate()

    def run(self) -> Dict:
        """
        Responsibilities:\
            call menu loop,\
            handle MenuQuit and KeyboardInterrupt,\
            count depth
        """
        self.active = True
        Menu._depth += 1

        try:
            self._menu_loop()
        except KeyboardInterrupt:
            if self.on_kbinterrupt == "raise":
                self._deactivate()
                raise
            elif self.on_kbinterrupt == "return":
                print()
        except MenuQuit:
            if Menu._depth > 1:
                raise
        finally:
            Menu._depth -= 1
            if Menu._depth == 0:
                Menu._return_mode = None
                self._case_handler = None

        return Menu._return or {}


def build_menu(
    cases: Union[Iterable[FunctionType], Dict[str, FunctionType], ModuleType],
    title: Optional[str] = None,
    *,
    case_args: Optional[Dict[FunctionType, tuple]] = None,
    case_kwargs: Optional[Dict[FunctionType, dict]] = None,
    decorator: Optional[FunctionType] = None,
    frontend: Optional[str] = None,
    on_blank: Optional[str] = None,
    on_kbinterrupt: Optional[str] = None,
    once: Optional[bool] = None,
    return_mode: Optional[str] = None,
) -> Menu:
    """
    This is a factory for the Menu class to reduce boilerplate.
    See docstring in menu() below.
    Returns  Menu object
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
        case_args=case_args,
        case_kwargs=case_kwargs,
        decorator=decorator,
        frontend=frontend or cng.DEFAULT_FRONTEND,
        on_blank=on_blank or cng.DEFAULT_ON_BLANK,
        on_kbinterrupt=on_kbinterrupt or cng.DEFAULT_ON_INTERRUPT,
        once=once,
        return_mode=return_mode or cng.DEFAULT_RETURN_MODE,
    )


def menu(
    cases: Union[Iterable[FunctionType], Dict[str, FunctionType], ModuleType],
    title: Optional[str] = None,
    *,
    case_args: Optional[Dict[FunctionType, tuple]] = None,
    case_kwargs: Optional[Dict[FunctionType, dict]] = None,
    decorator: Optional[FunctionType] = None,
    frontend: Optional[str] = None,
    on_blank: Optional[str] = None,
    on_kbinterrupt: Optional[str] = None,
    once: Optional[bool] = None,
    return_mode: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Factory function for the CLI class. This function initializes a menu.

    ## Parameters
    - `cases`: can be
        - a dictionary where keys are functions names and values are functions
        - an iterable of functions
        - a module containing functions

    - `title`: title of menu

    - `cases_args`: dictionary with function as key and tuple of positional arguments as values

    - `cases_kwargs`: dictionary with function as key and dict of keyword arguments as values

    - `once`: If you want menu to return after a a single choice.

    - `on_blank`: What to do the when given blank input. Available options are:
        - `"return"`, will return to parent menu
        - `"pass"`, does nothing. This should only be used for the root menu.

    - `on_kbinterrupt`: Behavior when encountering KeyboardInterrupt exception when the menu is running.
                      If `"raise"`, then will raise `KeyboardInterrupt`, if `"return"` the menu returns.

    - `decorator`: Decorator to applied for all case functions.

    - `frontend`: specify desired frontend:
        - `"auto"`: Will try to use fancy frontend if curses module is available, else
                use simple frontend (default)
        - `"fancy"`: Use fancy front end (if on Windows, install
                    windows-curses first or Python will not be able to find the required
                    `"curses"` package that the fancy frontend uses)
        - `"simple"`: Use the simple (but compatible with basically everything) frontend

    - `return_mode`: the dictionary structure to be returned after the menu is done running. Only effective
        menu is root menu, as nested menus will use root's. Return mode options are:
        - `"flat"`: This is the default. Returns dictionary with function names (as `str`)
                as keys, and their return values as values (if they are ran), if not their names
                will not be in the dictinary (see examples). The downside of this return mode is if you have
                nested menus, where the nested menus reuse function names that the parent menus have. The
                parent menus may overwrite the return values from the nested menus.
        - `"tree"`: Returns a nested dictionary structure, representing the structure of nested menus
                  (if you have that).

    ## Returns
    Dictionary where functions names (strings) are keys, and values are anything. Represents return
    values of case functions.

    ## Examples
    >>> def returnsOne():
    ...     def returnsOne():
    ...         return "1"
    ...     menu(locals())
    ...     return 1
    ...
    >>> def returnsTwo():
    ...     return 2
    ...
    >>> returns = menu(locals(), return_mode="flat") # Assume we have entered all cases
    { "returnsOne": 1, "returnsTwo": 2, }
    >>> returns = menu(locals(), return_mode="tree") # Assume we have entered all cases
    {
        "returnsOne": {
            "returnsOne": {
                "return": "1"
            }
            "return": 1
        },
        "returnsTwo": {
            "returns": 2
        },
    }
    >>> returns["returnsOne"]["returnsOne"]["return"]
    '1'
    """
    cli = build_menu(**locals())
    return cli.run()


if __name__ == "__main__":
    import subprocess

    subprocess.call(["python3", "example/cases.py"])
