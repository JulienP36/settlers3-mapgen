"""Five-family bonus placement and compatibility with three-family profiles."""
import json
import random

import numpy as np
import pytest

from s3mapgen.application.custom.controller import CustomGeneratorController
from s3mapgen.generation.custom import (
    CustomGenerationConfig, build_custom_config, MINERAL_KEYS, MINERAL_IDS,
    rocky_total_cells_max, rocky_equivalent_radius, rocky_proportional_targets,
)
from s3mapgen.generation.custom.terrain import terrain_transition_violations
from s3mapgen.map_data.constants import HEX6, ROCKY
from s3mapgen.map_data.hexgrid import hex_distance
from test_upgraded_start_bonus_zones import _content_state


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_optional_families_stay_off_in_defaults_old_profiles_and_bonus_reset(mode):
    config = build_custom_config(mode)
    defaults = config.semantic_sections()
    rocky = defaults["start_bonus"]["rocky_minerals"]
    assert [name for name in MINERAL_KEYS if rocky[name]["enabled"]] == ["coal", "iron", "gold"]
    assert rocky["total_core_cells"] == 183
    old = config.with_sections(defaults).to_dict()
    for name in ("gems", "sulfur"):
        del old["sections"]["start_bonus"]["rocky_minerals"][name]
    restored = CustomGenerationConfig.from_dict(json.loads(json.dumps(old)))
    assert restored.semantic_sections() == defaults
    changed = restored.semantic_sections()
    for name in ("gems", "sulfur"):
        changed["start_bonus"]["rocky_minerals"][name].update(enabled=True, core_cells=42, average_quantity=12)
    changed["start_bonus"]["rocky_minerals"]["surface_mode"] = "custom"
    edited = restored.with_sections(changed).with_start_packages(("start_rocky_minerals",))
    loaded = CustomGenerationConfig.from_dict(json.loads(json.dumps(edited.to_dict())))
    assert loaded.semantic_sections() == edited.semantic_sections()
    assert loaded.digest == edited.digest != restored.digest
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_config = loaded
    controller._custom_section_baseline = defaults
    controller._custom_current_mode = lambda: "custom"
    controller._custom_language = lambda: "fr"
    controller._selection_changed = lambda: None
    assert controller._custom_section_is_modified("start_bonus")
    controller._custom_reset_section("start_bonus")
    assert controller._custom_config.semantic_sections() == defaults


def test_five_family_surface_limits_and_prorata_are_consistent():
    assert rocky_total_cells_max(0) == 0
    assert rocky_total_cells_max(3) == 2460
    assert rocky_total_cells_max(5) == rocky_total_cells_max(99) == 4100
    assert rocky_equivalent_radius(305, 5) == 4
    assert rocky_equivalent_radius(4085, 5) == 16
    assert rocky_proportional_targets(50, ["gems", "sulfur"], {"gems": 2, "sulfur": 3}) == {"gems": 20, "sulfur": 30}
    capped = rocky_proportional_targets(4100, MINERAL_KEYS, {"coal": 1000, "sulfur": 1})
    assert capped == {key: 820 for key in MINERAL_KEYS}
    assert rocky_proportional_targets(95, MINERAL_KEYS, {}) == {key: 19 for key in MINERAL_KEYS}


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_optional_inputs_are_bounded_and_count_towards_total_capacity(mode):
    config = build_custom_config(mode)
    sections = config.semantic_sections()
    rocky = sections["start_bonus"]["rocky_minerals"]
    rocky.update(surface_mode="proportional", total_core_cells=9000)
    for name in MINERAL_KEYS:
        rocky[name].update(enabled=True, core_cells=9999, average_quantity=99)
    normalized = config.with_sections(sections).semantic_sections()["start_bonus"]["rocky_minerals"]
    assert normalized["total_core_cells"] == 4100
    assert all(normalized[key]["core_cells"] == 820 and normalized[key]["average_quantity"] == 15 for key in MINERAL_KEYS)
    rocky["gems"].update(core_cells=-1, average_quantity=-1)
    normalized = config.with_sections(sections).semantic_sections()["start_bonus"]["rocky_minerals"]
    assert normalized["gems"]["core_cells"] == normalized["gems"]["average_quantity"] == 1


def _config(mode, shape, surface_mode, active=MINERAL_KEYS):
    config = build_custom_config(mode)
    sections = config.semantic_sections()
    sections["start_bonus"]["force_extended_radius"] = True
    sections["minerals"]["shares"] = {key: 20 for key in MINERAL_KEYS}
    sections["minerals"]["average_quantity"] = {key: 1 for key in MINERAL_KEYS}
    rocky = sections["start_bonus"]["rocky_minerals"]
    rocky.update(shape=shape, surface_mode=surface_mode, radius_min=2, radius_max=2,
                 total_core_cells=135)
    for index, name in enumerate(MINERAL_KEYS):
        rocky[name].update(enabled=name in active, core_cells=19+index*4, average_quantity=5+index)
    return config.with_sections(sections).with_start_packages(("start_rocky_minerals",))


def _assert_connected(points):
    points = set(points)
    seen = {next(iter(points))}
    stack = list(seen)
    while stack:
        x, y = stack.pop()
        for dx, dy in HEX6:
            neighbour = x+dx, y+dy
            if neighbour in points and neighbour not in seen:
                seen.add(neighbour)
                stack.append(neighbour)
    assert seen == points


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
@pytest.mark.parametrize("shape", ["hexagon", "organic"])
@pytest.mark.parametrize("surface_mode", ["equal", "proportional", "custom"])
def test_five_minerals_place_connected_full_cores_and_preserve_global_accounting(mode, shape, surface_mode):
    state, content = _content_state(256, _config(mode, shape, surface_mode))
    state.metadata["upgraded_mineral_targets"] = {f"{MINERAL_IDS[key]:02x}": 100+index for index, key in enumerate(MINERAL_KEYS)}
    previous_targets = state.metadata["upgraded_mineral_targets"].copy()
    state.metadata["upgraded_minerals"] = {}
    before_height = state.height.copy()
    content._place_start_rocky_minerals(state, random.Random(19))
    content._place_start_rocky_resources(state, np.random.default_rng(23))
    meta = state.metadata["upgraded_start_rocky_minerals"]
    assert meta["placed_zones"] == meta["zones_requested"] == 5
    assert not meta["shortfalls"]
    assert state.metadata["upgraded_mineral_global_targets"] == previous_targets
    assert np.array_equal(state.height, before_height)
    assert terrain_transition_violations(state.terrain)["total"] == 0
    assert meta["global_quota_excludes_start_bonus"]
    by_resource = {zone["resource"]: zone for zone in meta["zones"]}
    assert set(by_resource) == set(MINERAL_KEYS)
    for index, name in enumerate(MINERAL_KEYS):
        zone = by_resource[name]
        expected_area = 19 if surface_mode == "equal" else 27 if surface_mode == "proportional" else 19+index*4
        assert zone["core_cells"] == zone["resource_cells"] == expected_area
        assert zone["quantity_mean_target"] == zone["resource_mean"] == 5+index
        assert zone["resource_stock"] == expected_area*(5+index)
        points = [tuple(point) for point in zone["core_points"]]
        _assert_connected(points)
        assert all(state.terrain[y, x] == ROCKY for x, y in points)
        assert all((int(state.resources[y, x]) & 0xF0) == MINERAL_IDS[name] for x, y in points)
        assert all(1 <= (int(state.resources[y, x]) & 0x0F) <= 15 for x, y in points)
        assert all(hex_distance(*state.starts[0], x, y) > 14 for x, y in points)
        key = f"{MINERAL_IDS[name]:02x}"
        assert state.metadata["upgraded_mineral_targets"][key] == previous_targets[key]+expected_area


@pytest.mark.parametrize("family", ["gems", "sulfur"])
def test_one_optional_family_can_run_alone_and_reports_illegal_support(family):
    config = _config("upgraded", "organic", "custom", active=(family,))
    state, content = _content_state(256, config)
    content._place_start_rocky_minerals(state, random.Random(19))
    content._place_start_rocky_resources(state, np.random.default_rng(23))
    meta = state.metadata["upgraded_start_rocky_minerals"]
    assert len(meta["zones"]) == 1 and meta["zones"][0]["resource"] == family
    assert not meta["shortfalls"]
    state, content = _content_state(256, config)
    content._start_bonus_reservation[:] = True
    before = state.area.copy()
    content._place_start_rocky_minerals(state, random.Random(19))
    content._place_start_rocky_resources(state, np.random.default_rng(23))
    assert np.array_equal(state.area, before)
    assert state.metadata["upgraded_start_rocky_minerals"]["placed_zones"] == 0
    assert state.metadata["upgraded_start_rocky_minerals"]["shortfalls"][0]["resource"] == family


def test_prorata_uses_only_the_two_enabled_optional_families():
    config = _config("upgraded", "organic", "proportional", active=("gems", "sulfur"))
    sections = config.semantic_sections()
    sections["minerals"]["shares"].update(coal=80, iron=5, gold=10, gems=2, sulfur=3)
    sections["start_bonus"]["rocky_minerals"]["total_core_cells"] = 50
    state, content = _content_state(256, config.with_sections(sections))
    content._place_start_rocky_minerals(state, random.Random(19))
    meta = state.metadata["upgraded_start_rocky_minerals"]
    assert meta["surface_targets"] == {"gems": 20, "sulfur": 30}
    assert {zone["resource"]: zone["core_cells"] for zone in meta["zones"]} == {"gems": 20, "sulfur": 30}
    assert not meta["shortfalls"]


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
@pytest.mark.parametrize("mean", [1, 15])
def test_optional_resource_bytes_keep_the_family_at_quantity_extremes(mode, mean):
    config = _config(mode, "hexagon", "custom", active=("gems", "sulfur"))
    sections = config.semantic_sections()
    for name in ("gems", "sulfur"):
        sections["start_bonus"]["rocky_minerals"][name]["average_quantity"] = mean
    state, content = _content_state(256, config.with_sections(sections))
    content._place_start_rocky_minerals(state, random.Random(19))
    content._place_start_rocky_resources(state, np.random.default_rng(23))
    meta = state.metadata["upgraded_start_rocky_minerals"]
    assert len(meta["zones"]) == 2
    for zone in meta["zones"]:
        assert all(state.resources[y, x] == (MINERAL_IDS[zone["resource"]] | mean) for x, y in zone["core_points"])


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_optional_family_switches_do_not_enable_a_disabled_package(mode):
    config = _config(mode, "organic", "custom", active=("gems", "sulfur")).with_start_packages(())
    state, content = _content_state(256, config)
    before = state.area.copy()
    content._place_start_rocky_minerals(state, random.Random(19))
    content._place_start_rocky_resources(state, np.random.default_rng(23))
    assert np.array_equal(before, state.area)
    meta = state.metadata["upgraded_start_rocky_minerals"]
    assert not meta["enabled"] and meta["zones_requested"] == 0


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_controller_edits_each_optional_bonus_value_through_the_normal_section_handler(mode):
    config = build_custom_config(mode)
    controller = CustomGeneratorController.__new__(CustomGeneratorController)
    controller._custom_config = config
    controller._custom_section_baseline = config.semantic_sections()
    controller._custom_language = lambda: "fr"
    controller._custom_current_mode = lambda: "custom"
    controller._custom_current_archetype = lambda: "continental"
    controller._custom_ensure_config = lambda *args: controller._custom_config
    controller._custom_activate = lambda config: setattr(controller, "_custom_config", config)
    for name in ("gems", "sulfur"):
        prefix = ("start_bonus", "rocky_minerals", name)
        controller._custom_section_changed(prefix+("enabled",), True)
        controller._custom_section_changed(prefix+("core_cells",), "31")
        controller._custom_section_changed(prefix+("average_quantity",), "12")
    rocky = controller._custom_config.semantic_sections()["start_bonus"]["rocky_minerals"]
    assert all(rocky[name]["enabled"] and rocky[name]["core_cells"] == 31 and rocky[name]["average_quantity"] == 12 for name in ("gems", "sulfur"))
    assert controller._custom_section_is_modified("start_bonus")
