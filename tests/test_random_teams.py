"""Random-team contract recovered from the validated R1 handoff."""
import numpy as np
import pytest
from s3mapgen.generation.teams import resolve_player_teams
from s3mapgen.generation import MapGenerator
from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE, MAP_SCAFFOLD, EDM_SCAFFOLD
from s3mapgen.application.session.cache import GenerationCacheKey
from s3mapgen.map_data.binary import export_with_scaffold, parse_parts, encode_player_teams


def test_seeded_balancing_and_manual_choices():
    choices=(20,20,0,-1,-1,-1,-1,-1);outcomes=set()
    for seed in range(20):
        teams=resolve_player_teams(8,seed,choices,3)
        assert teams[:3]==(20,20,0)
        assert sorted(teams.count(t) for t in (1,2,20))==[2,2,3]
        assert teams==resolve_player_teams(8,seed,choices,3)
        outcomes.add(teams)
    assert len(outcomes)>1


def test_impossible_counts_keep_fixed_alliances_and_independents():
    assert set(resolve_player_teams(4,42,(7,12,20,-1),2))=={7,12,20}
    assert resolve_player_teams(3,42,(0,-1,0),20)==(0,1,0)
    assert resolve_player_teams(4,42,(20,20,20,-1),20)==(20,20,20,1)
    for teams in ((),(0,0,0,0),(20,7,20,0)):
        assert resolve_player_teams(4,42,teams)==teams


@pytest.mark.parametrize('teams,count',[((-1,),2),((True,-1),2),((21,-1),2),((-2,0),2),((-1,-1),1),((-1,-1),21),((-1,-1),2.5)])
def test_reject_invalid_inputs(teams,count):
    with pytest.raises(ValueError):resolve_player_teams(2,42,teams,count)


def test_cache_preserves_requested_configuration():
    a=GenerationCacheKey(42,384,4,'upgraded','team_islands',player_teams=(-1,)*4)
    b=GenerationCacheKey(42,384,4,'upgraded','team_islands',player_teams=(-1,)*4,random_team_count=3)
    assert a!=b


@pytest.mark.parametrize('mode,count',[('legacy',2),('upgraded',2),('custom',2),('upgraded',3)])
def test_generation_equals_explicit_draw_and_exports_resolved_teams(tmp_path,mode,count):
    from s3mapgen.generation.custom import build_custom_config
    generator=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE)
    choices=(-1,)*4;teams=resolve_player_teams(4,42,choices,count)
    kwargs={'custom_config':build_custom_config('upgraded','team_islands')} if mode=='custom' else {}
    random=generator.generate(4,42,mode=mode,side=384,archetype='team_islands',player_teams=choices,random_team_count=count,**kwargs)
    fixed=generator.generate(4,42,mode=mode,side=384,archetype='team_islands',player_teams=teams,**kwargs)
    np.testing.assert_array_equal(random.state.area,fixed.state.area)
    assert random.state.starts==fixed.state.starts
    assert tuple(random.state.metadata['player_teams'])==teams
    assert random.state.metadata['requested_player_teams']==list(choices)
    assert all(v.passed for v in random.validations if v.hard)
    for scaffold,suffix in ((MAP_SCAFFOLD,'map'),(EDM_SCAFFOLD,'edm')):
        path=tmp_path/f'random.{suffix}';export_with_scaffold(random.state,scaffold,path)
        setup=dict(parse_parts(path,allow_terminal_padding=True)[1])[3]
        assert list(setup[33::2])==list(encode_player_teams(teams))
        assert list(setup[34::2])==[0]*4


def test_dialog_choice_updates_session_and_custom_preview(monkeypatch):
    from types import SimpleNamespace
    from s3mapgen.application.workflows.generation import GenerationWorkflowController
    from s3mapgen.application.workflows import classic_starts
    var=lambda value:SimpleNamespace(get=lambda:value);updates=[]
    host=SimpleNamespace(players=var(4),seed=var(42),size=var(384),prefs={'language':'fr'},
        _custom_schedule_archetype_preview_refresh=lambda:updates.append(True),
        _mode_key=lambda:'upgraded',_arch_key=lambda:'continental',_modifier_keys=lambda:(),
        _mirror_key=lambda:0,_start_algorithm_key=lambda:'auto',_start_nations=lambda _:(255,)*4)
    choices=((255,)*20,(-1,)*4+(0,)*16,3)
    monkeypatch.setattr(classic_starts,'choose_classic_nations',lambda *a,**kw:choices)
    assert GenerationWorkflowController._configure_classic_starts(host)
    key=GenerationWorkflowController._cache_key(host)
    assert key.random_team_count==3 and key.player_teams==(-1,)*4 and updates==[True]
    monkeypatch.setattr(classic_starts,'choose_classic_nations',lambda *a,**kw:None)
    assert not GenerationWorkflowController._configure_classic_starts(host)
    assert host.random_team_count==3 and updates==[True]
