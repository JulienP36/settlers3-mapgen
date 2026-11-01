import numpy as np
import pytest

from s3mapgen.generation.team_starts import geographical_assignment, place_team_starts
from s3mapgen.map_data.model import MapState
from s3mapgen.generation.start_safety import validate_start_safety
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE


def ring(count):
    angle=np.linspace(0,2*np.pi,count,endpoint=False)
    return np.column_stack((180+100*np.cos(angle)+50*np.sin(angle),180+100*np.sin(angle)))


@pytest.mark.parametrize('teams',[(1,2,1,2,1,2),(1,1,1,1,1,2),(1,2,3,1,2,3),(1,0,1,0,2,2)])
def test_team_ownership_is_contiguous_without_moving_or_compacting_starts(teams):
    points=ring(len(teams));slots=list(range(len(teams)))
    order,strategy=geographical_assignment(points,slots,teams,np.random.default_rng(42))
    assert sorted(order)==slots
    assert (order,strategy)==geographical_assignment(points,slots,teams,np.random.default_rng(42))
    owner={point:teams[slot] if teams[slot] else -(slot+1) for slot,point in enumerate(order)}
    circular=[owner[i] for i in range(len(points))]
    for team in set(circular):
        assert sum(circular[i]==team and circular[i-1]!=team for i in range(len(circular)))==1
    assert strategy in ('separating_axis','contiguous_sectors')


def test_no_team_does_not_make_an_alliance_and_partial_slots_keep_identity():
    points=ring(4);slots=[0,2,4,5];teams=(0,1,0,1,0,0)
    order,strategy=geographical_assignment(points,slots,teams,np.random.default_rng(0))
    assert strategy=='unrestricted' and sorted(order)==list(range(4))


def test_flat_map_keeps_allied_starts_spread_and_editor_legal():
    state=MapState.empty(256);state.terrain[:]=16
    state.metadata.update(players=4,player_teams=[1,2,1,2])
    place_team_starts(state,4,np.random.default_rng(42))
    assert len(state.starts)==4 and all(v.passed for v in validate_start_safety(state))
    assert state.metadata['team_starts']['allies_attracted'] is False
    for a,b in ((0,2),(1,3)):
        assert np.linalg.norm(np.array(state.starts[a])-state.starts[b])>90


@pytest.mark.parametrize('mode',['legacy','upgraded'])
@pytest.mark.parametrize('arch',['continental','large_islands','team_islands'])
def test_team_departures_follow_complete_pipeline_and_island_contract(mode,arch):
    result=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(
        4,42,mode=mode,archetype=arch,side=384,start_algorithm='teams',player_teams=(1,2,1,2))
    assert len(result.state.starts)==4
    assert result.state.metadata['start_algorithm_effective']=='teams'
    assert all(v.passed for v in result.validations if v.hard)
    assert [p['team'] for p in result.state.metadata['team_starts']['players']]==[1,2,1,2]
