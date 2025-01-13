"""This is the core of the `Precursor` Module and contains the `Precursor` class."""

from threading import Thread, Event
from typing import (
    Dict,
    List,
    Self,
    Literal,
    Union,
)

class Precursor:
    """`Precursor Thread Class.`
    
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
    
    @complete.setter
    def complete(self, comp: Union[int, float]) -> None: ...
    @complete.deleter
    def complete(self) -> None: ...
    
    @property
    def percent(self) -> float:
        """Percent of work done."""

    @property
    def secondselapsed(self) -> float:
        """Seconds elapsed since `use` was called."""
    
    @property
    def threads(self) -> Dict[str, Thread]:
        """All threads in the form of a `{'name': thread}` format."""