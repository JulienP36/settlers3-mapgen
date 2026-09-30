import numpy as np

from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation.archetypes.profiles import (
    continental_legacy_blocks_profile,
    continental_noise_calibration_profile,
    default_archetype_profile,
)
from s3mapgen.generation.generators.legacy.native_terrain import (
    NativeTerrainGrid as LegacyNativeTerrainGrid,
    _prune_orphan_custom_rivers as _prune_legacy_orphan_custom_rivers,
    generate_primary_terrain as generate_legacy_terrain,
    resume_deferred_terrain as resume_legacy_deferred_terrain,
)
from s3mapgen.generation.generators.legacy.native_validators import (
    _river_components_touch_water as _legacy_river_components_touch_water,
)
from s3mapgen.generation.generators.upgraded.native_terrain import (
    NativeTerrainGrid,
    _prune_orphan_custom_rivers,
    generate_primary_terrain as generate_upgraded_terrain,
    resume_deferred_terrain as resume_upgraded_deferred_terrain,
)
from s3mapgen.generation.generators.upgraded.validators import (
    _river_components_touch_water,
)


def _sections(mode="upgraded", rate=100.0):
    sections = build_custom_config(mode).semantic_sections()
    sections["rivers"]["rate_percent"] = rate
    return sections


def test_custom_river_rate_at_100_keeps_the_native_terrain_identical():
    for mode, generate in (("legacy", generate_legacy_terrain), ("upgraded", generate_upgraded_terrain)):
        native = generate(256, 20260904)
        custom = generate(256, 20260904, surface_rates=_sections(mode, rate=100.0))
        assert np.array_equal(custom.terrain, native.terrain)
        assert np.array_equal(custom.height, native.height)
        assert custom.metadata["river_rate_percent"] == 100.0
        assert custom.metadata["river_acceptance_threshold"] == 0x07D0


def test_legacy_native_archetype_keeps_both_engines_unchanged():
    profile = default_archetype_profile("continental")
    for generate in (generate_legacy_terrain, generate_upgraded_terrain):
        native = generate(256, 20260918)
        profiled = generate(256, 20260918, archetype_profile=profile)
        for field in ("height", "terrain", "variant", "marker"):
            assert np.array_equal(getattr(native, field), getattr(profiled, field))
        assert "river_profile_rate_multiplier" not in profiled.metadata


def test_custom_river_rate_zero_keeps_the_native_river_phase_but_accepts_none():
    for mode, generate in (("legacy", generate_legacy_terrain), ("upgraded", generate_upgraded_terrain)):
        result = generate(256, 20260904, surface_rates=_sections(mode, rate=0.0))
        assert not np.isin(result.terrain, (96, 97, 98, 99)).any()
        assert result.metadata["river_attempts"] == 4 * 256 * 256
        assert result.metadata["river_systems"] == 0
        assert result.metadata["river_cells"] == 0
        assert result.metadata["river_acceptance_threshold"] == 0


def test_custom_river_rate_scales_the_same_native_attempts():
    for mode, generate in (("legacy", generate_legacy_terrain), ("upgraded", generate_upgraded_terrain)):
        results = {
            rate: generate(256, 20260904, surface_rates=_sections(mode, rate=rate))
            for rate in (25.0, 100.0, 200.0, 500.0)
        }
        counts = {
            rate: int(np.isin(result.terrain, (96, 97, 98, 99)).sum())
            for rate, result in results.items()
        }
        assert all(
            results[rate].metadata["river_attempts"] == 4 * 256 * 256
            for rate in results
        )
        assert counts[25.0] < counts[100.0] < counts[200.0] < counts[500.0]
        assert results[500.0].metadata["river_acceptance_threshold"] == 10000


def test_custom_river_rate_keeps_full_pipeline_valid_in_both_modes():
    from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
    from s3mapgen.generation import MapGenerator

    generator = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)
    for mode in ("legacy", "upgraded"):
        config = build_custom_config(mode)
        sections = config.semantic_sections()
        sections["rivers"]["rate_percent"] = 500.0
        result = generator.generate(
            2,
            20260904,
            mode="custom",
            archetype="continental",
            side=256,
            custom_config=config.with_sections(sections),
        )
        assert all(value.passed for value in result.validations if value.hard), mode
        assert result.state.metadata["river_rate_percent"] == 500.0


def test_noise_profile_connectivity_gate_runs_in_both_custom_pipelines():
    from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
    from s3mapgen.generation import MapGenerator

    generator = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)
    archetype = continental_noise_calibration_profile()
    archetype["morphology"]["size_adaptive_frequency"] = True
    for mode in ("legacy", "upgraded"):
        config = build_custom_config(mode)
        sections = config.semantic_sections()
        sections["rivers"]["rate_percent"] = 100.0
        config = (
            config.with_archetype_profile(archetype)
            .with_sections(sections)
        )
        for seed in (20260920, 20260921):
            for mirror_mode in (0, 1, 2, 3):
                result = generator.generate(
                    2,
                    seed,
                    mode="custom",
                    archetype="continental",
                    side=384,
                    mirror_mode=mirror_mode,
                    custom_config=config,
                )
                connection = next(
                    value for value in result.validations
                    if value.rule_id == "CUSTOM_RIVER_WATER_CONNECTION"
                )
                assert connection.passed and connection.hard, (
                    mode, seed, mirror_mode
                )
                assert all(
                    value.passed for value in result.validations if value.hard
                ), (mode, seed, mirror_mode)
                assert result.state.metadata["river_effective_rate_percent"] == 40.0


def test_noise_profile_rebalances_river_rate_in_both_engines():
    profile = continental_noise_calibration_profile()
    profile["morphology"]["size_adaptive_frequency"] = True
    for mode, generate, validate_rivers in (
        ("legacy", generate_legacy_terrain, _legacy_river_components_touch_water),
        ("upgraded", generate_upgraded_terrain, _river_components_touch_water),
    ):
        result = generate(
            384,
            20260920,
            surface_rates=_sections(mode, rate=200.0),
            archetype_profile=profile,
        )
        assert result.metadata["river_rate_percent"] == 200.0
        assert result.metadata["river_effective_rate_percent"] == 80.0
        assert result.metadata["river_acceptance_threshold"] == 1600
        assert validate_rivers(result.terrain)


def test_noise_profile_river_cleanup_survives_deferred_mirror_pass():
    profile = continental_noise_calibration_profile()
    profile["morphology"]["size_adaptive_frequency"] = True
    for mode, generate, resume, validate_rivers in (
        (
            "legacy",
            generate_legacy_terrain,
            resume_legacy_deferred_terrain,
            _legacy_river_components_touch_water,
        ),
        (
            "upgraded",
            generate_upgraded_terrain,
            resume_upgraded_deferred_terrain,
            _river_components_touch_water,
        ),
    ):
        primary = generate(
            384,
            20260921,
            mode=1,
            surface_rates=_sections(mode),
            defer_non_archetype=True,
            archetype_profile=profile,
        )
        assert primary.deferred is not None
        assert np.array_equal(primary.terrain, primary.terrain.T), mode
        result = resume(primary)
        assert validate_rivers(result.terrain), mode


def test_custom_orphan_river_cleanup_requires_direct_water_connection():
    cleanup_paths = (
        (LegacyNativeTerrainGrid, _prune_legacy_orphan_custom_rivers, _legacy_river_components_touch_water),
        (NativeTerrainGrid, _prune_orphan_custom_rivers, _river_components_touch_water),
    )
    for grid_type, prune_orphans, validate_rivers in cleanup_paths:
        grid = grid_type.empty(16)
        grid.terrain.fill(0x10)
        grid.terrain[2, 2] = 0x00
        grid.terrain[3, 2] = 0x60
        grid.terrain[4, 2] = 0x61
        grid.terrain[12, 12] = 0x30
        grid.terrain[13, 12] = 0x62
        grid.terrain[7, 7] = 0x60
        grid.terrain[8, 7] = 0x60

        assert not validate_rivers(grid.terrain)
        removed = prune_orphans(grid)

        assert removed == {
            "river_orphan_components_removed": 2,
            "river_orphan_cells_removed": 3,
        }
        assert grid.terrain[3, 2] == 0x60
        assert grid.terrain[4, 2] == 0x61
        assert grid.terrain[13, 12] == 0x10
        assert grid.terrain[7, 7] == 0x10
        assert grid.terrain[8, 7] == 0x10
        assert validate_rivers(grid.terrain)


def test_custom_profile_rivers_do_not_start_in_open_water_and_reach_water():
    from s3mapgen.map_data.hexgrid import component_labels, neighbor_count

    profile = continental_legacy_blocks_profile()
    for generate in (generate_legacy_terrain, generate_upgraded_terrain):
        result = generate(256, 20260921, archetype_profile=profile)
        terrain = result.terrain
        river = np.isin(terrain, (96, 97, 98, 99))
        water = terrain <= 7
        labels, count = component_labels(river)
        touching_water = neighbor_count(water) > 0
        for label in range(1, count + 1):
            assert np.any((labels == label) & touching_water)
        # Open sea cells have at least five Water neighbours in HEX6; Custom
        # candidate starts are restricted to the coastal band.
        assert not np.any(river & (neighbor_count(water) >= 5))
