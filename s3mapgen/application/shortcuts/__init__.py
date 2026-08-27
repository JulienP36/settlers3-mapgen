"""Keyboard shortcut normalization, configuration UI and Help window."""

from .bindings import DEFAULT_SHORTCUTS, canonicalize_shortcut
from .controller import ShortcutController

__all__ = ["DEFAULT_SHORTCUTS", "ShortcutController", "canonicalize_shortcut"]
