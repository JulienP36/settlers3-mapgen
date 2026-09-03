"""Upgraded content pass.

This module is intentionally independent from the Legacy generator.  It owns
the calibrated Upgraded mineral/fish routines and the final object pass.  Dev
5 restores the content that belongs around the already-positioned starts:
mini-swamps, forest bonuses and building-stone bonuses.  Start coordinates
remain the isolated provisional bridge owned by :mod:`starts`.
"""

from __future__ import annotations

from collections import deque
import heapq
import math
import random

import numpy as np
from scipy import ndimage

from ....map_data.constants import (
    DESERT_IDS,
    GRASS,
    GRASS_SWAMP_TRANS,
    HEX6,
    MOUNTAIN_FAMILY_IDS,
    REEF_IDS,
    RIVER_IDS,
    SNOW,
    SNOW_TRANS,
    SWAMP,
    SWAMP_TRANS,
    WATER_IDS,
    SWAMP_IDS,
)
from ....map_data.hexgrid import hex_distance, neighbor_count


_HEX_STRUCTURE = np.array([[1, 1, 0], [1, 1, 1], [0, 1, 1]], dtype=bool)


def _make_blob_sizes(total: int, count: int, rng: np.random.Generator, pr: random.Random,
                     minimum: int = 18, maximum: int = 105) -> list[int]:
    total = int(total)
    if total <= 0:
        return []
    if total < int(minimum):
        return [total]
    count = max(1, min(int(count), total // max(1, int(minimum))))
    mean = total / count
    raw = rng.lognormal(mean=math.log(max(5, mean)) - 0.10, sigma=0.34, size=count)
    raw = np.clip(raw, minimum, maximum)
    sizes = np.rint(raw / raw.sum() * total).astype(int)
    sizes = np.clip(sizes, minimum, maximum)
    difference = total - int(sizes.sum())
    while difference:
        index = pr.randrange(count)
        if difference > 0 and sizes[index] < maximum:
            sizes[index] += 1
            difference -= 1
        elif difference < 0 and sizes[index] > minimum:
            sizes[index] -= 1
            difference += 1
    return sorted(map(int, sizes), reverse=True)


def _grow_ovoid_no_gap(region: np.ndarray, occupied: np.ndarray, target: int,
                       aspect: float, angle: float, pr: random.Random,
                       shape_space: str = "grid") -> list[tuple[int, int]] | None:
    """Grow one connected solid blob without creating a forced moat.

    ``grid`` preserves the historical square-array metric.  The upgraded
    profile can instead request ``parallelogram_compensated``: the priority is
    then evaluated in the same linear space as ``project_parallelogram`` so a
    round blob remains visually round in the normal map preview.  This only
    changes the shape metric; connectivity, no-gap topology and target cell
    counts remain unchanged.
    """

    h, w = region.shape
    available = region & ~occupied
    candidates = np.argwhere(available)
    if len(candidates) == 0:
        return None
    for _ in range(180):
        y0, x0 = map(int, candidates[pr.randrange(len(candidates))])
        radius = math.sqrt(target / (math.pi * aspect))
        major = radius * aspect
        ca, sa = math.cos(angle), math.sin(angle)

        def priority(x: int, y: int) -> float:
            dx, dy = x - x0, y - y0
            if shape_space == "parallelogram_compensated":
                # Keep this transform in sync with preview._project_point:
                # X = 2*x - y + constant, Y = 2*y.
                metric_x, metric_y = 2 * dx - dy, 2 * dy
            else:
                metric_x, metric_y = dx, dy
            u = ca * metric_x + sa * metric_y
            v = -sa * metric_x + ca * metric_y
            return (u / (major + 1e-6)) ** 2 + (v / (radius + 1e-6)) ** 2 + 0.045 * math.sin(.52 * u + .29 * v)

        heap: list[tuple[float, int, int]] = [(0.0, x0, y0)]
        seen = {(x0, y0)}
        chosen: list[tuple[int, int]] = []
        while heap and len(chosen) < target:
            _, x, y = heapq.heappop(heap)
            if not available[y, x]:
                continue
            chosen.append((x, y))
            for dx, dy in HEX6:
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen or not (0 <= nx < w and 0 <= ny < h):
                    continue
                seen.add((nx, ny))
                if available[ny, nx]:
                    heapq.heappush(heap, (priority(nx, ny), nx, ny))
        if len(chosen) < target:
            continue
        xs = [x for x, _ in chosen]
        ys = [y for _, y in chosen]
        sub = np.zeros((max(ys) - min(ys) + 1, max(xs) - min(xs) + 1), bool)
        for x, y in chosen:
            sub[y - min(ys), x - min(xs)] = True
        if (ndimage.binary_fill_holes(sub, structure=_HEX_STRUCTURE) & ~sub).any():
            continue
        if target / sub.size < 0.32:
            continue
        return chosen
    return None


def _hex_points(side: int, cx: int, cy: int, radius: int, *, exact: int | None = None) -> list[tuple[int, int]]:
    """Return bounded points in one canonical hex-distance disc."""

    points: list[tuple[int, int]] = []
    radius = max(0, int(radius))
    for y in range(max(0, cy - radius), min(side, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(side, cx + radius + 1)):
            distance = hex_distance(cx, cy, x, y)
            if distance <= radius and (exact is None or distance == int(exact)):
                points.append((x, y))
    return points


def _allocate_quantities(
    count: int,
    total: int,
    rng: np.random.Generator,
    *,
    minimum: int = 1,
    maximum: int = 12,
    weighted_fullness: bool = True,
    ensure_all_values: bool = False,
) -> np.ndarray:
    """Allocate exact building-stone units while retaining varied IDs."""

    count = int(count)
    total = int(total)
    minimum = int(minimum)
    maximum = int(maximum)
    if count <= 0:
        return np.zeros(0, dtype=np.int16)
    if minimum > maximum:
        raise ValueError("minimum quantity must not exceed maximum quantity")
    total = max(count * minimum, min(count * maximum, total))
    values = np.arange(minimum, maximum + 1, dtype=np.int16)
    if weighted_fullness:
        weights = (values.astype(float) - float(minimum) + 1.0) ** 2
    else:
        weights = np.ones(len(values), dtype=float)
    weights /= weights.sum()
    quantities = rng.choice(values, size=count, replace=True, p=weights).astype(np.int16)
    if ensure_all_values and count >= len(values):
        quantities[: len(values)] = values

    difference = total - int(quantities.sum())
    while difference:
        if difference > 0:
            eligible = np.flatnonzero(quantities < maximum)
            if not len(eligible):
                break
            quantities[int(rng.choice(eligible))] += 1
            difference -= 1
        else:
            eligible = np.flatnonzero(quantities > minimum)
            if not len(eligible):
                break
            quantities[int(rng.choice(eligible))] -= 1
            difference += 1
    return quantities


class UpgradedContent:
    """Global Upgraded content, with starts intentionally kept provisional."""

    def __init__(self, profile: dict, progress=None):
        self.profile = profile
        self.progress = progress
        self.side = 0
        self.reference_side = max(1, int(profile.get("side", 768)))
        self._stage_log: list[str] = []

    def log(self, stage: str, detail: str = "") -> None:
        self._stage_log.append(stage + (f" — {detail}" if detail else ""))
        if self.progress is not None:
            self.progress(stage, detail)

    def _scaled_target(self, value: int) -> int:
        """Scale a 768-calibrated quota by map area, without changing 768."""
        ratio = float(self.side) / float(self.reference_side)
        return max(0, int(round(int(value) * ratio * ratio)))

    def _core_mask(self, state, radius: int) -> np.ndarray:
        mask = np.zeros((state.side, state.side), dtype=bool)
        for sx, sy in state.starts:
            for y in range(max(0, sy - radius), min(state.side, sy + radius + 1)):
                for x in range(max(0, sx - radius), min(state.side, sx + radius + 1)):
                    if hex_distance(sx, sy, x, y) <= radius:
                        mask[y, x] = True
        return mask

    def _object_clear(self, state, x: int, y: int, radius: int = 2) -> bool:
        for yy in range(max(0, y - radius), min(self.side, y + radius + 1)):
            for xx in range(max(0, x - radius), min(self.side, x + radius + 1)):
                if state.objects[yy, xx] and hex_distance(x, y, xx, yy) < radius:
                    return False
        return True

    def _content_core(self, state) -> np.ndarray:
        """Return the global object-clearing zone around each start."""

        starts_cfg = self.profile["starts"]
        return self._core_mask(
            state,
            max(
                int(starts_cfg["technical_clear_hex"]),
                int(starts_cfg.get("editor_object_clear_hex", 14)),
            ),
        )

    def _rebuild_swamp_transitions(self, state) -> None:
        """Rebuild the three legal swamp depth IDs after painting bonuses."""

        terrain = state.terrain
        swamp = np.isin(terrain, SWAMP_IDS)
        if not swamp.any():
            return
        # A swamp cell is on the outside rim when one of its six neighbours is
        # non-swamp (or outside the map).  The exact HEX6 breadth-first depth
        # avoids mixing the grass-to-swamp and swamp-to-swamp transition IDs.
        depth = np.zeros(terrain.shape, dtype=np.int16)
        frontier = swamp & (neighbor_count(swamp) < 6)
        queue = deque()
        for y, x in np.argwhere(frontier):
            yy, xx = int(y), int(x)
            depth[yy, xx] = 1
            queue.append((xx, yy))
        while queue:
            x, y = queue.popleft()
            next_depth = int(depth[y, x]) + 1
            for dx, dy in HEX6:
                xx, yy = x + dx, y + dy
                if not (0 <= xx < self.side and 0 <= yy < self.side):
                    continue
                if swamp[yy, xx] and depth[yy, xx] == 0:
                    depth[yy, xx] = next_depth
                    queue.append((xx, yy))
        terrain[swamp & (depth == 1)] = GRASS_SWAMP_TRANS
        terrain[swamp & (depth == 2)] = SWAMP_TRANS
        terrain[swamp & (depth >= 3)] = SWAMP

    def _place_start_mini_swamps(self, state, pr: random.Random) -> None:
        """Paint one coherent, legacy-shaped mini-swamp per start.

        The coordinates are deliberately not recalculated here.  The starts
        bridge has already supplied them, and this pass only searches for a
        legal nearby patch.  On cramped editor sizes the patch is allowed to
        shrink rather than making the whole generation unavailable.
        """

        terrain = state.terrain
        starts_cfg = self.profile["starts"]
        bonus_cfg = self.profile.get("start_bonus", {}).get("mini_swamp", {})
        technical = self._core_mask(state, int(starts_cfg["technical_clear_hex"]))
        requested_cells = int(bonus_cfg.get("requested_cells", 19))
        outer_cells = int(bonus_cfg.get("outer_cells", 4))
        center_radius = int(bonus_cfg.get("center_hex", starts_cfg.get("initial_territory_hex_radius", 34)))
        placed_by_start: list[int] = []
        shortfalls: list[int] = []

        def clean_halo(points: list[tuple[int, int]]) -> bool:
            point_set = set(points)
            for x, y in points:
                for dx, dy in HEX6:
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < self.side and 0 <= yy < self.side):
                        continue
                    if (xx, yy) not in point_set and terrain[yy, xx] != GRASS:
                        return False
            return True

        def valid_base(cx: int, cy: int) -> list[tuple[int, int]]:
            points = _hex_points(self.side, cx, cy, 2)
            if len(points) != requested_cells:
                return []
            if any(technical[y, x] or terrain[y, x] != GRASS for x, y in points):
                return []
            return points

        def fallback_patch(sx: int, sy: int) -> list[tuple[int, int]]:
            available = np.argwhere((terrain == GRASS) & ~technical)
            if not len(available):
                return []
            candidates = [(int(x), int(y)) for y, x in available]
            candidates.sort(key=lambda point: abs(hex_distance(sx, sy, point[0], point[1]) - center_radius))
            pr.shuffle(candidates[: min(len(candidates), 512)])
            for seed_x, seed_y in candidates:
                if terrain[seed_y, seed_x] != GRASS or technical[seed_y, seed_x]:
                    continue
                patch: list[tuple[int, int]] = []
                frontier = [(seed_x, seed_y)]
                seen = {(seed_x, seed_y)}
                while frontier and len(patch) < requested_cells:
                    index = pr.randrange(len(frontier))
                    x, y = frontier.pop(index)
                    if terrain[y, x] != GRASS or technical[y, x]:
                        continue
                    patch.append((x, y))
                    neighbours = list(HEX6)
                    pr.shuffle(neighbours)
                    for dx, dy in neighbours:
                        xx, yy = x + dx, y + dy
                        if (
                            0 <= xx < self.side
                            and 0 <= yy < self.side
                            and (xx, yy) not in seen
                            and terrain[yy, xx] == GRASS
                            and not technical[yy, xx]
                        ):
                            seen.add((xx, yy))
                            frontier.append((xx, yy))
                if len(patch) >= max(1, min(requested_cells, 7)):
                    return patch
            return []

        for sx, sy in state.starts:
            sx, sy = int(sx), int(sy)
            centers: list[tuple[int, int]] = []
            for radius in range(max(1, center_radius - 2), center_radius + 3):
                centers.extend(
                    (x, y)
                    for x, y in _hex_points(self.side, sx, sy, radius, exact=radius)
                    if terrain[y, x] == GRASS and not technical[y, x]
                )
            pr.shuffle(centers)
            patch: list[tuple[int, int]] = []
            for cx, cy in centers:
                base = valid_base(cx, cy)
                if not base:
                    continue
                outer = [
                    (x, y)
                    for x, y in _hex_points(self.side, cx, cy, 3, exact=3)
                    if terrain[y, x] == GRASS and not technical[y, x]
                ]
                pr.shuffle(outer)
                with_outer = base + outer[:outer_cells]
                if clean_halo(with_outer):
                    patch = with_outer
                    break
                if clean_halo(base):
                    patch = base
                    break
            if not patch:
                patch = fallback_patch(sx, sy)
            for x, y in patch:
                terrain[y, x] = GRASS_SWAMP_TRANS
            placed_by_start.append(len(patch))
            if len(patch) < requested_cells:
                shortfalls.append(requested_cells - len(patch))

        self._rebuild_swamp_transitions(state)
        metadata = {
            "per_player": True,
            "requested_cells_per_start": requested_cells,
            "outer_cells_max": outer_cells,
            "center_hex": center_radius,
            "placed_cells_per_start": placed_by_start,
            "placed_cells": int(sum(placed_by_start)),
            "starts_with_bonus": sum(value > 0 for value in placed_by_start),
            "shortfalls": shortfalls,
            "outside_technical_zone": True,
        }
        state.metadata["upgraded_start_mini_swamps"] = metadata
        self.log("biomes.upgraded_start_mini_swamps", str(metadata))

    def generate(self, state, rng: np.random.Generator, pr: random.Random) -> dict[str, object]:
        self.side = state.side
        self._stage_log.clear()
        self._place_start_mini_swamps(state, pr)
        self._generate_minerals(state, rng, pr)
        self._generate_fish(state, rng)
        self._place_trees(state, rng, pr)
        self._place_decorations(state, rng, pr)
        self._place_building_stones(state, rng, pr)
        self._final_accessibility(state)
        state.metadata["upgraded_content_stages"] = list(self._stage_log)
        state.metadata["upgraded_start_content_deferred"] = False
        return {
            "minerals": state.metadata.get("upgraded_minerals", {}),
            "fish": state.metadata.get("upgraded_fish", {}),
            "trees": state.metadata.get("upgraded_trees", {}),
            "stones": state.metadata.get("upgraded_stones", {}),
            "decorations": state.metadata.get("upgraded_decorations", {}),
        }

    def _generate_minerals(self, state, rng: np.random.Generator, pr: random.Random) -> None:
        terrain, resources = state.terrain, state.resources
        cfg = self.profile["minerals"]
        resources[:] = 0
        support = np.isin(terrain, [32, 34, 35, SNOW_TRANS, SNOW])
        support_count = int(support.sum())
        target_total = int(round(support_count * float(cfg.get("rocky_accessible_occupancy_target", .90))))
        families = {int(k): v for k, v in cfg["families"].items()}
        shares = {int(k): float(v) for k, v in cfg.get("shares", {}).items()}
        aspect_min = max(1.0, float(cfg.get("blob_aspect_min", 1.0)))
        aspect_max = max(aspect_min, float(cfg.get("blob_aspect_max", aspect_min)))
        shape_space = str(cfg.get("shape_space", "grid"))
        if not shares:
            original = sum(int(v["cells"]) for v in families.values())
            shares = {key: int(value["cells"]) / original for key, value in families.items()}
        norm = sum(shares.values())
        order = list(families)
        targets: dict[int, int] = {}
        used = 0
        for family in order[:-1]:
            targets[family] = int(round(target_total * shares[family] / norm))
            used += targets[family]
        targets[order[-1]] = target_total - used

        occupied = np.zeros_like(support, bool)
        blob_counts: dict[int, int] = {}
        fallback_families: list[int] = []
        for family in order:
            fcfg = families[family]
            requested = max(1, round(targets[family] * int(fcfg["blobs"]) / max(1, int(fcfg["cells"]))))
            sizes = _make_blob_sizes(
                targets[family], requested, rng, pr,
                int(cfg.get("blob_size_min", 18)), int(cfg.get("blob_size_max", 105)),
            )
            placed = 0
            for size in sizes:
                cells = None
                for _ in range(48):
                    aspect = aspect_min + pr.random() * (aspect_max - aspect_min)
                    cells = _grow_ovoid_no_gap(
                        support,
                        occupied,
                        size,
                        aspect,
                        pr.random() * math.pi,
                        pr,
                        shape_space=shape_space,
                    )
                    if cells is not None:
                        break
                if cells is None:
                    if self.side == self.reference_side:
                        raise RuntimeError(f"Upgraded mineral placement failed for family {family:#x}")
                    # The copied no-gap morphology remains the calibrated
                    # 768×768 path.  Other editor sizes must still generate
                    # even when their fragmented support cannot accommodate
                    # the calibrated blob geometry; use deterministic
                    # individual support cells and expose the fallback in
                    # metadata rather than aborting the map.
                    available = np.argwhere(support & ~occupied)
                    if not len(available):
                        continue
                    fallback_families.append(int(family))
                    count = min(int(size), len(available))
                    chosen = available[rng.choice(len(available), count, replace=False)]
                    cells = [(int(x), int(y)) for y, x in chosen]
                q0 = rng.integers(1, 16, len(cells), dtype=np.uint8)
                q = np.minimum(int(cfg["quantity_cap"]), np.floor(q0.astype(float) * float(cfg["quantity_multiplier"]) + .5)).astype(np.uint8)
                for (x, y), quantity in zip(cells, q):
                    resources[y, x] = family | int(quantity)
                    occupied[y, x] = True
                placed += len(cells)
            if placed != targets[family] and self.side == self.reference_side:
                raise RuntimeError(f"Upgraded mineral target mismatch {family:#x}: {placed}/{targets[family]}")
            if placed != targets[family]:
                targets[family] = placed
            blob_counts[family] = len(sizes)

        target_total = sum(targets.values())
        metadata = {
            "model": "upgraded_v7_nogap",
            "shape_variant": str(cfg.get("shape_variant", "round_parallelogram_compensated_test")),
            "shape_aspect_range": [aspect_min, aspect_max],
            "shape_space": shape_space,
            "support_cells": support_count,
            "target_total": target_total,
            "targets": {f"{key:02x}": value for key, value in targets.items()},
            "blob_counts": {f"{key:02x}": value for key, value in blob_counts.items()},
            "non_reference_fallback_families": [f"{family:02x}" for family in sorted(set(fallback_families))],
        }
        state.metadata["upgraded_minerals"] = metadata
        state.metadata["upgraded_mineral_targets"] = metadata["targets"]
        self.log("resources.upgraded_minerals_v7", f"cells={target_total} support={support_count}")

    def _water_shore_distance(self, state) -> np.ndarray:
        terrain = state.terrain
        water = np.isin(terrain, WATER_IDS)
        shore = terrain == 48
        seed = water & (neighbor_count(shore) > 0)
        distance = np.full(terrain.shape, 32767, dtype=np.int16)
        queue = deque()
        for y, x in np.argwhere(seed):
            distance[y, x] = 1
            queue.append((int(x), int(y)))
        while queue:
            x, y = queue.popleft()
            next_distance = int(distance[y, x]) + 1
            if next_distance > 12:
                continue
            for dx, dy in HEX6:
                xx, yy = x + dx, y + dy
                if 0 <= xx < self.side and 0 <= yy < self.side and water[yy, xx] and next_distance < distance[yy, xx]:
                    distance[yy, xx] = next_distance
                    queue.append((xx, yy))
        return distance

    def _generate_fish(self, state, rng: np.random.Generator) -> None:
        terrain, resources = state.terrain, state.resources
        cfg = self.profile["fish"]
        water = np.isin(terrain, WATER_IDS)
        river = np.isin(terrain, RIVER_IDS)
        resources[water] = 0
        resources[river] = 0
        distance = self._water_shore_distance(state)
        selected = np.zeros_like(water)
        for low, high, fraction in cfg["bands"]:
            candidates = np.argwhere(water & (distance >= low) & (distance <= high))
            count = min(len(candidates), round(len(candidates) * fraction))
            if count:
                points = candidates[rng.choice(len(candidates), count, replace=False)]
                selected[points[:, 0], points[:, 1]] = True
        border = np.zeros_like(water)
        border[[0, -1], :] = True
        border[:, [0, -1]] = True
        eligible = water & (distance >= 1) & (distance <= int(cfg["max_shore_hex_distance"])) & ~border
        selected &= ~border
        profile_target = int(cfg["target_cells"])
        target = min(self._scaled_target(profile_target), int(eligible.sum()))
        current = int(selected.sum())
        if current < target:
            candidates = np.argwhere(eligible & ~selected)
            if len(candidates) < target - current:
                raise RuntimeError(f"Upgraded fish target impossible: {len(candidates)} available")
            points = candidates[rng.choice(len(candidates), target - current, replace=False)]
            selected[points[:, 0], points[:, 1]] = True
        elif current > target:
            points = np.argwhere(selected)
            points = points[rng.choice(len(points), current - target, replace=False)]
            selected[points[:, 0], points[:, 1]] = False
        q0 = rng.integers(1, 16, target, dtype=np.uint8)
        quantities = np.minimum(int(cfg["quantity_cap"]), np.floor(q0.astype(float) * float(cfg["quantity_multiplier"]) + .5)).astype(np.uint8)
        resources[selected] = quantities
        metadata = {
            "model": "upgraded_shore_bands",
            "cells": int(selected.sum()),
            "target": target,
            "profile_target_768": profile_target,
            "max_distance": int(cfg["max_shore_hex_distance"]),
        }
        state.metadata["upgraded_fish"] = metadata
        state.metadata["upgraded_fish_target"] = target
        self.log("resources.upgraded_fish", f"cells={metadata['cells']}")

    def _place_decorations(self, state, rng: np.random.Generator, pr: random.Random) -> None:
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        cfg = self.profile["decor"]
        core = self._content_core(state)
        native_cfg = cfg.get("legacy_static_families", {})
        density_split = int(cfg.get("legacy_static_density_split_players", 8))
        density_key = "low" if int(state.metadata.get("players", 0)) <= density_split else "high"
        scale = (float(self.side) / float(self.reference_side)) ** 2
        occupied = (objects != 0) | core
        counts: dict[str, int] = {}
        requested_targets: dict[str, int] = {}
        effective_targets: dict[str, int] = {}

        # The Legacy native pass has one independent quota per static family.
        # Keeping the table in the Upgraded profile avoids importing Legacy at
        # runtime while preserving its IDs, supports and density split.
        for name, family_cfg in native_cfg.items():
            targets_by_density = family_cfg.get("target_768_by_density", {})
            requested = int(round(float(targets_by_density.get(density_key, 0)) * scale))
            ids = tuple(int(value) for value in family_cfg.get("ids", ()))
            support_ids = tuple(int(value) for value in family_cfg.get("support_ids", ()))
            candidates = np.argwhere(np.isin(terrain, support_ids) & ~occupied)
            placed = 0
            if requested and len(candidates) and ids:
                id_array = np.asarray(ids, dtype=np.uint8)
                for index in rng.permutation(len(candidates)):
                    if placed >= requested:
                        break
                    y, x = map(int, candidates[index])
                    if occupied[y, x]:
                        continue
                    objects[y, x] = int(rng.choice(id_array))
                    occupied[y, x] = True
                    access[y, x] = 1
                    placed += 1
            counts[str(name)] = placed
            requested_targets[str(name)] = requested
            # Other editor sizes keep generating even if a copied native quota
            # cannot physically fit.  The effective target is what validators
            # use for that map; the requested target remains visible in stats.
            effective_targets[str(name)] = placed

        water = np.isin(terrain, WATER_IDS)
        deep = np.argwhere((terrain == 7) & (neighbor_count(~water) == 0) & (objects == 0))
        reef_target = min(self._scaled_target(cfg.get("reef_target", 0)), len(deep))
        reef_count = 0
        reef_ids = np.asarray(REEF_IDS, dtype=np.uint8)
        if reef_target and len(deep):
            for index in rng.permutation(len(deep)):
                if reef_count >= reef_target:
                    break
                y, x = map(int, deep[index])
                if objects[y, x]:
                    continue
                objects[y, x] = int(rng.choice(reef_ids))
                access[y, x] = 1
                reef_count += 1
        counts["reefs"] = reef_count
        requested_targets["reefs"] = reef_target
        effective_targets["reefs"] = reef_count
        metadata = {
            "model": "legacy_native_static_families_plus_upgraded_reefs",
            "density_profile": density_key,
            "legacy_static": counts,
            "legacy_static_targets": requested_targets,
            "legacy_static_effective_targets": effective_targets,
            "legacy_static_shortfalls": {
                name: max(0, requested_targets[name] - counts[name])
                for name in requested_targets
            },
            "decorative_objects": int(sum(counts.values())),
            "reefs": reef_count,
            "reef_target": reef_target,
        }
        state.metadata["upgraded_decorations"] = metadata
        self.log("objects.upgraded_decorations", str(metadata))

    def _place_trees(self, state, rng: np.random.Generator, pr: random.Random) -> None:
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        cfg = self.profile["trees"]
        core = self._content_core(state)
        technical = self._core_mask(state, int(self.profile["starts"]["technical_clear_hex"]))
        profile_target = int(cfg["adult_global_target"])
        target = self._scaled_target(profile_target)
        ids = np.asarray(cfg["adult_ids"], dtype=np.uint8)
        weights = np.asarray(cfg.get("adult_weights", np.ones(len(ids))), dtype=float)
        weights /= weights.sum()
        grass = (terrain == GRASS) & ~core
        adult_forest_clearance = max(0, int(cfg.get("adult_forest_min_hex_distance", 2)))

        def place(
            mask: np.ndarray,
            count: int,
            object_ids,
            probabilities=None,
            support: np.ndarray | None = None,
            clearance: int = 2,
        ) -> int:
            allowed = mask & (terrain == GRASS if support is None else support)
            points = np.argwhere(allowed & (objects == 0))
            placed = 0
            if not count or not len(points):
                return 0
            id_array = np.asarray(tuple(object_ids), dtype=np.uint8)
            for index in rng.permutation(len(points)):
                if placed >= count:
                    break
                y, x = map(int, points[index])
                if objects[y, x] or (clearance and not self._object_clear(state, x, y, clearance)):
                    continue
                objects[y, x] = int(rng.choice(id_array, p=probabilities)) if probabilities is not None else int(rng.choice(id_array))
                access[y, x] = 1
                placed += 1
            return placed

        def start_center(sx: int, sy: int) -> tuple[int, int] | None:
            desired = int(cfg.get("start_cluster_center_hex", 34))
            centers: list[tuple[int, int]] = []
            for radius in range(max(1, desired - 2), desired + 3):
                centers.extend(
                    (x, y)
                    for x, y in _hex_points(self.side, sx, sy, radius, exact=radius)
                    if terrain[y, x] == GRASS and not technical[y, x] and not objects[y, x]
                )
            if not centers:
                points = np.argwhere(grass & ~technical & (objects == 0))
                if not len(points):
                    return None
                centers = [(int(x), int(y)) for y, x in points]
                centers.sort(key=lambda point: abs(hex_distance(sx, sy, point[0], point[1]) - desired))
                centers = centers[: min(512, len(centers))]
            return pr.choice(centers)

        start_forest_records: list[dict[str, int]] = []
        start_adults = 0
        start_small = 0
        start_adult_target = int(cfg.get("adult_start_bonus_per_player", 0))
        start_small_target = int(cfg.get("small_tree_start_bonus_per_player", 0))
        start_forest_mask = np.zeros_like(grass)
        for player, (sx, sy) in enumerate(state.starts, start=1):
            center = start_center(int(sx), int(sy))
            if center is None:
                start_forest_records.append({"player": player, "adult": 0, "small": 0})
                continue
            cx, cy = center
            radius_min = int(cfg.get("start_cluster_radius_min", 5))
            radius_max = int(cfg.get("start_cluster_radius_max", 12))
            radius = pr.randint(min(radius_min, radius_max), max(radius_min, radius_max))
            effective_radius = radius
            forest = np.zeros_like(grass)
            for x, y in _hex_points(self.side, cx, cy, radius):
                if not technical[y, x] and terrain[y, x] == GRASS:
                    forest[y, x] = True
            adult_count = place(
                forest,
                start_adult_target,
                ids,
                weights,
                clearance=adult_forest_clearance,
            )
            # A cramped edge can leave a short first disc.  Expanding the same
            # forest patch keeps the bonus semantic while avoiding a size lock.
            if adult_count < start_adult_target:
                # Keep the bonus count stable when the stricter adult-tree
                # spacing meets a fragmented biome: grow the same forest
                # envelope in bounded rings instead of relaxing the spacing or
                # silently dropping start trees.
                for extra_radius in (4, 8, 12, 16):
                    if adult_count >= start_adult_target:
                        break
                    expanded = np.zeros_like(forest)
                    for x, y in _hex_points(self.side, cx, cy, radius + extra_radius):
                        if not technical[y, x] and terrain[y, x] == GRASS:
                            expanded[y, x] = True
                    forest |= expanded
                    effective_radius = radius + extra_radius
                    adult_count += place(
                        forest,
                        start_adult_target - adult_count,
                        ids,
                        weights,
                        clearance=adult_forest_clearance,
                    )
            small_count = place(
                forest,
                start_small_target,
                (int(cfg.get("small_tree_id", 84)),),
                clearance=0,
            )
            if small_count < start_small_target:
                small_count += place(
                    forest,
                    start_small_target - small_count,
                    (int(cfg.get("small_tree_id", 84)),),
                    clearance=0,
                )
            start_forest_mask |= forest
            start_adults += adult_count
            start_small += small_count
            start_forest_records.append(
                {
                    "player": player,
                    "center_x": int(cx),
                    "center_y": int(cy),
                    "radius": int(radius),
                    "effective_radius": int(effective_radius),
                    "adult": int(adult_count),
                    "small": int(small_count),
                }
            )

        # Build a set of explicit global forest regions.  Adults use a smaller
        # cluster region for the 30% quota; saplings can use the whole forest
        # region, so ID84 never falls back to a random grass scatter.
        global_forest = np.zeros_like(grass)
        adult_cluster_region = np.zeros_like(grass)
        small_cluster_region = np.zeros_like(grass)
        centers: list[tuple[int, int, int]] = []
        global_grass = grass & ~start_forest_mask
        points = np.argwhere(global_grass & (objects == 0))
        center_count = min(int(cfg.get("forest_centers", 38)), len(points))
        if center_count:
            for index in rng.choice(len(points), center_count, replace=False):
                y, x = map(int, points[index])
                radius_min = int(cfg.get("forest_radius_min", 7))
                radius_max = int(cfg.get("forest_radius_max", 12))
                radius = int(rng.integers(min(radius_min, radius_max), max(radius_min, radius_max) + 1))
                centers.append((x, y, radius))
                for fx, fy in _hex_points(self.side, x, y, radius):
                    if global_grass[fy, fx] and not core[fy, fx]:
                        global_forest[fy, fx] = True
                    if global_grass[fy, fx] and not core[fy, fx] and hex_distance(x, y, fx, fy) <= max(4, radius - 2):
                        adult_cluster_region[fy, fx] = True
                        small_cluster_region[fy, fx] = True

        clustered_target = min(target, round(target * float(cfg.get("adult_cluster_share", 0.30))))
        global_cluster_adults = place(
            adult_cluster_region,
            clustered_target,
            ids,
            weights,
            clearance=adult_forest_clearance,
        )
        # If a fragmented map made the inner regions too sparse, use the outer
        # part of those same forests before relaxing the quota.
        if global_cluster_adults < clustered_target:
            global_cluster_adults += place(
                global_forest,
                clustered_target - global_cluster_adults,
                ids,
                weights,
                clearance=adult_forest_clearance,
            )
        scatter_mask = global_grass & ~global_forest
        global_adults = global_cluster_adults + place(scatter_mask, max(0, target - global_cluster_adults), ids, weights)
        if global_adults < target:
            global_adults += place(global_grass, target - global_adults, ids, weights)

        small_id = int(cfg.get("small_tree_id", 84))
        small_profile_target = int(cfg.get("small_tree_target", 0))
        small_target = self._scaled_target(small_profile_target)
        small_cluster_target = round(small_target * float(cfg.get("small_tree_cluster_share", 0.76)))
        global_small_cluster = place(small_cluster_region, small_cluster_target, (small_id,))
        global_small = global_small_cluster + place(global_forest, max(0, small_target - global_small_cluster), (small_id,))
        if global_small < small_target:
            # This is a last-resort forest expansion, still represented by the
            # recorded forest centres and therefore not a free-world scatter.
            expanded_forest = np.zeros_like(global_forest)
            for cx, cy, _ in centers:
                for x, y in _hex_points(self.side, cx, cy, int(cfg.get("forest_radius_max", 12)) + 4):
                    if terrain[y, x] == GRASS and not core[y, x]:
                        expanded_forest[y, x] = True
            global_forest |= expanded_forest
            global_small += place(global_forest, small_target - global_small, (small_id,))

        desert = np.isin(terrain, DESERT_IDS) & ~core & (objects == 0)
        palm_profile_target = int(cfg.get("palm_target", 0))
        palm_requested = self._scaled_target(palm_profile_target)
        palms = place(desert, palm_requested, cfg.get("palm_ids", (78, 79)), support=desert)
        metadata = {
            "adult_trees": int(start_adults + global_adults),
            "palm_trees": palms,
            "small_trees": int(start_small + global_small),
            "adult_target": int(start_adults + global_adults),
            "small_target": int(start_small + global_small),
            "palm_target": int(palms),
            "palm_requested": palm_requested,
            "adult_global_requested": target,
            "adult_global_placed": int(global_adults),
            "adult_start_bonus_requested": start_adult_target * len(state.starts),
            "adult_start_bonus_placed": int(start_adults),
            "adult_forest_requested": clustered_target,
            "adult_forest_placed": int(global_cluster_adults),
            "adult_forest_min_hex_distance": adult_forest_clearance,
            "global_quota_excludes_start_bonus": True,
            "small_global_requested": small_target,
            "small_global_placed": int(global_small),
            "small_start_bonus_requested": start_small_target * len(state.starts),
            "small_start_bonus_placed": int(start_small),
            "small_forest_only": True,
            "small_forest_requested": small_target,
            "small_forest_placed": int(global_small),
            "small_forest_cluster_requested": small_cluster_target,
            "small_forest_cluster_placed": int(global_small_cluster),
            "start_forests": start_forest_records,
            "global_forests": [
                {"center_x": int(x), "center_y": int(y), "radius": int(radius)}
                for x, y, radius in centers
            ],
            "profile_targets_768": {
                "adult": profile_target,
                "small": small_profile_target,
                "palm": palm_profile_target,
            },
        }
        state.metadata["upgraded_trees"] = metadata
        state.metadata["upgraded_tree_targets"] = {
            "adult": int(start_adults + global_adults),
            "small": int(start_small + global_small),
            "palm": int(palms),
        }
        self.log("objects.upgraded_trees", str(metadata))

    def _place_building_stones(self, state, rng: np.random.Generator, pr: random.Random) -> None:
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        cfg = self.profile["building_stones"]
        core = self._content_core(state)
        technical = self._core_mask(state, int(self.profile["starts"]["technical_clear_hex"]))
        footprint = [tuple(item) for item in cfg["footprint"]]
        blocked = core.copy()
        covered = np.zeros_like(core)
        records: list[dict[str, object]] = []

        def mark(x, y):
            for yy in range(max(0, y - 3), min(self.side, y + 4)):
                for xx in range(max(0, x - 3), min(self.side, x + 4)):
                    if hex_distance(x, y, xx, yy) < int(cfg["anchor_min_hex_distance"]):
                        blocked[yy, xx] = True

        def valid(x, y, forbidden):
            if blocked[y, x]:
                return False
            for dx, dy in footprint:
                xx, yy = x + dx, y + dy
                if not (1 <= xx < self.side - 1 and 1 <= yy < self.side - 1):
                    return False
                if forbidden[yy, xx] or terrain[yy, xx] != GRASS or objects[yy, xx] or covered[yy, xx]:
                    return False
            return True

        def place(mask: np.ndarray, count: int, forbidden: np.ndarray, tag: str, player: int | None = None) -> int:
            candidates = np.argwhere(mask & (terrain == GRASS) & ~forbidden & (objects == 0))
            placed = 0
            for index in rng.permutation(len(candidates)):
                if placed >= count:
                    break
                y, x = map(int, candidates[index])
                if not valid(x, y, forbidden):
                    continue
                records.append({"x": x, "y": y, "tag": tag, "player": player})
                placed += 1
                # Reserve the complete seven-cell footprint immediately.  The
                # anchor ID is written only after unit allocation, so this
                # reservation cannot bias quantity assignment.
                for dx, dy in footprint:
                    covered[y + dy, x + dx] = True
                mark(x, y)
            return placed

        def start_center(sx: int, sy: int) -> tuple[int, int] | None:
            desired = int(cfg.get("start_cluster_center_hex", 34))
            centers: list[tuple[int, int]] = []
            for radius in range(max(1, desired - 2), desired + 3):
                centers.extend(
                    (x, y)
                    for x, y in _hex_points(self.side, sx, sy, radius, exact=radius)
                    if terrain[y, x] == GRASS and not technical[y, x] and not objects[y, x]
                )
            if not centers:
                points = np.argwhere((terrain == GRASS) & ~technical & (objects == 0))
                if not len(points):
                    return None
                centers = [(int(x), int(y)) for y, x in points]
                centers.sort(key=lambda point: abs(hex_distance(sx, sy, point[0], point[1]) - desired))
                centers = centers[: min(512, len(centers))]
            return pr.choice(centers)

        start_cfg = self.profile.get("start_bonus", {}).get("building_stones", {})
        start_anchor_target = int(start_cfg.get("anchors_per_player", max(1, math.ceil(int(start_cfg.get("stock_units_per_player", 0)) / 12))))
        start_stock_per_player = int(start_cfg.get("stock_units_per_player", 0))
        start_min = int(start_cfg.get("quantity_min", 1))
        start_max = int(start_cfg.get("quantity_max", 12))
        start_records_by_player: dict[int, list[dict[str, object]]] = {}
        start_centers: list[dict[str, int]] = []
        for player, (sx, sy) in enumerate(state.starts, start=1):
            center = start_center(int(sx), int(sy))
            if center is None:
                start_records_by_player[player] = []
                continue
            cx, cy = center
            radius_min = int(cfg.get("start_cluster_radius_min", 4))
            radius_max = int(cfg.get("start_cluster_radius_max", 10))
            radius = pr.randint(min(radius_min, radius_max), max(radius_min, radius_max))
            region = np.zeros_like(core)
            for x, y in _hex_points(self.side, cx, cy, radius):
                if terrain[y, x] == GRASS and not technical[y, x]:
                    region[y, x] = True
            before = len(records)
            placed = place(region, start_anchor_target, technical, "start_bonus", player)
            if placed < start_anchor_target:
                expanded = np.zeros_like(region)
                for x, y in _hex_points(self.side, cx, cy, radius + 5):
                    if terrain[y, x] == GRASS and not technical[y, x]:
                        expanded[y, x] = True
                placed += place(expanded, start_anchor_target - placed, technical, "start_bonus", player)
            if placed < start_anchor_target:
                placed += place((terrain == GRASS), start_anchor_target - placed, technical, "start_bonus", player)
            start_records_by_player[player] = records[before:]
            start_centers.append(
                {
                    "player": player,
                    "center_x": int(cx),
                    "center_y": int(cy),
                    "radius": int(radius),
                    "anchors": int(placed),
                }
            )

        requested_target = self._scaled_target(cfg["global_anchor_target"])
        global_target = requested_target
        cluster_target = round(global_target * float(cfg.get("cluster_share", 0.30)))
        global_cluster_region = np.zeros_like(core)
        candidates = np.argwhere((terrain == GRASS) & ~core & (objects == 0))
        center_count = min(int(cfg.get("cluster_centers", 60)), len(candidates))
        if center_count:
            for index in rng.choice(len(candidates), center_count, replace=False):
                y, x = map(int, candidates[index])
                radius = int(rng.integers(4, 13))
                for fx, fy in _hex_points(self.side, x, y, radius):
                    if terrain[fy, fx] == GRASS and not core[fy, fx]:
                        global_cluster_region[fy, fx] = True
        global_cluster_placed = place(global_cluster_region, cluster_target, core, "global_cluster")
        if global_cluster_placed < cluster_target:
            global_cluster_placed += place(global_cluster_region, cluster_target - global_cluster_placed, core, "global_cluster")
        global_placed = global_cluster_placed
        global_remaining = max(0, global_target - global_placed)
        global_placed += place((terrain == GRASS) & ~global_cluster_region, global_remaining, core, "global")
        if global_placed < global_target:
            global_placed += place((terrain == GRASS), global_target - global_placed, core, "global")

        global_records = [record for record in records if str(record["tag"]).startswith("global")]
        exhausted_requested = int(cfg.get("global_exhausted_anchor_target", 0))
        exhausted_count = min(exhausted_requested, len(global_records))
        exhausted_indices: set[int] = set()
        if exhausted_count:
            exhausted_indices = {
                int(value)
                for value in rng.choice(len(global_records), exhausted_count, replace=False)
            }
        active_global = len(global_records) - exhausted_count
        profile_stock_target = int(cfg["global_stock_target"])
        global_stock_target = self._scaled_target(profile_stock_target)
        global_quantities = _allocate_quantities(
            active_global,
            global_stock_target,
            rng,
            weighted_fullness=bool(cfg.get("global_stock_weighted_fullness", True)),
            ensure_all_values=True,
        )
        active_index = 0
        quantity_by_record: dict[int, int] = {}
        for index, record in enumerate(global_records):
            if index in exhausted_indices:
                quantity_by_record[id(record)] = 0
            else:
                quantity_by_record[id(record)] = int(global_quantities[active_index])
                active_index += 1

        start_stock = 0
        for player_records in start_records_by_player.values():
            quantities = _allocate_quantities(
                len(player_records),
                start_stock_per_player,
                rng,
                minimum=start_min,
                maximum=start_max,
                weighted_fullness=True,
            )
            for record, quantity in zip(player_records, quantities):
                quantity_by_record[id(record)] = int(quantity)
                start_stock += int(quantity)

        for record in records:
            x, y = int(record["x"]), int(record["y"])
            quantity = int(quantity_by_record.get(id(record), 0))
            objects[y, x] = int(cfg["exhausted_id"]) - quantity
            for dx, dy in footprint:
                access[y + dy, x + dx] = 1
        total_stock = int(sum(max(0, quantity_by_record.get(id(record), 0)) for record in records))
        id_counts = {
            str(object_id): int(np.count_nonzero(objects == object_id))
            for object_id in range(int(cfg["active_ids"][0]), int(cfg["exhausted_id"]) + 1)
        }
        metadata = {
            "anchors": len(records),
            "stock": total_stock,
            "anchor_target": len(records),
            "stock_target": total_stock,
            "global_anchors": len(global_records),
            "global_anchor_requested": requested_target,
            "global_stock": int(sum(quantity_by_record.get(id(record), 0) for record in global_records)),
            "global_stock_requested": global_stock_target,
            "global_active_anchors": active_global,
            "global_exhausted_anchors": exhausted_count,
            "start_bonus_anchors": len(records) - len(global_records),
            "start_bonus_anchor_requested": start_anchor_target * len(state.starts),
            "start_bonus_stock": start_stock,
            "start_bonus_stock_requested": start_stock_per_player * len(state.starts),
            "global_quota_excludes_start_bonus": True,
            "start_bonus_per_player": [
                {
                    "player": player,
                    "anchors": len(player_records),
                    "stock": int(sum(quantity_by_record.get(id(record), 0) for record in player_records)),
                }
                for player, player_records in start_records_by_player.items()
            ],
            "cluster_target": global_cluster_placed,
            "cluster_requested": cluster_target,
            "cluster_placed": global_cluster_placed,
            "cluster_share": float(cfg.get("cluster_share", 0.30)),
            "start_centers": start_centers,
            "id_counts": id_counts,
            "profile_targets_768": {
                "anchors": int(cfg["global_anchor_target"]),
                "stock": profile_stock_target,
            },
            "profile_start_bonus_stock_per_player": start_stock_per_player,
            "start_bonus_deferred": False,
        }
        state.metadata["upgraded_stones"] = metadata
        state.metadata["upgraded_stone_targets"] = {"anchors": len(records), "stock": total_stock}
        state.metadata["building_stone_anchors"] = [
            (int(record["x"]), int(record["y"]), int(quantity_by_record.get(id(record), 0)), str(record["tag"]))
            for record in records
        ]
        state.metadata["building_stone_footprint_cells"] = [
            (int(record["x"]) + dx, int(record["y"]) + dy)
            for record in records
            for dx, dy in footprint
        ]
        self.log("objects.upgraded_building_stones", str(metadata))

    def _final_accessibility(self, state) -> None:
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        water = np.isin(terrain, WATER_IDS)
        access[water] = 1
        access[np.isin(terrain, (SNOW_TRANS, SNOW))] = 1
        access[objects != 0] = 1
        access[objects == 127] = 0
        bad = (objects != 0) & np.isin(terrain, MOUNTAIN_FAMILY_IDS)
        objects[bad] = 0
        access[bad] = 0
        self.log("accessibility.upgraded_finalize")


__all__ = ("UpgradedContent",)
