from pathlib import Path

from s3mapgen.application.ui.i18n.viewer import VIEW_LABELS
from s3mapgen.application.ui.viewer.options import VIEW_ICON_COLORS
from s3mapgen.application.ui.widgets.icons import selector_icon_image


SRC='\n'.join(
    Path(path).read_text(encoding='utf-8')
    for path in (
        's3mapgen/application/main_window.py',
        's3mapgen/application/viewer/controller.py',
        's3mapgen/application/batch/controller.py',
    )
)


def test_starts_view_has_a_renderable_icon():
    assert 'starts' in VIEW_ICON_COLORS
    icon = selector_icon_image(VIEW_ICON_COLORS['starts'], 'starts')
    assert icon.mode == 'RGBA' and icon.getbbox() is not None

def test_territories_immediately_follow_starts_in_the_view_list():
    assert list(VIEW_LABELS['fr'])[:3]==['global','starts','territories']
    assert list(VIEW_LABELS['en'])[:3]==['global','starts','territories']


def test_starts_view_uses_the_opacity_slider_while_global_remains_locked():
    assert "state='disabled' if view=='global' else 'normal'" in SRC
    assert "100 if view=='global' else int(self.opacity_var.get())" in SRC
    assert "if self._view_key()=='global'" in SRC

def test_batch_previews_use_compact_start_sprites_without_start_boundaries():
    assert "render_square_base(out.state,view='global'" in SRC
    assert "compose_start_markers(base,out.state" in SRC
    assert "scale=2 if marker_mode=='normal' else 1" in SRC
    assert "self.prefs.get('preview_start_markers','small')" in SRC
