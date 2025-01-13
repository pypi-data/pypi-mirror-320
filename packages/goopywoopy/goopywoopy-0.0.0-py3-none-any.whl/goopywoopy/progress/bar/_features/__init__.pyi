"""`features` Module

This module contains features for `ProgressBar` class and other sub-requirement classes. 
Current features include:
- `Precursor`: This feature is strictly for defining `Widgets`. Inheriting this feature, tells
    the `ProgressBar` class that the respective widget requires the precursor to render itself
    and therefore `ProgressBar` explicitly provides precursor access to that particular widget.
- `Logging`: A feature that enables `ProgressBar` class to create logs. This is by default
    turned on when wrapping commands/scripts without a callback.
- `Decoy`: This feature helps simulate a fake progress bar for aesthetics or testing purposes
    (with a delay parameter, users can simulate work being done in the background).
- `ShellExecution`: This feature focuses on providing `ProgressBar` class the ability to run
    and wrap shell (bash) codes/scripts around the progress bar.

#### Precursor

The `Precursor` is a special class that contains all information regarding the processes and
the progress bar from the start of the progressbar until it terminates. `Precursor` uses
daemon threads to populate it's attributes that are being accessed by several widgets at any
given instant of time. It is also responsible for updating the status of the tasks that are
being carried out and provide the same information to the progress bar for it to show the
proper and correct status.

Any Feature not added in the __all__ is under development or experimental. Use at your own
risk.
"""

from typing import List
from .logging import Logging
from .precursor import Precursor
from .decoy import Decoy
from .shellexec import ShellExecution

__all__: List[str] = [
    "Logging",
    "Precursor",
    "Decoy",
    "ShellExecution"
]