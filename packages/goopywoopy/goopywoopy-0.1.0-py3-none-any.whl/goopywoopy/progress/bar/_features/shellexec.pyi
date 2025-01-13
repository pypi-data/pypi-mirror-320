"""`shellexec` Module

This module contains the `ShellExecution` Feature class for the `ProgressBar` class. It enables the
progress bar to facilitate shell (bash) code/script execution wrapping.

#### Usage

```python
with ProgressBar(10, 100, Label(), Bar(), Time()) as pbar:
    # 5 tasks as shell codes:
    pbar.use_shell_codes(['echo task 1','echo task 2', 'echo task 3', 'echo task 4', 'echo task 5'])
    # 5 tasks as shell scripts
    pbar.use_shell_scripts(['script.sh', 'script2.sh', 'script3.sh', 'script4.sh', 'script5.sh'])
    # total 10 tasks as mentioned in the ProgressBar(`10`, ...) definiton.
```
"""

from typing import List, Union, Protocol
from ....abc import Feature
from pathlib import Path
import subprocess
import time

class GenericCallback(Protocol):
    """Generic Callback layout."""
    def __call__(self, line: str, rendered: str) -> None:
        """Generic callback for rendering output and progress bar."""

class BottomFix(GenericCallback, Protocol):
    """Bottom Fix Callback Protocol."""
    def __call__(self, line: str, rendered: str) -> None:
        """Callback for Fixing the Progressbar in the bottom."""

class ShellExecution(Feature):
    """ShellExecution Feature for `ProgressBar` class.
    
    This feature adds two extra methods named `use_shell_codes` and
    `use_shell_scripts` which helps wrap execution of each of those
    codes/scripts with the progress bar and update status. Apart from
    these, it adds a callback `BOTTOMFIX_CALLBACK` which when used,
    fixes the progress bar at the bottom
    """

    BOTTOMFIX_CALLBACK: BottomFix

    def use_shell_codes(self, codes: List[str], delay: float = 0.1, callback: Union[GenericCallback, None] = None) -> None:
        """This method wraps the execution of the given shell codes across the progress bar
        and shows the status in the progress bar. The `delay` is the time to wait before
        executing the next code. Stores the output in a logfile. If logfile not given,
        creates a `logs.log` file in the current directory.However, this logging behaviour 
        can be bypassed by providing a callback function that handles what to do with the
        output.
        
        Each callback function must be of the type:
        ```python
        def callback(line: str, rendered: str) -> None: ...
        ```

        A default callback is already present in this class, named `BOTTOMFIX_CALLBACK` which
        fixes the progress bar at the bottom and any output is printed above it. The below
        code replicates the working of this callback:
        ```python
        def BOTTOMFIX_CALLBACK(line: str, rendered: str) -> None:
            print(' ' * len(rendered), end='\r') # erase the progress bar
            print(line) # add the line
            print(rendered, end='\r') # show the progress bar.
        ```

        In the above example, the function takes two parameters:
        - `line`: The stdout or stderr will be passed to this parameter internally.
        - `rendered`: The current rendered string of the progress bar will be passed to this
            parameter internally.
        
        Any callback with the function signature same as above can be used to handle desired
        output style.
        """
    
    def use_shell_scripts(self, script_paths: List[str], delay: float = 0.1, callback: Union[GenericCallback, None] = None) -> None:
        """This method wraps the execution of the given shell scripts across the progress bar
        and shows the status in the bar. The `delay` is the time to wait before executing the
        next code. Stores the output in a logfile. If logfile not given, creates a `logs.log`
        file in the current directory. However, this logging behaviour can be bypassed by
        providing a callback function that handles what to do with the output.
        
        Each callback function must be of the type:
        ```python
        def callback(line: str, rendered: str) -> None: ...
        ```

        A default callback is already present in this class, named `BOTTOMFIX_CALLBACK` which
        fixes the progress bar at the bottom and any output is printed above it. The below
        code replicates the working of this callback:
        ```python
        def BOTTOMFIX_CALLBACK(line: str, rendered: str) -> None:
            print(' ' * len(rendered), end='\r') # erase the progress bar
            print(line) # add the line
            print(rendered, end='\r') # show the progress bar.
        ```

        In the above example, the function takes two parameters:
        - `line`: The stdout or stderr will be passed to this parameter internally.
        - `rendered`: The current rendered string of the progress bar will be passed to this
            parameter internally.
        
        Any callback with the function signature same as above can be used to handle desired
        output style.
        """