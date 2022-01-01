import meny
import meny.strings as strings
from typing import Dict, Tuple, Callable


def print_funcmap(funcmap: Dict[str, Tuple[str, Callable]]) -> None:
    """
    Prints a func_map dictionary

    Items should be tuples with first elements as descriptions
    and second elements as function objects
    """
    for key, tup in funcmap.items():
        print(key + ".", tup[0])


def logo_title(title: str) -> None:
    """Prints logo title"""
    print("{:-^40s}".format(title))


def show_cases(funcmap: dict, title=strings.LOGO_TITLE) -> None:
    """Prints function map prettily with a given title"""
    logo_title(title)
    print_funcmap(funcmap)


def interface(cli: meny.Menu):
    print("\x1b[s", end="")  # Save current position
    show_cases(cli.funcmap, cli.title)
    retval = input(f"{strings.ENTER_PROMPT}: ")
    print("\x1b[u\x1b[J", end="")  # Restore saved position
    return retval
