import curses
from typing import Any, Callable, Dict, Optional, Tuple, Union
import pypatconsole


class BaseWindow:
    def __init__(self):
        self.window: Optional["curses._CursesWindow"] = None
        self.x = 0
        self.y = 0

    def cprint(
        self,
        string: Any,
        *args,
        newline: int = 1,
        cursorwin: Optional["curses._CursesWindow"] = None,
        offset: Optional[Tuple[int, int]] = None,
    ):
        string = str(string)
        strlen = len(string)
        self.window.addstr(self.y, self.x, string, *args)
        self.x += strlen

        if newline:
            self.x = 0
            self.y += newline

        self.set_cursor(self.y, self.x, cursorwin, offset)

    def set_cursor(
        self,
        y,
        x,
        cursorwin: Optional["curses._CursesWindow"] = None,
        offset: Optional[Tuple[int, int]] = None,
    ):
        if cursorwin is None:
            cursorwin = self.window

        lines, cols = self.window.getmaxyx()
        self.y = max(0, min(y, lines - 1))
        self.x = max(0, min(x, cols - 1))

        y = self.y
        x = self.x

        if offset is not None:
            y += offset[0]
            x += offset[1]

        cursorwin.move(y, x)

    def clear(self):
        self.y, self.x = 0, 0
        self.window.clear()
        self.window.move(self.y, self.x)


class BaseSubWindow(BaseWindow):
    def __init__(self, main: "MainWindow"):
        super().__init__()
        self.main: "MainWindow" = main
        self.window: Optional["curses._CursesWindow"] = None

    def cprint(
        self,
        string: Any,
        *args,
        newline: int = 1,
        cursorwin: Optional["curses._CursesWindow"] = None,
        offset: Optional[Tuple[int, int]] = None,
    ):
        if cursorwin is None:
            cursorwin = self.main.window
        if offset is None:
            offset = self.window.getbegyx()

        super().cprint(
            string, *args, newline=newline, cursorwin=cursorwin, offset=self.window.getbegyx()
        )

    def set_cursor(
        self,
        y,
        x,
        cursorwin: Optional["curses._CursesWindow"] = None,
        offset: Optional[Tuple[int, int]] = None,
    ):
        if cursorwin is None:
            cursorwin = self.main.window
        if offset is None:
            offset = self.window.getbegyx()

        return super().set_cursor(y, x, cursorwin=cursorwin, offset=offset)


class TitleSubWindow(BaseSubWindow):
    def __init__(self, main: "MainWindow"):
        super().__init__(main)
        main_rows, main_cols = self.main.window.getmaxyx()
        self.window = main.window.derwin(0, 0)
        self.cprint(f"{self.main.title:^40}", curses.A_UNDERLINE, newline=False)


class FuncmapSubWindow(BaseSubWindow):
    def __init__(self, main: "MainWindow"):
        super().__init__(main)
        self.window: "curses._CursesWindow" = main.window.derwin(1, 0)
        self.print_funcmap()

    def print_funcmap(self, highlight=-1):
        for i, (key, tup) in enumerate(self.main.funcmap.items()):
            if i == highlight:
                self.cprint(f"{f'{key}. {tup[0]}':<40}", curses.A_STANDOUT)
            else: 
                self.cprint(f"{f'{key}. {tup[0]}':<40}")

    def input_window_callback(self, inputwindow: 'InputSubWindow'):
        if inputwindow.curr_key is None:
            self.set_cursor(0, 0)
            self.print_funcmap(-1)
            self.window.refresh()
        else: 
            index = self.main.key2index[inputwindow.curr_key]
            self.set_cursor(0, 0)
            self.print_funcmap(index)
            self.window.refresh()


class InputSubWindow(BaseSubWindow):
    def __init__(self, main: "MainWindow"):
        super().__init__(main)
        rows = len(self.main.funcmap)
        main_rows, main_cols = self.main.window.getmaxyx()

        rows_ = min(rows+2, main_rows-1)
        self.window: "curses._CursesWindow" = main.window.derwin(rows_, 0)
        # self.context: 'Context' = context
        self.curr_key: Optional[str] = None
        self.curr_index: Optional[int] = None

        self._input_string: str = "Input: "
        self.cprint(self._input_string, newline=False)
        self.begin_input_yx = (self.y, self.x)
        self.inp: str = ""
        self.listeners: list = []

    def _broadcast_to_listeners(self):
        for listener in self.listeners:
            listener(self)
        self.set_cursor(self.y, self.x) # "Capture cursor back"

    def _sync_input_field(self):
        '''
        Synchronizes visual input field with self.inp
        '''
        self.set_cursor(*self.begin_input_yx)
        self.main.window.clrtoeol()
        self.cprint(self.inp, newline=False)
        self.handle_str_input(" ")
        self.main.window.clrtoeol()

    def _sync_context(self):
        '''
        Checks current input string (self.inp) and alter context accordingly
        '''
        start_token = self.inp.split(" ")[0]
        if start_token in self.main.funcmap:
            self.curr_key = start_token
            self.curr_index = self.main.key2index[start_token]
        else:
            self.curr_index = None
            self.curr_key = None
        self._broadcast_to_listeners()

    def handle_str_input(self, k: str) -> None:
        self.inp += k
        self.cprint(f"{k}", newline=False) 
        self._sync_context()
        self.window.refresh()

    def handle_int_input(self, k: int) -> None:
        if k == curses.KEY_BACKSPACE:
            # Can only remove if something if input field 
            if self.inp:
                self.inp = self.inp[:-1]
                self.set_cursor(self.y, self.x - 1)
                self.main.window.clrtoeol()  # Must call on main window

        elif k == curses.KEY_UP:
            if self.curr_key:
                self.curr_index = (self.curr_index - 1) % len(self.main.funcmap)
                self.inp = self.main.index2key[self.curr_index]
            else:
                self.inp = self.main.index2key[-1]
            self._sync_input_field()
                
        elif k == curses.KEY_DOWN:
            if self.curr_key:
                self.curr_index = (self.curr_index + 1) % len(self.main.funcmap)
                self.inp = self.main.index2key[self.curr_index]
            else:
                self.inp = self.main.index2key[0]
            self._sync_input_field()

        elif k == curses.KEY_LEFT:
            self.set_cursor(self.y, max(self.x - 1, self.begin_input_yx[1]))
        
        elif k == curses.KEY_RIGHT:
            self.set_cursor(self.y, max(self.x + 1, self.begin_input_yx[1]))
                
        self._sync_context()


class MainWindow(BaseWindow):
    def __init__(self, cli: pypatconsole.consoleclass.CLI):
        super().__init__()
        self.funcmap = cli.funcmap
        self.title = cli.title
        self.window: Optional["curses._CursesWindow"] = None

        self.int_listeners: list = []
        self.str_listeners: list = []
        self.key_listeners: list = []

        self.key2index = {key:index for index, key in enumerate(self.funcmap)}
        self.index2key = tuple(self.funcmap)

    def _broadcast_to_listeners(self, k):
        for listener in self.key_listeners:
            listener(k)

        if isinstance(k, int):
            for listener in self.int_listeners:
                listener(k)
        elif isinstance(k, str):  
            for listener in self.str_listeners:
                listener(k)
        else:
            raise TypeError(f"'k' is of unexpected type: {type(k)}")

    def run(self, window: "curses._CursesWindow"):
        self.window = window
        self.window.keypad(True)
        curses.use_default_colors()
        curses.noecho()
        self.window.refresh()

        # self.window = curses.newpad(1000, 1000)
        self.clear()

        n = len(self.funcmap)
        keys = tuple(self.funcmap)  # Gets keys

        titlewin = TitleSubWindow(self)
        funcwin = FuncmapSubWindow(self)
        inputwin = InputSubWindow(self)

        inputwin.listeners.append(funcwin.input_window_callback)
        self.str_listeners.append(inputwin.handle_str_input)
        self.int_listeners.append(inputwin.handle_int_input)

        inp = ""
        while not inp.endswith("\n"):
            k: Union[int, str] = window.get_wch()
            self._broadcast_to_listeners(k)
            inp = inputwin.inp
            window.refresh()

        return inp.strip("\n")


def interface(cli: pypatconsole.consoleclass.CLI):
    _interface_object = MainWindow(cli)
    return curses.wrapper(_interface_object.run)