"""Canonical keyboard-shortcut handling shared by settings and Tk bindings."""

from __future__ import annotations


DEFAULT_SHORTCUTS = {
    "generate": "Ctrl+G",
    "generate_batch": "Ctrl+Shift+G",
    "import": "Ctrl+O",
    "export": "Ctrl+E",
    "save_preview": "Ctrl+P",
    "manage_history": "Ctrl+H",
    "reset_view": "Ctrl+R",
    "copy_seed": "Ctrl+Shift+C",
    "toggle_ab": "Ctrl+B",
    "clear_compare": "",
    "toggle_theme": "Ctrl+Shift+T",
    "help": "F1",
}

_MODIFIER_ALIASES = {
    "ctrl": "Ctrl",
    "control": "Ctrl",
    "strg": "Ctrl",
    "shift": "Shift",
    "maj": "Shift",
    "umschalt": "Shift",
    "mayús": "Shift",
    "mayus": "Shift",
    "alt": "Alt",
    "option": "Alt",
}
_MODIFIER_ORDER = ("Ctrl", "Alt", "Shift")
_MODIFIER_KEYSYMS = {
    "Control_L", "Control_R", "Shift_L", "Shift_R", "Alt_L", "Alt_R",
    "Meta_L", "Meta_R", "Super_L", "Super_R", "Caps_Lock", "Num_Lock",
}
_SPECIAL_KEYS = {
    "space": "Space",
    "return": "Enter",
    "enter": "Enter",
    "tab": "Tab",
    "backspace": "Backspace",
    "delete": "Delete",
    "insert": "Insert",
    "home": "Home",
    "end": "End",
    "left": "Left",
    "right": "Right",
    "up": "Up",
    "down": "Down",
    "prior": "PageUp",
    "pageup": "PageUp",
    "next": "PageDown",
    "pagedown": "PageDown",
    "comma": ",",
    "period": ".",
    "minus": "-",
    "equal": "=",
    "plus": "Plus",
    "semicolon": ";",
    "colon": ":",
    "slash": "/",
    "backslash": "\\",
    "bracketleft": "[",
    "bracketright": "]",
    "ampersand": "&",
    "quotedbl": '"',
    "apostrophe": "'",
}
_DISPLAY_TO_TK = {
    "Space": "space", "Enter": "Return", "Tab": "Tab",
    "Backspace": "BackSpace", "Delete": "Delete", "Insert": "Insert",
    "Home": "Home", "End": "End", "Left": "Left", "Right": "Right",
    "Up": "Up", "Down": "Down", "PageUp": "Prior", "PageDown": "Next",
    ",": "comma", ".": "period", "-": "minus", "=": "equal",
    "Plus": "plus", ";": "semicolon", ":": "colon", "/": "slash",
    "\\": "backslash", "[": "bracketleft", "]": "bracketright",
    "&": "ampersand", '"': "quotedbl", "'": "apostrophe",
}


def _canonical_key(value: str) -> str:
    key = value.strip()
    if not key:
        raise ValueError("missing key")
    lower = key.casefold()
    if lower in _SPECIAL_KEYS:
        return _SPECIAL_KEYS[lower]
    for display in _DISPLAY_TO_TK:
        if key == display or lower == display.casefold():
            return display
    if lower.startswith("f") and lower[1:].isdigit() and 1 <= int(lower[1:]) <= 24:
        return lower.upper()
    if len(key) == 1 and key.isprintable():
        return key.upper() if key.isalpha() else key
    raise ValueError(f"unsupported key: {value}")


def canonicalize_shortcut(value: str | None) -> str:
    """Return a stable display form; an empty string means disabled."""
    if value is None or not str(value).strip():
        return ""
    raw_parts = [part.strip() for part in str(value).split("+")]
    if any(not part for part in raw_parts):
        raise ValueError("empty shortcut component")
    modifiers: set[str] = set()
    keys: list[str] = []
    for part in raw_parts:
        modifier = _MODIFIER_ALIASES.get(part.casefold())
        if modifier:
            modifiers.add(modifier)
        else:
            keys.append(part)
    if len(keys) != 1:
        raise ValueError("exactly one non-modifier key is required")
    key = _canonical_key(keys[0])
    return "+".join([*(name for name in _MODIFIER_ORDER if name in modifiers), key])


def shortcut_to_tk(value: str | None) -> str | None:
    """Convert a canonical shortcut to a Tk event sequence."""
    canonical = canonicalize_shortcut(value)
    if not canonical:
        return None
    parts = canonical.split("+")
    key = parts[-1]
    modifiers = parts[:-1]
    tk_modifiers = [{"Ctrl": "Control", "Alt": "Alt", "Shift": "Shift"}[m] for m in modifiers]
    if len(key) == 1 and key.isalpha():
        tk_key = key.upper() if "Shift" in modifiers else key.lower()
    else:
        tk_key = _DISPLAY_TO_TK.get(key, key)
    return "<" + "-".join([*tk_modifiers, tk_key]) + ">"


def shortcut_from_event(keysym: str, state: int, pressed_modifiers=None) -> str | None:
    """Build a canonical shortcut from one Tk key event.

    Modifier-only events return ``None`` so capture can remain active.  The
    masks cover the ordinary Tk modifiers plus the Windows extended Alt bit.
    """
    if keysym in _MODIFIER_KEYSYMS:
        return None
    if pressed_modifiers is None:
        # Only the portable Tk masks are safe here.  Extended Windows state
        # bits are platform/build dependent and produced phantom Alt captures
        # on a real Windows/AZERTY validation machine.
        modifiers=[]
        if state & 0x0004:modifiers.append("Ctrl")
        if state & 0x0008:modifiers.append("Alt")
        if state & 0x0001:modifiers.append("Shift")
    else:
        requested={str(value) for value in pressed_modifiers}
        modifiers=[name for name in _MODIFIER_ORDER if name in requested]
    key = _SPECIAL_KEYS.get(keysym.casefold(), keysym)
    return canonicalize_shortcut("+".join([*modifiers, key]))
