"""Spread legal starts, then assign alliances to contiguous geographical sides.

There is no attraction of allied starts towards a shared centre. Independent
players form distinct groups. These are terrain preferences, not runtime rules.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt, label

from ..map_data.constants import HEX_STRUCTURE, MOUNTAIN_FAMILY_IDS, RIVER_IDS, WATER_IDS
from ..map_data.hexgrid import hex_distance
from .start_safety import candidate_centers, start_terrain_reservation, EDITOR_MIN_SPACING


def geographical_assignment(points, slots, teams, rng):
    """Return point indices in slot order, preserving exact group capacities.

    Two groups use a straight separating axis; more groups use contiguous
    angular sectors around the layout centre. Try seeded group orders and all
    cuts, retaining the most spatially coherent assignment, without moving any
    start. Coordinates are projected into the physical HEX6 plane first.
    """
    points = np.asarray(points, dtype=float)
    groups = {}
    for slot in slots:
        team = teams[slot] if slot < len(teams) else 0
        groups.setdefault(('team', team) if team > 0 else ('solo', slot), []).append(slot)
    members = list(groups.values())
    if len(members) <= 1 or len(members) == len(slots):
        return rng.permutation(len(slots)).tolist(), 'unrestricted'
    xy = np.column_stack((points[:, 0] - .5 * points[:, 1], np.sqrt(.75) * points[:, 1]))
    centre = xy.mean(axis=0)
    angles = np.arctan2(xy[:, 1] - centre[1], xy[:, 0] - centre[0])
    angular = np.argsort(angles, kind='stable')
    best, best_cost = None, np.inf
    if len(members) == 2:
        orders = [np.argsort(xy @ np.array([np.cos(a), np.sin(a)]), kind='stable')
                  for a in np.linspace(0, 2*np.pi, 96, endpoint=False)]
        group_orders = [rng.permutation(2).tolist()]
        strategy = 'separating_axis'
    else:
        orders = [np.roll(angular, -cut) for cut in rng.permutation(len(points))]
        group_orders = [rng.permutation(len(members)).tolist() for _ in range(32)]
        strategy = 'contiguous_sectors'
    for group_order in group_orders:
        for order in orders:
            assignment, offset, cost = {}, 0, 0.
            for group in group_order:
                group_slots = members[group]
                indices = order[offset:offset+len(group_slots)]
                offset += len(group_slots)
                local = xy[indices]
                # This chooses ownership only; it cannot pull starts together.
                cost += float(((local-local.mean(axis=0))**2).sum())
                assignment.update(zip(group_slots, map(int, indices)))
            if cost < best_cost - 1e-9:
                best, best_cost = assignment, cost
    return [best[slot] for slot in slots], strategy


def _terrain_quality(state, points):
    """Prefer mountains/rivers on the same landmass; ignore absent features."""
    land = ~np.isin(state.terrain, WATER_IDS)
    masses, count = label(land, structure=HEX_STRUCTURE)
    ys, xs = points[:, 1], points[:, 0]
    quality = np.zeros(len(points), float)
    for mass in np.unique(masses[ys, xs]):
        rows = np.flatnonzero(masses[ys, xs] == mass)
        domain = masses == mass
        scores = []
        for ids in (MOUNTAIN_FAMILY_IDS, RIVER_IDS):
            feature = domain & np.isin(state.terrain, ids)
            if feature.any():
                distance = distance_transform_edt(~feature)[ys[rows], xs[rows]]
                scores.append(1. / (1. + distance / 60.))
        if scores:
            quality[rows] = .65*np.min(scores, axis=0) + .35*np.mean(scores, axis=0)
    clearance = distance_transform_edt(state.terrain == 16)[ys, xs]
    return quality + .1*np.minimum(clearance / 12., 1.)


def place_team_starts(state, players, rng, *, island_labels=None, technical_clear=14):
    """Preserve island contracts, otherwise select spread resource-aware starts."""
    from .archetypes.masses import analyze_startable_masses
    teams = tuple(state.metadata.get('player_teams', (0,)*players))
    if island_labels is not None:
        from .archetypes.large_islands import place_island_starts
        place_island_starts(state, players, rng, island_labels, technical_clear)
        active = list(state.metadata.get('start_slot_indices', range(len(state.starts))))
        strategy = 'team_island_geography'
        # Team islands already encode ownership. On individual islands the
        # physical islands stay intact; only player ownership is reassigned.
        if not state.metadata.get('large_island_topology', {}).get('team_islands') and active:
            order, strategy = geographical_assignment(state.starts, active, teams, rng)
            state.starts = [state.starts[i] for i in order]
            meta = state.metadata['large_island_starts']
            meta['island_labels'] = [meta['island_labels'][i] for i in order]
        considered = sum(state.metadata.get('island_start_search', {}).get('candidate_counts', []))
    else:
        valid = candidate_centers(state)
        all_points = np.argwhere(valid)[:, ::-1].astype(np.int32)
        considered = len(all_points)
        pool = rng.choice(len(all_points), 16000, replace=False) if len(all_points) > 16000 else np.arange(len(all_points))
        points = all_points[pool]
        quality = _terrain_quality(state, points) if len(points) else np.empty(0)
        land_cells = int(np.count_nonzero(~np.isin(state.terrain, WATER_IDS)))
        preferred = float(np.clip(.65*np.sqrt(land_cells/max(1, players)), 65, 150))
        best, best_score = [], -np.inf
        for attempt in range(min(24, len(points))):
            first = int(rng.integers(len(points)))
            chosen = [first]
            distance = np.full(len(points), np.inf)
            while True:
                dx, dy = np.abs(points[:, 0]-points[chosen[-1], 0]), np.abs(points[:, 1]-points[chosen[-1], 1])
                delta = points-points[chosen[-1]]
                hexes = np.maximum(np.maximum(dx, dy), np.abs(delta[:, 0]-delta[:, 1]))
                euclidean = np.sqrt((delta.astype(float)**2).sum(axis=1))
                # Both preference and editor clearance must hold independently.
                if len(chosen) == 1:
                    nearest_editor = euclidean
                else:
                    nearest_editor = np.minimum(nearest_editor, euclidean)
                distance = np.minimum(distance, hexes)
                if len(chosen) >= players:
                    break
                allowed = nearest_editor >= EDITOR_MIN_SPACING
                if not allowed.any():
                    break
                scores = np.minimum(distance/preferred, 1.8) + .8*quality
                scores[~allowed] = -np.inf
                chosen.append(int(np.argmax(scores)))
            selected = points[chosen]
            spacing = np.sqrt(((selected[:, None]-selected[None, :]).astype(float)**2).sum(axis=2))
            np.fill_diagonal(spacing, np.inf)
            spread = float(np.minimum(spacing.min(axis=1)/preferred, 1.).mean()) if len(selected)>1 else 0.
            score = spread + .8*float(quality[chosen].mean())
            if (len(chosen), score) > (len(best), best_score):
                best, best_score = chosen, score
        selected = points[best]
        # If sampling missed a narrow valid pocket, try the complete pool.
        if len(selected) < players and len(all_points) > len(points):
            from .fair_starts import _farthest_combination
            complete = _farthest_combination(all_points, players, rng.permutation(len(all_points))[:32], EDITOR_MIN_SPACING)
            if len(complete) > len(selected):
                selected = all_points[complete]
        active = list(range(len(selected)))
        order, strategy = geographical_assignment(selected, active, teams, rng)
        state.starts = [tuple(map(int, selected[i])) for i in order]
        state.metadata['start_slot_indices'] = active
        state.metadata['start_disabled_slots'] = list(range(len(active), players))
    state.metadata['team_starts'] = {
        'strategy': strategy, 'candidate_count': considered,
        'allies_attracted': False, 'group_sizes': [sum(t == v for t in teams) for v in sorted(set(teams)) if v > 0],
        'players': [{'slot': slot, 'team': teams[slot] if slot < len(teams) else 0, 'x': x, 'y': y}
                    for slot, (x, y) in zip(active, state.starts)],
    }
    state.metadata.update(start_algorithm_requested='teams', start_algorithm_effective='teams',
                          starts_placed_early=True, start_footprint_cells=int(start_terrain_reservation(state).sum()))
    state.metadata['start_min_spacing'] = min((hex_distance(*a, *b) for i, a in enumerate(state.starts) for b in state.starts[i+1:]), default=0)
    state.metadata['startable_mass'] = analyze_startable_masses(state.terrain, state.starts, candidate_centers_considered=considered)
    return start_terrain_reservation(state)
