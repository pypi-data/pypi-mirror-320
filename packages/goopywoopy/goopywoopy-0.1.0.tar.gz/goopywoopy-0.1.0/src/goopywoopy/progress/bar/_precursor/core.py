
from threading import Thread, Event
from typing import (
    Dict,
    List,
    Self,
    Union,
)
import time

class Precursor:
    class PrecursorError(Exception):
        WIDGET_RENDER = "'{}' Widget cannot be rendered! Precursor not set."
        PRECURSOR_PROPERTY = "'precursor' property error. Precursor not set."
        PRECURSOR_INSTANCE = "'{}' must be of the type Precursor."
        PRECURSOR_DELETE = "Cannot delete Precursor."
        PRECURSOR_THREAD = "Cannot get thread! Precursor is not set."
        NOT_NEEDED = "Precursor is not required for this widget and hence, all related functionalities are disabled."
    
    def __init__(self, total: Union[int, float]) -> None:
        # initial attributes
        self.elapsed: float = 0
        self.total = total
        self._complete = 0
        self.percentage: float = 0
        self.start_time: float = 0

        # thread specific
        self.allthreads: Dict[str, Thread] = {}
        self.allevents: List[Event] = []

        ## elapsed thread specific
        self.elapsed_thread_start = Event() # have to set for starting
        self.allevents.append(self.elapsed_thread_start)

        def update_elapsed():
            while self.elapsed_thread_start.is_set():
                self.elapsed = time.time() - self.start_time
                # time.sleep(1)
        
        self.elapsed_thread = Thread(target=update_elapsed)
        self.elapsed_thread.daemon = True
        self.allthreads['Time'] = self.elapsed_thread
    
    def __enter__(self) -> Self:
        return self.use()
    
    def __exit__(self, e_type, e_value, e_traceback) -> bool:
        self.cease()
        return False
    
    def use(self) -> Self:
        self.start_time = time.time()
        for e in self.allevents:
            e.set()
        for t in self.allthreads.values():
            t.start()
        return self
    
    def cease(self) -> Self:
        for e in self.allevents:
            e.clear()
        for t in self.allthreads.values():
            t.join()
        return self

    @property
    def totalwork(self) -> Union[int, float]:
        return self.total
    
    @property
    def complete(self) -> Union[int, float]:
        return self._complete
    
    @complete.setter
    def complete(self, comp: Union[int, float]) -> None:
        if comp > self.total:
            self._complete = self.total
            return None
        self._complete = comp
    
    @complete.deleter
    def complete(self) -> None:
        self._complete = 0
    
    @property
    def percent(self) -> float:
        return (self.complete/self.total) * 100
    
    @property
    def threads(self) -> Dict[str, Thread]:
        return self.allthreads
    
    @property
    def secondselapsed(self) -> float:
        return self.elapsed