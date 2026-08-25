import json
from pathlib import Path

import pytest

from s3mapgen.shortcuts import (
    DEFAULT_SHORTCUTS,
    canonicalize_shortcut,
    shortcut_from_event,
    shortcut_to_tk,
)


GUI_SOURCE = Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')


def test_shortcut_v2_defaults_cover_new_actions_and_allow_disabled_action():
    assert DEFAULT_SHORTCUTS['generate_batch'] == 'Ctrl+Shift+G'
    assert DEFAULT_SHORTCUTS['save_preview'] == 'Ctrl+P'
    assert DEFAULT_SHORTCUTS['manage_history'] == 'Ctrl+H'
    assert DEFAULT_SHORTCUTS['clear_compare'] == ''


def test_shortcuts_are_canonical_and_convert_to_reliable_tk_sequences():
    assert canonicalize_shortcut(' control + shift + t ') == 'Ctrl+Shift+T'
    assert canonicalize_shortcut('Alt+ampersand') == 'Alt+&'
    assert canonicalize_shortcut('f12') == 'F12'
    assert canonicalize_shortcut('') == ''
    assert shortcut_to_tk('Ctrl+Shift+T') == '<Control-Shift-T>'
    assert shortcut_to_tk('Alt+&') == '<Alt-ampersand>'
    assert shortcut_to_tk('') is None
    with pytest.raises(ValueError):
        canonicalize_shortcut('Ctrl+G+H')


def test_capture_understands_modifiers_function_keys_and_azerty_symbols():
    assert shortcut_from_event('T', 0x0001 | 0x0004) == 'Ctrl+Shift+T'
    assert shortcut_from_event('ampersand', 0x0008) == 'Alt+&'
    assert shortcut_from_event('G', 0x0080) == 'G'
    assert shortcut_from_event('G', 0x0004 | 0x0080) == 'Ctrl+G'
    assert shortcut_from_event('G', 0x20000) == 'G'
    assert shortcut_from_event('G', 0x20000, {'Ctrl'}) == 'Ctrl+G'
    assert shortcut_from_event('G', 0, {'Alt'}) == 'Alt+G'
    assert shortcut_from_event('F3', 0) == 'F3'
    assert shortcut_from_event('Control_L', 0x0004) is None


def test_old_settings_are_migrated_and_one_invalid_entry_is_local(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    settings_dir = tmp_path / 'Settlers3MapGen'
    settings_dir.mkdir()
    (settings_dir / 'settings.json').write_text(json.dumps({
        'theme': 'light',
        'shortcuts': {'generate': 'control+shift+g', 'import': 'not a key'},
    }), encoding='utf-8')
    import s3mapgen.preferences as preferences
    loaded = preferences.load_settings()
    assert loaded['settings_version'] == 2
    assert loaded['shortcuts']['generate'] == 'Ctrl+Shift+G'
    assert loaded['shortcuts']['import'] == DEFAULT_SHORTCUTS['import']
    assert loaded['shortcuts']['generate_batch'] == DEFAULT_SHORTCUTS['generate_batch']


def test_disabled_shortcuts_survive_settings_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    import s3mapgen.preferences as preferences
    shortcuts = dict(DEFAULT_SHORTCUTS)
    shortcuts['generate'] = ''
    preferences.save_settings({'shortcuts': shortcuts})
    assert preferences.load_settings()['shortcuts']['generate'] == ''


def test_help_is_a_reusable_themed_toplevel_and_capture_is_not_free_text():
    help_source = GUI_SOURCE.split('    def _show_help(self):', 1)[1].split('    def export(self):', 1)[0]
    settings_source = GUI_SOURCE.split('    def _shortcut_settings_tab(self):', 1)[1].split('    def _capture_translatable_widgets(self):', 1)[0]
    assert 'tk.Toplevel(self)' in help_source
    assert 'messagebox.showinfo' not in help_source
    assert '_apply_help_window_theme()' in GUI_SOURCE
    assert "self._retranslate_help_window()" in GUI_SOURCE
    assert 'shortcut_capture_buttons' in settings_source
    assert 'ttk.Entry' not in settings_source


def test_shortcut_conflicts_and_pending_changes_are_inline_and_non_modal():
    apply_source = GUI_SOURCE.split('    def _apply_shortcut_settings(self):', 1)[1].split('    def _reset_one_shortcut(self,cmd):', 1)[0]
    assert '_refresh_shortcut_validation' in GUI_SOURCE
    assert '_shortcut_status_tooltip' in GUI_SOURCE
    assert 'shortcut_pending_label' in GUI_SOURCE
    assert "state='disabled' if blocked else 'normal'" in GUI_SOURCE
    assert 'messagebox.' not in apply_source


def test_settings_and_shortcuts_share_compact_two_axis_scrolling():
    assert "f=self._scroll_notebook_tab('Paramètres')" in GUI_SOURCE
    assert "f=self._scroll_notebook_tab('Raccourcis')" in GUI_SOURCE
    assert "orient='horizontal'" in GUI_SOURCE
    assert "orient='vertical'" in GUI_SOURCE


def test_windows_shortcut_capture_uses_only_observed_modifier_key_events():
    assert 'GetAsyncKeyState' not in GUI_SOURCE
    assert '_shortcut_capture_modifiers.add(modifier)' in GUI_SOURCE
    assert 'pressed_modifiers=modifiers' in GUI_SOURCE
    assert '_release_shortcut_key' in GUI_SOURCE
