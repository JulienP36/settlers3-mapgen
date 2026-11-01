"""Exercise the UI save path through disk, rather than only the settings model."""
from types import SimpleNamespace

from s3mapgen.application.settings.controller import SettingsController
from s3mapgen.application.settings import preferences
from s3mapgen.application.viewer.controller import ViewerController
from s3mapgen.application.ui.i18n.viewer import VALID_START_LABELS


def test_departure_filter_selection_survives_other_preferences_and_restart(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    class Value:
        def __init__(self, value):
            self.value = value
        def get(self):
            return self.value

    window = SimpleNamespace(
        prefs=preferences.load_settings(), current=None,
        opacity_var=Value(42), wheel_var=Value(1.12),
        heatmap_var=Value(VALID_START_LABELS['fr']['valid_2:current']),
        _view_key=lambda: 'valid_starts', _refresh_preview=lambda *args: None,
    )
    window._save_prefs = lambda: SettingsController._save_prefs(window)
    ViewerController._heatmap_changed(window)
    assert preferences.load_settings()['valid_start_filter'] == 'valid_2:current'

    # A later unrelated setting change must not silently reset the filter.
    window.prefs['theme'] = 'light'
    window._save_prefs()
    restarted = preferences.load_settings()
    assert restarted['valid_start_filter'] == 'valid_2:current'
    assert restarted['theme'] == 'light'
    assert restarted['overlay_alpha'] == 42
    assert restarted['wheel_zoom'] == 1.12
