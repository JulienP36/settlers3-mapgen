import numpy as np
import pytest

from s3mapgen.generation.object_quotas import ObjectQuotaBasis, estimate_stone_quota
from s3mapgen.generation.custom import build_custom_config, CustomGenerationConfig
from s3mapgen.map_data.model import MapState
from s3mapgen.generation import MapGenerator
from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE


def disabled(mode='upgraded',arch='large_islands'):
    config=build_custom_config(mode,arch)
    sections=config.semantic_sections();sections['objects']['terrain_scaled_quotas']=False
    return config.with_sections(sections)


def test_default_migrates_old_profiles_and_false_survives_serialization():
    config=build_custom_config()
    assert config.semantic_sections()['objects']['terrain_scaled_quotas'] is True
    old=config.to_dict();old['sections']=config.semantic_sections();old['sections']['objects'].pop('terrain_scaled_quotas')
    assert CustomGenerationConfig.from_dict(old).semantic_sections()['objects']['terrain_scaled_quotas'] is True
    restored=CustomGenerationConfig.from_dict(disabled().to_dict())
    assert restored.semantic_sections()['objects']['terrain_scaled_quotas'] is False


@pytest.mark.parametrize('side',[256,384,768])
def test_off_uses_total_area_even_without_support_and_keeps_percentage(side):
    state=MapState.empty(side);state.terrain[:]=7
    basis=ObjectQuotaBasis.capture(state,terrain_scaled=False)
    assert basis.target(1683,(16,),150,channel='stones.anchors')==round(1683*(side/768)**2*1.5)
    assert basis.records['stones.anchors']['basis']=='map_area'
    assert estimate_stone_quota(disabled(),side,1683,150,state=state)[0]==round(1683*(side/768)**2*1.5)


@pytest.mark.parametrize('mode',['legacy','upgraded'])
def test_off_reaches_custom_placers_and_preserves_legal_supports(mode):
    config=disabled(mode);sections=config.semantic_sections()
    sections['trees']['base_quota_percent']=150
    sections['building_stones']['anchor_density_percent']=150
    sections['decorations']['cacti']=150
    config=config.with_sections(sections)
    out=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(4,42,mode=mode,side=384,archetype='large_islands',custom_config=config)
    q=out.state.metadata['object_quota_basis']['quotas']
    assert q['trees.pool']['requested']==round(2736*.25*1.5)
    assert q['stones.anchors']['requested']==round(1683*.25*1.5)
    assert all(row['basis']=='map_area' for row in q.values())
    assert all(v.passed for v in out.validations if v.hard)
    assert np.all(out.state.terrain[np.isin(out.state.objects,(45,46,47,48))]==64)


@pytest.mark.parametrize('mode',['legacy','upgraded'])
@pytest.mark.parametrize('arch',['continental','large_islands','team_islands'])
def test_checkbox_alone_applies_area_quotas_at_unchanged_100_percent(mode,arch):
    config=disabled(mode,arch)
    out=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(
        4,42,mode='custom',side=384,archetype=arch,player_teams=(1,2,1,2),custom_config=config)
    quotas=out.state.metadata['object_quota_basis']['quotas']
    assert quotas['trees.pool']['requested']==round(2736*.25)
    assert quotas['stones.anchors']['requested']==round(1683*.25)
    assert all(row['basis']=='map_area' for row in quotas.values())
    assert all(v.passed for v in out.validations if v.hard)
    if mode=='legacy':
        assert set(out.state.metadata['custom_object_controls']['replaced'])=={'trees','stones','decorations'}


def test_rechecking_alone_restores_the_same_native_custom_legacy_stream():
    config=disabled('legacy','continental');sections=config.semantic_sections()
    sections['objects']['terrain_scaled_quotas']=True
    restored=config.with_sections(sections)
    original=build_custom_config('legacy','continental')
    generator=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE)
    a=generator.generate(4,42,mode='custom',side=384,custom_config=original).state
    b=generator.generate(4,42,mode='custom',side=384,custom_config=restored).state
    assert np.array_equal(a.objects,b.objects) and a.starts==b.starts
    assert np.array_equal(a.terrain,b.terrain)
    assert np.array_equal(a.height,b.height)
    assert not b.metadata.get('custom_object_controls',{}).get('replaced')
