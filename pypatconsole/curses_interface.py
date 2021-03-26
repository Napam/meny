import curses
from typing import Any, Callable, Dict, Optional, Tuple, Type, Union
import pypatconsole


class BaseWindow:
    def __init__(self, window: 'curses._CursesWindow'):
        self._window = window

    def cprint(self, string: str, *args, newline: int = 1):
        """
        Mimics print with newline
        """
        self._window.addstr(string, *args)
        y, x = self._window.getyx()
        if newline:
            self._window.move(y+newline, 0)


class InputField(BaseWindow):
    def __init__(self, main: 'MainWindow') -> None:
        super().__init__(window=main.pad)
        self.main = main
        self._inp = ""
        self.inp_message = "Input: "
        self.cprint(self.inp_message, newline=0)
        self.begin_y, self.begin_x = self._window.getyx()
        self.first_token: Optional[str] = None

    @property
    def inp(self):
        return self._inp

    @inp.setter
    def inp(self, string: str):
        self._inp = string
        self.first_token = self._inp.split(" ")[0]

    def read_field(self, n: Optional[int] = None, decode: str = "utf-8") -> str:
        """
        Gets string in input field
        """
        prev_y, prev_x = self._window.getyx() 
        if n:
            string = self._window.instr(self.begin_y, self.begin_x, n).decode(decode).strip()
        else:
            string = self._window.instr(self.begin_y, self.begin_x).decode(decode).strip()
        self._window.move(prev_y, prev_x) 
        return string

    def sync_window_with_inp(self):
        """
        Sets the visibe window to match the content of self._inp
        """
        self._window.move(self.begin_y, self.begin_x)
        self._window.clrtoeol()
        self._window.addstr(self.inp)

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
                self._window.move(y, x+1)

        elif k == curses.KEY_LEFT:
            if x > len(self.inp_message):
                self._window.move(y, x-1)

        elif k == curses.KEY_BACKSPACE:
            if self.inp and x > self.begin_x:
                self._window.move(y, x-1)
                self._window.delch()
                self.inp = self.read_field()

    def handle_str_input(self, k: int, y: int, x: int):
        if k == "\n":
            # Must capture newline explicitly, since insstr just treats it as space or something
            self.inp += "\n"
            self._window.clear()
            return

        self._window.insstr(k)
        self._window.move(y, x+1)
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

        self.key2index = {key:index for index, key in enumerate(self.funcmap)}
        self.index2key = tuple(self.funcmap)
        self.curr_index: Optional[int] = None

    def highlight_funcmap(self, token: str, strlen: int):
        new_index = self.key2index.get(token, None)
        prev_y, prev_x = self.pad.getyx()

        if new_index is None: # Index not in funcmap
            if self.curr_index is not None: # If previously highlighted, remove highlight
                self.pad.chgat(self.curr_index+1, 0, curses.A_NORMAL)
                self.pad.move(prev_y, prev_x) # Put cursor back to previous position
                self.curr_index = None 
            return

        if self.curr_index is not None:
            # If previously highlighted, remove highlight before highlighting new one
            self.pad.chgat(self.curr_index+1, 0, curses.A_NORMAL)

        self.curr_index = new_index 
        self.pad.chgat(new_index+1, 0, strlen, curses.A_STANDOUT)
        self.pad.move(prev_y, prev_x) # Put cursor back to previous position

    def run(self, window: "curses._CursesWindow"):
        curses.use_default_colors()
        window.refresh()
        self.pad = curses.newpad(2048, 2048)
        super().__init__(self.pad)

        def refresh_pad():
            lines, cols = window.getmaxyx()
            self.pad.refresh(0, 0, 0, 0, lines-1, cols-1)

        # Print funcmap
        funcmap_strings = [f"{key}. {val[0]}" for key, val in self.funcmap.items()]
        maxstrlen = max(map(len, funcmap_strings)) # Get length of longest string in funcmap 
        maxstrlen = max(maxstrlen, len(self.title))
        self.cprint(f"{self.title:^{maxstrlen}}", curses.A_UNDERLINE)
        for s in funcmap_strings:
            self.cprint(s)

        self.cprint("")

        inputfield = InputField(self)    
        refresh_pad()
        while not inputfield._inp.endswith("\n"):
            # Get input using window instead of pad, using pad gives unexpected output
            k = window.get_wch()
            y, x = self.pad.getyx()
            inputfield.handle_input(k, y, x)
            self.highlight_funcmap(inputfield.first_token, maxstrlen)
            refresh_pad()
        return inputfield._inp

def interface(cli: pypatconsole.consoleclass.CLI):
    _interface_object = MainWindow(cli)
    return curses.wrapper(_interface_object.run)