import importlib

def test_preferences_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    import s3mapgen.preferences as p;importlib.reload(p)
    custom=dict(p.DEFAULT_SHORTCUTS);custom['generate']='Ctrl+Shift+G'
    p.save_settings({'theme':'light','overlay_alpha':42,'projection':'parallelogram','wheel_zoom':1.12,'language':'en','shortcuts':custom})
    got=p.load_settings();assert got['theme']=='light';assert got['overlay_alpha']==42;assert got['projection']=='parallelogram';assert abs(got['wheel_zoom']-1.12)<1e-9;assert got['language']=='en';assert got['shortcuts']['generate']=='Ctrl+Shift+G'

def test_defaults_include_dark_mode_and_shortcuts():
    import s3mapgen.preferences as p
    assert p.DEFAULTS['theme']=='dark';assert p.DEFAULTS['language']=='fr';assert p.DEFAULT_SHORTCUTS['help']=='F1'

def test_default_overlay_opacity_is_75_percent():
    import s3mapgen.preferences as p
    assert p.DEFAULTS['overlay_alpha']==75
