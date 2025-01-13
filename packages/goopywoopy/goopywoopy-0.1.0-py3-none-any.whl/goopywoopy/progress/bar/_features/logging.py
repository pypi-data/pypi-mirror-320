from ....abc import Feature
from pathlib import Path
from ..types import ProgressBar

class Logging(Feature):
    _logfile = Path.cwd() / 'logfile.log'

    def set_logfile(self: ProgressBar, logfile: str) -> None:
        self._logfile = Path(logfile).expanduser().resolve()
        if not self._logfile.parent.exists():
            raise FileNotFoundError("Parent directory of given logfile path does not exist.")
    
    def log(self: ProgressBar, content: str, mode: str = 'a') -> None:
        with open(str(self._logfile), mode=mode) as log_reference:
            log_reference.write(content)
    