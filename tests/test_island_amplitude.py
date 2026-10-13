from copy import deepcopy

import pytest

from s3mapgen.generation.archetypes.island_amplitude import resolve_island_profile
from s3mapgen.generation.archetypes.profiles import default_archetype_profile, normalize_archetype_profile
from s3mapgen.generation.custom import build_custom_config, CustomGenerationConfig


@pytest.mark.parametrize('side,players,amplitude,mountain,snow', [
    (384, 8, 50, 85, 108), (448, 11, 50, 85, 108),
    (512, 15, 50, 85, 108), (768, 20, 62, 95, 128),
    (512, 4, 100, 140, 200), (768, 4, 100, 140, 200),
])
def test_resolved_values_follow_island_area_and_preserve_saved_profile(side, players, amplitude, mountain, snow):
    profile = default_archetype_profile('large_islands')
    original = deepcopy(profile)
    effective = resolve_island_profile(profile, side, players)
    assert effective['morphology']['island_amplitude_percent'] == amplitude
    assert effective['relief']['mountain_threshold'] == mountain
    assert effective['relief']['snow_threshold'] == snow
    assert profile == original
    assert resolve_island_profile(effective, side, players) == effective


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
