from __future__ import annotations

from s3mapgen.generation.core import GenerationRequest
from s3mapgen.generation.generators.legacy import generate
from s3mapgen.generation.generators.legacy.profile import load_profile
from s3mapgen.generation.generators.legacy.resources import (
    _choose_mineral_radius,
    _choose_mineral_fill_r16,
    _hex_disk_area,
    _random_hex_selection_r16,
)


def test_native_mineral_hex_capacity_matches_the_rechecked_palette():
    assert {_hex_disk_area(radius) for radius in (3, 4, 5)} == {37, 61, 91}
    assert _hex_disk_area(6) == 127


def test_legacy_mineral_radius_sampler_is_discrete_and_weighted():
    resources = load_profile()["legacy_content"]["resources"]
    rng = __import__("numpy").random.default_rng(20260830)
    observed = {_choose_mineral_radius(resources, rng) for _ in range(512)}

    assert observed <= {3, 4, 5}
    assert observed == {3, 4, 5}


def test_legacy_mineral_selection_is_random_inside_one_hex_and_unique():
    np = __import__("numpy")
    yy, xx = np.indices((7, 7))
    dx, dy = xx - 3, yy - 3
    candidate = np.where(
        np.where(dx * dy >= 0, np.maximum(np.abs(dx), np.abs(dy)), np.abs(dx) + np.abs(dy)) <= 3,
        True,
        False,
    )
    y, x = _random_hex_selection_r16(
        candidate,
        0,
        0,
        (3, 3),
        19,
        np.random.default_rng(2026083013),
    )

    assert len(y) == 19
    assert len(set(zip(y.tolist(), x.tolist()))) == 19
    assert (3, 3) in set(zip(y.tolist(), x.tolist()))
    assert max(
        max(abs(int(cell_x) - 3), abs(int(cell_y) - 3))
        if (int(cell_x) - 3) * (int(cell_y) - 3) >= 0
        else abs(int(cell_x) - 3) + abs(int(cell_y) - 3)
        for cell_y, cell_x in zip(y, x)
    ) <= 3


def test_legacy_mineral_profile_exposes_random_zone_controls():
    resources = load_profile()["legacy_content"]["resources"]

    assert resources["mineral_support_ids"] == [32, 33, 34, 35, 128, 129]
    assert resources["mineral_mountain_occupancy_target"] == 0.53
    assert resources["mineral_zone_fill_max"] == 1.0
    assert resources["mineral_zone_fill_distribution"] == "uniform"
    assert resources["mineral_zone_fill_min_by_family"] == {
        "16": 0.20,
        "32": 0.26,
        "48": 0.29,
        "64": 0.28,
        "80": 0.29,
    }
    assert resources["quantity_multiplier"] == 1.0


def test_legacy_quantity_profile_keeps_native_integer_range():
    np = __import__("numpy")
    resources = load_profile()["legacy_content"]["resources"]
    raw = np.arange(1, 16, dtype=np.float64)
    quantities = np.minimum(
        int(resources["quantity_cap"]),
        np.floor(raw * float(resources["quantity_multiplier"]) + 0.5),
    ).astype(np.uint8)

    assert quantities.tolist() == list(range(1, 16))


def test_legacy_mineral_fill_sampler_stays_between_profile_bounds():
    np = __import__("numpy")
    resources = load_profile()["legacy_content"]["resources"]
    rng = np.random.default_rng(2026083014)
    for family, minimum in resources["mineral_zone_fill_min_by_family"].items():
        values = [_choose_mineral_fill_r16(resources, int(family), rng) for _ in range(64)]
        assert min(values) >= minimum
        assert max(values) <= 1.0


def test_legacy_generation_reports_elementary_hexes_without_shortfalls():
    state, validations = generate(
        GenerationRequest(side=384, players=4, seed=2026083004)
    )

    assert all(result.passed for result in validations if result.hard)
    assert state.metadata["mineral_hex_radius_choices"] == [3, 4, 5]
    assert all(
        not set(counts) - {"3", "4", "5"}
        for counts in state.metadata["mineral_hex_radius_counts"].values()
    )
    assert all(
        value == 0 for value in state.metadata["mineral_patch_shortfalls"].values()
    )
    assert state.metadata["mineral_support_ids"] == [32, 33, 34, 35, 128, 129]
    assert state.metadata["mineral_mountain_final_cells"] == sum(
        state.metadata["mineral_family_cells"].values()
    )
    assert state.metadata["mineral_mountain_occupancy"] > 0.45
