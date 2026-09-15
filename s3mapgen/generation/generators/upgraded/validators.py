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
    ROCKY,
    SNOW,
    SNOW_TRANS,
    SHORE,
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

    if state.metadata.get("mode_key") == "custom":
        from ...custom.terrain import terrain_transition_violations

        transition_check = terrain_transition_violations(terrain)
        add(
            "CUSTOM_TERRAIN_TRANSITIONS",
            int(transition_check["total"]) == 0,
            f"illegal={int(transition_check['total'])}",
        )

    water = np.isin(terrain, WATER_IDS)
    river = np.isin(terrain, RIVER_IDS)
    mountain = np.isin(terrain, MOUNTAIN_FAMILY_IDS)
    mud_count = int(np.isin(terrain, (23, 144, 145)).sum())
    custom_mud_rate = 0.0
    runtime = profile.get("_custom_runtime", {})
    if isinstance(runtime, dict) and isinstance(runtime.get("sections"), dict) and runtime["sections"]:
        from ...custom.terrain import effective_terrain_rates

        custom_mud_rate = float(effective_terrain_rates(runtime["sections"]).get("mud", 0.0))
    if custom_mud_rate > 0.0:
        add("UPGRADED_MUD_TARGET", mud_count > 0, f"{mud_count} cells at {custom_mud_rate:g}%")
    else:
        add("UPGRADED_NO_MUD", mud_count == 0, "mud parameter is 0")
    add("UPGRADED_WATER_HEIGHT", not np.any(height[water] != 0), f"bad={int(np.count_nonzero(height[water] != 0))}")
    add("UPGRADED_WATER_ACCESS", not np.any(access[water] != 1), f"bad={int(np.count_nonzero(access[water] != 1))}")
    edge = np.concatenate((terrain[0], terrain[-1], terrain[1:-1, 0], terrain[1:-1, -1]))
    add("UPGRADED_DEEP_EDGE", bool(np.all(edge == 7)), f"ids={sorted(set(map(int, edge)))}")
    reefs = np.isin(objects, (111, 112, 113, 114))
    ordinary_objects = (objects != 0) & ~reefs
    add("UPGRADED_OBJECTS_OFF_WATER", not np.any(ordinary_objects & water), f"bad={int(np.count_nonzero(ordinary_objects & water))}")
    add("UPGRADED_OBJECTS_OFF_MOUNTAIN", not np.any((objects != 0) & mountain), f"bad={int(np.count_nonzero((objects != 0) & mountain))}")

    mineral = (resources & 0xF0) != 0
    support = np.isin(terrain, MOUNTAIN_FAMILY_IDS)
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
    fish_metadata = state.metadata.get("upgraded_fish", {})
    fish_target_value = state.metadata.get("upgraded_fish_target")
    if fish_target_value is None:
        fish_target_value = profile.get("fish", {}).get("target_cells", 0)
    fish_target = int(fish_target_value)
    add("UPGRADED_FISH_TARGET", int(fish.sum()) == fish_target, f"{int(fish.sum())}/{fish_target}")
    add("UPGRADED_FISH_WATER_ONLY", not np.any(fish & ~water), f"bad={int(np.count_nonzero(fish & ~water))}")
    add("UPGRADED_FISH_NO_RIVER", not np.any(fish & river), f"bad={int(np.count_nonzero(fish & river))}")
    shore_limit = (
        int(fish_metadata["band_thickness_effective"])
        if isinstance(fish_metadata, dict)
        and fish_metadata.get("near_shore_effective")
        and fish_metadata.get("band_thickness_effective") is not None
        else None
    )
    shore_bad = int(np.count_nonzero(fish & (distance > shore_limit))) if shore_limit is not None else 0
    add(
        "UPGRADED_FISH_SHORE_DISTANCE",
        shore_bad == 0,
        f"bad={shore_bad}" if shore_limit is not None else "not constrained by the active fish section",
    )
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
    object_support_ids = (GRASS,)
    if isinstance(runtime, dict):
        sections = runtime.get("sections", {})
        object_controls = sections.get("objects", {}) if isinstance(sections, dict) else {}
        if isinstance(object_controls, dict) and object_controls.get(
            "grass_compatible_on_dry_and_details", False
        ):
            object_support_ids = GRASS_IDS
    add(
        "UPGRADED_TREES_ON_GRASS",
        not np.any(
            np.isin(objects, np.concatenate((tree_ids, [84])))
            & ~np.isin(terrain, object_support_ids)
        ),
        "grass-compatible support only",
    )

    stone = (objects >= 115) & (objects <= 126)
    exhausted = objects == int(profile["building_stones"]["exhausted_id"])
    anchors = int(np.count_nonzero(stone | exhausted))
    stone_targets = state.metadata.get("upgraded_stone_targets", {})
    target_anchors = int(stone_targets.get("anchors", profile["building_stones"]["global_anchor_target"]))
    stock = int(np.sum(int(profile["building_stones"]["exhausted_id"]) - objects[stone]))
    target_stock = int(stone_targets.get("stock", profile["building_stones"]["global_stock_target"]))
    add("UPGRADED_STONE_ANCHORS", anchors == target_anchors, f"{anchors}/{target_anchors}")
    add("UPGRADED_STONE_STOCK", stock == target_stock, f"{stock}/{target_stock}")
    add(
        "UPGRADED_STONES_ON_GRASS",
        not np.any((stone | exhausted) & ~np.isin(terrain, object_support_ids)),
        "grass-compatible support only",
    )

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
            expected_exhausted = int(stone_meta.get("global_exhausted_anchors", 0))
            actual_exhausted = int(np.count_nonzero(objects == int(profile["building_stones"]["exhausted_id"])))
            add("UPGRADED_STONE_EXHAUSTED_STATES", actual_exhausted == expected_exhausted, f"{actual_exhausted}/{expected_exhausted}")

    reeds = np.isin(objects, profile["decor"].get("swamp_reed_ids", []))
    add("UPGRADED_SWAMP_REEDS", not np.any((objects != 0) & np.isin(terrain, SWAMP_IDS) & ~reeds), "reeds only")
    add("UPGRADED_START_COUNT", len(state.starts) == int(state.metadata.get("players", len(state.starts))), f"starts={len(state.starts)}")
    mini_swamps = state.metadata.get("upgraded_start_mini_swamps", {})
    placed_swamps = mini_swamps.get("placed_cells_per_start", []) if isinstance(mini_swamps, dict) else []
    mini_swamp_disabled = isinstance(mini_swamps, dict) and mini_swamps.get("enabled") is False
    add(
        "UPGRADED_START_MINI_SWAMPS",
        mini_swamp_disabled or (
            len(placed_swamps) == len(state.starts)
            and all(int(value) > 0 for value in placed_swamps)
        ),
        "disabled by Custom profile"
        if mini_swamp_disabled
        else f"starts={sum(int(value) > 0 for value in placed_swamps)}/{len(state.starts)}",
    )
    add(
        "UPGRADED_START_CONTENT_RESTORED",
        not bool(state.metadata.get("upgraded_start_content_deferred")),
        "start terrain, resource and object bonuses active",
    )

    rocky_meta = state.metadata.get("upgraded_start_rocky_minerals", {})
    rocky_ok = True
    rocky_zones = rocky_meta.get("zones", []) if isinstance(rocky_meta, dict) else []
    for zone in rocky_zones:
        cx, cy, radius = int(zone["center_x"]), int(zone["center_y"]), int(zone["radius"])
        family = int(zone["family"])
        # R47 metadata contains only a centre/radius.  R48 also records the
        # exact irregular core so validation does not mistake an organic
        # contour for a missing mineral cell.
        raw_core = zone.get("core_points") if isinstance(zone, dict) else None
        if isinstance(raw_core, (list, tuple)) and raw_core:
            core = [
                (int(point[0]), int(point[1]))
                for point in raw_core
                if isinstance(point, (list, tuple)) and len(point) == 2
            ]
        else:
            # Use the generator's exact HEX6 metric without importing its
            # private placement helper.
            core = [
                (x, y)
                for y in range(max(0, cy - radius), min(state.side, cy + radius + 1))
                for x in range(max(0, cx - radius), min(state.side, cx + radius + 1))
                if _hex_distance(cx, cy, x, y) <= radius
            ]
        rocky_ok &= bool(core) and all(
            terrain[y, x] == ROCKY and (int(resources[y, x]) & 0xF0) == family
            for x, y in core
        )
    add(
        "UPGRADED_START_ROCKY_MINERALS",
        rocky_meta.get("enabled") is False or rocky_ok,
        "independent rocky cores are fully mineralized"
        if rocky_ok
        else "a rocky start zone is incomplete",
    )

    lake_meta = state.metadata.get("upgraded_start_lake_fish_river", {})
    lake_ok = True
    lake_transition_ok = True
    lake_rows = lake_meta.get("per_player", []) if isinstance(lake_meta, dict) else []
    for row in lake_rows:
        lake = row.get("lake") if isinstance(row, dict) else None
        if not isinstance(lake, dict):
            continue
        cx, cy, radius = int(lake["center_x"]), int(lake["center_y"]), int(lake["radius"])
        # Native lakes are intentionally rounded/irregular, so reconstruct the
        # actual water core inside the recorded radius instead of assuming a
        # complete hexagonal disc.  The hexagon option still yields the exact
        # historical disc and therefore exercises the same check.
        core = [
            (x, y)
            for y in range(max(0, cy - radius), min(state.side, cy + radius + 1))
            for x in range(max(0, cx - radius), min(state.side, cx + radius + 1))
            if _hex_distance(cx, cy, x, y) <= radius
            and terrain[y, x] in WATER_IDS
        ]
        expected_core = int(lake.get("core_cells", len(core)))
        lake_ok &= bool(core) and len(core) == expected_core
        core_set = set(core)
        lake_ok &= any(
            terrain[y, x] in RIVER_IDS
            and any(
                0 <= x + dx < state.side
                and 0 <= y + dy < state.side
                and (x + dx, y + dy) in core_set
                for dx, dy in HEX6
            )
            for y in range(max(0, cy - radius - 2), min(state.side, cy + radius + 3))
            for x in range(max(0, cx - radius - 2), min(state.side, cx + radius + 3))
        )
        for x, y in core:
            for dx, dy in HEX6:
                xx, yy = x + dx, y + dy
                if 0 <= xx < state.side and 0 <= yy < state.side:
                    lake_transition_ok &= (xx, yy) in core_set or terrain[yy, xx] in (SHORE, *RIVER_IDS)
    add(
        "UPGRADED_START_LAKE_RIVER",
        lake_meta.get("enabled") is False or lake_ok,
        "each placed bonus lake has a river mouth"
        if lake_ok
        else "a placed bonus lake has no legal river mouth",
    )
    add(
        "UPGRADED_START_LAKE_NO_DIRECT_GRASS",
        lake_meta.get("enabled") is False or lake_transition_ok,
        "bonus lake water is separated from grass by shore"
        if lake_transition_ok
        else "bonus lake water touches grass directly",
    )
    return out


def _hex_distance(x1: int, y1: int, x2: int, y2: int) -> int:
    dx, dy = int(x2) - int(x1), int(y2) - int(y1)
    return max(abs(dx), abs(dy)) if dx * dy >= 0 else abs(dx) + abs(dy)


__all__ = ("validate",)
