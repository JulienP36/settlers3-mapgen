from __future__ import annotations

import itertools

import numpy as np
import pytest

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.archetypes.island_amplitude import resolve_island_profile
from s3mapgen.generation.archetypes.island_teams import (
    group_players_by_team,
    player_island_labels,
)
from s3mapgen.generation.archetypes.large_islands import (
    _continental_land_percent,
    _inland_lake_count,
    _island_target_land_percent,
    _island_lakes,
    build_island_masks,
    place_island_starts,
    validate_island_contract,
)
from s3mapgen.generation.archetypes.profiles import default_archetype_profile
from s3mapgen.generation.archetypes.previews import generate_archetype_preview
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation.start_safety import validate_start_safety
from s3mapgen.map_data.constants import MOUNTAIN_FAMILY_IDS, WATER_IDS
from s3mapgen.map_data.hexgrid import component_labels, distance_from
from s3mapgen.map_data.model import MapState


def test_no_team_players_are_singletons_and_positive_teams_share_one_island():
    groups = group_players_by_team(6, (5, 5, 0, 2, 0, 2))
    assert groups == [[0, 1], [2], [3, 5], [4]]
    assert player_island_labels(groups, 6) == [1, 1, 2, 3, 4, 3]


@pytest.mark.parametrize(
    "groups",
    ([2, 1, 1], [4], [19, 1]),
)
def test_team_island_land_targets_are_proportional_and_connected(groups):
    side = 384 if sum(groups) <= 8 else 768
    labels, _, _, channel, _ = build_island_masks(
        side, len(groups), 2026101016, island_player_counts=groups,
    )
    sizes = [int(np.count_nonzero(labels == island)) for island in range(1, len(groups) + 1)]
    assert component_labels(labels > 0)[1] == len(groups)
    assert sizes == sorted(sizes, reverse=True)
    for island, count in enumerate(groups, 1):
        assert component_labels(labels == island)[1] == 1
        other = (labels > 0) & (labels != island)
        if other.any():
            from s3mapgen.map_data.hexgrid import distance_from

            assert int(distance_from(other)[labels == island].min()) >= channel
    ratios = [size / count for size, count in zip(sizes, sorted(groups, reverse=True))]
    assert max(ratios) - min(ratios) <= 1.0


@pytest.mark.parametrize("side", (384, 512, 640, 768))
def test_team_island_land_target_moves_from_island_profile_to_continental(side):
    many_islands = _island_target_land_percent(side, 8)
    two_islands = _island_target_land_percent(side, 2)
    one_island = _island_target_land_percent(side, 1)

    assert one_island >= two_islands > many_islands >= 56.5
    assert one_island == pytest.approx(_continental_land_percent(side), abs=1e-9)


def test_team_island_relief_uses_smallest_actual_team_island():
    profile = default_archetype_profile("team_islands")
    independent = resolve_island_profile(profile, 384, 4, player_teams=(0, 0, 0, 0))
    allied = resolve_island_profile(profile, 384, 4, player_teams=(7, 7, 7, 7))
    mixed = resolve_island_profile(profile, 384, 4, player_teams=(7, 7, 0, 0))
    assert allied["morphology"]["island_amplitude_percent"] > mixed["morphology"]["island_amplitude_percent"]
    assert mixed["morphology"]["island_amplitude_percent"] == independent["morphology"]["island_amplitude_percent"]
    assert allied["relief"]["mountain_threshold"] == 140


def test_team_island_preview_uses_selected_team_groups():
    preview = generate_archetype_preview(
        default_archetype_profile("team_islands"),
        384,
        2026101018,
        players=4,
        player_teams=(1, 1, 2, 2),
        relax_macro=False,
    )
    assert preview.island_mask is not None
    assert set(np.unique(preview.island_mask)) == {0, 1, 2}
    assert preview.mass.mass_count == 2
    sizes = np.bincount(preview.island_mask.ravel())[1:]
    assert sizes[0] == sizes[1]

    one_team = generate_archetype_preview(
        default_archetype_profile("team_islands"),
        384,
        2026101018,
        players=4,
        player_teams=(1, 1, 1, 1),
        relax_macro=False,
    )
    individual_islands = generate_archetype_preview(
        default_archetype_profile("team_islands"),
        384,
        2026101018,
        players=4,
        player_teams=(0, 0, 0, 0),
        relax_macro=False,
    )
    # Grouping is carried by source labels. Macro threshold classification can
    # expose a tiny coastal fragment (also present in the validated R62).
    assert set(np.unique(one_team.island_mask)) == {0, 1}
    assert one_team.mass.largest_mass_share_percent > 99.9
    assert individual_islands.mass.mass_count == 4
    assert np.count_nonzero(one_team.island_mask) > np.count_nonzero(
        individual_islands.island_mask
    )


def test_inland_lake_count_tracks_each_islands_physical_area():
    small_labels, *_ = build_island_masks(
        384, 1, 2026101015, island_player_counts=[8],
    )
    medium_labels, *_ = build_island_masks(
        512, 1, 2026101015, island_player_counts=[8],
    )
    large_labels, *_ = build_island_masks(
        768, 1, 2026101015, island_player_counts=[2],
    )
    areas = [
        int(np.count_nonzero(labels == 1))
        for labels in (small_labels, medium_labels, large_labels)
    ]

    # The number follows physical area, even with only two players.
    # Small maps gain one modest interior basin, not a player-scoped quota.
    assert areas[0] < 125_000 < areas[1] < 250_000 < areas[2]
    assert [_inland_lake_count(area) for area in areas] == [1, 3, 7]


def test_inland_lake_cells_keep_a_real_coast_buffer():
    yy, xx = np.indices((500, 500))
    island = (xx - 250) ** 2 + (yy - 250) ** 2 <= 220 ** 2
    depth = distance_from(~island)
    signal = np.zeros(int(np.count_nonzero(island)), dtype=np.float32)

    def flat_signal(x, y, wavelength, seed):
        return np.zeros(np.asarray(x).shape, dtype=np.float32)

    lake, count, cells = _island_lakes(
        island, depth, signal, 2026101015, flat_signal,
    )

    assert count == 2
    assert 500 < cells < 1500
    assert component_labels(lake)[1] == count
    assert np.all(island[lake])
    required_buffer = max(
        15,
        1.4 * np.sqrt((cells / count) / np.pi),
        .35 * float(depth[island].max()),
    )
    assert int(depth[lake].min()) >= required_buffer


def test_team_starts_share_their_island_and_keep_editor_spacing():
    state = MapState.empty(256)
    labels = np.zeros((256, 256), dtype=np.int16)
    labels[18:238, 18:86] = 1
    labels[18:238, 96:166] = 2
    labels[18:238, 176:238] = 3
    state.terrain[labels > 0] = 16
    state.metadata.update(
        players=4,
        large_island_topology={
            "team_islands": True,
            "requested_islands": 3,
            "player_island_labels": [1, 1, 2, 3],
            "preset_features_required": False,
        },
        large_island_features=[{"island": n} for n in range(1, 4)],
    )

    place_island_starts(state, 4, np.random.default_rng(42), labels, 14)

    slots = state.metadata["start_slot_indices"]
    island_labels = state.metadata["large_island_starts"]["island_labels"]
    assert slots == [0, 1, 2, 3]
    assert island_labels == [1, 1, 2, 3]
    assert [int(labels[y, x]) for x, y in state.starts] == island_labels
    assert all(check.passed for check in validate_start_safety(state))
    assert all(check.passed for check in validate_island_contract(state))
    assert all(
        (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 >= 50 ** 2
        for a, b in itertools.combinations(state.starts, 2)
    )


def test_team_start_candidates_prioritize_joint_mountain_and_river_access():
    state = MapState.empty(256)
    labels = np.zeros((256, 256), dtype=np.int16)
    labels[16:240, 16:240] = 1
    state.terrain[labels > 0] = 16
    # Two long resource fronts leave a broad, legal grass corridor between
    # them. Teammates can stay close to both without being forced to the coast.
    state.terrain[40:216, 75:79] = MOUNTAIN_FAMILY_IDS[0]
    state.terrain[40:216, 131:135] = 96
    state.metadata.update(
        players=4,
        large_island_topology={
            "team_islands": True,
            "requested_islands": 1,
            "player_island_labels": [1, 1, 1, 1],
            "preset_features_required": False,
        },
        large_island_features=[{"island": 1}],
    )

    place_island_starts(state, 4, np.random.default_rng(7), labels, 14)

    report = state.metadata["island_start_search"]
    assert report["strategy"] == "mountain_and_river_access_with_soft_spacing"
    assert len(report["selected_by_player"]) == 4
    assert report["resource_guard_islands"] == [1]
    assert all(
        player["mountain_distance_hex"] is not None
        and player["river_distance_hex"] is not None
        and player["mountain_distance_hex"] <= 38
        and player["river_distance_hex"] <= 38
        for player in report["selected_by_player"]
    )
    assert len(state.starts) == 4
    assert all(check.passed for check in validate_start_safety(state))


@pytest.mark.parametrize(
    "mode,teams,expected_sizes",
    [
        ("legacy", (1, 1, 2, 2), [2, 2]),
        ("upgraded", (1, 1, 0, 2), [2, 1, 1]),
        ("legacy", (3, 3, 3, 3), [4]),
        ("legacy", (0, 0, 0, 0), [1, 1, 1, 1]),
    ],
)
def test_team_islands_generate_grouped_starts_in_both_engines(mode, teams, expected_sizes):
    output = MapGenerator(
        LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE,
    ).generate(
        4,
        2026101017 + len(expected_sizes),
        mode=mode,
        archetype="team_islands",
        side=384,
        start_algorithm="auto",
        player_teams=teams,
    )
    state = output.state
    topology = state.metadata["large_island_topology"]
    relief = state.metadata["island_relief_source"]
    assert topology["team_islands"] is True
    assert topology["island_player_counts"] == expected_sizes
    profiles = relief["team_relief_profiles_by_island"]
    assert [profile["team_size"] if profile else 0 for profile in profiles] == [
        count if count > 1 else 0 for count in expected_sizes
    ]
    assert all(profile is None or profile["continuous_fields"] == 1 for profile in profiles)
    assert all(
        profile is None or profile["player_scoped_fields"] == 0
        for profile in profiles
    )
    assert [
        profile["ridge_weight"] if profile else 0.0 for profile in profiles
    ] == [0.28 if count >= 4 else 0.0 for count in expected_sizes]
    assert all(count >= 0 for count in relief["inland_lake_counts_by_island"])
    assert relief["team_lake_counts_by_island"] == relief["inland_lake_counts_by_island"]
    assert topology["player_island_labels"] == [
        int(value) for value in state.metadata["large_island_starts"]["player_island_labels"]
    ]
    land_sizes = [feature["land_cells"] for feature in state.metadata["large_island_features"]]
    actual_shares = np.asarray(land_sizes, dtype=np.float64) / sum(land_sizes)
    expected_shares = np.asarray(expected_sizes, dtype=np.float64) / sum(expected_sizes)
    assert np.allclose(actual_shares, expected_shares, atol=.01)
    assert len(state.starts) == 4
    assert state.metadata["start_slot_indices"] == [0, 1, 2, 3]
    assert [feature["island"] for feature in state.metadata["large_island_features"]] == list(
        range(1, len(expected_sizes) + 1)
    )
    assert all(check.passed for check in output.validations if check.hard), output.validations


def test_team_relief_scale_changes_gradually_with_group_size():
    from s3mapgen.generation.archetypes.large_islands import _team_relief_parameters

    parameters = [_team_relief_parameters(size) for size in (1, 2, 4, 8, 20)]
    wavelength_ratios = [item[0] for item in parameters]
    progression_powers = [item[1] for item in parameters]
    assert all(left > right for left, right in zip(wavelength_ratios[:3], wavelength_ratios[1:4]))
    assert all(left > right for left, right in zip(progression_powers[:3], progression_powers[1:4]))
    assert wavelength_ratios[3] == wavelength_ratios[4]
    assert progression_powers[3] == progression_powers[4]
    assert wavelength_ratios[-1] > .2


def test_large_team_island_uses_continuous_relief_and_inland_lakes():
    output = MapGenerator(
        LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE,
    ).generate(
        8,
        2026101015,
        mode="legacy",
        archetype="team_islands",
        side=768,
        start_algorithm="auto",
        player_teams=(1,) * 8,
    )
    state = output.state
    relief = state.metadata["island_relief_source"]
    assert relief["relief_distribution"] == "team_scaled_continuous_field"
    profile = relief["team_relief_profiles_by_island"][0]
    assert profile["team_size"] == 8
    assert profile["continuous_fields"] == 1
    assert profile["player_scoped_fields"] == 0
    assert profile["range_signal"] == "warped_continuous_ridges"
    assert profile["ridge_weight"] == 0.28
    assert .25 < profile["wavelength_ratio"] < .4
    assert relief["inland_lake_counts_by_island"] == [7]
    assert 4_000 < relief["inland_lake_cells_by_island"][0] < 7_000
    assert relief["team_lake_counts_by_island"] == relief["inland_lake_counts_by_island"]
    assert "relief_system_centers_by_island" not in relief

    land = ~np.isin(state.terrain, WATER_IDS)
    assert component_labels(land)[1] == 1
    water_labels, water_count = component_labels(np.isin(state.terrain, WATER_IDS))
    border_labels = set(np.unique(np.concatenate((
        water_labels[0], water_labels[-1], water_labels[:, 0], water_labels[:, -1],
    ))))
    border_labels.discard(0)
    inland_lakes = [
        int(np.count_nonzero(water_labels == label))
        for label in range(1, water_count + 1)
        if label not in border_labels
    ]
    assert sum(size >= 500 for size in inland_lakes) == 7, inland_lakes
    ocean = np.isin(water_labels, tuple(border_labels))
    ocean_distance = distance_from(ocean)
    inland_lake_labels = [
        label for label in range(1, water_count + 1)
        if label not in border_labels
        and int(np.count_nonzero(water_labels == label)) >= 500
    ]
    assert all(
        int(ocean_distance[water_labels == label].min()) >= 50
        for label in inland_lake_labels
    )

    mountain_cells = np.isin(state.terrain, MOUNTAIN_FAMILY_IDS)
    total_share = int(mountain_cells.sum()) / int(land.sum())
    assert 0.10 <= total_share <= 0.22
    mountain_labels, mountain_count = component_labels(mountain_cells)
    mountain_areas = np.bincount(
        mountain_labels.ravel(), minlength=mountain_count + 1,
    )[1:]
    assert np.count_nonzero(mountain_areas >= 20) >= 3
    assert len(state.starts) == 8
    assert all(check.passed for check in output.validations if check.hard), output.validations


def test_upgraded_large_team_island_uses_size_scaled_inland_lakes():
    output = MapGenerator(
        LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE,
    ).generate(
        8,
        2026101025,
        mode="upgraded",
        archetype="team_islands",
        side=768,
        start_algorithm="auto",
        player_teams=(1,) * 8,
    )

    state = output.state
    relief = state.metadata["island_relief_source"]
    assert relief["inland_lake_counts_by_island"] == [7]
    assert 4_000 < relief["inland_lake_cells_by_island"][0] < 7_000
    assert len(state.starts) == 8
    assert all(check.passed for check in output.validations if check.hard), output.validations


@pytest.mark.parametrize("base_mode", ("legacy", "upgraded"))
def test_team_islands_work_in_custom_profiles(base_mode):
    config = build_custom_config(base_mode, "team_islands")
    output = MapGenerator(
        LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE,
    ).generate(
        4,
        2026101020,
        mode="custom",
        archetype="team_islands",
        side=384,
        player_teams=(1, 1, 2, 2),
        custom_config=config,
    )
    assert output.state.metadata["large_island_topology"]["island_player_counts"] == [2, 2]
    assert all(check.passed for check in output.validations if check.hard), output.validations


@pytest.mark.parametrize("mode", ("legacy", "upgraded"))
@pytest.mark.parametrize("algorithm", ("classic", "fair"))
def test_team_islands_reject_start_strategies_that_cannot_guarantee_grouping(mode, algorithm):
    with pytest.raises(ValueError, match="coéquipiers commencent sur la même île"):
        MapGenerator(
            LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE,
        ).generate(
            4,
            42,
            mode=mode,
            archetype="team_islands",
            side=384,
            start_algorithm=algorithm,
            start_nations=(0, 0, 0, 0) if algorithm == "classic" else (),
            player_teams=(1, 1, 2, 2),
        )
