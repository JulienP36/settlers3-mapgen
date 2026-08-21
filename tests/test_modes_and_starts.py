import pytest
from s3mapgen.app_paths import LEGACY_PROFILE,UPGRADED_PROFILE,UPGRADED_REFERENCE,LIBRARY
from s3mapgen.generator_v15 import MapGenerator
from s3mapgen.rules import PIPELINE_STAGES
from s3mapgen.modes import MODES
from s3mapgen.archetypes import ARCHETYPES

def gen():return MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_PROFILE,UPGRADED_REFERENCE)

@pytest.fixture(scope='module')
def upgraded4():return gen().generate(4,2026082202,mode='upgraded',archetype='continental')
@pytest.fixture(scope='module')
def upgraded20():return gen().generate(20,2026082203,mode='upgraded',archetype='continental')

def test_architecture_names_are_separate():
    assert set(MODES)=={'legacy','upgraded','custom'};assert 'continental' in ARCHETYPES;assert MODES['legacy'].implemented;assert MODES['upgraded'].implemented;assert not MODES['custom'].implemented

def test_starts_are_early_in_pipeline():assert PIPELINE_STAGES.index('starts.maximin_early') < PIPELINE_STAGES.index('hydrology.micro_water_cleanup')

def test_upgraded_4p_hard_validators(upgraded4):
    assert upgraded4.state.metadata['starts_placed_early'] is True;assert all(v.passed for v in upgraded4.validations if v.hard);assert upgraded4.state.metadata['mode_key']=='upgraded'

def test_upgraded_20p_starts_survive_full_pipeline(upgraded20):
    assert len(upgraded20.state.starts)==20;assert all(v.passed for v in upgraded20.validations if v.hard)

def test_custom_still_fails_explicitly():
    with pytest.raises(NotImplementedError):gen().generate(4,2026081901,mode='custom',archetype='continental')

def test_upgraded_snow_is_blocked_and_swamp_chain_is_legal(upgraded4):
    from s3mapgen.constants import SNOW,SNOW_TRANS
    import numpy as np
    snow=np.isin(upgraded4.state.terrain,[SNOW_TRANS,SNOW]);assert snow.any();assert np.all(upgraded4.state.accessibility[snow]==1)
    rules={v.rule_id:v for v in upgraded4.validations};assert rules['SNOW_ACCESS'].passed;assert rules['SWAMP_TRANSITIONS'].passed
