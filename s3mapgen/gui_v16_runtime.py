from .app_paths import LEGACY_PROFILE, UPGRADED_PROFILE, UPGRADED_REFERENCE, LIBRARY
from .generator_v15 import MapGenerator
from .gui_v16 import App as _V16App

class App(_V16App):
    """v1.6 UI/tooling runtime. Generation engine deliberately remains v1.5."""
    def __init__(self):
        super().__init__()
        self.generator=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_PROFILE,UPGRADED_REFERENCE,progress_callback=self._progress_stage)

def main():App().mainloop()
