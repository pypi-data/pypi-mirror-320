
from ....abc import Feature
from ..types import ProgressBar
from typing import List, Self, Union, Tuple
import threading
import curses
import shutil

def thread(cls: Union['MultiThreading', ProgressBar], index: int) -> None:
    cls._threads[index][1].simulate
    while cls._threads[index][3].is_set():
        cls._thread_bars[index] = cls._threads[index][1].render()
    cls._threads[index][1].finish
    cls.precursor._complete += 1 # mark it as complete.

def get_total_lines():
    import sys
    from io import StringIO
    width = shutil.get_terminal_size().columns
    orig = sys.stdout
    sys.stdout = StringIO('', '\n')
    printed = sys.stdout.getvalue()

class MultiThreading(Feature):
    _threads: List[Tuple[int, ProgressBar, threading.Thread, threading.Event]] = []
    _thread_bars: List[str] = []

    def create_thread(self: Union[Self, ProgressBar], bar: ProgressBar) -> None:
        event = threading.Event()
        event.set()
        target = threading.Thread(target=thread, args=(len(self._threads),))
        target.daemon = True
        self._threads.append((len(self._threads), bar, target, event))
        self._thread_bars.append('')
    
    @property
    def childthread_bar_objects(self) -> List[ProgressBar]:
        return [x[1] for x in self._threads]
    
    @property
    def childthreads(self) -> List[threading.Thread]:
        return [x[2] for x in self._threads]

    def _one_alive_thread(self) -> bool:
        for thread in self._threads:
            if thread[3].is_set() and thread[2].is_alive():
                return True
        return False

    def _start_child_threads_helper(self, stdscr):
        for thread in self._threads:
            thread[2].start()
        # init curses
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(100)

        height, width = stdscr.getmaxyx()
        
        win = curses.newwin(len(self._thread_bars) + 1, shutil.get_terminal_size().columns, height // 2 - 2, width // 2 - 20)
        win.box()

    @property
    def startchildthreads(self) -> None:
        for thread in self._threads:
            thread[2].start()
        while self._one_alive_thread(): # at least one thread is alive.
            # use curses here.
            stdscr = curses