import importlib


def test_preferences_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv('APPDATA', str(tmp_path))
    import s3mapgen.preferences as p
    importlib.reload(p)
    p.save_settings({'theme':'light','overlay_alpha':42,'projection':'parallelogram','wheel_zoom':1.12})
    got=p.load_settings()
    assert got['theme']=='light'
    assert got['overlay_alpha']==42
    assert got['projection']=='parallelogram'
    assert abs(got['wheel_zoom']-1.12)<1e-9


def test_defaults_include_dark_mode():
    import s3mapgen.preferences as p
    assert p.DEFAULTS['theme']=='dark'
