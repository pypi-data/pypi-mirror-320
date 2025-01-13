from shutil import get_terminal_size as terminal
from typing import Union, List
from ..types import Widget, CustomRender

class Splitter:
    def __init__(self, *widgets: Union[Widget, CustomRender]) -> None:
        if not all(isinstance(widget, (CustomRender, Widget)) for widget in widgets):
            raise TypeError(
                "'widgets' parameter must contain objects which are child class `Widget`"
            )
        
        self.lengths: List[int] = [widget.length for widget in widgets if isinstance(widget.length, int)] # all except Bar types

        occupied_length = self.lengths[0] + 1 # first widget plus space
        for l in self.lengths[1:len(self.lengths)-1]: # for the remaining widgets except the last one
            occupied_length += l + 1
        occupied_length += self.lengths[-1] # for the last one

        self.remaining_length = terminal().columns - occupied_length # occupied length contains all widgets plus space.
    
    @property
    def possible_barlength(self) -> int:
        return self.remaining_length - 1 # exclude the space for bar.