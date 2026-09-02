"""Native Continental v1 archetype.

The original game does not expose a second, independent continent mask in the
generation entry point. Its primary terrain routine builds the relief and the
playable macro-form itself. This object carries that explicit context without
inventing a modern pre-mask.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ...map_data.model import MapState

from ..core.request import NATIVE_PLAYER_LIMITS


@dataclass(frozen=True, slots=True)
class ContinentalContext:
    """Inputs consumed by the native Legacy terrain pipeline."""

    side: int
    players: int
    native_mode: int = 0
    party_profile: int = 0

    @property
    def key(self) -> str:
        return "continental"


class ContinentalV1:
    """The v1 Continental archetype used by the native Legacy generator."""

    key = "continental"
    label = "Continental"

    def prepare(self, side: int, players: int) -> ContinentalContext:
        side = int(side)
        players = int(players)
        if side not in NATIVE_PLAYER_LIMITS:
            supported = ", ".join(map(str, NATIVE_PLAYER_LIMITS))
            raise ValueError(f"Continental native sides are: {supported}")
        maximum = NATIVE_PLAYER_LIMITS[side]
        if not 2 <= players <= maximum:
            raise ValueError(f"players must be in 2..{maximum} for side {side}")
        return ContinentalContext(side=side, players=players)


def assemble_continental_state(
    side: int,
    height: np.ndarray,
    terrain: np.ndarray,
    metadata: dict | None = None,
) -> MapState:
    """Assemble the neutral map state owned by the Continental archetype.

    Relief, terrain families, rivers and global content remain generator
    responsibilities.  The archetype only validates the field shapes and
    creates the six-channel state consumed by EDM/MAP and the viewer.
    """

    side = int(side)
    height = np.asarray(height, dtype=np.uint8)
    terrain = np.asarray(terrain, dtype=np.uint8)
    expected = (side, side)
    if height.shape != expected or terrain.shape != expected:
        raise ValueError(
            f"Continental fields must be {side}×{side}: "
            f"height={height.shape}, terrain={terrain.shape}"
        )

    state = MapState.empty(side)
    state.height[:] = height
    state.terrain[:] = terrain
    state.objects[:] = 0
    state.resources[:] = 0
    state.accessibility[:] = 0
    state.claim[:] = 255
    if metadata:
        state.metadata.update(metadata)
    state.metadata.setdefault("archetype_key", "continental")
    state.metadata.setdefault("archetype", "Continental")
    return state


__all__ = ("ContinentalContext", "ContinentalV1", "assemble_continental_state")
