"""A populated native MAP still yields the explicitly empty-map start mask."""
from pathlib import Path
import hashlib
import struct
import numpy as np

from s3mapgen.generation.start_diagnostics import departure_diagnostics, departure_source
from s3mapgen.generation.editor_starts import placed_start_checks
from s3mapgen.map_data.model import MapState
from s3mapgen.map_data.binary import parse_parts, read_area, read_start_context, read_starts

FIXTURE = Path(__file__).parent / 'fixtures/imported_map_r50/Wokkel.map'

def test_wokkel_map_ignores_private_entities_goods_and_initial_territories():
    digest = hashlib.sha256(FIXTURE.read_bytes()).digest()
    _, parts = parse_parts(FIXTURE, allow_terminal_padding=True)
    counts = {kind: struct.unpack_from('<I', payload)[0]
              for kind, payload in parts if kind in (7, 8, 9) and len(payload) >= 4}
    assert counts[7] == 888
    assert counts[8] == 6
    assert counts[9] == 303

    state = read_area(FIXTURE)
    state.starts = read_starts(FIXTURE)
    state.metadata.update(read_start_context(FIXTURE))
    state.metadata.update(source_format='MAP', territories_available=False)
    assert state.side == 640
    assert len(state.starts) == 4
    assert np.any(state.claim != 255)
    original = state.area.copy()

    for context, phase, expected_objects, expected_counts in (
        ('before_objects', 'export_before_objects', False, (44718, 3266)),
        ('current', 'export_current', True, (8914, 5812)),
    ):
        source, actual_phase = departure_source(state, context)
        assert actual_phase == phase
        assert np.all(source.claim == 255)
        assert bool(np.any(source.objects)) is expected_objects
        if expected_objects:
            assert np.array_equal(source.objects, state.objects)
        assert np.array_equal(state.area, original)

        report = departure_diagnostics(state, 'valid_all', context=context)
        assert not report['unavailable']
        assert report['editor']['available']
        assert (report['green_count'], report['yellow_count']) == expected_counts

    placed = placed_start_checks(state)
    assert len(placed) == 4
    assert all(row['game'] is not None for row in placed)

    assert hashlib.sha256(FIXTURE.read_bytes()).digest() == digest


def test_current_map_filter_uses_terrain_and_objects_but_not_claims_or_metadata():
    state = MapState.empty(64)
    state.terrain[:] = 16
    state.height[:] = 10
    state.objects[32, 32] = 68
    state.accessibility[32, 32] = 1
    state.claim[0, 0] = 3
    state.metadata.update(source_format='SAV', native_start_context_unavailable=True)
    before = state.area.copy()

    source, _ = departure_source(state, 'current')
    assert np.all(source.claim == 255)
    assert np.array_equal(source.objects, state.objects)
    assert not source.metadata['native_start_context_unavailable']
    assert np.array_equal(state.area, before)

    report = departure_diagnostics(state, 'valid_0', context='current')
    assert not report['unavailable']
    assert report['green_count'] > 0
    assert not report['green'][32, 32]
