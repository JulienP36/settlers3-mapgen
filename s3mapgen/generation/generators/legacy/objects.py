"""Legacy trees, palms and building stones after terrain has stabilised."""

from __future__ import annotations

import numpy as np

from ....map_data.constants import DESERT, GRASS, SNOW, SNOW_TRANS, WATER_IDS
from ....map_data.hexgrid import HEX6, dilate, hex_distance


def _neighbours(x: int, y: int, side: int):
    for dx, dy in HEX6:
        xx, yy = x + dx, y + dy
        if 0 <= xx < side and 0 <= yy < side:
            yield xx, yy


def _choose_empty(mask: np.ndarray, occupied: np.ndarray, rng: np.random.Generator) -> tuple[int, int] | None:
    valid = mask & ~occupied
    ys, xs = np.where(valid)
    if not len(xs):
        return None
    index = int(rng.integers(len(xs)))
    return int(xs[index]), int(ys[index])


def add_trees(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Place the full confirmed Legacy native tree pool with loose forests."""

    terrain, objects = state.terrain, state.objects
    cfg = profile["legacy_content"]["trees"]
    scale = (state.side / 768.0) ** 2
    object_clearance = dilate(reservation, 3)
    grass = (terrain == GRASS) & ~object_clearance
    target = min(int(round(int(cfg["grass_adult_target_768"]) * scale)), int(grass.sum()))
    tree_ids = np.asarray(cfg["grass_adult_ids"], dtype=np.uint8)
    weights = np.asarray(cfg["grass_adult_weights"], dtype=float)
    weights /= weights.sum()
    occupied = objects != 0
    placed = 0
    centers: list[tuple[int, int]] = []
    for _ in range(max(3, int(round(target / 75)))):
        center = _choose_empty(grass, occupied, rng)
        if center is not None:
            centers.append(center)
    # A majority belongs to loose, irregular forests; the remaining share is
    # sparse independent tree placement, matching the observed Legacy texture.
    clustered_target = int(round(target * .62))
    for _ in range(clustered_target * 14):
        if placed >= clustered_target or not centers:
            break
        cx, cy = centers[int(rng.integers(len(centers)))]
        radius = int(rng.integers(4, 14))
        x = int(np.clip(cx + rng.integers(-radius, radius + 1), 1, state.side - 2))
        y = int(np.clip(cy + rng.integers(-radius, radius + 1), 1, state.side - 2))
        if hex_distance(cx, cy, x, y) > radius or not grass[y, x] or occupied[y, x]:
            continue
        objects[y, x] = int(rng.choice(tree_ids, p=weights))
        occupied[y, x] = True
        placed += 1
    valid = np.argwhere(grass & ~occupied)
    for index in rng.permutation(len(valid)):
        if placed >= target:
            break
        y, x = map(int, valid[index])
        objects[y, x] = int(rng.choice(tree_ids, p=weights))
        occupied[y, x] = True
        placed += 1

    desert = (terrain == DESERT) & ~object_clearance & ~occupied
    palm_target = min(int(round(int(cfg["desert_palm_target_768"]) * scale)), int(desert.sum()))
    points = np.argwhere(desert)
    for index in rng.permutation(len(points))[:palm_target]:
        y, x = map(int, points[index])
        objects[y, x] = int(rng.choice(np.asarray(cfg["desert_palm_ids"], dtype=np.uint8)))
        occupied[y, x] = True
    return {"adult_trees": placed, "palm_trees": palm_target, "tree_target": target}


def add_building_stones(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Place legal stone anchors with their actual blocked 7-cell footprint."""

    terrain, objects, access = state.terrain, state.objects, state.accessibility
    cfg = profile["legacy_content"]["building_stones"]
    scale = (state.side / 768.0) ** 2
    object_clearance = dilate(reservation, 3)
    target = int(round(int(cfg["global_anchor_target_768"]) * scale))
    stock_target = int(round(int(cfg["global_stock_target_768"]) * scale))
    footprint = [tuple(item) for item in cfg["footprint"]]
    blocked = object_clearance.copy()
    anchors: list[tuple[int, int]] = []

    def valid(x: int, y: int) -> bool:
        if blocked[y, x]:
            return False
        for dx, dy in footprint:
            xx, yy = x + dx, y + dy
            if not (1 <= xx < state.side - 1 and 1 <= yy < state.side - 1):
                return False
            if terrain[yy, xx] != GRASS or objects[yy, xx] != 0:
                return False
        return True

    candidates = np.argwhere((terrain == GRASS) & ~object_clearance & (objects == 0))
    for index in rng.permutation(len(candidates)):
        if len(anchors) >= target:
            break
        y, x = map(int, candidates[index])
        if not valid(x, y):
            continue
        anchors.append((x, y))
        for yy in range(max(0, y - 3), min(state.side, y + 4)):
            for xx in range(max(0, x - 3), min(state.side, x + 4)):
                if hex_distance(x, y, xx, yy) < int(cfg["anchor_min_hex_distance"]):
                    blocked[yy, xx] = True
        for dx, dy in footprint:
            access[y + dy, x + dx] = 1
    if len(anchors) < target:
        raise RuntimeError(f"Pierres de construction insuffisantes : {len(anchors)}/{target}")
    # Quantities map inversely to the confirmed 115..127 IDs.  Assign the
    # stock after the legal anchors have been chosen; it never changes layout.
    quantities = np.full(len(anchors), 1, dtype=int)
    remaining = max(0, stock_target - int(quantities.sum()))
    while remaining:
        eligible = np.where(quantities < 12)[0]
        if not len(eligible):
            break
        index = int(rng.choice(eligible))
        quantities[index] += 1
        remaining -= 1
    for (x, y), amount in zip(anchors, quantities):
        objects[y, x] = int(cfg["exhausted_id"]) - int(amount)
    state.metadata["building_stone_anchors"] = [(x, y, int(q), "global") for (x, y), q in zip(anchors, quantities)]
    return {"building_stone_anchors": len(anchors), "building_stone_stock": int(quantities.sum())}


def add_decorations(state, profile: dict, rng: np.random.Generator) -> dict:
    """Reserved decoration phase; terrain calibration keeps it explicit.

    Terrain morphology is being calibrated first.  Keeping this explicit
    no-op phase means a later decoration implementation cannot slip ahead of
    resource objects or silently change the terrain workflow.
    """

    return {"decorative_objects": 0}


def finalize_accessibility(state) -> dict:
    terrain, objects, access = state.terrain, state.objects, state.accessibility
    water = np.isin(terrain, WATER_IDS)
    access[water] = 1
    access[np.isin(terrain, (SNOW_TRANS, SNOW))] = 1
    # Object anchors that have not already defined a stone footprint are
    # non-walkable.  This fixes the historic water-walking regression without
    # generating synthetic collision masks.
    access[(objects != 0) & ~water] = 1
    return {"blocked_water": int(water.sum()), "blocked_objects": int((objects != 0).sum())}


__all__ = ("add_building_stones", "add_decorations", "add_trees", "finalize_accessibility")
