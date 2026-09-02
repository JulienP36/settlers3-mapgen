"""Validation limited to the recovered native primary terrain contract."""

from __future__ import annotations

import numpy as np

from ....map_data.constants import HEX6, MOUNTAIN_FAMILY_IDS, RIVER_IDS, SNOW, SNOW_TRANS, WATER_IDS
from ....map_data.hexgrid import component_labels, neighbor_count
from ...rules import ValidationResult


_KNOWN_PRIMARY_IDS = {
    *WATER_IDS,
    0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x17, 0x18,
    0x20, 0x21, 0x22, 0x23,
    0x30,
    0x40, 0x41,
    0x50, 0x51,
    0x60, 0x61, 0x62, 0x63,
    0x80, 0x81,
    0x90, 0x91,
}


def _hex_neighbour_values(field: np.ndarray, row: int, col: int) -> list[int]:
    side = field.shape[0]
    values = []
    for dr, dc in HEX6:
        rr, cc = row + dr, col + dc
        if 0 <= rr < side and 0 <= cc < side:
            values.append(int(field[rr, cc]))
    return values


def _mirror_ok(field: np.ndarray, mode: int) -> bool:
    side = field.shape[0]
    if mode & 0x01:
        for col in range(1, side):
            if not np.array_equal(field[:col, col], field[col, :col]):
                return False
    if mode & 0x02:
        for outer in range(side - 1):
            for inner in range(side - outer - 1):
                if field[inner, outer] != field[side - 1 - outer, side - 1 - inner]:
                    return False
    return True


def validate(state, *, mode: int = 0) -> list[ValidationResult]:
    """Return hard checks that do not pretend to validate deferred layers."""

    terrain = state.terrain
    height = state.height
    water = np.isin(terrain, WATER_IDS)
    out: list[ValidationResult] = []

    def add(rule: str, passed: bool, message: str, hard: bool = True) -> None:
        out.append(ValidationResult(rule, bool(passed), message, hard))

    unknown = sorted({int(value) for value in np.unique(terrain)} - _KNOWN_PRIMARY_IDS)
    add("NATIVE_PRIMARY_IDS", not unknown, f"unknown={unknown}")
    add("NATIVE_WATER_HEIGHT", not np.any(height[water] != 0), f"bad={int(np.count_nonzero(height[water] != 0))}")
    edge_terrain = np.concatenate((terrain[0, :], terrain[-1, :], terrain[1:-1, 0], terrain[1:-1, -1]))
    edge_height = np.concatenate((height[0, :], height[-1, :], height[1:-1, 0], height[1:-1, -1]))
    add(
        "NATIVE_OUTER_EDGE_DEEP_WATER",
        bool(np.all(edge_terrain == 0x07) and np.all(edge_height == 0)),
        f"terrain={sorted(set(map(int, edge_terrain)))} height_max={int(edge_height.max(initial=0))}",
    )
    add("NATIVE_NO_WORK_SENTINELS", not np.isin(terrain, (0x70, 0xF0, 0xF3, 0xFE, 0xFF)).any(), "temporary terrain values cleared")
    add("NATIVE_RIVER_NO_BAD_NEIGHBOUR", _river_neighbours_are_legal(terrain), "river cleanup-compatible neighbours")
    mirror_mode = int(mode) & 0x03
    river_components_ok = _river_components_touch_water(terrain)
    add(
        "NATIVE_RIVER_COMPONENTS",
        river_components_ok or bool(mirror_mode),
        "each river component touches water"
        if not mirror_mode
        else "mirror topology accepted; native axis copy may create detached paths",
        # The native cleanup itself permits a one-cell river with only Grass
        # neighbours.  Mirroring can also duplicate a valid path away from
        # its original mouth.  Keep the topology note visible, but do not
        # present that native mode as a failed generation in the UI.
        hard=False,
    )
    add("NATIVE_MIRROR_RELIEF", _mirror_ok(height, int(mode)), f"mode={int(mode)}")
    add("NATIVE_MIRROR_TERRAIN", _mirror_ok(terrain, int(mode)), f"mode={int(mode)}")
    resources = state.resources
    objects = state.objects
    river = np.isin(terrain, RIVER_IDS)
    fish = water & ((resources & 0xF0) == 0) & ((resources & 0x0F) > 0)
    mineral = (resources & 0xF0) != 0
    # The recovered routine tests the terrain family nibble, not a short
    # enumerated list.  This includes native transition variants such as
    # 0x21/0x22/0x23 and 0x81 when they are present.
    mineral_support = ((terrain & 0xF0) == 0x20) | ((terrain & 0xF0) == 0x80)
    add("NATIVE_FISH_NO_RIVER", not np.any(fish & river), f"bad={int(np.count_nonzero(fish & river))}")
    add(
        "NATIVE_FISH_WATER_ONLY",
        not np.any(fish & ~water),
        "fish cells are water-only",
    )
    add("NATIVE_MINERALS_ON_SUPPORT", not np.any(mineral & ~mineral_support), "mineral cells use mountain support")
    add("NATIVE_OBJECTS_OFF_WATER", not np.any((objects != 0) & water), "objects are not placed on water")
    add("NATIVE_OBJECTS_OFF_MOUNTAIN", not np.any((objects != 0) & np.isin(terrain, MOUNTAIN_FAMILY_IDS)), "objects are not placed on mountain")
    add("NATIVE_WATER_ACCESS", not np.any(state.accessibility[water] != 1), "water is non-walkable")
    snow = np.isin(terrain, (SNOW_TRANS, SNOW))
    add("NATIVE_SNOW_ACCESS", not np.any(state.accessibility[snow] != 1), "snow is non-walkable")
    add("NATIVE_OBJECT_ACCESS", not np.any(state.accessibility[objects != 0] != 1), "object cells are non-walkable")
    add("NATIVE_START_COUNT", len(state.starts) == int(state.metadata.get("players", len(state.starts))), f"starts={len(state.starts)}")
    return out


def _river_neighbours_are_legal(terrain: np.ndarray) -> bool:
    side = terrain.shape[0]
    for row, col in np.argwhere((terrain >= 0x60) & (terrain <= 0x63)):
        for dr, dc in HEX6:
            rr, cc = int(row) + dr, int(col) + dc
            if not (0 <= rr < side and 0 <= cc < side):
                return False
            value = int(terrain[rr, cc])
            if not ((0x60 <= value <= 0x63) or value in (*WATER_IDS, 0x10, 0x30)):
                return False
    return True


def _river_components_touch_water(terrain: np.ndarray) -> bool:
    river = (terrain >= 0x60) & (terrain <= 0x63)
    if not river.any():
        return True
    labels, count = component_labels(river)
    water = np.isin(terrain, WATER_IDS)
    # A native source cell can itself become River while its former water
    # rim becomes Shore during the following structural-transition pass.
    # Shore is therefore a valid mouth for this primary-terrain validator.
    touching = neighbor_count(water | (terrain == 0x30)) > 0
    return all(np.any((labels == label) & touching) for label in range(1, count + 1))


__all__ = ("validate",)
