from pathlib import Path

import numpy as np

from s3mapgen.binary import read_area, read_starts
from s3mapgen.preview import compose_rendered_map, render, render_square_base


SRC=Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')


def _reference_state():
    path=Path('data/upgraded_reference_768.edm')
    state=read_area(path);state.starts=read_starts(path)
    return state


def test_split_renderer_is_pixel_identical_to_public_render_for_both_projections():
    state=_reference_state()
    for view,alpha in (('global',100),('starts',63),('territories',72)):
        base=render_square_base(state,view=view,overlay_alpha=alpha)
        for projection in ('square','parallelogram'):
            split=compose_rendered_map(base,state,labels=True,view=view,overlay_alpha=alpha,projection=projection)
            direct=render(state,labels=True,view=view,overlay_alpha=alpha,projection=projection)
            assert split.mode==direct.mode and split.size==direct.size
            assert np.array_equal(np.asarray(split),np.asarray(direct))


def test_language_theme_and_projection_do_not_invalidate_colorized_map_layer():
    language=SRC[SRC.index('def _language_changed'):SRC.index('def _apply_theme')]
    toggle=SRC[SRC.index('def _toggle_theme'):SRC.index('def _projection_changed')]
    projection=SRC[SRC.index('def _projection_changed'):SRC.index('def _preview_marker_changed')]
    assert '_invalidate_preview' not in language
    assert '_invalidate_preview' not in toggle
    assert '_invalidate_preview' not in projection
    assert '_refresh_preview' in language and '_refresh_preview' in toggle and '_refresh_preview' in projection


def test_main_preview_reuses_square_layer_and_bounds_projection_composites():
    refresh=SRC[SRC.index('def _refresh_preview'):SRC.index('def _source_cell_from_canvas')]
    assert "layer_view='global' if opts['view'] in ('global','starts')" in refresh
    assert 'render_square_base(state,layer_view,layer_alpha' in refresh
    assert 'if composite_key not in self._preview_projection_cache' in refresh
    assert 'compose_rendered_map(self._preview_layer_base,state' in refresh
    invalidate=SRC[SRC.index('def _invalidate_preview(self)'):SRC.index('def _refresh_preview')]
    assert 'self._preview_projection_cache={}' in invalidate
    view_change=SRC[SRC.index('def _view_changed'):SRC.index('def random_seed')]
    assert '_invalidate_preview' not in view_change


def test_starts_opacity_discards_only_composites_while_other_overlays_recolor():
    changed=SRC[SRC.index('def _opacity_changed'):SRC.index('def _wheel_changed')]
    assert "if self._view_key()=='starts':self._invalidate_preview_composite()" in changed
    assert 'else:self._invalidate_preview()' in changed


def test_batch_keeps_one_square_and_one_projected_base_per_result():
    batch=SRC[SRC.index('def _batch_render_thumbnail'):SRC.index('def _refresh_batch_previews')]
    assert "row.get('preview_square_base_key')!=state_key" in batch
    assert "row['preview_projected_base_image']=None" in batch
    assert "row.get('preview_projected_base_key')!=state_key" in batch
    assert "project_parallelogram(row['preview_square_base_image'])" in batch


def test_fast_slider_preferences_are_debounced_and_flushed_on_close():
    schedule=SRC[SRC.index('def _schedule_prefs_save'):SRC.index('def _theme_changed')]
    assert 'after_cancel(self._prefs_save_after)' in schedule
    assert 'self.after(200,self._flush_scheduled_prefs)' in schedule
    assert 'def destroy(self)' in schedule and 'self._save_prefs()' in schedule
    wheel=SRC[SRC.index('def _wheel_changed'):SRC.index('def _update_view_controls')]
    opacity=SRC[SRC.index('def _opacity_changed'):SRC.index('def _wheel_changed')]
    assert '_schedule_prefs_save()' in wheel
    assert '_schedule_prefs_save()' in opacity
