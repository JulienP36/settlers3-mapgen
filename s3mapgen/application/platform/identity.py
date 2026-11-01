"""Stable Windows shell identity for source and frozen launches."""
from __future__ import annotations

import sys


APP_USER_MODEL_ID = 'JulienP36.Settlers3MapGen'


def set_windows_app_identity() -> bool:
    """Set taskbar grouping before Tk creates the first native window."""
    if sys.platform != 'win32':
        return False
    try:
        import ctypes
        from ctypes import wintypes

        setter = ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID
        setter.argtypes = (wintypes.LPCWSTR,)
        setter.restype = ctypes.c_long
        return setter(APP_USER_MODEL_ID) >= 0
    except Exception:
        # Shell integration must not prevent application startup.
        return False
