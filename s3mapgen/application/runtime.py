"""Composition root binding the current UI to the protected v1.5 generator."""

from .paths import LEGACY_PROFILE, UPGRADED_PROFILE, UPGRADED_REFERENCE, LIBRARY
from ..generation import MapGenerator
from .main_window import MainWindow

class App(MainWindow):
    """Desktop runtime bound to the validated generation pipeline."""
    def __init__(self):
        super().__init__()
        self.generator=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_PROFILE,UPGRADED_REFERENCE,progress_callback=self._progress_stage)

def main():App().mainloop()
