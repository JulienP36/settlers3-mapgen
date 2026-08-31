"""Primitives neutres utilisées par les générateurs procéduraux.

Ce paquet ne connaît ni archetype, ni mode de jeu, ni quota de contenu.
"""

from .request import GenerationRequest, NATIVE_PLAYER_LIMITS
from .seed_streams import SeedStreams
from .noise import fractal_value_field, warped_fractal_field

__all__ = (
    "GenerationRequest", "NATIVE_PLAYER_LIMITS", "SeedStreams",
    "fractal_value_field", "warped_fractal_field",
)
