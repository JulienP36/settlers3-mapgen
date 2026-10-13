"""Departure routing; geometry and validity are shared by both engines."""
from ...start_placement import place_starts as _place_starts

def place_starts(state, players, rng, *, technical_clear=14, island_labels=None, start_algorithm='auto'):
    reservation = _place_starts(state, players, rng, technical_clear=technical_clear,
                                island_labels=island_labels, start_algorithm=start_algorithm)
    return reservation

__all__ = ('place_starts',)
