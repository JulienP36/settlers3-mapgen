"""Best-effort native Windows title-bar theming.

The application keeps the standard operating-system frame.  This module only
asks Desktop Window Manager (DWM) to recolor that frame, and becomes a no-op on
unsupported systems.  No polling or custom window chrome is involved.
"""

from __future__ import annotations

import sys
from typing import Mapping


DWMWA_USE_IMMERSIVE_DARK_MODE = 20
DWMWA_USE_IMMERSIVE_DARK_MODE_OLD = 19
DWMWA_BORDER_COLOR = 34
DWMWA_CAPTION_COLOR = 35
DWMWA_TEXT_COLOR = 36
GA_ROOT = 2


def _hex_to_colorref(color: str) -> int:
    """Convert ``#RRGGBB`` to the COLORREF byte order used by Win32."""
    value = color.removeprefix("#")
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB, got {color!r}")
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    return red | (green << 8) | (blue << 16)


def _apply_client_separator(window, color: str) -> None:
    """Overlay a one-pixel line at the top of the Tk client area.

    DWM's border color controls the outside frame, not a guaranteed line below
    the native caption. This overlay supplies that boundary without changing
    the geometry manager or the window layout.
    """
    import tkinter as tk

    separator = getattr(window, "_mapgen_titlebar_separator", None)
    if separator is None or not bool(separator.winfo_exists()):
        separator = tk.Frame(window, borderwidth=0, highlightthickness=0)
        window._mapgen_titlebar_separator = separator
    separator.configure(background=color)
    separator.place(x=0, y=0, relwidth=1, height=1)
    separator.lift()


def apply_native_titlebar(window, palette: Mapping[str, object]) -> bool:
    """Apply *palette* to one decorated Tk window when DWM is available.

    Returns ``True`` when at least one DWM attribute was accepted.  Every
    failure is intentionally local: title-bar theming must never prevent a
    window from opening or alter application behavior.
    """
    if sys.platform != "win32":
        return False

    try:
        # Borderless previews deliberately remain fully controlled by Tk.
        if bool(window.overrideredirect()):
            return False

        import ctypes
        from ctypes import wintypes

        window.update_idletasks()
        widget_handle = wintypes.HWND(int(window.winfo_id()))
        user32 = ctypes.windll.user32
        dwmapi = ctypes.windll.dwmapi

        user32.GetAncestor.argtypes = (wintypes.HWND, wintypes.UINT)
        user32.GetAncestor.restype = wintypes.HWND
        dwmapi.DwmSetWindowAttribute.argtypes = (
            wintypes.HWND,
            wintypes.DWORD,
            wintypes.LPCVOID,
            wintypes.DWORD,
        )
        dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long

        native_handle = user32.GetAncestor(widget_handle, GA_ROOT) or widget_handle
        # Caption mode and colors are semantic roles: the light and dark
        # application themes can therefore keep distinct native identities.
        dark_value = wintypes.BOOL(bool(palette.get("titlebar_dark", True)))
        separator_color = palette.get("titlebar_separator")
        if isinstance(separator_color, str) and separator_color:
            _apply_client_separator(window, separator_color)

        def set_attribute(attribute: int, value) -> bool:
            result = dwmapi.DwmSetWindowAttribute(
                native_handle,
                attribute,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
            return result >= 0

        changed = set_attribute(DWMWA_USE_IMMERSIVE_DARK_MODE, dark_value)
        if not changed:
            # Windows 10 builds predating the public attribute number used 19.
            changed = set_attribute(DWMWA_USE_IMMERSIVE_DARK_MODE_OLD, dark_value)

        # Windows 11 accepts explicit caption, text and border colors.  Older
        # versions simply reject these calls and retain their native palette.
        for attribute, role in (
            (DWMWA_CAPTION_COLOR, "titlebar"),
            (DWMWA_TEXT_COLOR, "titlebar_text"),
            (DWMWA_BORDER_COLOR, "titlebar_border"),
        ):
            color = palette.get(role)
            if color:
                changed = set_attribute(attribute, wintypes.DWORD(_hex_to_colorref(color))) or changed
        return changed
    except Exception:
        return False
