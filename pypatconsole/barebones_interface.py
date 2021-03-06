# from pypatconsole.consoleclass import CLI
from pypatconsole.utils import clear_screen, input_splitter, list_local_cases, print_help
import pypatconsole.strings as strings
import pypatconsole.config as cng
from pypatconsole.funcmap import print_funcmap

def logo_title(title: str) -> None:
    """Prints logo title"""
    print("{:-^40s}".format(title))

def show_cases(funcmap: dict, title=strings.LOGO_TITLE) -> None:
    """Prints function map prettily with a given title"""
    logo_title(title)
    print_funcmap(funcmap)
    
def interface(cli):
    clear_screen()
    show_cases(cli.funcmap, cli.title)
    print()
    # Empty string will evulate to False
    if cli.blank_hint:
        print(cli.blank_hint)
    return input(f"{strings.ENTER_PROMPT}: ")   