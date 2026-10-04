"""Selectable river policy: coastal topology, compatibility and routing."""

from pathlib import Path

import numpy as np
import pytest

from s3mapgen.generation.custom import CustomGenerationConfig, build_custom_config
from s3mapgen.generation.archetypes.island_detail import add_plain_detail
from s3mapgen.generation.generators.legacy import native_terrain as legacy
from s3mapgen.generation.generators.upgraded import native_terrain as upgraded
from s3mapgen.map_data.hexgrid import component_labels, neighbor_count


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_river_algorithm_persists_and_old_configs_default_to_native(mode):
    config = build_custom_config(mode)
    sections = config.semantic_sections()
    assert sections["rivers"]["algorithm"] == "native"
    sections["rivers"]["algorithm"] = "improved"
    edited = config.with_sections(sections)
    restored = CustomGenerationConfig.from_dict(edited.to_dict())
    assert restored.semantic_sections()["rivers"]["algorithm"] == "improved"
    assert restored.digest == edited.digest
    sections["rivers"].pop("algorithm")
    assert config.with_sections(sections).semantic_sections()["rivers"]["algorithm"] == "native"
    sections["rivers"]["algorithm"] = "unknown"
    assert config.with_sections(sections).semantic_sections()["rivers"]["algorithm"] == "native"


@pytest.mark.parametrize("engine", [legacy, upgraded], ids=["legacy", "upgraded"])
@pytest.mark.parametrize("fixture,seed", [("384_8_42.npz", 42), ("768_4_2026093006.npz", 2026093006)])
def test_improved_rivers_leave_coast_after_mouth_and_preserve_relief(engine, fixture, seed):
    data = np.load(Path(__file__).parent / "fixtures/islands_r13" / fixture)
    height, _ = add_plain_detail(data["height"], data["labels"], seed=seed,
                               water_threshold=0, mountain_threshold=140)
    results = {}
    for algorithm in ("native", "improved"):
        grid = engine.NativeTerrainGrid.empty(len(height))
        engine._initialize_cells(grid)
        grid.height[:] = height
        engine._classify_relief(grid)
        engine._clear_pre_river_fields(grid)
        initial_water = grid.terrain <= 7
        engine._generate_rivers(grid, engine.NativeRng16(seed), algorithm=algorithm)
        assert np.array_equal(grid.height, height)
        river = np.isin(grid.terrain, (96, 97, 98, 99))
        coastal_land_river = river & ~initial_water & (neighbor_count(initial_water) > 0)
        components, _ = component_labels(coastal_land_river)
        sizes = np.bincount(components.ravel())[1:]
        results[algorithm] = (grid, river)
        if algorithm == "improved":
            # Multiple water neighbours at a mouth are legitimate; a chain
            # of successive coastal land cells is the actual regression.
            assert sizes.size and sizes.max() == 1
            assert all(np.any(river & (data["labels"] == n))
                       for n in range(1, int(data["labels"].max()) + 1))
    assert not np.array_equal(results["improved"][1], results["native"][1])


@pytest.mark.parametrize("engine", [legacy, upgraded], ids=["legacy", "upgraded"])
def test_improved_policy_also_runs_on_classic_relief_and_zero_rate(engine):
    base = engine.generate_primary_terrain(256, 20260904)
    for rate in (0, 100):
        result = engine.generate_primary_terrain(
            256, 20260904, surface_rates={"rivers": {"algorithm": "improved", "rate_percent": rate}},
        )
        assert result.metadata["river_algorithm"] == "improved"
        assert np.array_equal(result.height, base.height)
        assert result.metadata["river_attempts"] == 4 * 256 * 256
        if rate == 0:
            assert not np.isin(result.terrain, (96, 97, 98, 99)).any()
        else:
            assert np.isin(result.terrain, (96, 97, 98, 99)).any()


@pytest.mark.parametrize("engine", [legacy, upgraded], ids=["legacy", "upgraded"])
def test_explicit_native_algorithm_matches_implicit_default(engine):
    implicit = engine.generate_primary_terrain(256, 20260904)
    explicit = engine.generate_primary_terrain(
        256, 20260904, surface_rates={"rivers": {"algorithm": "native", "rate_percent": 100}},
    )
    for field in ("height", "terrain", "marker", "variant"):
        assert np.array_equal(getattr(implicit, field), getattr(explicit, field))


@pytest.mark.parametrize("base_mode,archetype,side,players", [
    ("legacy", "continental", 256, 2),
    ("upgraded", "continental", 256, 2),
    ("legacy", "large_islands", 384, 8),
    ("upgraded", "large_islands", 384, 8),
])
def test_algorithm_is_routed_by_generator_section_and_full_pipeline_valid(base_mode, archetype, side, players):
    from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
    from s3mapgen.generation import MapGenerator
    from s3mapgen.generation.generators.upgraded.validators import _river_components_touch_water
    config = build_custom_config(base_mode, archetype)
    sections = config.semantic_sections()
    sections["rivers"]["algorithm"] = "improved"
    result = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE).generate(
        players, 42, mode="custom", archetype=archetype, side=side,
        custom_config=config.with_sections(sections),
    )
    assert all(v.passed for v in result.validations if v.hard), result.validations
    assert result.state.metadata["river_algorithm"] == "improved"
    assert _river_components_touch_water(result.state.terrain)
    if archetype == "large_islands":
        assert all(f["river_cells"] > 0 for f in result.state.metadata["large_island_features"])


@pytest.mark.parametrize("mode", ["legacy", "upgraded"])
def test_large_islands_default_and_explicit_classic_survive_serialization(mode):
    config = build_custom_config(mode, "large_islands")
    assert config.semantic_sections()["rivers"]["algorithm"] == "improved"
    sections = config.semantic_sections()
    sections["rivers"]["algorithm"] = "native"
    classic = config.with_sections(sections)
    assert CustomGenerationConfig.from_dict(classic.to_dict()).semantic_sections()["rivers"]["algorithm"] == "native"
    old = config.to_dict()
    old["sections"] = {}
    assert CustomGenerationConfig.from_dict(old).semantic_sections()["rivers"]["algorithm"] == "native"


@pytest.mark.parametrize("engine", [legacy, upgraded], ids=["legacy", "upgraded"])
def test_quantity_counts_committed_routes_and_rate_modulates_their_number(engine):
    data = np.load(Path(__file__).parent / "fixtures/islands_r13/384_8_42.npz")
    height, _ = add_plain_detail(data["height"], data["labels"], seed=42,
                               water_threshold=0, mountain_threshold=140)
    mouths = []
    for rate in (0, 50, 100, 200):
        grid = engine.NativeTerrainGrid.empty(len(height))
        engine._initialize_cells(grid)
        grid.height[:] = height
        engine._classify_relief(grid)
        land = int((grid.terrain > 7).sum())
        engine._clear_pre_river_fields(grid)
        meta = engine._generate_rivers(grid, engine.NativeRng16(42), algorithm="improved", rate_percent=rate)
        mouths.append(meta["river_committed_mouths"])
        assert meta["river_land_cells"] == land
        assert meta["river_committed_mouths"] <= np.ceil(meta["river_mouth_target"] * 1.2)
        assert np.array_equal(grid.height, height)
    assert mouths[0] == 0
    assert mouths == sorted(mouths)
    assert mouths[0] < mouths[1] < mouths[2] < mouths[3]


def test_quantity_regulation_is_independent_of_component_layout():
    from s3mapgen.generation.river_policy import ImprovedRiverPolicy
    # Identical area of land, different fragmentation: no island allocation.
    contiguous = np.zeros((64, 64), np.uint8)
    contiguous[16:48, :] = 16
    fragmented = np.zeros_like(contiguous)
    fragmented[::2, :] = 16
    policies = [ImprovedRiverPolicy(t) for t in (contiguous, fragmented)]
    for p, t in zip(policies, (contiguous, fragmented)):
        p.quantity(64, t, 100)
        p.mouths = 8
    assert policies[0].mouth_threshold(2000) == policies[1].mouth_threshold(2000)


@pytest.mark.parametrize("engine", [legacy, upgraded], ids=["legacy", "upgraded"])
@pytest.mark.parametrize("fixture,seed,small", [
    ("384_8_42.npz", 42, True),
    ("768_4_2026093006.npz", 2026093006, False),
])
def test_size_scaling_reduces_small_maps_and_expands_large_maps(engine, fixture, seed, small):
    data = np.load(Path(__file__).parent / "fixtures/islands_r13" / fixture)
    height, _ = add_plain_detail(data["height"], data["labels"], seed=seed,
                               water_threshold=0, mountain_threshold=140)
    grid = engine.NativeTerrainGrid.empty(len(height))
    engine._initialize_cells(grid)
    grid.height[:] = height
    engine._classify_relief(grid)
    engine._clear_pre_river_fields(grid)
    meta = engine._generate_rivers(grid, engine.NativeRng16(seed), algorithm="improved")
    # R15 witnessed routes on the same fields/seeds: 69 mouths, max48 at
    # 384/8/42; 89 mouths, max40 at 768/4/2026093006. Prevent reversed scaling.
    if small:
        assert 0 < meta["river_committed_mouths"] < 69
        assert meta["river_mouth_length_mean"] < 27.493
        assert meta["river_mouth_length_max"] < 48
        assert meta["river_mouth_acceptance_threshold"] == meta["river_acceptance_threshold"]
    else:
        assert meta["river_committed_mouths"] > 89
        assert meta["river_mouth_length_mean"] > 21.393
        assert meta["river_mouth_length_max"] > 40
        assert meta["river_mouth_acceptance_threshold"] > meta["river_acceptance_threshold"]
    assert np.array_equal(grid.height, height)


@pytest.mark.parametrize('branch', [False, True])
def test_local_length_potential_follows_connected_land_area_and_keeps_branches(branch):
    from s3mapgen.generation.river_policy import ImprovedRiverPolicy
    terrain = np.zeros((512, 512), np.uint8)
    terrain[20:220, 20:220] = 16
    terrain[300:400, 300:400] = 16
    policy = ImprovedRiverPolicy(terrain)
    policy.quantity(512, terrain, 100)
    policy.start(50, 50, branch)
    large_scale = policy.local_length_scale
    large_score = policy.score(50, 55, 55, 40)
    policy.start(350, 350, branch)
    assert policy.local_length_scale < large_scale
    assert policy.score(50, 355, 355, 40) < large_score
    policy.committed(branch, 16)
    assert policy.branches == int(branch) and policy.mouths == int(not branch)
    assert policy.proposal_threshold(2000) == 2000


def test_continental_length_potential_and_global_quantity_are_preserved():
    from s3mapgen.generation.river_policy import ImprovedRiverPolicy
    terrain = np.full((512, 512), 16, np.uint8)
    policy = ImprovedRiverPolicy(terrain)
    policy.quantity(512, terrain, 100)
    policy.start(250, 250, False)
    assert policy.local_length_scale == policy.length_scale == 1
    assert policy.mouth_target == .30 * 512
    assert policy.score(50, 255, 255, 40) == 42
