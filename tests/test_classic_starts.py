from pathlib import Path
import struct

import numpy as np
import pytest

from s3mapgen.application.paths import LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE,MAP_SCAFFOLD,EDM_SCAFFOLD
from s3mapgen.application.session.cache import GenerationCacheKey,SessionGenerationCache
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.classic_starts import ClassicRuntime
from s3mapgen.generation.core.request import GenerationRequest
from s3mapgen.map_data.binary import export_with_scaffold,parse_parts
from s3mapgen.map_data.model import MapState


FIXTURES = sorted((Path(__file__).parent/'fixtures'/'classic_starts').glob('*.npz'))


@pytest.mark.parametrize('path',FIXTURES,ids=lambda p:p.stem)
def test_active_classic_matches_full_native_selection_and_towns(path):
    with np.load(path) as reference:
        state = MapState(reference['area'].shape[0],reference['area'].copy())
        nations = tuple(map(int,reference['nations']))
        state.metadata['players'] = len(nations)
        original = state.area.copy()
        runtime = ClassicRuntime(state,nations,int(reference['goods']),42,int(reference['mirror_mode']),tuple(reference.get('slot_types',())))
        runtime.set_resources(state.resources)
        outcome = runtime.select()
        towns = [(i,s.fixed_x,s.fixed_y) for i,s in enumerate(runtime.slots) if s.placed]
        assert towns == [tuple(map(int,row)) for row in reference['towns']]
        assert (runtime.rng.a,runtime.rng.b,runtime.rng.c) == tuple(reference['rng_final'])
        assert outcome.disabled_slots == tuple(reference.get('disabled_slots',()))
        np.testing.assert_array_equal(runtime.claim,reference['claim'])
        np.testing.assert_array_equal(runtime.height,reference['height'])
        np.testing.assert_array_equal(runtime.objects,reference['objects'])
        # Town creation is the game's responsibility when loading the export.
        np.testing.assert_array_equal(state.area,original)


@pytest.mark.parametrize('mode,goods',[('legacy',2),('upgraded',3)])
def test_classic_is_after_global_content_and_export_keeps_nations(tmp_path,mode,goods):
    result = MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(
        2,42,mode=mode,side=256,start_algorithm='classic',start_nations=(0,1),player_teams=(0,20))
    state = result.state
    assert len(state.starts) == 2
    assert state.metadata['starts_status'] == 'native_classic_selection'
    assert state.metadata['starts_placed_provisionally'] is False
    assert all(v.passed for v in result.validations if v.hard)
    assert state.metadata['start_safety']['policy'] == 'native_game_chosen_nations'
    events = result.stage_log
    classic = next(i for i,s in enumerate(events) if 'starts_classic' in s)
    content = next(i for i,s in enumerate(events) if ('accessibility' in s if mode=='legacy' else 'upgraded_finalize' in s))
    assert content < classic
    output = tmp_path/'classic.MAP'
    export_with_scaffold(state,MAP_SCAFFOLD,output)
    parts = dict(parse_parts(output,allow_terminal_padding=True)[1])
    assert struct.unpack_from('<I',parts[1],8)[0] == goods
    assert bytes(parts[3][33:]) == bytes([0,0,1,0])
    assert state.metadata['player_teams'] == [0,20]
    assert [struct.unpack_from('<III',parts[2],i*45) for i in range(2)] == [
        (nation,x,y) for nation,(x,y) in zip((0,1),state.starts)]


def test_classic_requires_explicit_nations_and_rejects_extended_sizes():
    with pytest.raises(ValueError,match='nation'):
        GenerationRequest(384,4,42,start_algorithm='classic')
    for side in (832,896,960,1024):
        with pytest.raises(ValueError,match='Taille non prise en charge'):
            GenerationRequest(side,4,42,start_algorithm='classic',start_nations=(0,1,2,3))
    request = GenerationRequest(384,4,42,start_algorithm='classic',start_nations=(0,1,2,3))
    assert request.start_nations == (0,1,2,3)


def test_classic_cache_distinguishes_nation_inputs():
    first = GenerationCacheKey(42,384,4,'legacy','continental',start_algorithm='classic',start_nations=(0,1,2,3))
    second = GenerationCacheKey(42,384,4,'legacy','continental',start_algorithm='classic',start_nations=(255,0,0,0))
    cache = SessionGenerationCache(2)
    cache.put(first,'first map')
    assert cache.get(second) is None


@pytest.mark.parametrize('mode',['legacy','upgraded'])
def test_choose_remains_free_in_export_and_accepts_every_native_profile(tmp_path,mode):
    result = MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(
        2,42,mode=mode,side=256,start_algorithm='classic',start_nations=(255,1))
    state = result.state
    assert len(state.starts) == 2
    assert state.metadata['start_safety']['policy'] == 'native_game_with_free_choice_guards'
    runtime = ClassicRuntime(state,(255,1),state.metadata['classic_start_goods'],42,0)
    x,y = state.starts[0]
    assert all(runtime.valid_centers(n)[y,x] for n in range(4))
    output = tmp_path/'choose.MAP'
    export_with_scaffold(state,MAP_SCAFFOLD,output)
    player_info = dict(parse_parts(output,allow_terminal_padding=True)[1])[2]
    assert [struct.unpack_from('<I',player_info,i*45)[0] for i in range(2)] == [255,1]


def test_native_terrain_families_and_choose_intersection():
    # Expected results qualified against actual 4D99E0 in the supplied game.
    area = np.zeros((128,128,6),dtype=np.uint8)
    area[:,:,0] = 50
    area[:,:,3] = 255
    expected = {16:(True,True,True,True),64:(False,True,False,False),
                144:(False,False,True,False),80:(False,False,False,False)}
    for terrain, accepted in expected.items():
        area[:,:,1] = terrain
        runtime = ClassicRuntime(MapState(128,area.copy(),metadata={"players":1}),(255,),2,42,0)
        assert tuple(bool(runtime.valid_centers(n)[64,64]) for n in range(4)) == accepted
        assert bool(runtime.valid_centers(255)[64,64]) == all(accepted)



def test_team_input_boundaries_and_cache_separation():
    for teams in [(0,),(-1,0),(0,21),(0,1.5)]:
        with pytest.raises(ValueError,match='Équipes'):
            GenerationRequest(256,2,42,player_teams=teams)
    assert GenerationRequest(256,2,42,player_teams=(0,20)).player_teams == (0,20)
    cache = SessionGenerationCache(2)
    key = GenerationCacheKey(42,256,2,'legacy','continental',player_teams=(0,0))
    cache.put(key,'ungrouped')
    assert cache.get(GenerationCacheKey(42,256,2,'legacy','continental',player_teams=(1,1))) is None


def test_native_team_setup_is_written_in_both_export_formats(tmp_path):
    state = MapState.empty(640)
    state.starts = [(100+20*(i%5),100+20*(i//5)) for i in range(20)]
    teams = [*range(19),20]
    state.metadata['player_teams'] = teams
    nations = [0,1,2,3,255]*4
    state.metadata['player_nations'] = nations
    for scaffold,extension in [(MAP_SCAFFOLD,'MAP'),(EDM_SCAFFOLD,'EDM')]:
        output = tmp_path/f'teams.{extension}'
        export_with_scaffold(state,scaffold,output)
        setup = dict(parse_parts(output,allow_terminal_padding=True)[1])[3]
        assert len(setup) == 33+2*20
        assert list(setup[33::2]) == list(range(20))
        assert list(setup[34::2]) == [0]*20  # editor Played by: Choose
        info = dict(parse_parts(output,allow_terminal_padding=True)[1])[2]
        assert [struct.unpack_from('<I',info,i*45)[0] for i in range(20)] == nations


@pytest.mark.parametrize('mode',['legacy','upgraded'])
def test_balanced_civilizations_reach_both_exports_with_valid_starts(tmp_path,mode):
    generator = MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE)
    selected = generator.generate(2,42,mode=mode,side=256,
        start_algorithm='balanced',start_nations=(1,3))
    default = generator.generate(2,42,mode=mode,side=256,start_algorithm='balanced')
    assert selected.state.metadata['player_nations'] == [1,3]
    assert default.state.metadata['player_nations'] == [255,255]
    assert selected.state.starts == default.state.starts
    np.testing.assert_array_equal(selected.state.area,default.state.area)
    assert all(v.passed for v in selected.validations if v.hard)
    for scaffold,extension in [(MAP_SCAFFOLD,'MAP'),(EDM_SCAFFOLD,'EDM')]:
        output = tmp_path/f'civilizations.{extension}'
        export_with_scaffold(selected.state,scaffold,output)
        info = dict(parse_parts(output,allow_terminal_padding=True)[1])[2]
        assert [struct.unpack_from('<I',info,i*45)[0] for i in range(2)] == [1,3]

@pytest.mark.parametrize('side',[832,896,960,1024])
def test_classic_runtime_rejects_extended_fresh_map(side):
    state=MapState.empty(side);state.terrain[:]=16;state.height[:]=20
    state.metadata['players']=1
    with pytest.raises(ValueError,match='64..768'):
        ClassicRuntime(state,(0,),2,42,0)
