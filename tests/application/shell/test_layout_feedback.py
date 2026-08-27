from pathlib import Path

from s3mapgen.application.ui.i18n.shell import FEEDBACK_TEXT

APP_ROOT = Path(__file__).resolve().parents[3] / "s3mapgen" / "application"
SRC = (APP_ROOT / "main_window.py").read_text(encoding="utf-8")
VIEWER_SRC = (APP_ROOT / "viewer" / "controller.py").read_text(encoding="utf-8")

def test_viewer_tools_have_dedicated_responsive_toolbar():
    assert "def _build_viewer_toolbar" in VIEWER_SRC
    assert "def _apply_viewer_toolbar_layout" in VIEWER_SRC
    assert "self.viewer_recenter_button" in VIEWER_SRC
    assert "compact=width<720" in VIEWER_SRC

def test_feedback_covers_user_actions_and_locked_controls():
    for key in ("history_empty","compare_toggled","theme_changed","view_reset","seed_randomized","graph_exported","opacity_locked"):
        assert all(key in catalogue for catalogue in FEEDBACK_TEXT.values())

def test_header_reflows_whole_functional_regions_only():
    assert "compact=width<1750" in SRC
    assert "screen_h<=1100" not in SRC
    assert "self.generation_panel" in SRC
    assert "self.session_box" in SRC
    assert "self.global_panel" in SRC
    assert "Reflow whole functional regions" in SRC
