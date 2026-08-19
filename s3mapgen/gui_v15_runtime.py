from .app_paths import LEGACY_PROFILE, UPGRADED_PROFILE, UPGRADED_REFERENCE, LIBRARY
from .generator_v15 import MapGenerator
from .gui_v15 import App as _V15App


class App(_V15App):
    """Final v1.5 GUI runtime using the complete v1.5 generator."""

    def __init__(self):
        super().__init__()
        self.generator = MapGenerator(
            LEGACY_PROFILE,
            LIBRARY,
            UPGRADED_PROFILE,
            UPGRADED_REFERENCE,
            progress_callback=self._progress_stage,
        )


def main():
    App().mainloop()
