import random

import numpy as np
import pytest

import s3mapgen.generation.generators.upgraded.content as upgraded_content
from s3mapgen.generation.generators.upgraded.content import (
    UpgradedContent,
    _native_swamp_offsets,
)
from s3mapgen.generation.generators.upgraded.native_terrain import grow_native_bonus_river
from s3mapgen.generation.custom.bonus_water import native_lake_offsets, trace_native_river
from s3mapgen.generation.custom.bonus_minerals import hex_disc_offsets, transition_rings
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation.custom.start_packages import default_start_package_keys
from s3mapgen.generation.custom.terrain import terrain_transition_violations
from s3mapgen.generation.generators.upgraded.profile import load_profile
from s3mapgen.map_data.constants import HEX6, RIVER_IDS, ROCKY, SHORE, WATER_IDS
from s3mapgen.map_data.hexgrid import hex_distance
from s3mapgen.map_data.model import MapState


def test_all_declared_start_bonuses_are_active_by_default():
    assert default_start_package_keys() == ()


ALL_START_PACKAGES = (
    "start_forest",
    "start_building_stones",
    "start_mini_swamp",
    "start_rocky_minerals",
    "start_lake_fish_river",
)


def _content_state(side=500, config=None):
    state = MapState.empty(side)
    state.terrain[:] = 16
    state.height[:] = 1
    state.terrain[0, :] = 7
    state.terrain[-1, :] = 7
    state.terrain[:, 0] = 7
    state.terrain[:, -1] = 7
    state.height[0, :] = state.height[-1, :] = 0
    state.height[:, 0] = state.height[:, -1] = 0
    state.starts = [(side // 2, side // 2)]
    profile = config.runtime_profile() if config is not None else load_profile()
    content = UpgradedContent(profile)
    content.side = side
    content._start_bonus_reservation = np.zeros((side, side), dtype=bool)
    content._start_bonus_water = np.zeros((side, side), dtype=bool)
    return state, content


def test_custom_start_bonus_controls_reach_each_upgraded_start_pass():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["distance_from_border"] = 12
    sections["start_bonus"]["forest"].update(
        adult_trees_per_player=7,
        saplings_per_player=3,
        radius_min=3,
        radius_max=3,
    )
    sections["start_bonus"]["building_stones"].update(
        anchors_per_player=2,
        average_quantity=5.0,
        radius_min=3,
        radius_max=3,
    )
    sections["start_bonus"]["mini_swamp"].update(radius=1, shape="hexagon")
    sections["start_bonus"]["rocky_minerals"].update(
        radius_min=2,
        radius_max=2,
        coal={"enabled": True},
        iron={"enabled": False},
        gold={"enabled": False},
    )
    sections["minerals"]["average_quantity"]["coal"] = 5
    config = config.with_sections(sections).with_start_packages(ALL_START_PACKAGES)
    state, content = _content_state(256, config)

    content._place_start_mini_swamps(state, random.Random(1))
    content._place_start_rocky_minerals(state, random.Random(2))
    content._place_start_rocky_resources(state, np.random.default_rng(3))

    swamp = state.metadata["upgraded_start_mini_swamps"]
    assert swamp["shape"] == "hexagon"
    assert swamp["radius"] == 1
    assert swamp["requested_core_cells_per_start"] == 7
    assert swamp["requested_cells_per_start"] == 7
    assert swamp["placed_cells_per_start"] == [7]
    rocky = state.metadata["upgraded_start_rocky_minerals"]
    assert rocky["distance_from_border"] == 12
    assert rocky["radius_min"] == rocky["radius_max"] == 2
    assert rocky["zones_requested_per_player"] == 1
    assert rocky["placed_zones"] == 1
    assert rocky["zones"][0]["resource"] == "coal"
    assert np.mean(state.resources[state.resources != 0] & 0x0F) == pytest.approx(5.0)


@pytest.mark.parametrize(
    ("shape", "radius", "expected_cells"),
    (("hexagon", 1, 7), ("hexagon", 16, 817), ("native", 3, None)),
)
def test_start_mini_swamp_uses_shape_and_radius_instead_of_free_cell_quota(
    shape, radius, expected_cells
):
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["mini_swamp"].update(radius=radius, shape=shape)
    config = config.with_sections(sections).with_start_packages(("start_mini_swamp",))
    state, content = _content_state(256, config)

    content._place_start_mini_swamps(state, random.Random(4))

    metadata = state.metadata["upgraded_start_mini_swamps"]
    assert metadata["shape"] == shape
    assert metadata["radius"] == radius
    assert metadata["requested_core_cells_per_start"] == 1 + 3 * radius * (radius + 1)
    if expected_cells is None:
        expected_cells = len(_native_swamp_offsets(radius, random.Random(4)))
    assert metadata["requested_cells_per_start"] == expected_cells
    assert metadata["placed_cells_per_start"] == [expected_cells]
    assert terrain_transition_violations(state.terrain)["total"] == 0


def test_native_start_mini_swamp_uses_the_global_swamp_family_plan():
    offsets = _native_swamp_offsets(20, random.Random(4))
    hexagon = {
        (x, y)
        for y in range(-20, 21)
        for x in range(-20, 21)
        if hex_distance(0, 0, x, y) <= 20
    }

    assert offsets
    assert len(offsets) < len(hexagon)
    assert set(offsets) != hexagon
    assert max(hex_distance(0, 0, x, y) for x, y in offsets) <= 20


def test_native_start_mini_swamp_generates_one_shape_per_start(monkeypatch):
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["mini_swamp"].update(radius=3, shape="native")
    config = config.with_sections(sections).with_start_packages(("start_mini_swamp",))
    state, content = _content_state(256, config)
    state.starts = [(64, 64), (64, 192), (192, 64), (192, 192)]

    generated = [
        [(0, 0)],
        [(0, 0), (1, 0)],
        [(0, 0), (1, 0), (0, 1)],
        [(0, 0), (1, 0), (0, 1), (-1, 0)],
    ]
    calls = []

    def fake_native_offsets(radius, pr):
        calls.append((radius, pr.getstate()))
        return generated[len(calls) - 1]

    monkeypatch.setattr(upgraded_content, "_native_swamp_offsets", fake_native_offsets)
    content._place_start_mini_swamps(state, random.Random(4))

    metadata = state.metadata["upgraded_start_mini_swamps"]
    assert len(calls) == 4
    assert metadata["requested_cells_by_start"] == [1, 2, 3, 4]
    assert metadata["native_shape_cells_per_start"] == [1, 2, 3, 4]
    assert metadata["placed_cells_per_start"] == [1, 2, 3, 4]


def test_native_lake_shape_is_bounded_rounded_and_seeded():
    first = native_lake_offsets(9, random.Random(4))
    second = native_lake_offsets(9, random.Random(5))
    full = len(hex_disc_offsets(9))
    assert first and second
    assert first != second
    assert len(first) < full and len(second) < full
    assert max(hex_distance(0, 0, x, y) for x, y in first) <= 9
    assert max(hex_distance(0, 0, x, y) for x, y in second) <= 9


def test_bonus_native_river_is_connected_curved_and_stops_at_water():
    side = 128
    terrain = np.full((side, side), 16, dtype=np.uint8)
    height = np.ones((side, side), dtype=np.uint8)
    target = np.zeros((side, side), dtype=bool)
    target[0, :] = True
    target[-1, :] = True
    target[:, 0] = True
    target[:, -1] = True
    passable = terrain == 16
    route = trace_native_river(
        terrain,
        height,
        (64, 64),
        target,
        passable,
        rng=random.Random(17),
    )
    assert route
    assert len(route) > 20
    assert all(
        hex_distance(*route[index], *route[index + 1]) == 1
        for index in range(len(route) - 1)
    )
    assert any(
        route[index + 1][0] - route[index][0]
        != route[index][0] - route[index - 1][0]
        or route[index + 1][1] - route[index][1]
        != route[index][1] - route[index - 1][1]
        for index in range(1, len(route) - 1)
    )
    end_x, end_y = route[-1]
    assert any(target[end_y + dy, end_x + dx] for dx, dy in HEX6)
    assert not any(target[y, x] for x, y in route)


def test_bonus_native_stem_uses_one_native_id_and_never_routes_to_global_water():
    side = 128
    terrain = np.full((side, side), 16, dtype=np.uint8)
    height = np.ones((side, side), dtype=np.uint8)
    cx = cy = side // 2
    core_offsets = native_lake_offsets(2, random.Random(17))
    inner_offsets, _ = transition_rings(core_offsets, depth=2)
    core = [(cx + dx, cy + dy) for dx, dy in core_offsets]
    inner = [(cx + dx, cy + dy) for dx, dy in inner_offsets]
    for x, y in core + inner:
        terrain[y, x] = 0
    # A distant sea is present, but it is not a route target.
    terrain[0, :] = 0
    allowed = terrain == 16
    marker = np.zeros_like(terrain, dtype=np.uint8)

    route = None
    trial = None
    for mouth in inner:
        trial = terrain.copy()
        trial[mouth[1], mouth[0]] = 0
        route = grow_native_bonus_river(
            trial,
            height,
            mouth,
            marker=marker.copy(),
            allowed=allowed,
        )
        if route:
            break

    assert route
    assert trial is not None
    assert len(route) <= 70
    assert set(int(trial[y, x]) for x, y in route) == {RIVER_IDS[0]}
    assert not any(y == 0 for _, y in route)
    assert all(
        hex_distance(*route[index], *route[index + 1]) == 1
        for index in range(len(route) - 1)
    )


def test_lake_shape_selector_keeps_hexagon_compatibility():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["lake_fish_river"].update(
        radius_min=3,
        radius_max=3,
        shape="hexagon",
        water_proximity_from_territory_border=0,
    )
    config = config.with_sections(sections).with_start_packages(("start_lake_fish_river",))
    state, content = _content_state(256, config)
    content._place_start_lake_fish_river(state, random.Random(7))
    metadata = state.metadata["upgraded_start_lake_fish_river"]
    record = content._start_bonus_lake_records[0]
    assert metadata["shape"] == "hexagon"
    assert len(record["core_points"]) == 1 + 3 * 3 * 4
    assert len(record["shore_inner_points"]) == 6 * 4
    assert len(record["shore_outer_points"]) == 6 * 5
    assert len(record["shore_points"]) == 6 * 4 + 6 * 5


def test_start_rocky_bonus_has_full_independent_mineral_cores_and_legal_transitions():
    state, content = _content_state(256)
    before_height = state.height.copy()
    content._place_start_rocky_minerals(state, random.Random(7))
    content._place_start_rocky_resources(state, np.random.default_rng(8))

    metadata = state.metadata["upgraded_start_rocky_minerals"]
    assert metadata["placed_zones"] == 3
    assert metadata["start_bonus_cells"] == metadata["placed_core_cells"]
    assert np.array_equal(state.height, before_height)
    for zone in metadata["zones"]:
        cx, cy, radius = zone["center_x"], zone["center_y"], zone["radius"]
        family = zone["family"]
        core = [
            (x, y)
            for y in range(cy - radius, cy + radius + 1)
            for x in range(cx - radius, cx + radius + 1)
            if hex_distance(cx, cy, x, y) <= radius
        ]
        assert all(state.terrain[y, x] == ROCKY for x, y in core)
        assert all((int(state.resources[y, x]) & 0xF0) == family for x, y in core)
    assert terrain_transition_violations(state.terrain)["total"] == 0


def test_start_lake_bonus_uses_shore_fish_and_a_legal_river_without_overwriting_native_water():
    state, content = _content_state(500)
    native_edge = state.terrain.copy()
    content._place_start_lake_fish_river(state, random.Random(9))
    metadata = state.metadata["upgraded_start_lake_fish_river"]
    assert metadata["lakes_placed"] == 1
    assert metadata["river_algorithm"] == "native_single_system"
    assert metadata["river_global_target_search"] is False
    assert np.array_equal(state.terrain[0, :], native_edge[0, :])
    assert np.array_equal(state.terrain[:, 0], native_edge[:, 0])

    lake = metadata["per_player"][0]["lake"]
    cx, cy, radius = lake["center_x"], lake["center_y"], lake["radius"]
    record = content._start_bonus_lake_records[0]
    core = list(record["core_points"])
    shore = list(record["shore_points"])
    assert all(state.terrain[y, x] in WATER_IDS for x, y in core)
    assert any(state.terrain[y, x] in RIVER_IDS for x, y in shore)
    assert all(
        all(
            not (0 <= x + dx < state.side and 0 <= y + dy < state.side)
            or state.terrain[y + dy, x + dx] in (*WATER_IDS, SHORE, *RIVER_IDS)
            for dx, dy in HEX6
        )
        for x, y in core
    )

    content._generate_fish(state, np.random.default_rng(10))
    content._place_start_lake_fish(state, np.random.default_rng(11))
    assert metadata["fish_cells"] == round(len(core) * metadata["fish_fill_percent"] / 100.0)
    assert np.count_nonzero(np.isin(state.terrain, RIVER_IDS) & ((state.resources & 0x0F) > 0)) == 0


def test_custom_lake_controls_use_global_fish_mean_and_target_rivers():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["lake_fish_river"].update(
        radius_min=4,
        radius_max=4,
        water_proximity_from_territory_border=0,
        river_target_per_lake=2,
        fish_fill_percent=25.0,
    )
    sections["fish"]["average_quantity"] = 7
    state, content = _content_state(
        500,
        config.with_sections(sections).with_start_packages(("start_lake_fish_river",)),
    )
    content._place_start_lake_fish_river(state, random.Random(14))
    metadata = state.metadata["upgraded_start_lake_fish_river"]

    assert metadata["radius_min"] == metadata["radius_max"] == 4
    assert metadata["water_proximity_from_territory_border"] == 0
    assert metadata["river_target_per_lake"] == 2
    assert metadata["lakes_placed"] == 1
    assert 1 <= metadata["rivers_placed"] <= 2
    content._place_start_lake_fish(state, np.random.default_rng(15))
    lake = metadata["per_player"][0]["lake"]
    assert lake["fish_cells"] == round(lake["core_cells"] * 25.0 / 100.0)
    assert lake["fish_mean"] == pytest.approx(7.0)


def test_zero_water_proximity_threshold_disables_native_water_filter():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["lake_fish_river"].update(
        radius_min=2,
        radius_max=2,
        water_proximity_from_territory_border=0,
    )
    config = config.with_sections(sections).with_start_packages(("start_lake_fish_river",))
    state, content = _content_state(256, config)
    sx, sy = state.starts[0]
    # Native water inside the starting territory would reject the start when
    # the filter is enabled, but must be ignored when the configured value is 0.
    state.terrain[sy, sx] = 0

    content._place_start_lake_fish_river(state, random.Random(3))

    metadata = state.metadata["upgraded_start_lake_fish_river"]
    player = metadata["per_player"][0]
    assert metadata["water_proximity_filter_enabled"] is False
    assert metadata["lakes_placed"] == 1
    assert player["rejection_counts"]["water_proximity"] == 0


def test_positive_water_proximity_threshold_reports_native_water_rejection():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["lake_fish_river"].update(
        radius_min=2,
        radius_max=2,
        water_proximity_from_territory_border=1,
    )
    config = config.with_sections(sections).with_start_packages(("start_lake_fish_river",))
    state, content = _content_state(256, config)
    sx, sy = state.starts[0]
    state.terrain[sy, sx] = 0

    content._place_start_lake_fish_river(state, random.Random(3))

    metadata = state.metadata["upgraded_start_lake_fish_river"]
    player = metadata["per_player"][0]
    assert metadata["water_proximity_filter_enabled"] is True
    assert metadata["lakes_placed"] == 0
    assert player["skipped_reason"] == "existing_water_within_proximity_threshold"
    assert player["rejection_counts"]["water_proximity"] == 1
    assert metadata["rejection_totals"]["water_proximity"] == 1


def test_lake_placement_diagnostics_report_missing_support_centres():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["start_bonus"]["lake_fish_river"].update(
        radius_min=2,
        radius_max=2,
        water_proximity_from_territory_border=0,
    )
    config = config.with_sections(sections).with_start_packages(("start_lake_fish_river",))
    state, content = _content_state(128, config)
    state.terrain[1:-1, 1:-1] = 32

    content._place_start_lake_fish_river(state, random.Random(3))

    metadata = state.metadata["upgraded_start_lake_fish_river"]
    player = metadata["per_player"][0]
    assert metadata["candidate_attempts"] == 0
    assert metadata["candidate_accepts"] == 0
    assert player["rejection_counts"]["no_center_candidates"] == 1
    assert metadata["rejection_totals"]["no_center_candidates"] == 1


def test_force_extended_radius_is_a_common_bonus_switch():
    state, content = _content_state(128)
    blocked = np.zeros_like(state.terrain, dtype=bool)
    sx = sy = state.side // 2
    desired = 10
    for y in range(state.side):
        for x in range(state.side):
            if hex_distance(sx, sy, x, y) <= desired + 2:
                blocked[y, x] = True

    local = content._bonus_center_candidates(
        state,
        sx,
        sy,
        desired,
        state.terrain,
        blocked,
        random.Random(20),
        support_mask=np.ones_like(state.terrain, dtype=bool),
        force_extended=False,
    )
    extended = content._bonus_center_candidates(
        state,
        sx,
        sy,
        desired,
        state.terrain,
        blocked,
        random.Random(20),
        support_mask=np.ones_like(state.terrain, dtype=bool),
        force_extended=True,
    )

    assert local == []
    assert extended
    assert all(hex_distance(sx, sy, x, y) > desired + 2 for x, y in extended)
