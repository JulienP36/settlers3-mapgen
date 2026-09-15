import numpy as np

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.map_data.hexgrid import hex_distance


def _generator():
    return MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)


def _without_start_forest(config):
    return config.with_start_packages(())


def test_upgraded_tree_controls_keep_pools_and_outside_forest_placement_separate():
    config = _without_start_forest(build_custom_config("upgraded"))
    sections = config.semantic_sections()
    sections["trees"].update(
        {
            "base_quota_percent": 50,
            "saplings": {
                "enabled": True,
                "in_global_pool": False,
                "global_share_percent": 0,
                "quota_percent": 20,
                "placement": "outside_forests",
            },
            "forests": {
                "enabled": True,
                "share_percent": 50,
                "trees_per_forest": 10,
                "tree_count_variation_percent": 50,
            },
            "palm_quota_percent": 0,
        }
    )

    result = _generator().generate(
        2,
        20260904,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=config.with_sections(sections),
    )
    trees = result.state.metadata["upgraded_trees"]

    assert trees["adult_global_requested"] == 152
    assert trees["small_separate_requested"] == trees["small_global_requested"] == 61
    assert trees["small_global_placed"] == 61
    assert trees["palm_requested"] == 0
    assert trees["forests_enabled"] is True
    assert trees["forest_share_percent"] == 50.0
    assert trees["forest_trees_per_forest"] == 10.0
    assert trees["forest_tree_count_variation_percent"] == 50.0
    assert len(trees["global_forests"]) == 8
    assert len(set(trees["global_forest_tree_quotas"])) > 1

    saplings = np.argwhere(result.state.objects == 84)
    assert len(saplings) == trees["small_global_placed"]
    for y, x in saplings:
        assert all(
            hex_distance(
                int(x),
                int(y),
                forest["center_x"],
                forest["center_y"],
            ) > forest["radius"]
            for forest in trees["global_forests"]
        )


def test_upgraded_saplings_can_consume_the_base_global_pool():
    config = _without_start_forest(build_custom_config("upgraded"))
    sections = config.semantic_sections()
    sections["trees"]["forests"]["enabled"] = False
    sections["trees"]["saplings"] = {
        "enabled": True,
        "in_global_pool": True,
        "global_share_percent": 25,
        "quota_percent": 99,
        "placement": "everywhere",
    }

    result = _generator().generate(
        2,
        20260904,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=config.with_sections(sections),
    )
    trees = result.state.metadata["upgraded_trees"]

    assert trees["adult_global_requested"] == 228
    assert trees["small_global_requested"] == 76
    assert trees["small_separate_requested"] == 0
    assert trees["adult_global_requested"] + trees["small_global_requested"] == 304
    assert trees["saplings_in_global_pool"] is True
    assert trees["saplings_global_share_percent"] == 25.0
    assert trees["forests_enabled"] is False
    assert trees["global_forests"] == []


def test_legacy_tree_controls_apply_forest_average_variation_and_palm_cap():
    config = _without_start_forest(build_custom_config("legacy"))
    sections = config.semantic_sections()
    sections["trees"].update(
        {
            "base_quota_percent": 50,
            "saplings": {
                "enabled": True,
                "in_global_pool": False,
                "global_share_percent": 0,
                "quota_percent": 10,
                "placement": "forests_only",
            },
            "forests": {
                "enabled": True,
                "share_percent": 50,
                "trees_per_forest": 10,
                "tree_count_variation_percent": 50,
            },
            "palm_quota_percent": 0,
        }
    )

    result = _generator().generate(
        2,
        20260904,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=config.with_sections(sections),
    )
    trees = result.state.metadata["trees"]

    assert trees["tree_target"] == 152
    assert trees["small_tree_target"] == 30
    assert trees["palm_trees"] == 0
    assert trees["forests_enabled"] is True
    assert trees["forest_count"] == 8
    assert trees["forest_tree_count_variation_percent"] == 50.0
    assert sum(trees["forest_tree_quotas"]) == trees["adult_forest_target"] == 76
    assert len(set(trees["forest_tree_quotas"])) > 1
    assert trees["adult_forest_placed"] == sum(trees["forest_tree_placed"])


def test_tree_presets_do_not_reintroduce_the_removed_forty_four_percent_value():
    upgraded = build_custom_config("upgraded").semantic_sections()["trees"]
    legacy = build_custom_config("legacy").semantic_sections()["trees"]

    assert upgraded["forests"]["share_percent"] == 30.0
    assert legacy["forests"]["enabled"] is False
    assert legacy["forests"]["share_percent"] == 0.0
