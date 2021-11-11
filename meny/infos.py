from meny import strings
from types import FunctionType
from meny.funcmap import _get_case_name
from inspect import signature
from meny.utils import (
    RE_ANSI,
)


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


def print_help(*args, **kwargs) -> None:
    print(
        """
        To exit or return from menu interface (even if you are in a nested menu): Enter q

        To return to parent menu: Enter blank (press enter without giving input)
                                  or enter '..'. If you are in main menu, this 
                                  will exit the menu as well. 

        Press enter to exit help screen
        """
    )
    input()
