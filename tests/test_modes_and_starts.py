import pytest
from s3mapgen.application.paths import UPGRADED_PROFILE,UPGRADED_REFERENCE,LIBRARY
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.rules import PIPELINE_STAGES
from s3mapgen.generation.modes import MODES
from s3mapgen.generation.archetypes import ARCHETYPES

def gen():return MapGenerator(UPGRADED_PROFILE,LIBRARY,UPGRADED_REFERENCE)

@pytest.fixture(scope='module')
def upgraded4():return gen().generate(4,2026082202,mode='upgraded',archetype='continental')
@pytest.fixture(scope='module')
def upgraded20():return gen().generate(20,2026082203,mode='upgraded',archetype='continental')

def test_architecture_names_are_separate():
    assert set(MODES)=={'legacy','upgraded','custom'};assert 'continental' in ARCHETYPES;assert MODES['legacy'].implemented;assert MODES['upgraded'].implemented;assert not MODES['custom'].implemented

def test_provisional_starts_are_kept_out_of_the_content_pipeline():assert PIPELINE_STAGES.index('starts.provisional_bridge') < PIPELINE_STAGES.index('hydrology.micro_water_cleanup')

def test_upgraded_4p_hard_validators(upgraded4):
    assert upgraded4.state.metadata['starts_placed_early'] is False;assert upgraded4.state.metadata['starts_placed_provisionally'] is True;assert all(v.passed for v in upgraded4.validations if v.hard);assert upgraded4.state.metadata['mode_key']=='upgraded'

def test_upgraded_20p_starts_survive_full_pipeline(upgraded20):
    assert len(upgraded20.state.starts)==20;assert all(v.passed for v in upgraded20.validations if v.hard)

def test_custom_still_fails_explicitly():
    with pytest.raises(NotImplementedError):gen().generate(4,2026081901,mode='custom',archetype='continental')

def test_legacy_native_rebuild_is_reachable():
    result=gen().generate(2,2026081901,mode='legacy',archetype='continental',side=384)
    assert result.state.metadata['mode_key']=='legacy'
    assert result.state.metadata['engine_revision'].endswith('native-legacy-v1')
    assert len(result.state.starts)==2
    assert all(v.passed for v in result.validations if v.hard)

def test_reported_small_seed_finishes_without_relief_loop():
    result=gen().generate(2,297650040,mode='legacy',archetype='continental',side=256)
    assert result.state.side==256
    assert result.state.metadata['native_relief_relax_passes']<=128
    assert all(v.passed for v in result.validations if v.hard)

def test_legacy_native_tables_are_transcribed():
    from s3mapgen.generation.generators.legacy.native import NATIVE_NORMAL_START_FOOTPRINT,native_build_hex_offset_bank
    from s3mapgen.map_data.constants import START_FOOTPRINT
    bank=native_build_hex_offset_bank()
    assert len(bank)==19999
    assert [(o.dx,o.dy,o.ring,o.orientation) for o in bank[:7]]==[(0,0,0,0),(1,0,1,0),(1,1,1,1),(0,1,1,2),(-1,0,1,3),(-1,-1,1,4),(0,-1,1,5)]
    assert len(NATIVE_NORMAL_START_FOOTPRINT)==33
    assert set(NATIVE_NORMAL_START_FOOTPRINT)==set(START_FOOTPRINT)

def test_upgraded_snow_is_blocked_and_swamp_chain_is_legal(upgraded4):
    from s3mapgen.map_data.constants import SNOW,SNOW_TRANS
    import numpy as np
    snow=np.isin(upgraded4.state.terrain,[SNOW_TRANS,SNOW]);assert snow.any();assert np.all(upgraded4.state.accessibility[snow]==1)
    rules={v.rule_id:v for v in upgraded4.validations};assert rules['UPGRADED_WATER_ACCESS'].passed;assert rules['UPGRADED_NO_MUD'].passed


def test_upgraded_is_independent_and_omits_start_content(upgraded4):
    assert upgraded4.state.metadata['generator'] == 'continental_upgraded_native'
    assert upgraded4.state.metadata['upgraded_base_pipeline'] == 'independent_copy_of_continental_legacy_native'
    assert upgraded4.state.metadata['upgraded_start_content_deferred'] is True
    assert not any(int(v) in (23, 144, 145) for v in upgraded4.state.terrain.flat)


def test_upgraded_profile_exposes_round_mineral_test_and_deferred_start_rules():
    from s3mapgen.generation.generators.upgraded.profile import load_profile
    profile = load_profile()
    minerals = profile['minerals']
    assert minerals['shape_variant'] == 'round_parallelogram_compensated_test'
    assert minerals['shape_space'] == 'parallelogram_compensated'
    assert minerals['blob_aspect_min'] == minerals['blob_aspect_max'] == 1.0
    assert profile['start_bonus']['building_stones']['stock_units_per_player'] == 53
    assert profile['start_bonus']['mini_swamp']['outside_technical_zone'] is True


def test_upgraded_generation_records_the_active_mineral_shape_variant(upgraded4):
    minerals = upgraded4.state.metadata['upgraded_minerals']
    assert minerals['shape_variant'] == 'round_parallelogram_compensated_test'
    assert minerals['shape_aspect_range'] == [1.0, 1.0]
    assert minerals['shape_space'] == 'parallelogram_compensated'
    rules = upgraded4.state.metadata['upgraded_start_bonus_rules']
    assert rules['outside_global_quota'] is True
    assert rules['building_stones']['stock_units_per_player'] == 53
