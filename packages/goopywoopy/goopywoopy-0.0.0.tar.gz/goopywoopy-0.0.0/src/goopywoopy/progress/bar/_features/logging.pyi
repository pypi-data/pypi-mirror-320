"""`Logging` Module

This module contains the `Logging` feature for `ProgressBar` class. Usage of this class standalone is
somewhat possible but not recommended. It simply adds two methods `set_logfile` and `log` which as
their name suggests, are for setting the logfile and logging result/output respectively.

#### Usage

```python
with ProgressBar(11, 75, Label(), Bar(), Time(), logfile='some-log-file.log') as progressbar:
    progressbar.set_logfile('some-log-file.log') # this is redundant, but can be used to change the logfile mid way.
    progressbar.use_shell_codes(['echo hello', 'sleep 2', 'echo all done.'])

# the output of the shell codes will be logged to `some-log-file.log` in the current directory.
# provide full path to choose a different parent folder for the logfile.
```
"""

from ....abc import Feature
from pathlib import Path
from ..types import ProgressBar

class Logging(Feature):
    """Logging Feature for `ProgressBar` class.
    
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