import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import s3mapgen.application.viewer.controller as gui
from PIL import Image as PILImage


def test_gui_has_pillow_image_symbol_for_preview_resize():
    assert gui.Image is PILImage
    assert hasattr(gui.Image, "Resampling")
    assert hasattr(gui.Image.Resampling, "NEAREST")
