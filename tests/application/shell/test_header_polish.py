from pathlib import Path

from s3mapgen.application.ui.widgets.icons import selector_icon_image


APP_ROOT = Path(__file__).resolve().parents[3] / "s3mapgen" / "application"
SRC = "\n".join(
    (APP_ROOT / relative).read_text(encoding="utf-8")
    for relative in ("main_window.py", "history/controller.py")
)


def test_compact_layout_switches_before_the_right_edge_clips():
    assert "compact=width<1750" in SRC
    assert "switch earlier" in SRC


def test_compare_identity_buttons_are_natural_until_real_minimum():
    assert "compact=self._responsive_mode=='compact' and width<900" in SRC
    assert "self.compare_a_button.configure(width=8 if compact else 0)" in SRC
    assert "self.compare_b_button.configure(width=8 if compact else 0)" in SRC


def test_active_compare_delete_buttons_use_red_cross_icon():
    icon = selector_icon_image('#e04444', 'cross', 14)
    assert icon.mode == 'RGBA' and icon.getbbox() is not None
    assert "self._delete_icon_on=_selector_icon(self.session_box,'#e04444','cross',14)" in SRC
    assert "image=self._delete_icon_on if active else self._delete_icon_off" in SRC
