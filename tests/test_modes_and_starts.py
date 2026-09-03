import pytest
from s3mapgen.application.paths import UPGRADED_PROFILE,UPGRADED_REFERENCE,LIBRARY
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.rules import PIPELINE_STAGES
from s3mapgen.generation.modes import MODES
from s3mapgen.generation.archetypes import ARCHETYPES

def gen():return MapGenerator(UPGRADED_PROFILE,LIBRARY,UPGRADED_REFERENCE)

@pytest.fixture(scope='module')
def upgraded4():return gen().generate(4,2026082202,mode='upgraded',archetype='continental')
@pytest.fixture(scope='module')
def upgraded20():return gen().generate(20,2026082203,mode='upgraded',archetype='continental')

def test_architecture_names_are_separate():
    assert set(MODES)=={'legacy','upgraded','custom'};assert 'continental' in ARCHETYPES;assert MODES['legacy'].implemented;assert MODES['upgraded'].implemented;assert not MODES['custom'].implemented

def test_provisional_starts_are_kept_out_of_the_content_pipeline():assert PIPELINE_STAGES.index('starts.provisional_bridge') < PIPELINE_STAGES.index('hydrology.micro_water_cleanup')

def test_upgraded_4p_hard_validators(upgraded4):
    assert upgraded4.state.metadata['starts_placed_early'] is False;assert upgraded4.state.metadata['starts_placed_provisionally'] is True;assert all(v.passed for v in upgraded4.validations if v.hard);assert upgraded4.state.metadata['mode_key']=='upgraded'

def test_upgraded_20p_starts_survive_full_pipeline(upgraded20):
    assert len(upgraded20.state.starts)==20;assert all(v.passed for v in upgraded20.validations if v.hard)

def test_custom_still_fails_explicitly():
    with pytest.raises(NotImplementedError):gen().generate(4,2026081901,mode='custom',archetype='continental')

def test_legacy_native_rebuild_is_reachable():
    result=gen().generate(2,2026081901,mode='legacy',archetype='continental',side=384)
    assert result.state.metadata['mode_key']=='legacy'
    assert result.state.metadata['engine_revision'].endswith('native-legacy-v1')
    assert len(result.state.starts)==2
    assert all(v.passed for v in result.validations if v.hard)

def test_upgraded_native_mirror_is_reachable_on_small_test_maps():
    result=gen().generate(2,2026081901,mode='upgraded',archetype='continental',side=256,mirror_mode=3)
    assert result.state.metadata['mode_key']=='upgraded'
    assert result.state.metadata['native_mode_mask']==3
    assert result.state.metadata['native_mirror_main_diagonal'] is True
    assert result.state.metadata['native_mirror_anti_diagonal'] is True
    assert all(v.passed for v in result.validations if v.hard)

def test_reported_small_seed_finishes_without_relief_loop():
    result=gen().generate(2,297650040,mode='legacy',archetype='continental',side=256)
    assert result.state.side==256
    assert result.state.metadata['native_relief_relax_passes']<=128
    assert all(v.passed for v in result.validations if v.hard)

def test_legacy_native_tables_are_transcribed():
    from s3mapgen.generation.generators.legacy.native import NATIVE_NORMAL_START_FOOTPRINT,native_build_hex_offset_bank
    from s3mapgen.map_data.constants import START_FOOTPRINT
    bank=native_build_hex_offset_bank()
    assert len(bank)==19999
    assert [(o.dx,o.dy,o.ring,o.orientation) for o in bank[:7]]==[(0,0,0,0),(1,0,1,0),(1,1,1,1),(0,1,1,2),(-1,0,1,3),(-1,-1,1,4),(0,-1,1,5)]
    assert len(NATIVE_NORMAL_START_FOOTPRINT)==33
    assert set(NATIVE_NORMAL_START_FOOTPRINT)==set(START_FOOTPRINT)

def test_upgraded_snow_is_blocked_and_swamp_chain_is_legal(upgraded4):
    from s3mapgen.map_data.constants import SNOW,SNOW_TRANS
    import numpy as np
    snow=np.isin(upgraded4.state.terrain,[SNOW_TRANS,SNOW]);assert snow.any();assert np.all(upgraded4.state.accessibility[snow]==1)
    rules={v.rule_id:v for v in upgraded4.validations};assert rules['UPGRADED_WATER_ACCESS'].passed;assert rules['UPGRADED_NO_MUD'].passed


def test_upgraded_is_independent_and_restores_start_content(upgraded4):
    assert upgraded4.state.metadata['generator'] == 'continental_upgraded_native'
    assert upgraded4.state.metadata['upgraded_base_pipeline'] == 'independent_copy_of_continental_legacy_native'
    assert upgraded4.state.metadata['upgraded_start_content_deferred'] is False
    assert all(value > 0 for value in upgraded4.state.metadata['upgraded_start_mini_swamps']['placed_cells_per_start'])
    assert upgraded4.state.metadata['upgraded_trees']['adult_start_bonus_placed'] == 41 * 4
    assert upgraded4.state.metadata['upgraded_trees']['small_start_bonus_placed'] == 21 * 4
    assert upgraded4.state.metadata['upgraded_stones']['start_bonus_stock'] == 53 * 4
    assert not any(int(v) in (23, 144, 145) for v in upgraded4.state.terrain.flat)


def test_upgraded_profile_exposes_round_mineral_and_start_rules():
    from s3mapgen.generation.generators.upgraded.profile import load_profile
    profile = load_profile()
    minerals = profile['minerals']
    assert minerals['shape_variant'] == 'round_parallelogram_compensated_test'
    assert minerals['shape_space'] == 'parallelogram_compensated'
    assert minerals['blob_aspect_min'] == minerals['blob_aspect_max'] == 1.0
    assert profile['start_bonus']['building_stones']['stock_units_per_player'] == 53
    assert profile['start_bonus']['mini_swamp']['outside_technical_zone'] is True
    assert profile['trees']['adult_global_target'] == 2736
    assert profile['trees']['adult_cluster_share'] == 0.30
    assert profile['building_stones']['global_stock_target'] == 16338
    assert len(profile['decor']['legacy_static_families']) == 16


def test_upgraded_generation_records_the_active_mineral_shape_variant(upgraded4):
    minerals = upgraded4.state.metadata['upgraded_minerals']
    assert minerals['shape_variant'] == 'round_parallelogram_compensated_test'
    assert minerals['shape_aspect_range'] == [1.0, 1.0]
    assert minerals['shape_space'] == 'parallelogram_compensated'
    rules = upgraded4.state.metadata['upgraded_start_bonus_rules']
    assert rules['outside_global_quota'] is True
    assert rules['building_stones']['stock_units_per_player'] == 53


def test_upgraded_uses_legacy_static_quotas_and_stone_states(upgraded4):
    decorations = upgraded4.state.metadata['upgraded_decorations']
    assert not any(decorations['legacy_static_shortfalls'].values())
    assert decorations['legacy_static']['reefs'] == 11
    stones = upgraded4.state.metadata['upgraded_stones']
    assert stones['global_anchors'] == 1683
    assert stones['global_stock'] == 16338
    assert stones['global_exhausted_anchors'] == 20
    assert stones['cluster_placed'] == stones['cluster_target']
    assert all(stones['id_counts'][str(object_id)] > 0 for object_id in range(115, 127))


def test_upgraded_start_bonuses_are_additional_and_forests_keep_legacy_spacing(upgraded4):
    from s3mapgen.map_data.hexgrid import hex_distance
    import numpy as np

    trees = upgraded4.state.metadata['upgraded_trees']
    assert trees['global_quota_excludes_start_bonus'] is True
    assert trees['adult_global_placed'] == trees['adult_global_requested'] == 2736
    assert trees['small_global_placed'] == trees['small_global_requested'] == 1067
    assert trees['adult_trees'] == trees['adult_global_placed'] + trees['adult_start_bonus_placed']
    assert trees['small_trees'] == trees['small_global_placed'] + trees['small_start_bonus_placed']
    assert trees['adult_start_bonus_placed'] == 41 * 4
    assert trees['small_start_bonus_placed'] == 21 * 4
    assert trees['adult_forest_min_hex_distance'] == 3
    assert all(row['adult'] == 41 for row in trees['start_forests'])

    adult_ids = tuple(range(68, 78)) + (80, 81)
    adult_points = [
        (int(x), int(y))
        for y, x in np.argwhere(np.isin(upgraded4.state.objects, adult_ids))
    ]
    for forest in trees['global_forests'] + trees['start_forests']:
        if 'center_x' not in forest:
            continue
        points = [
            (x, y)
            for x, y in adult_points
            if hex_distance(forest['center_x'], forest['center_y'], x, y)
            <= forest.get('effective_radius', forest['radius'])
        ]
        for index, (x, y) in enumerate(points):
            nearest = min(
                (hex_distance(x, y, xx, yy) for other, (xx, yy) in enumerate(points) if other != index),
                default=trees['adult_forest_min_hex_distance'],
            )
            assert nearest >= trees['adult_forest_min_hex_distance']

    stones = upgraded4.state.metadata['upgraded_stones']
    assert stones['global_quota_excludes_start_bonus'] is True
    assert stones['anchors'] == stones['global_anchors'] + stones['start_bonus_anchors']
    assert stones['stock'] == stones['global_stock'] + stones['start_bonus_stock']
    assert stones['global_anchors'] == 1683
    assert stones['global_stock'] == 16338
