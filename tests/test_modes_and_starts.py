import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pytest
from s3mapgen.app_paths import PROFILE,LIBRARY
from s3mapgen.engine import MapGenerator
from s3mapgen.rules import PIPELINE_STAGES
from s3mapgen.modes import MODES
from s3mapgen.archetypes import ARCHETYPES


def test_architecture_names_are_separate():
    assert set(MODES) == {'legacy','upgraded','custom'}
    assert 'continental' in ARCHETYPES
    assert MODES['legacy'].implemented
    assert not MODES['upgraded'].implemented
    assert not MODES['custom'].implemented


def test_starts_are_early_in_pipeline():
    assert PIPELINE_STAGES.index('starts.maximin_early') < PIPELINE_STAGES.index('hydrology.micro_water_cleanup')
    assert PIPELINE_STAGES.index('starts.reserve_zones') < PIPELINE_STAGES.index('hydrology.micro_water_cleanup')


def test_20p_starts_survive_full_pipeline():
    res=MapGenerator(PROFILE,LIBRARY).generate(20,2026081902,mode='legacy',archetype='continental')
    assert res.state.metadata['starts_placed_early'] is True
    assert len(res.state.starts)==20
    assert all(v.passed for v in res.validations if v.hard), [v.label() for v in res.validations if v.hard and not v.passed]
    stages=res.stage_log
    start_i=next(i for i,s in enumerate(stages) if s.startswith('starts.maximin_early'))
    hydro_i=next(i for i,s in enumerate(stages) if s.startswith('hydrology.micro_water_cleanup'))
    assert start_i < hydro_i


def test_unimplemented_modes_fail_explicitly():
    g=MapGenerator(PROFILE,LIBRARY)
    with pytest.raises(NotImplementedError):
        g.generate(4,2026081901,mode='upgraded',archetype='continental')
    with pytest.raises(NotImplementedError):
        g.generate(4,2026081901,mode='custom',archetype='continental')
