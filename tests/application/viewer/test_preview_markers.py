from pathlib import Path

from s3mapgen.application.ui.i18n.shell import PREVIEW_START_MARKER_LABELS


MAIN_SRC = Path('s3mapgen/application/main_window.py').read_text(encoding='utf-8')
SETTINGS_SRC = Path('s3mapgen/application/settings/controller.py').read_text(encoding='utf-8')
VIEWER_SRC = Path('s3mapgen/application/viewer/controller.py').read_text(encoding='utf-8')
BATCH_SRC = Path('s3mapgen/application/batch/controller.py').read_text(encoding='utf-8')
SRC = '\n'.join((MAIN_SRC, SETTINGS_SRC, VIEWER_SRC, BATCH_SRC))


def test_preview_marker_setting_is_bilingual_and_lives_in_display_settings():
    assert PREVIEW_START_MARKER_LABELS['fr']=={'hidden':'Masqués','tiny':'Petits','small':'Normaux','normal':'Grands'}
    assert PREVIEW_START_MARKER_LABELS['en']=={'hidden':'Hidden','tiny':'Tiny','small':'Normal','normal':'Large'}
    settings=SETTINGS_SRC[SETTINGS_SRC.index('def _settings_tab'):SETTINGS_SRC.index('def _find_combo_for_var')]
    assert "text='Marqueurs de départ'" in settings
    assert "bind('<<ComboboxSelected>>',lambda e:self._preview_marker_changed())" in settings


def test_preview_marker_change_is_persisted_and_refreshes_open_batch_previews():
    changed=VIEWER_SRC[VIEWER_SRC.index('def _preview_marker_changed'):VIEWER_SRC.index('def _update_view_controls')]
    assert "self.prefs['preview_start_markers']=self._preview_marker_key()" in changed
    assert 'self._save_prefs()' in changed
    assert 'self._refresh_preview(False)' in changed
    assert 'self._refresh_batch_previews()' in changed


def test_marker_modes_map_to_hidden_tiny_normal_and_large_in_batch_and_starts_views():
    batch=SRC[SRC.index('def _batch_render_thumbnail'):SRC.index('def _refresh_batch_previews')]
    assert "row.get('preview_square_base_key')!=state_key" in batch
    assert "row.get('preview_projected_base_key')!=state_key" in batch
    assert "render_square_base(out.state,view='global'" in batch
    compose=SRC[SRC.index('def _batch_compose_preview'):SRC.index('def _refresh_batch_previews')]
    assert "if marker_mode=='hidden':return base" in compose
    assert "compose_start_markers(base,out.state" in compose
    assert "scale=START_MARKER_SCALES.get(marker_mode,START_MARKER_SCALES['small'])" in compose
    render_options=VIEWER_SRC[VIEWER_SRC.index('def _render_options'):VIEWER_SRC.index('def _refresh_preview')]
    assert "'start_markers':bool(view=='starts' and marker_mode!='hidden')" in render_options
    assert "'start_marker_scale':START_MARKER_SCALES.get(marker_mode,START_MARKER_SCALES['small'])" in render_options


def test_open_tooltip_is_updated_atomically_without_destroying_its_window():
    refresh=SRC[SRC.index('def _refresh_batch_previews'):SRC.index('def _batch_schedule_hover_preview')]
    assert '_batch_hide_preview_tooltip' not in refresh
    assert 'self._batch_refresh_preview_tooltip(visible_row)' in refresh
    atomic=SRC[SRC.index('def _batch_refresh_preview_tooltip'):SRC.index('def _batch_hide_preview_tooltip')]
    assert 'label.configure(image=photo)' in atomic
    assert '_batch_hide_preview_tooltip' not in atomic
