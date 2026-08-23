import importlib

def test_preferences_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    import s3mapgen.preferences as p;importlib.reload(p)
    custom=dict(p.DEFAULT_SHORTCUTS);custom['generate']='Ctrl+Shift+G'
    p.save_settings({'theme':'light','overlay_alpha':42,'projection':'parallelogram','preview_start_markers':'normal','wheel_zoom':1.12,'language':'en','shortcuts':custom})
    got=p.load_settings();assert got['theme']=='light';assert got['overlay_alpha']==42;assert got['projection']=='parallelogram';assert got['preview_start_markers']=='normal';assert abs(got['wheel_zoom']-1.12)<1e-9;assert got['language']=='en';assert got['shortcuts']['generate']=='Ctrl+Shift+G'

def test_defaults_include_dark_mode_and_shortcuts():
    import s3mapgen.preferences as p
    assert p.DEFAULTS['theme']=='dark';assert p.DEFAULTS['language']=='fr';assert p.DEFAULT_SHORTCUTS['help']=='F1'

def test_default_overlay_opacity_is_75_percent():
    import s3mapgen.preferences as p
    assert p.DEFAULTS['overlay_alpha']==75

def test_preview_start_markers_default_to_small_and_invalid_values_are_cleaned(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    import s3mapgen.preferences as p;importlib.reload(p)
    assert p.DEFAULTS['preview_start_markers']=='small'
    p.save_settings({'preview_start_markers':'oversized'})
    assert p.load_settings()['preview_start_markers']=='small'


def test_shift_shortcuts_use_uppercase_tk_keysym():
    from s3mapgen.gui_v16 import App
    assert App._tk_sequence('Ctrl+Shift+T') == '<Control-Shift-T>'
    assert App._tk_sequence('Ctrl+Shift+C') == '<Control-Shift-C>'


def test_simple_letter_shortcut_stays_lowercase_tk_keysym():
    from s3mapgen.gui_v16 import App
    assert App._tk_sequence('A') == '<a>'
