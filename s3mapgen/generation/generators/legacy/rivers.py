"""Downhill river routing that always terminates at the ocean or a lake."""

from __future__ import annotations

import numpy as np

from ...core.noise import warped_fractal_field
from ....map_data.constants import GRASS, MOUNTAIN_IDS, RIVER_IDS, SHORE, WATER_IDS
from ....map_data.hexgrid import HEX6, component_labels, distance_from, hex_distance, neighbor_count


def _neighbours(x: int, y: int, side: int):
    for dx, dy in HEX6:
        xx, yy = x + dx, y + dy
        if 0 <= xx < side and 0 <= yy < side:
            yield xx, yy


def _river_id(rng: np.random.Generator, shares: dict) -> int:
    values = np.asarray([float(shares[str(key)]) for key in RIVER_IDS], dtype=float)
    values /= values.sum()
    return int(rng.choice(np.asarray(RIVER_IDS), p=values))


def add_rivers(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Route many short grass-only river systems to existing water.

    Unlike the discarded early pass, a river can neither originate in terrain
    water nor wander into mountain terrain.  Its precomputed outlet distance
    is monotonic, so each accepted path has a real hydrological endpoint.
    """

    side = state.side
    terrain, height = state.terrain, state.height
    cfg = profile["rivers"]
    water = np.isin(terrain, WATER_IDS)
    mountain_distance = distance_from(
        np.isin(terrain, MOUNTAIN_IDS),
        max_distance=int(cfg["source_max_mountain_distance"]),
    )
    # The final river cell is allowed to replace Shore, but routing otherwise
    # stays within grass and cannot draw blue lines through mountains.
    routeable = (terrain == GRASS) & ~reservation & (mountain_distance >= 2)
    outlets = (terrain == SHORE) & (neighbor_count(water) > 0) & ~reservation
    allowed = routeable | outlets
    cap = int(profile["supported_sizes"][str(side)]["river_practical_max_cells"])
    outlet_distance = distance_from(outlets, max_distance=cap, passable=allowed)
    outlet_min = int(cfg["source_outlet_distance_min"])
    outlet_max = min(cap - 2, int(cfg["source_outlet_distance_max"]))
    reachable = routeable & (outlet_distance >= outlet_min) & (outlet_distance <= outlet_max)
    source = (
        reachable
        & (height >= int(cfg["source_min_height"]))
        & (mountain_distance >= int(cfg["source_min_mountain_distance"]))
        & (mountain_distance <= int(cfg["source_max_mountain_distance"]))
    )
    ys, xs = np.where(source)
    target = int(round(
        side * side
        * float(cfg["fraction_map_by_side"][str(side)])
        * float(cfg.get("target_fraction_scale", 1.0))
    ))
    if not len(xs) or not outlets.any() or target <= 0:
        return {"river_cells": 0, "river_systems": 0, "river_target": target}

    # A broad field alone tends to make every path follow the shortest
    # outlet-gradient like a ruler.  This second, finer field supplies local
    # lateral pressure so the accepted route can visibly lézarder while the
    # outlet-distance field remains the hard connectivity rail.
    texture = warped_fractal_field(side, rng, scales=(.025, .070, .15), warp_scale=.032, warp_strength=.042)
    meander = warped_fractal_field(side, rng, scales=(.055, .13, .28), warp_scale=.048, warp_strength=.075)
    occupied = np.zeros_like(routeable, dtype=bool)
    occupied_buffer = np.zeros_like(routeable, dtype=bool)
    river_cells = 0
    systems = 0
    desired_systems = int(cfg["system_target_by_side"][str(side)])
    source_separation = int(cfg["source_min_separation"])
    source_points: list[tuple[int, int]] = []
    accepted_lengths: list[int] = []

    candidates = np.arange(len(xs))
    for _ in range(desired_systems * 8):
        if river_cells >= target or systems >= desired_systems or not len(candidates):
            break
        # Select a coastal source around the requested short native length.
        # This avoids the old paths that crossed most of the continent merely
        # because a distant outlet happened to be reachable.
        desired_length = int(np.clip(
            rng.normal(float(cfg["target_length_mean"]), float(cfg["target_length_stddev"])),
            outlet_min,
            outlet_max,
        ))
        candidate_distances = outlet_distance[ys[candidates], xs[candidates]]
        matching = candidates[np.abs(candidate_distances - desired_length) <= 3]
        pool = matching if len(matching) else candidates
        selected = int(pool[int(rng.integers(len(pool)))])
        candidates = candidates[candidates != selected]
        x, y = int(xs[selected]), int(ys[selected])
        if any(hex_distance(x, y, px, py) < source_separation for px, py in source_points):
            continue
        if occupied_buffer[y, x]:
            continue
        path: list[tuple[int, int]] = []
        seen: set[tuple[int, int]] = set()
        cx, cy = x, y
        previous_direction: tuple[int, int] | None = None
        reached = False
        path_cap = min(cap, desired_length + 3)
        for _step in range(path_cap):
            if (cx, cy) in seen:
                break
            seen.add((cx, cy)); path.append((cx, cy))
            if outlets[cy, cx]:
                reached = True
                break
            options = []
            current_distance = int(outlet_distance[cy, cx])
            for nx, ny in _neighbours(cx, cy, side):
                if not allowed[ny, nx] or occupied_buffer[ny, nx] or (nx, ny) in seen:
                    continue
                next_distance = int(outlet_distance[ny, nx])
                # A limited same-contour sidestep supplies natural meanders.
                # When the remaining cap becomes tight we require progress so
                # every accepted line still reaches an actual outlet.
                if next_distance >= 32767 or next_distance > current_distance + 1:
                    continue
                if len(path) + next_distance >= path_cap - 1 and next_distance >= current_distance:
                    continue
                # The outlet field is the safety rail, not a straight-line
                # drawing instruction: a height term and a warped flow field
                # decide among nearby valid cells before the final approach.
                fall = int(height[cy, cx]) - int(height[ny, nx])
                progress = current_distance - next_distance
                direction = (nx - cx, ny - cy)
                turn = 0.0
                if previous_direction is not None:
                    turn = .95 if direction != previous_direction else -.38
                score = (
                    .48 * progress
                    + .10 * fall
                    + 1.85 * float(texture[ny, nx])
                    + 1.30 * float(meander[ny, nx])
                    + .70 * turn
                    - .16 * abs(float(texture[ny, nx] - texture[cy, cx]))
                    + float(rng.normal(0, .52))
                )
                options.append((score, nx, ny))
            if not options:
                break
            _, nx, ny = max(options, key=lambda item: item[0])
            previous_direction = (nx - cx, ny - cy)
            cx, cy = nx, ny
        if not reached or len(path) < min(5, desired_length // 2):
            continue
        for px, py in path:
            terrain[py, px] = _river_id(rng, cfg["width_shares"])
            occupied[py, px] = True
            occupied_buffer[py, px] = True
            for nx, ny in _neighbours(px, py, side):
                occupied_buffer[ny, nx] = True
        river_cells += len(path)
        systems += 1
        source_points.append((x, y))
        accepted_lengths.append(len(path))

    state.metadata["river_target_cells"] = target
    # A one-cell Shore48 remnant is neither a real beach nor a useful mouth.
    # Merge it into its adjoining river when present, otherwise into water.
    shore_labels, shore_count = component_labels(terrain == SHORE)
    for label in range(1, shore_count + 1):
        component = shore_labels == label
        if int(component.sum()) != 1:
            continue
        if np.any(component & reservation):
            continue
        y, x = (int(value) for value in np.argwhere(component)[0])
        river_neighbours = [terrain[ny, nx] for nx, ny in _neighbours(x, y, side) if terrain[ny, nx] in RIVER_IDS]
        terrain[y, x] = int(river_neighbours[0]) if river_neighbours else 0
        state.height[y, x] = 0
    return {
        "river_cells": river_cells,
        "river_systems": systems,
        "river_target": target,
        "river_mean_length": float(np.mean(accepted_lengths)) if accepted_lengths else 0.0,
    }


__all__ = ("add_rivers",)
