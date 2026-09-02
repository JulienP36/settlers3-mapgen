"""Compatibility names for the independent Upgraded terrain core."""

from __future__ import annotations

from dataclasses import dataclass

from ....map_data.constants import START_FOOTPRINT
from .native_terrain import (
    HEX6,
    NativeRng16,
    NativeTerrainGrid,
    NativeTerrainResult,
    generate_primary_terrain,
)


NativePRNG16 = NativeRng16
NATIVE_NORMAL_START_FOOTPRINT = START_FOOTPRINT


@dataclass(frozen=True, slots=True)
class NativeHexOffset:
    dx: int
    dy: int
    ring: int
    orientation: int


def native_build_hex_offset_bank() -> tuple[NativeHexOffset, ...]:
    """Return the diagnostic six-neighbour bank used by the terrain copy."""

    return tuple(NativeHexOffset(int(dx), int(dy), 1, index) for index, (dx, dy) in enumerate(HEX6))


__all__ = (
    "NativePRNG16",
    "NativeRng16",
    "NativeTerrainGrid",
    "NativeTerrainResult",
    "NativeHexOffset",
    "NATIVE_NORMAL_START_FOOTPRINT",
    "generate_primary_terrain",
    "native_build_hex_offset_bank",
)
