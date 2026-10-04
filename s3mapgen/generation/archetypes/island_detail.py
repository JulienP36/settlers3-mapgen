"""Fixed-cell plain undulations, preserving an island's relaxed macro relief."""

from __future__ import annotations

import numpy as np

from ...map_data.constants import HEX6
from ...map_data.hexgrid import distance_from


def _fixed_cell_detail(side: int, seed: int) -> np.ndarray:
    """Refine signed midpoints at 8/4/2/1 cells, independent of island size.

    This is an independent detail source inspired by Classic's fixed scales,
    not a call to the continental/native relief generator. Periodic samples
    avoid creating a second outer coastline or consuming the river PRNG.
    """
    rng = np.random.default_rng((int(seed) ^ 0x44455441) & 0xFFFFFFFF)
    field = np.zeros((side, side), dtype=np.float32)
    field[::16, ::16] = rng.integers(-13, 14, size=(side // 16, side // 16))
    for scale, delta in ((8, 13), (4, 6), (2, 3), (1, 1)):
        step = 2 * scale
        anchors = field[::step, ::step].copy()
        shape = anchors.shape
        field[scale::step, ::step] = (
            (anchors + np.roll(anchors, -1, axis=0)) / 2
            + rng.integers(-delta, delta, size=shape)
        )
        field[::step, scale::step] = (
            (anchors + np.roll(anchors, -1, axis=1)) / 2
            + rng.integers(-delta, delta, size=shape)
        )
        field[scale::step, scale::step] = (
            (anchors + np.roll(anchors, (-1, -1), axis=(0, 1))) / 2
            + rng.integers(-delta, delta, size=shape)
        )
    return field


def add_plain_detail(
    height: np.ndarray,
    labels: np.ndarray,
    *,
    seed: int,
    water_threshold: int,
    mountain_threshold: int,
) -> tuple[np.ndarray, dict[str, int | str]]:
    """Add bounded local detail without moving water, upper foothills or peaks.

    The native relaxation has already built the macro relief. Moving only
    modified cells back towards that baseline prevents a second relaxation
    from propagating local plain changes into validated mountain heights.
    New slopes stay within ±5; existing larger signed slopes are preserved
    as upper/lower bounds, never enlarged or reversed into a new large jump.
    """
    baseline = np.asarray(height, dtype=np.int16)
    land = np.asarray(labels) > 0
    protection_height = int(mountain_threshold) - 10
    if protection_height <= int(water_threshold) + 1:
        return np.asarray(height, dtype=np.uint8).copy(), {
            "source": "fixed_cell_midpoint_8_4_2_1_and_coastal_variation", "changed_cells": 0,
            "slope_projection_passes": 0,
        }
    depth = distance_from(~land)
    guard = distance_from((baseline >= protection_height) | ~land)
    weight = (
        np.clip((depth - 1) / 4, 0, 1)
        * np.clip((protection_height - baseline) / 25, 0, 1)
        * np.clip((guard - 2) / 5, 0, 1)
    )
    # A separate, fine coastal signal breaks near-flat shoreline corridors.
    # Its width stays fixed at six land rows for every map/island size. The
    # protected high foothills and all water cells remain exact.
    rng = np.random.default_rng((int(seed) ^ 0x434F4153) & 0xFFFFFFFF)
    coastal_detail = (
        3.0 * rng.uniform(-1, 1, baseline.shape)
        * np.clip((7 - depth) / 6, 0, 1) * land
    )
    values = np.clip(np.rint(
        baseline + 1.5 * weight * _fixed_cell_detail(baseline.shape[0], seed)
        + coastal_detail
    ), 0, 255).astype(np.int16)
    values[baseline >= protection_height] = baseline[baseline >= protection_height]
    values[land] = np.maximum(int(water_threshold) + 1, values[land])
    values[~land] = baseline[~land]

    # Opposite HEX6 directions check the same pair, so keep three undirected
    # edges. Precompute bounds once, rather than allocating them each pass.
    side = baseline.shape[0]
    edges = []
    for dr, dc in HEX6:
        if dr < 0 or (dr == 0 and dc < 0):
            continue
        a = (slice(max(0, dr), side + min(0, dr)),
             slice(max(0, dc), side + min(0, dc)))
        b = (slice(max(0, -dr), side + min(0, -dr)),
             slice(max(0, -dc), side + min(0, -dc)))
        delta = baseline[a] - baseline[b]
        edges.append((a, b, np.minimum(-5, delta), np.maximum(5, delta)))
    passes = 0
    while True:
        bad = np.zeros(values.shape, dtype=bool)
        for a, b, lower, upper in edges:
            delta = values[a] - values[b]
            excess = (delta < lower) | (delta > upper)
            bad[a] |= excess
            bad[b] |= excess
        bad &= values != baseline
        if not np.any(bad):
            break
        # Each pass strictly reduces the finite L1 distance to the baseline;
        # even a difficult field must converge without an arbitrary cap.
        values[bad] -= np.sign(values[bad] - baseline[bad]).astype(np.int16)
        passes += 1
    return values.astype(np.uint8), {
        "source": "fixed_cell_midpoint_8_4_2_1_and_coastal_variation",
        "changed_cells": int(np.count_nonzero(values != baseline)),
        "slope_projection_passes": passes,
    }
