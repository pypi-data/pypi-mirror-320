"""types Module

This module contains class types for `bar` module.
"""

from typing import (
    Protocol,
    Self,
    Union,
    Literal,
    List,
    Dict,
    runtime_checkable
)
from threading import Thread, Event
from pathlib import Path

class UnknownLength:
    """A class to mark Unknown Length of an object."""

@runtime_checkable
class Precursor(Protocol):
    """Precursor [`Type`].

    This class represents the internal precursor thread that is
    responsible for updating attributes for runtime information.

    This is just a type declaration of `Precursor` object under
    progressbar module (`modkit.progress.progressbar.precursor.Precursor`)
    and not the actual implementation.
    
    This class (`modkit.progress.progressbar.types.Precursor`)
    supports runtime checking (usage of `isinstance` and 
    `issubclass` methods).

    ### Original Metadata:

    `Precursor Thread Class.`
    
    This class holds all the responsible attributes for smooth
    rendering of the progress bar elements and widgets, and
    creates and maintains several threads for updating those
    attributes as per their criteria.

    The attributes that are monitored are:
    - time elapsed since `use` method is called or context entry.
    - total number of tasks to be done.
    - number of tasks that are completed.
    - percentage of tasks completed.

    The time elapsed since context entry (or `use` method call)
    is done using a separate daemon thread to avoid lag when the
    progress bar is used with other components that costs huge
    amount of resources.
    """

    allthreads: Dict[str, Thread]
    allevents: List[Event]

    class PrecursorError(Exception):
        """Generic Error Exception for Precursor Type."""

        WIDGET_RENDER: Literal["'{}' Widget cannot be rendered! Precursor not set."]
        PRECURSOR_PROPERTY: Literal["'precursor' property error. Precursor not set."]
        PRECURSOR_INSTANCE: Literal["'{}' must be of the type Precursor."]
        PRECURSOR_DELETE: Literal["Cannot delete Precursor."]
        PRECURSOR_THREAD: Literal["Cannot get thread! Precursor is not set."]
        NOT_NEEDED: Literal["Precursor is not required for this widget and hence, all related functionalities are disabled."]
    
    def __init__(self, total: Union[int, float]) -> None:
        """Create a `Precursor` object.
        
        This creates a `Precursor` thread object that is responsible for creating
        and managing threads to update class attributes and store relevant data
        which is essential for smooth rendering of the progress bar.
        """
    
    def __enter__(self) -> Self:
        """Context Manager Entry Point."""
    
    def __exit__(self, e_type, e_value, e_traceback) -> bool:
        """Context Manager Exit Point."""

    def use(self) -> Self:
        """Start all threads of precursor class and populate the
        attributes and is automatically called if context
        manager is used. This method can only be called once per
        initialization of `Precursor` class.

        ```python
        With Precursor(100) as p:
            # at this point, `use` method has already been run.
            # rest of the code goes here
            pass
        ```
        """
    
    def cease(self) -> Self:
        """Cease all threads and wait for them to finish and exit.
        This method is automatically called upon exiting the `With`
        block when used with context manager."""

    @property
    def totalwork(self) -> Union[int, float]:
        """Total Work count to be carried out."""
    
    @property
    def complete(self) -> Union[int, float]:
        """Completed work count."""
    
    @property
    def percent(self) -> float:
        """Percent of work done."""

    @property
    def secondselapsed(self) -> float:
        """Seconds elapsed since `use` was called."""
    
    @property
    def threads(self) -> Dict[str, Thread]:
        """All threads in the form of a `{'name': thread}` format."""

@runtime_checkable
class Widget(Protocol):
    """Widget [`Type`].
    
    This is a type declaration for objects that inherit that `Widget` abstract
    class (`modkit.progress.progressbar.widgets.abc.Widget`) and not the actual
    implementation. This class particularly represents any class that inherits
    from the `Widget` abstract class and not the `Widget` class itself.
    """
    __name__: str

    @property
    def precursor(self) -> Precursor:
        """Precursor getter, setter, deleter."""

    @property
    def length(self) -> Union[int, UnknownLength]:
        """Absolute fixed length of the widget."""

    @property
    def thread(self) -> Thread:
        """The underlying thread that is responsible for updating
        this widget's precursor attribute."""
    
    @property
    def is_sensitive(self) -> bool:
        """True if thread needs to be run separately for constant
        update."""

    def render(self) -> str:
        """Renders widget's current state and returns a string."""

@runtime_checkable
class CustomRender(Widget, Protocol):
    """CustomRender [`Type`].
    
    This is a type declaration for all widgets that inherit the `CustomRender`
    abstract class and not the implementation itself. The implementation can be
    found under `modkit.progress.progressbar.widgets.abc`.w
    """
    def render(self) -> str:
        """Renders widget's current state based on possible length and normalization."""
    def set_possible_length(self, length: float) -> None:
        """Set the possible length for custom rendering."""
    def set_normalization(self, normalization: float) -> None:
        """Set the normalization for custom rendering."""

@runtime_checkable
class WidgetWrapper(Widget, Protocol):
    """WidgetWrapper [`Type`].
    
    This is a type declaration for all widgets that inherit the `WidgetWrapper`
    abstract class and not the implementation itself.
    """
    widget: Union[Widget, CustomRender]

@runtime_checkable
class Splitter(Protocol):
    """Splitter [`Type`].

    This is a type declaration for `Splitter` class found under
    `modkit.progress.progressbar.utils`.

    ### Original Metadata:

    `Splitter Class.`
    
    This class helps deduce tha bar length based on passed widgets
    and the terminal column size.
    """
    def __init__(self, *widgets: Union[Widget, CustomRender]) -> None:
        """Create a splitter object."""
    
    @property
    def possible_barlength(self) -> int:
        """Returns only the bar's length to fit it according to parameters."""

@runtime_checkable
class Logging(Protocol):
    """Logging Feature [`Type`].
    
    This is a type declaration and not the actual implementation
    of this feature.

    ### Original Metadata:

    Logging Feature for `ProgressBar` class.
    
    This feature adds logging abilities to the `ProgressBar` class
    by adding two methods: `set_logfile` and `log`.
    """
    _logfile: Path
    def set_logfile(self, logfile: str) -> None:
        """Set the path of logfile for logging. If this method
        is never called, by default, the log file is created in
        the current directory named `logs.log`."""
    def log(self, content: str, mode: str = 'a') -> None:
        """Logs a given content to the logfile with given mode."""

@runtime_checkable
class Decoy(Protocol):
    """Decoy Feature [`Type`].
    
    This is a type declaration of Decoy Feature and not the
    actual implementation

    ### Original Metadata

    Decoy Feature for `ProgressBar` class.
    
    This feature adds an extra method named `decoy` which helps
    creating a decoy progress bar with time delay to simulate
    work being done.
    """
    def decoy(self: ProgressBar, delay: float = 0.1) -> None:
        """This method simulates a fake progress bar with time
        delay to simulate some work being done in the background."""

@runtime_checkable
class ProgressBar(Logging, Decoy, Protocol):
    """ProgressBar [`Type`].
    
    This is a type declaration for `ProgressBar` class and not the actual
    implementation.
    """
    precursor: Precursor
    splitter: Splitter
    widgets: List[Union[Widget, CustomRender]]
    tolog: bool
    bar_normalization: float

    def render(self) -> str:
        """Renders the progress bar for this instant."""
    
    def update(self, i: int) -> None:
        """Updates the completed task count."""
    
    @property
    def simulate(self) -> None:
        """Start the `ProgressBar` `Precursor` Thread that handles all
        sensitive and non sensitive widgets."""
    
    @property
    def finish(Self) -> None:
        """Stop the `ProgressBar` `Precursor` Thread which ultimately
        puts a stop to all widget functionality and prints the final
        rendered progress bar in the terminal."""