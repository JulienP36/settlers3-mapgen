from __future__ import annotations

import numpy as np

from s3mapgen.generation.generators.legacy.native_content import (
    FIXED_OBJECT_CALLS,
    RANGE_OBJECT_CALLS,
    build_native_pattern_bank,
)
from s3mapgen.generation.generators.legacy.native_terrain import generate_primary_terrain


def test_native_pattern_bank_has_the_recovered_shape_and_order():
    bank = build_native_pattern_bank()
    assert bank.shape == (19999, 2)
    assert bank.dtype == np.int16
    assert not bank.flags.writeable
    assert bank[:7].tolist() == [
        [0, 0], [1, 0], [1, 1], [0, 1], [-1, 0], [-1, -1], [0, -1]
    ]


def test_native_primary_call_tables_exclude_the_start_object_pool():
    assert len(FIXED_OBJECT_CALLS) == 94
    assert len(RANGE_OBJECT_CALLS) == 8
    fixed_ids = {call[1] for call in FIXED_OBJECT_CALLS}
    range_ids = {value for call in RANGE_OBJECT_CALLS for value in range(call[1], call[2] + 1)}
    assert not (fixed_ids | range_ids) & set(range(82, 115))


def test_native_mirror_copies_global_content_without_leaking_sentinels():
    result = generate_primary_terrain(256, 2026090202, 3)
    assert np.array_equal(result.objects, result.objects.T)
    assert np.array_equal(result.resources, result.resources.T)
    assert np.array_equal(result.objects, np.rot90(result.objects, 2).T)
    assert np.array_equal(result.resources, np.rot90(result.resources, 2).T)
    assert not np.any(result.objects == 0xFF)
    assert result.metadata["native_content_core"] == "recovered_s3_exe"
    assert result.metadata["native_pattern_bank_records"] == 19999


def test_native_content_keeps_minerals_and_fish_in_their_native_nibbles():
    result = generate_primary_terrain(384, 2026090203, 0)
    resources = result.resources
    terrain = result.terrain
    mineral = (resources & 0xF0) != 0
    assert not np.any(mineral & ~((((terrain & 0xF0) == 0x20) | ((terrain & 0xF0) == 0x80))))
    fish = ((resources & 0xF0) == 0) & ((resources & 0x0F) > 0)
    assert not np.any(fish & ((terrain & 0xF0) != 0))
    assert set(np.unique(resources[mineral]) & 0xF0) <= {0x10, 0x20, 0x30, 0x40, 0x50}
