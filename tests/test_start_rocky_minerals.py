import random

import numpy as np

from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation.custom.bonus_minerals import compact_hex_offsets, organic_offsets
from s3mapgen.generation.custom.terrain import terrain_transition_violations
from s3mapgen.generation.generators.upgraded.content import UpgradedContent
from s3mapgen.map_data.constants import HEX6, ROCKY
from s3mapgen.map_data.hexgrid import hex_distance
from s3mapgen.map_data.model import MapState


def _state_and_content(sections):
    config = build_custom_config("upgraded").with_sections(sections).with_start_packages(
        ("start_rocky_minerals",)
    )
    side = 256
    state = MapState.empty(side)
    state.terrain[:] = 16
    state.terrain[0, :] = state.terrain[-1, :] = 7
    state.terrain[:, 0] = state.terrain[:, -1] = 7
    state.starts = [(side // 2, side // 2)]
    content = UpgradedContent(config.runtime_profile())
    content.side = side
    content._start_bonus_reservation = np.zeros((side, side), dtype=bool)
    return state, content


def test_organic_shape_is_exact_connected_and_not_the_compact_hex_cap():
    points = set(organic_offsets(43, random.Random(101)))

    assert len(points) == 43
    assert (0, 0) in points
    seen = {(0, 0)}
    pending = [(0, 0)]
    while pending:
        x, y = pending.pop()
        for dx, dy in HEX6:
            neighbour = (x + dx, y + dy)
            if neighbour in points and neighbour not in seen:
                seen.add(neighbour)
                pending.append(neighbour)
    assert seen == points
    assert max(hex_distance(0, 0, x, y) for x, y in points) <= 5
    assert points != set(compact_hex_offsets(43, random.Random(101)))


def test_organic_shape_is_compensated_for_parallelogram_and_varies_smoothly():
    first = set(organic_offsets(61, random.Random(7)))
    second = set(organic_offsets(61, random.Random(31)))
    projected = [(2 * x - y, 2 * y) for x, y in first]
    width = max(x for x, _ in projected) - min(x for x, _ in projected) + 1
    height = max(y for _, y in projected) - min(y for _, y in projected) + 1

    # The normal preview doubles the hex-grid x/y axes into this space.  A
    # compensated organic core should remain broadly rounded there rather
    # than inheriting a fixed parallelogram stretch.
    assert 0.65 <= width / height <= 1.55
    # The low-frequency contour parameters must produce more than a single
    # reusable silhouette for the same requested surface.
    assert len(first.symmetric_difference(second)) >= 12


def test_organic_core_is_exactly_full_and_keeps_legal_transitions():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    rocky = sections["start_bonus"]["rocky_minerals"]
    rocky.update(shape="organic", surface_mode="custom", radius_min=2, radius_max=2)
    rocky["coal"].update(enabled=True, core_cells=43, average_quantity=6)
    rocky["iron"].update(enabled=False)
    rocky["gold"].update(enabled=False)
    state, content = _state_and_content(sections)

    content._place_start_rocky_minerals(state, random.Random(101))
    content._place_start_rocky_resources(state, np.random.default_rng(102))
    metadata = state.metadata["upgraded_start_rocky_minerals"]
    zone = metadata["zones"][0]

    assert zone["shape"] == "organic"
    assert zone["surface_mode"] == "custom"
    assert zone["core_cells"] == zone["requested_core_cells"] == 43
    assert all(state.terrain[y][x] == ROCKY for x, y in zone["core_points"])
    assert all((int(state.resources[y][x]) & 0xF0) == 0x10 for x, y in zone["core_points"])
    assert zone["quantity_mean_target"] == 6
    assert terrain_transition_violations(state.terrain)["total"] == 0


def test_proportional_surface_renormalizes_global_deposit_shares_to_active_families():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    rocky = sections["start_bonus"]["rocky_minerals"]
    rocky.update(shape="organic", surface_mode="proportional", total_core_cells=47)
    rocky["coal"]["enabled"] = True
    rocky["iron"]["enabled"] = True
    rocky["gold"]["enabled"] = False
    sections["minerals"]["shares"].update(coal=70, iron=30, gold=0)
    state, content = _state_and_content(sections)

    content._place_start_rocky_minerals(state, random.Random(103))
    metadata = state.metadata["upgraded_start_rocky_minerals"]
    by_resource = {zone["resource"]: zone for zone in metadata["zones"]}

    assert metadata["surface_mode"] == "proportional"
    assert metadata["surface_targets"] == {"coal": 33, "iron": 14}
    assert by_resource["coal"]["core_cells"] == 33
    assert by_resource["iron"]["core_cells"] == 14
    assert sum(zone["core_cells"] for zone in by_resource.values()) == 47


def test_zone_quantity_defaults_follow_global_mineral_mean_and_can_be_overridden():
    config = build_custom_config("upgraded")
    sections = config.semantic_sections()
    sections["minerals"]["average_quantity"].update(coal=5, iron=8, gold=10)
    rocky = sections["start_bonus"]["rocky_minerals"]
    rocky.update(surface_mode="custom", shape="hexagon")
    rocky["coal"].update(enabled=True, core_cells=19)
    rocky["iron"].update(enabled=False)
    rocky["gold"].update(enabled=False)
    state, content = _state_and_content(sections)
    content._place_start_rocky_minerals(state, random.Random(104))
    content._place_start_rocky_resources(state, np.random.default_rng(105))
    zone = state.metadata["upgraded_start_rocky_minerals"]["zones"][0]

    assert zone["quantity_mean_target"] == 5
    sections["start_bonus"]["rocky_minerals"]["coal"]["average_quantity"] = 12
    state, content = _state_and_content(sections)
    content._place_start_rocky_minerals(state, random.Random(106))
    content._place_start_rocky_resources(state, np.random.default_rng(107))
    zone = state.metadata["upgraded_start_rocky_minerals"]["zones"][0]
    assert zone["quantity_mean_target"] == 12
