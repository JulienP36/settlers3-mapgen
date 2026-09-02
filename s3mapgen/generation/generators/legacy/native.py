"""Compatibility names for the modular native Legacy engine.

The implementation now lives in ``native_terrain``, ``native_content`` and
``native_pipeline``.  This small module keeps the diagnostic/table imports
used by older callers stable while making the separation explicit.
"""

from __future__ import annotations

from dataclasses import dataclass

from ....map_data.constants import START_FOOTPRINT
from .native_content import build_native_pattern_bank
from .native_terrain import (
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
    """Return the native placement bank in the historical diagnostic shape."""

    records = build_native_pattern_bank()
    return tuple(
        NativeHexOffset(
            int(dx),
            int(dy),
            (index - 1) // 6 + 1 if index else 0,
            (index - 1) % 6 if index else 0,
        )
        for index, (dx, dy) in enumerate(records)
    )


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
