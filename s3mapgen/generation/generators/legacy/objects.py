"""Legacy trees, palms, stones and decorative objects after terrain stabilises."""

from __future__ import annotations

import numpy as np

from ....map_data.constants import DESERT, GRASS, SNOW, SNOW_TRANS, SWAMP_IDS, WATER_IDS
from ....map_data.hexgrid import HEX6, dilate, hex_distance, neighbor_count
from ...custom.content import _full_range_quantities


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


def _bounded_percent(value, default: float = 100.0, maximum: float = 200.0) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = float(default)
    return min(float(maximum), max(0.0, value))


def _half_step_quantity(value: float, default: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = float(default)
    number = min(12.0, max(1.0, number))
    return float(min(12.0, max(1.0, np.floor(number * 2.0 + 0.5) / 2.0)))


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
    cells = (
        tuple(state.metadata.get("building_stone_footprint_cells", ()))
        + tuple(state.metadata.get("legacy_start_building_stone_footprint_cells", ()))
    )
    for cell in cells:
        if isinstance(cell, (list, tuple)) and len(cell) == 2:
            x, y = int(cell[0]), int(cell[1])
            if 0 <= x < state.side and 0 <= y < state.side:
                mask[y, x] = True
    return mask


def _live_object_collision_mask(
    state,
    *,
    start_bonus_object_clearance: np.ndarray | None = None,
) -> np.ndarray:
    """Return the live two-HEX6 object clearance for an active Custom pass.

    The source cells are only actual object anchors and written Building Stone
    footprint cells.  ``start_bonus_object_clearance`` is already a written
    bonus hitbox supplied by the priority route; it is merged as-is rather
    than treated as a future zone reservation.
    """

    cells = np.asarray(state.objects != 0, dtype=bool)
    cells = cells | _building_stone_footprint_mask(state)
    mask = dilate(cells, 2)
    if start_bonus_object_clearance is not None:
        mask |= np.asarray(start_bonus_object_clearance, dtype=bool)
    return mask


def _mark_live_object_collision(mask: np.ndarray, x: int, y: int) -> None:
    """Mark one just-written one-cell object in a live hitbox field."""

    side = mask.shape[0]
    for yy in range(max(0, int(y) - 2), min(side, int(y) + 3)):
        for xx in range(max(0, int(x) - 2), min(side, int(x) + 3)):
            if hex_distance(int(x), int(y), xx, yy) <= 2:
                mask[yy, xx] = True


def add_trees(
    state,
    profile: dict,
    reservation: np.ndarray,
    rng: np.random.Generator,
    *,
    grass_support_ids: tuple[int, ...] = (GRASS,),
    collision_mask: np.ndarray | None = None,
) -> dict:
    """Place a semantic Custom Legacy tree pool without exposing native IDs."""

    terrain, objects = state.terrain, state.objects
    cfg = profile["legacy_content"]["trees"]
    scale = (state.side / 768.0) ** 2
    native_cfg = _native_objects_config(state, profile)
    density_key = _native_density_key(state, native_cfg) if native_cfg else ""
    object_clearance = (
        np.asarray(collision_mask, dtype=bool).copy()
        if collision_mask is not None
        else dilate(reservation, 3)
    )
    if collision_mask is not None:
        object_clearance |= np.asarray(reservation, dtype=bool)
    grass = np.isin(terrain, tuple(int(value) for value in grass_support_ids)) & ~object_clearance
    adult_base = (
        cfg.get("native_adult_tree_target_768_by_density", {}).get(density_key)
        if native_cfg else None
    )
    if adult_base is None:
        adult_base = cfg["grass_adult_target_768"]
    base_quota = _bounded_percent(cfg.get("base_quota_percent", 100.0), maximum=500.0)
    global_pool_target = int(round(float(adult_base) * scale * base_quota / 100.0))
    saplings_enabled = bool(cfg.get("saplings_enabled", False))
    saplings_in_global_pool = bool(cfg.get("saplings_in_global_pool", False)) if saplings_enabled else False
    sapling_global_share = _bounded_percent(cfg.get("saplings_global_share_percent", 0.0), maximum=100.0)
    if saplings_in_global_pool:
        small_target = int(round(global_pool_target * sapling_global_share / 100.0))
        target = max(0, global_pool_target - small_target)
    else:
        target = global_pool_target
        separate_quota = _bounded_percent(cfg.get("saplings_quota_percent", 0.0))
        small_target = int(round(float(adult_base) * scale * separate_quota / 100.0)) if saplings_enabled else 0
    target = min(target, int(grass.sum()))
    tree_ids = np.asarray(cfg["grass_adult_ids"], dtype=np.uint8)
    weights = np.asarray(cfg["grass_adult_weights"], dtype=float)
    weights /= weights.sum()
    occupied = objects != 0
    if collision_mask is not None:
        occupied = occupied | object_clearance
    placed = 0
    forest_mask = np.zeros_like(grass)
    forest_enabled = bool(cfg.get("forests_enabled", False))
    forest_share = _bounded_percent(cfg.get("forest_share_percent", 0.0), maximum=100.0) if forest_enabled else 0.0
    clustered_target = int(round(target * forest_share / 100.0))
    forest_variation = _bounded_percent(
        cfg.get("forest_tree_count_variation_percent", 0.0), maximum=100.0
    ) if forest_enabled else 0.0
    centers: list[tuple[int, int]] = []
    center_count = max(1, int(round(clustered_target / max(1.0, float(cfg.get("forest_trees_per_forest", 1.0)))))) if clustered_target else 0
    for _ in range(min(center_count, max(0, int(grass.sum())))):
        center = _choose_empty(grass, occupied, rng)
        if center is not None:
            centers.append(center)
            cx, cy = center
            for yy in range(max(0, cy - 12), min(state.side, cy + 13)):
                for xx in range(max(0, cx - 12), min(state.side, cx + 13)):
                    if hex_distance(cx, cy, xx, yy) <= 12 and grass[yy, xx]:
                        forest_mask[yy, xx] = True
    def forest_quotas(total: int, count: int, variation: float) -> list[int]:
        if total <= 0 or count <= 0:
            return []
        if variation <= 0:
            weights = np.ones(count, dtype=float)
        else:
            low = max(0.01, 1.0 - variation / 100.0)
            weights = rng.uniform(low, 1.0 + variation / 100.0, count)
        raw = total * weights / float(weights.sum())
        quotas = np.floor(raw).astype(int)
        remainder = int(total - int(quotas.sum()))
        if remainder:
            order = np.argsort(-(raw - quotas))
            for index in order[:remainder]:
                quotas[int(index)] += 1
        return [int(value) for value in quotas]

    forest_tree_quotas = forest_quotas(clustered_target, len(centers), forest_variation)
    forest_tree_placed: list[int] = []
    clustered_placed = 0
    for (cx, cy), quota in zip(centers, forest_tree_quotas):
        forest_placed = 0
        for _ in range(quota * 14):
            if forest_placed >= quota:
                break
            radius = int(rng.integers(4, 14))
            x = int(np.clip(cx + rng.integers(-radius, radius + 1), 1, state.side - 2))
            y = int(np.clip(cy + rng.integers(-radius, radius + 1), 1, state.side - 2))
            if hex_distance(cx, cy, x, y) > radius or not grass[y, x] or occupied[y, x]:
                continue
            objects[y, x] = int(rng.choice(tree_ids, p=weights))
            occupied[y, x] = True
            if collision_mask is not None:
                _mark_live_object_collision(object_clearance, x, y)
                occupied[...] |= object_clearance
            placed += 1
            clustered_placed += 1
            forest_placed += 1
        forest_tree_placed.append(forest_placed)
    valid = np.argwhere(grass & ~occupied)
    for index in rng.permutation(len(valid)):
        if placed >= target:
            break
        y, x = map(int, valid[index])
        if collision_mask is not None and occupied[y, x]:
            continue
        objects[y, x] = int(rng.choice(tree_ids, p=weights))
        occupied[y, x] = True
        if collision_mask is not None:
            _mark_live_object_collision(object_clearance, int(x), int(y))
            occupied[...] |= object_clearance
        placed += 1

    small_id = int(cfg.get("small_tree_id", 84))
    small_placement = str(cfg.get("saplings_placement", "everywhere")) if saplings_enabled else "everywhere"
    if small_placement == "forests_only":
        small_mask = grass & forest_mask
    elif small_placement == "outside_forests":
        small_mask = grass & ~forest_mask
    else:
        small_mask = grass
    small_points = np.argwhere(small_mask & ~occupied)
    small_placed = 0
    if small_target and len(small_points):
        for index in rng.permutation(len(small_points)):
            if small_placed >= small_target:
                break
            y, x = map(int, small_points[index])
            if occupied[y, x]:
                continue
            objects[y, x] = small_id
            occupied[y, x] = True
            if collision_mask is not None:
                _mark_live_object_collision(object_clearance, int(x), int(y))
                occupied[...] |= object_clearance
            small_placed += 1

    desert = (terrain == DESERT) & ~object_clearance & ~occupied
    palm_base = (
        native_cfg.get("native_palm_target_768_by_density", {}).get(density_key)
        if native_cfg else None
    )
    if palm_base is None:
        palm_base = cfg["desert_palm_target_768"]
    palm_quota = _bounded_percent(cfg.get("palm_quota_percent", 100.0), maximum=500.0)
    palm_target = min(int(round(float(palm_base) * scale * palm_quota / 100.0)), int(desert.sum()))
    points = np.argwhere(desert)
    for index in rng.permutation(len(points))[:palm_target]:
        y, x = map(int, points[index])
        objects[y, x] = int(rng.choice(np.asarray(cfg["desert_palm_ids"], dtype=np.uint8)))
        occupied[y, x] = True
        if collision_mask is not None:
            _mark_live_object_collision(object_clearance, int(x), int(y))
            occupied[...] |= object_clearance
    return {
        "adult_trees": placed,
        "palm_trees": palm_target,
        "small_tree_id": small_id,
        "small_trees": small_placed,
        "small_tree_target": small_target,
        "tree_target": target,
        "tree_density_profile": density_key or None,
        "base_quota_percent": base_quota,
        "saplings_enabled": saplings_enabled,
        "saplings_in_global_pool": saplings_in_global_pool,
        "saplings_global_share_percent": sapling_global_share,
        "saplings_quota_percent": _bounded_percent(cfg.get("saplings_quota_percent", 0.0)),
        "saplings_placement": small_placement,
        "forests_enabled": forest_enabled,
        "forest_share_percent": forest_share,
        "forest_trees_per_forest": float(cfg.get("forest_trees_per_forest", 1.0)),
        "forest_tree_count_variation_percent": _bounded_percent(cfg.get("forest_tree_count_variation_percent", 0.0), maximum=100.0),
        "adult_forest_target": clustered_target,
        "adult_forest_placed": clustered_placed,
        "adult_forest_shortfall": max(0, clustered_target - clustered_placed),
        "forest_count": len(centers),
        "forest_tree_quotas": forest_tree_quotas,
        "forest_tree_placed": forest_tree_placed,
        "palm_quota_percent": palm_quota,
    }


def add_building_stones(
    state,
    profile: dict,
    reservation: np.ndarray,
    rng: np.random.Generator,
    *,
    grass_support_ids: tuple[int, ...] = (GRASS,),
    collision_mask: np.ndarray | None = None,
) -> dict:
    """Place legal stone anchors with their actual blocked 7-cell footprint."""

    terrain, objects, access = state.terrain, state.objects, state.accessibility
    cfg = profile["legacy_content"]["building_stones"]
    scale = (state.side / 768.0) ** 2
    native_cfg = _native_objects_config(state, profile)
    density_key = _native_density_key(state, native_cfg) if native_cfg else ""
    object_clearance = (
        np.asarray(collision_mask, dtype=bool).copy()
        if collision_mask is not None
        else dilate(reservation, 3)
    )
    if collision_mask is not None:
        object_clearance |= np.asarray(reservation, dtype=bool)
    native_target = (
        native_cfg.get("building_stone_target_768_by_density", {}).get(density_key)
        if native_cfg else None
    )
    anchor_density = _bounded_percent(cfg.get("anchor_density_percent", 100.0))
    average_quantity = cfg.get("average_quantity")
    if average_quantity is not None:
        average_quantity = _half_step_quantity(average_quantity)
    target = int(round(float(native_target if native_target is not None else cfg["global_anchor_target_768"]) * scale * anchor_density / 100.0))
    footprint = [tuple(item) for item in cfg["footprint"]]
    blocked = object_clearance.copy()
    blocked |= dilate(np.isin(objects, (43, 44, *range(68, 82), 84)), 2)
    anchors: list[tuple[int, int]] = []
    footprint_cells: list[tuple[int, int]] = []

    def valid(x: int, y: int) -> bool:
        if blocked[y, x]:
            return False
        for dx, dy in footprint:
            xx, yy = x + dx, y + dy
            if not (1 <= xx < state.side - 1 and 1 <= yy < state.side - 1):
                return False
            if terrain[yy, xx] not in grass_support_ids or objects[yy, xx] != 0:
                return False
            if collision_mask is not None and object_clearance[yy, xx]:
                return False
        return True

    group_cfg = cfg.get("groups", {})
    group_cfg = group_cfg if isinstance(group_cfg, dict) else {}
    cluster_share = group_cfg.get("share_percent", cfg.get("cluster_share_percent"))
    if cluster_share is None:
        cluster_share = _bounded_percent(float(cfg.get("cluster_share", 0.0)) * 100.0, maximum=100.0)
    else:
        cluster_share = _bounded_percent(cluster_share, maximum=100.0)
    groups_enabled = bool(group_cfg.get("enabled", cfg.get("groups_enabled", cluster_share > 0)))
    if not groups_enabled:
        cluster_share = 0.0
    cluster_target = min(target, int(round(target * cluster_share / 100.0)))
    cluster_region = np.zeros_like(blocked)
    seeds = np.argwhere(np.isin(terrain, grass_support_ids) & ~object_clearance & (objects == 0))
    group_regions: list[np.ndarray] = []
    center_count = min(
        max(1, int(np.ceil(cluster_target / max(1.0, float(group_cfg.get("stones_per_group", cfg.get("cluster_typical_anchors", 8.0)))))))
        if target and cluster_share > 0
        else 0,
        len(seeds),
    )
    if center_count:
        for index in rng.choice(len(seeds), center_count, replace=False):
            sy, sx = map(int, seeds[index])
            radius_min = max(1, int(cfg.get("cluster_radius_min", 4)))
            radius_max = max(radius_min, int(cfg.get("cluster_radius_max", 12)))
            radius = int(rng.integers(radius_min, radius_max + 1))
            region = np.zeros_like(blocked)
            for yy in range(max(0, sy - radius), min(state.side, sy + radius + 1)):
                for xx in range(max(0, sx - radius), min(state.side, sx + radius + 1)):
                    if hex_distance(sx, sy, xx, yy) <= radius:
                        region[yy, xx] = True
                        cluster_region[yy, xx] = True
            group_regions.append(region)

    def group_quotas(total: int, count: int) -> list[int]:
        if total <= 0 or count <= 0:
            return []
        variation = _bounded_percent(
            group_cfg.get(
                "stone_count_variation_percent",
                cfg.get("cluster_count_variation_percent", 0.0),
            ),
            maximum=100.0,
        )
        if variation <= 0:
            weights = np.ones(count, dtype=float)
        else:
            low = max(0.01, 1.0 - variation / 100.0)
            weights = rng.uniform(low, 1.0 + variation / 100.0, count)
        raw = total * weights / float(weights.sum())
        quotas = np.floor(raw).astype(int)
        for index in np.argsort(-(raw - quotas))[: total - int(quotas.sum())]:
            quotas[int(index)] += 1
        return [int(value) for value in quotas]

    def place_from(mask: np.ndarray, limit: int) -> int:
        candidates = np.argwhere(mask & np.isin(terrain, grass_support_ids) & ~object_clearance & (objects == 0))
        placed = 0
        for index in rng.permutation(len(candidates)):
            if placed >= limit:
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
            placed += 1
        return placed

    cluster_placed = 0
    group_targets = group_quotas(cluster_target, len(group_regions))
    group_placed: list[int] = []
    for region, group_target in zip(group_regions, group_targets):
        placed = place_from(region, group_target)
        group_placed.append(placed)
        cluster_placed += placed
    if cluster_placed < cluster_target:
        cluster_placed += place_from(cluster_region, cluster_target - cluster_placed)
    global_placed = cluster_placed + place_from(
        np.ones_like(blocked, dtype=bool) & ~cluster_region,
        max(0, target - cluster_placed),
    )
    if global_placed < target:
        global_placed += place_from(np.ones_like(blocked, dtype=bool), target - global_placed)
    # A saturated compatible area is reported, never filled by illegal anchors.
    # Quantities map inversely to the confirmed 115..127 IDs.  Assign the
    # stock after the legal anchors have been chosen; it never changes layout.
    exhausted_count = int(rng.binomial(len(anchors), 0.01125))
    exhausted_indices = (
        set(map(int, rng.choice(len(anchors), exhausted_count, replace=False)))
        if exhausted_count
        else set()
    )
    active_indices = [index for index in range(len(anchors)) if index not in exhausted_indices]
    if average_quantity is None:
        stock_target = int(round(int(cfg["global_stock_target_768"]) * scale))
    else:
        profile_active = max(1, int(cfg.get("global_anchor_target_768", cfg.get("global_anchor_target", target))) - int(cfg.get("global_exhausted_anchor_target", 0)))
        profile_average = int(round(int(cfg["global_stock_target_768"]) / profile_active))
        if anchor_density == 100.0 and average_quantity == profile_average:
            stock_target = int(round(int(cfg["global_stock_target_768"]) * scale))
        else:
            stock_target = int(round(len(active_indices) * average_quantity))
    quantities = np.zeros(len(anchors), dtype=int)
    if average_quantity is None:
        quantities[active_indices] = 1
        remaining = max(0, stock_target - len(active_indices))
        while remaining:
            eligible = np.asarray([index for index in active_indices if quantities[index] < 12], dtype=int)
            if not len(eligible):
                break
            index = int(rng.choice(eligible))
            quantities[index] += 1
            remaining -= 1
        distribution_model = "native_random_balance"
    elif active_indices:
        distribution_mean = stock_target / len(active_indices)
        distributed = _full_range_quantities(
            len(active_indices),
            distribution_mean,
            rng,
            minimum=1,
            maximum=12,
        )
        quantities[active_indices] = distributed.astype(int)
        distribution_model = "full_range_mean_tilt"
    else:
        distribution_model = "full_range_mean_tilt"
    for (x, y), amount in zip(anchors, quantities):
        objects[y, x] = int(cfg["exhausted_id"]) - int(amount)
        if amount == 0:
            for dx, dy in footprint:
                access[y + dy, x + dx] = 0
    footprint_cells = [
        (x + dx, y + dy) for (x, y), amount in zip(anchors, quantities)
        if amount > 0 for dx, dy in footprint
    ]
    state.metadata["building_stone_anchors"] = [(x, y, int(q), "global") for (x, y), q in zip(anchors, quantities)]
    state.metadata["building_stone_footprint_cells"] = footprint_cells
    id_counts = {
        str(object_id): int(np.count_nonzero(objects == object_id))
        for object_id in range(int(cfg["active_ids"][0]), int(cfg["exhausted_id"]) + 1)
    }
    return {
        "building_stone_anchors": len(anchors),
        "building_stone_stock": int(quantities.sum()),
        "building_stone_target": target,
        "building_stone_density_profile": density_key or None,
        "anchor_density_percent": anchor_density,
        "average_quantity": average_quantity if average_quantity is not None else None,
        "cluster_share_percent": cluster_share,
        "groups_enabled": groups_enabled,
        "cluster_target": cluster_target,
        "cluster_placed": cluster_placed,
        "cluster_centers": len(group_regions),
        "cluster_group_targets": group_targets,
        "cluster_group_placed": group_placed,
        "cluster_count_variation_percent": _bounded_percent(
            group_cfg.get(
                "stone_count_variation_percent",
                cfg.get("cluster_count_variation_percent", 0.0),
            ),
            maximum=100.0,
        ),
        "global_exhausted_anchors": exhausted_count,
        "stock_target": stock_target,
        "active_average_quantity": round(
            float(quantities[active_indices].mean()), 4
        ) if active_indices else 0.0,
        "quantity_distribution_model": distribution_model,
        "id_counts": id_counts,
    }


def _add_native_decorations(
    state,
    profile: dict,
    reservation: np.ndarray | None,
    rng: np.random.Generator,
    collision_mask: np.ndarray | None = None,
) -> dict:
    """Place every static world-decor family observed in native SAV byte 14.

    The IDs, terrain supports and per-map quotas are calibrated from the
    static-object corpus.  The placement routine is not exposed by the public
    API, so this remains a deterministic compatibility implementation rather
    than a claim of byte-for-byte native RNG equivalence.
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
    if collision_mask is not None:
        blocked |= np.asarray(collision_mask, dtype=bool)
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
                if collision_mask is not None:
                    _mark_live_object_collision(blocked, x, y)
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
    collision_mask: np.ndarray | None = None,
) -> dict:
    """Place the legal Legacy decorative families after resource objects.

    The native profile deliberately keeps this layer conservative: reeds are
    restricted to swamp, desert props to desert, decorative stones to plain
    grass, and reefs to open deep water.  Every family has its own quota so a
    future calibration can change one family without affecting the others.
    """

    native_cfg = _native_objects_config(state, profile)
    if native_cfg:
        return _add_native_decorations(
            state,
            profile,
            reservation,
            rng,
            collision_mask=collision_mask,
        )

    terrain, objects, access = state.terrain, state.objects, state.accessibility
    cfg = profile["legacy_content"].get("decor", {})
    scale = (state.side / 768.0) ** 2
    if reservation is None:
        reservation = np.zeros_like(terrain, dtype=bool)
    start_clearance = (
        np.asarray(collision_mask, dtype=bool).copy()
        if collision_mask is not None
        else dilate(reservation, int(cfg.get("start_clearance_hex", 3)))
    )
    if collision_mask is not None:
        start_clearance |= np.asarray(reservation, dtype=bool)
    occupied = objects != 0
    occupied |= _building_stone_footprint_mask(state)
    occupied |= start_clearance
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
            if collision_mask is not None:
                _mark_live_object_collision(start_clearance, x, y)
                occupied[...] |= start_clearance
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
    access[(objects == 127) & ~water] = 0
    return {"blocked_water": int(water.sum()), "blocked_objects": int((objects != 0).sum())}


__all__ = ("add_building_stones", "add_decorations", "add_trees", "finalize_accessibility")
