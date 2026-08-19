import importlib


def test_preferences_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    import s3mapgen.preferences as p
    importlib.reload(p)
    p.save_settings({
        'theme':'light','overlay_alpha':42,'projection':'parallelogram',
        'wheel_zoom':1.12,'language':'en',
        'shortcuts':{**p.DEFAULT_SHORTCUTS,'generate':'Ctrl+Alt+G'},
    })
    got=p.load_settings()
    assert got['theme']=='light'
    assert got['overlay_alpha']==42
    assert got['projection']=='parallelogram'
    assert abs(got['wheel_zoom']-1.12)<1e-9
    assert got['language']=='en'
    assert got['shortcuts']['generate']=='Ctrl+Alt+G'
    assert got['shortcuts']['help']=='F1'


def test_defaults_include_dark_mode_french_and_shortcuts():
    import s3mapgen.preferences as p
    assert p.DEFAULTS['theme']=='dark'
    assert p.DEFAULTS['language']=='fr'
    assert p.DEFAULT_SHORTCUTS['toggle_ab']=='Ctrl+B'
    assert p.DEFAULTS['shortcuts']['help']=='F1'


def test_partial_shortcut_settings_keep_other_defaults(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    import s3mapgen.preferences as p
    importlib.reload(p)
    p.save_settings({'shortcuts':{'generate':'Alt+G'}})
    got=p.load_settings()
    assert got['shortcuts']['generate']=='Alt+G'
    assert got['shortcuts']['import']==p.DEFAULT_SHORTCUTS['import']
