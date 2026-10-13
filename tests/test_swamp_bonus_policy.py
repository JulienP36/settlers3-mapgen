"""Swamp bonuses follow civilization, retained slots and land connectivity."""
import random
import numpy as np
import pytest
from s3mapgen.generation.start_bonus_policy import swamp_bonus_players
from s3mapgen.generation.generators.upgraded.content import UpgradedContent
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.map_data.model import MapState
from s3mapgen.map_data.constants import GRASS
from s3mapgen.map_data.hexgrid import component_labels,hex_distance


def fixture(nations=(255,), *, islands=True, force=False):
    state=MapState.empty(128)
    state.terrain[:]=GRASS
    if islands:state.terrain[:,64:67]=0
    state.starts=[(49,64)]
    state.metadata.update(players=len(nations),player_nations=list(nations))
    config=build_custom_config('upgraded','large_islands')
    sections=config.semantic_sections()
    sections['start_bonus']['mini_swamp'].update(radius=1,shape='hexagon',center_hex=20)
    sections['start_bonus']['force_extended_radius']=force
    # center_hex is inherited from runtime start territory below.
    content=UpgradedContent(config.with_sections(sections).runtime_profile())
    content.side=128
    content.profile['starts']['initial_territory_hex_radius']=20
    content._start_bonus_reservation=np.zeros((128,128),bool)
    content._start_bonus_swamp_mask=np.zeros((128,128),bool)
    return state,content


@pytest.mark.parametrize('nation,expected',[(0,False),(1,False),(2,True),(3,False),(255,True)])
def test_only_chinese_and_free_choice_receive_bonus(nation,expected):
    state,content=fixture((nation,),islands=False)
    before=state.area.copy()
    content._place_start_mini_swamps(state,random.Random(42))
    meta=state.metadata['upgraded_start_mini_swamps']
    assert meta['eligible_by_start']==[expected]
    assert (meta['placed_cells']>0)==expected
    if not expected:
        np.testing.assert_array_equal(state.area,before)
        assert meta['shortfalls']==[]
        assert meta['requested_cells_by_start']==[0]


def test_retained_start_uses_original_player_slot():
    state,_=fixture((0,1,2,3))
    state.metadata['start_slot_indices']=[2]
    assert swamp_bonus_players(state)==[True]
    state.metadata['start_slot_indices']=[3]
    assert swamp_bonus_players(state)==[False]


@pytest.mark.parametrize('force',[False,True])
def test_neighbour_island_cannot_supply_bonus(force):
    state,content=fixture(force=force)
    state.objects[:,:64]=68
    state.objects[50:79,35:64]=0 # clear technical start area, no legal patch at D=20
    labels,_=component_labels(state.terrain!=0)
    content._place_start_mini_swamps(state,random.Random(13))
    mask=content._start_bonus_swamp_mask
    assert not np.any(mask)
    assert state.metadata['upgraded_start_mini_swamps']['shortfalls']
    assert not np.any(mask & (labels!=labels[64,49]))
    for placement in state.metadata['upgraded_start_mini_swamps']['placements']:
        if placement['center'] is not None:
            assert labels[placement['center'][1],placement['center'][0]]==labels[64,49]


def test_bonus_on_own_island_respects_requested_ring():
    state,content=fixture()
    content._place_start_mini_swamps(state,random.Random(7))
    metadata=state.metadata['upgraded_start_mini_swamps']
    assert metadata['placed_cells']>0
    center=metadata['placements'][0]['center']
    assert abs(hex_distance(49,64,*center)-metadata['center_hex'])<=2


@pytest.mark.parametrize('mode',['legacy','upgraded'])
def test_regression_seed_places_all_swamps_on_own_islands(mode):
    from s3mapgen.generation import MapGenerator
    from s3mapgen.application.paths import LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE
    result=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(
        15,4156456048,mode=mode,archetype='large_islands',side=512,start_algorithm='islands')
    assert len(result.state.starts)==15
    assert all(v.passed for v in result.validations if v.hard)
    labels,_=component_labels(~np.isin(result.state.terrain,range(8)))
    for (sx,sy),row in zip(result.state.starts,result.state.metadata['upgraded_start_mini_swamps']['placements']):
        cx,cy=row['center']
        assert row['cells']>0
        assert labels[cy,cx]==labels[sy,sx]


@pytest.mark.parametrize('mode',['legacy','upgraded'])
@pytest.mark.parametrize('nations',[(0,1,3,0),(0,2,3,255)])
def test_real_island_validation_requires_swamps_only_for_eligible_players(mode,nations):
    from s3mapgen.generation import MapGenerator
    from s3mapgen.application.paths import LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE
    result=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(
        4,42,mode=mode,archetype='large_islands',side=512,start_algorithm='islands',start_nations=nations)
    assert len(result.state.starts)==4
    assert all(v.passed for v in result.validations if v.hard)
    meta=result.state.metadata['upgraded_start_mini_swamps']
    expected=[n in (2,255) for n in nations]
    assert meta['eligible_by_start']==expected
    assert [n>0 for n in meta['placed_cells_per_start']]==expected
