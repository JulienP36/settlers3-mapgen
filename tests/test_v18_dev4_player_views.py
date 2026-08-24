from pathlib import Path

from s3mapgen.gui_v16 import VIEW_ICON_COLORS, VIEW_LABELS, WINDOW_TITLES


SRC=Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')


def test_dev4_adds_dedicated_localized_starts_view():
    assert VIEW_LABELS['fr']['starts']=='Départs'
    assert VIEW_LABELS['en']['starts']=='Starts'
    assert 'starts' in VIEW_ICON_COLORS
    assert "elif kind=='starts'" in SRC

def test_territories_immediately_follow_starts_in_the_view_list():
    assert list(VIEW_LABELS['fr'])[:3]==['global','starts','territories']
    assert list(VIEW_LABELS['en'])[:3]==['global','starts','territories']


def test_starts_view_uses_the_opacity_slider_while_global_remains_locked():
    assert "state='disabled' if view=='global' else 'normal'" in SRC
    assert "100 if view=='global' else int(self.opacity_var.get())" in SRC
    assert "if self._view_key()=='global'" in SRC


def test_dev4_candidate_title_is_explicit():
    assert all('TITLEBAR_TEST_R4' in title for title in WINDOW_TITLES.values())


def test_batch_previews_use_compact_start_sprites_without_start_boundaries():
    assert "render_square_base(out.state,view='global'" in SRC
    assert "compose_start_markers(base,out.state" in SRC
    assert "scale=2 if marker_mode=='normal' else 1" in SRC
    assert "self.prefs.get('preview_start_markers','small')" in SRC
