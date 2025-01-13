"""core Module

This module under `bar` module contains the main `ProgressBar`
class responsible for simulating a progress bar.
"""

from typing import (
    Union,
    Self,
)
from ._precursor import Precursor
from ._features import Logging, Decoy, ShellExecution
from .utils import Splitter
from .widgets import Label, Bar, Time
from .types import Widget, CustomRender

class ProgressBar(Logging, Decoy, ShellExecution):
    """`Progress Bar Class.`
    
    This class helps creating customizable progress bars based on given
    parameters and different kinds of widgets.

    External Features that are inherited by this class
    (from `modkit.progress.progressbar.features`):
    - `Logging` (Logging results of executed commands, if any).
    - `Decoy` (Fake Progress Bar creation for simulating work).
    """
    def __init__(
            self,
            total: int,
            normalized_bar_size: float = 100,
            *widgets: Union[Widget, CustomRender],
            logfile: Union[str, None] = None,
    ) -> None:
        """Create a Progress Bar object with a set of parameters.
        
        #### Parameter Description

        - `total` is the total number of tasks to be carried out.
        - `normalized_bar_size` must be a float value from 0..100. If 100,
            the maximum area the bar can occupy will be accepted apart from
            the widgets. If it is lower that 100, say 70, only 70% of the
            maximum space the bar can occupy will be accepted for creating the
            progress bar. 
        - `*widgets` accepts all widgets in sequence (from left to right) that
            are to be included in the progress bar.

        >>> from modkit.progress.progressbar import ProgressBar
        >>> from modkit.progress.progressbar import Label, Bar, Time
        >>> bar = ProgressBar(10, 100, Label('label:'), Bar(), Time())
        >>> bar.
        >>> # bar => label: |████████████████████| Time Elapsed: HH:MM:SS

        - `logfile` is the path to the logfile. The logfile may or maynot
            exist but the parent directory of the path must exist.
        
        #### Definition

        `ProgressBar` class can either be called with the `with` keyword or
        normally using a variable to store the `ProgressBar` object.

        >>> # with keyword
        >>> with ProgressBar(10, 60, Label('ABC:'), Bar(), Time()) as bar:
        ...     bar.decoy(0.2)

        >>> # normally
        >>> bar = ProgressBar(10, 50, Label(), Bar(), Time())
        >>> bar.simulate # auto called with `with` keyword
        >>> bar.decoy(0.1)
        >>> bar.finish # auto called with `with` keyword

        Note that once `simulate` property has been invoked, invoking it
        again will raise a `RuntimeError`. Same with the `finish` property.

        It is also not possible to start the progress bar again using the
        `simulate` property once `finish` has been invoked. A new instance
        of the `ProgressBar` class has to be created. This is due to thread
        safety and limitaions of the `threading` library.
        """
    
    def __enter__(self) -> Self:
        """Context Manager Entry Point.
        
        Invokes the `simulate` property automatically once the context
        manager comes into play.
        """
    
    def __exit__(self, e_type: type, e_value: Exception, e_tb: any) -> bool:
        """Context Manager Exit Point.
        
        Invokes the `finish` property automatically once the context manager
        exits. Returns `False` when it is supposed to handle exceptions, and
        `True` when it is supposed to suppress exceptions. By default, it
        returns `False`.
        """
    
    def render(self) -> str:
        """Renders the bar at this current instant of time and returns the
        progress bar as a string. The maximum length of the string is the
        terminal window width."""
    
    def update(self, i: int) -> None:
        """Updates the `completed` job count and replaces it with `i`."""
    
    @property
    def simulate(self) -> None:
        """Start the `ProgressBar` `Precursor` Thread that handles all
        sensitive and non sensitive widgets."""
    
    @property
    def finish(Self) -> None:
        """Stop the `ProgressBar` `Precursor` Thread which ultimately
        puts a stop to all widget functionality and prints the final
        rendered progress bar in the terminal."""