from typing import (
    Protocol,
    Self,
    Union,
    List,
    Dict,
    runtime_checkable
)
from threading import Thread
from pathlib import Path

class UnknownLength:
    def __str__(self) -> str:
        return 'Unknown'
    
    def __repr__(self) -> str:
        return 'Unknown'
    
    def __float__(self) -> float:
        return 0
    
    def __int__(self) -> int:
        return 0

@runtime_checkable
class Precursor(Protocol):

    class PrecursorError(Exception):
        WIDGET_RENDER = "'{}' Widget cannot be rendered! Precursor not set."
        PRECURSOR_PROPERTY = "'precursor' property error. Precursor not set."
        PRECURSOR_INSTANCE = "'{}' must be of the type Precursor."
        PRECURSOR_DELETE = "Cannot delete Precursor."
        PRECURSOR_THREAD = "Cannot get thread! Precursor is not set."
        NOT_NEEDED = "Precursor is not required for this widget and hence, all related functionalities are disabled."

    def __init__(self, total: Union[int, float]) -> None: ...
    def __enter__(self) -> Self: ...
    def __exit__(self, e_type, e_value, e_traceback) -> bool: ...
    def use(self) -> Self:...
    def cease(self) -> Self: ...

    @property
    def totalwork(self) -> Union[int, float]: ...
    @property
    def complete(self) -> Union[int, float]: ...
    @property
    def percent(self) -> float: ...
    @property
    def secondselapsed(self) -> float: ...
    @property
    def threads(self) -> Dict[str, Thread]: ...

@runtime_checkable
class Widget(Protocol):
    __name__: str

    @property
    def precursor(self) -> Precursor: ...
    @property
    def length(self) -> Union[int, UnknownLength]: ...
    @property
    def thread(self) -> Thread: ...
    @property
    def is_sensitive(self) -> bool: ...

    def render(self) -> str: ...

@runtime_checkable
class CustomRender(Widget, Protocol):
    def set_possible_length(self, length: float) -> None: ...
    def set_normalization(self, normalization: float) -> None: ...

@runtime_checkable
class WidgetWrapper(Widget, Protocol):
    widget: Union[Widget, CustomRender]

@runtime_checkable
class Splitter(Protocol):
    def __init__(self, *widgets: Union[Widget, CustomRender]) -> None: ...
    @property
    def possible_barlength(self) -> int:...

@runtime_checkable
class Logging(Protocol):
    _logfile: Path
    def set_logfile(self, logfile: str) -> None: ...
    def log(self, content: str, mode: str = 'a') -> None: ...

@runtime_checkable
class Decoy(Protocol):
    def decoy(self, delay: float = 0.1) -> None: ...

@runtime_checkable
class ProgressBar(Logging, Decoy, Protocol):
    precursor: Precursor
    splitter: Splitter
    widgets: List[Union[Widget, CustomRender]]
    tolog: bool
    bar_normalization: float

    def render(self) -> str: ...
    def update(self, i: int) -> None: ...

    @property
    def simulate(self) -> None: ...
    @property
    def finish(self) -> None: ...