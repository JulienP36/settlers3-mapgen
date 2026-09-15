"""Defaults owned by the active independent Upgraded generator.

The old 768 JSON was a compatibility/calibration artifact from the abandoned
Upgraded v1.5 path.  Runtime defaults live here so the active engine no longer
depends on that historical file or on a protected 768 profile resource.
"""

from __future__ import annotations

from copy import deepcopy


def _family(
    ids: list[int],
    support_ids: list[int],
    low: int,
    high: int,
) -> dict[str, object]:
    return {
        "ids": ids,
        "support_ids": support_ids,
        "target_768_by_density": {"low": low, "high": high},
    }


ACTIVE_UPGRADED_PROFILE: dict[str, object] = {
    "profile_name": "Upgraded Continental",
    "profile_kind": "upgraded",
    # Reference area used only for proportional quotas outside the calibrated
    # map size.  It is not a separate generator version.
    "side": 768,
    "max_players": 20,
    "supported_players": list(range(2, 21)),
    "fish": {
        "max_shore_hex_distance": 12,
        "edge_is_not_shore": True,
    },
    "minerals": {
        "families": {
            "16": {"name": "Coal", "cells": 28375, "blobs": 500},
            "32": {"name": "Iron", "cells": 12202, "blobs": 240},
            "48": {"name": "Gold", "cells": 8164, "blobs": 165},
            "64": {"name": "Gems", "cells": 3098, "blobs": 75},
            "80": {"name": "Sulfur", "cells": 4745, "blobs": 100},
        },
        "shares": {"16": 0.525, "32": 0.225, "48": 0.15, "64": 0.05, "80": 0.05},
        "blob_size_min": 18,
        "blob_size_max": 105,
        "shape_variant": "round_parallelogram_compensated_test",
        "shape_space": "parallelogram_compensated",
        "blob_aspect_min": 1.0,
        "blob_aspect_max": 1.0,
        "rocky_accessible_occupancy_target": 0.90,
    },
    "snow": {
        "relative_percentile": 80,
        "absolute_min_height": 135,
        "mountain_hex_depth_min": 4,
        "target_cells": 11618,
    },
    "trees": {
        "adult_ids": [68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 80, 81],
        "adult_weights": [236, 226, 191, 200, 187, 185, 202, 195, 193, 213, 351, 356],
        "adult_global_target": 2736,
        "adult_start_bonus_per_player": 30,
        "small_tree_id": 84,
        "small_tree_target": 1067,
        "small_tree_start_bonus_per_player": 20,
        "small_tree_separate_pool": True,
        "palm_ids": [78, 79],
        "palm_target": 8,
        "forest_centers": 38,
        "forest_radius_min": 7,
        "forest_radius_max": 12,
        "adult_forest_min_hex_distance": 3,
        "adult_cluster_share": 0.30,
        "small_tree_cluster_share": 0.76,
        "start_cluster_center_hex": 34,
    },
    "building_stones": {
        "active_ids": [115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126],
        "exhausted_id": 127,
        "exhausted_buildable": True,
        "global_anchor_target": 1683,
        "global_exhausted_anchor_target": 20,
        "global_stock_target": 16338,
        "global_stock_weighted_fullness": True,
        "anchor_min_hex_distance": 4,
        "footprint": [[-1, -1], [0, -1], [-1, 0], [0, 0], [1, 0], [0, 1], [1, 1]],
        "cluster_share": 0.30,
        "cluster_centers": 60,
        "cluster_typical_anchors": 8,
        "start_cluster_center_hex": 34,
    },
    "decor": {
        "reef_target": 20,
        "reef_edge_margin": 2,
        "legacy_static_density_split_players": 8,
        "legacy_static_families": {
            "big_stones": _family([1, 2, 3, 4, 5, 6, 7, 8], [16], 253, 245),
            "decorative_stones": _family([9, 10, 11, 12], [16], 129, 128),
            "border_stones": _family([13, 14, 15, 16, 17, 18, 19, 20], [16], 243, 225),
            "small_stones": _family([21, 22, 23, 24, 25, 26, 27, 28], [16], 233, 236),
            "bushes": _family([57, 58, 59, 60, 61], [16], 137, 141),
            "cacti": _family([45, 46, 47, 48], [64], 26, 20),
            "dead_trees": _family([43, 44], [64], 5, 6),
            "graves": _family([34], [16], 29, 32),
            "skeletons": _family([49], [64], 3, 3),
            "small_bushes": _family([53, 54, 55, 56], [16], 110, 115),
            "small_flowers": _family([50, 51, 52], [16], 87, 87),
            "small_plants": _family([35, 36, 37], [16], 87, 87),
            "stumps": _family([41, 42], [16], 55, 59),
            "toadstools": _family([38, 39, 40], [16], 91, 83),
            "wrecks": _family([29, 30, 31, 32, 33], [48], 6, 6),
            "reeds": _family([62, 63, 64, 65, 66, 67], [80], 2, 1),
        },
        "swamp_reeds_only": True,
        "desert_ids": [43, 44, 45, 46, 47, 48, 49],
        "desert_target": 30,
        "swamp_reed_ids": [62, 63, 64, 65, 66, 67],
        "swamp_target": 60,
        "decorative_stone_target": 89,
        "forbid_objects_on_mountain": True,
    },
    "starts": {
        "min_pair_hex_distance": 52,
        "technical_clear_hex": 10,
        "local_bonus_outer_hex": 42,
        "initial_territory_hex_radius": 34,
        "height_range_max": 10,
        "immediate_height_delta_max": 4,
        "immediate_height_delta_sum_max": 14,
        "editor_terrain_clear_hex": 10,
        "editor_water_clear_hex": 20,
        "editor_object_clear_hex": 14,
    },
    "start_bonus": {
        "outside_global_quota": True,
        "forest": {
            "per_player": True,
            "style": "small_loose_cluster",
            "center_hex": 34,
            "distance_from_border": 0,
        },
        "building_stones": {
            "anchors_per_player": 15,
            "stock_units_per_player": 150,
            "average_quantity": 10.0,
            "quantity_min": 1,
            "quantity_max": 12,
            "footprint_cells": 7,
            "minimum_anchor_hex": 4,
            "center_hex": 34,
            "distance_from_border": 0,
        },
        "mini_swamp": {
            "per_player": True,
            "radius": 2,
            "shape": "native",
            "outer_cells": 4,
            "center_hex": 34,
            "distance_from_border": 0,
            "outside_technical_zone": True,
            "global_swamp_forbidden_in_technical_zone": True,
        },
        "rocky_minerals": {
            "per_player": True,
            "distance_from_border": 0,
            "center_hex": 34,
            "radius_min": 4,
            "radius_max": 4,
            "shape": "hexagon",
            "transition_rings": 2,
            "quantity_mean_source": "upgraded_global",
            "zones": {
                "coal": {"enabled": True, "family": 16},
                "iron": {"enabled": True, "family": 32},
                "gold": {"enabled": True, "family": 48},
            },
        },
        "lake_fish_river": {
            "per_player": True,
            "distance_from_border": 0,
            "center_hex": 34,
            "radius_min": 7,
            "radius_max": 9,
            "shape": "native",
            "water_proximity_from_territory_border": 150,
            "river_target": 1,
            "require_river": True,
            "fish_fill_percent": 50.0,
            "fish_average_quantity": 10,
        },
    },
    "upgraded_rules": {
        "start_first": True,
        "start_content_restored": True,
        "start_bonus_outside_global_quota": True,
        "mini_swamp_per_player": True,
        "global_swamp_forbidden_in_start_zone": True,
        "fish_after_final_hydrology": True,
        "minerals_v7_nogap": True,
        "snow_from_relief": True,
        "stone_full_footprint": True,
        "stone_exhausted_buildable": True,
        "legacy_static_object_families": True,
        "deep_water_external_edge": True,
        "coast_not_straight_clipped": True,
        "start_rocky_minerals": True,
        "start_lake_fish_river": True,
    },
}


def active_upgraded_profile() -> dict[str, object]:
    """Return an isolated copy for one generation or Custom preset."""

    return deepcopy(ACTIVE_UPGRADED_PROFILE)


__all__ = ("ACTIVE_UPGRADED_PROFILE", "active_upgraded_profile")
