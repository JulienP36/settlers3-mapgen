from pathlib import Path
import numpy as np
import pytest
from s3mapgen.map_data.model import MapState
from s3mapgen.generation.editor_starts import editor_occupation,editor_start_checks,placed_start_checks
from s3mapgen.generation.start_diagnostics import departure_diagnostics,capture_departure_source
from s3mapgen.application.rendering.preview import _overlay_rgb,render
from s3mapgen.application.ui.i18n.viewer import VALID_START_LABELS

FIXTURES=Path(__file__).parent/'fixtures'

@pytest.mark.parametrize('object_id',[1,2,13,68,84,115,127,128,216,247,255])
def test_object_footprint_matches_native_virtual_rebuild(object_id):
    objects=np.zeros((32,32),np.uint8);objects[16,16]=object_id
    grid,known=editor_occupation(objects)
    with np.load(FIXTURES/'editor_occupation_united.npz') as data:
        assert known
        assert np.array_equal(grid,data[f'object_{object_id}'] != 0)

@pytest.mark.parametrize('nation',[0,1,2,3,255])
def test_local_editor_admission_matches_original_native_block(nation):
    with np.load(FIXTURES/'editor_local_united.npz') as data:
        state=MapState(64,data['area']);checks=editor_start_checks(state,(nation,))
        row=data['expected'][list(data['nations']).index(nation)]
        assert [bool(checks['valid'][y,x]) for x,y in data['points']]==list(row)

def fresh():
    state=MapState.empty(64);state.terrain[:]=16;state.height[:]=10
    return state

def test_yellow_is_native_game_minus_editor_not_mapgen_conservative():
    state=fresh();state.terrain[32,27]=48 # editor (-5,0), outside Roman town
    report=departure_diagnostics(state,'valid_0')
    assert report['valid'][32,32] and report['yellow'][32,32]
    assert not report['editor']['terrain'][32,32]
    state=fresh();state.objects[32,26]=2 # anchor-only object; extra MapGen halo
    report=departure_diagnostics(state,'valid_0')
    assert report['green'][32,32]
    assert not departure_diagnostics(state,'valid_conservative')['valid'][32,32]

def test_editor_flags_stricter_than_game_and_no_editor_height_test():
    state=fresh();state.accessibility[32,32]=16
    report=departure_diagnostics(state,'valid_0')
    assert report['yellow'][32,32] and report['editor']['terrain'][32,32]
    assert not report['editor']['clearance'][32,32]
    state=fresh();state.height[:]=np.arange(64)[None,:]*3
    report=departure_diagnostics(state,'valid_0')
    assert report['editor']['valid'][32,32] and not report['valid'][32,32]
    assert report['green'][32,32] and report['relocation'][32,32]
    assert not report['yellow'][32,32]

def test_editor_egyptians_accept_exact_desert_ids_but_not_whole_family():
    state=fresh();state.terrain[:]=64
    assert editor_start_checks(state,(1,))['valid'][32,32]
    assert not editor_start_checks(state,(0,))['valid'][32,32]
    state.terrain[:]=66
    assert departure_diagnostics(state,'valid_1')['yellow'][32,32]

def test_whole_map_counts_use_final_geography_and_ignore_later_objects():
    state=fresh();state.terrain[32,27]=48;capture_departure_source(state,'before_objects')
    before=departure_diagnostics(state,'valid_0')
    state.objects[:]=68
    state.accessibility[:]=1
    after=departure_diagnostics(state,'valid_0')
    assert np.array_equal(before['green'],after['green'])
    assert np.array_equal(before['yellow'],after['yellow'])
    assert after['total']==after['green_count']+after['yellow_count']
    assert sum(v[0] for v in after['island_colors'])==after['green_count']
    assert sum(v[1] for v in after['island_colors'])==after['yellow_count']

def test_placed_starts_use_final_state_nations_and_spacing():
    state=fresh();state.starts=[(30,32),(40,32)];state.metadata['player_nations']=[0,0]
    capture_departure_source(state,'before_objects')
    rows=placed_start_checks(state)
    assert all(r['game'] and not r['editor'] and r['status']=='yellow' for r in rows)
    assert all(r['editor_reason']=='spacing' for r in rows)
    state.starts=[(32,32)];state.metadata['player_nations']=[1];state.terrain[:]=64
    assert placed_start_checks(state)[0]['status']=='green'
    state.metadata['player_nations']=[0]
    assert placed_start_checks(state)[0]['status']=='invalid'
    state.metadata['player_nations']=[1];state.objects[32,32]=68
    assert placed_start_checks(state)[0]['editor_reason']=='occupation'

def test_point_game_check_agrees_with_existing_native_profile_masks():
    from s3mapgen.generation.classic_starts import ClassicRuntime
    from s3mapgen.generation.editor_starts import _game_point
    state=fresh();state.metadata['players']=1
    state.height[:]=np.arange(64)[None,:];state.terrain[20:25,20:25]=64
    runtime=ClassicRuntime(state,(0,),2,0,0)
    for nation in range(4):
        valid=runtime.valid_centers(nation)
        for x,y in [(0,0),(15,15),(16,20),(32,32),(48,48),(49,49)]:
            assert _game_point(state,nation,x,y)==bool(valid[y,x])

def test_raster_uses_green_yellow_and_uncolored_game_refusals_without_mutation():
    state=fresh();state.terrain[32,27]=48;before=state.area.copy()
    rgb=_overlay_rgb(state,'valid_starts','valid_0')
    assert tuple(rgb[32,32])==(255,210,45)
    assert tuple(rgb[40,40])==(50,255,100)
    # Original editor's stalled iterator admits this border point; the game
    # cannot keep its exact position. It must remain visible with that warning.
    assert tuple(rgb[0,0]) == (50,255,100)
    assert np.array_equal(state.area,before)
    state.starts=[(32,32)];state.metadata['player_nations']=[0]
    for projection in ('square','parallelogram'):
        image=render(state,view='valid_starts',heatmap_resource='valid_0',projection=projection)
        assert image.size[0]>0

def test_no_visible_conservative_policy_and_unsupported_editor_footprint_not_miscolored():
    assert all('valid_conservative' not in labels for labels in VALID_START_LABELS.values())
    state=fresh();state.objects[32,32]=129
    report=departure_diagnostics(state,'valid_0')
    assert not report['editor']['available']
    assert not report['green'].any() and not report['yellow'].any()

def test_old_visible_filter_preference_migrates_and_new_filter_persists(tmp_path,monkeypatch):
    import json
    from s3mapgen.application.settings import preferences as prefs
    path=tmp_path/'settings.json';path.write_text(json.dumps({'valid_start_filter':'valid_conservative'}))
    monkeypatch.setattr(prefs,'settings_path',lambda:path)
    assert prefs.load_settings()['valid_start_filter']=='valid_all'
    prefs.save_settings({'valid_start_filter':'valid_2'})
    assert prefs.load_settings()['valid_start_filter']=='valid_2'

def test_imported_nations_are_read_and_current_context_ignores_stale_start_metadata(tmp_path):
    from s3mapgen.map_data.binary import export_with_scaffold,read_start_context
    from s3mapgen.application.paths import EDM_SCAFFOLD
    state=fresh();state.starts=[(32,32)];state.metadata['player_nations']=[1]
    path=tmp_path/'egypt.edm';export_with_scaffold(state,EDM_SCAFFOLD,path)
    context=read_start_context(path)
    assert context['player_nations']==[1] and not context['start_nations_unavailable']
    state.metadata.update(context);state.terrain[:]=64
    assert placed_start_checks(state)[0]['status']=='green'
    state.metadata['native_start_context_unavailable']=True
    report=departure_diagnostics(state,'valid_1',context='current')
    assert not report['unavailable'] and report['green'][32,32]
    assert placed_start_checks(state)[0]['status']=='green'
    # Selection-time generation still fails closed when explicitly marked
    # unknown; the imported current-map question does not use this metadata.
    report=departure_diagnostics(state,'valid_1')
    assert report['unavailable'] and not report['green'].any() and not report['yellow'].any()
