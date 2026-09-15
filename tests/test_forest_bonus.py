from itertools import combinations

import numpy as np

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.map_data.hexgrid import hex_distance


def _generator():
    return MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)


def _forest_config(mode, *, grass_variants=False):
    config = build_custom_config(mode)
    sections = config.semantic_sections()
    sections["objects"]["grass_compatible_on_dry_and_details"] = grass_variants
    return config.with_sections(sections).with_start_packages(("start_forest",))


def _forest_points(record):
    return [
        (int(x), int(y))
        for x, y in record["adult_points"] + record["small_points"]
    ]


def test_start_forest_is_opt_in_for_custom_legacy_and_upgraded():
    generator = _generator()

    for mode in ("legacy", "upgraded"):
        config = build_custom_config(mode).with_sections(
            build_custom_config(mode).semantic_sections()
        )
        output = generator.generate(
            2,
            20260909,
            mode="custom",
            archetype="continental",
            side=256,
            custom_config=config,
        )

        if mode == "legacy":
            forest = output.state.metadata["legacy_start_forest"]
            assert forest["enabled"] is False
            assert forest["adult_placed"] == 0
            assert forest["saplings_placed"] == 0
        else:
            trees = output.state.metadata["upgraded_trees"]
            assert trees["start_forest_enabled"] is False
            assert trees["adult_start_bonus_placed"] == 0
            assert trees["small_start_bonus_placed"] == 0

        assert all(value.passed for value in output.validations if value.hard)


def test_start_forest_places_adults_then_saplings_with_common_spacing():
    generator = _generator()

    for mode in ("legacy", "upgraded"):
        output = generator.generate(
            2,
            20260909,
            mode="custom",
            archetype="continental",
            side=256,
            custom_config=_forest_config(mode),
        )

        if mode == "legacy":
            metadata = output.state.metadata["legacy_start_forest"]
            records = metadata["forests"]
            assert metadata["adult_placed"] == 2 * 30
            assert metadata["saplings_placed"] == 2 * 20
            assert metadata["tree_spacing_hex"] == 3
            assert metadata["radius_mode"] == "derived_from_tree_count_and_spacing"
        else:
            metadata = output.state.metadata["upgraded_trees"]
            records = metadata["start_forests"]
            assert metadata["adult_start_bonus_placed"] == 2 * 30
            assert metadata["small_start_bonus_placed"] == 2 * 20
            assert metadata["start_forest_tree_spacing_hex"] == 3
            assert metadata["start_forest_radius_mode"] == "derived_from_tree_count_and_spacing"

        assert len(records) == 2
        for record in records:
            assert record["adult"] == 30
            assert record["small" if mode == "upgraded" else "saplings"] == 20
            points = _forest_points(record)
            assert len(points) == 50
            assert all(
                hex_distance(x, y, xx, yy) >= 3
                for (x, y), (xx, yy) in combinations(points, 2)
            )
            assert record["radius"] >= record["minimum_required_radius"]
            adult_core_radius = record["adult_core_radius"]
            assert all(
                hex_distance(record["center_x"], record["center_y"], x, y)
                > adult_core_radius
                for x, y in record["small_points"]
            )

        assert all(value.passed for value in output.validations if value.hard)


def test_forest_radius_is_derived_and_old_radius_controls_are_ignored():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["forest"].update(
        adult_trees_per_player=4,
        saplings_per_player=2,
        radius_min=1,
        radius_max=1,
    )
    normalized = config.with_sections(sections).semantic_sections()
    forest = normalized["start_bonus"]["forest"]

    assert forest["adult_trees_per_player"] == 4
    assert forest["saplings_per_player"] == 2
    assert "radius_min" not in forest
    assert "radius_max" not in forest

    output = _generator().generate(
        2,
        20260909,
        mode="custom",
        archetype="continental",
        side=256,
        custom_config=config.with_sections(sections).with_start_packages(
            ("start_forest",)
        ),
    )
    records = output.state.metadata["upgraded_trees"]["start_forests"]
    assert all(record["adult"] == 4 and record["small"] == 2 for record in records)
    assert all(
        record["minimum_required_radius"] == record["radius"]
        for record in records
    )


def test_start_forest_counts_are_capped_at_one_hundred_each():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["forest"].update(
        adult_trees_per_player=1000,
        saplings_per_player=1000,
    )
    forest = config.with_sections(sections).semantic_sections()["start_bonus"]["forest"]
    assert forest["adult_trees_per_player"] == 100
    assert forest["saplings_per_player"] == 100


def test_grass_compatible_switch_adds_only_the_three_requested_terrain_ids():
    generator = _generator()
    for mode in ("legacy", "upgraded"):
        output = generator.generate(
            2,
            20260909,
            mode="custom",
            archetype="continental",
            side=256,
            custom_config=_forest_config(mode, grass_variants=True),
        )
        assert all(value.passed for value in output.validations if value.hard)
        if mode == "legacy":
            support = output.state.metadata["legacy_start_forest"]["support_terrains"]
        else:
            support = output.state.metadata["upgraded_trees"]["grass_object_support_terrains"]
        assert support == [16, 18, 19, 24]
        assert 34 not in support
        variant_objects = np.isin(output.state.terrain, (18, 19, 24)) & (
            output.state.objects != 0
        )
        assert int(variant_objects.sum()) > 0
