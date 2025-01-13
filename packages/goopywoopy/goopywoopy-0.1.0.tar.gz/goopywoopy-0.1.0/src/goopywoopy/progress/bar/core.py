from typing import (
    Union,
    Self,
)
from .precursor import Precursor
from ._features import Logging, Decoy, ShellExecution
from .utils import Splitter
from .widgets import Label, Bar, Time
from .types import Widget as WDGT_TYPE, CustomRender as CR_TYPE, WidgetWrapper as WW_TYPE
from .widgets.abc import Widget, CustomRender

class ProgressBar(Logging, Decoy, ShellExecution):
    def __init__(
            self,
            total: int,
            normalized_bar_size: float = 100,
            *widgets: Union[WDGT_TYPE, CR_TYPE, WW_TYPE],
            logfile: Union[str, None] = None,
    ) -> None:
        if len(widgets) == 0:
            widgets = (Label(), Bar(), Time())
        self.precursor = Precursor(total)
        self.splitter = Splitter(*widgets)
        self.widgets = list(widgets)
        self.tolog = logfile is not None
        if self.tolog:
            self.set_logfile(logfile)
        self.bar_normalization = normalized_bar_size

        for widget in self.widgets:
            if isinstance(widget, CustomRender):
                widget.set_normalization(normalized_bar_size)
                widget.set_possible_length(self.splitter.possible_barlength)
            if hasattr(widget, '__precursor__') and getattr(widget, '__precursor__') == 'enabled':
                widget.precursor = self.precursor

        self.used: bool = False
        self.ceased: bool = False
    
    def __enter__(self) -> Self:
        if not self.used:
            self.used = True
            self.precursor.use()
            print(self.render(), end='\r')
        else:
            raise RuntimeError("Please create a new instance of the progress bar to continue simulating.\nEach instance can only be simulated once.")
        return self
    
    def __exit__(self, e_type, e_value, e_tb) -> bool:
        if self.used and not self.ceased:
            self.ceased = True
            self.precursor.cease()
            print(self.render())
        else:
            raise RuntimeError("The ProgressBar has already shut down all threads. Cannot shut down again.")
        return False
    
    def render(self) -> str:
        strings = []
        for wdgt in self.widgets:
            strings.append(wdgt.render())
        
        return ' '.join(strings)
    
    def update(self, i: int) -> None:
        self.precursor.complete = i
    
    @property
    def simulate(self) -> None:
        self.__enter__()
    
    @property
    def finish(self) -> None:
        self.__exit__(None, None, None)
    
    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> None:
        return self.render()