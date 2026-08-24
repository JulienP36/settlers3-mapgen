from pathlib import Path

import pytest

from s3mapgen.native_titlebar import (
    DWMWA_BORDER_COLOR,
    DWMWA_CAPTION_COLOR,
    DWMWA_TEXT_COLOR,
    DWMWA_USE_IMMERSIVE_DARK_MODE,
    _hex_to_colorref,
    apply_native_titlebar,
)


GUI_SOURCE = Path('s3mapgen/gui_v16.py').read_text(encoding='utf-8')


def test_colorref_conversion_uses_win32_bgr_byte_order():
    assert _hex_to_colorref('#112233') == 0x00332211
    assert _hex_to_colorref('A0B0C0') == 0x00C0B0A0
    with pytest.raises(ValueError):
        _hex_to_colorref('#123')


def test_documented_dwm_attribute_numbers_are_kept_explicit():
    assert DWMWA_USE_IMMERSIVE_DARK_MODE == 20
    assert (DWMWA_BORDER_COLOR, DWMWA_CAPTION_COLOR, DWMWA_TEXT_COLOR) == (34, 35, 36)


def test_non_windows_platform_is_a_safe_noop(monkeypatch):
    monkeypatch.setattr('s3mapgen.native_titlebar.sys.platform', 'linux')

    class WindowThatMustNotBeTouched:
        def __getattr__(self, name):
            raise AssertionError(name)

    # The helper must return before touching Tk or loading Win32 libraries.
    assert apply_native_titlebar(WindowThatMustNotBeTouched(), {}) is False


def test_titlebars_refresh_on_theme_changes_and_new_toplevel_maps():
    assert "bind_class('Toplevel','<Map>',self._native_titlebar_mapped,add='+')" in GUI_SOURCE
    assert 'self._schedule_native_titlebar_refresh()' in GUI_SOURCE
    assert 'apply_native_titlebar(target,palette)' in GUI_SOURCE


def test_built_in_themes_have_distinct_native_caption_palettes():
    from s3mapgen.gui_v16 import THEME_PALETTES

    dark = THEME_PALETTES['dark']
    light = THEME_PALETTES['light']
    assert dark['titlebar_dark'] is True
    assert dark['titlebar'] == '#15171a'
    assert dark['titlebar_text'] == '#e8eaed'
    assert dark['titlebar_border'] == '#3c4043'
    assert dark['titlebar_separator'] == '#6f7378'
    assert light['titlebar_dark'] is False
    assert light['titlebar'] == '#dfe3e8'
    assert light['titlebar_text'] == '#202124'
    assert light['titlebar_border'] == '#aeb3b8'
    assert light['titlebar_separator'] == '#8f969e'
    assert dark['titlebar'] != dark['window']
    assert light['titlebar'] != light['window']


def test_separator_is_a_real_client_edge_overlay_not_only_a_dwm_border():
    source = Path('s3mapgen/native_titlebar.py').read_text(encoding='utf-8')
    assert 'relwidth=1, height=1' in source
    assert 'titlebar_separator' in source
