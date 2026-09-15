"""Semantic tree and building-stone overrides for Custom Legacy maps.

The Legacy native pass remains the default.  This adapter is entered only
when a visible Custom tree or stone control differs from its Legacy default;
it translates the small semantic section into the existing legal object
placers without exposing their calibrated IDs or collision geometry.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

import numpy as np

from .bonus_placement import FORCED_CENTER_EXTENSION, ordered_centers, plan_objects
from .sections import (
    DECORATION_FAMILY_KEYS,
    DECORATION_FAMILY_SPECS,
    START_FOREST_COUNT_MAX,
    START_STONE_ANCHOR_MAX,
    START_STONE_AVERAGE_DEFAULT,
    UPGRADED_REEF_TARGET_768,
    default_sections,
    normalize_sections,
)
from .terrain import effective_decoration_rates
from ...map_data.constants import GRASS, GRASS_IDS, WATER_IDS
from ...map_data.hexgrid import dilate, hex_distance, neighbor_count
from ..generators.legacy.objects import (
    _building_stone_footprint_mask,
    _live_object_collision_mask,
    _mark_live_object_collision,
    add_building_stones,
    add_trees,
)


ADULT_TREE_IDS = tuple(range(68, 78)) + (80, 81)
PALM_TREE_IDS = (78, 79)
SMALL_TREE_IDS = (84,)
TREE_OBJECT_IDS = ADULT_TREE_IDS + PALM_TREE_IDS + SMALL_TREE_IDS
BUILDING_STONE_IDS = tuple(range(115, 128))
START_FOREST_TREE_SPACING_HEX = 3


def _hex_disc(side: int, cx: int, cy: int, radius: int) -> list[tuple[int, int]]:
    """Return one bounded HEX6 disc without importing a generator class."""

    radius = max(0, int(radius))
    return [
        (x, y)
        for y in range(max(0, int(cy) - radius), min(int(side), int(cy) + radius + 1))
        for x in range(max(0, int(cx) - radius), min(int(side), int(cx) + radius + 1))
        if hex_distance(int(cx), int(cy), x, y) <= radius
    ]


def _minimum_spaced_disc_radius(object_count: int, spacing: int) -> int:
    """Derive the first clean HEX6 disc that can pack spaced anchors.

    The packing probe uses the same HEX6 distance as the actual object
    collision check.  Terrain fragmentation and already occupied cells are
    handled by the placement pass, which may expand this derived envelope.
    """

    target = max(1, int(object_count))
    spacing = max(1, int(spacing))
    radius = 0
    while True:
        points = [
            (x, y)
            for y in range(-radius, radius + 1)
            for x in range(-radius, radius + 1)
            if hex_distance(0, 0, x, y) <= radius
        ]
        chosen: list[tuple[int, int]] = []
        for x, y in points:
            if all(hex_distance(x, y, xx, yy) >= spacing for xx, yy in chosen):
                chosen.append((x, y))
                if len(chosen) >= target:
                    return radius
        radius += 1


def _minimum_tree_forest_radius(
    tree_count: int,
    spacing: int = START_FOREST_TREE_SPACING_HEX,
) -> int:
    return _minimum_spaced_disc_radius(tree_count, spacing)


def _support_terrain_ids(enabled: bool) -> tuple[int, ...]:
    return tuple(GRASS_IDS) if bool(enabled) else (GRASS,)


def _objects_grass_variant_enabled(sections: Mapping[str, Any]) -> bool:
    objects = sections.get("objects", {}) if isinstance(sections, Mapping) else {}
    return bool(
        isinstance(objects, Mapping)
        and objects.get("grass_compatible_on_dry_and_details", False)
    )


def _force_extended_start_bonus(sections: Mapping[str, Any]) -> bool:
    start_bonus = sections.get("start_bonus", {}) if isinstance(sections, Mapping) else {}
    return bool(
        isinstance(start_bonus, Mapping)
        and start_bonus.get("force_extended_radius", False)
    )


def _section(profile: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    direct = profile.get(key)
    if isinstance(direct, Mapping):
        return direct
    legacy_content = profile.get("legacy_content", {})
    if isinstance(legacy_content, Mapping):
        nested = legacy_content.get(key)
        if isinstance(nested, Mapping):
            return nested
    return {}


def _legacy_profile(profile: Mapping[str, Any], sections: Mapping[str, Any]) -> dict[str, Any]:
    """Build the private legacy-content shape consumed by the object placers."""

    legacy_content = profile.get("legacy_content", {})
    result = deepcopy(dict(legacy_content)) if isinstance(legacy_content, Mapping) else {}

    trees = deepcopy(dict(result.get("trees", {}))) if isinstance(result.get("trees"), Mapping) else {}
    source_trees = _section(profile, "trees")
    trees.setdefault("grass_adult_ids", source_trees.get("adult_ids", ADULT_TREE_IDS))
    trees.setdefault("grass_adult_weights", source_trees.get("adult_weights", (1,) * len(ADULT_TREE_IDS)))
    trees.setdefault("grass_adult_target_768", source_trees.get("adult_global_target", 0))
    trees.setdefault("desert_palm_ids", source_trees.get("palm_ids", PALM_TREE_IDS))
    trees.setdefault("desert_palm_target_768", source_trees.get("palm_target", 0))
    trees.setdefault("small_tree_id", source_trees.get("small_tree_id", 84))
    trees.setdefault("small_tree_target_768", source_trees.get("small_tree_target", 0))
    trees.setdefault("small_tree_cluster_share", source_trees.get("small_tree_cluster_share", 0.0))
    tree_sections = sections["trees"]
    sapling_sections = tree_sections["saplings"]
    forest_sections = tree_sections["forests"]
    trees.update(
        {
            "base_quota_percent": tree_sections["base_quota_percent"],
            "saplings_enabled": sapling_sections["enabled"],
            "saplings_in_global_pool": sapling_sections["in_global_pool"],
            "saplings_global_share_percent": sapling_sections["global_share_percent"],
            "saplings_quota_percent": sapling_sections["quota_percent"],
            "saplings_placement": sapling_sections["placement"],
            "forests_enabled": forest_sections["enabled"],
            "forest_share_percent": forest_sections["share_percent"],
            "forest_trees_per_forest": forest_sections["trees_per_forest"],
            "forest_tree_count_variation_percent": forest_sections["tree_count_variation_percent"],
            "palm_quota_percent": tree_sections["palm_quota_percent"],
        }
    )
    result["trees"] = trees

    stones = deepcopy(dict(result.get("building_stones", {}))) if isinstance(result.get("building_stones"), Mapping) else {}
    source_stones = _section(profile, "building_stones")
    stones.setdefault("active_ids", source_stones.get("active_ids", BUILDING_STONE_IDS[:-1]))
    stones.setdefault("exhausted_id", source_stones.get("exhausted_id", 127))
    stones.setdefault("global_anchor_target_768", source_stones.get("global_anchor_target", 0))
    stones.setdefault("global_exhausted_anchor_target", source_stones.get("global_exhausted_anchor_target", 0))
    stones.setdefault("global_stock_target_768", source_stones.get("global_stock_target", 0))
    stones.setdefault("anchor_min_hex_distance", source_stones.get("anchor_min_hex_distance", 4))
    stones.setdefault(
        "footprint",
        source_stones.get(
            "footprint",
            ((-1, -1), (0, -1), (-1, 0), (0, 0), (1, 0), (0, 1), (1, 1)),
        ),
    )
    stones.update(
        {
            "anchor_density_percent": sections["building_stones"]["anchor_density_percent"],
            "average_quantity": sections["building_stones"]["average_quantity"],
            "groups_enabled": sections["building_stones"]["groups"]["enabled"],
            "cluster_share_percent": sections["building_stones"]["groups"]["share_percent"],
            "cluster_typical_anchors": sections["building_stones"]["groups"]["stones_per_group"],
            "cluster_count_variation_percent": sections["building_stones"]["groups"]["stone_count_variation_percent"],
        }
    )
    result["building_stones"] = stones
    return {"legacy_content": result}


def _stone_footprint_mask(state, footprint=None) -> np.ndarray:
    """Recover full stone emprises when native metadata stores anchors only."""

    mask = _building_stone_footprint_mask(state)
    for cell in state.metadata.get("legacy_start_building_stone_footprint_cells", ()):
        if isinstance(cell, (tuple, list)) and len(cell) == 2:
            x, y = int(cell[0]), int(cell[1])
            if 0 <= x < state.side and 0 <= y < state.side:
                mask[y, x] = True
    if footprint is None:
        return mask
    objects = state.objects
    for y, x in np.argwhere(np.isin(objects, BUILDING_STONE_IDS)):
        for dx, dy in footprint:
            xx, yy = int(x) + int(dx), int(y) + int(dy)
            if 0 <= xx < state.side and 0 <= yy < state.side:
                mask[yy, xx] = True
    return mask


def semantic_object_changes(
    profile: Mapping[str, Any],
    sections: Mapping[str, Any],
) -> tuple[dict[str, Any], bool, bool, bool]:
    """Return normalized sections and the object families needing replacement."""

    fallback = default_sections(profile, "legacy")
    normalized = normalize_sections(sections, fallback=fallback)
    effective_decorations = effective_decoration_rates(normalized)
    fallback_decorations = effective_decoration_rates(fallback)
    grass_variant_support = _objects_grass_variant_enabled(normalized)
    return (
        normalized,
        normalized["trees"] != fallback["trees"] or grass_variant_support,
        normalized["building_stones"] != fallback["building_stones"] or grass_variant_support,
        effective_decorations != fallback_decorations or grass_variant_support,
    )


def _decoration_support_mask(
    state,
    family_key: str,
    spec: Mapping[str, Any],
    *,
    grass_support_ids: tuple[int, ...] = (GRASS,),
) -> np.ndarray:
    """Return the native support terrain for one static decoration family."""

    if family_key == "reefs":
        water = np.isin(state.terrain, WATER_IDS)
        return (state.terrain == 7) & (neighbor_count(~water) == 0)
    support_ids = tuple(int(value) for value in spec.get("support_ids", ()))
    if GRASS in support_ids:
        support_ids = tuple(dict.fromkeys((*support_ids, *grass_support_ids)))
    return np.isin(state.terrain, support_ids)


def _replace_legacy_decorations(
    state,
    rates: Mapping[str, Any],
    occupied: np.ndarray,
    rng: np.random.Generator,
    changed_families: tuple[str, ...],
    stone_footprint,
    native_baseline_counts: Mapping[str, int],
    grass_support_ids: tuple[int, ...] = (GRASS,),
    collision_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Scale only changed native decoration families from their actual count.

    The native pass has already created the selected profile's decorations.
    A Custom rate therefore means ``target = native_count × rate`` rather
    than an invented global map quota.  Reefs are the deliberate exception:
    Legacy's native count is zero, so they use the shared calibrated Upgraded
    target as their reference.  This keeps 100% untouched for ordinary
    families and makes every rate proportional to the exact map size.
    """

    objects = state.objects
    access = state.accessibility
    blocked = occupied.copy()
    blocked |= _stone_footprint_mask(state, stone_footprint)
    if collision_mask is not None:
        blocked |= np.asarray(collision_mask, dtype=bool)
    baseline_counts: dict[str, int] = {}
    targets: dict[str, int] = {}
    counts: dict[str, int] = {}
    shortfalls: dict[str, int] = {}
    normalized_rates: dict[str, float] = {}

    for family_key in DECORATION_FAMILY_KEYS:
        spec = DECORATION_FAMILY_SPECS[family_key]
        ids = tuple(int(value) for value in spec["ids"])
        baseline_count = int(native_baseline_counts.get(family_key, 0))
        baseline_counts[family_key] = baseline_count
        try:
            rate = min(500.0, max(0.0, float(rates.get(family_key, 100.0))))
        except (TypeError, ValueError):
            rate = 100.0
        normalized_rates[family_key] = rate
        if family_key not in changed_families:
            counts[family_key] = baseline_count
            targets[family_key] = baseline_count
            shortfalls[family_key] = 0
            continue

        # Changed families were omitted from the native layer before any
        # bonus or Custom object placement, so their legal cells are available
        # without a later erase pass.
        if family_key == "reefs":
            # Legacy's native reef population is intentionally zero, but a
            # positive Custom rate must still have a meaningful reference.
            # Use the established Upgraded target, scaled to this map size;
            # 0% remains empty and 100% means the current Upgraded behaviour.
            scale = (float(state.side) / 768.0) ** 2
            reference_target = int(round(UPGRADED_REEF_TARGET_768 * scale))
            target = int(round(reference_target * rate / 100.0))
        else:
            target = int(round(baseline_count * rate / 100.0))
        targets[family_key] = target
        support = _decoration_support_mask(
            state,
            family_key,
            spec,
            grass_support_ids=grass_support_ids,
        )
        candidates = np.argwhere(support & ~blocked & (objects == 0))
        placed = 0
        if target and len(candidates):
            id_array = np.asarray(ids, dtype=np.uint8)
            for index in rng.permutation(len(candidates)):
                if placed >= target:
                    break
                y, x = map(int, candidates[index])
                if blocked[y, x] or objects[y, x] != 0:
                    continue
                objects[y, x] = int(rng.choice(id_array))
                access[y, x] = 1
                if collision_mask is not None:
                    _mark_live_object_collision(blocked, int(x), int(y))
                placed += 1
        counts[family_key] = placed
        shortfalls[family_key] = max(0, target - placed)

    return {
        "model": "native_family_reference_count_scaled",
        "rates": normalized_rates,
        "baseline_counts": baseline_counts,
        "targets": targets,
        "counts": counts,
        "shortfalls": shortfalls,
        "cleared": {},
        "decorative_objects": int(sum(counts.values())),
    }


def apply_custom_legacy_objects(
    state,
    profile: Mapping[str, Any],
    sections: Mapping[str, Any],
    start_occupied: np.ndarray,
    rng: np.random.Generator,
    start_bonus_object_clearance: np.ndarray | None = None,
) -> dict[str, Any]:
    """Replace only the semantic object families changed by the user."""

    normalized, replace_trees, replace_stones, replace_decorations = semantic_object_changes(profile, sections)
    grass_support_enabled = _objects_grass_variant_enabled(normalized)
    grass_support_ids = _support_terrain_ids(grass_support_enabled)
    if not replace_trees and not replace_stones and not replace_decorations:
        return {"trees": {}, "stones": {}, "decorations": {}, "replaced": (), "cleared": {}}

    legacy_profile = _legacy_profile(profile, normalized)
    stone_footprint = legacy_profile["legacy_content"]["building_stones"]["footprint"]

    decoration_rates = effective_decoration_rates(normalized)
    # Compare against the selected profile's semantic defaults, rather than
    # against a hard-coded 100%.  In particular, Legacy's reef default is 0%
    # and must not be treated as a user-edited family when another decoration
    # is changed.
    default_decoration_rates = effective_decoration_rates(default_sections(profile, "legacy"))
    changed_decoration_families = tuple(
        key for key in DECORATION_FAMILY_KEYS
        if float(decoration_rates.get(key, default_decoration_rates.get(key, 100.0)))
        != float(default_decoration_rates.get(key, 100.0))
    ) if replace_decorations else ()
    if grass_support_enabled:
        changed_decoration_families = tuple(dict.fromkeys(
            (*changed_decoration_families, *(
                key for key in DECORATION_FAMILY_KEYS
                if GRASS in tuple(int(value) for value in DECORATION_FAMILY_SPECS[key].get("support_ids", ()))
            ))
        ))
    decoration_baseline_counts = {
        family_key: int(
            np.count_nonzero(
                np.isin(state.objects, tuple(int(value) for value in DECORATION_FAMILY_SPECS[family_key]["ids"]))
            )
        )
        for family_key in DECORATION_FAMILY_KEYS
    }

    # Changed native families are deliberately absent from the initial layer:
    # they were disabled before the native placement pass, not placed and
    # erased afterwards.  Keep the proportional Custom model by using the
    # selected profile's calibrated map-size reference for those families
    # instead of treating their intentionally empty live layer as a zero
    # baseline.
    native_profile = profile
    if not isinstance(profile.get("legacy_content"), Mapping) or not profile.get(
        "legacy_content", {}
    ).get("native_objects"):
        from ..generators.legacy.profile import load_profile

        native_profile = load_profile()
    native_objects = native_profile.get("legacy_content", {}).get("native_objects", {})
    native_families = (
        native_objects.get("families", {})
        if isinstance(native_objects, Mapping)
        else {}
    )
    split = int(native_objects.get("density_split_players", 8)) if isinstance(
        native_objects, Mapping
    ) else 8
    density_key = "low" if int(state.metadata.get("players", 0)) <= split else "high"
    scale = (float(state.side) / 768.0) ** 2
    for family_key in changed_decoration_families:
        if decoration_baseline_counts[family_key] != 0:
            continue
        family_profile = native_families.get(family_key, {})
        target_by_density = (
            family_profile.get("target_768_by_density", {})
            if isinstance(family_profile, Mapping)
            else {}
        )
        if isinstance(target_by_density, Mapping):
            decoration_baseline_counts[family_key] = int(round(
                float(target_by_density.get(density_key, 0)) * scale
            ))

    # The native pass was told not to emit changed families.  There is
    # therefore nothing to erase here: every following object is written once
    # on a cell that is still legal at the moment of placement.
    cleared: dict[str, Any] = {}
    occupied = np.asarray(start_occupied, dtype=bool).copy()
    occupied |= _stone_footprint_mask(state, stone_footprint)
    occupied |= state.objects != 0
    if start_bonus_object_clearance is not None:
        occupied |= np.asarray(start_bonus_object_clearance, dtype=bool)

    # Only the active Custom replacement route enables the generalized live
    # hitbox field.  The untouched native/preset path never enters this
    # function, preserving its byte-identical object stream.
    live_collision = _live_object_collision_mask(
        state,
        start_bonus_object_clearance=start_bonus_object_clearance,
    )
    live_collision |= np.asarray(start_occupied, dtype=bool)
    occupied |= live_collision

    result: dict[str, Any] = {
        "replaced": tuple(
            key for key, enabled in (
                ("trees", replace_trees),
                ("stones", replace_stones),
                ("decorations", replace_decorations),
            ) if enabled
        ),
        "cleared": cleared,
    }
    if replace_trees:
        result["trees"] = add_trees(
            state,
            legacy_profile,
            occupied,
            rng,
            grass_support_ids=grass_support_ids,
            collision_mask=live_collision,
        )
        state.metadata["trees"] = result["trees"]
        live_collision = _live_object_collision_mask(
            state,
            start_bonus_object_clearance=start_bonus_object_clearance,
        )
        live_collision |= np.asarray(start_occupied, dtype=bool)
        occupied[...] |= live_collision
    else:
        result["trees"] = state.metadata.get("trees", {})
    if replace_stones:
        result["stones"] = add_building_stones(
            state,
            legacy_profile,
            occupied,
            rng,
            grass_support_ids=grass_support_ids,
            collision_mask=live_collision,
        )
        state.metadata["stones"] = result["stones"]
        live_collision = _live_object_collision_mask(
            state,
            start_bonus_object_clearance=start_bonus_object_clearance,
        )
        live_collision |= np.asarray(start_occupied, dtype=bool)
        occupied[...] |= live_collision
    else:
        result["stones"] = state.metadata.get("stones", {})
    if replace_decorations:
        result["decorations"] = _replace_legacy_decorations(
            state,
            decoration_rates,
            occupied,
            rng,
            changed_decoration_families,
            stone_footprint,
            decoration_baseline_counts,
            grass_support_ids,
            collision_mask=live_collision,
        )
        state.metadata["decorations"] = result["decorations"]
    else:
        result["decorations"] = state.metadata.get("decorations", {})
    return result


def apply_custom_legacy_start_forest(
    state,
    profile: Mapping[str, Any],
    sections: Mapping[str, Any],
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Place the opt-in start forest on top of Custom Legacy content.

    Legacy's native pass has no start-object layer.  This helper is
    therefore deliberately separate from ``add_trees``: the global Legacy
    quota stays untouched, while the additional per-player adults and
    saplings use the same 3-HEX6 object spacing and the live object layer as
    their collision source.
    """

    fallback = default_sections(profile, "legacy")
    normalized = normalize_sections(sections, fallback=fallback)
    runtime = profile.get("_custom_runtime", {})
    package_enabled = bool(
        isinstance(runtime, Mapping)
        and "start_forest" in tuple(runtime.get("start_packages", ()))
    )
    forest_cfg = normalized["start_bonus"]["forest"]
    bonus_enabled = package_enabled and bool(forest_cfg.get("enabled", True))
    adult_target = (
        int(round(float(forest_cfg.get("adult_trees_per_player", 30))))
        if bonus_enabled else 0
    )
    small_target = (
        int(round(float(forest_cfg.get("saplings_per_player", 20))))
        if bonus_enabled else 0
    )
    adult_target = min(START_FOREST_COUNT_MAX, max(0, adult_target))
    small_target = min(START_FOREST_COUNT_MAX, max(0, small_target))
    support_enabled = _objects_grass_variant_enabled(normalized)
    support_ids = _support_terrain_ids(support_enabled)
    force_extended = _force_extended_start_bonus(normalized)
    total_target = adult_target + small_target
    minimum_radius = (
        _minimum_tree_forest_radius(total_target, START_FOREST_TREE_SPACING_HEX)
        if bonus_enabled and total_target > 0 else 0
    )
    minimum_adult_radius = (
        _minimum_tree_forest_radius(adult_target, START_FOREST_TREE_SPACING_HEX)
        if bonus_enabled and adult_target > 0 else 0
    )
    metadata: dict[str, Any] = {
        "enabled": bool(bonus_enabled),
        "per_player": True,
        "adult_trees_per_player": int(adult_target),
        "saplings_per_player": int(small_target),
        "adult_requested": int(adult_target * len(getattr(state, "starts", ()))),
        "saplings_requested": int(small_target * len(getattr(state, "starts", ()))),
        "adult_placed": 0,
        "saplings_placed": 0,
        "minimum_required_radius": int(minimum_radius),
        "radius_mode": "derived_from_tree_count_and_spacing",
        "tree_spacing_hex": START_FOREST_TREE_SPACING_HEX,
        "distance_from_border": int(normalized["start_bonus"].get("distance_from_border", 0)),
        "support_terrains": [int(value) for value in support_ids],
        "force_extended_radius": bool(force_extended),
        **({"center_extension_limit": FORCED_CENTER_EXTENSION} if force_extended else {}),
        "extended_radius_used": False,
        "global_quota_excludes_start_bonus": True,
        "outside_technical_zone": True,
        "forests": [],
        "shortfalls": [],
    }
    if not bonus_enabled:
        metadata["disabled_reason"] = (
            "disabled by Custom start-package switch"
            if not package_enabled else "disabled by Custom profile"
        )
        state.metadata["legacy_start_forest"] = metadata
        return metadata

    terrain, objects, access = state.terrain, state.objects, state.accessibility
    side = int(state.side)
    technical_radius = int(
        max(
            1,
            _section(profile, "starts").get(
                "editor_object_clear_hex",
                _section(profile, "starts").get("technical_clear_hex", 14),
            ),
        )
    )
    technical = np.zeros_like(terrain, dtype=bool)
    for sx, sy in state.starts:
        for x, y in _hex_disc(side, int(sx), int(sy), technical_radius):
            technical[y, x] = True

    source_trees = _section(profile, "trees")
    adult_ids = tuple(int(value) for value in source_trees.get("adult_ids", ADULT_TREE_IDS))
    if not adult_ids:
        adult_ids = ADULT_TREE_IDS
    raw_weights = source_trees.get("adult_weights", (1,) * len(adult_ids))
    try:
        weights = np.asarray(tuple(float(value) for value in raw_weights), dtype=float)
    except (TypeError, ValueError):
        weights = np.ones(len(adult_ids), dtype=float)
    if len(weights) != len(adult_ids) or not np.isfinite(weights).all() or float(weights.sum()) <= 0:
        weights = np.ones(len(adult_ids), dtype=float)
    weights /= weights.sum()
    small_id = int(source_trees.get("small_tree_id", 84))
    start_profile = profile.get("start_bonus", {})
    start_profile = start_profile if isinstance(start_profile, Mapping) else {}
    forest_profile = start_profile.get("forest", {})
    forest_profile = forest_profile if isinstance(forest_profile, Mapping) else {}
    center_radius = int(forest_profile.get(
        "center_hex",
        _section(profile, "starts").get("initial_territory_hex_radius", 34),
    ))
    center_radius += int(normalized["start_bonus"].get("distance_from_border", 0))
    center_radius = max(1, center_radius)
    def object_clear(x: int, y: int) -> bool:
        spacing = START_FOREST_TREE_SPACING_HEX
        return not any(
            objects[yy, xx] != 0
            and hex_distance(x, y, xx, yy) < spacing
            for yy in range(max(0, y - spacing), min(side, y + spacing + 1))
            for xx in range(max(0, x - spacing), min(side, x + spacing + 1))
        )

    def place(
        mask: np.ndarray,
        count: int,
        ids,
        probabilities=None,
        point_sink: list[tuple[int, int]] | None = None,
    ) -> int:
        candidates = np.argwhere(
            mask
            & np.isin(terrain, support_ids)
            & ~technical
            & (objects == 0)
        )
        placed = 0
        if not count or not len(candidates):
            return 0
        id_array = np.asarray(tuple(ids), dtype=np.uint8)
        for index in rng.permutation(len(candidates)):
            if placed >= count:
                break
            y, x = map(int, candidates[index])
            if not object_clear(x, y):
                continue
            object_id = (
                int(rng.choice(id_array, p=probabilities))
                if probabilities is not None else int(rng.choice(id_array))
            )
            objects[y, x] = object_id
            access[y, x] = 1
            if point_sink is not None:
                point_sink.append((x, y))
            placed += 1
        return placed

    def centre_candidates(sx: int, sy: int) -> list[tuple[int, int]]:
        if force_extended:
            return list(ordered_centers(
                np.isin(terrain, support_ids) & ~technical & (objects == 0),
                sx, sy, center_radius, rng.shuffle,
            ))
        centres: list[tuple[int, int]] = []
        for ring in range(max(1, center_radius - 2), center_radius + 3):
            centres.extend(
                (x, y)
                for x, y in _hex_disc(side, sx, sy, ring)
                if hex_distance(sx, sy, x, y) == ring
                and np.isin(terrain[y, x], support_ids)
                and not technical[y, x]
                and objects[y, x] == 0
            )
        if not centres:
            return []
        if centres:
            local = [
                point for point in centres
                if hex_distance(sx, sy, point[0], point[1]) <= center_radius + 2
            ]
            extended = [
                point for point in centres
                if hex_distance(sx, sy, point[0], point[1]) > center_radius + 2
            ]
            if local:
                order = rng.permutation(len(local))
                local = [local[int(index)] for index in order]
            centres = local + extended
        return centres

    for player, (sx, sy) in enumerate(state.starts, start=1):
        centres = centre_candidates(int(sx), int(sy))
        if not centres:
            metadata["shortfalls"].append({
                "player": player,
                "adult": int(adult_target),
                "saplings": int(small_target),
                "reason": "no_legal_grass_center",
            })
            continue
        forced_plan = None
        if force_extended:
            forced_plan = plan_objects(
                centres,
                np.isin(terrain, support_ids) & ~technical & (objects == 0)
                & (state.resources == 0),
                _live_object_collision_mask(state),
                (adult_target, small_target), START_FOREST_TREE_SPACING_HEX,
                ((0, 0),), minimum_radius, minimum_adult_radius, rng,
            )
        cx, cy = forced_plan.center if forced_plan is not None else centres[0]
        forest = np.zeros_like(terrain, dtype=bool)
        adult_count = 0
        small_count = 0
        adult_points: list[tuple[int, int]] = []
        small_points: list[tuple[int, int]] = []
        adult_region_radius = minimum_adult_radius
        effective_radius = minimum_radius
        # There is intentionally no user-facing maximum.  The envelope grows
        # until the requested legal population fits or the finite map is
        # exhausted; the latter is reported as a shortfall.
        if force_extended and forced_plan is not None:
            adult_points = forced_plan.adults
            small_points = forced_plan.saplings
            adult_count, small_count = len(adult_points), len(small_points)
            effective_radius = forced_plan.radius
            adult_region_radius = forced_plan.adult_radius
            for x, y in adult_points:
                objects[y, x] = int(rng.choice(adult_ids, p=weights))
                access[y, x] = 1
            for x, y in small_points:
                objects[y, x] = small_id
                access[y, x] = 1
        else:
            for radius in range(minimum_radius, max(minimum_radius, side * 2) + 1):
                effective_radius = radius
                forest = np.zeros_like(terrain, dtype=bool)
                for x, y in _hex_disc(side, cx, cy, radius):
                    if (
                        np.isin(terrain[y, x], support_ids)
                        and not technical[y, x]
                    ):
                        forest[y, x] = True
                if adult_count < adult_target:
                    adult_region_radius = min(
                        radius,
                        max(
                            minimum_adult_radius,
                            minimum_adult_radius + radius - minimum_radius,
                        ),
                    )
                    adult_region = np.zeros_like(forest)
                    for x, y in _hex_disc(side, cx, cy, adult_region_radius):
                        if forest[y, x]:
                            adult_region[y, x] = True
                    adult_count += place(
                        adult_region,
                        adult_target - adult_count,
                        adult_ids,
                        weights,
                        point_sink=adult_points,
                    )
                if adult_count >= adult_target:
                    sapling_region = forest.copy()
                    if adult_target > 0:
                        for x, y in _hex_disc(side, cx, cy, adult_region_radius):
                            sapling_region[y, x] = False
                    small_count += place(
                        sapling_region,
                        small_target - small_count,
                        (small_id,),
                        point_sink=small_points,
                    )
                if adult_count >= adult_target and small_count >= small_target:
                    break
        metadata["adult_placed"] += int(adult_count)
        metadata["saplings_placed"] += int(small_count)
        if adult_count < adult_target or small_count < small_target:
            metadata["shortfalls"].append({
                "player": player,
                "adult": int(adult_target - adult_count),
                "saplings": int(small_target - small_count),
                "reason": "insufficient_legal_support",
            })
        metadata["forests"].append({
            "player": player,
            "center_x": int(cx),
            "center_y": int(cy),
            "radius": int(effective_radius),
            "minimum_required_radius": int(minimum_radius),
            "adult_core_radius": int(adult_region_radius),
            "adult": int(adult_count),
            "saplings": int(small_count),
            "adult_points": [[int(x), int(y)] for x, y in adult_points],
            "small_points": [[int(x), int(y)] for x, y in small_points],
        })
        metadata["extended_radius_used"] = bool(
            metadata["extended_radius_used"]
            or hex_distance(int(sx), int(sy), int(cx), int(cy)) > center_radius + 2
        )

    metadata["occupied_cells"] = int(
        metadata["adult_placed"] + metadata["saplings_placed"]
    )
    state.metadata["legacy_start_forest"] = metadata
    return metadata


def apply_custom_legacy_start_stones(
    state,
    profile: Mapping[str, Any],
    sections: Mapping[str, Any],
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Place opt-in start stones without changing Legacy's global quota."""

    from ..generators.upgraded.content import _full_range_quantities

    fallback = default_sections(profile, "legacy")
    normalized = normalize_sections(sections, fallback=fallback)
    runtime = profile.get("_custom_runtime", {})
    package_enabled = bool(
        isinstance(runtime, Mapping)
        and "start_building_stones" in tuple(runtime.get("start_packages", ()))
    )
    stone_cfg = normalized["start_bonus"]["building_stones"]
    bonus_enabled = package_enabled and bool(stone_cfg.get("enabled", True))
    anchor_target = (
        min(
            START_STONE_ANCHOR_MAX,
            max(0, int(round(float(stone_cfg.get("anchors_per_player", 15))))),
        )
        if bonus_enabled else 0
    )
    average = float(stone_cfg.get("average_quantity", START_STONE_AVERAGE_DEFAULT))
    average = min(12.0, max(1.0, np.floor(average * 2.0 + 0.5) / 2.0))
    stock_target = int(np.floor(anchor_target * average + 0.5))
    source = _section(profile, "building_stones")
    footprint = tuple(
        tuple(int(value) for value in item)
        for item in source.get(
            "footprint",
            ((-1, -1), (0, -1), (-1, 0), (0, 0), (1, 0), (0, 1), (1, 1)),
        )
    )
    spacing = max(1, int(source.get("anchor_min_hex_distance", 4)))
    minimum_radius = (
        _minimum_spaced_disc_radius(anchor_target, spacing) + 2
        if bonus_enabled and anchor_target > 0 else 0
    )
    support_enabled = _objects_grass_variant_enabled(normalized)
    support_ids = _support_terrain_ids(support_enabled)
    force_extended = _force_extended_start_bonus(normalized)
    metadata: dict[str, Any] = {
        "enabled": bool(bonus_enabled),
        "per_player": True,
        "anchors_per_player": int(anchor_target),
        "average_quantity": float(average),
        "stock_units_per_player": int(stock_target),
        "anchors_requested": int(anchor_target * len(getattr(state, "starts", ()))),
        "anchors_placed": 0,
        "stock_placed": 0,
        "quantity_distribution_model": "full_range_mean_tilt",
        "minimum_required_radius": int(minimum_radius),
        "radius_mode": "derived_from_anchor_count_and_spacing",
        "anchor_spacing_hex": int(spacing),
        "distance_from_border": int(normalized["start_bonus"].get("distance_from_border", 0)),
        "support_terrains": [int(value) for value in support_ids],
        "force_extended_radius": bool(force_extended),
        **({"center_extension_limit": FORCED_CENTER_EXTENSION} if force_extended else {}),
        "extended_radius_used": False,
        "global_quota_excludes_start_bonus": True,
        "outside_technical_zone": True,
        "groups": [],
        "shortfalls": [],
    }
    if not bonus_enabled:
        metadata["disabled_reason"] = (
            "disabled by Custom start-package switch"
            if not package_enabled else "disabled by Custom profile"
        )
        state.metadata["legacy_start_building_stones"] = metadata
        return metadata

    terrain, objects, access = state.terrain, state.objects, state.accessibility
    side = int(state.side)
    starts_cfg = _section(profile, "starts")
    technical_radius = int(max(
        1,
        starts_cfg.get("editor_object_clear_hex", starts_cfg.get("technical_clear_hex", 14)),
    ))
    technical = np.zeros_like(terrain, dtype=bool)
    for sx, sy in state.starts:
        for x, y in _hex_disc(side, int(sx), int(sy), technical_radius):
            technical[y, x] = True
    start_profile = profile.get("start_bonus", {})
    start_profile = start_profile if isinstance(start_profile, Mapping) else {}
    stone_profile = start_profile.get("building_stones", {})
    stone_profile = stone_profile if isinstance(stone_profile, Mapping) else {}
    center_radius = int(stone_profile.get(
        "center_hex",
        starts_cfg.get("initial_territory_hex_radius", 34),
    ))
    center_radius = max(
        1,
        center_radius + int(normalized["start_bonus"].get("distance_from_border", 0)),
    )
    def centre_candidates(sx: int, sy: int) -> list[tuple[int, int]]:
        if force_extended:
            return list(ordered_centers(
                np.isin(terrain, support_ids) & ~technical & (objects == 0),
                sx, sy, center_radius, rng.shuffle,
            ))
        centres: list[tuple[int, int]] = []
        for ring in range(max(1, center_radius - 2), center_radius + 3):
            centres.extend(
                (x, y)
                for x, y in _hex_disc(side, sx, sy, ring)
                if hex_distance(sx, sy, x, y) == ring
                and np.isin(terrain[y, x], support_ids)
                and not technical[y, x]
                and objects[y, x] == 0
            )
        if not centres:
            return []
        if centres:
            local = [
                point for point in centres
                if hex_distance(sx, sy, point[0], point[1]) <= center_radius + 2
            ]
            extended = [
                point for point in centres
                if hex_distance(sx, sy, point[0], point[1]) > center_radius + 2
            ]
            if local:
                order = rng.permutation(len(local))
                local = [local[int(index)] for index in order]
            centres = local + extended
        return centres

    for player, (sx, sy) in enumerate(state.starts, start=1):
        centres = centre_candidates(int(sx), int(sy))
        if not centres:
            metadata["shortfalls"].append({
                "player": player,
                "anchors": int(anchor_target),
                "stock": int(stock_target),
                "reason": "no_legal_grass_center",
            })
            continue
        forced_plan = None
        if force_extended:
            forced_plan = plan_objects(
                centres,
                np.isin(terrain, support_ids) & ~technical & (objects == 0)
                & (state.resources == 0),
                dilate(objects != 0, max(0, spacing - 1)),
                (anchor_target, 0), spacing, footprint,
                minimum_radius, minimum_radius, rng,
            )
        cx, cy = forced_plan.center if forced_plan is not None else centres[0]
        blocked = (
            dilate(objects != 0, max(0, spacing - 1))
            | technical
        )
        covered = np.zeros_like(terrain, dtype=bool)
        points: list[tuple[int, int]] = []
        region = np.zeros_like(terrain, dtype=bool)
        effective_radius = minimum_radius

        def valid(x: int, y: int) -> bool:
            if blocked[y, x]:
                return False
            for dx, dy in footprint:
                xx, yy = x + dx, y + dy
                if not (1 <= xx < side - 1 and 1 <= yy < side - 1):
                    return False
                if (
                    not np.isin(terrain[yy, xx], support_ids)
                    or objects[yy, xx] != 0
                    or covered[yy, xx]
                ):
                    return False
            return True

        def place(mask: np.ndarray, count: int) -> int:
            candidates = np.argwhere(mask & np.isin(terrain, support_ids) & (objects == 0))
            placed = 0
            for index in rng.permutation(len(candidates)):
                if placed >= count:
                    break
                y, x = map(int, candidates[index])
                if not valid(x, y):
                    continue
                points.append((x, y))
                for dx, dy in footprint:
                    covered[y + dy, x + dx] = True
                for yy in range(max(0, y - spacing + 1), min(side, y + spacing)):
                    for xx in range(max(0, x - spacing + 1), min(side, x + spacing)):
                        if hex_distance(x, y, xx, yy) < spacing:
                            blocked[yy, xx] = True
                placed += 1
            return placed

        placed = 0
        if force_extended and forced_plan is not None:
            points = forced_plan.adults
            placed = len(points)
            effective_radius = forced_plan.radius
        else:
            for radius in range(minimum_radius, max(minimum_radius, side * 2) + 1):
                effective_radius = radius
                region = np.zeros_like(terrain, dtype=bool)
                for x, y in _hex_disc(side, cx, cy, radius):
                    if (
                        np.isin(terrain[y, x], support_ids)
                        and not technical[y, x]
                    ):
                        region[y, x] = True
                placed += place(region, anchor_target - placed)
                if placed >= anchor_target:
                    break

        quantities = _full_range_quantities(
            placed,
            average,
            rng,
            minimum=1,
            maximum=12,
        )
        player_stock = 0
        for (x, y), quantity in zip(points, quantities):
            objects[y, x] = 127 - int(quantity)
            player_stock += int(quantity)
            for dx, dy in footprint:
                access[y + dy, x + dx] = 1
        metadata["anchors_placed"] += int(placed)
        metadata["stock_placed"] += int(player_stock)
        if placed < anchor_target or player_stock < stock_target:
            metadata["shortfalls"].append({
                "player": player,
                "anchors": int(anchor_target - placed),
                "stock": int(max(0, stock_target - player_stock)),
                "reason": "insufficient_legal_support",
            })
        metadata["groups"].append({
            "player": player,
            "center_x": int(cx),
            "center_y": int(cy),
            "radius": int(effective_radius),
            "minimum_required_radius": int(minimum_radius),
            "anchors": int(placed),
            "stock": int(player_stock),
            "points": [[int(x), int(y)] for x, y in points],
        })
        metadata["extended_radius_used"] = bool(
            metadata["extended_radius_used"]
            or hex_distance(int(sx), int(sy), int(cx), int(cy)) > center_radius + 2
        )

    metadata["occupied_cells"] = int(metadata["anchors_placed"] * len(footprint))
    state.metadata["legacy_start_building_stone_footprint_cells"] = [
        [int(x + dx), int(y + dy)]
        for group in metadata["groups"]
        for x, y in group["points"]
        for dx, dy in footprint
        if 0 <= int(x + dx) < side and 0 <= int(y + dy) < side
    ]
    state.metadata["legacy_start_building_stones"] = metadata
    return metadata


__all__ = (
    "ADULT_TREE_IDS",
    "BUILDING_STONE_IDS",
    "PALM_TREE_IDS",
    "SMALL_TREE_IDS",
    "TREE_OBJECT_IDS",
    "apply_custom_legacy_objects",
    "apply_custom_legacy_start_forest",
    "apply_custom_legacy_start_stones",
    "semantic_object_changes",
)
