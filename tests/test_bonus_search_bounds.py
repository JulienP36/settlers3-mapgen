"""Shared bonus-search settings, compatibility and real placement bounds."""
import json
import random

import numpy as np
import pytest

from s3mapgen.application.custom.controller import CustomGeneratorController
from s3mapgen.generation.custom import build_custom_config, CustomGenerationConfig
from s3mapgen.generation.custom.bonus_placement import ordered_centers
from s3mapgen.generation.custom.objects import (
    apply_custom_legacy_start_forest, apply_custom_legacy_start_stones,
)
from s3mapgen.map_data.hexgrid import hex_distance
from test_upgraded_start_bonus_zones import _content_state, ALL_START_PACKAGES


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_missing_setting_roundtrip_and_bonus_reset(mode):
    original = build_custom_config(mode)
    old = original.to_dict()
    old["sections"].get("start_bonus", {}).pop("center_extension_limit", None)
    restored = CustomGenerationConfig.from_dict(json.loads(json.dumps(old)))
    assert restored.semantic_sections()["start_bonus"]["center_extension_limit"] == 34
    sections = restored.semantic_sections()
    sections["start_bonus"].update(center_extension_limit=67, force_extended_radius=True)
    edited = restored.with_sections(sections)
    loaded = CustomGenerationConfig.from_dict(json.loads(json.dumps(edited.to_dict())))
    assert loaded.semantic_sections()["start_bonus"]["center_extension_limit"] == 67
    assert loaded.digest == edited.digest != restored.digest
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_config = loaded
    controller._custom_section_baseline = original.semantic_sections()
    controller._custom_current_mode = lambda: "custom"
    controller._custom_language = lambda: "fr"
    controller._selection_changed = lambda: None
    assert controller._custom_section_is_modified("start_bonus")
    controller._custom_reset_section("start_bonus")
    assert controller._custom_config.semantic_sections()["start_bonus"] == original.semantic_sections()["start_bonus"]
    assert not controller._custom_section_is_modified("start_bonus")


@pytest.mark.parametrize("value,expected", [
    (0, 2), (-20, 2), (513, 512), ("42", 42), ("bad", 34),
    (None, 34), (float("nan"), 34), (float("inf"), 34),
])
def test_extension_normalization(value, expected):
    config = build_custom_config()
    sections = config.semantic_sections()
    sections["start_bonus"]["center_extension_limit"] = value
    assert config.with_sections(sections).semantic_sections()["start_bonus"]["center_extension_limit"] == expected


@pytest.mark.parametrize("limit", [2, 8, 34])
def test_configured_extension_keeps_ring_order_and_determinism(limit):
    support = np.ones((160, 160), dtype=bool)
    points = list(ordered_centers(support, 80, 80, 20, random.Random(9).shuffle,
                                 extension_limit=limit))
    distances = [hex_distance(80, 80, x, y) for x, y in points]
    assert set(distances) == set(range(18, 20 + limit + 1))
    assert [max(22, d) for d in distances] == sorted(max(22, d) for d in distances)
    assert len(points) == len(set(points))
    assert points == list(ordered_centers(support, 80, 80, 20, random.Random(9).shuffle,
                                         extension_limit=limit))


def _place(mode, kind, limit, *, force=True, blocked=False):
    config = build_custom_config(mode)
    sections = config.semantic_sections()
    bonus = sections["start_bonus"]
    bonus.update(force_extended_radius=force, center_extension_limit=limit)
    bonus["forest"].update(adult_trees_per_player=2, saplings_per_player=1)
    bonus["building_stones"]["anchors_per_player"] = 2
    bonus["mini_swamp"].update(radius=1, shape="hexagon")
    bonus["rocky_minerals"].update(radius_min=2, radius_max=2,
        coal={"enabled": True}, iron={"enabled": False}, gold={"enabled": False})
    bonus["lake_fish_river"].update(radius_min=2, radius_max=2,
        water_proximity_from_territory_border=0)
    config = config.with_sections(sections).with_start_packages(("start_" + kind,))
    state, content = _content_state(192, config)
    if blocked:
        # The entire normal band is illegal. Only the extended rings can work.
        yy, xx = np.indices(state.terrain.shape)
        sx, sy = state.starts[0]
        distance = np.maximum.reduce((abs(xx-sx), abs(yy-sy), abs((xx-sx)-(yy-sy))))
        state.terrain[(distance > 14) & (distance <= 36)] = 32
    before = state.area.copy()
    rng, pr = np.random.default_rng(8), random.Random(8)
    if kind in ("forest", "building_stones") and mode == "legacy":
        fn = apply_custom_legacy_start_forest if kind == "forest" else apply_custom_legacy_start_stones
        meta = fn(state, config.runtime_profile(), config.semantic_sections(), rng)
        records = meta["forests" if kind == "forest" else "groups"]
    elif kind == "forest":
        content._place_trees(state, rng, pr)
        meta = state.metadata["upgraded_trees"]
        records = meta["start_forests"]
    elif kind == "building_stones":
        content._place_building_stones(state, rng, pr, phase="start")
        meta = state.metadata["upgraded_stones"]
        records = meta["start_centers"]
    else:
        suffix = "mini_swamps" if kind == "mini_swamp" else kind
        getattr(content, "_place_start_" + suffix)(state, pr)
        meta = state.metadata["upgraded_start_" + suffix]
        records = (meta["zones"] if kind == "rocky_minerals" else
                   content._start_bonus_lake_records if kind == "lake_fish_river" else [])
    return state, meta, records, before


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
@pytest.mark.parametrize("kind", [key.removeprefix("start_") for key in ALL_START_PACKAGES])
def test_each_bonus_obeys_the_configured_centre_bound(mode, kind):
    _, short, records, _ = _place(mode, kind, 2, blocked=True)
    assert short["center_extension_limit"] == 2
    assert short["shortfalls"]
    assert not [r for r in records if "center_x" in r]
    state, placed, records, before = _place(mode, kind, 12, blocked=True)
    assert placed["center_extension_limit"] == 12
    assert not placed["shortfalls"]
    if kind == "mini_swamp":
        assert placed["starts_with_bonus"] == 1
        assert not np.array_equal(state.terrain, before[:, :, 1])
        return
    assert records
    sx, sy = state.starts[0]
    assert all(36 < hex_distance(sx, sy, r["center_x"], r["center_y"]) <= 46 for r in records)


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
@pytest.mark.parametrize("kind", [key.removeprefix("start_") for key in ALL_START_PACKAGES])
def test_extension_setting_has_no_effect_when_forcing_is_off(mode, kind):
    state_a, meta_a, _, _ = _place(mode, kind, 2, force=False)
    state_b, meta_b, _, _ = _place(mode, kind, 512, force=False)
    assert np.array_equal(state_a.area, state_b.area)
    assert meta_a == meta_b
    assert "center_extension_limit" not in meta_a
