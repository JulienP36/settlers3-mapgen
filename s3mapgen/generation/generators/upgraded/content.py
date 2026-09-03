"""Upgraded content pass.

This module is intentionally independent from the Legacy generator.  It keeps
the calibrated Upgraded content routines that are meant to be applied on the
copied native terrain pipeline: v7 no-gap mountain minerals, shore fish,
global decorations/trees and building stones.  Start resources and settlers
are deliberately not generated here.
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
    GRASS_IDS,
    HEX6,
    MOUNTAIN_FAMILY_IDS,
    RIVER_IDS,
    SNOW,
    SNOW_TRANS,
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

    def generate(self, state, rng: np.random.Generator, pr: random.Random) -> dict[str, object]:
        self.side = state.side
        self._stage_log.clear()
        self._generate_minerals(state, rng, pr)
        self._generate_fish(state, rng)
        self._place_decorations(state, rng, pr)
        self._place_trees(state, rng, pr)
        self._place_building_stones(state, rng, pr)
        self._final_accessibility(state)
        state.metadata["upgraded_content_stages"] = list(self._stage_log)
        state.metadata["upgraded_start_content_deferred"] = True
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
        core = self._core_mask(state, max(self.profile["starts"]["technical_clear_hex"], self.profile["starts"].get("editor_object_clear_hex", 14)))

        def place(points, target, ids, blocks=False):
            placed = 0
            for index in rng.permutation(len(points)):
                if placed >= target:
                    break
                y, x = map(int, points[index])
                if objects[y, x] or not self._object_clear(state, x, y, 2):
                    continue
                objects[y, x] = int(pr.choice(ids))
                if blocks:
                    access[y, x] = 1
                placed += 1
            return placed

        desert = np.argwhere(np.isin(terrain, DESERT_IDS) & ~core & (objects == 0))
        desert_count = place(desert, min(self._scaled_target(cfg.get("desert_target", 0)), len(desert)), cfg.get("desert_ids", ()), True) if len(desert) else 0
        swamp = np.argwhere(np.isin(terrain, SWAMP_IDS) & ~core & (objects == 0))
        swamp_count = place(swamp, min(self._scaled_target(cfg.get("swamp_target", 0)), len(swamp)), cfg.get("swamp_reed_ids", ()), False) if len(swamp) else 0
        grass = np.argwhere((terrain == GRASS) & ~core & (objects == 0))
        decorative_count = place(grass, min(self._scaled_target(cfg.get("decorative_stone_target", 0)), len(grass)), range(1, 29), True) if len(grass) else 0
        water = np.isin(terrain, WATER_IDS)
        deep = np.argwhere((terrain == 7) & (neighbor_count(~water) == 0) & (objects == 0))
        reef_count = place(deep, min(self._scaled_target(cfg.get("reef_target", 0)), len(deep)), range(111, 115), True) if len(deep) else 0
        metadata = {"desert": desert_count, "swamp_reeds": swamp_count, "decorative_stones": decorative_count, "reefs": reef_count}
        state.metadata["upgraded_decorations"] = metadata
        self.log("objects.upgraded_decorations", str(metadata))

    def _place_trees(self, state, rng: np.random.Generator, pr: random.Random) -> None:
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        cfg = self.profile["trees"]
        core = self._core_mask(state, max(self.profile["starts"]["technical_clear_hex"], self.profile["starts"].get("editor_object_clear_hex", 14)))
        grass = (terrain == GRASS) & ~core & (objects == 0)
        profile_target = int(cfg["adult_global_target"])
        target = min(self._scaled_target(profile_target), int(grass.sum()))
        ids = np.asarray(cfg["adult_ids"], dtype=np.uint8)
        weights = np.asarray(cfg.get("adult_weights", np.ones(len(ids))), dtype=float)
        weights /= weights.sum()
        occupied = objects != 0
        centers = []
        points = np.argwhere(grass)
        if len(points):
            for index in rng.choice(len(points), min(int(cfg.get("forest_centers", 38)), len(points)), replace=False):
                y, x = map(int, points[index])
                centers.append((x, y))
        clustered_target = round(target * float(cfg.get("adult_cluster_share", 0.0)))
        placed = 0
        attempts = 0
        while placed < clustered_target and centers and attempts < max(1, clustered_target) * 80:
            attempts += 1
            cx, cy = centers[int(rng.integers(len(centers)))]
            radius = int(rng.integers(5, 13))
            x = int(np.clip(cx + rng.integers(-radius, radius + 1), 2, self.side - 3))
            y = int(np.clip(cy + rng.integers(-radius, radius + 1), 2, self.side - 3))
            if hex_distance(cx, cy, x, y) <= radius and grass[y, x] and not occupied[y, x] and self._object_clear(state, x, y, 2):
                objects[y, x] = int(rng.choice(ids, p=weights))
                access[y, x] = 1
                occupied[y, x] = True
                placed += 1
        for index in rng.permutation(len(points)):
            if placed >= target:
                break
            y, x = map(int, points[index])
            if not occupied[y, x] and self._object_clear(state, x, y, 2):
                objects[y, x] = int(rng.choice(ids, p=weights))
                access[y, x] = 1
                occupied[y, x] = True
                placed += 1
        desert = np.isin(terrain, DESERT_IDS) & ~core & (objects == 0)
        palm_points = np.argwhere(desert)
        palm_profile_target = int(cfg.get("palm_target", 0))
        palm_target = min(self._scaled_target(palm_profile_target), len(palm_points))
        palms = 0
        for index in rng.permutation(len(palm_points)):
            if palms >= palm_target:
                break
            y, x = map(int, palm_points[index])
            if self._object_clear(state, x, y, 2):
                objects[y, x] = int(pr.choice(cfg.get("palm_ids", (78, 79))))
                access[y, x] = 1
                palms += 1
        small_id = int(cfg.get("small_tree_id", 84))
        small_points = np.argwhere(grass & (objects == 0))
        small_profile_target = int(cfg.get("small_tree_target", 0))
        small_target = min(self._scaled_target(small_profile_target), len(small_points))
        small = 0
        for index in rng.permutation(len(small_points)):
            if small >= small_target:
                break
            y, x = map(int, small_points[index])
            if self._object_clear(state, x, y, 2):
                objects[y, x] = small_id
                access[y, x] = 1
                small += 1
        if placed < target or palms < palm_target or small < small_target:
            raise RuntimeError(f"Upgraded tree quotas not reached: adult={placed}/{target}, palms={palms}/{palm_target}, small={small}/{small_target}")
        metadata = {
            "adult_trees": placed,
            "palm_trees": palms,
            "small_trees": small,
            "adult_target": target,
            "small_target": small_target,
            "palm_target": palm_target,
            "profile_targets_768": {
                "adult": profile_target,
                "small": small_profile_target,
                "palm": palm_profile_target,
            },
        }
        state.metadata["upgraded_trees"] = metadata
        state.metadata["upgraded_tree_targets"] = {
            "adult": target,
            "small": small_target,
            "palm": palm_target,
        }
        self.log("objects.upgraded_trees", str(metadata))

    def _place_building_stones(self, state, rng: np.random.Generator, pr: random.Random) -> None:
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        cfg = self.profile["building_stones"]
        core = self._core_mask(state, max(self.profile["starts"]["technical_clear_hex"], self.profile["starts"].get("editor_object_clear_hex", 14)))
        footprint = [tuple(item) for item in cfg["footprint"]]
        blocked = core.copy()
        covered = np.zeros_like(core)
        anchors: list[tuple[int, int, int]] = []

        def mark(x, y):
            for yy in range(max(0, y - 3), min(self.side, y + 4)):
                for xx in range(max(0, x - 3), min(self.side, x + 4)):
                    if hex_distance(x, y, xx, yy) < int(cfg["anchor_min_hex_distance"]):
                        blocked[yy, xx] = True

        def valid(x, y):
            if blocked[y, x]:
                return False
            for dx, dy in footprint:
                xx, yy = x + dx, y + dy
                if not (1 <= xx < self.side - 1 and 1 <= yy < self.side - 1):
                    return False
                if core[yy, xx] or terrain[yy, xx] != GRASS or objects[yy, xx] or covered[yy, xx]:
                    return False
            return True

        candidates = np.argwhere((terrain == GRASS) & ~core & (objects == 0))
        requested_target = self._scaled_target(cfg["global_anchor_target"])
        target = min(requested_target, len(candidates))
        for index in rng.permutation(len(candidates)):
            if len(anchors) >= target:
                break
            y, x = map(int, candidates[index])
            if not valid(x, y):
                continue
            objects[y, x] = int(cfg["exhausted_id"]) - 8
            for dx, dy in footprint:
                access[y + dy, x + dx] = 1
                covered[y + dy, x + dx] = True
            mark(x, y)
            anchors.append((x, y, 8))
        if len(anchors) < target and self.side == self.reference_side:
            raise RuntimeError(f"Upgraded building-stone quota not reached: {len(anchors)}/{target}")
        target = len(anchors)
        profile_stock_target = int(cfg["global_stock_target"])
        stock_target = self._scaled_target(profile_stock_target)
        if target:
            stock_target = max(target, min(target * 12, stock_target))
        else:
            stock_target = 0
        base_quantity = min(8, max(1, stock_target // target)) if target else 0
        quantities = np.full(len(anchors), base_quantity, dtype=int)
        while int(quantities.sum()) < stock_target:
            eligible = np.where(quantities < 12)[0]
            if not len(eligible):
                break
            quantities[int(rng.choice(eligible))] += 1
        while int(quantities.sum()) > stock_target:
            eligible = np.where(quantities > 1)[0]
            if not len(eligible):
                break
            quantities[int(rng.choice(eligible))] -= 1
        for (x, y, _), quantity in zip(anchors, quantities):
            objects[y, x] = int(cfg["exhausted_id"]) - int(quantity)
        metadata = {
            "anchors": len(anchors),
            "stock": int(quantities.sum()),
            "anchor_target": target,
            "stock_target": stock_target,
            "profile_targets_768": {
                "anchors": int(cfg["global_anchor_target"]),
                "stock": profile_stock_target,
            },
            "start_bonus_deferred": True,
        }
        state.metadata["upgraded_stones"] = metadata
        state.metadata["upgraded_stone_targets"] = {"anchors": target, "stock": stock_target}
        state.metadata["building_stone_anchors"] = [(x, y, int(q), "global") for (x, y, _), q in zip(anchors, quantities)]
        state.metadata["building_stone_footprint_cells"] = [(x + dx, y + dy) for x, y, _ in anchors for dx, dy in footprint]
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
