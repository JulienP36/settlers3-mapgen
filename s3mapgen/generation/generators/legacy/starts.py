"""Early, deterministic player-start selection for procedural Legacy maps."""

from __future__ import annotations

import numpy as np

from ....map_data.constants import GRASS, START_FOOTPRINT
from ....map_data.hexgrid import dilate, hex_distance


def _footprint_ok(terrain: np.ndarray, x: int, y: int) -> bool:
    side = terrain.shape[0]
    for dx, dy in START_FOOTPRINT:
        xx, yy = x + dx, y + dy
        if not (0 <= xx < side and 0 <= yy < side) or terrain[yy, xx] != GRASS:
            return False
    return True


def place_starts(state, players: int, rng: np.random.Generator, *, technical_clear: int = 14) -> np.ndarray:
    """Place starts before details and return only their exact footprints.

    Candidates are naturally flat grass cells, sampled with a maximin rule.
    Later terrain layers use this exact footprint as a hard no-overlap mask;
    they do not receive a large dilated halo, so a mountain or biome cannot be
    visibly cut into a regular hexagon around a player.  Object placement may
    still derive its own small collision clearance from this mask.
    """

    side = state.side
    terrain = state.terrain
    edge = max(technical_clear + 8, side // 18)
    yy, xx = np.mgrid[:side, :side]
    candidate = (
        (terrain == GRASS)
        & (xx >= edge) & (yy >= edge)
        & (xx < side - edge) & (yy < side - edge)
    )
    # Every start is checked against the actual 33-cell footprint afterwards;
    # this broad filter makes selection fast without assuming a fixed layout.
    candidate &= ~dilate(terrain != GRASS, 8)
    ys, xs = np.where(candidate)
    if len(xs) < players:
        candidate = terrain == GRASS
        ys, xs = np.where(candidate)
    if len(xs) < players:
        raise RuntimeError("Surface herbeuse insuffisante pour les positions de départ")

    # A bounded candidate sample preserves deterministic performance on 768².
    pool = np.arange(len(xs))
    if len(pool) > 16000:
        pool = rng.choice(pool, 16000, replace=False)
    points = [(int(xs[i]), int(ys[i])) for i in pool if _footprint_ok(terrain, int(xs[i]), int(ys[i]))]
    if len(points) < players:
        raise RuntimeError("Aucune position de départ suffisamment dégagée")

    first = points[int(rng.integers(len(points)))]
    starts = [first]
    while len(starts) < players:
        best = None
        best_score = -1
        # Random tie break makes equivalent parts of an otherwise symmetric
        # landmass deterministic per seed without hard-coded player slots.
        for x, y in points:
            distance = min(hex_distance(x, y, sx, sy) for sx, sy in starts)
            score = distance * 1000 + int(rng.integers(1000))
            if score > best_score:
                best_score, best = score, (x, y)
        assert best is not None
        starts.append(best)

    state.starts = starts
    reservation = np.zeros((side, side), dtype=bool)
    for x, y in starts:
        for dx, dy in START_FOOTPRINT:
            xx, yy = x + dx, y + dy
            if 0 <= xx < side and 0 <= yy < side:
                reservation[yy, xx] = True
    state.metadata["starts_placed_early"] = True
    state.metadata["start_footprint_cells"] = int(reservation.sum())
    state.metadata["start_min_spacing"] = min(
        hex_distance(ax, ay, bx, by)
        for i, (ax, ay) in enumerate(starts) for bx, by in starts[i + 1:]
    ) if len(starts) > 1 else 0
    return reservation


__all__ = ("place_starts",)
