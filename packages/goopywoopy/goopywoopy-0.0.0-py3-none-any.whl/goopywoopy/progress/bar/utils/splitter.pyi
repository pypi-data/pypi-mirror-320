"""Splitter Module

This module contains the `Splitter` class that helps
deduce the actual length of the `Bar` widget based
on the widgets that are to be used and the terminal
column size.
"""

from shutil import get_terminal_size as terminal
from typing import Union, Protocol, runtime_checkable, List
from ..types import Widget, CustomRender

class Splitter:
    """`Splitter Class.`
    
    This class helps deduce tha bar length based on passed widgets
    and the terminal column size.
    """
    def __init__(self, *widgets: Union[Widget, CustomRender]) -> None:
        """Create a splitter object."""
    
    @property
    def possible_barlength(self) -> int:
        """Returns only the bar's length to fit it according to parameters."""