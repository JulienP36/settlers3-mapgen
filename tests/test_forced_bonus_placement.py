"""Forced centre order, transactional packing and tower safety regressions."""
import random
from itertools import combinations

import numpy as np
import pytest

from s3mapgen.generation.custom.bonus_placement import (
    ordered_centers, plan_objects, radius_center_pairs,
)
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.map_data.hexgrid import hex_distance
from test_start_bonus_hitboxes import _generator, _bonus_object_cells, START_PACKAGES
from test_upgraded_start_bonus_zones import _content_state


def test_forced_centres_use_nearest_ring_and_stop_at_extension_limit():
    support = np.ones((160, 160), dtype=bool)
    points = list(ordered_centers(support, 80, 80, 20, random.Random(9).shuffle))
    ds = [hex_distance(80, 80, x, y) for x, y in points]
    assert set(ds) == set(range(18, 55))
    assert [max(22, d) for d in ds] == sorted(max(22, d) for d in ds)
    assert len(points) == len(set(points))
    assert points == list(ordered_centers(support, 80, 80, 20, random.Random(9).shuffle))


def test_all_sizes_in_nearest_band_precede_farther_candidates():
    centers = [(30, 20), (33, 20), (34, 20)]
    trials = list(radius_center_pairs(centers, [5, 2], 20, 20, 10, True))
    assert trials.index((2, 30, 20)) < trials.index((5, 33, 20))


def test_object_plan_does_not_write_and_checks_full_footprint():
    legal = np.ones((64, 64), dtype=bool)
    for y in range(64):
        for x in range(64):
            if hex_distance(32, 32, x, y) <= 14:
                legal[y, x] = False
    before = legal.copy()
    footprint = ((-1,-1),(0,-1),(-1,0),(0,0),(1,0),(0,1),(1,1))
    plan = plan_objects([(47,32)], legal, np.zeros_like(legal), (15,0), 4,
                        footprint, 8, 8, np.random.default_rng(4))
    assert np.array_equal(legal, before)
    assert len(plan.adults) == 15
    assert all(hex_distance(32,32,x+dx,y+dy)>14
               for x,y in plan.adults for dx,dy in footprint)
    assert all(hex_distance(*a,*b)>=4 for a,b in combinations(plan.adults,2))


def test_impossible_object_request_returns_explicit_partial_plan():
    legal = np.zeros((32,32), dtype=bool)
    legal[15,15] = True
    plan = plan_objects([(15,15)], legal, np.zeros_like(legal), (2,1), 3,
                        ((0,0),), 2, 1, np.random.default_rng(1))
    assert len(plan.adults) == 1
    assert plan.saplings == []
    assert legal.sum() == 1


@pytest.mark.parametrize('mode', ['legacy','upgraded'])
def test_forced_bonuses_preserve_hitboxes_and_all_tower_clearings(mode):
    config = build_custom_config(mode)
    sections = config.semantic_sections()
    sections['start_bonus']['force_extended_radius'] = True
    config = config.with_sections(sections).with_start_packages(START_PACKAGES)
    output = _generator().generate(2,20260912,mode='custom',side=256,
                                   archetype='continental',custom_config=config)
    trees, stones, footprints = _bonus_object_cells(output,mode)
    assert len(trees) == 100
    assert len(stones) == 30
    assert all(hex_distance(sx,sy,x,y)>14 for sx,sy in output.state.starts
               for x,y in trees | footprints)
    assert all(hex_distance(*a,*b)>=3 for a,b in combinations(trees | stones,2))
    assert all(hex_distance(*a,*b)>=4 for a,b in combinations(stones,2))
    assert all(v.passed for v in output.validations if v.hard)


def test_forced_swamp_rejects_near_tower_footprint_and_uses_full_shape():
    config=build_custom_config('upgraded')
    sections=config.semantic_sections()
    sections['start_bonus']['force_extended_radius']=True
    sections['start_bonus']['mini_swamp'].update(radius=20,shape='hexagon')
    config=config.with_sections(sections).with_start_packages(('start_mini_swamp',))
    state,content=_content_state(256,config)
    content._place_start_mini_swamps(state,random.Random(8))
    mask=np.isin(state.terrain,(21,80,81))
    assert mask.sum()==817
    assert all(hex_distance(128,128,int(x),int(y))>14 for y,x in np.argwhere(mask))
    assert not state.metadata['upgraded_start_mini_swamps']['shortfalls']


def test_forced_mineral_zone_stays_inside_bounded_centre_search():
    config=build_custom_config('upgraded')
    sections=config.semantic_sections()
    sections['start_bonus']['force_extended_radius']=True
    sections['start_bonus']['rocky_minerals'].update(radius_min=2,radius_max=2,
        coal={'enabled':True},iron={'enabled':False},gold={'enabled':False})
    config=config.with_sections(sections).with_start_packages(('start_rocky_minerals',))
    state,content=_content_state(256,config)
    # No legal centres within D+34; abundant grass farther away must be ignored.
    for y in range(256):
        for x in range(256):
            if hex_distance(128,128,x,y)<=68:
                content._start_bonus_reservation[y,x]=True
    before=state.terrain.copy()
    content._place_start_rocky_minerals(state,random.Random(4))
    assert np.array_equal(before,state.terrain)
    assert state.metadata['upgraded_start_rocky_minerals']['shortfalls']

@pytest.mark.parametrize('mode', ['legacy','upgraded'])
@pytest.mark.parametrize('kind', ['forest','building_stones'])
def test_object_bonus_uses_first_available_extended_ring(mode,kind):
    from s3mapgen.generation.custom.objects import (
        apply_custom_legacy_start_forest, apply_custom_legacy_start_stones,
    )
    config=build_custom_config(mode)
    sections=config.semantic_sections()
    sections['start_bonus']['force_extended_radius']=True
    config=config.with_sections(sections).with_start_packages((
        'start_forest' if kind=='forest' else 'start_building_stones',))
    state,content=_content_state(192,config)
    sx,sy=state.starts[0]
    for y in range(192):
        for x in range(192):
            if 14 < hex_distance(sx,sy,x,y) <= 36:
                state.terrain[y,x]=32
    if mode=='legacy':
        fn=apply_custom_legacy_start_forest if kind=='forest' else apply_custom_legacy_start_stones
        meta=fn(state,config.runtime_profile(),config.semantic_sections(),np.random.default_rng(8))
        records=meta['forests' if kind=='forest' else 'groups']
        assert not meta['shortfalls']
    elif kind=='forest':
        content._place_trees(state,np.random.default_rng(8),random.Random(8))
        meta=state.metadata['upgraded_trees']
        records=meta['start_forests']
        assert not meta['shortfalls']
    else:
        content._place_building_stones(state,np.random.default_rng(8),random.Random(8),phase='start')
        meta=state.metadata['upgraded_stones']
        records=meta['start_centers']
        assert not meta['shortfalls']
    assert len(records)==1
    assert hex_distance(sx,sy,records[0]['center_x'],records[0]['center_y'])==37


def test_forced_lake_and_entire_river_avoid_all_towers():
    config=build_custom_config('upgraded')
    sections=config.semantic_sections()
    sections['start_bonus']['force_extended_radius']=True
    sections['start_bonus']['lake_fish_river'].update(
        radius_min=2,radius_max=2,water_proximity_from_territory_border=0)
    config=config.with_sections(sections).with_start_packages(('start_lake_fish_river',))
    state,content=_content_state(192,config)
    state.starts=[(96,96),(70,70)]
    content._place_start_lake_fish_river(state,random.Random(3))
    assert content._start_bonus_lake_records
    for record in content._start_bonus_lake_records:
        sx,sy=state.starts[record['player']-1]
        assert 32<=hex_distance(sx,sy,record['center_x'],record['center_y'])<=68
        assert record['river_points']
        assert all(hex_distance(sx,sy,x,y)>20 for sx,sy in state.starts
            for x,y in record['core_points']+record['shore_points']+record['river_points'])
