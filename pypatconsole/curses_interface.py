import curses
import curses.ascii
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union
import pypatconsole
import inspect
from functools import wraps


def recover_cursor(f):
    """Wrapper for functions that should put cursor to where it was before"""

    @wraps(f)
    def wrapper(*args, **kwargs):
        self: BaseWindow = args[0]
        prev_y, prev_x = self._window.getyx()
        return_val = f(*args, **kwargs)
        self._window.move(prev_y, prev_x)
        return return_val

    return wrapper


class BaseWindow:
    def __init__(self, window: "curses._CursesWindow"):
        self._window = window
        self._window.keypad(True)

    def cprint(self, string: str, *args, newline: int = 1):
        """
        Mimics print with newline
        """
        self._window.addstr(string, *args)
        y, x = self._window.getyx()
        if newline:
            self._window.move(y + newline, 0)


class InputField(BaseWindow):
    def __init__(self, main: "MainWindow") -> None:
        super().__init__(window=main._window)
        self.main = main
        self._inp = ""
        self.inp_message = "Input: "
        self.cprint(self.inp_message, newline=0)
        self.begin_y, self.begin_x = self._window.getyx()
        self.first_token: str = ""

    @property
    def inp(self):
        return self._inp

    @inp.setter
    def inp(self, string: str):
        self._inp = string
        self.first_token = self._inp.split(" ")[0]

    @recover_cursor
    def read_field(self, n: Optional[int] = None, decode: str = "utf-8") -> str:
        """
        Gets string in input field
        """
        if n:
            string = self._window.instr(self.begin_y, self.begin_x, n).decode(decode).strip()
        else:
            string = self._window.instr(self.begin_y, self.begin_x).decode(decode).strip()
        return string

    def sync_window_with_inp(self):
        """
        Sets the visibe window to match the content of self._inp
        """
        self._window.move(self.begin_y, self.begin_x)
        self._window.clrtoeol()
        self._window.addstr(self.inp)

    def handle_backspace(self, y: int, x:int):
        if self.inp and x > self.begin_x:
            self._window.move(y, x - 1)
            self._window.delch()
            self.inp = self.read_field()

    def handle_int_input(self, k: int, y: int, x: int):
        """
        k: key
        y: current y pos
        x: current x pos
        """
        if k == curses.KEY_UP:
            if self.main.curr_index is None:
                self.inp = self.main.index2key[-1]
            else:
                new_index = (self.main.curr_index - 1) % len(self.main.funcmap)
                self.inp = self.main.index2key[new_index]
            self.inp += " "
            self.sync_window_with_inp()

        elif k == curses.KEY_DOWN:
            if self.main.curr_index is None:
                self.inp = self.main.index2key[0]
            else:
                new_index = (self.main.curr_index + 1) % len(self.main.funcmap)
                self.inp = self.main.index2key[new_index]
            self.inp += " "
            self.sync_window_with_inp()

        elif k == curses.KEY_RIGHT:
            _, max_x = self._window.getmaxyx()
            if x < max_x:
                self._window.move(y, x + 1)

        elif k == curses.KEY_LEFT:
            if x > len(self.inp_message):
                self._window.move(y, x - 1)

        elif k in (curses.KEY_BACKSPACE, curses.ascii.BS, curses.ascii.DEL):
            self.handle_backspace(y, x)

    def handle_str_input(self, k: str, y: int, x: int):
        if k == "\n":
            # Must capture newline explicitly, since insstr just treats it as space or something
            self.inp += "\n"
            self._window.clear()
        elif (k in ("\b", "\x7f")) or ord(k) == 127:
            # Some systems (erm, Windows at least) gives "\b" for backspace
            self.handle_backspace(y, x)
        elif (k == "\x00") or (ord(k) == 0):
            # Windows key or some weird ass key, idk what to do about it, just return
            return
        else:
            # Sometimes crash on funny keys, e.g. windows key
            self._window.insstr(k)
            self._window.move(y, x + 1)
            self.inp = self.read_field()

    def handle_input(self, k: Union[int, str], y: int, x: int):
        if isinstance(k, str):
            self.handle_str_input(k, y, x)
        elif isinstance(y, int):
            self.handle_int_input(k, y, x)
        else:
            raise TypeError(f"k is of unexpected type: {type(k)}")


class MainWindow(BaseWindow):
    def __init__(self, cli: pypatconsole.consoleclass.CLI):
        self.funcmap = cli.funcmap
        self.title = cli.title

        self.key2index = {key: index for index, key in enumerate(self.funcmap)}
        self.index2key = tuple(self.funcmap)
        self.curr_index: Optional[int] = None

    @recover_cursor
    def highlight_funcmap(self, token: str, strlen: int):
        """Highlight line in funcmap print

        Exploits the fact that funcmap starts at line 1, and ends at line 1 + len(funcmap)

        Parameters
        ----------
        token : str
        strlen : int, how many columns highlight should span
        """
        # Handle option -1, -2 etc.. works like list(...)[-1]
        if token.startswith("-") and len(token) >= 2:
            try:
                token = str(len(self.funcmap) + int(token) + 1)
            except ValueError:
                pass

        new_index = self.key2index.get(token, None)

        if new_index is None:  # Index not in funcmap
            if self.curr_index is not None:
                # Clear previous highlight
                self._window.chgat(self.curr_index + 1, 0, curses.A_NORMAL)
                self.curr_index = None
            return

        if self.curr_index is not None:
            # If previously highlighted, remove highlight before highlighting new one
            self._window.chgat(self.curr_index + 1, 0, curses.A_NORMAL)

        self.curr_index = new_index
        self._window.chgat(new_index + 1, 0, strlen, curses.A_STANDOUT)

    @recover_cursor
    def hint_args(self, inp: str):
        prev_y, prev_x = self._window.getyx()
        # Clear line under input field
        self._window.move(prev_y + 1, 0)
        self._window.clrtoeol()
        if self.curr_index is None:
            return

        func = self.funcmap[self.index2key[self.curr_index]][1]
        signature = inspect.signature(func)
        paramiter = signature.parameters.items()
        iterlen = len(paramiter)
        if iterlen == 0:
            return

        self._window.move(prev_y + 1, prev_x)  # Under input field
        # TODO: Use better parser, this does not look at quotation marks, results in wrong highlight
        inp_list = inp.split(" ")
        n_tokens = len(inp_list)

        self._window.addstr("(")
        for i, p in enumerate(paramiter):
            if i == n_tokens - 2:
                self._window.addstr(f"{p[1]}", curses.A_UNDERLINE | curses.A_BOLD)
            else:
                self._window.addstr(f"{p[1]}")
            if i < iterlen - 1:
                self._window.addstr(", ")
        self._window.addstr(")")

        if n_tokens > iterlen + 1:
            self._window.chgat(prev_y + 1, prev_x, len(str(signature)), curses.color_pair(1))

    def run(self, window: "curses._CursesWindow"):
        """
        Will do almost all work on a padded window, which
        is accessible with self._window

        window (not self._window) is only used for keystrokes
        """
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        super().__init__(curses.newpad(2048, 2048))  # This will populate the self._window attribute

        def refresh_pad():
            lines, cols = window.getmaxyx()
            self._window.refresh(0, 0, 0, 0, lines - 1, cols - 1)

        # Print funcmap
        funcmap_strings = [f"{key}. {val[0]}" for key, val in self.funcmap.items()]
        maxstrlen = max(map(len, funcmap_strings))  # Get length of longest string in funcmap
        maxstrlen = max(maxstrlen, len(self.title))
        self.cprint(f"{self.title:^{maxstrlen}}", curses.A_UNDERLINE)
        for s in funcmap_strings:
            self.cprint(s)

        self.cprint("")

        inputfield = InputField(self)
        refresh_pad()
        while not inputfield._inp.endswith("\n"):
            # Get input using window instead of pad, using pad gives unexpected output
            k = self._window.get_wch()
            y, x = self._window.getyx()
            inputfield.handle_input(k, y, x)
            self.highlight_funcmap(inputfield.first_token, maxstrlen)
            self.hint_args(inputfield.inp)
            refresh_pad()
        return inputfield._inp


def interface(cli: pypatconsole.consoleclass.CLI):
    _interface_object = MainWindow(cli)
    return curses.wrapper(_interface_object.run)