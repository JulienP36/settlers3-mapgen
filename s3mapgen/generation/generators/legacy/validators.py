"""Read-only hard validations for the procedural Continental Legacy pipeline."""

from __future__ import annotations

import numpy as np
from scipy import ndimage

from ....generation.rules import ValidationResult
from ....map_data.constants import DESERT_IDS, GRASS, GRASS_IDS, MOUNTAIN_IDS, RIVER_IDS, SHORE, SNOW, SNOW_TRANS, START_FOOTPRINT, SWAMP_IDS, WATER_IDS
from ....map_data.hexgrid import HEX6, component_labels, component_sizes, neighbor_count


_HEX = np.array(((1, 1, 0), (1, 1, 1), (0, 1, 1)), dtype=bool)


def _transition_violations(terrain: np.ndarray, terrain_id: int, allowed: set[int]) -> int:
    """Count HEX6 neighbour edges that break one explicit terrain chain."""

    bad = 0
    side = terrain.shape[0]
    for dx, dy in HEX6:
        y0, y1 = max(0, dy), min(side, side + dy)
        x0, x1 = max(0, dx), min(side, side + dx)
        sy0, sy1 = max(0, -dy), min(side, side - dy)
        sx0, sx1 = max(0, -dx), min(side, side - dx)
        current = terrain[y0:y1, x0:x1]
        neighbour = terrain[sy0:sy1, sx0:sx1]
        bad += int(np.count_nonzero((current == terrain_id) & ~np.isin(neighbour, tuple(allowed))))
    return bad


def _family_hole_cells(mask: np.ndarray) -> int:
    filled = ndimage.binary_fill_holes(mask, structure=_HEX)
    return int(np.count_nonzero(filled & ~mask))


def validate(state, profile: dict) -> list[ValidationResult]:
    """Validate runtime-independent terrain, content and export invariants."""

    terrain, height, objects, access, resources = (
        state.terrain,
        state.height,
        state.objects,
        state.accessibility,
        state.resources,
    )
    out: list[ValidationResult] = []

    def add(rule: str, passed: bool, message: str, hard: bool = True) -> None:
        out.append(ValidationResult(rule, bool(passed), message, hard))

    water = np.isin(terrain, WATER_IDS)
    river = np.isin(terrain, RIVER_IDS)
    add("V2_PROCEDURAL_ONLY", state.metadata.get("runtime_native_inputs", 0) == 0, "native_runtime_inputs=0")
    add("WATER_HEIGHT", not np.any(height[water] != 0), f"nonzero={int(np.count_nonzero(height[water]))}")
    add("WATER_ACCESS", not np.any(access[water] != 1), f"bad={int(np.count_nonzero(access[water] != 1))}")
    snow_block = np.isin(terrain, (SNOW_TRANS, SNOW))
    add("SNOW_ACCESS", not np.any(access[snow_block] != 1), f"bad={int(np.count_nonzero(access[snow_block] != 1))}")
    edge = np.concatenate((terrain[0, :], terrain[-1, :], terrain[:, 0], terrain[:, -1]))
    add("DEEP_OCEAN_EDGE", bool(np.all(edge == 7)), f"non_water7={int(np.count_nonzero(edge != 7))}")
    labels, sizes = component_sizes(water)
    sea = int(np.argmax(sizes) + 1) if sizes else 0
    micro = sum(
        1
        for label, size in enumerate(sizes, 1)
        if label != sea and size <= int(profile["terrain"]["forbid_inland_water_components_leq"])
    )
    add("NO_MICRO_LAKES", micro == 0, f"components_1_4={micro}")
    river_labels, river_count = component_labels(river)
    touching_water = neighbor_count(water) > 0
    orphans = sum(not np.any((river_labels == label) & touching_water) for label in range(1, river_count + 1))
    add("RIVERS_CONNECTED", orphans == 0, f"orphan_components={orphans}")
    fish = water & ((resources & 15) > 0)
    add("NO_FISH_IN_RIVERS", not np.any(fish & river), f"bad={int(np.count_nonzero(fish & river))}")
    add("OBJECTS_OFF_MOUNTAINS", not np.any((objects != 0) & np.isin(terrain, MOUNTAIN_IDS)), f"bad={int(np.count_nonzero((objects != 0) & np.isin(terrain, MOUNTAIN_IDS)))}")
    add("START_COUNT", len(state.starts) == int(state.metadata.get("players", len(state.starts))), f"starts={len(state.starts)}")
    start_footprint = np.zeros_like(terrain, dtype=bool)
    for x, y in state.starts:
        for dx, dy in START_FOOTPRINT:
            xx, yy = int(x) + dx, int(y) + dy
            if 0 <= xx < state.side and 0 <= yy < state.side:
                start_footprint[yy, xx] = True
    start_bad = int(np.count_nonzero(terrain[start_footprint] != GRASS))
    add("START_FOOTPRINT_GRASS", start_bad == 0, f"non_grass={start_bad}")

    mountain_bad = sum(
        _transition_violations(terrain, terrain_id, allowed)
        for terrain_id, allowed in ((17, {16, 17, 33}), (33, {17, 33, 32}), (32, {33, 32, 35}))
    )
    desert_bad = sum(
        _transition_violations(terrain, terrain_id, allowed)
        for terrain_id, allowed in ((20, {16, 20, 65}), (65, {20, 65, 64}), (64, {65, 64}))
    )
    swamp_bad = sum(
        _transition_violations(terrain, terrain_id, allowed)
        for terrain_id, allowed in ((21, {16, 21, 81}), (81, {21, 81, 80}), (80, {81, 80}))
    )
    snow_bad = sum(
        _transition_violations(terrain, terrain_id, allowed)
        for terrain_id, allowed in ((35, {32, 35, 129}), (129, {35, 129, 128}), (128, {129, 128}))
    )
    add("MOUNTAIN_TRANSITIONS", mountain_bad == 0, f"bad_edges={mountain_bad}")
    add("DESERT_TRANSITIONS", desert_bad == 0, f"bad_edges={desert_bad}")
    add("SWAMP_TRANSITIONS", swamp_bad == 0, f"bad_edges={swamp_bad}")
    add("SNOW_TRANSITIONS", snow_bad == 0, f"bad_edges={snow_bad}")
    mountain_holes = _family_hole_cells(np.isin(terrain, MOUNTAIN_IDS))
    desert_holes = _family_hole_cells(np.isin(terrain, DESERT_IDS))
    swamp_holes = _family_hole_cells(np.isin(terrain, SWAMP_IDS))
    add(
        "NO_TERRAIN_FAMILY_HOLES",
        mountain_holes + desert_holes + swamp_holes == 0,
        f"mountain={mountain_holes}, desert={desert_holes}, swamp={swamp_holes}",
    )
    shore_without_water = int(np.count_nonzero((terrain == SHORE) & (neighbor_count(water) == 0)))
    shore_labels, shore_count = component_labels(terrain == SHORE)
    shore_singletons = sum(int(np.count_nonzero(shore_labels == label)) == 1 for label in range(1, shore_count + 1))
    add("SHORE_REAL_RIMS", shore_without_water == 0 and shore_singletons == 0, f"without_water={shore_without_water}, singletons={shore_singletons}")
    water_facing = (~water) & (neighbor_count(water) > 0)
    transition_allowed = np.isin(terrain, (SHORE, *RIVER_IDS))
    direct_water_land = int(np.count_nonzero(water_facing & ~transition_allowed))
    direct_water_grass = int(np.count_nonzero(water_facing & np.isin(terrain, GRASS_IDS)))
    add(
        "WATER_SHORE_TRANSITIONS",
        direct_water_land == 0,
        f"direct_water_to_nonshore_land_cells={direct_water_land}",
    )
    add(
        "NO_WATER_GRASS_DIRECT",
        direct_water_grass == 0,
        f"direct_water_to_grass_cells={direct_water_grass}",
    )
    return out


def hard_failures(validations: list[ValidationResult]) -> list[ValidationResult]:
    return [result for result in validations if result.hard and not result.passed]


__all__ = ("hard_failures", "validate")
