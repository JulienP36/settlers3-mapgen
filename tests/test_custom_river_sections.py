import numpy as np

from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation.generators.legacy.native_terrain import (
    generate_primary_terrain as generate_legacy_terrain,
)
from s3mapgen.generation.generators.upgraded.native_terrain import (
    generate_primary_terrain as generate_upgraded_terrain,
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
