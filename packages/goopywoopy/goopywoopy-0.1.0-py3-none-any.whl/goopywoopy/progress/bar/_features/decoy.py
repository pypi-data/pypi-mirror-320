from ....abc import Feature
from ..types import ProgressBar
import time

class Decoy(Feature):
    def decoy(self: ProgressBar, delay: float = 0.1):
        for _ in range(self.precursor.totalwork + 1):
            self.update(_)
            time.sleep(delay)
            print(self.render(), end='\r')