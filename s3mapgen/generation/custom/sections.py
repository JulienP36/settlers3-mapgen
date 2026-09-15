"""User-facing Custom generator sections.

The built-in profiles contain calibration and implementation details.  This
module is the small semantic layer exposed by the Custom editor instead: it
keeps the labels stable while each generator maps the values to its own
algorithm.
"""

from __future__ import annotations

from copy import deepcopy
import math
from typing import Any, Mapping

from .terrain import (
    TERRAIN_ENABLED_RATE_MIN,
    TERRAIN_FAMILY_KEYS,
    TERRAIN_RATE_MAX,
    TERRAIN_RATE_MIN,
)


MINERAL_SPECS = (
    ("coal", 0x10),
    ("iron", 0x20),
    ("gold", 0x30),
    ("gems", 0x40),
    ("sulfur", 0x50),
)
MINERAL_KEYS = tuple(key for key, _ in MINERAL_SPECS)
MINERAL_IDS = {key: family for key, family in MINERAL_SPECS}
MINERAL_KEYS_BY_ID = {family: key for key, family in MINERAL_SPECS}
MINERAL_ALGORITHMS = ("legacy", "upgraded", "random")
SIZE_VARIATIONS = ("low", "normal", "high")
RESOURCE_MINIMUM = 1
RESOURCE_MAXIMUM = 15
STONE_QUANTITY_MINIMUM = 1
STONE_QUANTITY_MAXIMUM = 12
STONE_QUANTITY_STEP = 0.5

# These are the readable defaults of the two active resource behaviours.  The
# former Custom editor used a generic 768 calibration placeholder, which made
# a Legacy-derived profile look richer than the intended current behaviour.
LEGACY_RESOURCE_MEAN = 8
UPGRADED_RESOURCE_MEAN = 10
LEGACY_FISH_FILL_PERCENT = 36.5
UPGRADED_FISH_FILL_PERCENT = 50.0
DEFAULT_FISH_BAND_THICKNESS = 12

# Tree and building-stone controls are deliberately relative to the selected
# profile.  This keeps the editor useful on every map size without exposing
# the calibrated object IDs, collision rules or footprint geometry.
SEMANTIC_DENSITY_MIN = 0.0
SEMANTIC_DENSITY_MAX = 200.0
# Base trees and palms are quotas rather than ordinary density controls.  The
# editor deliberately lets them reach five times the selected profile so that
# dense custom scenarios can be compared without changing the other limits.
TREE_QUOTA_MAX = 500.0
SEMANTIC_SHARE_MIN = 0.0
SEMANTIC_SHARE_MAX = 100.0
TREE_PLACEMENTS = ("everywhere", "forests_only", "outside_forests")
FOREST_TREE_COUNT_MIN = 1.0
FOREST_TREE_COUNT_MAX = 100.0
FOREST_TREE_VARIATION_MIN = 0.0
FOREST_TREE_VARIATION_MAX = 100.0
UPGRADED_STONE_CLUSTER_SHARE_PERCENT = 30.0
STONE_GROUP_COUNT_MIN = 1.0
STONE_GROUP_COUNT_MAX = 1000.0
STONE_GROUP_VARIATION_MIN = 0.0
STONE_GROUP_VARIATION_MAX = 100.0

# Start bonuses use explicit on/off package switches plus real quantities.  A
# zero is reserved for disabling a package; active quantities therefore start
# at one.  The common distance is measured from the player's territory border,
# so zero preserves the native start-border placement.
START_BONUS_DISTANCE_MIN = 0
START_BONUS_DISTANCE_MAX = 512
START_BONUS_FORCE_EXTENDED_DEFAULT = False
START_BONUS_COUNT_MIN = 1
START_BONUS_COUNT_MAX = 1000
START_SWAMP_RADIUS_MIN = 1
START_SWAMP_RADIUS_MAX = 16
START_SWAMP_RADIUS_DEFAULT = 2
START_SWAMP_SHAPES = ("native", "hexagon")
START_FOREST_COUNT_MIN = 1
START_FOREST_COUNT_MAX = 100
START_FOREST_ADULT_DEFAULT = 30
START_FOREST_SAPLING_DEFAULT = 20
START_STONE_ANCHOR_MIN = 1
START_STONE_ANCHOR_MAX = 50
START_STONE_ANCHOR_DEFAULT = 15
START_STONE_AVERAGE_DEFAULT = 10.0
START_BONUS_STOCK_MIN = 1
START_BONUS_STOCK_MAX = 100000
START_BONUS_RADIUS_MIN = 1
START_BONUS_RADIUS_MAX = 16
# Start lakes retain the exact hexagon as a compatibility choice and add a
# bounded, rounded footprint inspired by the native water pass.  The lake
# shares the compact radius ceiling used by the other start-area zones.
START_LAKE_SHAPES = ("native", "hexagon")
# Mineral start zones have their own deliberately compact bounds.  The rocky
# panel exposes one common radius in equal mode and explicit surfaces in the
# other two modes.
START_ROCKY_RADIUS_MAX = 16
START_ROCKY_SHAPES = ("hexagon", "organic")
START_ROCKY_SURFACE_MODES = ("equal", "proportional", "custom")
START_ROCKY_CORE_CELLS_MIN = 1
# A complete HEX6 disc of radius 16 contains 1 + 3r(r+1) = 817 cells.  The
# public input uses the nearest round ceiling, 820, so the radius-16 disc is
# fully representable while custom/organic surfaces get a small headroom.
START_ROCKY_CORE_CELLS_MAX = 820
START_BONUS_WATER_PROXIMITY_MIN = 0
START_BONUS_WATER_PROXIMITY_MAX = 4096
START_BONUS_FISH_FILL_MIN = 0.0
START_BONUS_FISH_FILL_MAX = 100.0
START_BONUS_RIVER_TARGET_MIN = 1
START_BONUS_RIVER_TARGET_MAX = 6


def rocky_total_cells_max(active_count: int) -> int:
    """Return the total-core ceiling for the currently active minerals."""

    count = max(0, min(3, int(active_count)))
    return START_ROCKY_CORE_CELLS_MAX * count


def rocky_equal_core_cells(radius: int) -> int:
    """Return the exact HEX6 disc surface for one equal-mode zone."""

    radius = max(START_BONUS_RADIUS_MIN, min(START_ROCKY_RADIUS_MAX, int(radius)))
    return 1 + 3 * radius * (radius + 1)


def rocky_equivalent_radius(
    total: int,
    active_count: int,
    fallback: int = 4,
) -> int:
    """Return the nearest common radius represented by a total surface.

    Proportional and custom modes can express totals that are not exact sums
    of equal HEX6 discs.  The UI keeps a disabled common-radius indicator in
    those modes so a later switch to equal mode has a deterministic, nearby
    radius instead of restoring an unrelated stale value.
    """

    count = max(0, min(3, int(active_count)))
    if count <= 0:
        return max(START_BONUS_RADIUS_MIN, min(START_ROCKY_RADIUS_MAX, int(fallback)))
    bounded_total = max(
        count * START_ROCKY_CORE_CELLS_MIN,
        min(rocky_total_cells_max(count), int(round(float(total)))),
    )
    target_per_zone = bounded_total / count
    return min(
        range(START_BONUS_RADIUS_MIN, START_ROCKY_RADIUS_MAX + 1),
        key=lambda radius: (abs(rocky_equal_core_cells(radius) - target_per_zone), radius),
    )

# Rivers use the existing native attempt loop.  The public value changes only
# the chance that a native attempt is accepted; the hexagonal route, length
# rules, water connection and cleanup remain engine invariants.
RIVER_RATE_MIN = 0.0
RIVER_RATE_MAX = 500.0
RIVER_RATE_STEP = 1.0

# Décorations are exposed as independent appearance rates.  The catalogue is
# the shared static-object vocabulary already used by the Legacy and Upgraded
# content passes; IDs and terrain supports stay implementation details.
DECORATION_RATE_MIN = 0.0
DECORATION_RATE_MAX = 500.0
# The current Upgraded calibration is the shared reference for a non-zero
# Custom reef rate, including when the base profile is Legacy.
UPGRADED_REEF_TARGET_768 = 20
DECORATION_FAMILY_KEYS = (
    "big_stones",
    "decorative_stones",
    "border_stones",
    "small_stones",
    "bushes",
    "cacti",
    "dead_trees",
    "graves",
    "skeletons",
    "small_bushes",
    "small_flowers",
    "small_plants",
    "stumps",
    "toadstools",
    "wrecks",
    "reeds",
    "reefs",
)
DECORATION_FAMILY_SPECS = {
    "big_stones": {"ids": (1, 2, 3, 4, 5, 6, 7, 8), "support_ids": (16,)},
    "decorative_stones": {"ids": (9, 10, 11, 12), "support_ids": (16,)},
    "border_stones": {"ids": (13, 14, 15, 16, 17, 18, 19, 20), "support_ids": (16,)},
    "small_stones": {"ids": (21, 22, 23, 24, 25, 26, 27, 28), "support_ids": (16,)},
    "bushes": {"ids": (57, 58, 59, 60, 61), "support_ids": (16,)},
    "cacti": {"ids": (45, 46, 47, 48), "support_ids": (64,)},
    "dead_trees": {"ids": (43, 44), "support_ids": (64,)},
    "graves": {"ids": (34,), "support_ids": (16,)},
    "skeletons": {"ids": (49,), "support_ids": (64,)},
    "small_bushes": {"ids": (53, 54, 55, 56), "support_ids": (16,)},
    "small_flowers": {"ids": (50, 51, 52), "support_ids": (16,)},
    "small_plants": {"ids": (35, 36, 37), "support_ids": (16,)},
    "stumps": {"ids": (41, 42), "support_ids": (16,)},
    "toadstools": {"ids": (38, 39, 40), "support_ids": (16,)},
    "wrecks": {"ids": (29, 30, 31, 32, 33), "support_ids": (48,)},
    "reeds": {"ids": (62, 63, 64, 65, 66, 67), "support_ids": (80,)},
    # Reefs use a special open-deep-water test rather than a single support ID.
    "reefs": {"ids": (111, 112, 113, 114), "support_ids": ()},
}


def _number(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)
    return number


def _clamp(value: Any, low: float, high: float, default: float) -> float:
    return min(high, max(low, _number(value, default)))


def _integer(value: Any, low: int, high: int, default: int) -> int:
    return int(round(_clamp(value, low, high, default)))


def _profile_family_shares(profile: Mapping[str, Any]) -> dict[str, float]:
    minerals = profile.get("minerals", {})
    raw_shares = minerals.get("shares", {}) if isinstance(minerals, Mapping) else {}
    if isinstance(raw_shares, Mapping) and any(str(key) in raw_shares for _, key in MINERAL_SPECS):
        values = {
            key: max(0.0, _number(raw_shares.get(str(family), 0.0), 0.0))
            for key, family in MINERAL_SPECS
        }
    else:
        families = minerals.get("families", {}) if isinstance(minerals, Mapping) else {}
        values = {
            key: max(
                0.0,
                _number(
                    families.get(str(family), {}).get("cells", 0.0)
                    if isinstance(families, Mapping)
                    and isinstance(families.get(str(family), {}), Mapping)
                    else 0.0,
                    0.0,
                ),
            )
            for key, family in MINERAL_SPECS
        }
    total = sum(values.values())
    if total <= 0:
        return {key: 20.0 for key in MINERAL_KEYS}
    # Keep the profile calibration precise internally.  The native Upgraded
    # routine stores the family shares as fractions with five decimal places;
    # rounding them to one decimal here changes the integer cell targets and
    # makes an otherwise identical Custom profile diverge from Upgraded.
    return {key: values[key] / total * 100.0 for key in MINERAL_KEYS}


def _profile_section(profile: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    """Read a content section from either active or compatibility profiles."""

    direct = profile.get(key)
    if isinstance(direct, Mapping):
        return direct
    legacy_content = profile.get("legacy_content", {})
    if isinstance(legacy_content, Mapping):
        nested = legacy_content.get(key, {})
        if isinstance(nested, Mapping):
            return nested
    return {}


def _profile_start_bonus(profile: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    bonuses = profile.get("start_bonus", {})
    if not isinstance(bonuses, Mapping):
        return {}
    value = bonuses.get(key, {})
    return value if isinstance(value, Mapping) else {}


def _half_step(value: Any, low: float, high: float, default: float) -> float:
    """Clamp a quantity to the half-unit precision exposed by the editor."""

    bounded = _clamp(value, low, high, default)
    snapped = math.floor(bounded / STONE_QUANTITY_STEP + 0.5) * STONE_QUANTITY_STEP
    return min(float(high), max(float(low), float(snapped)))


def _stone_average_quantity(profile: Mapping[str, Any]) -> float:
    """Return the readable mean of the active profile's stone stock."""

    stones = _profile_section(profile, "building_stones")
    anchors = _number(stones.get("global_anchor_target", stones.get("global_anchor_target_768", 0)), 0)
    exhausted = _number(stones.get("global_exhausted_anchor_target", 0), 0)
    active = max(1.0, anchors - exhausted)
    stock = _number(stones.get("global_stock_target", stones.get("global_stock_target_768", 0)), 0)
    return _half_step(
        stock / active,
        STONE_QUANTITY_MINIMUM,
        STONE_QUANTITY_MAXIMUM,
        float(STONE_QUANTITY_MINIMUM),
    )


def default_sections(profile: Mapping[str, Any], base_mode: str) -> dict[str, Any]:
    """Build readable controls from a built-in profile.

    These defaults are only materialized when the user first edits a semantic
    control.  An untouched Custom configuration continues to use the exact
    built-in profile, preserving the validated baseline.
    """

    minerals = profile.get("minerals", {})
    fish = profile.get("fish", {})
    has_fish = (
        bool(int(_number(fish.get("target_cells", 32313), 32313)))
        if isinstance(fish, Mapping)
        else True
    )
    mode = str(base_mode)
    if mode == "legacy":
        # The active native Legacy profile stores its mineral calibration in a
        # separate generation profile.  The retained compatibility JSON does
        # not expose that field, so use the measured native occupancy rather
        # than its historical procedural 80.08% placeholder.
        legacy_resources = profile.get("legacy_content", {}).get("resources", {})
        occupancy = _number(
            legacy_resources.get("mineral_mountain_occupancy_target", 0.53)
            if isinstance(legacy_resources, Mapping)
            else 0.53,
            0.53,
        )
        resource_mean = LEGACY_RESOURCE_MEAN
        fill_default = LEGACY_FISH_FILL_PERCENT if has_fish else 0.0
        near_shore = False
    else:
        occupancy = _number(
            minerals.get("rocky_accessible_occupancy_target", 0.9)
            if isinstance(minerals, Mapping)
            else 0.9,
            0.9,
        )
        # This is the default for the direct coastal-band control.  The old
        # four-band calibration is historical and no longer drives placement.
        resource_mean = UPGRADED_RESOURCE_MEAN
        fill_default = UPGRADED_FISH_FILL_PERCENT if has_fish else 0.0
        near_shore = True
    trees = _profile_section(profile, "trees")
    stones = _profile_section(profile, "building_stones")
    adult_target = _number(
        trees.get("adult_global_target", trees.get("grass_adult_target_768", 0)),
        0.0,
    )
    forest_share = _number(trees.get("adult_cluster_share"), 0.0) * 100.0
    forest_enabled = "adult_cluster_share" in trees and forest_share > 0.0
    forest_centers = max(1, int(_number(trees.get("forest_centers", 1), 1)))
    forest_average = (
        adult_target * forest_share / 100.0 / forest_centers
        if forest_enabled and adult_target > 0
        else 1.0
    )
    sapling_target = _number(
        trees.get("small_tree_target", trees.get("small_tree_target_768", 0)),
        0.0,
    )
    saplings_enabled = sapling_target > 0.0
    saplings_separate = bool(trees.get("small_tree_separate_pool", saplings_enabled))
    sapling_quota = (
        sapling_target / adult_target * 100.0
        if saplings_separate and adult_target > 0
        else 0.0
    )
    sapling_global_share = (
        sapling_target / (adult_target + sapling_target) * 100.0
        if saplings_enabled and not saplings_separate and adult_target + sapling_target > 0
        else 0.0
    )
    sapling_placement = "forests_only" if forest_enabled and saplings_enabled else "everywhere"
    stone_cluster_share = (
        _number(stones.get("cluster_share"), 0.0) * 100.0
        if "cluster_share" in stones
        else 0.0
    )
    stone_average = _stone_average_quantity(profile)
    stone_group_average = _number(stones.get("cluster_typical_anchors"), 1.0)
    terrain_enabled = {
        key: not (key == "mud" and mode != "legacy")
        for key in TERRAIN_FAMILY_KEYS
    }

    start_forest_cfg = _profile_start_bonus(profile, "forest")
    start_stone_cfg = _profile_start_bonus(profile, "building_stones")
    start_swamp_cfg = _profile_start_bonus(profile, "mini_swamp")
    start_rocky_cfg = _profile_start_bonus(profile, "rocky_minerals")
    start_lake_cfg = _profile_start_bonus(profile, "lake_fish_river")
    start_distance = _integer(
        start_forest_cfg.get("distance_from_border", 0),
        START_BONUS_DISTANCE_MIN,
        START_BONUS_DISTANCE_MAX,
        0,
    )
    # Start-forest size is derived by the engines from the requested adult +
    # sapling counts and the common tree spacing.  The former arbitrary
    # radius controls remain accepted in old serialized payloads but are not
    # part of the semantic model anymore.
    start_forest_adults = _integer(
        START_FOREST_ADULT_DEFAULT,
        START_FOREST_COUNT_MIN,
        START_FOREST_COUNT_MAX,
        START_FOREST_ADULT_DEFAULT,
    )
    start_forest_saplings = _integer(
        START_FOREST_SAPLING_DEFAULT,
        START_FOREST_COUNT_MIN,
        START_FOREST_COUNT_MAX,
        START_FOREST_SAPLING_DEFAULT,
    )
    start_stone_anchors = _integer(
        start_stone_cfg.get("anchors_per_player", START_STONE_ANCHOR_DEFAULT),
        START_STONE_ANCHOR_MIN,
        START_STONE_ANCHOR_MAX,
        START_STONE_ANCHOR_DEFAULT,
    )
    raw_start_stone_average = start_stone_cfg.get("average_quantity")
    if raw_start_stone_average is None and "stock_units_per_player" in start_stone_cfg:
        raw_start_stone_average = (
            _number(start_stone_cfg.get("stock_units_per_player"), 0.0)
            / max(1, start_stone_anchors)
        )
    start_stone_average = _half_step(
        raw_start_stone_average,
        STONE_QUANTITY_MINIMUM,
        STONE_QUANTITY_MAXIMUM,
        START_STONE_AVERAGE_DEFAULT,
    )
    start_stone_stock = math.floor(start_stone_anchors * start_stone_average + 0.5)
    start_swamp_radius = _integer(
        start_swamp_cfg.get("radius", START_SWAMP_RADIUS_DEFAULT),
        START_SWAMP_RADIUS_MIN,
        START_SWAMP_RADIUS_MAX,
        START_SWAMP_RADIUS_DEFAULT,
    )
    start_swamp_shape = str(
        start_swamp_cfg.get("shape", "native")
    ).lower()
    if start_swamp_shape not in START_SWAMP_SHAPES:
        start_swamp_shape = "native"
    rocky_zones = start_rocky_cfg.get("zones", {})
    rocky_zones = rocky_zones if isinstance(rocky_zones, Mapping) else {}
    rocky_families = {
        key: bool(
            isinstance(value, Mapping)
            and value.get("enabled", True)
        )
        for key, value in (
            ("coal", rocky_zones.get("coal", {})),
            ("iron", rocky_zones.get("iron", {})),
            ("gold", rocky_zones.get("gold", {})),
        )
    }
    start_rocky_radius_min = _integer(
        start_rocky_cfg.get("radius_min", 3),
        START_BONUS_RADIUS_MIN,
        START_ROCKY_RADIUS_MAX,
        3,
    )
    start_rocky_radius_max = _integer(
        start_rocky_cfg.get("radius_max", 5),
        start_rocky_radius_min,
        START_ROCKY_RADIUS_MAX,
        max(start_rocky_radius_min, 5),
    )
    rocky_shape = str(start_rocky_cfg.get("shape", "hexagon")).lower()
    if rocky_shape not in START_ROCKY_SHAPES:
        rocky_shape = "hexagon"
    rocky_surface_mode = str(
        start_rocky_cfg.get(
            "surface_mode",
            start_rocky_cfg.get("allocation_mode", "equal"),
        )
    ).lower()
    if rocky_surface_mode in {"share", "shares", "prorata", "pro_rata", "proportional"}:
        rocky_surface_mode = "proportional"
    elif rocky_surface_mode in {"per_mineral", "per_family", "customized"}:
        rocky_surface_mode = "custom"
    if rocky_surface_mode not in START_ROCKY_SURFACE_MODES:
        rocky_surface_mode = "equal"
    if rocky_surface_mode == "equal":
        # Keep the old min/max keys in the serialized contract for backwards
        # compatibility, but make equal mode a single radius for every zone.
        # A midpoint is the least surprising migration for older 3..5
        # profiles that did not yet have a common-radius field.
        equal_radius = _integer(
            start_rocky_cfg.get(
                "radius",
                int(round((start_rocky_radius_min + start_rocky_radius_max) / 2.0)),
            ),
            START_BONUS_RADIUS_MIN,
            START_ROCKY_RADIUS_MAX,
            4,
        )
        start_rocky_radius_min = equal_radius
        start_rocky_radius_max = equal_radius
    default_radius = int(round((start_rocky_radius_min + start_rocky_radius_max) / 2.0))
    default_core_cells = 1 + 3 * default_radius * (default_radius + 1)
    profile_quantity_defaults = (
        minerals.get("average_quantity", {})
        if isinstance(minerals, Mapping) and isinstance(minerals.get("average_quantity", {}), Mapping)
        else {}
    )
    rocky_core_defaults = start_rocky_cfg.get("core_cells", {})
    rocky_core_defaults = rocky_core_defaults if isinstance(rocky_core_defaults, Mapping) else {}
    start_lake_radius_min = _integer(
        start_lake_cfg.get("radius_min", 7),
        START_BONUS_RADIUS_MIN,
        START_BONUS_RADIUS_MAX,
        7,
    )
    start_lake_radius_max = _integer(
        start_lake_cfg.get("radius_max", 9),
        start_lake_radius_min,
        START_BONUS_RADIUS_MAX,
        max(start_lake_radius_min, 9),
    )

    return {
        "minerals": {
            "algorithm": mode if mode in MINERAL_ALGORITHMS else "upgraded",
            "occupancy_percent": round(_clamp(occupancy * 100.0, 0.0, 100.0, 90.0), 1),
            "shares": _profile_family_shares(profile),
            "size_variation": "normal",
            "average_quantity": {key: resource_mean for key in MINERAL_KEYS},
        },
        "fish": {
            "fill_percent": fill_default,
            "average_quantity": resource_mean,
            "near_shore": near_shore,
            "band_thickness": DEFAULT_FISH_BAND_THICKNESS,
        },
        "rivers": {
            "rate_percent": 100.0,
        },
        "terrains": {
            key: {
                "enabled": enabled,
                "rate_percent": 100.0 if enabled else 0.0,
            }
            for key, enabled in terrain_enabled.items()
        },
        "trees": {
            "base_quota_percent": 100.0,
            "saplings": {
                "enabled": saplings_enabled,
                "in_global_pool": (not saplings_separate) if saplings_enabled else False,
                "global_share_percent": round(
                    _clamp(
                        sapling_global_share,
                        SEMANTIC_SHARE_MIN,
                        SEMANTIC_SHARE_MAX,
                        0.0,
                    ),
                    1,
                ),
                "quota_percent": round(
                    _clamp(sapling_quota, SEMANTIC_DENSITY_MIN, SEMANTIC_DENSITY_MAX, 0.0),
                    1,
                ),
                "placement": sapling_placement,
            },
            "forests": {
                "enabled": forest_enabled,
                "share_percent": round(
                    _clamp(forest_share, SEMANTIC_SHARE_MIN, SEMANTIC_SHARE_MAX, 0.0), 1
                ),
                "trees_per_forest": round(
                    _clamp(forest_average, FOREST_TREE_COUNT_MIN, FOREST_TREE_COUNT_MAX, 1.0),
                    1,
                ),
                "tree_count_variation_percent": 0.0,
            },
            "palm_quota_percent": 100.0,
        },
        "building_stones": {
            "anchor_density_percent": 100.0,
            "average_quantity": stone_average,
            "groups": {
                "enabled": stone_cluster_share > 0,
                "share_percent": round(
                    _clamp(stone_cluster_share, SEMANTIC_SHARE_MIN, SEMANTIC_SHARE_MAX, 30.0), 1
                ),
                "stones_per_group": round(
                    _clamp(stone_group_average, STONE_GROUP_COUNT_MIN, STONE_GROUP_COUNT_MAX, 1.0), 1
                ),
                "stone_count_variation_percent": 0.0,
            },
        },
        # Start-area parameters are separate from the global content sections.
        # The package checkboxes remain the activation switches; these values
        # describe the active package and are applied only by the Upgraded
        # start-content pass.
        "start_bonus": {
            "distance_from_border": start_distance,
            "force_extended_radius": False,
            "forest": {
                "enabled": bool(start_forest_cfg.get("per_player", True)),
                "adult_trees_per_player": start_forest_adults,
                "saplings_per_player": start_forest_saplings,
                "shape": "native",
            },
            "building_stones": {
                "enabled": bool(start_stone_anchors > 0 and start_stone_stock > 0),
                "anchors_per_player": start_stone_anchors,
                "stock_units_per_player": start_stone_stock,
                "average_quantity": start_stone_average,
                "quantity_min": STONE_QUANTITY_MINIMUM,
                "quantity_max": STONE_QUANTITY_MAXIMUM,
                "shape": "native",
            },
            "mini_swamp": {
                "enabled": bool(start_swamp_cfg.get("per_player", True)),
                "radius": start_swamp_radius,
                "shape": start_swamp_shape,
            },
            "rocky_minerals": {
                "enabled": bool(any(rocky_families.values())),
                "radius_min": start_rocky_radius_min,
                "radius_max": start_rocky_radius_max,
                "shape": rocky_shape,
                "surface_mode": rocky_surface_mode,
                "total_core_cells": max(
                    START_ROCKY_CORE_CELLS_MIN,
                    min(
                        rocky_total_cells_max(sum(rocky_families.values())),
                        int(
                            _number(
                                start_rocky_cfg.get(
                                    "total_core_cells",
                                    default_core_cells * sum(rocky_families.values()),
                                ),
                                default_core_cells * sum(rocky_families.values()),
                            )
                        ),
                    ),
                ),
                "coal": {
                    "enabled": rocky_families["coal"],
                    "core_cells": _integer(
                        rocky_core_defaults.get("coal", default_core_cells),
                        START_ROCKY_CORE_CELLS_MIN,
                        START_ROCKY_CORE_CELLS_MAX,
                        default_core_cells,
                    ),
                    "average_quantity": _integer(
                        profile_quantity_defaults.get("coal", resource_mean),
                        RESOURCE_MINIMUM,
                        RESOURCE_MAXIMUM,
                        resource_mean,
                    ),
                    "quantity_mode": "global",
                },
                "iron": {
                    "enabled": rocky_families["iron"],
                    "core_cells": _integer(
                        rocky_core_defaults.get("iron", default_core_cells),
                        START_ROCKY_CORE_CELLS_MIN,
                        START_ROCKY_CORE_CELLS_MAX,
                        default_core_cells,
                    ),
                    "average_quantity": _integer(
                        profile_quantity_defaults.get("iron", resource_mean),
                        RESOURCE_MINIMUM,
                        RESOURCE_MAXIMUM,
                        resource_mean,
                    ),
                    "quantity_mode": "global",
                },
                "gold": {
                    "enabled": rocky_families["gold"],
                    "core_cells": _integer(
                        rocky_core_defaults.get("gold", default_core_cells),
                        START_ROCKY_CORE_CELLS_MIN,
                        START_ROCKY_CORE_CELLS_MAX,
                        default_core_cells,
                    ),
                    "average_quantity": _integer(
                        profile_quantity_defaults.get("gold", resource_mean),
                        RESOURCE_MINIMUM,
                        RESOURCE_MAXIMUM,
                        resource_mean,
                    ),
                    "quantity_mode": "global",
                },
            },
            "lake_fish_river": {
                "enabled": bool(start_lake_radius_max > 0),
                "radius_min": start_lake_radius_min,
                "radius_max": start_lake_radius_max,
                "shape": "native",
                "water_proximity_from_territory_border": _integer(
                    start_lake_cfg.get("water_proximity_from_territory_border", 150),
                    START_BONUS_WATER_PROXIMITY_MIN,
                    START_BONUS_WATER_PROXIMITY_MAX,
                    150,
                ),
                "river_target_per_lake": _integer(
                    start_lake_cfg.get("river_target", 1),
                    START_BONUS_RIVER_TARGET_MIN,
                    START_BONUS_RIVER_TARGET_MAX,
                    1,
                ),
                "fish_fill_percent": round(
                    _clamp(
                        start_lake_cfg.get("fish_fill_percent", 50.0),
                        START_BONUS_FISH_FILL_MIN,
                        START_BONUS_FISH_FILL_MAX,
                        50.0,
                    ),
                    1,
                ),
            },
        },
        # Legacy has no native reef quota.  Keep that distinction visible in
        # the semantic editor: 0% means the selected Legacy behaviour,
        # whereas Upgraded's 100% means its currently calibrated reef quota.
        "decorations": {
            key: (0.0 if key == "reefs" and mode == "legacy" else 100.0)
            for key in DECORATION_FAMILY_KEYS
        },
        "objects": {
            "grass_compatible_on_dry_and_details": False,
        },
    }


def normalize_sections(value: Mapping[str, Any] | None, *, fallback: Mapping[str, Any]) -> dict[str, Any]:
    """Return a complete, bounded semantic configuration.

    Values are clamped to real format/game limits instead of causing a
    generation lock.  Percentages remain independently editable; their
    mineral pool is normalized by the placement routine when necessary.
    """

    source = value if isinstance(value, Mapping) else {}
    base = deepcopy(dict(fallback))
    raw_minerals = source.get("minerals", {})
    raw_minerals = raw_minerals if isinstance(raw_minerals, Mapping) else {}
    minerals = base["minerals"]
    algorithm = str(raw_minerals.get("algorithm", minerals["algorithm"]))
    minerals["algorithm"] = algorithm if algorithm in MINERAL_ALGORITHMS else minerals["algorithm"]
    minerals["occupancy_percent"] = round(
        _clamp(
            raw_minerals.get("occupancy_percent", minerals["occupancy_percent"]),
            0.0,
            100.0,
            minerals["occupancy_percent"],
        ),
        1,
    )
    raw_shares = raw_minerals.get("shares", {})
    raw_shares = raw_shares if isinstance(raw_shares, Mapping) else {}
    minerals["shares"] = {
        key: _clamp(
            raw_shares.get(key, minerals["shares"].get(key, 0.0)),
            0.0,
            100.0,
            0.0,
        )
        for key in MINERAL_KEYS
    }
    variation = str(raw_minerals.get("size_variation", minerals["size_variation"]))
    minerals["size_variation"] = variation if variation in SIZE_VARIATIONS else "normal"
    raw_quantities = raw_minerals.get("average_quantity", {})
    raw_quantities = raw_quantities if isinstance(raw_quantities, Mapping) else {}
    minerals["average_quantity"] = {
        key: _integer(
            raw_quantities.get(key, minerals["average_quantity"].get(key, UPGRADED_RESOURCE_MEAN)),
            RESOURCE_MINIMUM,
            RESOURCE_MAXIMUM,
            int(minerals["average_quantity"].get(key, UPGRADED_RESOURCE_MEAN)),
        )
        for key in MINERAL_KEYS
    }

    raw_fish = source.get("fish", {})
    raw_fish = raw_fish if isinstance(raw_fish, Mapping) else {}
    fish = base["fish"]
    fish["fill_percent"] = round(
        _clamp(raw_fish.get("fill_percent", fish["fill_percent"]), 0.0, 100.0, fish["fill_percent"]),
        1,
    )
    fish["average_quantity"] = _integer(
        raw_fish.get("average_quantity", fish["average_quantity"]),
        RESOURCE_MINIMUM,
        RESOURCE_MAXIMUM,
        int(fish["average_quantity"]),
    )
    fish["near_shore"] = bool(raw_fish.get("near_shore", fish["near_shore"]))
    fish["band_thickness"] = _integer(
        raw_fish.get("band_thickness", fish.get("band_thickness", DEFAULT_FISH_BAND_THICKNESS)),
        1,
        4096,
        DEFAULT_FISH_BAND_THICKNESS,
    )

    fallback_rivers = base.setdefault("rivers", {"rate_percent": 100.0})
    raw_rivers = source.get("rivers", {})
    raw_rivers = raw_rivers if isinstance(raw_rivers, Mapping) else {}
    fallback_rivers["rate_percent"] = round(
        _clamp(
            raw_rivers.get("rate_percent", fallback_rivers.get("rate_percent", 100.0)),
            RIVER_RATE_MIN,
            RIVER_RATE_MAX,
            100.0,
        ),
        1,
    )

    fallback_terrains = base.setdefault(
        "terrains",
        {
            key: {"enabled": True, "rate_percent": 100.0}
            for key in TERRAIN_FAMILY_KEYS
        },
    )
    raw_terrains = source.get("terrains", {})
    raw_terrains = raw_terrains if isinstance(raw_terrains, Mapping) else {}
    for terrain_key in TERRAIN_FAMILY_KEYS:
        default_entry = fallback_terrains.setdefault(
            terrain_key,
            {"enabled": True, "rate_percent": 100.0},
        )
        raw_entry = raw_terrains.get(terrain_key, {})
        if isinstance(raw_entry, Mapping):
            enabled = bool(raw_entry.get("enabled", default_entry.get("enabled", True)))
            raw_rate = raw_entry.get("rate_percent", default_entry.get("rate_percent", 100.0))
        else:
            enabled = True
            raw_rate = raw_entry
        bounded_rate = _clamp(
            raw_rate,
            TERRAIN_RATE_MIN,
            TERRAIN_RATE_MAX,
            float(default_entry.get("rate_percent", 100.0)),
        )
        if enabled:
            bounded_rate = max(TERRAIN_ENABLED_RATE_MIN, bounded_rate)
        fallback_terrains[terrain_key] = {
            "enabled": enabled,
            "rate_percent": round(bounded_rate, 1),
        }

    fallback_trees = base.setdefault("trees", {})
    raw_trees = source.get("trees", {})
    raw_trees = raw_trees if isinstance(raw_trees, Mapping) else {}
    # Migrate the short-lived flat schema while reading an in-progress
    # candidate.  The normalized result always uses the semantic tree model.
    if "base_quota_percent" not in raw_trees and "adult_density_percent" in raw_trees:
        raw_trees = dict(raw_trees)
        raw_trees["base_quota_percent"] = raw_trees["adult_density_percent"]
    if "forests" not in raw_trees and "forest_share_percent" in raw_trees:
        raw_trees = dict(raw_trees)
        raw_trees["forests"] = {
            "enabled": float(raw_trees["forest_share_percent"]) > 0,
            "share_percent": raw_trees["forest_share_percent"],
        }
    if "saplings" not in raw_trees and "sapling_density_percent" in raw_trees:
        raw_trees = dict(raw_trees)
        raw_trees["saplings"] = {
            "enabled": float(raw_trees["sapling_density_percent"]) > 0,
            "in_global_pool": False,
            "quota_percent": raw_trees["sapling_density_percent"],
            "placement": "forests_only",
        }
    if "palm_quota_percent" not in raw_trees and "palm_density_percent" in raw_trees:
        raw_trees = dict(raw_trees)
        raw_trees["palm_quota_percent"] = raw_trees["palm_density_percent"]
    fallback_trees.setdefault("base_quota_percent", 100.0)
    fallback_trees.setdefault(
        "saplings",
        {"enabled": False, "in_global_pool": False, "global_share_percent": 0.0, "quota_percent": 100.0, "placement": "everywhere"},
    )
    fallback_trees.setdefault(
        "forests",
        {"enabled": False, "share_percent": 0.0, "trees_per_forest": 1.0, "tree_count_variation_percent": 0.0},
    )
    fallback_trees.setdefault("palm_quota_percent", 100.0)
    fallback_trees["base_quota_percent"] = round(
        _clamp(raw_trees.get("base_quota_percent", fallback_trees["base_quota_percent"]), SEMANTIC_DENSITY_MIN, TREE_QUOTA_MAX, 100.0),
        1,
    )
    saplings = fallback_trees["saplings"]
    raw_saplings = raw_trees.get("saplings", {})
    raw_saplings = raw_saplings if isinstance(raw_saplings, Mapping) else {}
    saplings["enabled"] = bool(raw_saplings.get("enabled", saplings.get("enabled", False)))
    saplings["in_global_pool"] = bool(raw_saplings.get("in_global_pool", saplings.get("in_global_pool", False)))
    saplings["global_share_percent"] = round(_clamp(raw_saplings.get("global_share_percent", saplings.get("global_share_percent", 0.0)), SEMANTIC_SHARE_MIN, SEMANTIC_SHARE_MAX, 0.0), 1)
    saplings["quota_percent"] = round(_clamp(raw_saplings.get("quota_percent", saplings.get("quota_percent", 100.0)), SEMANTIC_DENSITY_MIN, SEMANTIC_DENSITY_MAX, 100.0), 1)
    placement = str(raw_saplings.get("placement", saplings.get("placement", "everywhere")))
    saplings["placement"] = placement if placement in TREE_PLACEMENTS else "everywhere"
    forests = fallback_trees["forests"]
    raw_forests = raw_trees.get("forests", {})
    raw_forests = raw_forests if isinstance(raw_forests, Mapping) else {}
    forests["enabled"] = bool(raw_forests.get("enabled", forests.get("enabled", False)))
    forests["share_percent"] = round(_clamp(raw_forests.get("share_percent", forests.get("share_percent", 0.0)), SEMANTIC_SHARE_MIN, SEMANTIC_SHARE_MAX, 0.0), 1)
    forests["trees_per_forest"] = round(_clamp(raw_forests.get("trees_per_forest", forests.get("trees_per_forest", 1.0)), FOREST_TREE_COUNT_MIN, FOREST_TREE_COUNT_MAX, 1.0), 1)
    forests["tree_count_variation_percent"] = round(_clamp(raw_forests.get("tree_count_variation_percent", forests.get("tree_count_variation_percent", 0.0)), FOREST_TREE_VARIATION_MIN, FOREST_TREE_VARIATION_MAX, 0.0), 1)
    fallback_trees["palm_quota_percent"] = round(_clamp(raw_trees.get("palm_quota_percent", fallback_trees.get("palm_quota_percent", 100.0)), SEMANTIC_DENSITY_MIN, TREE_QUOTA_MAX, 100.0), 1)

    fallback_stones = base.setdefault(
        "building_stones",
        {
            "anchor_density_percent": 100.0,
            "average_quantity": _stone_average_quantity(fallback),
            "groups": {
                "enabled": True,
                "share_percent": 30.0,
                "stones_per_group": 1.0,
                "stone_count_variation_percent": 0.0,
            },
        },
    )
    raw_stones = source.get("building_stones", {})
    raw_stones = raw_stones if isinstance(raw_stones, Mapping) else {}
    fallback_stones["anchor_density_percent"] = round(
        _clamp(raw_stones.get("anchor_density_percent", fallback_stones.get("anchor_density_percent", 100.0)),
               SEMANTIC_DENSITY_MIN, SEMANTIC_DENSITY_MAX, 100.0), 1)
    default_average = float(fallback_stones.get("average_quantity", _stone_average_quantity(fallback)))
    legacy_stock_percent = raw_stones.get("stock_percent")
    average_value = raw_stones.get("average_quantity")
    if average_value is None and legacy_stock_percent is not None:
        average_value = default_average * _clamp(legacy_stock_percent, 0.0, 200.0, 100.0) / 100.0
    fallback_stones["average_quantity"] = _half_step(
        default_average if average_value is None else average_value,
        STONE_QUANTITY_MINIMUM,
        STONE_QUANTITY_MAXIMUM,
        default_average,
    )
    default_groups = fallback_stones.setdefault("groups", {})
    raw_groups = raw_stones.get("groups", {})
    raw_groups = raw_groups if isinstance(raw_groups, Mapping) else {}
    legacy_share = raw_stones.get("cluster_share_percent")
    legacy_enabled = raw_stones.get("groups_enabled")
    enabled_default = default_groups.get("enabled", False)
    if legacy_enabled is None and legacy_share is not None:
        enabled_default = _number(legacy_share, 0.0) > 0.0
    default_groups["enabled"] = bool(
        raw_groups.get("enabled", legacy_enabled if legacy_enabled is not None else enabled_default)
    )
    default_groups["share_percent"] = round(_clamp(
        raw_groups.get("share_percent", legacy_share if legacy_share is not None else default_groups.get("share_percent", 0.0)),
        SEMANTIC_SHARE_MIN, SEMANTIC_SHARE_MAX, 0.0), 1)
    default_groups["stones_per_group"] = round(_clamp(
        raw_groups.get("stones_per_group", default_groups.get("stones_per_group", 1.0)),
        STONE_GROUP_COUNT_MIN, STONE_GROUP_COUNT_MAX, 1.0), 1)
    default_groups["stone_count_variation_percent"] = round(_clamp(
        raw_groups.get("stone_count_variation_percent", default_groups.get("stone_count_variation_percent", 0.0)),
        STONE_GROUP_VARIATION_MIN, STONE_GROUP_VARIATION_MAX, 0.0), 1)

    fallback_start = base.setdefault("start_bonus", {})
    raw_start = source.get("start_bonus", {})
    raw_start = raw_start if isinstance(raw_start, Mapping) else {}
    fallback_start["distance_from_border"] = _integer(
        raw_start.get(
            "distance_from_border",
            fallback_start.get("distance_from_border", 0),
        ),
        START_BONUS_DISTANCE_MIN,
        START_BONUS_DISTANCE_MAX,
        0,
    )
    fallback_start["force_extended_radius"] = bool(
        raw_start.get(
            "force_extended_radius",
            fallback_start.get("force_extended_radius", START_BONUS_FORCE_EXTENDED_DEFAULT),
        )
    )

    def start_entry(key: str) -> tuple[dict[str, Any], Mapping[str, Any]]:
        default_entry = fallback_start.setdefault(key, {})
        if not isinstance(default_entry, dict):
            default_entry = {}
            fallback_start[key] = default_entry
        raw_entry = raw_start.get(key, {})
        return default_entry, raw_entry if isinstance(raw_entry, Mapping) else {}

    forest, raw_forest = start_entry("forest")
    forest["enabled"] = bool(raw_forest.get("enabled", forest.get("enabled", True)))
    forest["adult_trees_per_player"] = _integer(
        raw_forest.get(
            "adult_trees_per_player",
            forest.get("adult_trees_per_player", START_FOREST_ADULT_DEFAULT),
        ),
        START_FOREST_COUNT_MIN,
        START_FOREST_COUNT_MAX,
        START_FOREST_ADULT_DEFAULT,
    )
    forest["saplings_per_player"] = _integer(
        raw_forest.get(
            "saplings_per_player",
            forest.get("saplings_per_player", START_FOREST_SAPLING_DEFAULT),
        ),
        START_FOREST_COUNT_MIN,
        START_FOREST_COUNT_MAX,
        START_FOREST_SAPLING_DEFAULT,
    )
    # Former serialized radius controls are deliberately ignored.  Keeping the
    # normalized entry free of them prevents an old saved value from
    # accidentally regaining authority in a future engine pass.
    forest.pop("radius_min", None)
    forest.pop("radius_max", None)
    forest["shape"] = "native"

    start_stones, raw_start_stones = start_entry("building_stones")
    start_stones["enabled"] = bool(raw_start_stones.get("enabled", start_stones.get("enabled", True)))
    stone_anchors = _integer(
        raw_start_stones.get(
            "anchors_per_player",
            start_stones.get("anchors_per_player", START_STONE_ANCHOR_DEFAULT),
        ),
        START_STONE_ANCHOR_MIN,
        START_STONE_ANCHOR_MAX,
        START_STONE_ANCHOR_DEFAULT,
    )
    start_stones["anchors_per_player"] = stone_anchors
    stone_average_default = float(
        start_stones.get("average_quantity", START_STONE_AVERAGE_DEFAULT)
    )
    stone_average_value = _half_step(
        raw_start_stones.get("average_quantity", stone_average_default),
        STONE_QUANTITY_MINIMUM,
        STONE_QUANTITY_MAXIMUM,
        START_STONE_AVERAGE_DEFAULT,
    )
    start_stones["average_quantity"] = stone_average_value
    # Stock is always derived from the two visible controls.  A stale raw
    # stock or radius in an older preset must never override them.
    raw_stock = math.floor(stone_anchors * stone_average_value + 0.5)
    start_stones["stock_units_per_player"] = _integer(
        raw_stock,
        START_BONUS_STOCK_MIN,
        START_BONUS_STOCK_MAX,
        math.floor(START_STONE_ANCHOR_DEFAULT * START_STONE_AVERAGE_DEFAULT + 0.5),
    )
    start_stones["quantity_min"] = STONE_QUANTITY_MINIMUM
    start_stones["quantity_max"] = STONE_QUANTITY_MAXIMUM
    start_stones.pop("radius_min", None)
    start_stones.pop("radius_max", None)
    start_stones["shape"] = "native"

    swamp, raw_swamp = start_entry("mini_swamp")
    swamp["enabled"] = bool(raw_swamp.get("enabled", swamp.get("enabled", True)))
    raw_radius = raw_swamp.get("radius")
    if raw_radius is None:
        # Accept old serialized Custom profiles once, then immediately expose
        # the new radius-based schema.  A radius-2 core is the former 19-cell
        # default; larger legacy counts map to the first containing hex disc.
        legacy_cells = _integer(
            raw_swamp.get("cells_per_player", swamp.get("requested_cells", 19)),
            START_BONUS_COUNT_MIN,
            START_BONUS_COUNT_MAX,
            19,
        )
        raw_radius = 1
        while (1 + 3 * raw_radius * (raw_radius + 1)) < legacy_cells:
            raw_radius += 1
    swamp["radius"] = _integer(
        raw_radius,
        START_SWAMP_RADIUS_MIN,
        START_SWAMP_RADIUS_MAX,
        START_SWAMP_RADIUS_DEFAULT,
    )
    shape = str(raw_swamp.get("shape", swamp.get("shape", "native"))).lower()
    swamp["shape"] = shape if shape in START_SWAMP_SHAPES else "native"
    swamp.pop("cells_per_player", None)

    rocky, raw_rocky = start_entry("rocky_minerals")
    rocky["enabled"] = bool(raw_rocky.get("enabled", rocky.get("enabled", True)))
    rocky_min = _integer(
        raw_rocky.get("radius_min", rocky.get("radius_min", 3)),
        START_BONUS_RADIUS_MIN,
        START_ROCKY_RADIUS_MAX,
        3,
    )
    rocky["radius_min"] = rocky_min
    rocky["radius_max"] = _integer(
        raw_rocky.get("radius_max", rocky.get("radius_max", 5)),
        rocky_min,
        START_ROCKY_RADIUS_MAX,
        max(rocky_min, 5),
    )
    shape = str(raw_rocky.get("shape", rocky.get("shape", "hexagon"))).lower()
    rocky["shape"] = shape if shape in START_ROCKY_SHAPES else "hexagon"
    mode = str(
        raw_rocky.get(
            "surface_mode",
            raw_rocky.get("allocation_mode", rocky.get("surface_mode", "equal")),
        )
    ).lower()
    if mode in {"share", "shares", "prorata", "pro_rata", "proportional"}:
        mode = "proportional"
    elif mode in {"per_mineral", "per_family", "customized"}:
        mode = "custom"
    rocky["surface_mode"] = mode if mode in START_ROCKY_SURFACE_MODES else "equal"
    if rocky["surface_mode"] == "equal":
        equal_radius = _integer(
            raw_rocky.get(
                "radius",
                int(round((rocky_min + int(rocky.get("radius_max", 5))) / 2.0)),
            ),
            START_BONUS_RADIUS_MIN,
            START_ROCKY_RADIUS_MAX,
            4,
        )
        rocky_min = equal_radius
        rocky["radius_min"] = equal_radius
        rocky["radius_max"] = equal_radius
    default_core = int(
        rocky.get(
            "total_core_cells",
            1 + 3 * int(round((rocky_min + int(rocky.get("radius_max", 5))) / 2.0))
            * (int(round((rocky_min + int(rocky.get("radius_max", 5))) / 2.0)) + 1),
        )
    )
    raw_total = raw_rocky.get("total_core_cells", default_core * 3)
    rocky["total_core_cells"] = _integer(
        raw_total,
        START_ROCKY_CORE_CELLS_MIN,
        START_ROCKY_CORE_CELLS_MAX * 3,
        default_core * 3,
    )
    raw_top_areas = raw_rocky.get("core_cells", {})
    raw_top_areas = raw_top_areas if isinstance(raw_top_areas, Mapping) else {}
    for family in ("coal", "iron", "gold"):
        default_family = rocky.setdefault(family, {"enabled": True})
        if not isinstance(default_family, dict):
            default_family = {"enabled": True}
            rocky[family] = default_family
        raw_family = raw_rocky.get(family, {})
        raw_family = raw_family if isinstance(raw_family, Mapping) else {}
        default_family["enabled"] = bool(raw_family.get("enabled", default_family.get("enabled", True)))
        raw_area = raw_family.get(
            "core_cells",
            raw_family.get("surface", raw_top_areas.get(family, default_family.get("core_cells", 61))),
        )
        default_family["core_cells"] = _integer(
            raw_area,
            START_ROCKY_CORE_CELLS_MIN,
            START_ROCKY_CORE_CELLS_MAX,
            int(default_family.get("core_cells", 61)),
        )
        global_mean = minerals.get("average_quantity", {}).get(family, UPGRADED_RESOURCE_MEAN)
        default_mean = int(default_family.get("average_quantity", global_mean))
        raw_mean = raw_family.get("average_quantity", default_mean)
        raw_mode = str(raw_family.get("quantity_mode", default_family.get("quantity_mode", "global"))).lower()
        # The semantic default is linked to the global mineral control.  A
        # manually supplied value that differs from the materialized default
        # is treated as an explicit per-zone override, which keeps old JSON
        # payloads ergonomic while still allowing the global field to update
        # all zones at once.
        if raw_mode not in {"global", "custom", "override"}:
            raw_mode = "global"
        if raw_mode == "global" and raw_mean != default_mean:
            raw_mode = "custom"
        if raw_mode == "global" or raw_mean is None:
            raw_mean = global_mean
        default_family["average_quantity"] = _integer(
            raw_mean,
            RESOURCE_MINIMUM,
            RESOURCE_MAXIMUM,
            int(global_mean),
        )
        default_family["quantity_mode"] = "custom" if raw_mode == "custom" else "global"

    active_rocky_count = sum(
        bool(rocky[family].get("enabled", True))
        for family in ("coal", "iron", "gold")
    )
    rocky["total_core_cells"] = _integer(
        raw_total,
        START_ROCKY_CORE_CELLS_MIN,
        rocky_total_cells_max(active_rocky_count),
        default_core * max(1, active_rocky_count),
    )

    lake, raw_lake = start_entry("lake_fish_river")
    lake["enabled"] = bool(raw_lake.get("enabled", lake.get("enabled", True)))
    lake_min = _integer(
        raw_lake.get("radius_min", lake.get("radius_min", 7)),
        START_BONUS_RADIUS_MIN,
        START_BONUS_RADIUS_MAX,
        7,
    )
    lake["radius_min"] = lake_min
    lake["radius_max"] = _integer(
        raw_lake.get("radius_max", lake.get("radius_max", 9)),
        lake_min,
        START_BONUS_RADIUS_MAX,
        max(lake_min, 9),
    )
    lake_shape = str(raw_lake.get("shape", lake.get("shape", "native"))).lower()
    lake["shape"] = lake_shape if lake_shape in START_LAKE_SHAPES else "native"
    lake["water_proximity_from_territory_border"] = _integer(
        raw_lake.get(
            "water_proximity_from_territory_border",
            lake.get("water_proximity_from_territory_border", 150),
        ),
        START_BONUS_WATER_PROXIMITY_MIN,
        START_BONUS_WATER_PROXIMITY_MAX,
        150,
    )
    lake["river_target_per_lake"] = _integer(
        raw_lake.get("river_target_per_lake", lake.get("river_target_per_lake", 1)),
        START_BONUS_RIVER_TARGET_MIN,
        START_BONUS_RIVER_TARGET_MAX,
        1,
    )
    lake["fish_fill_percent"] = round(
        _clamp(
            raw_lake.get("fish_fill_percent", lake.get("fish_fill_percent", 50.0)),
            START_BONUS_FISH_FILL_MIN,
            START_BONUS_FISH_FILL_MAX,
            50.0,
        ),
        1,
    )

    fallback_decorations = base.setdefault(
        "decorations",
        {key: 100.0 for key in DECORATION_FAMILY_KEYS},
    )
    raw_decorations = source.get("decorations", {})
    raw_decorations = raw_decorations if isinstance(raw_decorations, Mapping) else {}
    for key in DECORATION_FAMILY_KEYS:
        fallback_decorations[key] = round(
            _clamp(
                raw_decorations.get(key, fallback_decorations.get(key, 100.0)),
                DECORATION_RATE_MIN,
                DECORATION_RATE_MAX,
                float(fallback_decorations.get(key, 100.0)),
            ),
            1,
        )
    fallback_objects = base.setdefault(
        "objects",
        {"grass_compatible_on_dry_and_details": False},
    )
    raw_objects = source.get("objects", {})
    raw_objects = raw_objects if isinstance(raw_objects, Mapping) else {}
    fallback_objects["grass_compatible_on_dry_and_details"] = bool(
        raw_objects.get(
            "grass_compatible_on_dry_and_details",
            fallback_objects.get("grass_compatible_on_dry_and_details", False),
        )
    )
    return base


def mineral_shares_as_fractions(shares: Mapping[str, Any]) -> dict[str, float]:
    """Normalize editable mineral shares for placement."""

    values = {key: max(0.0, _number(shares.get(key, 0.0), 0.0)) for key in MINERAL_KEYS}
    total = sum(values.values())
    if total <= 0:
        return {key: 0.0 for key in MINERAL_KEYS}
    return {key: values[key] / total for key in MINERAL_KEYS}


def rocky_proportional_targets(
    total: int,
    enabled: tuple[str, ...] | list[str],
    shares: Mapping[str, Any],
) -> dict[str, int]:
    """Resolve the prorata counts shown by the editor and written by the engine."""

    names = tuple(name for name in enabled if name in {"coal", "iron", "gold"})
    if not names:
        return {}
    total = max(
        len(names) * START_ROCKY_CORE_CELLS_MIN,
        min(rocky_total_cells_max(len(names)), int(round(float(total)))),
    )
    values = {
        name: max(0.0, _number(shares.get(name, 0.0), 0.0))
        for name in names
    }
    if not any(values.values()):
        values = {name: 1.0 for name in names}
    weight_total = sum(values.values())
    capacity = START_ROCKY_CORE_CELLS_MAX - START_ROCKY_CORE_CELLS_MIN
    remaining = total - len(names) * START_ROCKY_CORE_CELLS_MIN
    raw = {name: total * values[name] / weight_total for name in names}
    raw_extra = {name: remaining * values[name] / weight_total for name in names}
    targets = {
        name: START_ROCKY_CORE_CELLS_MIN + min(capacity, int(raw_extra[name]))
        for name in names
    }
    remainder = total - sum(targets.values())
    order = sorted(
        names,
        key=lambda name: (raw[name] - int(raw[name]), name),
        reverse=True,
    )
    while remainder > 0:
        changed = False
        for name in order:
            if targets[name] >= START_ROCKY_CORE_CELLS_MAX:
                continue
            targets[name] += 1
            remainder -= 1
            changed = True
            if remainder == 0:
                break
        if not changed:
            break
    return targets


__all__ = (
    "MINERAL_ALGORITHMS",
    "MINERAL_IDS",
    "MINERAL_KEYS",
    "MINERAL_KEYS_BY_ID",
    "MINERAL_SPECS",
    "DEFAULT_FISH_BAND_THICKNESS",
    "LEGACY_FISH_FILL_PERCENT",
    "LEGACY_RESOURCE_MEAN",
    "RESOURCE_MAXIMUM",
    "RESOURCE_MINIMUM",
    "STONE_QUANTITY_MAXIMUM",
    "STONE_QUANTITY_MINIMUM",
    "STONE_QUANTITY_STEP",
    "STONE_GROUP_COUNT_MAX",
    "STONE_GROUP_COUNT_MIN",
    "STONE_GROUP_VARIATION_MAX",
    "STONE_GROUP_VARIATION_MIN",
    "RIVER_RATE_MAX",
    "RIVER_RATE_MIN",
    "RIVER_RATE_STEP",
    "DECORATION_FAMILY_KEYS",
    "DECORATION_FAMILY_SPECS",
    "DECORATION_RATE_MAX",
    "DECORATION_RATE_MIN",
    "UPGRADED_REEF_TARGET_768",
    "TERRAIN_FAMILY_KEYS",
    "TERRAIN_RATE_MAX",
    "TERRAIN_RATE_MIN",
    "FOREST_TREE_COUNT_MAX",
    "FOREST_TREE_COUNT_MIN",
    "FOREST_TREE_VARIATION_MAX",
    "FOREST_TREE_VARIATION_MIN",
    "SEMANTIC_DENSITY_MAX",
    "SEMANTIC_DENSITY_MIN",
    "TREE_QUOTA_MAX",
    "SEMANTIC_SHARE_MAX",
    "SEMANTIC_SHARE_MIN",
    "SIZE_VARIATIONS",
    "TREE_PLACEMENTS",
    "UPGRADED_FISH_FILL_PERCENT",
    "UPGRADED_RESOURCE_MEAN",
    "UPGRADED_STONE_CLUSTER_SHARE_PERCENT",
    "START_BONUS_DISTANCE_MIN",
    "START_BONUS_DISTANCE_MAX",
    "START_BONUS_FORCE_EXTENDED_DEFAULT",
    "START_BONUS_COUNT_MIN",
    "START_BONUS_COUNT_MAX",
    "START_SWAMP_RADIUS_MIN",
    "START_SWAMP_RADIUS_MAX",
    "START_SWAMP_RADIUS_DEFAULT",
    "START_SWAMP_SHAPES",
    "START_FOREST_COUNT_MIN",
    "START_FOREST_COUNT_MAX",
    "START_FOREST_ADULT_DEFAULT",
    "START_FOREST_SAPLING_DEFAULT",
    "START_STONE_ANCHOR_MIN",
    "START_STONE_ANCHOR_MAX",
    "START_STONE_ANCHOR_DEFAULT",
    "START_STONE_AVERAGE_DEFAULT",
    "START_BONUS_STOCK_MIN",
    "START_BONUS_STOCK_MAX",
    "START_BONUS_RADIUS_MIN",
    "START_BONUS_RADIUS_MAX",
    "START_LAKE_SHAPES",
    "START_ROCKY_RADIUS_MAX",
    "START_ROCKY_CORE_CELLS_MIN",
    "START_ROCKY_CORE_CELLS_MAX",
    "rocky_total_cells_max",
    "rocky_equal_core_cells",
    "rocky_equivalent_radius",
    "rocky_proportional_targets",
    "START_BONUS_WATER_PROXIMITY_MIN",
    "START_BONUS_WATER_PROXIMITY_MAX",
    "START_BONUS_FISH_FILL_MIN",
    "START_BONUS_FISH_FILL_MAX",
    "START_BONUS_RIVER_TARGET_MIN",
    "START_BONUS_RIVER_TARGET_MAX",
    "default_sections",
    "mineral_shares_as_fractions",
    "normalize_sections",
)
