import struct

from s3mapgen.binary import (
    GOODS_DEFAULT_HIGH,
    GOODS_DEFAULT_MEDIUM,
    _goods_default_for_state,
    _set_players,
)
from s3mapgen.model import MapState


def _parts():
    return [
        [1, bytearray(struct.pack('<6I', 0, 20, 19, 0, 0, 0))],
        [2, bytearray(45 * 20)],
        [3, bytearray(33 + 40)],
    ]


def test_legacy_goods_default_is_medium():
    state = MapState.empty(32)
    state.metadata['mode_key'] = 'legacy'
    assert _goods_default_for_state(state) == GOODS_DEFAULT_MEDIUM


def test_upgraded_goods_default_is_high():
    state = MapState.empty(32)
    state.metadata['mode_key'] = 'upgraded'
    assert _goods_default_for_state(state) == GOODS_DEFAULT_HIGH


def test_player_writer_never_uses_player_count_as_goods_default():
    parts = _parts()
    starts = [(10 + i, 10 + i) for i in range(20)]
    _set_players(parts, starts, GOODS_DEFAULT_MEDIUM)
    vals = struct.unpack_from('<6I', parts[0][1], 0)
    assert vals[1] == 20
    assert vals[2] == GOODS_DEFAULT_MEDIUM


def test_upgraded_writer_sets_high_goods_default():
    parts = _parts()
    starts = [(10 + i, 10 + i) for i in range(20)]
    _set_players(parts, starts, GOODS_DEFAULT_HIGH)
    vals = struct.unpack_from('<6I', parts[0][1], 0)
    assert vals[2] == GOODS_DEFAULT_HIGH
