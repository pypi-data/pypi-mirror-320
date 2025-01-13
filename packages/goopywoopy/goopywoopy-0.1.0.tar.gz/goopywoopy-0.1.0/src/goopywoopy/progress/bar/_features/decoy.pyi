"""`Decoy` Module

This module contains the `Decoy` feature of the `ProgressBar`. It is responsible for adding an extra
method `decoy` which simulates fake tasks being done in the background of the progressbar. Apart from
adding complex aesthetics and testing it has no purpose. Usage of `Decoy` class standalone is not
possible!

### Usage:

```python
from modkit.progress.bar import ProgressBar, Label, Bar, Time

with ProgressBar(10, 100, Label(), Bar(), Time()) as progressbar:
    progressbar.decoy(delay=0.2) # 200 ms
```
"""

from ....abc import Feature
from ..types import ProgressBar
import time

class Decoy(Feature):
    """Decoy Feature for `ProgressBar` class.
    
    This feature adds an extra method named `decoy` which helps
    creating a decoy progress bar with time delay to simulate
    work being done.
    """
    def decoy(self, delay: float = 0.1) -> None:
        """This method simulates a fake progress bar with time
        delay to simulate some work being done in the background."""