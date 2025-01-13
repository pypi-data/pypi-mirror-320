from enum import Enum
import colorama

class Color(Enum):
    """Colour Enum class for colorizing strings.
    
    Example:
    ```python
    >>> from modkit.tools.utilities import Color
    >>> def func(color: Color) -> None:
    ...     print(str(color) + "abc" + color.reset)
    >>> func(Color.RED)
    abc # will be red in color
    ```
    """

    RED: str
    GREEN: str
    BLUE: str
    BLACK: str
    CYAN: str
    MAGENTA: str
    WHITE: str
    YELLOW: str
    LIGHTRED: str
    LIGHTGREEN: str
    LIGHTBLUE: str
    LIGHTBLACK: str
    LIGHTCYAN: str
    LIGHTMAGENTA: str
    LIGHTWHITE: str
    LIGHTYELLOW: str

    @staticmethod
    def colorize() -> None:
        """Initializes color in the terminal."""
    
    @staticmethod
    def fix_ANSI_in_Windows() -> None:
        """Creates a `fix-ANSI.bat` file in the current working
        directory. Run the file using adminitrator priviledges
        to fix Windows CMD/POWERSHELL color handling.
        
        Working:
        - Checks if there is a registry for handling ANSI color codes
        - If not found, creates one.
        """
    
    def __init__(self, color: str) -> None:
        """Enum __init__."""
    
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

    def render(self) -> str:
        """Returns the color code."""

    @property
    def reset(self) -> str:
        """Reset code."""