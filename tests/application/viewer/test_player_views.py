from pathlib import Path

from s3mapgen.application.ui.i18n.viewer import VIEW_LABELS
from s3mapgen.application.ui.viewer.options import VIEW_ICON_COLORS


SRC='\n'.join(
    Path(path).read_text(encoding='utf-8')
    for path in (
        's3mapgen/application/main_window.py',
        's3mapgen/application/viewer/controller.py',
        's3mapgen/application/batch/controller.py',
    )
)


def test_starts_view_is_removed_from_the_view_selector():
    assert 'starts' not in VIEW_ICON_COLORS
    assert all('starts' not in labels for labels in VIEW_LABELS.values())

def test_territories_are_the_second_view_after_global():
    assert list(VIEW_LABELS['fr'])[:2]==['global','territories']
    assert list(VIEW_LABELS['en'])[:2]==['global','territories']


def test_all_real_views_keep_the_global_opacity_rule():
    assert "state='disabled' if view=='global' else 'normal'" in SRC
    assert "'overlay_alpha':100 if view=='global' else int(self.opacity_var.get())" in SRC
    assert "if self._view_key()=='starts'" not in SRC

def test_batch_previews_use_compact_start_sprites_without_start_boundaries():
    assert "render_square_base(out.state,view='global'" in SRC
    assert "compose_start_markers(base,out.state" in SRC
    assert "scale=START_MARKER_SCALES.get(marker_mode,START_MARKER_SCALES['small'])" in SRC
    assert "self.prefs.get('preview_start_markers','small')" in SRC
    assert "start_circles=bool(self.prefs.get('preview_start_circles',False))" in SRC
