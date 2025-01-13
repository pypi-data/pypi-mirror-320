"""`Precursor` Module

This module contains the `Precursor` Feature class that helps identify widgets that require
precursor (thread handler class with the same name) access.
"""

from ....abc import Feature
from typing import Literal

class Precursor(Feature):
    """Precursor Feature for Widgets.
    
    Inheriting this feature adds an attribute `__precursor__` which
    depicts that the current widget requires precursor to function
    and requires the `ProgressBar` class to set the precursor for
    this widget before proceeding.
    """
    __precursor__: Literal['enabled']