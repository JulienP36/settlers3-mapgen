from __future__ import annotations

import numpy as np

from s3mapgen.generation.generators.legacy import native_terrain as legacy_native
from s3mapgen.generation.generators.upgraded import native_terrain as upgraded_native


class _CountingZeroRng:
    def __init__(self) -> None:
        self.calls = 0

    def next(self) -> int:
        self.calls += 1
        return 0


def test_native_river_scan_uses_refinement_cursor_and_skips_edge_rng_draws():
    side = 256
    expected_draws = 4 * (side - 15) ** 2
    engines = (
        (legacy_native, legacy_native.NativeTerrainGrid),
        (upgraded_native, upgraded_native.NativeTerrainGrid),
    )

    for module, grid_type in engines:
        assert module.NATIVE_RIVER_SCAN_START == 0x0600
        sampled: list[tuple[int, int]] = []
        original_filter = module._river_candidate_filter

        def record_candidate(
            _grid, row, col, *, margin_checked=False, allow_water_start=True
        ):
            assert margin_checked
            if not sampled:
                sampled.append((row, col))
            return False, False

        module._river_candidate_filter = record_candidate
        rng = _CountingZeroRng()
        try:
            result = module._generate_rivers(grid_type.empty(side), rng)
        finally:
            module._river_candidate_filter = original_filter

        # The game carries 0x600 from the last relief-refinement pass. At
        # 256² the first four scan positions fail the margin; the fifth is
        # (row 92, col 8), the first one allowed to draw from the PRNG.
        assert sampled == [(92, 8)]
        assert rng.calls == expected_draws
        assert result["river_attempts"] == 4 * side * side


def test_bonus_river_first_step_uses_the_shared_native_selector():
    module = upgraded_native
    original_filter = module._river_candidate_filter
    original_conflict = module._river_window_conflict
    original_selector = module._choose_first_river_step
    received: list[tuple[int, int, int, bool, np.ndarray | None]] = []

    def accept_start(_grid, _row, _col, *, margin_checked=False):
        return True, False

    def selector(grid, row, col, continuation, *, allowed_mask=None):
        received.append((row, col, grid.side, continuation, allowed_mask))
        return 0

    module._river_candidate_filter = accept_start
    module._river_window_conflict = lambda *_args: False
    module._choose_first_river_step = selector
    terrain = np.full((32, 32), module.GRASS, dtype=np.uint8)
    height = np.zeros_like(terrain)
    allowed = np.ones_like(terrain, dtype=bool)
    try:
        route = module.grow_native_bonus_river(
            terrain, height, (16, 16), allowed=allowed
        )
    finally:
        module._river_candidate_filter = original_filter
        module._river_window_conflict = original_conflict
        module._choose_first_river_step = original_selector

    assert route is None
    assert len(received) == 1
    row, col, side, continuation, received_allowed = received[0]
    assert (row, col, side, continuation) == (16, 16, 32, False)
    assert received_allowed is allowed
