"""Legacy trees, palms, stones and decorative objects after terrain stabilises."""

from __future__ import annotations

import numpy as np

from ....map_data.constants import DESERT, GRASS, GRASS_IDS, SNOW, SNOW_TRANS, SWAMP_IDS, WATER_IDS
from ....map_data.hexgrid import HEX6, dilate, hex_distance, neighbor_count


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


def _native_density_key(state, native_cfg: dict) -> str:
    split = int(native_cfg.get("density_split_players", 8))
    return "low" if int(state.metadata.get("players", 0)) <= split else "high"


def _native_objects_config(state, profile: dict) -> dict | None:
    """Return the SAV-calibrated object profile for the native pipeline only."""
    if state.metadata.get("generator") != "continental_legacy_native_content":
        return None
    value = profile.get("legacy_content", {}).get("native_objects")
    return value if isinstance(value, dict) else None


def _building_stone_footprint_mask(state) -> np.ndarray:
    mask = np.zeros((state.side, state.side), dtype=bool)
    for cell in state.metadata.get("building_stone_footprint_cells", ()):
        if isinstance(cell, (list, tuple)) and len(cell) == 2:
            x, y = int(cell[0]), int(cell[1])
            if 0 <= x < state.side and 0 <= y < state.side:
                mask[y, x] = True
    return mask


def add_trees(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Place the full confirmed Legacy native tree pool with loose forests."""

    terrain, objects = state.terrain, state.objects
    cfg = profile["legacy_content"]["trees"]
    scale = (state.side / 768.0) ** 2
    native_cfg = _native_objects_config(state, profile)
    density_key = _native_density_key(state, native_cfg) if native_cfg else ""
    object_clearance = dilate(reservation, 3)
    grass = np.isin(terrain, GRASS_IDS) & ~object_clearance
    adult_base = (
        cfg.get("native_adult_tree_target_768_by_density", {}).get(density_key)
        if native_cfg else None
    )
    if adult_base is None:
        adult_base = cfg["grass_adult_target_768"]
    target = min(int(round(float(adult_base) * scale)), int(grass.sum()))
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
    palm_base = (
        cfg.get("native_palm_target_768_by_density", {}).get(density_key)
        if native_cfg else None
    )
    if palm_base is None:
        palm_base = cfg["desert_palm_target_768"]
    palm_target = min(int(round(float(palm_base) * scale)), int(desert.sum()))
    points = np.argwhere(desert)
    for index in rng.permutation(len(points))[:palm_target]:
        y, x = map(int, points[index])
        objects[y, x] = int(rng.choice(np.asarray(cfg["desert_palm_ids"], dtype=np.uint8)))
        occupied[y, x] = True

    # ID 84 is kept as a separate pool.  The calibrated Legacy profile is
    # intentionally allowed to set this to zero (the native Legacy corpus did
    # not establish a non-zero ID84 quota), while the same layer can be
    # enabled by a later profile without stealing adult-tree cells.
    small_id = int(cfg.get("small_tree_id", 84))
    small_target = min(
        int(round(float(cfg.get("small_tree_target_768", 0)) * scale)),
        int(np.count_nonzero(grass & ~occupied)),
    )
    small_points = np.argwhere(grass & ~occupied)
    small_placed = 0
    small_cluster_target = int(round(small_target * float(cfg.get("small_tree_cluster_share", 0.0))))
    if small_target and len(small_points):
        # Reuse the adult forest centres.  This keeps saplings in the same
        # ecological pockets while retaining a distinct quota and ID.
        for _ in range(small_cluster_target * 16):
            if small_placed >= small_cluster_target or not centers:
                break
            cx, cy = centers[int(rng.integers(len(centers)))]
            radius = int(rng.integers(4, 14))
            x = int(np.clip(cx + rng.integers(-radius, radius + 1), 1, state.side - 2))
            y = int(np.clip(cy + rng.integers(-radius, radius + 1), 1, state.side - 2))
            if hex_distance(cx, cy, x, y) > radius or not grass[y, x] or occupied[y, x]:
                continue
            objects[y, x] = small_id
            occupied[y, x] = True
            small_placed += 1
        if small_placed < small_target:
            for index in rng.permutation(len(small_points)):
                if small_placed >= small_target:
                    break
                y, x = map(int, small_points[index])
                if occupied[y, x]:
                    continue
                objects[y, x] = small_id
                occupied[y, x] = True
                small_placed += 1
    return {
        "adult_trees": placed,
        "palm_trees": palm_target,
        "small_tree_id": small_id,
        "small_trees": small_placed,
        "small_tree_target": small_target,
        "small_tree_cluster_target": small_cluster_target,
        "tree_target": target,
        "tree_density_profile": density_key or None,
    }


def add_building_stones(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Place legal stone anchors with their actual blocked 7-cell footprint."""

    terrain, objects, access = state.terrain, state.objects, state.accessibility
    cfg = profile["legacy_content"]["building_stones"]
    scale = (state.side / 768.0) ** 2
    native_cfg = _native_objects_config(state, profile)
    density_key = _native_density_key(state, native_cfg) if native_cfg else ""
    object_clearance = dilate(reservation, 3)
    native_target = (
        native_cfg.get("building_stone_target_768_by_density", {}).get(density_key)
        if native_cfg else None
    )
    target = int(round(float(native_target if native_target is not None else cfg["global_anchor_target_768"]) * scale))
    stock_target = int(round(int(cfg["global_stock_target_768"]) * scale))
    footprint = [tuple(item) for item in cfg["footprint"]]
    blocked = object_clearance.copy()
    anchors: list[tuple[int, int]] = []
    footprint_cells: list[tuple[int, int]] = []

    def valid(x: int, y: int) -> bool:
        if blocked[y, x]:
            return False
        for dx, dy in footprint:
            xx, yy = x + dx, y + dy
            if not (1 <= xx < state.side - 1 and 1 <= yy < state.side - 1):
                return False
            if terrain[yy, xx] not in GRASS_IDS or objects[yy, xx] != 0:
                return False
        return True

    candidates = np.argwhere(np.isin(terrain, GRASS_IDS) & ~object_clearance & (objects == 0))
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
            footprint_cells.append((x + dx, y + dy))
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
    state.metadata["building_stone_footprint_cells"] = footprint_cells
    return {
        "building_stone_anchors": len(anchors),
        "building_stone_stock": int(quantities.sum()),
        "building_stone_target": target,
        "building_stone_density_profile": density_key or None,
    }


def _add_native_decorations(
    state,
    profile: dict,
    reservation: np.ndarray | None,
    rng: np.random.Generator,
) -> dict:
    """Place every static world-decor family observed in native SAV byte 14.

    The IDs, terrain supports and per-map quotas are calibrated from the
    decoded static-object corpus.  The hidden executable placement routine is
    not recovered, so this intentionally remains a deterministic reconstruction
    rather than a claim of byte-for-byte native RNG equivalence.
    """
    terrain, objects, access = state.terrain, state.objects, state.accessibility
    native_cfg = _native_objects_config(state, profile)
    if not native_cfg:
        return {}
    density_key = _native_density_key(state, native_cfg)
    scale = (state.side / 768.0) ** 2
    blocked = objects != 0
    if reservation is not None:
        blocked |= reservation
    blocked |= _building_stone_footprint_mask(state)
    counts: dict[str, int] = {}
    targets: dict[str, int] = {}

    def place_family(name: str, family_cfg: dict) -> int:
        target = int(round(float(family_cfg.get("target_768_by_density", {}).get(density_key, 0)) * scale))
        ids = tuple(int(value) for value in family_cfg.get("ids", ()))
        support = np.isin(terrain, tuple(int(value) for value in family_cfg.get("support_ids", ())))
        candidates = np.argwhere(support & ~blocked)
        placed = 0
        if target and len(candidates) and ids:
            for index in rng.permutation(len(candidates)):
                if placed >= target:
                    break
                y, x = map(int, candidates[index])
                if blocked[y, x]:
                    continue
                objects[y, x] = int(rng.choice(np.asarray(ids, dtype=np.uint8)))
                blocked[y, x] = True
                access[y, x] = 1
                placed += 1
        counts[name] = placed
        targets[name] = target
        return placed

    for name, family_cfg in native_cfg.get("families", {}).items():
        place_family(str(name), family_cfg)
    counts["native_object_targets"] = targets
    counts["native_object_density_profile"] = density_key
    counts["native_object_shortfalls"] = {
        name: max(0, targets[name] - counts[name]) for name in targets
    }
    counts["decorative_objects"] = sum(value for name, value in counts.items() if name in targets)
    return counts


def add_decorations(
    state,
    profile: dict,
    reservation: np.ndarray | None,
    rng: np.random.Generator,
) -> dict:
    """Place the legal Legacy decorative families after resource objects.

    The native profile deliberately keeps this layer conservative: reeds are
    restricted to swamp, desert props to desert, decorative stones to plain
    grass, and reefs to open deep water.  Every family has its own quota so a
    future calibration can change one family without affecting the others.
    """

    native_cfg = _native_objects_config(state, profile)
    if native_cfg:
        return _add_native_decorations(state, profile, reservation, rng)

    terrain, objects, access = state.terrain, state.objects, state.accessibility
    cfg = profile["legacy_content"].get("decor", {})
    scale = (state.side / 768.0) ** 2
    if reservation is None:
        reservation = np.zeros_like(terrain, dtype=bool)
    start_clearance = dilate(reservation, int(cfg.get("start_clearance_hex", 3)))
    occupied = objects != 0
    occupied |= _building_stone_footprint_mask(state)
    counts: dict[str, int] = {}

    def place_family(
        name: str,
        mask: np.ndarray,
        target: int,
        ids: tuple[int, ...] | list[int],
        *,
        spacing: int = 0,
        blocks: bool = False,
    ) -> int:
        candidates = np.argwhere(mask & ~start_clearance & ~occupied)
        if not target or not len(candidates) or not ids:
            counts[name] = 0
            return 0
        placed = 0
        for index in rng.permutation(len(candidates)):
            if placed >= target:
                break
            y, x = map(int, candidates[index])
            if occupied[y, x]:
                continue
            if spacing and any(
                objects[yy, xx] != 0 and hex_distance(x, y, xx, yy) < spacing
                for yy in range(max(0, y - spacing), min(state.side, y + spacing + 1))
                for xx in range(max(0, x - spacing), min(state.side, x + spacing + 1))
            ):
                continue
            object_id = int(rng.choice(np.asarray(ids, dtype=np.uint8)))
            objects[y, x] = object_id
            occupied[y, x] = True
            if blocks:
                access[y, x] = 1
            placed += 1
        counts[name] = placed
        return placed

    swamp_target = int(round(float(cfg.get("swamp_target_768", 0)) * scale))
    desert_target = int(round(float(cfg.get("desert_target_768", 0)) * scale))
    stone_target = int(round(float(cfg.get("decorative_stone_target_768", 0)) * scale))
    reef_target = int(round(float(cfg.get("reef_target_768", 0)) * scale))

    place_family(
        "swamp_reeds",
        np.isin(terrain, SWAMP_IDS),
        swamp_target,
        tuple(int(value) for value in cfg.get("swamp_reed_ids", ())),
    )
    place_family(
        "desert_decorations",
        np.isin(terrain, (20, 64, 65)),
        desert_target,
        tuple(int(value) for value in cfg.get("desert_ids", ())),
    )
    place_family(
        "decorative_stones",
        terrain == GRASS,
        stone_target,
        tuple(int(value) for value in cfg.get("decorative_stone_ids", range(1, 29))),
        spacing=int(cfg.get("decorative_stone_clearance_hex", 2)),
        blocks=True,
    )
    water = np.isin(terrain, WATER_IDS)
    open_deep_water = (terrain == 7) & (neighbor_count(~water) == 0)
    place_family(
        "reefs",
        open_deep_water,
        reef_target,
        tuple(int(value) for value in cfg.get("reef_ids", (111, 112, 113, 114))),
        spacing=2,
        blocks=True,
    )
    counts["decorative_objects"] = sum(counts.values())
    counts["decorative_targets"] = {
        "swamp_reeds": swamp_target,
        "desert_decorations": desert_target,
        "decorative_stones": stone_target,
        "reefs": reef_target,
    }
    return counts


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
