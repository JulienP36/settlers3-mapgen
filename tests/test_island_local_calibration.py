"""Real contour calibration, classification parity and saved-setting boundaries."""

from copy import deepcopy

import numpy as np
import pytest

from s3mapgen.generation.archetypes.island_amplitude import resolve_island_profile
from s3mapgen.generation.archetypes.island_source import generate_island_source
from s3mapgen.generation.archetypes.previews import (
    classify_macro,
    generate_archetype_preview,
    generate_archetype_indicative_preview,
)
from s3mapgen.generation.archetypes.profiles import (
    default_archetype_profile,
    continental_landmass_profile,
)
from s3mapgen.generation.custom import build_custom_config, CustomGenerationConfig


def test_team_contours_have_independent_amplitudes_and_thresholds_before_lakes():
    profile = default_archetype_profile("team_islands")
    fields = generate_island_source(
        384, 4, 42, profile, native_relaxation=None, player_teams=(1, 1, 1, 2)
    )
    assert fields.report["amplitudes_percent_by_island"] == [100, 83]
    assert fields.report["mountain_thresholds_by_island"] == [140, 118]
    for n, threshold in enumerate(fields.report["mountain_thresholds_by_island"], 1):
        assert np.all(
            fields.threshold_fields[0][fields.source_labels == n] == threshold
        )
    assert fields.report["preset_features_required"]


@pytest.mark.parametrize("engine", ["legacy", "upgraded"])
def test_preview_and_native_classifier_use_the_same_local_threshold_fields(engine):
    from importlib import import_module

    native = import_module(f"s3mapgen.generation.generators.{engine}.native_terrain")
    profile = default_archetype_profile("team_islands")
    effective = resolve_island_profile(
        profile, 384, 4, seed=42, player_teams=(1, 1, 1, 2)
    )
    fields = generate_island_source(
        384, 4, 42, effective, native_relaxation=None, player_teams=(1, 1, 1, 2)
    )
    macro = classify_macro(
        fields.noise,
        effective,
        final_height=fields.height,
        threshold_fields=fields.threshold_fields,
    )
    grid = native.NativeTerrainGrid.empty(384)
    grid.height[:] = fields.height
    native._classify_relief(grid, effective, fields.noise, fields.threshold_fields)
    for category, terrain in [
        (0, native.WATER),
        (2, native.GRASS),
        (3, native.ROCK),
        (4, native.SNOW),
    ]:
        mask = macro[1:-1, 1:-1] == category
        assert mask.any()
        assert np.all(grid.terrain[1:-1, 1:-1][mask] == terrain)
    # The test actually contains a height accepted as mountain only on the small island.
    small = fields.source_labels == 2
    assert np.any(small & (fields.height >= 118) & (fields.height < 140))


def test_indicative_preview_matches_unrelaxed_exact_preview_for_local_thresholds():
    profile = default_archetype_profile("team_islands")
    kwargs = dict(players=4, player_teams=(1, 1, 1, 2))
    preview = generate_archetype_preview(profile, 384, 42, relax_macro=False, **kwargs)
    noise, macro = generate_archetype_indicative_preview(profile, 384, 42, **kwargs)
    assert np.array_equal(preview.noise, noise)
    assert np.array_equal(preview.macro, macro)


def test_continental_ignores_inherited_auto_flags_but_preserves_manual_amplitude():
    profile = continental_landmass_profile()
    assert not profile["morphology"]["island_amplitude_auto"]
    assert not profile["morphology"]["island_thresholds_auto"]
    inherited = deepcopy(profile)
    inherited["morphology"].update(
        island_amplitude_auto=True, island_thresholds_auto=True
    )
    restored = build_custom_config('upgraded', 'continental', archetype_profile=inherited)
    assert not restored.archetype_profile['morphology']['island_amplitude_auto']
    assert not restored.archetype_profile['morphology']['island_thresholds_auto']

    a = generate_island_source(256, 4, 42, profile, native_relaxation=None)
    b = generate_island_source(256, 4, 42, inherited, native_relaxation=None)
    assert np.array_equal(a.height, b.height)
    assert a.report["amplitudes_percent_by_island"] == [100]
    inherited["morphology"].update(
        island_amplitude_auto=False,
        island_thresholds_auto=False,
        island_amplitude_percent=75,
    )
    c = generate_island_source(256, 4, 42, inherited, native_relaxation=None)
    assert c.report["amplitudes_percent_by_island"] == [75]
    assert not np.array_equal(a.height, c.height)


def test_saved_generator_values_and_unresolved_island_switches_are_preserved():
    config = build_custom_config("upgraded", "team_islands")
    assert config.semantic_sections()["terrains"]["mud"]["rate_percent"] == 50
    saved = config.to_dict()
    saved["sections"]["terrains"]["desert"] = {"enabled": True, "rate_percent": 100.0}
    saved["sections"]["terrains"]["mud"] = {"enabled": False, "rate_percent": 0.0}
    restored = CustomGenerationConfig.from_dict(saved)
    assert restored.semantic_sections()["terrains"]["desert"]["rate_percent"] == 100
    assert restored.semantic_sections()["terrains"]["mud"]["rate_percent"] == 0
    resolve_island_profile(
        restored.archetype_profile, 384, 4, seed=42, player_teams=(1, 1, 1, 2)
    )
    assert restored.archetype_profile["morphology"]["island_amplitude_auto"]
    assert "_island_relief_values" not in restored.to_dict()["archetype_profile"]


def test_direct_upgraded_default_rates_match_explicit_generator_controls():
    from s3mapgen.generation.generators.upgraded.native_terrain import generate_primary_terrain
    implicit = generate_primary_terrain(256, 42)
    sections = build_custom_config('upgraded').semantic_sections()
    explicit = generate_primary_terrain(256, 42, surface_rates=sections)
    assert implicit.metadata['custom_terrain']['rates'] == explicit.metadata['custom_terrain']['rates']
    assert implicit.metadata['custom_terrain']['rates']['desert'] == 50
    assert implicit.metadata['custom_terrain']['rates']['mud'] == 50
    for channel in ('height', 'terrain', 'variant', 'marker'):
        assert np.array_equal(getattr(implicit, channel), getattr(explicit, channel))
