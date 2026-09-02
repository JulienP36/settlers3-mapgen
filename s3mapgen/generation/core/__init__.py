"""Primitives neutres utilisées par les générateurs procéduraux.

Ce paquet ne connaît ni archetype, ni mode de jeu, ni quota de contenu.
"""

from .request import (
    EDITOR_EXTENDED_SIDES,
    NATIVE_GAME_MAX_SIDE,
    NATIVE_GAME_MIN_SIDE,
    GenerationRequest,
    NATIVE_PLAYER_LIMITS,
    native_size_warning_kind,
)
from .seed_streams import SeedStreams
from .noise import fractal_value_field, warped_fractal_field

__all__ = (
    "GenerationRequest", "NATIVE_PLAYER_LIMITS", "SeedStreams",
    "NATIVE_GAME_MIN_SIDE", "NATIVE_GAME_MAX_SIDE", "EDITOR_EXTENDED_SIDES",
    "native_size_warning_kind",
    "fractal_value_field", "warped_fractal_field",
)
