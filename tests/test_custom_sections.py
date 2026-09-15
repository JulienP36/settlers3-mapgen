import numpy as np
import pytest

from s3mapgen.generation.custom import (
    DECORATION_FAMILY_KEYS,
    DECORATION_RATE_MAX,
    FOREST_TREE_COUNT_MAX,
    MINERAL_KEYS,
    RIVER_RATE_MAX,
    RIVER_RATE_MIN,
    RIVER_RATE_STEP,
    START_BONUS_RADIUS_MAX,
    START_BONUS_RIVER_TARGET_MAX,
    TERRAIN_FAMILY_KEYS,
    TERRAIN_RATE_MAX,
    TREE_QUOTA_MAX,
    build_custom_config,
    mineral_shares_as_fractions,
    normalize_sections,
    rocky_equal_core_cells,
    rocky_equivalent_radius,
)
from s3mapgen.generation.custom.content import _place_legacy_minerals, apply_custom_resource_sections
from s3mapgen.map_data.constants import RIVER_IDS
from s3mapgen.generation.custom.content import _shore_distances, _resource_quantities


def test_rocky_surface_helpers_keep_equal_area_and_nearest_radius_consistent():
    assert rocky_equal_core_cells(4) == 61
    assert rocky_equal_core_cells(16) == 817
    assert rocky_equivalent_radius(183, 3) == 4
    assert rocky_equivalent_radius(507, 3) == 7
    # A non-representable total still gets a deterministic common-radius
    # indicator; switching to equal mode then canonicalizes it visibly.
    assert rocky_equivalent_radius(500, 3) == 7


def _water_test_terrain(side=64):
    terrain = np.full((side, side), 16, dtype=np.uint8)
    terrain[10, 2:-2] = 48
    terrain[11:side - 2, 2:-2] = 0
    return terrain


def test_custom_sections_have_short_bounded_semantic_defaults():
    config = build_custom_config()
    sections = config.semantic_sections()

    assert START_BONUS_RADIUS_MAX == 16
    assert START_BONUS_RIVER_TARGET_MAX == 6

    assert set(sections) == {
        "minerals", "fish", "rivers", "terrains", "trees", "building_stones",
        "start_bonus", "decorations", "objects",
    }
    assert tuple(sections["terrains"]) == TERRAIN_FAMILY_KEYS
    assert sections["terrains"]["mud"] == {"enabled": False, "rate_percent": 0.0}
    assert sections["terrains"]["desert"] == {"enabled": True, "rate_percent": 100.0}
    assert all(
        sections["terrains"][key] == {"enabled": True, "rate_percent": 100.0}
        for key in TERRAIN_FAMILY_KEYS
        if key != "mud"
    )
    assert tuple(sections["decorations"]) == DECORATION_FAMILY_KEYS
    assert sections["decorations"] == {key: 100.0 for key in DECORATION_FAMILY_KEYS}
    legacy_sections = build_custom_config("legacy").semantic_sections()
    assert legacy_sections["terrains"]["mud"] == {"enabled": True, "rate_percent": 100.0}
    assert legacy_sections["decorations"]["reefs"] == 0.0
    assert all(
        legacy_sections["decorations"][key] == 100.0
        for key in DECORATION_FAMILY_KEYS
        if key != "reefs"
    )
    assert sections["minerals"]["algorithm"] == "upgraded"
    assert sections["minerals"]["occupancy_percent"] == 90.0
    assert set(sections["minerals"]["shares"]) == set(MINERAL_KEYS)
    assert sections["minerals"]["shares"] == pytest.approx({
        "coal": 52.5,
        "iron": 22.5,
        "gold": 15.0,
        "gems": 5.0,
        "sulfur": 5.0,
    })
    assert sections["fish"]["near_shore"] is True
    assert sections["minerals"]["average_quantity"] == {key: 10 for key in MINERAL_KEYS}
    assert sections["fish"]["average_quantity"] == 10
    assert sections["fish"]["band_thickness"] == 12
    assert sections["rivers"] == {"rate_percent": 100.0}
    assert sections["objects"] == {"grass_compatible_on_dry_and_details": False}
    assert sections["trees"] == {
        "base_quota_percent": 100.0,
        "saplings": {
            "enabled": True,
            "in_global_pool": False,
            "global_share_percent": 0.0,
            "quota_percent": 39.0,
            "placement": "forests_only",
        },
        "forests": {
            "enabled": True,
            "share_percent": 30.0,
            "trees_per_forest": 21.6,
            "tree_count_variation_percent": 0.0,
        },
        "palm_quota_percent": 100.0,
    }
    assert sections["building_stones"] == {
        "anchor_density_percent": 100.0,
        "average_quantity": 10,
        "groups": {
            "enabled": True,
            "share_percent": 30.0,
            "stones_per_group": 8.0,
            "stone_count_variation_percent": 0.0,
        },
    }
    assert sections["start_bonus"] == {
        "distance_from_border": 0,
        "force_extended_radius": False,
        "forest": {
            "enabled": True,
            "adult_trees_per_player": 30,
            "saplings_per_player": 20,
            "shape": "native",
        },
        "building_stones": {
            "enabled": True,
            "anchors_per_player": 15,
            "stock_units_per_player": 150,
            "average_quantity": 10.0,
            "quantity_min": 1,
            "quantity_max": 12,
            "shape": "native",
        },
        "mini_swamp": {
            "enabled": True,
            "radius": 2,
            "shape": "native",
        },
        "rocky_minerals": {
            "enabled": True,
            "radius_min": 4,
            "radius_max": 4,
            "shape": "hexagon",
            "surface_mode": "equal",
            "total_core_cells": 183,
            "coal": {"enabled": True, "core_cells": 61, "average_quantity": 10, "quantity_mode": "global"},
            "iron": {"enabled": True, "core_cells": 61, "average_quantity": 10, "quantity_mode": "global"},
            "gold": {"enabled": True, "core_cells": 61, "average_quantity": 10, "quantity_mode": "global"},
        },
            "lake_fish_river": {
                "enabled": True,
                "radius_min": 7,
                "radius_max": 9,
                "shape": "native",
            "water_proximity_from_territory_border": 150,
            "river_target_per_lake": 1,
            "fish_fill_percent": 50.0,
        },
    }

    legacy = build_custom_config("legacy").semantic_sections()
    assert legacy["minerals"]["average_quantity"] == {key: 8 for key in MINERAL_KEYS}
    assert legacy["fish"]["average_quantity"] == 8
    assert legacy["fish"]["near_shore"] is False
    assert legacy["fish"]["fill_percent"] == 36.5
    assert legacy["rivers"] == {"rate_percent": 100.0}
    assert legacy["trees"] == {
        "base_quota_percent": 100.0,
        "saplings": {
            "enabled": False,
            "in_global_pool": False,
            "global_share_percent": 0.0,
            "quota_percent": 0.0,
            "placement": "everywhere",
        },
        "forests": {
            "enabled": False,
            "share_percent": 0.0,
            "trees_per_forest": 1.0,
            "tree_count_variation_percent": 0.0,
        },
        "palm_quota_percent": 100.0,
    }
    assert legacy["building_stones"]["average_quantity"] == 6.5
    assert legacy["building_stones"]["groups"] == {
        "enabled": False,
        "share_percent": 0.0,
        "stones_per_group": 1.0,
        "stone_count_variation_percent": 0.0,
    }


def test_custom_sections_round_trip_through_the_generation_cache_payload():
    config = build_custom_config().with_sections(build_custom_config().semantic_sections())
    restored = type(config).from_dict(config.to_dict())

    assert restored.semantic_sections() == config.semantic_sections()
    assert restored.runtime_profile()["_custom_runtime"]["sections"] == config.semantic_sections()
    assert restored.digest == config.digest


def test_custom_river_rate_is_bounded_to_the_public_range():
    fallback = build_custom_config("upgraded").semantic_sections()

    normalized = normalize_sections(
        {"rivers": {"rate_percent": -20}},
        fallback=fallback,
    )
    assert normalized["rivers"]["rate_percent"] == RIVER_RATE_MIN

    normalized = normalize_sections(
        {"rivers": {"rate_percent": 999}},
        fallback=fallback,
    )
    assert normalized["rivers"]["rate_percent"] == RIVER_RATE_MAX
    assert RIVER_RATE_STEP == 1.0


def test_start_bonus_controls_are_bounded_and_stone_stock_is_derived():
    fallback = build_custom_config("upgraded").semantic_sections()
    normalized = normalize_sections(
        {
            "start_bonus": {
                "distance_from_border": 9999,
                "forest": {
                    "adult_trees_per_player": 0,
                    "saplings_per_player": 2001,
                    "radius_min": 0,
                    "radius_max": 999,
                },
                "building_stones": {
                    "anchors_per_player": 4,
                    "average_quantity": 6.25,
                    "stock_units_per_player": 1,
                },
                "mini_swamp": {"radius": 0, "shape": "unknown"},
                "rocky_minerals": {
                    "coal": {"enabled": False},
                    "iron": {"enabled": True},
                },
                "lake_fish_river": {
                    "water_proximity_from_territory_border": -1,
                    "radius_max": 999,
                    "river_target_per_lake": 99,
                    "fish_fill_percent": 101,
                },
            },
        },
        fallback=fallback,
    )["start_bonus"]

    assert normalized["distance_from_border"] == 512
    assert normalized["forest"]["adult_trees_per_player"] == 1
    assert normalized["forest"]["saplings_per_player"] == 100
    assert "radius_min" not in normalized["forest"]
    assert "radius_max" not in normalized["forest"]
    assert normalized["building_stones"]["average_quantity"] == 6.5
    assert normalized["building_stones"]["stock_units_per_player"] == 26
    assert "radius_min" not in normalized["building_stones"]
    assert "radius_max" not in normalized["building_stones"]
    assert normalized["mini_swamp"]["radius"] == 1
    assert normalized["mini_swamp"]["shape"] == "native"
    assert "cells_per_player" not in normalized["mini_swamp"]
    high_swamp = normalize_sections(
        {"start_bonus": {"mini_swamp": {"radius": 999, "shape": "hexagon"}}},
        fallback=fallback,
    )["start_bonus"]["mini_swamp"]
    assert high_swamp["radius"] == 16
    assert high_swamp["shape"] == "hexagon"
    assert normalized["rocky_minerals"]["coal"]["enabled"] is False
    assert normalized["lake_fish_river"]["water_proximity_from_territory_border"] == 0
    assert normalized["lake_fish_river"]["radius_max"] == 16
    assert normalized["lake_fish_river"]["river_target_per_lake"] == 6
    assert normalized["lake_fish_river"]["fish_fill_percent"] == 100.0


def test_custom_sections_clamp_real_resource_limits_without_rejecting_generation():
    fallback = build_custom_config().semantic_sections()
    normalized = normalize_sections(
        {
            "minerals": {
                "occupancy_percent": 140,
                "shares": {"coal": -2, "iron": 40},
                "average_quantity": {"coal": 0, "iron": 99},
            },
            "fish": {
            "fill_percent": -10,
            "average_quantity": 100,
                "band_thickness": -4,
            },
            "trees": {
                "base_quota_percent": 999,
                "saplings": {
                    "enabled": True,
                    "in_global_pool": True,
                    "global_share_percent": 120,
                    "quota_percent": 999,
                    "placement": "invalid",
                },
                "forests": {
                    "enabled": True,
                    "share_percent": 120,
                    "trees_per_forest": 0,
                    "tree_count_variation_percent": 999,
                },
                "palm_quota_percent": 999,
            },
            "building_stones": {
                "anchor_density_percent": 250,
                "stock_percent": -5,
                "cluster_share_percent": -1,
            },
            "terrains": {
                "desert": {"enabled": False, "rate_percent": 900},
                "swamp": {"enabled": True, "rate_percent": -4},
            },
        },
        fallback=fallback,
    )

    assert normalized["minerals"]["occupancy_percent"] == 100.0
    assert normalized["minerals"]["shares"]["coal"] == 0.0
    assert normalized["minerals"]["average_quantity"]["coal"] == 1
    assert normalized["minerals"]["average_quantity"]["iron"] == 15
    assert normalized["fish"]["fill_percent"] == 0.0
    assert normalized["fish"]["average_quantity"] == 15
    assert normalized["fish"]["band_thickness"] == 1
    assert TREE_QUOTA_MAX == 500.0
    assert normalized["trees"]["base_quota_percent"] == 500.0
    assert normalized["trees"]["saplings"]["global_share_percent"] == 100.0
    assert normalized["trees"]["saplings"]["quota_percent"] == 200.0
    assert normalized["trees"]["saplings"]["placement"] == "everywhere"
    assert normalized["trees"]["forests"]["share_percent"] == 100.0
    assert normalized["trees"]["forests"]["trees_per_forest"] == 1.0
    assert FOREST_TREE_COUNT_MAX == 100.0
    assert normalized["trees"]["forests"]["tree_count_variation_percent"] == 100.0
    assert normalized["trees"]["palm_quota_percent"] == 500.0
    assert normalized["building_stones"]["anchor_density_percent"] == 200.0
    assert normalized["building_stones"]["average_quantity"] == 1
    assert normalized["building_stones"]["groups"]["enabled"] is False
    assert normalized["building_stones"]["groups"]["share_percent"] == 0.0
    assert DECORATION_RATE_MAX == 500.0
    assert TERRAIN_RATE_MAX == 500.0
    assert normalized["terrains"]["desert"] == {"enabled": False, "rate_percent": 500.0}
    assert normalized["terrains"]["swamp"] == {"enabled": True, "rate_percent": 1.0}

    normalized_decorations = normalize_sections(
        {"decorations": {DECORATION_FAMILY_KEYS[0]: -4, DECORATION_FAMILY_KEYS[-1]: 900}},
        fallback=fallback,
    )["decorations"]
    assert normalized_decorations[DECORATION_FAMILY_KEYS[0]] == 0.0
    assert normalized_decorations[DECORATION_FAMILY_KEYS[-1]] == 500.0

    half_step = normalize_sections(
        {"building_stones": {"average_quantity": 6.25}},
        fallback=fallback,
    )
    assert half_step["building_stones"]["average_quantity"] == 6.5

    fractions = mineral_shares_as_fractions({"coal": 10, "iron": 30})
    assert fractions["coal"] == 0.25
    assert fractions["iron"] == 0.75
    assert sum(fractions.values()) == 1.0


def test_equal_rocky_mode_materializes_one_common_radius_with_compact_bounds():
    fallback = build_custom_config("upgraded").semantic_sections()

    migrated = normalize_sections(
        {
            "start_bonus": {
                "rocky_minerals": {
                    "surface_mode": "equal",
                    "radius_min": 3,
                    "radius_max": 5,
                },
            },
        },
        fallback=fallback,
    )["start_bonus"]["rocky_minerals"]
    assert migrated["radius_min"] == migrated["radius_max"] == 4

    explicit = normalize_sections(
        {
            "start_bonus": {
                "rocky_minerals": {
                    "surface_mode": "equal",
                    "radius": 999,
                    "radius_min": 1,
                    "radius_max": 2,
                    "total_core_cells": 9999,
                    "coal": {"core_cells": 9999},
                },
            },
        },
        fallback=fallback,
    )["start_bonus"]["rocky_minerals"]
    assert explicit["radius_min"] == explicit["radius_max"] == 16
    assert explicit["total_core_cells"] == 2460
    assert explicit["coal"]["core_cells"] == 820


def test_rocky_total_max_scales_with_active_mineral_families():
    fallback = build_custom_config("upgraded").semantic_sections()
    for enabled, expected in ((0, 0), (1, 820), (2, 1640), (3, 2460)):
        rocky = {
            "surface_mode": "proportional",
            "total_core_cells": 9999,
            "coal": {"enabled": enabled >= 1},
            "iron": {"enabled": enabled >= 2},
            "gold": {"enabled": enabled >= 3},
        }
        normalized = normalize_sections(
            {"start_bonus": {"rocky_minerals": rocky}}, fallback=fallback
        )["start_bonus"]["rocky_minerals"]
        assert normalized["total_core_cells"] == expected


def test_custom_fish_applies_fill_directly_inside_the_requested_coastal_band():
    terrain = _water_test_terrain()
    resources = np.zeros_like(terrain)
    sections = build_custom_config().semantic_sections()
    sections["minerals"]["occupancy_percent"] = 0
    sections["fish"].update({"fill_percent": 20, "near_shore": True, "band_thickness": 3})

    state = type("State", (), {"terrain": terrain, "resources": resources})()
    metadata = apply_custom_resource_sections(
        state,
        sections,
        np.random.default_rng(20260904),
    )["fish"]

    assert metadata["cells"] == metadata["target_cells"]
    assert metadata["near_shore_effective"] is True
    assert metadata["band_thickness_requested"] == 3
    assert metadata["band_thickness_effective"] == 3
    assert metadata["selection_mode"] == "coastal_band_uniform"
    assert metadata["candidate_cells"] == metadata["coastal_band_cells"]
    chosen = resources[resources > 0]
    assert len(chosen) == metadata["cells"]
    assert int(chosen.min()) >= 1
    assert int(chosen.max()) <= 15
    distances = _shore_distances(terrain)
    assert np.all(distances[resources > 0] <= 3)


def test_custom_fish_falls_back_to_global_distribution_when_coastal_reach_is_insufficient():
    terrain = _water_test_terrain()
    resources = np.zeros_like(terrain)
    sections = build_custom_config().semantic_sections()
    sections["minerals"]["occupancy_percent"] = 0
    sections["fish"].update({"fill_percent": 80, "near_shore": True, "band_thickness": 4096})
    terrain[25, 25] = RIVER_IDS[0]
    state = type("State", (), {"terrain": terrain, "resources": resources})()

    metadata = apply_custom_resource_sections(
        state,
        sections,
        np.random.default_rng(20260904),
    )["fish"]

    assert metadata["cells"] == metadata["target_cells"]
    assert metadata["near_shore_effective"] is False
    assert metadata["selection_mode"] == "global_uniform_band_exceeded"
    assert metadata["fill_basis"] == "eligible_water"


def test_legacy_derived_custom_profile_can_use_coastal_band_thickness():
    from s3mapgen.generation.core.request import GenerationRequest
    from s3mapgen.generation.generators.legacy.native_pipeline import generate

    config = build_custom_config("legacy")
    sections = config.semantic_sections()
    sections["fish"].update({"near_shore": True, "band_thickness": 3})
    state, _ = generate(
        GenerationRequest(side=256, players=2, seed=20260904),
        profile=config.with_sections(sections).runtime_profile(),
    )

    metadata = state.metadata["fish"]
    assert metadata["near_shore_effective"] is True
    assert metadata["band_thickness_effective"] == 3
    assert metadata["selection_mode"] == "coastal_band_uniform"


def test_custom_mineral_method_switches_between_the_three_real_placement_algorithms():
    side = 64
    terrain = np.full((side, side), 32, dtype=np.uint8)
    resources = np.zeros_like(terrain)
    sections = build_custom_config().semantic_sections()
    sections["minerals"].update({
        "occupancy_percent": 10,
        "shares": {"coal": 100, "iron": 0, "gold": 0, "gems": 0, "sulfur": 0},
    })
    sections["fish"]["fill_percent"] = 0
    state = type("State", (), {"terrain": terrain, "resources": resources})()

    sections["minerals"]["algorithm"] = "legacy"
    legacy = apply_custom_resource_sections(state, sections, np.random.default_rng(3))["minerals"]
    assert legacy["algorithm"] == "legacy"
    assert legacy["model"] == "custom_legacy_hex_zones_r17"
    assert legacy["placed_total"] == legacy["target_total"]

    sections["minerals"]["algorithm"] = "upgraded"
    upgraded = apply_custom_resource_sections(state, sections, np.random.default_rng(3))["minerals"]
    assert upgraded["algorithm"] == "upgraded"
    assert upgraded["model"] == "custom_upgraded_connected_blobs"
    assert upgraded["placed_total"] == upgraded["target_total"]

    sections["minerals"]["algorithm"] = "random"
    random_pixels = apply_custom_resource_sections(state, sections, np.random.default_rng(3))["minerals"]
    assert random_pixels["algorithm"] == "random"
    assert random_pixels["model"] == "custom_random_scatter_pixels"
    assert random_pixels["placement"] == "uniform_random_independent_pixels"
    assert random_pixels["placed_total"] == random_pixels["target_total"]
    assert all(
        family["placed"] == family["target"]
        for family in random_pixels["families"].values()
    )


def test_random_minerals_write_through_the_interleaved_resource_channel():
    """The MapState resource layer is a strided view, not a flat array."""

    side = 64
    area = np.zeros((side, side, 6), dtype=np.uint8)
    area[:, :, 3] = 255
    terrain = area[:, :, 1]
    terrain[:] = 32
    resources = area[:, :, 5]
    sections = build_custom_config("upgraded").semantic_sections()
    sections["minerals"].update({
        "algorithm": "random",
        "occupancy_percent": 25,
        "shares": {"coal": 100, "iron": 0, "gold": 0, "gems": 0, "sulfur": 0},
    })
    sections["fish"]["fill_percent"] = 0
    state = type("State", (), {"terrain": terrain, "resources": resources})()

    metadata = apply_custom_resource_sections(
        state,
        sections,
        np.random.default_rng(20260904),
    )["minerals"]

    assert not resources.flags.c_contiguous
    assert metadata["target_total"] > 0
    assert metadata["placed_total"] == metadata["target_total"]
    assert int(np.count_nonzero(resources & 0xF0)) == metadata["target_total"]


def test_legacy_hex_method_keeps_multiple_bounded_random_zones():
    side = 96
    terrain = np.full((side, side), 32, dtype=np.uint8)
    resources = np.zeros_like(terrain)
    sections = build_custom_config("legacy").semantic_sections()
    sections["minerals"].update({
        "occupancy_percent": 10,
        "shares": {"coal": 100, "iron": 0, "gold": 0, "gems": 0, "sulfur": 0},
    })
    sections["fish"]["fill_percent"] = 0
    state = type("State", (), {"terrain": terrain, "resources": resources})()

    metadata = apply_custom_resource_sections(state, sections, np.random.default_rng(20260904))["minerals"]

    mask = (resources & 0xF0) == 0x10
    remaining = {(int(x), int(y)) for y, x in np.argwhere(mask)}
    components = []
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        stack = [seed]
        while stack:
            x, y = stack.pop()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1)):
                point = (x + dx, y + dy)
                if point in remaining:
                    remaining.remove(point)
                    component.add(point)
                    stack.append(point)
        components.append(len(component))

    assert metadata["families"]["coal"]["fallback_cells"] == 0
    assert metadata["families"]["coal"]["deposit_count"] >= 2
    assert components
    assert max(components) >= 20


def test_legacy_occupancy_is_reachable_without_a_giant_fallback_deposit():
    side = 96
    terrain = np.full((side, side), 32, dtype=np.uint8)
    sections = build_custom_config("legacy").semantic_sections()["minerals"]
    sections["shares"] = {"coal": 100, "iron": 0, "gold": 0, "gems": 0, "sulfur": 0}

    support_cells = int(np.count_nonzero((terrain & 0xF0) == 0x20))
    for occupancy in (0, 10, 53, 80, 100):
        resources = np.zeros_like(terrain)
        sections["occupancy_percent"] = occupancy
        metadata = _place_legacy_minerals(
            terrain,
            resources,
            sections,
            np.random.default_rng(20260904 + occupancy),
        )

        assert metadata["target_total"] == round(support_cells * occupancy / 100)
        assert metadata["placed_total"] == metadata["target_total"]
        assert metadata["actual_occupancy_percent"] == pytest.approx(occupancy, abs=0.01)
        assert all(
            family["deposit_size_range"][1] <= 95
            for family in metadata["families"].values()
        )


def test_resource_quantity_profiles_match_the_two_requested_means():
    native = _resource_quantities(15000, 8, np.random.default_rng(8))
    upgraded = _resource_quantities(15000, 10, np.random.default_rng(10))

    assert set(np.unique(native)) == set(range(1, 16))
    assert float(native.mean()) == pytest.approx(8.0, abs=0.1)
    assert float(upgraded.mean()) == pytest.approx(10.0, abs=0.01)
    assert int(upgraded.min()) >= 1
    assert int(upgraded.max()) <= 15
