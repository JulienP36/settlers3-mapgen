from pathlib import Path

SRC = (Path(__file__).parents[1] / "s3mapgen" / "gui_v16.py").read_text(encoding="utf-8")

def test_legacy_header_progressbar_is_never_remapped_by_responsive_layout():
    assert "The historical header Progressbar is obsolete" in SRC
    assert "self.progress.grid(row=9" not in SRC
    assert "self.progress.grid(row=7" not in SRC

def test_viewer_tools_have_dedicated_responsive_toolbar():
    assert "def _build_viewer_toolbar" in SRC
    assert "def _apply_viewer_toolbar_layout" in SRC
    assert "self.viewer_recenter_button" in SRC
    assert "compact=width<720" in SRC

def test_feedback_v1_covers_new_user_actions():
    for key in ("history_empty","compare_toggled","theme_changed","view_reset","seed_randomized","graph_exported","opacity_locked"):
        assert f"'{key}'" in SRC

def test_r6_header_reflows_whole_functional_regions_only():
    assert "compact=width<1750" in SRC
    assert "screen_h<=1100" not in SRC
    assert "self.generation_panel" in SRC
    assert "self.session_box" in SRC
    assert "self.global_panel" in SRC
    assert "Reflow whole functional regions" in SRC
