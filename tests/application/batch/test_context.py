"""Batch variants retain detached Custom generator and geography independently."""
from copy import deepcopy
from itertools import product

import pytest

from s3mapgen.application.batch.context import BatchContext
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.generation.archetypes.profiles import continental_landmass_profile


def edited_config():
    config = build_custom_config('upgraded','team_islands')
    sections = config.semantic_sections()
    sections['minerals']['occupancy_percent'] = 73
    profile = deepcopy(config.archetype_profile)
    profile['morphology']['mask_layer_count'] = 1
    profile['morphology']['mask_layers'][0].update(enabled=True,type='manual',
        provider_settings={'grid_side':64,'grid':[n % 256 for n in range(4096)]})
    return config.with_sections(sections).with_archetype_profile(profile)


@pytest.mark.parametrize('custom_generator,custom_archetype',tuple(product((False,True),repeat=2)))
def test_context_exposes_only_custom_choices_present_on_opening(custom_generator,custom_archetype):
    config=edited_config()
    context=BatchContext('custom' if custom_generator else 'upgraded',
                         'edited' if custom_archetype else 'team_islands',
                         config.to_dict(),(255,)*20,(0,)*20,4)
    assert ('custom' in context.modes) is custom_generator
    assert ('edited' in context.archetypes) is custom_archetype
    assert context.archetypes[:4] == ('classic','continental','large_islands','team_islands')
    for mode,arch in product(context.modes,context.archetypes):
        context.resolve(mode,arch)


def test_custom_survives_standard_choices_and_mutation_of_returned_profiles():
    original=edited_config();payload=original.to_dict()
    context=BatchContext('custom','edited',payload,[255,1,2,3],[1,1,-1,0],4)
    payload['profile'].clear()
    for mode,arch in product(('legacy','upgraded'),context.archetypes):
        _,variant=context.resolve(mode,arch)
        variant.profile.clear()
    backend,restored=context.resolve('custom','edited')
    assert backend=='team_islands' and restored.to_dict()==original.to_dict()
    assert context.nations[:4]==(255,1,2,3) and context.teams[:4]==(1,1,-1,0)
    assert len(context.nations)==len(context.teams)==20


def test_generator_and_archetype_custom_are_composed_independently():
    original=edited_config()
    context=BatchContext('custom','edited',original.to_dict(),(),(),2)
    backend,variant=context.resolve('custom','continental')
    assert backend=='continental'
    assert variant.profile==original.profile and variant.sections==original.sections
    assert variant.archetype_profile==continental_landmass_profile()
    backend,variant=context.resolve('legacy','edited')
    assert backend=='team_islands' and variant.base_mode=='legacy'
    assert variant.archetype_profile==original.archetype_profile
    assert variant.profile==build_custom_config('legacy','team_islands').profile


def test_classic_and_continental_are_distinct_profiles_on_same_engine_route():
    context=BatchContext('legacy','classic',build_custom_config('legacy','continental').to_dict(),(),(),2)
    a,classic=context.resolve('legacy','classic')
    b,continental=context.resolve('legacy','continental')
    assert a==b=='continental'
    assert classic.digest!=continental.digest
    assert classic==build_custom_config('legacy','continental')
    assert continental==build_custom_config('legacy','continental',archetype_profile=continental_landmass_profile())
    with pytest.raises(ValueError):context.resolve('custom','classic')
    with pytest.raises(ValueError):context.resolve('legacy','edited')


def test_language_selector_uses_exact_supplied_flag_pixels():
    from s3mapgen.application.ui.sprites import sprite_image
    from s3mapgen.application.ui.widgets.icons import selector_icon_image
    for lang in ('fr','en','de','es'):
        image=selector_icon_image('#000000','flag_'+lang)
        assert image.size==(18,18)
        assert image.tobytes()==sprite_image('languages/'+lang).tobytes()
