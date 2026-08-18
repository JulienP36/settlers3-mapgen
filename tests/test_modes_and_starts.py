import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from s3mapgen.app_paths import LEGACY_PROFILE,UPGRADED_PROFILE,UPGRADED_REFERENCE,LIBRARY
from s3mapgen.engine import MapGenerator
from s3mapgen.rules import PIPELINE_STAGES
from s3mapgen.modes import MODES
from s3mapgen.archetypes import ARCHETYPES

def gen():
    return MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_PROFILE,UPGRADED_REFERENCE)

def test_architecture_names_are_separate():
    assert set(MODES)=={'legacy','upgraded','custom'}
    assert 'continental' in ARCHETYPES
    assert MODES['legacy'].implemented
    assert MODES['upgraded'].implemented
    assert not MODES['custom'].implemented

def test_starts_are_early_in_pipeline():
    assert PIPELINE_STAGES.index('starts.maximin_early') < PIPELINE_STAGES.index('hydrology.micro_water_cleanup')

def test_upgraded_4p_hard_validators():
    res=gen().generate(4,2026082001,mode='upgraded',archetype='continental')
    assert res.state.metadata['starts_placed_early'] is True
    assert all(v.passed for v in res.validations if v.hard), [v.label() for v in res.validations if v.hard and not v.passed]
    assert res.state.metadata['mode_key']=='upgraded'

def test_upgraded_20p_starts_survive_full_pipeline():
    res=gen().generate(20,2026082002,mode='upgraded',archetype='continental')
    assert len(res.state.starts)==20
    assert all(v.passed for v in res.validations if v.hard), [v.label() for v in res.validations if v.hard and not v.passed]

def test_legacy_still_runs():
    res=gen().generate(4,2026081901,mode='legacy',archetype='continental')
    assert len(res.state.starts)==4

def test_custom_still_fails_explicitly():
    with pytest.raises(NotImplementedError):
        gen().generate(4,2026081901,mode='custom',archetype='continental')
