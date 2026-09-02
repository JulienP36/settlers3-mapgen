"""Static content routines recovered from the Settlers III generator.

The executable keeps the content pass in the same native PRNG stream as the
terrain pass.  This module mirrors the small routines around ``0x51B010``
(fixed objects), ``0x51B1A0`` (object ranges), ``0x51AD40`` (mountain
resources) and the direct fish loop.  It intentionally does not implement
the player-start records: those belong to the future SAV writer and are not
part of the global MAP/EDM content pass.

The functions operate on the temporary :class:`NativeTerrainGrid` without
importing ``native_terrain`` at runtime.  Keeping the dependency one-way is
important because the terrain generator calls this module immediately before
its native mirror copies.
"""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:  # pragma: no cover - imports used only by type checkers
    from .native_terrain import NativeRng16, NativeTerrainGrid


# This is the executable's memory-neighbour order.  It differs from the
# renderer's clockwise order and is therefore kept local and explicit.
NATIVE_HEX6 = ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))

_PATTERN_CANDIDATES = 5000
_PATTERN_RECORDS = 3333


@lru_cache(maxsize=1)
def _pattern_bank_records() -> tuple[tuple[int, int], ...]:
    """Build the 19,999-record native placement pattern bank.

    The initializer first enumerates the triangular ``(u, v)`` domain, then
    repeatedly takes its smallest score.  Python's stable sort is equivalent
    to the executable's strict ``<`` minimum scan when equal scores occur.
    """

    candidates: list[tuple[int, int]] = []
    u = 1
    while len(candidates) < _PATTERN_CANDIDATES:
        for v in range(u):
            candidates.append((u, v))
            if len(candidates) == _PATTERN_CANDIDATES:
                break
        u += 1

    scores = [2500 * (2 * uu - vv) ** 2 + 7569 * vv ** 2 for uu, vv in candidates]
    selected = sorted(range(len(candidates)), key=scores.__getitem__)[:_PATTERN_RECORDS]

    records: list[tuple[int, int]] = [(0, 0)]
    for index in selected:
        uu, vv = candidates[index]
        records.extend(
            (
                (uu, vv),
                (uu - vv, uu),
                (-vv, uu - vv),
                (-uu, -vv),
                (vv - uu, -uu),
                (vv, vv - uu),
            )
        )
    return tuple(records)


@lru_cache(maxsize=1)
def _pattern_bank_array() -> np.ndarray:
    bank = np.asarray(_pattern_bank_records(), dtype=np.int16)
    bank.setflags(write=False)
    return bank


def build_native_pattern_bank() -> np.ndarray:
    """Return the read-only native pattern bank for diagnostics/tests."""

    return _pattern_bank_array()


def _random_scaled(rng: NativeRng16, span: int) -> int:
    return (rng.next() * int(span)) >> 16


def _inside(side: int, row: int, col: int) -> bool:
    return 0 <= int(row) < int(side) and 0 <= int(col) < int(side)


def _interior(side: int, row: int, col: int) -> bool:
    return 1 <= int(row) < int(side) - 1 and 1 <= int(col) < int(side) - 1


def _terrain_at(terrain: np.ndarray, row: int, col: int) -> int:
    if _inside(terrain.shape[0], row, col):
        return int(terrain[row, col])
    # The native object backing store is zero outside the active square.  All
    # object source terrains are non-zero, so this also makes edge support
    # checks fail safely without Python's negative-index wrapping.
    return 0


def _source_neighbourhood(terrain: np.ndarray, row: int, col: int, source: int) -> bool:
    side = terrain.shape[0]
    if _terrain_at(terrain, row, col) != int(source):
        return False
    for dr, dc in NATIVE_HEX6:
        if not _inside(side, row + dr, col + dc):
            return False
        if int(terrain[row + dr, col + dc]) != int(source):
            return False
    return True


def _collision_free(
    objects: np.ndarray,
    object_flags: np.ndarray,
    barrier: np.ndarray,
    row: int,
    col: int,
    count: int,
    bank: tuple[tuple[int, int], ...],
) -> bool:
    side = objects.shape[0]
    for dr, dc in bank[: int(count)]:
        rr, cc = int(row) + dr, int(col) + dc
        # Reads outside the active map hit the zeroed native backing store.
        # There is consequently no collision there; range candidates are
        # already bounds-checked at their origin by the executable.
        if not _inside(side, rr, cc):
            continue
        if (
            int(objects[rr, cc]) != 0
            or (int(object_flags[rr, cc]) & 0x01) != 0
            or bool(barrier[rr, cc])
        ):
            return False
    return True


def _write_flags(
    object_flags: np.ndarray,
    row: int,
    col: int,
    flag_mode: int,
) -> None:
    side = object_flags.shape[0]
    if int(flag_mode) == 1:
        object_flags[row, col] |= 0x01
    elif int(flag_mode) == 2:
        if _inside(side, row, col):
            object_flags[row, col] |= 0x01
        for dr, dc in NATIVE_HEX6:
            rr, cc = row + dr, col + dc
            if _inside(side, rr, cc):
                object_flags[rr, cc] |= 0x01


def _placement_count(flag_mode: int, pattern_arg: int) -> int:
    return 19 if int(flag_mode) + int(pattern_arg) == 3 else 7


def _place_fixed(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    barrier: np.ndarray,
    source: int,
    object_id: int,
    density: int,
    flag_mode: int,
    pattern_arg: int,
    bank: tuple[tuple[int, int], ...],
) -> tuple[int, int]:
    """Run one recovered fixed-object call and return attempts/accepts."""

    blocks = grid.side // 64
    total = blocks * blocks * int(density)
    if (total & ~0x01) == 0:
        return 0, 0

    attempts = total // 2
    count = _placement_count(flag_mode, pattern_arg)
    accepted = 0
    terrain, objects, object_flags = grid.terrain, grid.objects, grid.object_flags
    for _ in range(attempts):
        row = 1 + _random_scaled(rng, grid.side - 2)
        col = 1 + _random_scaled(rng, grid.side - 2)
        if not _source_neighbourhood(terrain, row, col, source):
            continue
        if not _collision_free(objects, object_flags, barrier, row, col, count, bank):
            continue
        objects[row, col] = int(object_id) & 0xFF
        _write_flags(object_flags, row, col, flag_mode)
        accepted += 1
    return attempts, accepted


def _place_range(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    barrier: np.ndarray,
    source: int,
    low_id: int,
    high_id: int,
    density: int,
    flag_mode: int,
    pattern_arg: int,
    bank: tuple[tuple[int, int], ...],
) -> tuple[int, int]:
    """Run one recovered ranged-object call and return attempts/accepts."""

    blocks = grid.side // 64
    total = blocks * blocks * int(density)
    if (total & ~0x0F) == 0:
        return 0, 0

    groups = total // 16
    count = _placement_count(flag_mode, pattern_arg)
    attempts = 0
    accepted = 0
    terrain, objects, object_flags = grid.terrain, grid.objects, grid.object_flags
    for _ in range(groups):
        base_row = 1 + _random_scaled(rng, grid.side - 2)
        base_col = 1 + _random_scaled(rng, grid.side - 2)
        length = (rng.next() & 0x0F) + 4
        for _ in range(length):
            attempts += 1
            pattern_row, pattern_col = bank[rng.next() & 0x01FF]
            row, col = base_row + pattern_row, base_col + pattern_col
            if not _inside(grid.side, row, col):
                continue
            if not _source_neighbourhood(terrain, row, col, source):
                continue
            if not _collision_free(objects, object_flags, barrier, row, col, count, bank):
                continue
            object_id = int(low_id) + (
                (rng.next() * (int(high_id) - int(low_id) + 1)) >> 16
            )
            objects[row, col] = object_id & 0xFF
            _write_flags(object_flags, row, col, flag_mode)
            accepted += 1
    return attempts, accepted


def _place_mineral_family(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    family: int,
    coefficient: int,
    bank: tuple[tuple[int, int], ...],
) -> tuple[int, int]:
    """Run one ``0x51AD40`` family call and return groups/writes."""

    blocks = grid.side // 64
    total = blocks * blocks * int(coefficient)
    if (total & ~0x07) == 0:
        return 0, 0

    groups = total // 8
    writes = 0
    terrain, resources = grid.terrain, grid.resources
    for _ in range(groups):
        origin_row = _random_scaled(rng, grid.side)
        origin_col = _random_scaled(rng, grid.side)
        pattern_count = (rng.next() & 0x3F) + 0x20
        threshold = (rng.next() & 0x7FFF) + 0x8000
        for pattern_row, pattern_col in bank[:pattern_count]:
            row, col = origin_row + pattern_row, origin_col + pattern_col
            if not _interior(grid.side, row, col):
                continue
            if (int(terrain[row, col]) & 0xF0) not in (0x20, 0x80):
                continue
            if int(resources[row, col]) != 0:
                continue
            if rng.next() >= threshold:
                continue
            resources[row, col] = (int(family) + (rng.next() % 15) + 1) & 0xFF
            writes += 1
    return groups, writes


def _place_fish(grid: NativeTerrainGrid, rng: NativeRng16) -> tuple[int, int]:
    """Run the direct native fish loop: columns outside, rows inside."""

    if grid.side <= 1:
        return 0, 0
    writes = 0
    nonzero = 0
    terrain, resources = grid.terrain, grid.resources
    for outer_col in range(grid.side - 1):
        for inner_row in range(grid.side - 1):
            if (int(terrain[inner_row, outer_col]) & 0xF0) != 0:
                continue
            if rng.next() <= 0x9C40:
                continue
            quantity = rng.next() & 0x0F
            resources[inner_row, outer_col] = quantity
            writes += 1
            nonzero += int(quantity > 0)
    return writes, nonzero


def _mirror_barrier(side: int, mode: int) -> np.ndarray:
    """Reproduce the temporary object-byte sentinels used by mirror modes."""

    barrier = np.zeros((int(side), int(side)), dtype=bool)
    if int(mode) & 0x01:
        for index in range(int(side)):
            barrier[index, index] = True
    if int(mode) & 0x02:
        for index in range(int(side)):
            barrier[index, int(side) - 1 - index] = True
        for index in range(int(side) - 1):
            barrier[index, int(side) - 2 - index] = True
            barrier[index + 1, int(side) - 1 - index] = True
    return barrier


def _expand_fixed_calls() -> tuple[tuple[int, int, int, int, int], ...]:
    calls: list[tuple[int, int, int, int, int]] = []

    def add(source: int, ids, density: int, flag_mode: int, pattern_arg: int) -> None:
        calls.extend(
            (int(source), int(object_id), int(density), int(flag_mode), int(pattern_arg))
            for object_id in ids
        )

    add(0x10, (1,), 1, 2, 1)
    add(0x10, range(2, 13), 1, 0, 0)
    add(0x10, range(13, 21), 1, 2, 0)
    add(0x10, (34,), 1, 2, 1)
    add(0x10, range(21, 29), 1, 0, 0)
    add(0x10, range(35, 43), 1, 0, 0)
    add(0x10, range(50, 62), 1, 0, 0)
    add(0x10, range(68, 78), 1, 1, 2)
    add(0x10, range(80, 82), 9, 1, 2)
    add(0x10, range(115, 127), 1, 2, 1)
    add(0x10, (127,), 1, 0, 0)

    add(0x30, range(29, 31), 5, 2, 0)
    add(0x30, (31,), 5, 0, 0)
    add(0x30, range(32, 34), 5, 2, 0)

    add(0x40, range(43, 45), 3, 1, 2)
    add(0x40, range(45, 48), 6, 1, 1)
    add(0x40, (48,), 6, 0, 0)
    add(0x40, (49,), 3, 0, 0)
    add(0x40, range(78, 80), 1, 1, 2)

    add(0x50, range(62, 68), 150, 0, 0)
    return tuple(calls)


FIXED_OBJECT_CALLS = _expand_fixed_calls()
RANGE_OBJECT_CALLS = (
    (0x10, 68, 69, 11, 1, 2),
    (0x10, 70, 71, 11, 1, 2),
    (0x10, 72, 73, 11, 1, 2),
    (0x10, 74, 75, 11, 1, 2),
    (0x10, 76, 77, 11, 1, 2),
    (0x40, 78, 79, 11, 1, 2),
    (0x10, 80, 81, 11, 1, 2),
    (0x10, 115, 126, 55, 2, 1),
)
MINERAL_CALLS = (
    (0x50, 0x1E),
    (0x40, 0x14),
    (0x30, 0x3C),
    (0x20, 0x64),
    (0x10, 0x12C),
)


def populate_native_content(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    mode: int = 0,
) -> dict[str, object]:
    """Populate global native objects, mountain minerals and fish.

    No start reservation is consulted here.  The executable's pass runs
    before the future SAV-only start placement, and the caller deliberately
    keeps those player resources/settlers deferred.
    """

    bank = _pattern_bank_records()
    barrier = _mirror_barrier(grid.side, int(mode))

    fixed_attempts = 0
    fixed_accepts = 0
    for source, object_id, density, flag_mode, pattern_arg in FIXED_OBJECT_CALLS:
        attempts, accepted = _place_fixed(
            grid,
            rng,
            barrier,
            source,
            object_id,
            density,
            flag_mode,
            pattern_arg,
            bank,
        )
        fixed_attempts += attempts
        fixed_accepts += accepted

    range_attempts = 0
    range_accepts = 0
    for source, low_id, high_id, density, flag_mode, pattern_arg in RANGE_OBJECT_CALLS:
        attempts, accepted = _place_range(
            grid,
            rng,
            barrier,
            source,
            low_id,
            high_id,
            density,
            flag_mode,
            pattern_arg,
            bank,
        )
        range_attempts += attempts
        range_accepts += accepted

    mineral_groups: dict[str, int] = {}
    mineral_writes: dict[str, int] = {}
    for family, coefficient in MINERAL_CALLS:
        groups, writes = _place_mineral_family(grid, rng, family, coefficient, bank)
        key = f"{family:02x}"
        mineral_groups[key] = groups
        mineral_writes[key] = writes

    fish_writes, fish_nonzero = _place_fish(grid, rng)

    objects = grid.objects
    resources = grid.resources
    terrain = grid.terrain
    object_values, object_counts = np.unique(objects[objects != 0], return_counts=True)
    object_count_map = {
        str(int(object_id)): int(count)
        for object_id, count in zip(object_values, object_counts)
    }

    final_families = resources & 0xF0
    mineral_families = tuple(family for family, _ in MINERAL_CALLS)
    mineral_family_cells = {
        f"{family:02x}": int(np.count_nonzero(final_families == family))
        for family in mineral_families
    }
    mineral_mask = final_families != 0
    mineral_support = ((terrain & 0xF0) == 0x20) | ((terrain & 0xF0) == 0x80)
    support_count = int(np.count_nonzero(mineral_support))
    mineral_count = int(np.count_nonzero(mineral_mask))

    adult_ids = set(range(68, 78)) | {80, 81}
    palm_ids = {78, 79}
    building_stone_ids = set(range(115, 128))
    adult_trees = sum(object_count_map.get(str(object_id), 0) for object_id in adult_ids)
    palm_trees = sum(object_count_map.get(str(object_id), 0) for object_id in palm_ids)
    building_stone_anchors = sum(
        object_count_map.get(str(object_id), 0) for object_id in building_stone_ids
    )
    building_stone_stock = sum(
        max(0, 127 - object_id) * object_count_map.get(str(object_id), 0)
        for object_id in range(115, 127)
    )
    decorative_objects = max(
        0,
        int(np.count_nonzero(objects)) - adult_trees - palm_trees - building_stone_anchors,
    )

    water_like = (terrain & 0xF0) == 0
    fish_mask = water_like & ((resources & 0xF0) == 0) & ((resources & 0x0F) > 0)

    minerals_meta = {
        "mineral_model_status": "recovered_s3_exe",
        "mineral_support_rule": "terrain_high_nibble_0x20_or_0x80",
        "mineral_support_cells": support_count,
        "mineral_mountain_final_cells": mineral_count,
        "mineral_mountain_occupancy": (
            float(mineral_count / support_count) if support_count else 0.0
        ),
        "mineral_family_cells": mineral_family_cells,
        "native_mineral_group_counts": mineral_groups,
        "native_mineral_group_writes": mineral_writes,
    }
    fish_meta = {
        "fish_model_status": "recovered_s3_exe",
        "fish_cells": int(np.count_nonzero(fish_mask)),
        "fish_written_cells": fish_writes,
        "fish_nonzero_writes": fish_nonzero,
    }
    trees_meta = {
        "adult_trees": adult_trees,
        "palm_trees": palm_trees,
        "native_tree_ids": sorted(adult_ids),
        "native_palm_ids": sorted(palm_ids),
    }
    stones_meta = {
        "building_stone_anchors": building_stone_anchors,
        "building_stone_stock": building_stone_stock,
        "native_building_stone_ids": sorted(building_stone_ids),
    }
    decorations_meta = {
        "decorative_objects": decorative_objects,
        "native_static_objects": int(np.count_nonzero(objects)),
    }
    return {
        "native_content_core": "recovered_s3_exe",
        "native_content_excludes": ("player_start_objects", "settlers", "sav_writer"),
        "native_pattern_bank_records": len(bank),
        "native_fixed_object_calls": len(FIXED_OBJECT_CALLS),
        "native_range_object_calls": len(RANGE_OBJECT_CALLS),
        "native_fixed_object_attempts": fixed_attempts,
        "native_fixed_object_accepts": fixed_accepts,
        "native_range_object_attempts": range_attempts,
        "native_range_object_accepts": range_accepts,
        "native_object_attempts": fixed_attempts + range_attempts,
        "native_object_accepts": fixed_accepts + range_accepts,
        "native_object_counts": object_count_map,
        "native_object_mirror_barrier_cells": int(np.count_nonzero(barrier)),
        "mineral_family_cells": mineral_family_cells,
        "mineral_mountain_final_cells": mineral_count,
        "mineral_mountain_occupancy": (
            float(mineral_count / support_count) if support_count else 0.0
        ),
        "fish_cells": int(np.count_nonzero(fish_mask)),
        "fish_written_cells": fish_writes,
        "adult_trees": adult_trees,
        "palm_trees": palm_trees,
        "building_stone_anchors": building_stone_anchors,
        "building_stone_stock": building_stone_stock,
        "decorative_objects": decorative_objects,
        "native_content": {
            "minerals": minerals_meta,
            "fish": fish_meta,
            "trees": trees_meta,
            "stones": stones_meta,
            "decorations": decorations_meta,
        },
    }


__all__ = (
    "FIXED_OBJECT_CALLS",
    "MINERAL_CALLS",
    "NATIVE_HEX6",
    "RANGE_OBJECT_CALLS",
    "build_native_pattern_bank",
    "populate_native_content",
)
