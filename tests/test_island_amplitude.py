from copy import deepcopy

import pytest

from s3mapgen.generation.archetypes.island_amplitude import resolve_island_profile
from s3mapgen.generation.archetypes.profiles import default_archetype_profile, normalize_archetype_profile
from s3mapgen.generation.custom import build_custom_config, CustomGenerationConfig


@pytest.mark.parametrize('side,players', [(384, 8), (448, 11), (512, 15), (768, 20), (512, 4), (768, 4)])
def test_resolved_values_follow_actual_contours_and_preserve_saved_profile(side, players):
    from math import pi, sqrt
    import numpy as np
    from s3mapgen.generation.archetypes.large_islands import build_island_masks
    from s3mapgen.generation.archetypes.island_amplitude import amplitude_for_radius, calibrated_thresholds
    profile = default_archetype_profile('large_islands')
    original = deepcopy(profile)
    effective = resolve_island_profile(profile, side, players, seed=42)
    labels, *_ = build_island_masks(side, players, 42)
    areas = np.bincount(labels.ravel())[1:]
    for value, area in zip(effective['_island_relief_values'], areas):
        radius = sqrt(area / pi)
        amplitude = amplitude_for_radius(radius)
        assert value['area'] == area
        assert value['amplitude'] == amplitude
        assert (value['mountain'], value['snow']) == calibrated_thresholds(0, 140, 200, amplitude / 100., radius)
    assert profile == original
    assert resolve_island_profile(effective, side, players, seed=42) == effective


def test_manual_amplitude_and_literal_thresholds_survive_config_roundtrip():
    profile = default_archetype_profile('large_islands')
    profile['morphology'].update(island_amplitude_auto=False, island_amplitude_percent=75, island_thresholds_auto=False)
    profile['relief'].update(mountain_threshold=110, snow_threshold=160)
    config = build_custom_config('upgraded', 'large_islands', archetype_profile=profile)
    restored = CustomGenerationConfig.from_dict(config.to_dict())
    for side, players in ((384, 8), (768, 4)):
        effective = resolve_island_profile(restored.archetype_profile, side, players)
        assert effective['morphology']['island_amplitude_percent'] == 75
        assert effective['relief']['mountain_threshold'] == 110
        assert effective['relief']['snow_threshold'] == 160


def test_continental_source_is_never_affected_and_old_manual_thresholds_remain_literal():
    profile = default_archetype_profile('continental')
    assert resolve_island_profile(profile, 384, 8) is profile
    old = default_archetype_profile('large_islands')
    old['schema_version'] = 21
    old['morphology'].pop('island_amplitude_auto')
    old['morphology'].pop('island_thresholds_auto')
    old['morphology'].pop('island_amplitude_percent')
    old['relief'].update(mountain_threshold=120, snow_threshold=180)
    migrated = normalize_archetype_profile(old, archetype_key='large_islands')
    assert not migrated['morphology']['island_thresholds_auto']
    assert resolve_island_profile(migrated, 384, 8)['relief'] == old['relief']
