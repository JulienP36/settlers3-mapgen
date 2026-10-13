"""Old user EDM imports: goods must not masquerade as private entities."""
from pathlib import Path
import hashlib
import struct
import pytest
from s3mapgen.map_data import binary
from s3mapgen.generation.start_diagnostics import departure_diagnostics

FIXTURES = Path(__file__).parent / 'fixtures/imported_goods_r49'

@pytest.mark.parametrize('name,count', [
    ('1-768-Echappee.edm', 200),
    ('1-768-Echappee_2.edm', 200),
    ('Echappee.edm', 120),
])
@pytest.mark.parametrize('context', ['before_objects', 'current'])
def test_original_imports_with_goods_show_departure_zones(name, count, context):
    path = FIXTURES / name
    before = hashlib.sha256(path.read_bytes()).digest()
    _, parts = binary.parse_parts(path, allow_terminal_padding=True)
    goods = [payload for kind, payload in parts if kind == 9]
    assert len(goods) == 1
    assert struct.unpack_from('<I', goods[0])[0] == count
    assert len(goods[0]) == 4 + 8 * count
    state = binary.read_area(path)
    state.starts = binary.read_starts(path)
    state.metadata.update(binary.read_start_context(path))
    state.metadata.update(source_format='EDM', territories_available=False)
    assert not state.metadata['native_start_context_unavailable']
    assert not state.metadata['start_nations_unavailable']
    report = departure_diagnostics(state, 'valid_all', context=context)
    assert not report['unavailable']
    assert report['editor']['available']
    assert report['green_count'] > 0
    assert hashlib.sha256(path.read_bytes()).digest() == before

@pytest.mark.parametrize('kind', [7, 8])
@pytest.mark.parametrize('count', [0, 1])
def test_private_entities_do_not_block_empty_map_context(monkeypatch, kind, count):
    _, parts = binary.parse_parts(FIXTURES / 'Echappee.edm')
    # Keep native private records present; the empty-map diagnostic deliberately
    # ignores them rather than treating them as occupancy.
    parts = parts + [(kind, struct.pack('<I', count))]
    monkeypatch.setattr(binary, 'parse_parts', lambda *args, **kwargs: (None, parts))
    context = binary.read_start_context('not-needed.edm')
    assert not context['native_start_context_unavailable']
    assert not context['start_nations_unavailable']
