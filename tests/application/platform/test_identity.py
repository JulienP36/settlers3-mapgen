from types import SimpleNamespace

from s3mapgen.application.platform import identity


def test_identity_is_a_safe_noop_outside_windows(monkeypatch):
    monkeypatch.setattr(identity.sys, 'platform', 'linux')
    assert identity.set_windows_app_identity() is False


def test_windows_shell_receives_a_stable_identity(monkeypatch):
    import ctypes

    calls = []
    def setter(value):
        calls.append(value)
        return 0

    monkeypatch.setattr(identity.sys, 'platform', 'win32')
    monkeypatch.setattr(ctypes, 'windll', SimpleNamespace(shell32=SimpleNamespace(
        SetCurrentProcessExplicitAppUserModelID=setter)), raising=False)
    assert identity.set_windows_app_identity() is True
    assert calls == ['JulienP36.Settlers3MapGen']
    assert 'DEV_' not in calls[0]


def test_unavailable_windows_shell_does_not_block_startup(monkeypatch):
    import ctypes

    def unavailable(value):
        raise OSError('Shell integration unavailable')

    monkeypatch.setattr(identity.sys, 'platform', 'win32')
    monkeypatch.setattr(ctypes, 'windll', SimpleNamespace(shell32=SimpleNamespace(
        SetCurrentProcessExplicitAppUserModelID=unavailable)), raising=False)
    assert identity.set_windows_app_identity() is False
