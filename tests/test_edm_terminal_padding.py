from __future__ import annotations

import struct
from pathlib import Path

import numpy as np
import pytest

from s3mapgen.binary import checksum, encrypt, parse_parts, read_area, read_starts


def _part(part_type: int, payload: bytes = b"") -> bytes:
    return struct.pack("<II", part_type, 8 + len(payload)) + encrypt(payload, part_type)


def _aligned_edm(padding_size: int, *, include_terminal: bool = True) -> bytes:
    if padding_size not in (1, 2, 3):
        raise ValueError(padding_size)

    side = 1
    area_payload = struct.pack("<I", side) + bytes((17, 16, 0, 255, 0, 0))
    starts_payload = bytearray(45)
    struct.pack_into("<III", starts_payload, 0, 255, 0, 0)

    data = bytearray(8)
    data += _part(6, area_payload)
    data += _part(2, starts_payload)

    # Vary an unknown, preserved part so the terminal part finishes one, two
    # or three bytes short of the next DWORD boundary.
    filler_size = next(
        size
        for size in range(4)
        if (-(len(data) + 8 + size + (8 if include_terminal else 0))) % 4
        == padding_size
    )
    data += _part(0x12345678, bytes(range(filler_size)))
    if include_terminal:
        data += _part(0)
    data += bytes(range(1, padding_size + 1))
    assert len(data) % 4 == 0
    struct.pack_into("<I", data, 0, checksum(data))
    return bytes(data)


@pytest.mark.parametrize("padding_size", (1, 2, 3))
def test_import_accepts_confirmed_padding_after_terminal_part(tmp_path: Path, padding_size: int):
    path = tmp_path / f"aligned-tail-{padding_size}.edm"
    path.write_bytes(_aligned_edm(padding_size))

    state = read_area(path)

    assert state.side == 1
    assert np.array_equal(state.area[0, 0], np.array((17, 16, 0, 255, 0, 0), dtype=np.uint8))
    assert read_starts(path) == [(0, 0)]


def test_scaffold_parser_remains_strict_to_avoid_discarding_unknown_tail(tmp_path: Path):
    path = tmp_path / "strict-scaffold.edm"
    path.write_bytes(_aligned_edm(1))

    with pytest.raises(ValueError, match="Part scan did not end at EOF"):
        parse_parts(path)


def test_import_rejects_tail_without_terminal_part(tmp_path: Path):
    path = tmp_path / "unterminated.edm"
    path.write_bytes(_aligned_edm(1, include_terminal=False))

    with pytest.raises(ValueError, match="Part scan did not end at EOF"):
        read_area(path)
