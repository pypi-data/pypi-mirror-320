"""`bar` Module

This module includes every publicly available class related to creating
a progress bar.
"""

from typing import List
from .core import ProgressBar
from .widgets import (
    Label,
    Bar,
    Time
)
from .widgets import Tint, Color

__all__: List[str] = [
    # ProgressBar
    "ProgressBar",

    # Widgets
    "Label",
    "Bar",
    "Time",

    # Tint
    "Tint",
    "Color"
]