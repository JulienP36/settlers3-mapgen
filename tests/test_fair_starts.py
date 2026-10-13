import numpy as np
from s3mapgen.map_data.model import MapState
from s3mapgen.generation.fair_starts import place_fair_starts, local_metrics
from s3mapgen.generation.start_safety import require_start_safety
from s3mapgen.generation.start_algorithms import resolve_start_algorithm


def test_fair_ignores_island_quotas_but_keeps_native_classic_dispatch():
    islands = np.ones((128,128),np.int32)
    assert resolve_start_algorithm('fair',islands)=='fair'
    assert resolve_start_algorithm('classic',islands)=='classic'
    assert resolve_start_algorithm('auto',islands)=='islands'


def test_nearby_ore_on_another_island_does_not_count_as_land_access():
    state=MapState.empty(128);state.terrain[:]=16;state.height[:]=10
    state.terrain[:,60:65]=0
    state.terrain[40:60,75:85]=32;state.resources[40:60,75:85]=0x1A
    assert local_metrics(state,(40,50))[0]==0
    state.terrain[50,60:65]=16
    assert local_metrics(state,(40,50))[0]==2000


def test_resource_preferences_never_reject_a_valid_resource_poor_map():
    state=MapState.empty(128);state.terrain[:]=16;state.height[:]=10
    state.terrain[30:55,30:55]=64;state.objects[70:90,30:55]=68
    other=MapState(128,state.area.copy())
    place_fair_starts(state,4,np.random.default_rng(42))
    place_fair_starts(other,4,np.random.default_rng(42))
    assert state.starts==other.starts and len(state.starts)==4
    assert all(v.passed for v in require_start_safety(state))
    assert np.array_equal(state.area,other.area)
    assert all(p['coal']==p['iron']==0 for p in state.metadata['fair_starts']['players'])


def test_insufficient_valid_space_keeps_map_without_inventing_a_start():
    state=MapState.empty(128);state.terrain[:]=0
    state.terrain[45:80,45:80]=16
    original=state.area.copy()
    place_fair_starts(state,4,np.random.default_rng(42))
    assert len(state.starts)==1
    assert state.metadata['start_disabled_slots']==[1,2,3]
    assert np.array_equal(state.area,original)
    checks=require_start_safety(state)
    assert all(v.passed for v in checks if v.rule_id!='START_PLAYER_COUNT')
    assert not checks[-1].passed


def test_small_map_with_room_does_not_cluster_equally_rich_starts():
    state=MapState.empty(256);state.terrain[:]=16;state.height[:]=10
    original=state.area.copy()
    place_fair_starts(state,4,np.random.default_rng(42))
    assert len(state.starts)==4
    assert state.metadata['fair_starts']['minimum_spacing_coordinates']>=80
    assert all(v.passed for v in require_start_safety(state))
    assert np.array_equal(state.area,original)


def test_preferred_spacing_does_not_drop_players_when_only_close_starts_fit(monkeypatch):
    from s3mapgen.generation import fair_starts
    state=MapState.empty(256);state.terrain[:]=16;state.height[:]=10
    candidates=np.zeros((256,256),bool)
    candidates[60,[60,110,160]]=True
    monkeypatch.setattr(fair_starts,'candidate_centers',lambda state:candidates)
    place_fair_starts(state,3,np.random.default_rng(42))
    assert set(state.starts)=={(60,60),(110,60),(160,60)}
    assert not state.metadata['start_disabled_slots']
    assert state.metadata['fair_starts']['preferred_spacing_coordinates']>50
    assert all(v.passed for v in require_start_safety(state))


def test_reported_seed_searches_spaced_layouts_before_trading_resources():
    from s3mapgen.generation import MapGenerator
    from s3mapgen.application.paths import LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE
    generator=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE)
    for mode in ('legacy','upgraded'):
        result=generator.generate(4,2026100817,side=512,mode=mode,start_algorithm='fair')
        report=result.state.metadata['fair_starts']
        assert len(result.state.starts)==4
        assert report['minimum_spacing_coordinates']>=report['preferred_spacing_coordinates']
        assert not report['preferred_spacing_relaxed']
        assert all(check.passed for check in require_start_safety(result.state))
        assert all(check.passed for check in result.validations if check.hard), result.validations
