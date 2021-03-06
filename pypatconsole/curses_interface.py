import curses
from typing import Any, Callable, Dict, Optional, Tuple, Union 
import pypatconsole
            

# class Window:
    # def __init__(self, stdscr: 'curses._CursesWindow'):
        # stdscr.

class Interface:
    def __init__(self, cli: pypatconsole.consoleclass.CLI):
        self.funcmap = cli.funcmap
        self.title = cli.title
        self.stdscr: Optional['curses._CursesWindow'] = None

        self.x = 0
        self.y = 0

    def cprint(self, string: Any, *args, newline: int = 1, ):
        string = str(string)
        strlen = len(string)
        self.stdscr.addstr(string, *args)
        self.x += strlen
        
        if newline:
            self.x = 0    
            self.y += newline

        self.set_cursor(self.y, self.x)

    def set_cursor(self, y, x):
        lines, cols = self.stdscr.getmaxyx()
        self.y = max(0, min(y, lines-1))
        self.x = max(0, min(x, cols-1))
        self.stdscr.move(self.y, self.x)

    def clear(self):
        self.y, self.x = 0, 0
        self.stdscr.clear()
        self.stdscr.move(self.y, self.x)

    def print_funcmap(self, highlight, absolute=False):

        if absolute:
            temp = self.y, self.x
            self.set_cursor(1, 0)
        for i, (key, tup) in enumerate(self.funcmap.items()):
            if i == highlight:
                self.cprint(f"{f'{key}. {tup[0]}':<40}", curses.A_STANDOUT)
            else:
                self.cprint(f"{f'{key}. {tup[0]}':<40}")
        if absolute:
            self.set_cursor(*temp)

    def run(self, stdscr: 'curses._CursesWindow'):
        self.stdscr = stdscr
        self.clear()
        curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
        
        n = len(self.funcmap)
        keys = tuple(self.funcmap) # Gets keys

        highlight = -1
                    
        self.cprint(f"{self.title:^40}", curses.A_UNDERLINE)
        self.print_funcmap(-1)
        self.cprint("")
        self.cprint("Input: ", newline=False)

        inp = ""
        k = ""
        while not inp.endswith("\n"):
            k: Union[int, str] = stdscr.get_wch()
            if isinstance(k, int):
                if k == curses.KEY_UP:
                    highlight = (highlight-1) % n
                elif k == curses.KEY_DOWN:
                    highlight = (highlight+1) % n
                elif k == curses.KEY_BACKSPACE:
                    if inp: 
                        inp = inp[:-1]
                        self.set_cursor(self.y, self.x-1)
                        stdscr.clrtoeol()
            else:
                self.cprint(k, newline=False)
                inp += k

                if inp:
                    first = inp.split(" ")[0]
                    choice = first if first in self.funcmap else None
                    if choice:
                        self.print_funcmap(int(choice)-1, absolute=True)
                    else:
                        self.print_funcmap(-1, absolute=True)
            
            if not inp:
                self.print_funcmap(-1, absolute=True)
            self.stdscr.refresh()
                
        return keys[highlight]

def interface(cli: pypatconsole.consoleclass.CLI):
    _interface_object = Interface(cli)
    return curses.wrapper(_interface_object.run)