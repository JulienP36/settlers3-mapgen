"""Give the disposable Windows CI runner enough desktop space for real Tk tests.

Uses supported display modes; changes only the current session, not the registry.
API/ABI: https://learn.microsoft.com/windows/win32/api/wingdi/ns-wingdi-devmodew
https://learn.microsoft.com/windows/win32/api/winuser/nf-winuser-changedisplaysettingsw
"""
from __future__ import annotations

import ctypes
import os
from ctypes import wintypes


class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ('dmDeviceName', wintypes.WCHAR * 32),
        ('dmSpecVersion', wintypes.WORD), ('dmDriverVersion', wintypes.WORD),
        ('dmSize', wintypes.WORD), ('dmDriverExtra', wintypes.WORD),
        ('dmFields', wintypes.DWORD), ('display_union', wintypes.BYTE * 16),
        ('dmColor', ctypes.c_short), ('dmDuplex', ctypes.c_short),
        ('dmYResolution', ctypes.c_short), ('dmTTOption', ctypes.c_short),
        ('dmCollate', ctypes.c_short), ('dmFormName', wintypes.WCHAR * 32),
        ('dmLogPixels', wintypes.WORD), ('dmBitsPerPel', wintypes.DWORD),
        ('dmPelsWidth', wintypes.DWORD), ('dmPelsHeight', wintypes.DWORD),
        ('dmDisplayFlags', wintypes.DWORD), ('dmDisplayFrequency', wintypes.DWORD),
        ('dmICMMethod', wintypes.DWORD), ('dmICMIntent', wintypes.DWORD),
        ('dmMediaType', wintypes.DWORD), ('dmDitherType', wintypes.DWORD),
        ('dmReserved1', wintypes.DWORD), ('dmReserved2', wintypes.DWORD),
        ('dmPanningWidth', wintypes.DWORD), ('dmPanningHeight', wintypes.DWORD),
    ]


def main() -> None:
    if os.name != 'nt':
        raise RuntimeError('This desktop preparation is only for Windows CI.')
    assert ctypes.sizeof(DEVMODEW) == 220
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    enumerate_mode = user32.EnumDisplaySettingsW
    enumerate_mode.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DEVMODEW)]
    enumerate_mode.restype = wintypes.BOOL
    change_mode = user32.ChangeDisplaySettingsW
    change_mode.argtypes = [ctypes.POINTER(DEVMODEW), wintypes.DWORD]
    change_mode.restype = wintypes.LONG
    current = DEVMODEW()
    current.dmSize = ctypes.sizeof(current)
    if not enumerate_mode(None, 0xFFFFFFFF, ctypes.byref(current)):
        raise ctypes.WinError(ctypes.get_last_error())
    print(f'Current display: {current.dmPelsWidth}x{current.dmPelsHeight}', flush=True)
    if current.dmPelsWidth < 1920 or current.dmPelsHeight < 1080:
        modes = []
        index = 0
        while True:
            mode = DEVMODEW()
            mode.dmSize = ctypes.sizeof(mode)
            if not enumerate_mode(None, index, ctypes.byref(mode)):
                break
            if mode.dmPelsWidth >= 1920 and mode.dmPelsHeight >= 1080:
                modes.append(mode)
            index += 1
        if not modes:
            raise RuntimeError('Runner display has no supported mode of at least 1920x1080.')
        selected = min(modes, key=lambda m: (
            m.dmPelsWidth * m.dmPelsHeight, -m.dmBitsPerPel,
            abs(m.dmDisplayFrequency - current.dmDisplayFrequency),
        ))
        # The enumerated mode carries supported depth/frequency as well as size.
        result = change_mode(ctypes.byref(selected), 0)
        if result != 0:
            raise RuntimeError(f'ChangeDisplaySettingsW failed: {result}')
        print(f'Selected display: {selected.dmPelsWidth}x{selected.dmPelsHeight}', flush=True)
    import tkinter as tk
    root = tk.Tk()
    try:
        root.withdraw()
        width, height = root.winfo_screenwidth(), root.winfo_screenheight()
        print(f'Tk desktop: {width}x{height}', flush=True)
        if width < 1920 or height < 1080:
            raise RuntimeError('Tk cannot see the requested desktop; real UI tests cannot run reliably.')
    finally:
        root.destroy()


if __name__ == '__main__':
    main()
