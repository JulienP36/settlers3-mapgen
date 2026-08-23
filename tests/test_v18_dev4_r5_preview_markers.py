from pathlib import Path

from s3mapgen.gui_v16 import PREVIEW_START_MARKER_LABELS


SRC = Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')


def test_preview_marker_setting_is_bilingual_and_lives_in_display_settings():
    assert PREVIEW_START_MARKER_LABELS['fr']=={'hidden':'Masqués','small':'Petits','normal':'Normaux'}
    assert PREVIEW_START_MARKER_LABELS['en']=={'hidden':'Hidden','small':'Small','normal':'Normal'}
    settings=SRC[SRC.index('def _settings_tab'):SRC.index('def _build')]
    assert "text='Marqueurs dans les aperçus'" in settings
    assert "bind('<<ComboboxSelected>>',lambda e:self._preview_marker_changed())" in settings


def test_preview_marker_change_is_persisted_and_refreshes_open_batch_previews():
    changed=SRC[SRC.index('def _preview_marker_changed'):SRC.index('def _update_view_controls')]
    assert "self.prefs['preview_start_markers']=self._preview_marker_key()" in changed
    assert 'self._save_prefs()' in changed
    assert 'self._refresh_batch_previews()' in changed


def test_batch_marker_modes_map_to_hidden_small_and_normal_without_touching_starts_view():
    batch=SRC[SRC.index('def _batch_render_thumbnail'):SRC.index('def _refresh_batch_previews')]
    assert "row.get('preview_square_base_key')!=state_key" in batch
    assert "row.get('preview_projected_base_key')!=state_key" in batch
    assert "render_square_base(out.state,view='global'" in batch
    compose=SRC[SRC.index('def _batch_compose_preview'):SRC.index('def _refresh_batch_previews')]
    assert "if marker_mode=='hidden':return base" in compose
    assert "compose_start_markers(base,out.state" in compose
    assert "scale=2 if marker_mode=='normal' else 1" in compose
    render_options=SRC[SRC.index('def _render_options'):SRC.index('def _refresh_preview')]
    assert 'preview_start_markers' not in render_options


def test_open_tooltip_is_updated_atomically_without_destroying_its_window():
    refresh=SRC[SRC.index('def _refresh_batch_previews'):SRC.index('def _batch_schedule_hover_preview')]
    assert '_batch_hide_preview_tooltip' not in refresh
    assert 'self._batch_refresh_preview_tooltip(visible_row)' in refresh
    atomic=SRC[SRC.index('def _batch_refresh_preview_tooltip'):SRC.index('def _batch_hide_preview_tooltip')]
    assert 'label.configure(image=photo)' in atomic
    assert '_batch_hide_preview_tooltip' not in atomic
