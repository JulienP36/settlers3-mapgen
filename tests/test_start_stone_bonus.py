import numpy as np

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.custom import build_custom_config


def _generator():
    return MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)


def _stone_config(mode):
    config = build_custom_config(mode)
    return config.with_sections(config.semantic_sections()).with_start_packages(
        ("start_building_stones",)
    )


def test_start_stones_default_to_fifteen_anchors_and_ten_units_per_player():
    generator = _generator()
    for mode in ("legacy", "upgraded"):
        output = generator.generate(
            2,
            20260910,
            mode="custom",
            archetype="continental",
            side=256,
            custom_config=_stone_config(mode),
        )
        if mode == "legacy":
            stones = output.state.metadata["legacy_start_building_stones"]
            assert stones["anchors_placed"] == 30
            assert stones["stock_placed"] == 300
            assert stones["quantity_distribution_model"] == "full_range_mean_tilt"
            assert stones["radius_mode"] == "derived_from_anchor_count_and_spacing"
        else:
            stones = output.state.metadata["upgraded_stones"]
            assert stones["start_bonus_anchors"] == 30
            assert stones["start_bonus_stock"] == 300
            assert stones["start_bonus_quantity_distribution_model"] == "full_range_mean_tilt"
            assert stones["start_bonus_radius_mode"] == "derived_from_anchor_count_and_spacing"
        assert all(value.passed for value in output.validations if value.hard)


def test_zero_global_stones_and_disabled_start_bonus_leave_no_stone_objects():
    generator = _generator()
    for mode in ("legacy", "upgraded"):
        config = build_custom_config(mode)
        sections = config.semantic_sections()
        sections["building_stones"]["anchor_density_percent"] = 0
        sections["start_bonus"]["building_stones"]["enabled"] = False
        config = config.with_sections(sections).with_start_packages(())
        output = generator.generate(
            2,
            20260910,
            mode="custom",
            archetype="continental",
            side=256,
            custom_config=config,
        )
        stone_objects = (output.state.objects >= 115) & (output.state.objects <= 127)
        assert not stone_objects.any(), mode
        assert all(value.passed for value in output.validations if value.hard)


def test_zero_global_trees_are_not_preserved_inside_start_stone_bonus():
    config = build_custom_config("legacy")
    sections = config.semantic_sections()
    sections["trees"].update({
        "base_quota_percent": 0,
        "palm_quota_percent": 0,
        "saplings": {
            "enabled": False,
            "in_global_pool": False,
            "global_share_percent": 0,
            "quota_percent": 0,
            "placement": "everywhere",
        },
    })
    sections["building_stones"]["anchor_density_percent"] = 0
    config = config.with_sections(sections).with_start_packages(
        ("start_building_stones",)
    )

    output = _generator().generate(
        2,
        20260910,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=config,
    )

    tree_ids = tuple(range(68, 82)) + (84,)
    assert not np.any(np.isin(output.state.objects, tree_ids))
    assert output.state.metadata["legacy_start_building_stones"]["anchors_placed"] == 30
    assert "custom_start_bonus_reservation" not in output.state.metadata
    assert all(value.passed for value in output.validations if value.hard)


def test_start_stone_anchor_count_is_capped_and_old_radii_are_ignored():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["building_stones"].update(
        anchors_per_player=999,
        average_quantity=9.75,
        radius_min=1,
        radius_max=1,
    )
    stones = config.with_sections(sections).semantic_sections()["start_bonus"]["building_stones"]
    assert stones["anchors_per_player"] == 50
    assert stones["average_quantity"] == 10.0
    assert stones["stock_units_per_player"] == 500
    assert "radius_min" not in stones
    assert "radius_max" not in stones


def test_every_start_bonus_toggle_reaches_custom_legacy_without_switching_engine():
    packages = (
        "start_forest",
        "start_building_stones",
        "start_mini_swamp",
        "start_rocky_minerals",
        "start_lake_fish_river",
    )
    config = build_custom_config("legacy")
    config = config.with_sections(config.semantic_sections()).with_start_packages(packages)
    output = _generator().generate(
        2,
        20260910,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=config,
    )
    metadata = output.state.metadata
    assert metadata["custom_profile_diagnostics"]["base_mode"] == "legacy"
    assert metadata["legacy_start_forest"]["enabled"] is True
    assert metadata["legacy_start_building_stones"]["enabled"] is True
    assert metadata["upgraded_start_mini_swamps"]["placed_cells"] > 0
    assert metadata["upgraded_start_rocky_minerals"]["enabled"] is True
    assert metadata["upgraded_start_lake_fish_river"]["enabled"] is True
    assert all(value.passed for value in output.validations if value.hard)
