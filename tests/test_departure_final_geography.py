"""Regression for the R46 old-biome colors and independent native admission."""
from pathlib import Path
import numpy as np
import pytest
from s3mapgen.map_data.model import MapState
from s3mapgen.generation.start_diagnostics import capture_departure_source,departure_diagnostics,departure_source
from s3mapgen.generation.editor_starts import editor_start_checks,_game_point

FIXTURES=Path(__file__).parent/'fixtures'

def fresh():
    s=MapState.empty(64);s.height[:]=10;s.terrain[:]=16
    return s

@pytest.mark.parametrize('phase',['selection','before_objects'])
@pytest.mark.parametrize('terrain,game_all,editor_all',[(24,True,False),(23,True,False),(20,True,False),(64,False,False),(144,False,False),(7,False,False)])
def test_final_biomes_replace_early_grass_without_false_green(phase,terrain,game_all,editor_all):
    s=fresh();capture_departure_source(s,phase);saved=s.departure_area.copy()
    s.terrain[:]=terrain;before=s.area.copy()
    report=departure_diagnostics(s,'valid_all')
    assert bool(report['valid'][32,32])==game_all
    assert bool(report['green'][32,32])==(game_all and editor_all)
    assert bool(report['yellow'][32,32])==(game_all and not editor_all)
    assert report['phase']=='final_'+phase
    assert np.array_equal(s.area,before) and np.array_equal(s.departure_area,saved)
    assert not s.departure_area.flags.writeable

@pytest.mark.parametrize('terrain,policy',[(64,'valid_1'),(144,'valid_2')])
def test_final_nation_specific_terrain_is_not_hidden_by_snapshot(terrain,policy):
    s=fresh();capture_departure_source(s,'selection');s.terrain[:]=terrain
    report=departure_diagnostics(s,policy)
    assert report['valid'][32,32]
    assert report['green'][32,32] if terrain==64 else report['yellow'][32,32]

def test_final_height_and_claim_are_live_but_late_objects_are_ignored():
    s=fresh();capture_departure_source(s,'selection')
    s.objects[32,32]=68;s.accessibility[32,32]=1
    assert departure_diagnostics(s,'valid_all')['green'][32,32]
    s.height[:]=np.arange(64)[None,:]*3
    assert not departure_diagnostics(s,'valid_all')['valid'][32,32]
    s.height[:]=10;s.claim[0,0]=0
    assert departure_diagnostics(s,'valid_all')['unavailable']

def test_terrain_blocking_updates_without_erasing_unrelated_flags_or_objects():
    s=fresh();s.terrain[30,30]=7;s.accessibility[30,30]=1;s.accessibility[32,32]=16
    s.objects[40,40]=68;s.accessibility[40,40]=1;capture_departure_source(s,'selection')
    s.terrain[30,30]=16;s.terrain[31,31]=128;s.objects[:]=0;s.accessibility[:]=0
    source,_=departure_source(s)
    assert source.accessibility[30,30]==0
    assert source.accessibility[31,31]&1
    assert source.accessibility[32,32]==16
    assert source.objects[40,40]==68 and source.accessibility[40,40]==1

def test_classic_after_content_and_import_use_current_objects():
    for phase in (None,'after_objects'):
        s=fresh()
        if phase:capture_departure_source(s,phase)
        s.objects[32,32]=68;s.accessibility[32,32]=1
        assert not departure_diagnostics(s,'valid_all')['valid'][32,32]

@pytest.mark.parametrize('kind',['terrain','flags','claim'])
def test_game_matches_independent_original_helper_byte_matrix(kind):
    with np.load(FIXTURES/'start_admission_r47.npz') as native:
        values=native['claims'] if kind=='claim' else range(256)
        for i,value in enumerate(values):
            s=fresh();getattr(s,{'terrain':'terrain','flags':'accessibility','claim':'claim'}[kind])[:]=value
            for nation in range(4):assert _game_point(s,nation,32,32)==bool(native['game_'+kind][i,nation])

@pytest.mark.parametrize('kind',['terrain','flags','claim'])
def test_editor_matches_both_original_editor_byte_matrices(kind):
    with np.load(FIXTURES/'editor_admission_r47.npz') as native:
        values=(0,1,254,255) if kind=='claim' else range(256)
        for i,value in enumerate(values):
            s=fresh();getattr(s,{'terrain':'terrain','flags':'accessibility','claim':'claim'}[kind])[:]=value
            for j,nation in enumerate((0,1,2,3,255)):
                got=bool(editor_start_checks(s,(nation,))['valid'][32,32])
                assert got==bool(native['united_'+kind][i,j])==bool(native['standard_'+kind][i,j])

def test_game_height_profiles_and_borders_match_original_leveller():
    with np.load(FIXTURES/'start_admission_r47.npz') as native:
        for slope in range(len(native['game_height'])):
            s=fresh();s.height[:]=np.minimum(np.arange(64)[None,:]*slope,255)
            for nation in range(4):
                for i,(x,y) in enumerate(native['coords']):
                    assert _game_point(s,nation,int(x),int(y))==bool(native['game_height'][slope,nation,i])

@pytest.mark.parametrize('mode',['legacy','upgraded'])
def test_reported_768_six_islands_seed_has_no_false_green_on_final_biomes(mode):
    with np.load(FIXTURES/f'early_islands_r47_{mode}.npz') as native:
        s=MapState(768,native['area'].copy());s.departure_area=native['departure_area'].copy()
        s.departure_area.flags.writeable=False;s.departure_phase='selection';s.starts=list(map(tuple,native['starts']))
        before=s.area.copy();report=departure_diagnostics(s,'valid_all')
        assert not np.any(report['green']&(s.terrain==24))
        assert not np.any(report['valid']&np.isin(s.terrain,(64,65,144,145)))
        if mode=='legacy':
            assert report['yellow'][53,528] and not report['valid'][101,587]
        assert report['phase']=='final_selection' and np.array_equal(s.area,before)
