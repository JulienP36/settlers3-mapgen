import numpy as np
import pytest
from s3mapgen.map_data.model import MapState
from s3mapgen.generation.start_diagnostics import departure_diagnostics
from s3mapgen.map_data.binary import export_with_scaffold, read_area, read_starts, parse_parts
from s3mapgen.application.paths import EDM_SCAFFOLD


def test_diagnostics_exposes_level_rejection_without_changing_map():
    state = MapState.empty(64); state.terrain[:] = 16
    state.height[:] = np.arange(64)[None,:]*3
    original = state.area.copy()
    report = departure_diagnostics(state)
    assert report['clearance'].any() and not report['valid'].any()
    assert np.array_equal(state.area, original)
    state.height[:] = 10
    assert departure_diagnostics(state, 'valid_all')['total'] > 0


def test_explicit_test_edm_preserves_retained_player_identity_and_allows_empty(tmp_path):
    state = MapState.empty(128); state.terrain[:] = 16; state.height[:] = 10
    state.starts = [(60,60)]
    state.metadata.update(players=3, start_disabled_slots=[0,2], start_slot_indices=[1],
                          player_nations=[0,2,3], player_teams=[1,7,3])
    path = tmp_path/'partial.edm'
    with pytest.raises(ValueError): export_with_scaffold(state, EDM_SCAFFOLD, path)
    export_with_scaffold(state, EDM_SCAFFOLD, path, test_edm=True)
    restored = read_area(path)
    assert read_starts(path) == state.starts
    import struct
    parts = dict(parse_parts(path,allow_terminal_padding=True)[1])
    assert struct.unpack_from('<I',parts[2])[0] == 2
    assert parts[3][33:] == bytes([0,0])  # retained player becomes native team zero
    export_with_scaffold(state, EDM_SCAFFOLD, path, test_edm=True, empty=True)
    assert read_starts(path) == []
    with pytest.raises(ValueError):
        export_with_scaffold(state, EDM_SCAFFOLD, tmp_path/'unsafe.map', test_edm=True)


def test_dense_islands_fair_places_before_objects_and_preserves_final_clearance():
    from s3mapgen.generation import MapGenerator
    from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
    from s3mapgen.generation.start_safety import require_start_safety
    for mode in ('legacy','upgraded'):
        state = MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_REFERENCE).generate(
            20,42,mode=mode,archetype='large_islands',side=768,start_algorithm='fair').state
        assert len(state.starts) == 20
        assert state.metadata['archetype_key'] == 'large_islands'
        assert state.metadata['archetype'] == 'Individual Islands'
        assert state.metadata['fair_starts']['evaluation_before_objects']
        assert all(v.passed for v in require_start_safety(state))


@pytest.mark.parametrize('policy', ['valid_conservative', 'valid_all', 'valid_0', 'valid_1', 'valid_2', 'valid_3'])
def test_selection_snapshot_ignores_later_objects_but_uses_final_terrain(policy):
    from s3mapgen.generation.start_diagnostics import capture_departure_source
    state = MapState.empty(64)
    state.terrain[:] = 16; state.height[:] = 10
    capture_departure_source(state, 'before_objects')
    before = departure_diagnostics(state, policy)
    state.objects[32,32] = 68
    state.accessibility[32,32] = 1
    state.terrain[20:25,20:25] = 80
    after = departure_diagnostics(state, policy)
    assert before['valid'][32,32]
    assert after['valid'][32,32]  # Late object/access flag is ignored here.
    assert not after['valid'][22,22]  # Final swamp replaces snapshot grass.
    assert after['total'] < before['total']
    assert after['phase'] == 'final_before_objects'
    assert not state.departure_area.flags.writeable
    current = MapState(state.side, state.area.copy())
    assert not departure_diagnostics(current, policy)['valid'][32,32]
    assert departure_diagnostics(current, policy)['phase'] == 'current'


@pytest.mark.parametrize('policy', ['valid_conservative', 'valid_all', 'valid_0'])
def test_stages_distinguish_occupation_from_terrain_and_nivellement(policy):
    state = MapState.empty(64); state.terrain[:] = 16; state.height[:] = 10
    state.objects[32,32] = 68; state.accessibility[32,32] = 1
    report = departure_diagnostics(state, policy)
    assert report['terrain'][32,32] and not report['clearance'][32,32]
    assert report['stages'][0] > report['stages'][1] == report['stages'][2]
    assert report['island_stages'] == [report['stages']]
    state.objects[:] = 0; state.accessibility[:] = 0
    state.height[:] = np.arange(64)[None,:]*3
    report = departure_diagnostics(state, policy)
    assert report['terrain'][32,32] and report['clearance'][32,32]
    assert report['stages'][0] == report['stages'][1] > report['stages'][2] == 0


def test_native_terrain_stages_follow_each_civilization():
    state = MapState.empty(64); state.terrain[:] = 64; state.height[:] = 10
    assert departure_diagnostics(state, 'valid_1')['total'] > 0
    assert departure_diagnostics(state, 'valid_0')['stages'] == [0,0,0]
    assert departure_diagnostics(state, 'valid_all')['stages'] == [0,0,0]

def test_native_diagnostics_accept_maximum_and_reject_extended_map():
    state=MapState.empty(768);state.terrain[:]=16;state.height[:]=20
    report=departure_diagnostics(state,'valid_all')
    assert not report['unavailable']
    assert report['valid'][700,700]
    state.claim[0,0]=0
    assert departure_diagnostics(state,'valid_all')['unavailable']
    assert departure_diagnostics(MapState.empty(832),'valid_all')['unavailable']
