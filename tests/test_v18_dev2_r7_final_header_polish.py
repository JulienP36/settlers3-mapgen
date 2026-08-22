from pathlib import Path


SRC = (Path(__file__).parents[1] / "s3mapgen" / "gui_v16.py").read_text(encoding="utf-8")


def test_inherited_elastic_header_columns_are_reset():
    assert "for c in range(18):top.columnconfigure(c,weight=0,minsize=0)" in SRC
    assert "prevent the global region from reaching the right edge" in SRC


def test_compact_switches_before_the_r6_right_edge_clip():
    assert "compact=width<1750" in SRC
    assert "switch earlier" in SRC


def test_compare_identity_buttons_are_natural_until_real_minimum():
    assert "compact=self._responsive_mode=='compact' and width<900" in SRC
    assert "self.compare_a_button.configure(width=8 if compact else 0)" in SRC
    assert "self.compare_b_button.configure(width=8 if compact else 0)" in SRC


def test_active_compare_delete_buttons_use_red_cross_icon():
    assert "elif kind=='cross':" in SRC
    assert "self._delete_icon_on=_selector_icon(self.session_box,'#e04444','cross',14)" in SRC
    assert "image=self._delete_icon_on if active else self._delete_icon_off" in SRC
