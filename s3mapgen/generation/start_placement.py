"""Early, deterministic player-start selection for procedural Legacy maps."""

from __future__ import annotations

import numpy as np

from ..map_data.constants import GRASS, START_FOOTPRINT
from ..map_data.hexgrid import dilate, hex_distance
from .archetypes.masses import analyze_startable_masses
from .start_safety import candidate_centers, separated
from .start_algorithms import resolve_start_algorithm


def _footprint_ok(terrain: np.ndarray, x: int, y: int) -> bool:
    side = terrain.shape[0]
    for dx, dy in START_FOOTPRINT:
        xx, yy = x + dx, y + dy
        if not (0 <= xx < side and 0 <= yy < side) or terrain[yy, xx] != GRASS:
            return False
    return True


def place_starts(state, players: int, rng: np.random.Generator, *, technical_clear: int = 14, island_labels: np.ndarray | None = None, start_algorithm: str = 'auto') -> np.ndarray:
    """Place starts before details and return only their exact footprints.

    Candidates are clear grass cells, sampled with a maximin rule.
    Later terrain layers use this exact footprint as a hard no-overlap mask;
    they do not receive a large dilated halo, so a mountain or biome cannot be
    visibly cut into a regular hexagon around a player.  Object placement may
    still derive its own small collision clearance from this mask.
    """

    from .start_diagnostics import capture_departure_source
    capture_departure_source(state, "selection")
    effective = resolve_start_algorithm(start_algorithm, island_labels)
    if effective in ('classic', 'fair'):
        raise ValueError('Le Classique doit être exécuté après le contenu global, avec les nations choisies')
    state.metadata['start_algorithm_requested'] = start_algorithm
    state.metadata['start_algorithm_effective'] = effective
    if effective == 'islands':
        from .archetypes.large_islands import place_island_starts
        return place_island_starts(state, players, rng, island_labels, technical_clear)

    side = state.side
    terrain = state.terrain
    edge = max(technical_clear + 8, side // 18)
    yy, xx = np.mgrid[:side, :side]
    safe = candidate_centers(state)
    candidate = (
        safe
        & (xx >= edge) & (yy >= edge)
        & (xx < side - edge) & (yy < side - edge)
    )
    # Every start is checked against the actual 33-cell footprint afterwards;
    # this broad filter makes selection fast without assuming a fixed layout.
    candidate &= ~dilate(terrain != GRASS, 8)
    ys, xs = np.where(candidate)
    if len(xs) < players:
        candidate = safe
        ys, xs = np.where(candidate)

    # A bounded candidate sample preserves deterministic performance on 768².
    pool = np.arange(len(xs))
    if len(pool) > 16000:
        pool = rng.choice(pool, 16000, replace=False)
    points = [(int(xs[i]), int(ys[i])) for i in pool if _footprint_ok(terrain, int(xs[i]), int(ys[i]))]

    # Retry the first choice when greedy maximin cannot fit every player.
    # Every attempt uses the same admissible pool and mandatory separation.
    longest = []
    for attempt in range(min(32, len(points))):
        first = points[int(rng.integers(len(points)))]
        starts = [first]
        while len(starts) < players:
            best = None
            best_score = -1
            # Random tie break makes equivalent parts of an otherwise symmetric
            # landmass deterministic per seed without hard-coded player slots.
            for x, y in points:
                if not separated(x, y, starts):
                    continue
                distance = min(hex_distance(x, y, sx, sy) for sx, sy in starts)
                score = distance * 1000 + int(rng.integers(1000))
                if score > best_score:
                    best_score, best = score, (x, y)
            if best is None:
                break
            starts.append(best)
        if len(starts) > len(longest):
            longest = starts
        if len(starts) == players:
            break
    else:
        starts = longest
    state.metadata["start_disabled_slots"] = list(range(len(starts), players))

    state.starts = starts
    state.metadata["startable_mass"] = analyze_startable_masses(
        terrain,
        starts,
        candidate_centers_considered=len(points),
    )
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
