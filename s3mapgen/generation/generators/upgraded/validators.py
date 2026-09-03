"""Validators for the independent Upgraded pipeline."""

from __future__ import annotations

from collections import deque

import numpy as np

from ....map_data.constants import (
    DESERT_IDS,
    GRASS,
    GRASS_IDS,
    HEX6,
    MOUNTAIN_FAMILY_IDS,
    RIVER_IDS,
    SNOW,
    SNOW_TRANS,
    SWAMP_IDS,
    WATER_IDS,
)
from ....map_data.hexgrid import neighbor_count
from ...rules import ValidationResult


def _shore_distance(state) -> np.ndarray:
    terrain = state.terrain
    water = np.isin(terrain, WATER_IDS)
    seed = water & (neighbor_count(terrain == 48) > 0)
    result = np.full(terrain.shape, 32767, dtype=np.int16)
    queue = deque()
    for y, x in np.argwhere(seed):
        result[y, x] = 1
        queue.append((int(x), int(y)))
    while queue:
        x, y = queue.popleft()
        next_distance = int(result[y, x]) + 1
        if next_distance > 12:
            continue
        for dx, dy in HEX6:
            xx, yy = x + dx, y + dy
            if 0 <= xx < state.side and 0 <= yy < state.side and water[yy, xx] and next_distance < result[yy, xx]:
                result[yy, xx] = next_distance
                queue.append((xx, yy))
    return result


def validate(state, profile: dict) -> list[ValidationResult]:
    terrain, height, objects, access, resources = (
        state.terrain, state.height, state.objects, state.accessibility, state.resources
    )
    out: list[ValidationResult] = []

    def add(rule: str, passed: bool, message: str, hard: bool = True):
        out.append(ValidationResult(rule, bool(passed), message, hard))

    water = np.isin(terrain, WATER_IDS)
    river = np.isin(terrain, RIVER_IDS)
    mountain = np.isin(terrain, MOUNTAIN_FAMILY_IDS)
    add("UPGRADED_NO_MUD", not np.isin(terrain, (23, 144, 145)).any(), "mud disabled")
    add("UPGRADED_WATER_HEIGHT", not np.any(height[water] != 0), f"bad={int(np.count_nonzero(height[water] != 0))}")
    add("UPGRADED_WATER_ACCESS", not np.any(access[water] != 1), f"bad={int(np.count_nonzero(access[water] != 1))}")
    edge = np.concatenate((terrain[0], terrain[-1], terrain[1:-1, 0], terrain[1:-1, -1]))
    add("UPGRADED_DEEP_EDGE", bool(np.all(edge == 7)), f"ids={sorted(set(map(int, edge)))}")
    reefs = np.isin(objects, (111, 112, 113, 114))
    ordinary_objects = (objects != 0) & ~reefs
    add("UPGRADED_OBJECTS_OFF_WATER", not np.any(ordinary_objects & water), f"bad={int(np.count_nonzero(ordinary_objects & water))}")
    add("UPGRADED_OBJECTS_OFF_MOUNTAIN", not np.any((objects != 0) & mountain), f"bad={int(np.count_nonzero((objects != 0) & mountain))}")

    mineral = (resources & 0xF0) != 0
    support = np.isin(terrain, [32, 34, 35, SNOW_TRANS, SNOW])
    add("UPGRADED_MINERALS_ON_SUPPORT", not np.any(mineral & ~support), "mountain support only")
    expected = state.metadata.get("upgraded_mineral_targets", {})
    for family, cfg in profile["minerals"]["families"].items():
        key = f"{int(family):02x}"
        target = int(expected.get(key, 0))
        actual = int(np.count_nonzero((resources & 0xF0) == int(family)))
        add(f"UPGRADED_MINERAL_{cfg['name'].upper()}", actual == target, f"{actual}/{target}")

    fish = water & ((resources & 0xF0) == 0) & ((resources & 0x0F) > 0)
    distance = _shore_distance(state)
    border = np.zeros_like(water)
    border[[0, -1], :] = True
    border[:, [0, -1]] = True
    fish_target = int(state.metadata.get("upgraded_fish_target", profile["fish"]["target_cells"]))
    add("UPGRADED_FISH_TARGET", int(fish.sum()) == fish_target, f"{int(fish.sum())}/{fish_target}")
    add("UPGRADED_FISH_WATER_ONLY", not np.any(fish & ~water), f"bad={int(np.count_nonzero(fish & ~water))}")
    add("UPGRADED_FISH_NO_RIVER", not np.any(fish & river), f"bad={int(np.count_nonzero(fish & river))}")
    add("UPGRADED_FISH_SHORE_DISTANCE", not np.any(fish & (distance > int(profile["fish"]["max_shore_hex_distance"]))), f"bad={int(np.count_nonzero(fish & (distance > int(profile['fish']['max_shore_hex_distance']))))}")
    add("UPGRADED_FISH_NO_EDGE", not np.any(fish & border), f"bad={int(np.count_nonzero(fish & border))}")

    tree_ids = np.asarray(profile["trees"]["adult_ids"], dtype=np.uint8)
    adult = int(np.isin(objects, tree_ids).sum())
    small = int((objects == int(profile["trees"]["small_tree_id"])).sum())
    palms = int(np.isin(objects, profile["trees"].get("palm_ids", [78, 79])).sum())
    tree_targets = state.metadata.get("upgraded_tree_targets", {})
    adult_target = int(tree_targets.get("adult", profile["trees"]["adult_global_target"]))
    small_target = int(tree_targets.get("small", profile["trees"].get("small_tree_target", 0)))
    palm_target = int(tree_targets.get("palm", profile["trees"].get("palm_target", 0)))
    add("UPGRADED_ADULT_TREES", adult == adult_target, f"{adult}/{adult_target}")
    add("UPGRADED_SMALL_TREES", small == small_target, f"{small}/{small_target}")
    add("UPGRADED_PALMS", palms == palm_target, f"{palms}/{palm_target}")
    add("UPGRADED_TREES_ON_GRASS", not np.any(np.isin(objects, np.concatenate((tree_ids, [84]))) & (terrain != GRASS)), "grass only")

    stone = (objects >= 115) & (objects <= 126)
    exhausted = objects == int(profile["building_stones"]["exhausted_id"])
    anchors = int(np.count_nonzero(stone | exhausted))
    stone_targets = state.metadata.get("upgraded_stone_targets", {})
    target_anchors = int(stone_targets.get("anchors", profile["building_stones"]["global_anchor_target"]))
    stock = int(np.sum(int(profile["building_stones"]["exhausted_id"]) - objects[stone]))
    target_stock = int(stone_targets.get("stock", profile["building_stones"]["global_stock_target"]))
    add("UPGRADED_STONE_ANCHORS", anchors == target_anchors, f"{anchors}/{target_anchors}")
    add("UPGRADED_STONE_STOCK", stock == target_stock, f"{stock}/{target_stock}")
    add("UPGRADED_STONES_ON_GRASS", not np.any((stone | exhausted) & (terrain != GRASS)), "grass only")

    stone_meta = state.metadata.get("upgraded_stones", {})
    if isinstance(stone_meta, dict):
        global_anchors = int(stone_meta.get("global_anchors", 0))
        cluster_placed = int(stone_meta.get("cluster_placed", 0))
        cluster_target = int(stone_meta.get("cluster_target", 0))
        add(
            "UPGRADED_STONE_CLUSTERS",
            cluster_placed == cluster_target,
            f"{cluster_placed}/{cluster_target}",
        )
        if global_anchors:
            expected_exhausted = min(
                int(profile["building_stones"].get("global_exhausted_anchor_target", 0)),
                global_anchors,
            )
            actual_exhausted = int(np.count_nonzero(objects == int(profile["building_stones"]["exhausted_id"])))
            add("UPGRADED_STONE_EXHAUSTED_STATES", actual_exhausted == expected_exhausted, f"{actual_exhausted}/{expected_exhausted}")

    reeds = np.isin(objects, profile["decor"].get("swamp_reed_ids", []))
    add("UPGRADED_SWAMP_REEDS", not np.any((objects != 0) & np.isin(terrain, SWAMP_IDS) & ~reeds), "reeds only")
    add("UPGRADED_START_COUNT", len(state.starts) == int(state.metadata.get("players", len(state.starts))), f"starts={len(state.starts)}")
    mini_swamps = state.metadata.get("upgraded_start_mini_swamps", {})
    placed_swamps = mini_swamps.get("placed_cells_per_start", []) if isinstance(mini_swamps, dict) else []
    add(
        "UPGRADED_START_MINI_SWAMPS",
        len(placed_swamps) == len(state.starts) and all(int(value) > 0 for value in placed_swamps),
        f"starts={sum(int(value) > 0 for value in placed_swamps)}/{len(state.starts)}",
    )
    add(
        "UPGRADED_START_CONTENT_RESTORED",
        not bool(state.metadata.get("upgraded_start_content_deferred")),
        "start forest, stone and mini-swamp bonuses active",
    )
    return out


__all__ = ("validate",)
