"""Upgraded content pass.

This module is intentionally independent from the Legacy generator.  It owns
the calibrated Upgraded mineral/fish routines and the final object pass.  The
start pass consumes the already-positioned coordinates for five independent
bonuses: mini-swamps, forest, building stones, rocky mineral zones and
mini-lakes with fish/rivers.  Start coordinates remain the isolated
provisional bridge owned by :mod:`starts`.
"""

from __future__ import annotations

from collections.abc import Mapping
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
    GRASS_SWAMP_TRANS,
    HEX6,
    MOUNTAIN_FAMILY_IDS,
    REEF_IDS,
    RIVER_IDS,
    ROCK_TRANS_1,
    ROCK_TRANS_2,
    ROCKY,
    SNOW,
    SNOW_TRANS,
    SHORE,
    SWAMP,
    SWAMP_TRANS,
    WATER_IDS,
    SWAMP_IDS,
)
from ....map_data.hexgrid import dilate, distance_from, hex_distance, neighbor_count
from ...custom.bonus_placement import (
    FORCED_CENTER_EXTENSION, ordered_centers, radius_center_pairs, plan_objects,
)
from ...custom.bonus_minerals import (
    compact_hex_offsets,
    organic_offsets,
    transition_rings,
)
from ...custom.bonus_water import (
    native_lake_offsets,
    water_depths,
)
from ...custom.content import (
    _bounded_quantities,
    _full_range_quantities,
    _place_custom_fish,
    _place_legacy_minerals,
    _place_random_minerals,
    _size_bounds,
)
from ...custom.sections import (
    DEFAULT_FISH_BAND_THICKNESS,
    MINERAL_SPECS,
    STONE_QUANTITY_MAXIMUM,
    STONE_QUANTITY_MINIMUM,
    RESOURCE_MAXIMUM,
    RESOURCE_MINIMUM,
    START_BONUS_COUNT_MAX,
    START_BONUS_COUNT_MIN,
    START_FOREST_COUNT_MAX,
    START_FOREST_COUNT_MIN,
    START_FOREST_ADULT_DEFAULT,
    START_FOREST_SAPLING_DEFAULT,
    START_STONE_ANCHOR_MAX,
    START_STONE_ANCHOR_MIN,
    START_STONE_ANCHOR_DEFAULT,
    START_STONE_AVERAGE_DEFAULT,
    START_BONUS_DISTANCE_MAX,
    START_BONUS_DISTANCE_MIN,
    START_BONUS_FISH_FILL_MAX,
    START_BONUS_FISH_FILL_MIN,
    START_BONUS_RADIUS_MAX,
    START_LAKE_SHAPES,
    START_BONUS_RADIUS_MIN,
    START_ROCKY_RADIUS_MAX,
    START_ROCKY_CORE_CELLS_MAX,
    START_ROCKY_CORE_CELLS_MIN,
    rocky_proportional_targets,
    START_SWAMP_RADIUS_DEFAULT,
    START_SWAMP_RADIUS_MAX,
    START_SWAMP_RADIUS_MIN,
    START_SWAMP_SHAPES,
    START_BONUS_RIVER_TARGET_MAX,
    START_BONUS_RIVER_TARGET_MIN,
    START_BONUS_STOCK_MAX,
    START_BONUS_STOCK_MIN,
    START_BONUS_WATER_PROXIMITY_MAX,
    START_BONUS_WATER_PROXIMITY_MIN,
    UPGRADED_FISH_FILL_PERCENT,
    UPGRADED_RESOURCE_MEAN,
)
from ...custom.terrain import (
    TERRAIN_TRANSITION_ALLOWED,
    effective_decoration_rates,
)
from .native_terrain import (
    NativeRng16 as _NativeRng16,
    NativeTerrainGrid as _NativeTerrainGrid,
    _FAMILY_PLANS as _NATIVE_FAMILY_PLANS,
    _apply_family_plan as _apply_native_family_plan,
    grow_native_bonus_river,
)


_HEX_STRUCTURE = np.array([[1, 1, 0], [1, 1, 1], [0, 1, 1]], dtype=bool)
_NATIVE_SWAMP_PLAN = _NATIVE_FAMILY_PLANS[1]
_NATIVE_SWAMP_ATTEMPTS = 16

# Kept deliberately compact: this is diagnostic metadata for the generator,
# not a second user-facing report.  The counters let the UI/tests explain
# why a forced lake was skipped without changing placement behaviour.
_LAKE_REJECTION_KEYS = (
    "water_proximity",
    "no_center_candidates",
    "footprint_out_of_bounds",
    "footprint_non_grass",
    "footprint_technical_clearance",
    "footprint_reserved",
    "footprint_object_collision",
    "footprint_resource_collision",
    "shape_invalid",
    "no_legal_river_mouth",
    "river_trace_failed",
    "shore_transition_invalid",
)


def _half_step_quantity(value: float, default: float = 1.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = float(default)
    number = min(float(STONE_QUANTITY_MAXIMUM), max(float(STONE_QUANTITY_MINIMUM), number))
    return float(
        min(
            float(STONE_QUANTITY_MAXIMUM),
            max(float(STONE_QUANTITY_MINIMUM), math.floor(number * 2.0 + 0.5) / 2.0),
        )
    )


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


def _native_swamp_offsets(radius: int, pr: random.Random) -> list[tuple[int, int]]:
    """Generate one native-shaped swamp footprint inside ``radius``.

    The global native swamp pass is a brush/expand/erode sequence, not a
    geometric hexagon.  Run that same family plan on a sufficiently large
    grass sandbox, then keep its largest native component and recenter it on
    the requested bonus centre.  The requested radius is a hard extent cap;
    it is not replaced by a hand-drawn ring or a free-cell quota.

    The previous implementation used a radius-sized sandbox with a very high
    artificial brush rate.  Small requests therefore saturated into a perfect
    hexagon, while real maps often rejected the complete patch at the first
    obstacle.  A fixed native-sized sandbox plus the same plan at a modest
    radius-scaled rate preserves the native morphology and leaves the caller
    room to apply a legal partial fallback.
    """

    radius = max(1, int(radius))
    sandbox_side = 256
    native_rate = min(500.0, max(100.0, 100.0 + 10.0 * radius))
    best_complete: list[tuple[int, int]] = []
    best_complete_score = (-1, -1)
    best_clipped: list[tuple[int, int]] = []
    best_clipped_score = (-1, -1)

    for _ in range(_NATIVE_SWAMP_ATTEMPTS):
        grid = _NativeTerrainGrid.empty(sandbox_side)
        grid.terrain[:] = GRASS
        _apply_native_family_plan(
            grid,
            _NativeRng16(pr.randrange(1, 0xFFFFFFFF)),
            _NATIVE_SWAMP_PLAN,
            native_rate,
        )
        mask = np.isin(grid.terrain, SWAMP_IDS)
        labels, component_count = ndimage.label(mask, structure=_HEX_STRUCTURE)
        for label in range(1, int(component_count) + 1):
            ys, xs = np.where(labels == label)
            if not len(xs):
                continue
            component_center_x = round(float(xs.mean()))
            component_center_y = round(float(ys.mean()))
            raw_points = [
                (int(x) - component_center_x, int(y) - component_center_y)
                for x, y in zip(xs, ys)
            ]
            points = [
                (x, y)
                for x, y in raw_points
                if hex_distance(0, 0, x, y) <= radius
            ]
            clipped_score = (len(points), len(raw_points))
            if points and clipped_score > best_clipped_score:
                best_clipped = points
                best_clipped_score = clipped_score
            if len(points) == len(raw_points):
                complete_score = (len(raw_points), len(raw_points))
                if complete_score > best_complete_score:
                    best_complete = raw_points
                    best_complete_score = complete_score
    # Prefer a complete component.  Cropping a larger component to the radius
    # is only a fallback: it regularly filled the whole disc and made the
    # Native option visually indistinguishable from Hexagon.
    return best_complete or best_clipped


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
    protected = np.zeros(count, dtype=bool)
    if ensure_all_values and count >= len(values):
        quantities[: len(values)] = values
        # Keep the representative 1..12 states alive while the exact total
        # is balanced.  Without this small reservation an upward correction
        # could increment the only quantity-1 anchor and silently remove ID
        # 126 from an otherwise complete building-stone distribution.
        protected[: len(values)] = True

    difference = total - int(quantities.sum())
    while difference:
        if difference > 0:
            eligible = np.flatnonzero((quantities < maximum) & ~protected)
            if not len(eligible):
                eligible = np.flatnonzero(quantities < maximum)
            if not len(eligible):
                break
            quantities[int(rng.choice(eligible))] += 1
            difference -= 1
        else:
            eligible = np.flatnonzero((quantities > minimum) & ~protected)
            if not len(eligible):
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
        self._start_bonus_reservation: np.ndarray | None = None
        self._start_bonus_swamp_mask: np.ndarray | None = None
        self._start_bonus_water: np.ndarray | None = None
        self._start_bonus_rocky_records: list[dict[str, object]] = []
        self._start_bonus_lake_records: list[dict[str, object]] = []
        self._prioritized_start_stone_state: dict[str, object] | None = None
        self._start_bonus_object_clearance: np.ndarray | None = None
        # The native/no-bonus path deliberately leaves this disabled.  The
        # active Custom start-package route uses it as a live hitbox field:
        # only cells occupied by an object (or by a written stone footprint)
        # are expanded into the collision halo.  It is refreshed/extended
        # after each real object write; it is never a planned zone mask.
        self._object_hitbox_enforced = False
        self._object_collision_mask: np.ndarray | None = None
        runtime = profile.get("_custom_runtime", {})
        self._custom_start_packages = (
            set(str(value) for value in runtime.get("start_packages", ()))
            if isinstance(runtime, dict) and "start_packages" in runtime
            else None
        )
        self._custom_sections = (
            runtime.get("sections")
            if isinstance(runtime, dict) and isinstance(runtime.get("sections"), dict) and runtime.get("sections")
            else None
        )

    def _start_package_enabled(self, key: str) -> bool:
        """Return the declarative start-package state, preserving Upgraded defaults."""

        return self._custom_start_packages is None or str(key) in self._custom_start_packages

    def _custom_start_bonus_config(self, key: str) -> dict[str, object]:
        """Combine the active profile rule with the semantic start controls.

        The profile keeps engine-only geometry and collision invariants.  The
        Custom editor stores only the readable quantities and switches in its
        ``start_bonus`` section, so the overlay must be recursive and must
        apply the one common border distance to every compatible bonus.
        """

        profile_bonuses = self.profile.get("start_bonus", {})
        profile_value = profile_bonuses.get(key, {}) if isinstance(profile_bonuses, Mapping) else {}
        result: dict[str, object] = dict(profile_value) if isinstance(profile_value, Mapping) else {}
        custom_start = self._custom_sections.get("start_bonus", {}) if isinstance(self._custom_sections, Mapping) else {}
        custom_value = custom_start.get(key, {}) if isinstance(custom_start, Mapping) else {}

        def merge(target: dict[str, object], overlay: Mapping[str, object]) -> None:
            for name, value in overlay.items():
                if isinstance(value, Mapping) and isinstance(target.get(name), Mapping):
                    child = dict(target[name])
                    merge(child, value)
                    target[name] = child
                else:
                    target[name] = value

        if isinstance(custom_value, Mapping):
            merge(result, custom_value)
        if isinstance(custom_start, Mapping) and "distance_from_border" in custom_start:
            result["distance_from_border"] = custom_start["distance_from_border"]
        return result

    @staticmethod
    def _start_bonus_int(value, low: int, high: int, default: int) -> int:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = float(default)
        return int(round(min(float(high), max(float(low), number))))

    @staticmethod
    def _start_bonus_float(value, low: float, high: float, default: float) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = float(default)
        return min(float(high), max(float(low), number))

    def _custom_global_resource_mean(self, family: str, default: int = UPGRADED_RESOURCE_MEAN) -> int:
        """Use the same readable resource mean as the corresponding global pool."""

        value: object = default
        section_name = "fish" if family == "fish" else "minerals"
        section = self._custom_sections.get(section_name, {}) if isinstance(self._custom_sections, Mapping) else {}
        if family == "fish" and isinstance(section, Mapping):
            value = section.get("average_quantity", default)
        elif isinstance(section, Mapping):
            averages = section.get("average_quantity", {})
            if isinstance(averages, Mapping):
                value = averages.get(family, default)
        return self._start_bonus_int(value, RESOURCE_MINIMUM, RESOURCE_MAXIMUM, default)

    def log(self, stage: str, detail: str = "") -> None:
        self._stage_log.append(stage + (f" — {detail}" if detail else ""))
        if self.progress is not None:
            self.progress(stage, detail)

    def _scaled_target(self, value: int) -> int:
        """Scale a 768-calibrated quota by map area, without changing 768."""
        ratio = float(self.side) / float(self.reference_side)
        return max(0, int(round(int(value) * ratio * ratio)))

    def _custom_percent(
        self,
        section: str,
        key: str,
        default: float,
        *,
        maximum: float = 200.0,
    ) -> float:
        """Read one bounded semantic percentage without exposing profile knobs."""

        value = default
        if isinstance(self._custom_sections, dict):
            candidate = self._custom_sections.get(section, {})
            if isinstance(candidate, dict):
                for part in str(key).split("."):
                    if not isinstance(candidate, dict) or part not in candidate:
                        candidate = None
                        break
                    candidate = candidate[part]
                if candidate is not None:
                    value = candidate
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = float(default)
        return min(float(maximum), max(0.0, value))

    def _grass_object_support_enabled(self) -> bool:
        """Whether Custom may use dry/detail grass for normal grass objects."""

        objects = self._custom_sections.get("objects", {}) if isinstance(self._custom_sections, Mapping) else {}
        return bool(
            isinstance(objects, Mapping)
            and objects.get("grass_compatible_on_dry_and_details", False)
        )

    def _grass_object_support_mask(self, terrain: np.ndarray) -> np.ndarray:
        ids = GRASS_IDS if self._grass_object_support_enabled() else (GRASS,)
        return np.isin(terrain, ids)

    def _force_extended_start_bonus(self) -> bool:
        start_bonus = (
            self._custom_sections.get("start_bonus", {})
            if isinstance(self._custom_sections, Mapping)
            else {}
        )
        return bool(
            isinstance(start_bonus, Mapping)
            and start_bonus.get("force_extended_radius", False)
        )

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

    def _refresh_object_collision_mask(self, state) -> None:
        """Rebuild the live object hitbox field from actual writes only."""

        cells = np.asarray(state.objects != 0, dtype=bool).copy()
        footprint = state.metadata.get("building_stone_footprint_cells", ())
        if self._prioritized_start_stone_state is not None:
            start_mask = self._prioritized_start_stone_state.get("start_stone_mask")
            if isinstance(start_mask, np.ndarray):
                cells |= np.asarray(start_mask, dtype=bool)
        for cell in footprint:
            if isinstance(cell, (tuple, list)) and len(cell) == 2:
                x, y = int(cell[0]), int(cell[1])
                if 0 <= x < self.side and 0 <= y < self.side:
                    cells[y, x] = True
        self._object_collision_mask = dilate(cells, 2)

    def _mark_object_collision_cells(
        self,
        points: list[tuple[int, int]] | tuple[tuple[int, int], ...],
    ) -> None:
        """Extend the live hitbox mask around cells just written."""

        if not self._object_hitbox_enforced:
            return
        if self._object_collision_mask is None:
            return
        for x, y in points:
            x, y = int(x), int(y)
            for yy in range(max(0, y - 2), min(self.side, y + 3)):
                for xx in range(max(0, x - 2), min(self.side, x + 3)):
                    if hex_distance(x, y, xx, yy) <= 2:
                        self._object_collision_mask[yy, xx] = True

    def _content_core(self, state) -> np.ndarray:
        """Return the global object-clearing zone around each start."""

        starts_cfg = self.profile["starts"]
        core = self._core_mask(
            state,
            max(
                int(starts_cfg["technical_clear_hex"]),
                int(starts_cfg.get("editor_object_clear_hex", 14)),
            ),
        )
        if self._start_bonus_reservation is not None:
            core |= self._start_bonus_reservation
        return core

    def _refresh_start_bonus_object_clearance(self, state) -> None:
        """Build the live collision halo around written start objects.

        The mask is deliberately derived from actual object/footprint writes,
        never from a planned forest or stone envelope.  Two HEX6 dilation
        steps make a later anchor at distance 1 or 2 illegal, leaving the
        calibrated distance 3 available for tree/object contacts.
        """

        cells = state.objects != 0
        if self._prioritized_start_stone_state is not None:
            stone_mask = self._prioritized_start_stone_state.get("start_stone_mask")
            if isinstance(stone_mask, np.ndarray):
                cells = cells | np.asarray(stone_mask, dtype=bool)
        self._start_bonus_object_clearance = dilate(cells, 2)
        if self._object_hitbox_enforced:
            self._refresh_object_collision_mask(state)
            if self._object_collision_mask is not None:
                self._start_bonus_object_clearance = self._object_collision_mask.copy()

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
        # Details/dry grass are valid object supports when the shared switch
        # is enabled, but the measured swamp transition table uses base grass
        # (16) at the outside rim.  Normalize only cells adjacent to a bonus
        # swamp, reserve them from the other bonus layers, and leave native
        # swamp output untouched.
        bonus_swamp = self._start_bonus_swamp_mask
        if bonus_swamp is not None and bonus_swamp.any():
            normalize = (
                np.isin(terrain, GRASS_IDS)
                & (neighbor_count(bonus_swamp) > 0)
                & ~swamp
            )
            terrain[normalize] = GRASS
            if self._start_bonus_reservation is not None:
                self._start_bonus_reservation[normalize] = True

    def _place_start_mini_swamps(
        self,
        state,
        pr: random.Random,
        *,
        rebuild_transitions: bool = True,
    ) -> None:
        """Paint one coherent mini-swamp per start.

        The coordinates are deliberately not recalculated here.  The starts
        bridge has already supplied them, and this pass only searches for a
        legal nearby patch.  The visible size is a radius, not an arbitrary
        cell quota.  ``native`` runs the same brush/expand/erode family plan
        as the global swamp pass; ``hexagon`` keeps the complete disc.
        """

        starts_cfg = self.profile["starts"]
        bonus_cfg = self._custom_start_bonus_config("mini_swamp")
        package_enabled = self._start_package_enabled("start_mini_swamp")
        bonus_enabled = package_enabled and bool(bonus_cfg.get("enabled", True))
        shape = str(bonus_cfg.get("shape", "native")).lower()
        if shape not in START_SWAMP_SHAPES:
            shape = "native"
        requested_radius = self._start_bonus_int(
            bonus_cfg.get("radius", START_SWAMP_RADIUS_DEFAULT),
            START_SWAMP_RADIUS_MIN,
            START_SWAMP_RADIUS_MAX,
            START_SWAMP_RADIUS_DEFAULT,
        ) if bonus_enabled else 0
        requested_core_cells = (
            1 + 3 * requested_radius * (requested_radius + 1)
            if requested_radius > 0 else 0
        )
        # Native footprints are generated per start below.  Keeping the first
        # shape in ``native_offsets`` preserves the existing scalar diagnostics
        # while allowing every player to receive an independent native draw.
        native_offsets: list[tuple[int, int]] = []
        native_shape_cells_per_start: list[int] = []
        requested_cells_by_start: list[int] = []
        requested_cells = requested_core_cells if shape != "native" else 0
        if not bonus_enabled or requested_radius <= 0:
            state.metadata["upgraded_start_mini_swamps"] = {
                "enabled": False,
                "shape": shape,
                "radius": requested_radius,
                "requested_core_cells_per_start": requested_core_cells,
                "requested_cells_per_start": requested_cells,
                "placed_cells_per_start": [0 for _ in state.starts],
                "placed_cells": 0,
                "starts_with_bonus": 0,
                "shortfalls": [],
                "outside_technical_zone": True,
                "disabled_reason": (
                    "disabled by Custom profile"
                    if not package_enabled or not bool(bonus_cfg.get("enabled", True))
                    else "non_positive_size"
                ),
            }
            self.log("biomes.upgraded_start_mini_swamps", "disabled by Custom profile")
            return
        terrain = state.terrain
        objects, resources = state.objects, state.resources
        grass_support = self._grass_object_support_mask(terrain)
        force_extended = self._force_extended_start_bonus()
        technical = self._core_mask(state, max(
            int(starts_cfg["technical_clear_hex"]),
            int(starts_cfg.get("editor_object_clear_hex", 14)) if self._force_extended_start_bonus() else 0,
        ))
        reservation = self._start_bonus_reservation
        if reservation is None:
            reservation = np.zeros_like(terrain, dtype=bool)
        center_radius = int(bonus_cfg.get("center_hex", starts_cfg.get("initial_territory_hex_radius", 34)))
        center_radius = max(1, center_radius + self._start_bonus_int(
            bonus_cfg.get("distance_from_border", 0),
            START_BONUS_DISTANCE_MIN,
            START_BONUS_DISTANCE_MAX,
            0,
        ))
        placed_by_start: list[int] = []
        shortfalls: list[int] = []
        extended_radius_used = False

        def clean_halo(points: list[tuple[int, int]]) -> bool:
            point_set = set(points)
            for x, y in points:
                for dx, dy in HEX6:
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < self.side and 0 <= yy < self.side):
                        return False
                    if (xx, yy) in point_set:
                        continue
                    if (
                        not grass_support[yy, xx]
                        or technical[yy, xx]
                        or reservation[yy, xx]
                        or objects[yy, xx] != 0
                        or resources[yy, xx] != 0
                    ):
                        return False
            return True

        def point_legal(x: int, y: int) -> bool:
            return (
                0 <= x < self.side
                and 0 <= y < self.side
                and grass_support[y, x]
                and not technical[y, x]
                and not reservation[y, x]
                and objects[y, x] == 0
                and resources[y, x] == 0
            )

        def legal_patch(points: list[tuple[int, int]]) -> bool:
            return bool(points) and all(
                0 <= x < self.side
                and 0 <= y < self.side
                and grass_support[y, x]
                and not technical[y, x]
                and not reservation[y, x]
                and objects[y, x] == 0
                and resources[y, x] == 0
                for x, y in points
            )

        def partial_patch(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
            """Keep the largest native-shaped part with a legal transition rim."""

            legal = {point for point in points if point_legal(*point)}
            if not legal:
                return []
            components: list[set[tuple[int, int]]] = []
            while legal:
                seed = legal.pop()
                component = {seed}
                queue = [seed]
                while queue:
                    x, y = queue.pop()
                    for dx, dy in HEX6:
                        neighbour = (x + dx, y + dy)
                        if neighbour in legal:
                            legal.remove(neighbour)
                            component.add(neighbour)
                            queue.append(neighbour)
                components.append(component)

            best: list[tuple[int, int]] = []
            for component in sorted(components, key=len, reverse=True):
                current = set(component)
                # Obstacles at the border of a clipped native component must
                # not become an illegal terrain transition.  Peel only the
                # cells that touch such an obstacle; this is a legal fallback
                # for a requested zone that cannot fit completely.
                for _ in range(max(1, requested_radius * 2 + 2)):
                    safe = {
                        (x, y)
                        for x, y in current
                        if all(
                            0 <= x + dx < self.side
                            and 0 <= y + dy < self.side
                            and (
                                (x + dx, y + dy) in current
                                or point_legal(x + dx, y + dy)
                            )
                            for dx, dy in HEX6
                        )
                    }
                    if safe == current:
                        break
                    if not safe:
                        current = set()
                        break
                    current = safe
                candidate = list(current)
                if candidate and clean_halo(candidate) and len(candidate) > len(best):
                    best = candidate
            return best

        def shape_points(
            cx: int,
            cy: int,
            radius: int,
            native_offsets_for_start: list[tuple[int, int]],
        ) -> list[tuple[int, int]]:
            if shape == "native":
                return [
                    (cx + dx, cy + dy)
                    for dx, dy in native_offsets_for_start
                    if hex_distance(0, 0, dx, dy) <= radius
                ]
            core = _hex_points(self.side, cx, cy, radius)
            if len(core) != 1 + 3 * radius * (radius + 1):
                return []
            return core

        for start_index, (sx, sy) in enumerate(state.starts):
            sx, sy = int(sx), int(sy)
            start_native_offsets = (
                _native_swamp_offsets(requested_radius, pr)
                if shape == "native" and requested_radius > 0
                else []
            )
            start_requested_cells = (
                len(start_native_offsets)
                if shape == "native"
                else requested_core_cells
            )
            if start_index == 0:
                native_offsets = start_native_offsets
                requested_cells = start_requested_cells
            if shape == "native":
                native_shape_cells_per_start.append(len(start_native_offsets))
            requested_cells_by_start.append(start_requested_cells)
            centers: list[tuple[int, int]] = []
            for radius in range(max(1, center_radius - 2), center_radius + 3):
                centers.extend(
                    (x, y)
                    for x, y in _hex_points(self.side, sx, sy, radius, exact=radius)
                    if (
                        grass_support[y, x]
                        and not technical[y, x]
                        and not reservation[y, x]
                        and objects[y, x] == 0
                        and resources[y, x] == 0
                    )
                )
            pr.shuffle(centers)
            if force_extended:
                centers = list(ordered_centers(
                    grass_support & ~technical & ~reservation
                    & (objects == 0) & (resources == 0),
                    sx, sy, center_radius, pr.shuffle,
                ))
            patch: list[tuple[int, int]] = []
            chosen_center: tuple[int, int] | None = None

            # Prefer the requested radius everywhere in the local ring before
            # accepting a smaller complete shape.  The old centre-first loop
            # often accepted a radius-1 fallback at the first candidate even
            # when a complete requested patch existed a few cells later.
            for candidate_radius in (requested_radius,):
                for cx, cy in centers:
                    candidate = shape_points(
                        cx, cy, candidate_radius, start_native_offsets
                    )
                    if legal_patch(candidate) and clean_halo(candidate):
                        patch = candidate
                        chosen_center = (cx, cy)
                        break
                if patch:
                    break

            # If a complete requested zone does not fit, retain the largest
            # legal native/hexagonal component instead of dropping the bonus.
            # This writes only the cells that will really become swamp.
            if not patch:
                best_partial: list[tuple[int, int]] = []
                best_center: tuple[int, int] | None = None
                for cx, cy in centers:
                    candidate = partial_patch(
                        shape_points(
                            cx, cy, requested_radius, start_native_offsets
                        )
                    )
                    if len(candidate) > len(best_partial):
                        best_partial = candidate
                        best_center = (cx, cy)
                if best_partial:
                    patch = best_partial
                    chosen_center = best_center

            # A smaller complete radius remains preferable to an isolated
            # one-cell fragment when no requested-radius subset is legal.
            if not patch:
                for candidate_radius in range(requested_radius - 1, 0, -1):
                    for cx, cy in centers:
                        candidate = shape_points(
                            cx, cy, candidate_radius, start_native_offsets
                        )
                        if legal_patch(candidate) and clean_halo(candidate):
                            patch = candidate
                            chosen_center = (cx, cy)
                            break
                    if patch:
                        break
            if chosen_center is not None:
                cx, cy = chosen_center
                extended_radius_used = bool(
                    extended_radius_used
                    or hex_distance(sx, sy, cx, cy) > center_radius + 2
                )
            for x, y in patch:
                terrain[y, x] = GRASS_SWAMP_TRANS
                reservation[y, x] = True
                if self._start_bonus_swamp_mask is not None:
                    self._start_bonus_swamp_mask[y, x] = True
            placed_by_start.append(len(patch))
            if len(patch) < start_requested_cells:
                shortfalls.append(start_requested_cells - len(patch))

        if rebuild_transitions:
            self._rebuild_swamp_transitions(state)
        metadata = {
            "enabled": True,
            "per_player": True,
            "shape": shape,
            "radius": requested_radius,
            "requested_core_cells_per_start": requested_core_cells,
            "requested_cells_per_start": requested_cells,
            "requested_cells_by_start": requested_cells_by_start,
            "native_shape_cells": len(native_offsets),
            "native_shape_cells_per_start": native_shape_cells_per_start,
            "center_hex": center_radius,
            "placed_cells_per_start": placed_by_start,
            "placed_cells": int(sum(placed_by_start)),
            "starts_with_bonus": sum(value > 0 for value in placed_by_start),
            "shortfalls": shortfalls,
            "force_extended_radius": bool(force_extended),
            **({"center_extension_limit": FORCED_CENTER_EXTENSION, "tower_clear_hex": int(self.profile["starts"].get("editor_object_clear_hex", 14))} if force_extended else {}),
            "extended_radius_used": bool(extended_radius_used),
            "outside_technical_zone": True,
        }
        state.metadata["upgraded_start_mini_swamps"] = metadata
        self.log("biomes.upgraded_start_mini_swamps", str(metadata))

    def _bonus_center_candidates(
        self,
        state,
        sx: int,
        sy: int,
        desired: int,
        terrain: np.ndarray,
        blocked: np.ndarray,
        pr: random.Random,
        *,
        support_mask: np.ndarray | None = None,
        force_extended: bool = False,
    ) -> list[tuple[int, int]]:
        """Return randomized centres around the requested start-border ring."""

        centres: list[tuple[int, int]] = []
        desired = max(1, int(desired))
        support = (
            np.asarray(support_mask, dtype=bool)
            if support_mask is not None
            else terrain == GRASS
        )
        if force_extended:
            return list(ordered_centers(support & ~blocked, sx, sy, desired, pr.shuffle))
        for ring in range(max(1, desired - 2), desired + 3):
            centres.extend(
                (x, y)
                for x, y in _hex_points(self.side, sx, sy, ring, exact=ring)
                if support[y, x] and not blocked[y, x]
            )
        local = list(centres)
        pr.shuffle(local)
        return local

    @staticmethod
    def _full_hex_disc_area(radius: int) -> int:
        radius = max(0, int(radius))
        return 1 + 3 * radius * (radius + 1)

    @staticmethod
    def _full_hex_ring_area(radius: int) -> int:
        return max(0, 6 * (int(radius) + 1))

    @staticmethod
    def _canonical_rocky_surface_mode(value: object) -> str:
        mode = str(value).lower()
        if mode in {"share", "shares", "prorata", "pro_rata", "proportional"}:
            return "proportional"
        if mode in {"per_mineral", "per_family", "customized"}:
            return "custom"
        return mode if mode in {"equal", "proportional", "custom"} else "equal"

    def _rocky_surface_targets(
        self,
        cfg: Mapping[str, object],
        zone_specs: list[tuple[str, int, bool]],
        radius_min: int,
        radius_max: int,
    ) -> tuple[str, dict[str, int], dict[str, float]]:
        """Resolve R48 core surfaces without changing R47's default mode."""

        mode = self._canonical_rocky_surface_mode(
            cfg.get("surface_mode", cfg.get("allocation_mode", "equal"))
        )

        enabled = [name for name, _family, active in zone_specs if active]
        default_radius = int(round((radius_min + radius_max) / 2.0)) if radius_max else 0
        default_area = self._full_hex_disc_area(default_radius)
        targets: dict[str, int] = {}
        shares: dict[str, float] = {}

        if mode == "custom":
            for name in enabled:
                entry = cfg.get(name, {})
                entry = entry if isinstance(entry, Mapping) else {}
                try:
                    target = int(round(float(entry.get("core_cells", entry.get("surface", default_area)))))
                except (TypeError, ValueError):
                    target = default_area
                targets[name] = max(
                    START_ROCKY_CORE_CELLS_MIN,
                    min(START_ROCKY_CORE_CELLS_MAX, target),
                )
            return mode, targets, shares

        if mode == "proportional":
            raw_total = cfg.get("total_core_cells")
            try:
                total = int(round(float(raw_total))) if raw_total is not None else default_area * len(enabled)
            except (TypeError, ValueError):
                total = default_area * len(enabled)
            total = (
                max(
                    len(enabled) * START_ROCKY_CORE_CELLS_MIN,
                    min(START_ROCKY_CORE_CELLS_MAX * len(enabled), total),
                )
                if enabled
                else 0
            )
            raw_shares: object = {}
            if isinstance(self._custom_sections, Mapping):
                mineral_section = self._custom_sections.get("minerals", {})
                if isinstance(mineral_section, Mapping):
                    raw_shares = mineral_section.get("shares", {})
            if not isinstance(raw_shares, Mapping):
                raw_shares = {}
            profile_shares = self.profile.get("minerals", {}).get("shares", {})
            profile_shares = profile_shares if isinstance(profile_shares, Mapping) else {}
            for name in enabled:
                value = raw_shares.get(name)
                if value is None:
                    family = next((family for family_name, family, active in zone_specs if family_name == name), 0)
                    value = profile_shares.get(str(family), 0.0)
                try:
                    shares[name] = max(0.0, float(value))
                except (TypeError, ValueError):
                    shares[name] = 0.0
            if not any(shares.values()):
                shares = {name: 1.0 for name in enabled}
            weight_total = sum(shares.values())
            # Allocate with a per-mineral cap.  The public total scales with
            # the active families (up to 2,460), while no individual
            # coal/iron/gold core may exceed the rounded 820-cell ceiling.
            targets = rocky_proportional_targets(total, enabled, shares)
            shares = {
                name: (shares[name] / weight_total * 100.0 if weight_total else 0.0)
                for name in enabled
            }
            return mode, targets, shares

        # ``equal`` deliberately returns no explicit target: its existing
        # radius loop is retained byte-for-byte for Hexagon/R47 compatibility.
        return mode, targets, shares

    @staticmethod
    def _rocky_relative_shape(
        shape: str,
        mode: str,
        target: int,
        radius: int,
        pr: random.Random,
    ) -> list[tuple[int, int]]:
        if shape == "organic":
            return organic_offsets(target, pr)
        if mode == "equal" and target <= 0:
            return []
        if mode == "equal":
            # The caller passes the canonical radius area in this case.
            return compact_hex_offsets(target, pr)
        return compact_hex_offsets(target, pr)

    @staticmethod
    def _minimum_tree_forest_radius(tree_count: int, spacing: int) -> int:
        """Derive the first clean HEX6 disc that can pack the tree request."""

        target = max(1, int(tree_count))
        spacing = max(1, int(spacing))
        radius = 0
        while True:
            points = [
                (x, y)
                for y in range(-radius, radius + 1)
                for x in range(-radius, radius + 1)
                if hex_distance(0, 0, x, y) <= radius
            ]
            chosen: list[tuple[int, int]] = []
            for x, y in points:
                if all(hex_distance(x, y, xx, yy) >= spacing for xx, yy in chosen):
                    chosen.append((x, y))
                    if len(chosen) >= target:
                        return radius
            radius += 1

    def _place_start_rocky_minerals(self, state, pr: random.Random) -> None:
        """Paint independent start mineral zones, retaining a legal halo.

        The core is the only part that receives a resource family.  The two
        surrounding rings reproduce the native grass → rock transition chain
        (17 → 33 → 32) and the whole envelope is reserved before global
        content is generated.
        """

        cfg = self._custom_start_bonus_config("rocky_minerals")
        package_enabled = self._start_package_enabled("start_rocky_minerals")
        bonus_enabled = package_enabled and bool(cfg.get("enabled", True))
        terrain, objects, resources = state.terrain, state.objects, state.resources
        grass_support = self._grass_object_support_mask(terrain)
        force_extended = self._force_extended_start_bonus()
        reservation = self._start_bonus_reservation
        if reservation is None:
            reservation = np.zeros_like(terrain, dtype=bool)
            self._start_bonus_reservation = reservation
        technical = self._core_mask(state, max(
            int(self.profile["starts"]["technical_clear_hex"]),
            int(self.profile["starts"].get("editor_object_clear_hex", 14)) if self._force_extended_start_bonus() else 0,
        ))
        surface_mode_hint = self._canonical_rocky_surface_mode(
            cfg.get("surface_mode", cfg.get("allocation_mode", "equal"))
        )
        raw_min = self._start_bonus_int(
            cfg.get("radius_min", 3),
            START_BONUS_RADIUS_MIN,
            START_ROCKY_RADIUS_MAX,
            3,
        ) if bonus_enabled else 0
        raw_max = self._start_bonus_int(
            cfg.get("radius_max", 5),
            raw_min or START_BONUS_RADIUS_MIN,
            START_ROCKY_RADIUS_MAX,
            max(raw_min, 5),
        ) if bonus_enabled else 0
        if bonus_enabled and surface_mode_hint == "equal":
            equal_radius = self._start_bonus_int(
                cfg.get("radius", int(round((raw_min + raw_max) / 2.0))),
                START_BONUS_RADIUS_MIN,
                START_ROCKY_RADIUS_MAX,
                4,
            )
            raw_min = raw_max = equal_radius
        radius_max = max(0, raw_max)
        radius_min = max(1, min(raw_min, radius_max)) if radius_max else 0
        zones_cfg = cfg.get("zones", {}) if isinstance(cfg, dict) else {}
        zones_cfg = zones_cfg if isinstance(zones_cfg, Mapping) else {}
        zone_specs = []
        for name, default_family in (("coal", 0x10), ("iron", 0x20), ("gold", 0x30)):
            entry = zones_cfg.get(name, {})
            entry = dict(entry) if isinstance(entry, Mapping) else {}
            semantic_entry = cfg.get(name, {})
            if isinstance(semantic_entry, Mapping) and "enabled" in semantic_entry:
                entry["enabled"] = semantic_entry["enabled"]
            family = int(entry.get("family", default_family)) & 0xF0
            enabled = bonus_enabled and bool(entry.get("enabled", True)) and radius_max > 0
            zone_specs.append((name, family, enabled))
        shape = str(cfg.get("shape", "hexagon")).lower()
        if shape not in {"hexagon", "organic"}:
            shape = "hexagon"
        surface_mode, surface_targets, surface_shares = self._rocky_surface_targets(
            cfg,
            zone_specs,
            radius_min,
            radius_max,
        )
        quantity_targets: dict[str, int] = {}
        for name, _family, _enabled in zone_specs:
            entry = cfg.get(name, {})
            entry = entry if isinstance(entry, Mapping) else {}
            fallback_mean = self._custom_global_resource_mean(name, UPGRADED_RESOURCE_MEAN)
            quantity_targets[name] = self._start_bonus_int(
                entry.get("average_quantity", fallback_mean),
                RESOURCE_MINIMUM,
                RESOURCE_MAXIMUM,
                fallback_mean,
            )

        metadata: dict[str, object] = {
            "enabled": bool(bonus_enabled and any(item[2] for item in zone_specs)),
            "per_player": True,
            "distance_from_border": int(cfg.get("distance_from_border", 0)),
            "force_extended_radius": bool(force_extended),
            **({"center_extension_limit": FORCED_CENTER_EXTENSION, "tower_clear_hex": int(self.profile["starts"].get("editor_object_clear_hex", 14))} if force_extended else {}),
            "extended_radius_used": False,
            "center_hex": int(cfg.get("center_hex", self.profile["starts"].get("initial_territory_hex_radius", 34))),
            "radius_min": radius_min,
            "radius_max": radius_max,
            "shape": shape,
            "surface_mode": surface_mode,
            "surface_allocation": "global_deposit_shares" if surface_mode == "proportional" else surface_mode,
            "surface_targets": dict(surface_targets),
            "surface_shares": dict(surface_shares),
            "transition_rings": int(cfg.get("transition_rings", 2)),
            "zones_requested_per_player": sum(item[2] for item in zone_specs) if package_enabled else 0,
            "zones_requested": (sum(item[2] for item in zone_specs) * len(state.starts)) if package_enabled else 0,
            "zones": [],
            "per_player": [],
            "shortfalls": [],
            "placed_zones": 0,
            "placed_core_cells": 0,
            "reserved_cells": 0,
            "quantity_mean_source": str(cfg.get("quantity_mean_source", "upgraded_global")),
            "quantity_mean_target": int(UPGRADED_RESOURCE_MEAN),
            "quantity_mean_targets": {
                name: quantity_targets[name]
                for name in ("coal", "iron", "gold")
            },
            "outside_global_quota": bool(self.profile.get("start_bonus", {}).get("outside_global_quota", True)),
            "height_unchanged": True,
            "outside_technical_zone": True,
        }
        if not bonus_enabled:
            metadata["enabled"] = False
            state.metadata["upgraded_start_rocky_minerals"] = metadata
            self._start_bonus_rocky_records = []
            self.log("resources.upgraded_start_rocky_minerals", "disabled by Custom profile")
            return

        desired = int(metadata["center_hex"]) + int(metadata["distance_from_border"])
        self._start_bonus_rocky_records = []

        def clear(points: list[tuple[int, int]]) -> bool:
            return bool(points) and all(
                0 <= x < self.side
                and 0 <= y < self.side
                and grass_support[y, x]
                and not technical[y, x]
                and not reservation[y, x]
                and objects[y, x] == 0
                and resources[y, x] == 0
                for x, y in points
            )

        def legal_halo(points: list[tuple[int, int]], envelope: set[tuple[int, int]]) -> bool:
            for x, y in points:
                for dx, dy in HEX6:
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < self.side and 0 <= yy < self.side):
                        return False
                    if (xx, yy) in envelope:
                        continue
                    if (
                        not grass_support[yy, xx]
                        or technical[yy, xx]
                        or reservation[yy, xx]
                        or objects[yy, xx] != 0
                        or resources[yy, xx] != 0
                    ):
                        return False
            return True

        for player, (sx, sy) in enumerate(state.starts, start=1):
            player_record: dict[str, object] = {
                "player": player,
                "requested_zones": int(metadata["zones_requested_per_player"]),
                "placed_zones": 0,
                "zones": [],
                "shortfalls": [],
            }
            centres = self._bonus_center_candidates(
                state,
                int(sx),
                int(sy),
                desired,
                terrain,
                technical | reservation,
                pr,
                support_mask=grass_support,
                force_extended=force_extended,
            )
            for name, family, enabled in zone_specs:
                if not enabled:
                    continue
                radii = list(range(radius_min, radius_max + 1))
                pr.shuffle(radii)
                placed = None
                relative_cache: dict[tuple[str, int], list[tuple[int, int]]] = {}
                if shape == "hexagon" and surface_mode == "equal":
                    candidate_iter = (
                        (radius, cx, cy, None)
                        for radius, cx, cy in radius_center_pairs(
                            centres, radii, int(sx), int(sy), desired, force_extended,
                        )
                    )
                elif surface_mode == "equal":
                    candidate_iter = (
                        (radius, cx, cy, self._full_hex_disc_area(radius))
                        for radius, cx, cy in radius_center_pairs(
                            centres, radii, int(sx), int(sy), desired, force_extended,
                        )
                    )
                else:
                    target = int(surface_targets.get(name, self._full_hex_disc_area(
                        int(round((radius_min + radius_max) / 2.0))
                    )))
                    candidate_iter = (
                        (0, cx, cy, target)
                        for cx, cy in centres
                    )
                for radius, cx, cy, requested_core_cells in candidate_iter:
                    if requested_core_cells is None:
                        core = _hex_points(self.side, cx, cy, radius)
                        inner = _hex_points(self.side, cx, cy, radius + 1, exact=radius + 1)
                        outer = _hex_points(self.side, cx, cy, radius + 2, exact=radius + 2)
                        if len(core) != self._full_hex_disc_area(radius):
                            continue
                        if len(inner) != self._full_hex_ring_area(radius):
                            continue
                        if len(outer) != self._full_hex_ring_area(radius + 1):
                            continue
                    else:
                        cache_key = (shape, int(requested_core_cells))
                        relative = relative_cache.get(cache_key)
                        if relative is None:
                            relative = self._rocky_relative_shape(
                                shape,
                                surface_mode,
                                int(requested_core_cells),
                                int(radius),
                                pr,
                            )
                            relative_cache[cache_key] = relative
                        core = [(cx + dx, cy + dy) for dx, dy in relative]
                        if len(core) != int(requested_core_cells) or len(set(core)) != len(core):
                            continue
                        if not all(0 <= x < self.side and 0 <= y < self.side for x, y in core):
                            continue
                        inner_offsets, outer_offsets = transition_rings(relative, 2)
                        inner = [(cx + dx, cy + dy) for dx, dy in inner_offsets]
                        outer = [(cx + dx, cy + dy) for dx, dy in outer_offsets]
                        radius = max(
                            1,
                            max((hex_distance(0, 0, dx, dy) for dx, dy in relative), default=1),
                        )
                    envelope = core + inner + outer
                    if not clear(envelope):
                        continue
                    envelope_set = set(envelope)
                    if not legal_halo(outer, envelope_set):
                        continue
                    # The order is important: 17 is the outer ring, 33 is
                    # the inner transition, and 32 is the mineral core.
                    for x, y in outer:
                        terrain[y, x] = ROCK_TRANS_1
                    for x, y in inner:
                        terrain[y, x] = ROCK_TRANS_2
                    for x, y in core:
                        terrain[y, x] = ROCKY
                    halo = {
                        (x + dx, y + dy)
                        for x, y in outer
                        for dx, dy in HEX6
                        if (x + dx, y + dy) not in envelope_set
                    }
                    for x, y in envelope:
                        reservation[y, x] = True
                    halo_points = list(halo)
                    for x, y in halo_points:
                        reservation[y, x] = True
                    self._start_bonus_rocky_records.append({
                        "player": player,
                        "resource": name,
                        "family": family,
                        "center_x": int(cx),
                        "center_y": int(cy),
                        "radius": int(radius),
                        "shape": shape,
                        "surface_mode": surface_mode,
                        "requested_core_cells": int(requested_core_cells or len(core)),
                        "quantity_mean": int(quantity_targets.get(name, UPGRADED_RESOURCE_MEAN)),
                        "core_points": core,
                        "inner_points": inner,
                        "outer_points": outer,
                        "halo_points": list(halo),
                    })
                    placed = self._start_bonus_rocky_records[-1]
                    break
                if placed is None:
                    shortfall = {
                        "player": player,
                        "resource": name,
                        "reason": "no_complete_legal_zone",
                        "requested_radius": [radius_min, radius_max],
                        "surface_mode": surface_mode,
                        "requested_core_cells": int(surface_targets.get(name, 0)),
                    }
                    player_record["shortfalls"].append(shortfall)
                    metadata["shortfalls"].append(shortfall)
                    continue
                zone_view = {
                    "player": player,
                    "resource": name,
                    "family": int(family),
                    "center_x": int(placed["center_x"]),
                    "center_y": int(placed["center_y"]),
                    "radius": int(placed["radius"]),
                    "shape": str(placed.get("shape", shape)),
                    "surface_mode": str(placed.get("surface_mode", surface_mode)),
                    "core_cells": len(placed["core_points"]),
                    "requested_core_cells": int(placed.get("requested_core_cells", len(placed["core_points"]))),
                    "core_points": [list(point) for point in placed["core_points"]],
                    "quantity_mean_target": int(placed.get("quantity_mean", quantity_targets.get(name, UPGRADED_RESOURCE_MEAN))),
                    "transition_cells": len(placed["inner_points"]) + len(placed["outer_points"]),
                    "reserved_cells": len(placed["core_points"]) + len(placed["inner_points"]) + len(placed["outer_points"]) + len(placed["halo_points"]),
                }
                player_record["zones"].append(zone_view)
                metadata["zones"].append(zone_view)
                metadata["extended_radius_used"] = bool(
                    metadata["extended_radius_used"]
                    or hex_distance(int(sx), int(sy), int(cx), int(cy))
                    > int(metadata["center_hex"]) + int(metadata["distance_from_border"]) + 2
                )
                player_record["placed_zones"] = int(player_record["placed_zones"]) + 1
                metadata["placed_zones"] = int(metadata["placed_zones"]) + 1
                metadata["placed_core_cells"] = int(metadata["placed_core_cells"]) + len(placed["core_points"])
                metadata["reserved_cells"] = int(metadata["reserved_cells"]) + zone_view["reserved_cells"]
            metadata["per_player"].append(player_record)

        state.metadata["upgraded_start_rocky_minerals"] = metadata
        self.log("resources.upgraded_start_rocky_minerals", str(metadata))

    def _place_start_rocky_resources(self, state, rng: np.random.Generator) -> None:
        """Fill the already-reserved rocky cores after global minerals."""

        metadata = state.metadata.get("upgraded_start_rocky_minerals", {})
        if not isinstance(metadata, dict):
            metadata = {}
        bonus_targets: dict[str, int] = {}
        quantity_total = 0
        family_names = {0x10: "coal", 0x20: "iron", 0x30: "gold", 0x40: "gems", 0x50: "sulfur"}
        for record in self._start_bonus_rocky_records:
            core = list(record["core_points"])
            family = int(record["family"])
            fallback_mean = self._custom_global_resource_mean(
                family_names.get(family, "coal"),
                UPGRADED_RESOURCE_MEAN,
            )
            quantity_mean = self._start_bonus_int(
                record.get("quantity_mean", fallback_mean),
                RESOURCE_MINIMUM,
                RESOURCE_MAXIMUM,
                fallback_mean,
            )
            quantities = _bounded_quantities(len(core), quantity_mean, rng)
            for (x, y), quantity in zip(core, quantities):
                state.resources[y, x] = family | int(quantity)
            key = f"{family:02x}"
            bonus_targets[key] = bonus_targets.get(key, 0) + len(core)
            quantity_total += int(quantities.sum())
            for zone in metadata.get("zones", []):
                if (
                    zone.get("player") == record["player"]
                    and zone.get("resource") == record["resource"]
                    and zone.get("center_x") == record["center_x"]
                    and zone.get("center_y") == record["center_y"]
                ):
                    zone["resource_cells"] = len(core)
                    zone["resource_stock"] = int(quantities.sum())
                    zone["resource_mean"] = float(np.mean(quantities)) if len(quantities) else 0.0
                    break

        previous = state.metadata.get("upgraded_mineral_targets", {})
        previous = previous if isinstance(previous, dict) else {}
        global_targets: dict[str, int] = {}
        combined: dict[str, int] = {}
        for family, name in family_names.items():
            key = f"{family:02x}"
            base = int(previous.get(key, previous.get(name, 0)))
            global_targets[key] = base
            combined[key] = base + int(bonus_targets.get(key, 0))
        state.metadata["upgraded_mineral_global_targets"] = global_targets
        state.metadata["upgraded_mineral_targets"] = combined
        minerals = state.metadata.get("upgraded_minerals", {})
        if isinstance(minerals, dict):
            minerals["global_targets"] = global_targets
            minerals["start_bonus_targets"] = bonus_targets
            minerals["targets"] = combined
            minerals["start_bonus_cells"] = int(sum(bonus_targets.values()))
            minerals["start_bonus_stock"] = quantity_total
            minerals["global_quota_excludes_start_bonus"] = True
        metadata["start_bonus_targets"] = bonus_targets
        metadata["start_bonus_cells"] = int(sum(bonus_targets.values()))
        metadata["start_bonus_stock"] = quantity_total
        metadata["global_quota_excludes_start_bonus"] = True
        state.metadata["upgraded_start_rocky_minerals"] = metadata
        self.log("resources.upgraded_start_rocky_minerals_fill", f"cells={sum(bonus_targets.values())}")

    def _place_start_lake_fish_river(self, state, pr: random.Random) -> None:
        """Draw independent start lakes and one legal river target per lake."""

        cfg = self._custom_start_bonus_config("lake_fish_river")
        package_enabled = self._start_package_enabled("start_lake_fish_river")
        bonus_enabled = package_enabled and bool(cfg.get("enabled", True))
        terrain, objects, resources = state.terrain, state.objects, state.resources
        reservation = self._start_bonus_reservation
        if reservation is None:
            reservation = np.zeros_like(terrain, dtype=bool)
            self._start_bonus_reservation = reservation
        self._start_bonus_water = np.zeros_like(terrain, dtype=bool)
        # A lake and its whole river mouth are a large early-game footprint.
        # Keep the native technical zone and the editor water/object clearance
        # around the tower in every mode; forced mode only changes how far the
        # centre search may extend, never how close the footprint may start.
        tower_clear_hex = max(
            int(self.profile["starts"].get("editor_object_clear_hex", 14)),
            int(self.profile["starts"].get("editor_water_clear_hex", 20)),
        )
        technical = self._core_mask(
            state,
            max(int(self.profile["starts"]["technical_clear_hex"]), tower_clear_hex),
        )
        grass_support = self._grass_object_support_mask(terrain)
        force_extended = self._force_extended_start_bonus()
        raw_min = self._start_bonus_int(
            cfg.get("radius_min", 7),
            START_BONUS_RADIUS_MIN,
            START_BONUS_RADIUS_MAX,
            7,
        ) if bonus_enabled else 0
        raw_max = self._start_bonus_int(
            cfg.get("radius_max", 9),
            raw_min or START_BONUS_RADIUS_MIN,
            START_BONUS_RADIUS_MAX,
            max(raw_min, 9),
        ) if bonus_enabled else 0
        radius_max = max(0, raw_max)
        radius_min = max(1, min(raw_min, radius_max)) if radius_max else 0
        threshold = self._start_bonus_int(
            cfg.get("water_proximity_from_territory_border", 150),
            START_BONUS_WATER_PROXIMITY_MIN,
            START_BONUS_WATER_PROXIMITY_MAX,
            150,
        )
        territory_radius = int(cfg.get("center_hex", self.profile["starts"].get("initial_territory_hex_radius", 34)))
        distance_from_border = self._start_bonus_int(
            cfg.get("distance_from_border", 0),
            START_BONUS_DISTANCE_MIN,
            START_BONUS_DISTANCE_MAX,
            0,
        )
        river_target = self._start_bonus_int(
            cfg.get("river_target_per_lake", cfg.get("river_target", 1)),
            START_BONUS_RIVER_TARGET_MIN,
            START_BONUS_RIVER_TARGET_MAX,
            1,
        )
        fish_fill = self._start_bonus_float(
            cfg.get("fish_fill_percent", 50.0),
            START_BONUS_FISH_FILL_MIN,
            START_BONUS_FISH_FILL_MAX,
            50.0,
        )
        fish_mean = self._custom_global_resource_mean(
            "fish",
            self._start_bonus_int(
                cfg.get("fish_average_quantity", UPGRADED_RESOURCE_MEAN),
                RESOURCE_MINIMUM,
                RESOURCE_MAXIMUM,
                UPGRADED_RESOURCE_MEAN,
            ),
        )
        shape = str(cfg.get("shape", "native")).lower()
        if shape not in START_LAKE_SHAPES:
            shape = "native"
        native_water = np.isin(terrain, WATER_IDS)
        native_river = np.isin(terrain, RIVER_IDS)
        native_shore = terrain == SHORE
        waterish = native_water | native_shore | native_river
        water_distance = distance_from(waterish) if waterish.any() else None
        # Bonus rivers are not routed towards this mask.  It is retained only
        # for the existing proximity control, which decides whether the lake
        # itself may be placed near the native hydrology.
        interior = np.ones_like(terrain, dtype=bool)
        if self.side:
            interior[[0, -1], :] = False
            interior[:, [0, -1]] = False
        # Native rivers only carve eligible grass.  The old bonus route also
        # required all six neighbours to be in a broad allow-list, which made
        # it stop at arbitrary terrain pockets and produced straight,
        # shortest-path-looking traces.  Keep the complete collision mask but
        # let the native-style tracer make the local topology decisions.
        safe_route = (
            grass_support
            & ~technical
            & ~reservation
            & (objects == 0)
            & (resources == 0)
            & interior
            & ~native_water
            & ~native_river
            & ~native_shore
        )
        # Native river markers are an internal working field, not part of the
        # serialized MapState.  Keep one for the bonus pass so several stems
        # use the same native spacing/backtracking rules without touching the
        # already-generated river systems.
        bonus_marker = np.zeros_like(terrain, dtype=np.uint8)
        metadata: dict[str, object] = {
            "enabled": bool(bonus_enabled and radius_max > 0),
            "per_player": True,
            "distance_from_border": distance_from_border,
            "force_extended_radius": bool(force_extended),
            "tower_clear_hex": tower_clear_hex,
            **({"center_extension_limit": FORCED_CENTER_EXTENSION} if force_extended else {}),
            "extended_radius_used": False,
            "center_hex": territory_radius,
            "radius_min": radius_min,
            "radius_max": radius_max,
            "shape": shape,
            "water_proximity_from_territory_border": threshold,
            "river_target_per_lake": river_target,
            "require_river": bool(cfg.get("require_river", True)),
            "river_algorithm": "native_single_system",
            "river_global_target_search": False,
            "river_normal_id": int(RIVER_IDS[0]),
            "fish_fill_percent": fish_fill,
            "fish_average_quantity": fish_mean,
            "lakes_requested": len(state.starts) if bonus_enabled and radius_max > 0 else 0,
            "lakes_placed": 0,
            "rivers_requested": (len(state.starts) * river_target) if bonus_enabled and radius_max > 0 else 0,
            "rivers_placed": 0,
            "fish_cells": 0,
            "fish_stock": 0,
            "per_player": [],
            "shortfalls": [],
            "outside_global_quota": bool(self.profile.get("start_bonus", {}).get("outside_global_quota", True)),
            "native_water_protected": True,
            "native_rivers_protected": True,
            "water_proximity_filter_enabled": bool(threshold > 0),
            "candidate_attempts": 0,
            "candidate_accepts": 0,
            "rejection_totals": {key: 0 for key in _LAKE_REJECTION_KEYS},
        }
        self._start_bonus_lake_records = []
        if not bonus_enabled:
            metadata["enabled"] = False
            state.metadata["upgraded_start_lake_fish_river"] = metadata
            self.log("hydrology.upgraded_start_lake_fish_river", "disabled by Custom profile")
            return
        if radius_max <= 0:
            metadata["enabled"] = False

        desired = territory_radius + distance_from_border

        def add_rejection(player_record: dict[str, object], reason: str) -> None:
            """Increment one compact per-player and global diagnostic counter."""

            if reason not in _LAKE_REJECTION_KEYS:
                return
            counts = player_record["rejection_counts"]
            assert isinstance(counts, dict)
            counts[reason] = int(counts.get(reason, 0)) + 1
            totals = metadata["rejection_totals"]
            assert isinstance(totals, dict)
            totals[reason] = int(totals.get(reason, 0)) + 1

        def add_attempt(player_record: dict[str, object]) -> None:
            player_record["candidate_attempts"] = int(player_record["candidate_attempts"]) + 1
            metadata["candidate_attempts"] = int(metadata["candidate_attempts"]) + 1

        def add_accept(player_record: dict[str, object]) -> None:
            player_record["candidate_accepts"] = int(player_record["candidate_accepts"]) + 1
            metadata["candidate_accepts"] = int(metadata["candidate_accepts"]) + 1

        def clear_failure(points: list[tuple[int, int]]) -> str | None:
            """Return the first collision class, preserving the old bool test."""

            if not points:
                return "footprint_out_of_bounds"
            for x, y in points:
                if not (0 <= x < self.side and 0 <= y < self.side):
                    return "footprint_out_of_bounds"
                if not grass_support[y, x]:
                    return "footprint_non_grass"
                if technical[y, x]:
                    return "footprint_technical_clearance"
                if reservation[y, x]:
                    return "footprint_reserved"
                if objects[y, x] != 0:
                    return "footprint_object_collision"
                if resources[y, x] != 0:
                    return "footprint_resource_collision"
            return None

        def shore_boundary_legal(
            shore_points: list[tuple[int, int]],
            envelope: set[tuple[int, int]],
        ) -> bool:
            """Keep a new shore from touching an incompatible transition."""

            for x, y in shore_points:
                for dx, dy in HEX6:
                    xx, yy = x + dx, y + dy
                    if not (0 <= xx < self.side and 0 <= yy < self.side):
                        return False
                    if (xx, yy) in envelope:
                        continue
                    allowed = TERRAIN_TRANSITION_ALLOWED.get(int(terrain[yy, xx]))
                    if allowed is not None and SHORE not in allowed:
                        return False
            return True

        for player, (sx, sy) in enumerate(state.starts, start=1):
            player_record: dict[str, object] = {
                "player": player,
                "placed": False,
                "skipped_reason": None,
                "candidate_attempts": 0,
                "candidate_accepts": 0,
                "rejection_counts": {key: 0 for key in _LAKE_REJECTION_KEYS},
            }
            if radius_max <= 0:
                player_record["skipped_reason"] = "non_positive_radius"
                add_rejection(player_record, "no_center_candidates")
                metadata["shortfalls"].append({"player": player, "reason": "non_positive_radius"})
                metadata["per_player"].append(player_record)
                continue
            if water_distance is None:
                border_distance = 32767
            else:
                border_distance = int(water_distance[int(sy), int(sx)]) - territory_radius
            player_record["nearest_water_from_border"] = max(0, border_distance)
            # Zero explicitly disables the native-water proximity filter.  A
            # positive value is the actual border-distance exclusion scale.
            if water_distance is not None and threshold > 0 and border_distance <= threshold:
                player_record["skipped_reason"] = "existing_water_within_proximity_threshold"
                add_rejection(player_record, "water_proximity")
                metadata["per_player"].append(player_record)
                continue
            centres = self._bonus_center_candidates(
                state,
                int(sx),
                int(sy),
                desired,
                terrain,
                technical | reservation,
                pr,
                support_mask=grass_support,
                force_extended=force_extended,
            )
            if not centres:
                add_rejection(player_record, "no_center_candidates")
            radii = list(range(radius_min, radius_max + 1))
            pr.shuffle(radii)
            placed = None
            for radius, cx, cy in radius_center_pairs(
                centres, radii, int(sx), int(sy), desired, force_extended,
            ):
                add_attempt(player_record)
                if shape == "native":
                    offsets = native_lake_offsets(radius, pr)
                    core = [
                        (int(cx + dx), int(cy + dy))
                        for dx, dy in offsets
                    ]
                    inner_shore_offsets, outer_shore_offsets = transition_rings(offsets, depth=2)
                    inner_shore = [
                        (int(cx + dx), int(cy + dy))
                        for dx, dy in inner_shore_offsets
                    ]
                    outer_shore = [
                        (int(cx + dx), int(cy + dy))
                        for dx, dy in outer_shore_offsets
                    ]
                    shore = inner_shore + outer_shore
                else:
                    core = _hex_points(self.side, cx, cy, radius)
                    inner_shore = _hex_points(self.side, cx, cy, radius + 1, exact=radius + 1)
                    outer_shore = _hex_points(self.side, cx, cy, radius + 2, exact=radius + 2)
                    shore = inner_shore + outer_shore
                    if len(core) != self._full_hex_disc_area(radius):
                        add_rejection(player_record, "shape_invalid")
                        continue
                    if len(inner_shore) != self._full_hex_ring_area(radius):
                        add_rejection(player_record, "shape_invalid")
                        continue
                    if len(outer_shore) != self._full_hex_ring_area(radius + 1):
                        add_rejection(player_record, "shape_invalid")
                        continue
                clear_reason = clear_failure(core + shore)
                if clear_reason is not None:
                    add_rejection(player_record, clear_reason)
                    continue

                # The native river starts on a raw Water cell and grows into
                # Grass.  Build the lake core first, without painting its
                # shoreline yet, so the native first-step filter can see the
                # same Water→Grass mouth that it sees in the main pass.
                core_set = set(core)
                depths = water_depths(core)
                working_terrain = terrain.copy()
                for x, y in core:
                    working_terrain[y, x] = int(depths.get((x, y), 0))
                # The native 9x9 candidate filter counts raw Water
                # cells, not the later Shore IDs.  Treat the first ring as
                # temporary raw water while selecting the mouth; it is
                # converted back to Shore everywhere the chosen river does
                # not pass.  This keeps small (radius-2) bonus lakes eligible
                # without weakening the native filter itself.
                for x, y in inner_shore:
                    working_terrain[y, x] = 0
                working_marker = bonus_marker.copy()
                # The native candidate itself is converted to River96.  Keep
                # the bonus lake's Water core intact by using a raw-Water
                # mouth on its first transition ring, exactly where the
                # normal structural pass would expose the embouchure.
                boundary_candidates = [
                    (x, y)
                    for x, y in inner_shore
                    if any(
                        0 <= x + dx < self.side
                        and 0 <= y + dy < self.side
                        and safe_route[y + dy, x + dx]
                        for dx, dy in HEX6
                    )
                ]
                pr.shuffle(boundary_candidates)
                if not boundary_candidates and bool(cfg.get("require_river", True)):
                    add_rejection(player_record, "no_legal_river_mouth")
                    continue
                routes: list[list[tuple[int, int]]] = []
                for mouth in boundary_candidates:
                    if len(routes) >= river_target:
                        break
                    trial_terrain = working_terrain.copy()
                    trial_marker = working_marker.copy()
                    trial_terrain[mouth[1], mouth[0]] = 0
                    route = grow_native_bonus_river(
                        trial_terrain,
                        state.height,
                        mouth,
                        marker=trial_marker,
                        allowed=safe_route,
                    )
                    if route is None:
                        continue
                    route_set = set(route)
                    if any(
                        (x, y) not in core_set
                        and (
                            not safe_route[y, x]
                            or native_river[y, x]
                            or native_water[y, x]
                            or native_shore[y, x]
                        )
                        for x, y in route_set
                    ):
                        continue
                    working_terrain = trial_terrain
                    working_marker = trial_marker
                    routes.append(route)
                if not routes and bool(cfg.get("require_river", True)):
                    add_rejection(player_record, "river_trace_failed")
                    continue
                path = [point for route in routes for point in route]
                path_set = set(path)

                # A native river opens the shoreline at its mouth.  Preserve
                # the two-ring lake treatment everywhere else, but do not
                # repaint any ring cell that the native route occupies.
                painted_inner_shore = [point for point in inner_shore if point not in path_set]
                painted_outer_shore = [point for point in outer_shore if point not in path_set]
                painted_shore = painted_inner_shore + painted_outer_shore
                if not shore_boundary_legal(
                    painted_shore,
                    core_set | set(painted_shore) | path_set,
                ):
                    add_rejection(player_record, "shore_transition_invalid")
                    continue

                for x, y in core:
                    terrain[y, x] = int(depths.get((x, y), 0))
                    state.height[y, x] = 0
                for x, y in painted_shore:
                    terrain[y, x] = SHORE
                # A normal native system uses River96 throughout.  The
                # alternating 96/97/98/99 pattern belonged only to the old
                # synthetic route and never represented native width.
                for x, y in path_set:
                    terrain[y, x] = RIVER_IDS[0]
                bonus_marker[:] = working_marker
                all_reserved = core + painted_shore + path
                for x, y in all_reserved:
                    reservation[y, x] = True
                for x, y in core:
                    self._start_bonus_water[y, x] = True
                placed = {
                    "player": player,
                    "center_x": int(cx),
                    "center_y": int(cy),
                    "radius": int(radius),
                    "shape": shape,
                    "core_points": core,
                    "shore_points": shore,
                    "painted_shore_points": painted_shore,
                    "shore_inner_points": inner_shore,
                    "shore_outer_points": outer_shore,
                    "shore_rings": 2,
                    "river_points": path,
                    "river_routes": routes,
                    "nearest_water_from_border": max(0, border_distance),
                }
                add_accept(player_record)
                break
            if placed is None:
                player_record["skipped_reason"] = "no_complete_lake_with_legal_river"
                metadata["shortfalls"].append({"player": player, "reason": player_record["skipped_reason"]})
                metadata["per_player"].append(player_record)
                continue
            self._start_bonus_lake_records.append(placed)
            metadata["extended_radius_used"] = bool(
                metadata["extended_radius_used"]
                or hex_distance(int(sx), int(sy), int(placed["center_x"]), int(placed["center_y"]))
                > desired + 2
            )
            lake_view = {
                "player": player,
                "center_x": int(placed["center_x"]),
                "center_y": int(placed["center_y"]),
                "radius": int(placed["radius"]),
                "shape": shape,
                "core_cells": len(placed["core_points"]),
                "shore_cells": len(placed["shore_points"]),
                "shore_rings": 2,
                "river_cells": len(placed["river_points"]),
                "river_count": len(placed["river_routes"]),
                "nearest_water_from_border": int(placed["nearest_water_from_border"]),
            }
            player_record.update({"placed": True, "lake": lake_view})
            metadata["per_player"].append(player_record)
            metadata["lakes_placed"] = int(metadata["lakes_placed"]) + 1
            metadata["rivers_placed"] = int(metadata["rivers_placed"]) + len(placed["river_routes"])
        state.metadata["upgraded_start_lake_fish_river"] = metadata
        self.log("hydrology.upgraded_start_lake_fish_river", str(metadata))

    def _place_start_lake_fish(self, state, rng: np.random.Generator) -> None:
        """Fill the bonus lake cores after global fish selection."""

        metadata = state.metadata.get("upgraded_start_lake_fish_river", {})
        if not isinstance(metadata, dict):
            metadata = {}
        total_cells = 0
        total_stock = 0
        for record in self._start_bonus_lake_records:
            core = [
                (x, y)
                for x, y in record["core_points"]
                if state.terrain[y, x] in WATER_IDS and not np.isin(state.terrain[y, x], RIVER_IDS)
            ]
            target = min(len(core), max(0, int(round(len(core) * float(metadata.get("fish_fill_percent", 50.0)) / 100.0))))
            if target:
                chosen_indices = rng.choice(len(core), target, replace=False)
                chosen = [core[int(index)] for index in chosen_indices]
            else:
                chosen = []
            quantities = _bounded_quantities(
                len(chosen),
                int(metadata.get("fish_average_quantity", UPGRADED_RESOURCE_MEAN)),
                rng,
            )
            for (x, y), quantity in zip(chosen, quantities):
                state.resources[y, x] = int(quantity)
            fish_cells = len(chosen)
            fish_stock = int(quantities.sum())
            total_cells += fish_cells
            total_stock += fish_stock
            for row in metadata.get("per_player", []):
                lake = row.get("lake") if isinstance(row, dict) else None
                if isinstance(lake, dict) and lake.get("center_x") == record["center_x"] and lake.get("center_y") == record["center_y"]:
                    lake["fish_cells"] = fish_cells
                    lake["fish_stock"] = fish_stock
                    lake["fish_mean"] = float(np.mean(quantities)) if len(quantities) else 0.0
                    break
        metadata["fish_cells"] = total_cells
        metadata["fish_stock"] = total_stock
        metadata["global_quota_excludes_start_bonus"] = True
        state.metadata["upgraded_start_lake_fish_river"] = metadata
        fish = state.metadata.get("upgraded_fish", {})
        global_target = int(state.metadata.get("upgraded_fish_target", 0))
        if isinstance(fish, dict):
            fish["global_target_cells"] = global_target
            fish["start_bonus_cells"] = total_cells
            fish["start_bonus_stock"] = total_stock
            fish["target_cells"] = global_target + total_cells
            fish["cells"] = int(np.count_nonzero(
                np.isin(state.terrain, WATER_IDS)
                & ((state.resources & 0xF0) == 0)
                & ((state.resources & 0x0F) > 0)
            ))
            fish["global_quota_excludes_start_bonus"] = True
        state.metadata["upgraded_fish_global_target"] = global_target
        state.metadata["upgraded_fish_target"] = global_target + total_cells
        self.log("resources.upgraded_start_lake_fish", f"cells={total_cells}")

    def generate(self, state, rng: np.random.Generator, pr: random.Random) -> dict[str, object]:
        self.side = state.side
        self._stage_log.clear()
        self._start_bonus_reservation = np.zeros((state.side, state.side), dtype=bool)
        self._start_bonus_swamp_mask = np.zeros((state.side, state.side), dtype=bool)
        self._start_bonus_water = np.zeros((state.side, state.side), dtype=bool)
        self._start_bonus_rocky_records = []
        self._start_bonus_lake_records = []
        self._prioritized_start_stone_state = None
        self._start_bonus_object_clearance = None
        self._object_hitbox_enforced = False
        self._object_collision_mask = None
        self._place_start_mini_swamps(state, pr)
        self._place_start_rocky_minerals(state, pr)
        self._place_start_lake_fish_river(state, pr)
        self._generate_minerals(state, rng, pr)
        self._place_start_rocky_resources(state, rng)
        self._generate_fish(state, rng)
        self._place_start_lake_fish(state, rng)
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

    def generate_start_bonuses(
        self,
        state,
        rng: np.random.Generator,
        pr: random.Random,
        occupied: np.ndarray | None = None,
    ) -> dict[str, object]:
        """Apply only terrain/resource start layers to an existing map.

        Custom Legacy uses this compatibility entry point after its starts are
        known.  Every bonus routine writes its terrain/resources immediately;
        the internal mask only records cells already occupied by those
        writes, so no later pass has to clear a provisional area.
        """

        self.side = state.side
        self._stage_log.clear()
        baseline = (
            np.asarray(occupied, dtype=bool).copy()
            if occupied is not None
            else np.zeros((state.side, state.side), dtype=bool)
        )
        self._start_bonus_reservation = baseline.copy()
        self._start_bonus_swamp_mask = np.zeros((state.side, state.side), dtype=bool)
        self._start_bonus_water = np.zeros((state.side, state.side), dtype=bool)
        self._start_bonus_rocky_records = []
        self._start_bonus_lake_records = []
        self._prioritized_start_stone_state = None
        self._start_bonus_object_clearance = None
        self._object_hitbox_enforced = False
        self._object_collision_mask = None
        self._place_start_mini_swamps(state, pr, rebuild_transitions=False)
        self._place_start_rocky_minerals(state, pr)
        self._place_start_lake_fish_river(state, pr)
        self._rebuild_swamp_transitions(state)
        self._place_start_rocky_resources(state, rng)
        self._place_start_lake_fish(state, rng)
        bonus_occupied = self._start_bonus_reservation & ~baseline
        state.metadata["custom_start_bonus_occupied_cells"] = int(
            bonus_occupied.sum()
        )
        return {
            "mini_swamp": state.metadata.get("upgraded_start_mini_swamps", {}),
            "rocky_minerals": state.metadata.get("upgraded_start_rocky_minerals", {}),
            "lake_fish_river": state.metadata.get("upgraded_start_lake_fish_river", {}),
            "occupied_cells": int(bonus_occupied.sum()),
        }

    def begin_prioritized_terrain_bonuses(
        self,
        state,
        pr: random.Random,
    ) -> dict[str, object]:
        """Paint start terrain bonuses before the global terrain families.

        This is used only by the explicit start-package route.  The normal
        generator keeps the native terrain/content pass together, so this
        method must never be reached for a map without an active bonus.
        """

        self.side = state.side
        self._stage_log.clear()
        self._start_bonus_reservation = np.zeros((state.side, state.side), dtype=bool)
        self._start_bonus_swamp_mask = np.zeros((state.side, state.side), dtype=bool)
        self._start_bonus_water = np.zeros((state.side, state.side), dtype=bool)
        self._start_bonus_rocky_records = []
        self._start_bonus_lake_records = []
        self._prioritized_start_stone_state = None
        self._start_bonus_object_clearance = np.zeros((state.side, state.side), dtype=bool)
        self._object_hitbox_enforced = True
        self._object_collision_mask = np.zeros((state.side, state.side), dtype=bool)
        self._place_start_mini_swamps(state, pr, rebuild_transitions=False)
        self._place_start_rocky_minerals(state, pr)
        self._place_start_lake_fish_river(state, pr)
        self._rebuild_swamp_transitions(state)
        return {
            "mini_swamp": state.metadata.get("upgraded_start_mini_swamps", {}),
            "rocky_minerals": state.metadata.get("upgraded_start_rocky_minerals", {}),
            "lake_fish_river": state.metadata.get("upgraded_start_lake_fish_river", {}),
            "protected_mask": self._start_bonus_reservation.copy(),
        }

    def apply_prioritized_start_resources(
        self,
        state,
        rng: np.random.Generator,
    ) -> dict[str, object]:
        """Add start resource quantities after the global resource layer."""

        self._place_start_rocky_resources(state, rng)
        return {
            "rocky_minerals": state.metadata.get("upgraded_start_rocky_minerals", {}),
            "lake_fish_river": state.metadata.get("upgraded_start_lake_fish_river", {}),
        }

    def apply_prioritized_start_fish(
        self,
        state,
        rng: np.random.Generator,
    ) -> dict[str, object]:
        """Fill start-lake fish after the global fish pass has completed."""

        self._place_start_lake_fish(state, rng)
        return {
            "lake_fish_river": state.metadata.get("upgraded_start_lake_fish_river", {}),
        }

    def generate_prioritized(
        self,
        state,
        rng: np.random.Generator,
        pr: random.Random,
    ) -> dict[str, object]:
        """Finish a staged start-package generation after terrain is resumed."""

        self.side = state.side
        if self._start_bonus_reservation is None:
            self.begin_prioritized_terrain_bonuses(state, pr)
        # Start terrain has already been written.  Object collision starts
        # from the actual layer and grows only when a later object is written.
        self._object_hitbox_enforced = True
        self._refresh_object_collision_mask(state)
        self._generate_minerals(state, rng, pr)
        self.apply_prioritized_start_resources(state, rng)
        self._generate_fish(state, rng)
        self._place_start_lake_fish(state, rng)
        self._place_building_stones(state, rng, pr, phase="start")
        self._place_trees(state, rng, pr)
        self._place_decorations(state, rng, pr)
        self._place_building_stones(state, rng, pr, phase="global")
        self._final_accessibility(state)
        state.metadata["upgraded_content_stages"] = list(self._stage_log)
        state.metadata["upgraded_start_content_deferred"] = False
        state.metadata["start_bonus_priority_order"] = (
            "terrain_before_global_terrain",
            "start_objects_before_global_objects",
        )
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
        custom_minerals = self._custom_sections.get("minerals") if self._custom_sections else None
        if isinstance(custom_minerals, dict) and custom_minerals.get("algorithm") == "legacy":
            metadata = _place_legacy_minerals(
                terrain,
                resources,
                custom_minerals,
                rng,
                excluded_mask=self._start_bonus_reservation,
            )
            state.metadata["upgraded_minerals"] = metadata
            state.metadata["upgraded_mineral_targets"] = metadata["targets"]
            self.log("resources.upgraded_minerals_custom_legacy", f"cells={metadata['placed_total']}")
            return
        if isinstance(custom_minerals, dict) and custom_minerals.get("algorithm") == "random":
            metadata = _place_random_minerals(
                terrain,
                resources,
                custom_minerals,
                rng,
                support_ids=(32, 34, 35, SNOW_TRANS, SNOW),
                excluded_mask=self._start_bonus_reservation,
            )
            state.metadata["upgraded_minerals"] = metadata
            state.metadata["upgraded_mineral_targets"] = metadata["targets"]
            self.log("resources.upgraded_minerals_custom_random", f"cells={metadata['placed_total']}")
            return
        support = np.isin(terrain, [32, 34, 35, SNOW_TRANS, SNOW])
        if self._start_bonus_reservation is not None:
            support &= ~self._start_bonus_reservation
        support_count = int(support.sum())
        if isinstance(custom_minerals, dict):
            target_total = int(round(
                support_count * float(custom_minerals.get("occupancy_percent", 0.0)) / 100.0
            ))
        else:
            target_total = int(round(support_count * float(cfg.get("rocky_accessible_occupancy_target", .90))))
        families = {int(k): v for k, v in cfg["families"].items()}
        if isinstance(custom_minerals, dict):
            shares = {
                int(family): float(custom_minerals.get("shares", {}).get(key, 0.0))
                for key, family in MINERAL_SPECS
            }
        else:
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
        if norm:
            for family in order[:-1]:
                targets[family] = int(round(target_total * shares.get(family, 0.0) / norm))
                used += targets[family]
            targets[order[-1]] = target_total - used
        else:
            targets = {family: 0 for family in order}

        occupied = np.zeros_like(support, bool)
        blob_counts: dict[int, int] = {}
        fallback_families: list[int] = []
        for family in order:
            fcfg = families[family]
            requested = max(1, round(targets[family] * int(fcfg["blobs"]) / max(1, int(fcfg["cells"]))))
            if isinstance(custom_minerals, dict):
                blob_min, blob_max = _size_bounds(
                    str(custom_minerals.get("size_variation", "normal")),
                    "upgraded",
                )
            else:
                blob_min = int(cfg.get("blob_size_min", 18))
                blob_max = int(cfg.get("blob_size_max", 105))
            sizes = _make_blob_sizes(
                targets[family], requested, rng, pr,
                blob_min, blob_max,
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
                if isinstance(custom_minerals, dict):
                    family_key = next(
                        key for key, family_id in MINERAL_SPECS if int(family_id) == int(family)
                    )
                    q = _bounded_quantities(
                        len(cells),
                        int(custom_minerals.get("average_quantity", {}).get(family_key, 10)),
                        rng,
                    )
                else:
                    # Upgraded now targets the explicit mean 10.  The
                    # retained profile multiplier is historical compatibility
                    # data and must not be applied to newly generated cells.
                    q = _bounded_quantities(len(cells), 10, rng)
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
            "model": "custom_upgraded_connected_blobs" if custom_minerals else "upgraded_v7_nogap",
            "algorithm": "upgraded" if custom_minerals else "upgraded",
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

    def _generate_fish(self, state, rng: np.random.Generator) -> None:
        terrain, resources = state.terrain, state.resources
        cfg = self.profile["fish"]
        custom_fish = self._custom_sections.get("fish") if self._custom_sections else None
        # Upgraded and its equivalent Custom configuration deliberately share
        # this exact implementation.  The historical four-band pass used to
        # select a different spatial distribution and then force a calibrated
        # cell target, so a Custom profile with the same visible parameters
        # could never reproduce the preset.
        fish = custom_fish if isinstance(custom_fish, dict) else {
            "fill_percent": UPGRADED_FISH_FILL_PERCENT,
            "average_quantity": UPGRADED_RESOURCE_MEAN,
            "near_shore": True,
            "band_thickness": int(
                cfg.get("max_shore_hex_distance", DEFAULT_FISH_BAND_THICKNESS)
            ),
        }
        metadata = _place_custom_fish(
            terrain,
            resources,
            fish,
            rng,
            excluded_mask=self._start_bonus_reservation,
        )
        if not isinstance(custom_fish, dict):
            # Keep the established diagnostic keys for reports and validators;
            # the target now describes the direct coastal-band percentage.
            metadata.update({
                "model": "upgraded_coastal_band_uniform",
                "target": metadata["target_cells"],
                "profile_target_768": int(cfg.get("target_cells", 0)),
                "max_distance": int(fish["band_thickness"]),
                "quantity_mean_target": int(fish["average_quantity"]),
                "quantity_multiplier_applied": False,
            })
        state.metadata["upgraded_fish"] = metadata
        state.metadata["upgraded_fish_target"] = metadata["target_cells"]
        self.log(
            "resources.upgraded_fish_custom" if isinstance(custom_fish, dict) else "resources.upgraded_fish",
            f"cells={metadata['cells']}",
        )

    def _place_decorations(self, state, rng: np.random.Generator, pr: random.Random) -> None:
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        cfg = self.profile["decor"]
        core = self._content_core(state)
        native_cfg = cfg.get("legacy_static_families", {})
        density_split = int(cfg.get("legacy_static_density_split_players", 8))
        density_key = "low" if int(state.metadata.get("players", 0)) <= density_split else "high"
        scale = (float(self.side) / float(self.reference_side)) ** 2
        occupied = (objects != 0) | core
        if self._start_bonus_object_clearance is not None:
            occupied |= self._start_bonus_object_clearance
        if self._object_hitbox_enforced and self._object_collision_mask is not None:
            occupied |= self._object_collision_mask
        counts: dict[str, int] = {}
        requested_targets: dict[str, int] = {}
        effective_targets: dict[str, int] = {}
        decoration_rates: dict[str, float] = {}
        effective_custom_decorations = effective_decoration_rates(self._custom_sections)

        # The Legacy native pass has one independent quota per static family.
        # Keeping the table in the Upgraded profile avoids importing Legacy at
        # runtime while preserving its IDs, supports and density split.
        for name, family_cfg in native_cfg.items():
            targets_by_density = family_cfg.get("target_768_by_density", {})
            profile_target = int(round(float(targets_by_density.get(density_key, 0)) * scale))
            rate = float(effective_custom_decorations.get(str(name), 100.0))
            requested = int(round(profile_target * rate / 100.0))
            decoration_rates[str(name)] = rate
            ids = tuple(int(value) for value in family_cfg.get("ids", ()))
            support_ids = tuple(int(value) for value in family_cfg.get("support_ids", ()))
            if GRASS in support_ids and self._grass_object_support_enabled():
                support_ids = tuple(dict.fromkeys((*support_ids, *GRASS_IDS)))
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
                    if self._object_hitbox_enforced:
                        self._mark_object_collision_cells(((x, y),))
                        if self._object_collision_mask is not None:
                            occupied[...] |= self._object_collision_mask
                    access[y, x] = 1
                    placed += 1
            counts[str(name)] = placed
            requested_targets[str(name)] = requested
            # Other editor sizes keep generating even if a copied native quota
            # cannot physically fit.  The effective target is what validators
            # use for that map; the requested target remains visible in stats.
            effective_targets[str(name)] = placed

        water = np.isin(terrain, WATER_IDS)
        deep_candidates = (
            (terrain == 7)
            & (neighbor_count(~water) == 0)
            & (
                ~occupied
                if self._object_hitbox_enforced
                else (objects == 0)
            )
        )
        deep = np.argwhere(deep_candidates)
        reef_rate = float(effective_custom_decorations.get("reefs", 100.0))
        decoration_rates["reefs"] = reef_rate
        reef_profile_target = self._scaled_target(cfg.get("reef_target", 0))
        reef_target = min(int(round(reef_profile_target * reef_rate / 100.0)), len(deep))
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
                if self._object_hitbox_enforced:
                    self._mark_object_collision_cells(((x, y),))
                    if self._object_collision_mask is not None:
                        occupied |= self._object_collision_mask
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
            "rates": decoration_rates,
            "decorative_objects": int(sum(counts.values())),
            "reefs": reef_count,
            "reef_target": reef_target,
        }
        state.metadata["upgraded_decorations"] = metadata
        if self._object_hitbox_enforced:
            self._refresh_object_collision_mask(state)
        self.log("objects.upgraded_decorations", str(metadata))

    def _place_trees(self, state, rng: np.random.Generator, pr: random.Random) -> None:
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        cfg = self.profile["trees"]
        core = self._content_core(state)
        technical = self._core_mask(state, max(
            int(self.profile["starts"]["technical_clear_hex"]),
            int(self.profile["starts"].get("editor_object_clear_hex", 14)) if self._force_extended_start_bonus() else 0,
        ))
        tree_sections = self._custom_sections.get("trees", {}) if isinstance(self._custom_sections, dict) else {}
        tree_sections = tree_sections if isinstance(tree_sections, dict) else {}
        sapling_sections = tree_sections.get("saplings", {})
        sapling_sections = sapling_sections if isinstance(sapling_sections, dict) else {}
        forest_sections = tree_sections.get("forests", {})
        forest_sections = forest_sections if isinstance(forest_sections, dict) else {}
        profile_target = int(cfg["adult_global_target"])
        small_profile_target = int(cfg.get("small_tree_target", 0))
        base_quota = self._custom_percent(
            "trees", "base_quota_percent", 100.0, maximum=500.0
        )
        global_pool_target = int(round(self._scaled_target(profile_target) * base_quota / 100.0))
        native_saplings_enabled = small_profile_target > 0
        native_saplings_separate = bool(cfg.get("small_tree_separate_pool", True))
        native_sapling_quota = (
            small_profile_target / profile_target * 100.0 if profile_target > 0 else 0.0
        )
        native_sapling_placement = (
            "forests_only" if float(cfg.get("small_tree_cluster_share", 0.0)) > 0 else "everywhere"
        )
        saplings_enabled = bool(sapling_sections.get("enabled", native_saplings_enabled))
        saplings_in_global_pool = bool(
            sapling_sections.get("in_global_pool", not native_saplings_separate)
        ) if saplings_enabled else False
        sapling_global_share = min(
            100.0,
            max(
                0.0,
                float(
                    sapling_sections.get(
                        "global_share_percent",
                        (small_profile_target / (profile_target + small_profile_target) * 100.0)
                        if not native_saplings_separate and profile_target + small_profile_target > 0
                        else 0.0,
                    )
                ),
            ),
        )
        sapling_quota = self._custom_percent(
            "trees", "saplings.quota_percent", native_sapling_quota
        )
        if saplings_in_global_pool:
            small_target = int(round(global_pool_target * sapling_global_share / 100.0))
            target = max(0, global_pool_target - small_target)
        else:
            target = global_pool_target
            small_target = int(round(self._scaled_target(profile_target) * sapling_quota / 100.0)) if saplings_enabled else 0
        native_forest_enabled = "adult_cluster_share" in cfg and float(cfg.get("adult_cluster_share", 0.0)) > 0
        native_forest_share = float(cfg.get("adult_cluster_share", 0.0)) * 100.0
        native_forest_average = (
            profile_target * float(cfg.get("adult_cluster_share", 0.0))
            / max(1, int(cfg.get("forest_centers", 1)))
            if native_forest_enabled
            else 1.0
        )
        forest_enabled = bool(forest_sections.get("enabled", native_forest_enabled))
        forest_share = self._custom_percent(
            "trees",
            "forests.share_percent",
            native_forest_share,
            maximum=100.0,
        ) if forest_enabled else 0.0
        forest_average = max(
            1.0,
            float(forest_sections.get("trees_per_forest", native_forest_average)),
        )
        forest_variation = min(100.0, max(0.0, float(forest_sections.get("tree_count_variation_percent", 0.0))))
        ids = np.asarray(cfg["adult_ids"], dtype=np.uint8)
        weights = np.asarray(cfg.get("adult_weights", np.ones(len(ids))), dtype=float)
        weights /= weights.sum()
        object_grass = self._grass_object_support_mask(terrain)
        force_extended = self._force_extended_start_bonus()
        grass = object_grass & ~core
        adult_forest_clearance = max(3, int(cfg.get("adult_forest_min_hex_distance", 3)))
        tree_spacing = adult_forest_clearance
        start_forest_cfg = self._custom_start_bonus_config("forest")
        start_forest_enabled = (
            self._start_package_enabled("start_forest")
            and bool(start_forest_cfg.get("enabled", True))
        )

        def place(
            mask: np.ndarray,
            count: int,
            object_ids,
            probabilities=None,
            support: np.ndarray | None = None,
            clearance: int = 2,
            point_sink: list[tuple[int, int]] | None = None,
        ) -> int:
            allowed = mask & (object_grass if support is None else support)
            if self._start_bonus_object_clearance is not None:
                allowed &= ~self._start_bonus_object_clearance
            if self._object_hitbox_enforced and self._object_collision_mask is not None:
                allowed &= ~self._object_collision_mask
            points = np.argwhere(allowed & (objects == 0))
            placed = 0
            if not count or not len(points):
                return 0
            id_array = np.asarray(tuple(object_ids), dtype=np.uint8)
            for index in rng.permutation(len(points)):
                if placed >= count:
                    break
                y, x = map(int, points[index])
                effective_clearance = (
                    max(clearance, tree_spacing)
                    if self._object_hitbox_enforced
                    else clearance
                )
                if (
                    objects[y, x]
                    or (
                        self._object_hitbox_enforced
                        and self._object_collision_mask is not None
                        and self._object_collision_mask[y, x]
                    )
                    or (
                        effective_clearance
                        and not self._object_clear(state, x, y, effective_clearance)
                    )
                ):
                    continue
                objects[y, x] = int(rng.choice(id_array, p=probabilities)) if probabilities is not None else int(rng.choice(id_array))
                access[y, x] = 1
                if self._object_hitbox_enforced:
                    self._mark_object_collision_cells(((x, y),))
                if point_sink is not None:
                    point_sink.append((x, y))
                placed += 1
            return placed

        def start_center(sx: int, sy: int) -> tuple[tuple[int, int] | None, bool]:
            desired = int(start_forest_cfg.get("center_hex", cfg.get("start_cluster_center_hex", 34)))
            desired += int(start_forest_cfg.get("distance_from_border", 0))
            centers: list[tuple[int, int]] = []
            for radius in range(max(1, desired - 2), desired + 3):
                centers.extend(
                    (x, y)
                    for x, y in _hex_points(self.side, sx, sy, radius, exact=radius)
                    if (
                        object_grass[y, x]
                        and not core[y, x]
                        and not start_forest_mask[y, x]
                        and not objects[y, x]
                    )
                )
            pr.shuffle(centers)
            if centers:
                return pr.choice(centers), False
            return None, False

        start_forest_records: list[dict[str, int]] = []
        start_adults = 0
        start_small = 0
        start_forest_extended_used = False
        start_adult_target = self._start_bonus_int(
            start_forest_cfg.get(
                "adult_trees_per_player",
                cfg.get("adult_start_bonus_per_player", 30),
            ),
            START_FOREST_COUNT_MIN,
            START_FOREST_COUNT_MAX,
            START_FOREST_ADULT_DEFAULT,
        ) if start_forest_enabled else 0
        start_small_target = self._start_bonus_int(
            start_forest_cfg.get(
                "saplings_per_player",
                cfg.get("small_tree_start_bonus_per_player", 20),
            ),
            START_FOREST_COUNT_MIN,
            START_FOREST_COUNT_MAX,
            START_FOREST_SAPLING_DEFAULT,
        ) if start_forest_enabled else 0
        minimum_tree_forest_radius = (
            self._minimum_tree_forest_radius(
                start_adult_target + start_small_target,
                tree_spacing,
            )
            if start_forest_enabled else 0
        )
        minimum_adult_forest_radius = (
            self._minimum_tree_forest_radius(start_adult_target, tree_spacing)
            if start_forest_enabled and start_adult_target > 0 else 0
        )
        start_forest_mask = np.zeros_like(grass)
        for player, (sx, sy) in enumerate(state.starts, start=1):
            if not start_forest_enabled:
                start_forest_records.append({"player": player, "adult": 0, "small": 0})
                continue
            forced_plan = None
            if force_extended:
                desired = int(start_forest_cfg.get("center_hex", cfg.get("start_cluster_center_hex", 34))) + int(start_forest_cfg.get("distance_from_border", 0))
                legal_cells = object_grass & ~core & ~technical & ~start_forest_mask & (objects == 0) & (state.resources == 0)
                collision = dilate(objects != 0, tree_spacing - 1).copy()
                if self._object_collision_mask is not None:
                    collision |= self._object_collision_mask
                if self._start_bonus_object_clearance is not None:
                    collision |= self._start_bonus_object_clearance
                forced_plan = plan_objects(
                    ordered_centers(legal_cells, sx, sy, desired, pr.shuffle),
                    legal_cells, collision,
                    (start_adult_target, start_small_target), tree_spacing, ((0, 0),), minimum_tree_forest_radius, minimum_adult_forest_radius, rng,
                )
                center = forced_plan.center if forced_plan is not None else None
                center_extended = bool(center and hex_distance(sx, sy, *center) > desired + 2)
            else:
                center, center_extended = start_center(int(sx), int(sy))
            if center is None:
                start_forest_records.append({"player": player, "adult": 0, "small": 0})
                continue
            cx, cy = center
            radius = minimum_tree_forest_radius
            effective_radius = radius
            forest = np.zeros_like(grass)
            adult_count = 0
            small_count = 0
            adult_points: list[tuple[int, int]] = []
            small_points: list[tuple[int, int]] = []
            adult_region_radius = minimum_adult_forest_radius
            # The first radius is derived from the total population and the
            # common hitbox.  If terrain or existing objects fragment it, the
            # same envelope grows until the legal request fits; no arbitrary
            # user-facing radius maximum is applied.
            if force_extended and forced_plan is not None:
                adult_points, small_points = forced_plan.adults, forced_plan.saplings
                adult_count, small_count = len(adult_points), len(small_points)
                effective_radius, adult_region_radius = forced_plan.radius, forced_plan.adult_radius
                for x, y in adult_points + small_points:
                    objects[y, x] = int(rng.choice(ids, p=weights)) if (x, y) in adult_points else int(cfg.get("small_tree_id", 84))
                    access[y, x] = 1
                    if self._object_hitbox_enforced:
                        self._mark_object_collision_cells(((x, y),))
            else:
                for candidate_radius in range(
                    minimum_tree_forest_radius,
                    max(minimum_tree_forest_radius, self.side * 2) + 1,
                ):
                    effective_radius = candidate_radius
                    forest = np.zeros_like(grass)
                    for x, y in _hex_points(self.side, cx, cy, candidate_radius):
                        if (
                            not core[y, x]
                            and not technical[y, x]
                            and object_grass[y, x]
                            and not start_forest_mask[y, x]
                            and not self._start_bonus_reservation[y, x]
                        ):
                            forest[y, x] = True
                    if adult_count < start_adult_target:
                        adult_region_radius = min(
                            candidate_radius,
                            max(
                                minimum_adult_forest_radius,
                                minimum_adult_forest_radius
                                + candidate_radius
                                - minimum_tree_forest_radius,
                            ),
                        )
                        adult_region = np.zeros_like(forest)
                        for x, y in _hex_points(self.side, cx, cy, adult_region_radius):
                            if forest[y, x]:
                                adult_region[y, x] = True
                        adult_count += place(
                            adult_region,
                            start_adult_target - adult_count,
                            ids,
                            weights,
                            clearance=tree_spacing,
                            point_sink=adult_points,
                        )
                    if adult_count >= start_adult_target:
                        sapling_region = forest.copy()
                        if start_adult_target > 0:
                            for x, y in _hex_points(self.side, cx, cy, adult_region_radius):
                                sapling_region[y, x] = False
                        small_count += place(
                            sapling_region,
                            start_small_target - small_count,
                            (int(cfg.get("small_tree_id", 84)),),
                            clearance=tree_spacing,
                            point_sink=small_points,
                        )
                    if adult_count >= start_adult_target and small_count >= start_small_target:
                        break
            # Record only cells that received a tree.  The search envelope is
            # not a reservation: empty legal grass remains available to later
            # global passes.
            for x, y in adult_points + small_points:
                start_forest_mask[y, x] = True
            self._refresh_start_bonus_object_clearance(state)
            start_adults += adult_count
            start_small += small_count
            start_forest_extended_used = bool(start_forest_extended_used or center_extended)
            start_forest_records.append(
                {
                    "player": player,
                    "center_x": int(cx),
                    "center_y": int(cy),
                    "radius": int(radius),
                    "effective_radius": int(effective_radius),
                    "minimum_required_radius": int(minimum_tree_forest_radius),
                    "adult_core_radius": int(adult_region_radius),
                    "adult": int(adult_count),
                    "small": int(small_count),
                    "extended_radius_used": bool(center_extended),
                    "adult_points": [[int(x), int(y)] for x, y in adult_points],
                    "small_points": [[int(x), int(y)] for x, y in small_points],
                }
            )

        # Keep only the actual bonus tree anchors visible to later passes.
        # Collision checks use the live object layer for the complete spacing
        # rule; no empty forest envelope is reserved.
        if start_forest_enabled:
            self._start_bonus_reservation |= start_forest_mask

        # Build a set of explicit global forest regions.  Adults use a smaller
        # cluster region for the 30% quota; saplings can use the whole forest
        # region, so ID84 never falls back to a random grass scatter.
        global_forest = np.zeros_like(grass)
        adult_cluster_region = np.zeros_like(grass)
        small_cluster_region = np.zeros_like(grass)
        forest_regions: list[np.ndarray] = []
        centers: list[tuple[int, int, int]] = []
        global_grass = grass & ~start_forest_mask
        points = np.argwhere(global_grass & (objects == 0))
        clustered_target = min(target, round(target * forest_share / 100.0))
        center_count = (
            min(max(1, int(round(clustered_target / forest_average))), len(points))
            if forest_enabled and clustered_target
            else 0
        )
        if center_count:
            for index in rng.choice(len(points), center_count, replace=False):
                y, x = map(int, points[index])
                radius_min = int(cfg.get("forest_radius_min", 7))
                radius_max = int(cfg.get("forest_radius_max", 12))
                radius = int(rng.integers(min(radius_min, radius_max), max(radius_min, radius_max) + 1))
                centers.append((x, y, radius))
                adult_region = np.zeros_like(grass)
                for fx, fy in _hex_points(self.side, x, y, radius):
                    if global_grass[fy, fx] and not core[fy, fx]:
                        global_forest[fy, fx] = True
                    if global_grass[fy, fx] and not core[fy, fx] and hex_distance(x, y, fx, fy) <= max(4, radius - 2):
                        adult_cluster_region[fy, fx] = True
                        small_cluster_region[fy, fx] = True
                        adult_region[fy, fx] = True
                forest_regions.append(adult_region)

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

        forest_quotas_values = forest_quotas(clustered_target, len(forest_regions), forest_variation)
        global_cluster_adults = 0
        forest_placed_values: list[int | None] = []
        if forest_variation <= 0:
            # Keep the zero-variation/default path byte-for-byte equivalent
            # to the native Upgraded placement: one shuffled candidate pool,
            # with the forest share affecting the quota but not the order.
            global_cluster_adults = place(
                adult_cluster_region,
                clustered_target,
                ids,
                weights,
                clearance=adult_forest_clearance,
            )
            forest_placed_values = [None] * len(forest_regions)
        else:
            for region, quota in zip(forest_regions, forest_quotas_values):
                placed_in_region = place(
                    region,
                    quota,
                    ids,
                    weights,
                    clearance=adult_forest_clearance,
                )
                forest_placed_values.append(placed_in_region)
                global_cluster_adults += placed_in_region
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
        small_placement = str(
            sapling_sections.get("placement", native_sapling_placement)
        ) if saplings_enabled else "everywhere"
        if small_placement == "forests_only":
            small_mask = global_forest
        elif small_placement == "outside_forests":
            small_mask = global_grass & ~global_forest
        else:
            small_mask = global_grass
        small_cluster_target = round(small_target * float(cfg.get("small_tree_cluster_share", 0.76))) if small_placement == "forests_only" else 0
        global_small_cluster = place(
            small_cluster_region,
            min(small_target, small_cluster_target),
            (small_id,),
            clearance=adult_forest_clearance,
        )
        global_small = global_small_cluster + place(
            small_mask,
            max(0, small_target - global_small_cluster),
            (small_id,),
            clearance=adult_forest_clearance,
        )
        if global_small < small_target and small_placement == "forests_only":
            # Expand the same generated forest envelopes when the inner
            # regions are too sparse; never turn a forest-only request into a
            # free-world placement.
            expanded_forest = np.zeros_like(global_forest)
            for cx, cy, _ in centers:
                for x, y in _hex_points(self.side, cx, cy, int(cfg.get("forest_radius_max", 12)) + 4):
                    if object_grass[y, x] and not core[y, x] and not start_forest_mask[y, x]:
                        expanded_forest[y, x] = True
            global_forest |= expanded_forest
            global_small += place(
                global_forest,
                small_target - global_small,
                (small_id,),
                clearance=adult_forest_clearance,
            )

        desert = np.isin(terrain, DESERT_IDS) & ~core & (objects == 0)
        palm_profile_target = int(cfg.get("palm_target", 0))
        palm_quota = self._custom_percent(
            "trees", "palm_quota_percent", 100.0, maximum=500.0
        )
        palm_requested = int(round(self._scaled_target(palm_profile_target) * palm_quota / 100.0))
        palms = place(desert, palm_requested, cfg.get("palm_ids", (78, 79)), support=desert)
        metadata = {
            "adult_trees": int(start_adults + global_adults),
            "palm_trees": palms,
            "small_trees": int(start_small + global_small),
            "adult_target": int(start_adults + global_adults),
            "small_target": int(start_small + global_small),
            "palm_target": int(palms),
            "palm_requested": palm_requested,
            "palm_quota_percent": palm_quota,
            "adult_global_requested": target,
            "adult_global_placed": int(global_adults),
            "base_quota_percent": base_quota,
            "adult_start_bonus_requested": start_adult_target * len(state.starts),
            "adult_start_bonus_placed": int(start_adults),
            "start_forest_enabled": start_forest_enabled,
            "adult_forest_requested": clustered_target,
            "adult_forest_placed": int(global_cluster_adults),
            "forests_enabled": forest_enabled,
            "forest_share_percent": forest_share,
            "forest_trees_per_forest": forest_average,
            "forest_tree_count_variation_percent": forest_variation,
            "adult_forest_min_hex_distance": adult_forest_clearance,
            "start_forest_tree_spacing_hex": tree_spacing,
            "start_forest_radius_mode": "derived_from_tree_count_and_spacing",
            "start_forest_minimum_required_radius": int(minimum_tree_forest_radius),
            "start_bonus_force_extended_radius": bool(force_extended),
            **({"center_extension_limit": FORCED_CENTER_EXTENSION} if force_extended else {}),
            "start_bonus_extended_radius_used": bool(start_forest_extended_used),
            "grass_object_support_terrains": [
                int(value) for value in (GRASS_IDS if self._grass_object_support_enabled() else (GRASS,))
            ],
            "global_quota_excludes_start_bonus": True,
            "small_global_requested": small_target,
            "small_separate_requested": small_target if saplings_enabled and not saplings_in_global_pool else 0,
            "small_global_placed": int(global_small),
            "saplings_enabled": saplings_enabled,
            "saplings_in_global_pool": saplings_in_global_pool,
            "saplings_global_share_percent": sapling_global_share,
            "saplings_quota_percent": sapling_quota if saplings_enabled else 0.0,
            "saplings_placement": small_placement,
            "small_start_bonus_requested": start_small_target * len(state.starts),
            "small_start_bonus_placed": int(start_small),
            "small_forest_only": small_placement == "forests_only",
            "small_forest_requested": small_target,
            "small_forest_placed": int(global_small),
            "small_forest_cluster_requested": small_cluster_target,
            "small_forest_cluster_placed": int(global_small_cluster),
            **({"shortfalls": [
                {"player": r["player"], "adult": start_adult_target - r["adult"],
                 "saplings": start_small_target - r["small"],
                 "reason": "insufficient_legal_support_within_center_limit"}
                for r in start_forest_records
                if r["adult"] < start_adult_target or r["small"] < start_small_target
            ]} if force_extended else {}),
            "start_forests": start_forest_records,
            "global_forests": [
                {
                    "center_x": int(x),
                    "center_y": int(y),
                    "radius": int(radius),
                    "requested_trees": int(forest_quotas_values[index])
                    if index < len(forest_quotas_values)
                    else 0,
                    "placed_trees": forest_placed_values[index]
                    if index < len(forest_placed_values)
                    else None,
                }
                for index, (x, y, radius) in enumerate(centers)
            ],
            "global_forest_tree_quotas": forest_quotas_values,
            "global_forest_tree_placed": forest_placed_values,
            "profile_targets_768": {
                "adult": profile_target,
                "small": small_profile_target,
                "palm": palm_profile_target,
            },
        }
        if self._object_hitbox_enforced:
            self._refresh_object_collision_mask(state)
            if self._object_collision_mask is not None:
                self._start_bonus_object_clearance = self._object_collision_mask.copy()
        state.metadata["upgraded_trees"] = metadata
        state.metadata["upgraded_tree_targets"] = {
            "adult": int(start_adults + global_adults),
            "small": int(start_small + global_small),
            "palm": int(palms),
        }
        self.log("objects.upgraded_trees", str(metadata))

    def _place_building_stones(
        self,
        state,
        rng: np.random.Generator,
        pr: random.Random,
        *,
        phase: str = "all",
    ) -> None:
        if phase not in {"all", "start", "global"}:
            raise ValueError(f"Phase de pierres inconnue : {phase}")
        start_phase = phase in {"all", "start"}
        terrain, objects, access = state.terrain, state.objects, state.accessibility
        object_grass = self._grass_object_support_mask(terrain)
        force_extended = self._force_extended_start_bonus()
        cfg = self.profile["building_stones"]
        core = self._content_core(state)
        technical = self._core_mask(state, max(
            int(self.profile["starts"]["technical_clear_hex"]),
            int(self.profile["starts"].get("editor_object_clear_hex", 14)) if self._force_extended_start_bonus() else 0,
        ))
        footprint = [tuple(item) for item in cfg["footprint"]]
        blocked = core.copy()
        # Family-wide mixed clearance: a tree anchor may be at distance 3,
        # never 1 or 2. Occupation alone (seven stone cells) is insufficient.
        blocked |= dilate(np.isin(objects, (43, 44, *range(68, 82), 84)), 2)
        if self._start_bonus_object_clearance is not None:
            blocked |= self._start_bonus_object_clearance
        if self._object_hitbox_enforced and self._object_collision_mask is not None:
            blocked |= self._object_collision_mask
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
                if (
                    forbidden[yy, xx]
                    or core[yy, xx]
                    or not object_grass[yy, xx]
                    or objects[yy, xx]
                    or covered[yy, xx]
                ):
                    return False
                if (
                    self._object_hitbox_enforced
                    and self._object_collision_mask is not None
                    and self._object_collision_mask[yy, xx]
                ):
                    return False
            return True

        def place(mask: np.ndarray, count: int, forbidden: np.ndarray, tag: str, player: int | None = None) -> int:
            candidates = np.argwhere(mask & object_grass & ~forbidden & (objects == 0))
            placed = 0
            for index in rng.permutation(len(candidates)):
                if placed >= count:
                    break
                y, x = map(int, candidates[index])
                if not valid(x, y, forbidden):
                    continue
                records.append({"x": x, "y": y, "tag": tag, "player": player})
                placed += 1
                # Mark the selected footprint immediately for collision
                # checks.  It is an already chosen anchor, not an empty
                # future region; the final object ID is written after stock
                # allocation below.
                for dx, dy in footprint:
                    covered[y + dy, x + dx] = True
                mark(x, y)
            return placed

        def start_center(sx: int, sy: int) -> tuple[tuple[int, int] | None, bool]:
            desired = int(start_stone_cfg.get("center_hex", cfg.get("start_cluster_center_hex", 34)))
            desired += self._start_bonus_int(
                start_stone_cfg.get("distance_from_border", 0),
                START_BONUS_DISTANCE_MIN,
                START_BONUS_DISTANCE_MAX,
                0,
            )
            centers: list[tuple[int, int]] = []
            for radius in range(max(1, desired - 2), desired + 3):
                centers.extend(
                    (x, y)
                    for x, y in _hex_points(self.side, sx, sy, radius, exact=radius)
                    if object_grass[y, x] and not core[y, x] and not objects[y, x]
                )
            pr.shuffle(centers)
            if centers:
                return pr.choice(centers), False
            return None, False

        start_cfg = self._custom_start_bonus_config("building_stones")
        start_stone_cfg = start_cfg
        start_stones_enabled = (
            self._start_package_enabled("start_building_stones")
            and bool(start_cfg.get("enabled", True))
        )
        start_anchor_target = self._start_bonus_int(
            start_cfg.get("anchors_per_player", START_STONE_ANCHOR_DEFAULT),
            START_STONE_ANCHOR_MIN,
            START_STONE_ANCHOR_MAX,
            START_STONE_ANCHOR_DEFAULT,
        ) if start_stones_enabled else 0
        start_average = _half_step_quantity(
            start_cfg.get("average_quantity", START_STONE_AVERAGE_DEFAULT),
            START_STONE_AVERAGE_DEFAULT,
        )
        start_stock_per_player = self._start_bonus_int(
            math.floor(start_anchor_target * start_average + 0.5),
            START_BONUS_STOCK_MIN,
            START_BONUS_STOCK_MAX,
            int(START_STONE_ANCHOR_DEFAULT * START_STONE_AVERAGE_DEFAULT),
        ) if start_stones_enabled and start_anchor_target > 0 else 0
        start_min = self._start_bonus_int(
            start_cfg.get("quantity_min", STONE_QUANTITY_MINIMUM),
            STONE_QUANTITY_MINIMUM,
            STONE_QUANTITY_MAXIMUM,
            STONE_QUANTITY_MINIMUM,
        )
        start_max = self._start_bonus_int(
            start_cfg.get("quantity_max", STONE_QUANTITY_MAXIMUM),
            start_min,
            STONE_QUANTITY_MAXIMUM,
            STONE_QUANTITY_MAXIMUM,
        )
        start_records_by_player: dict[int, list[dict[str, object]]] = {}
        start_centers: list[dict[str, int]] = []
        start_stone_mask = np.zeros_like(core)
        start_stone_extended_used = False
        minimum_stone_radius = (
            self._minimum_tree_forest_radius(
                start_anchor_target,
                int(cfg["anchor_min_hex_distance"]),
            ) + 2
            if start_stones_enabled and start_anchor_target > 0 else 0
        )
        if phase == "global" and self._prioritized_start_stone_state is not None:
            saved = self._prioritized_start_stone_state
            records = list(saved["records"])
            start_records_by_player = {
                int(player): list(player_records)
                for player, player_records in saved["start_records_by_player"].items()
            }
            start_centers = [dict(item) for item in saved["start_centers"]]
            start_stone_mask = np.asarray(saved["start_stone_mask"], dtype=bool).copy()
            blocked = np.asarray(saved["blocked"], dtype=bool).copy()
            covered = np.asarray(saved["covered"], dtype=bool).copy()
            start_stone_extended_used = bool(saved["extended_used"])
            # The global stone pass runs after the complete start forest.
            # Reapply the live halo here because the saved start-phase mask
            # predates those tree writes.
            if self._start_bonus_object_clearance is not None:
                blocked |= self._start_bonus_object_clearance
        elif start_phase:
            for player, (sx, sy) in enumerate(state.starts, start=1):
                if not start_stones_enabled:
                    start_records_by_player[player] = []
                    continue
                forced_plan = None
                if force_extended:
                    desired = int(start_stone_cfg.get("center_hex", cfg.get("start_cluster_center_hex", 34))) + int(start_stone_cfg.get("distance_from_border", 0))
                    legal_cells = object_grass & ~core & ~technical & ~covered & (objects == 0) & (state.resources == 0)
                    collision = blocked.copy()
                    if self._object_collision_mask is not None:
                        collision |= self._object_collision_mask
                    if self._start_bonus_object_clearance is not None:
                        collision |= self._start_bonus_object_clearance
                    legal_cells &= ~collision
                    forced_plan = plan_objects(
                        ordered_centers(legal_cells, sx, sy, desired, pr.shuffle),
                        legal_cells, collision,
                        (start_anchor_target, 0), int(cfg["anchor_min_hex_distance"]), footprint, minimum_stone_radius, minimum_stone_radius, rng,
                    )
                    center = forced_plan.center if forced_plan is not None else None
                    center_extended = bool(center and hex_distance(sx, sy, *center) > desired + 2)
                else:
                    center, center_extended = start_center(int(sx), int(sy))
                if center is None:
                    start_records_by_player[player] = []
                    continue
                cx, cy = center
                region = np.zeros_like(core)
                before = len(records)
                placed = 0
                effective_radius = minimum_stone_radius
                # The first radius follows the requested anchor count, the native
                # spacing and the seven-cell footprint.  Fragmented legal terrain
                # may expand it, but there is no arbitrary user radius or endless
                # retry loop.
                if force_extended and forced_plan is not None:
                    effective_radius = forced_plan.radius
                    placed = len(forced_plan.adults)
                    for x, y in forced_plan.adults:
                        records.append({"x": x, "y": y, "tag": "start_bonus", "player": player})
                        for dx, dy in footprint:
                            covered[y + dy, x + dx] = True
                        mark(x, y)
                else:
                    for radius in range(
                        minimum_stone_radius,
                        max(minimum_stone_radius, self.side * 2) + 1,
                    ):
                        effective_radius = radius
                        region = np.zeros_like(core)
                        for x, y in _hex_points(self.side, cx, cy, radius):
                            if (
                                object_grass[y, x]
                                and not core[y, x]
                                and not start_stone_mask[y, x]
                            ):
                                region[y, x] = True
                        placed += place(
                            region,
                            start_anchor_target - placed,
                            technical,
                            "start_bonus",
                            player,
                        )
                        if placed >= start_anchor_target:
                            break
                for record in records[before:]:
                    anchor_x, anchor_y = int(record["x"]), int(record["y"])
                    for dx, dy in footprint:
                        xx, yy = anchor_x + dx, anchor_y + dy
                        if 0 <= xx < self.side and 0 <= yy < self.side:
                            start_stone_mask[yy, xx] = True
                start_stone_extended_used = bool(start_stone_extended_used or center_extended)
                start_records_by_player[player] = records[before:]
                start_centers.append(
                    {
                        "player": player,
                        "center_x": int(cx),
                        "center_y": int(cy),
                        "radius": int(effective_radius),
                        "minimum_required_radius": int(minimum_stone_radius),
                        "anchors": int(placed),
                        "extended_radius_used": bool(center_extended),
                    }
                )

        if start_stones_enabled:
            core |= start_stone_mask
            self._start_bonus_reservation |= start_stone_mask

        if phase == "start":
            start_quantity_by_record: dict[int, int] = {}
            start_stock = 0
            for player_records in start_records_by_player.values():
                quantities = _full_range_quantities(
                    len(player_records),
                    start_average,
                    rng,
                    minimum=start_min,
                    maximum=start_max,
                )
                for record, quantity in zip(player_records, quantities):
                    start_quantity_by_record[id(record)] = int(quantity)
                    start_stock += int(quantity)
            for record in records:
                x, y = int(record["x"]), int(record["y"])
                quantity = int(start_quantity_by_record.get(id(record), 0))
                objects[y, x] = int(cfg["exhausted_id"]) - quantity
                for dx, dy in footprint:
                    if quantity > 0:
                        access[y + dy, x + dx] = 1
            self._prioritized_start_stone_state = {
                "records": records,
                "start_records_by_player": start_records_by_player,
                "start_centers": start_centers,
                "start_stone_mask": start_stone_mask.copy(),
                "blocked": blocked.copy(),
                "covered": covered.copy(),
                "extended_used": start_stone_extended_used,
                "quantity_by_record": start_quantity_by_record,
                "stock": start_stock,
            }
            self._refresh_start_bonus_object_clearance(state)
            state.metadata["upgraded_stones"] = {
                "anchors": len(records),
                "stock": start_stock,
                "global_anchors": 0,
                "global_stock": 0,
                "start_bonus_anchors": len(records),
                "start_bonus_anchor_requested": start_anchor_target * len(state.starts),
                "start_bonus_stock": start_stock,
                "start_bonus_stock_requested": start_stock_per_player * len(state.starts),
                "start_bonus_quantity_distribution_model": "full_range_mean_tilt",
                "start_building_stones_enabled": start_stones_enabled,
                "start_bonus_minimum_required_radius": int(minimum_stone_radius),
                "start_bonus_radius_mode": "derived_from_anchor_count_and_spacing",
                "start_bonus_force_extended_radius": bool(force_extended),
            **({"center_extension_limit": FORCED_CENTER_EXTENSION} if force_extended else {}),
                "start_bonus_extended_radius_used": bool(start_stone_extended_used),
                "global_quota_excludes_start_bonus": True,
                **({"shortfalls": [
                {"player": player, "anchors": start_anchor_target - len(player_records),
                 "reason": "insufficient_legal_support_within_center_limit"}
                for player, player_records in start_records_by_player.items()
                if len(player_records) < start_anchor_target
            ]} if force_extended else {}),
            "start_bonus_per_player": [
                    {
                        "player": player,
                        "anchors": len(player_records),
                        "stock": int(sum(start_quantity_by_record.get(id(record), 0) for record in player_records)),
                    }
                    for player, player_records in start_records_by_player.items()
                ],
                "start_centers": start_centers,
                "start_bonus_deferred": True,
            }
            state.metadata["upgraded_stone_targets"] = {
                "anchors": len(records),
                "stock": start_stock,
            }
            self.log("objects.upgraded_start_building_stones", str(state.metadata["upgraded_stones"]))
            return

        anchor_density = self._custom_percent("building_stones", "anchor_density_percent", 100.0)
        stone_controls = (self._custom_sections or {}).get("building_stones", {})
        stone_controls = stone_controls if isinstance(stone_controls, dict) else {}
        group_controls = stone_controls.get("groups", {})
        group_controls = group_controls if isinstance(group_controls, dict) else {}
        profile_stock_target = int(cfg["global_stock_target"])
        profile_active = max(
            1,
            int(cfg["global_anchor_target"])
            - int(cfg.get("global_exhausted_anchor_target", 0)),
        )
        profile_average = int(round(profile_stock_target / profile_active))
        average_value = stone_controls.get("average_quantity")
        if average_value is None:
            average_value = profile_average
        try:
            average_quantity = _half_step_quantity(average_value, profile_average)
        except (TypeError, ValueError):
            average_quantity = profile_average
        average_quantity = _half_step_quantity(average_quantity, profile_average)
        cluster_share = group_controls.get(
            "share_percent",
            stone_controls.get(
                "cluster_share_percent",
                float(cfg.get("cluster_share", 0.30)) * 100.0,
            ),
        )
        try:
            cluster_share = float(cluster_share)
        except (TypeError, ValueError):
            cluster_share = float(cfg.get("cluster_share", 0.30)) * 100.0
        cluster_share = min(100.0, max(0.0, cluster_share))
        groups_enabled = bool(
            group_controls.get(
                "enabled",
                stone_controls.get("groups_enabled", cluster_share > 0),
            )
        )
        if not groups_enabled:
            cluster_share = 0.0
        group_average_value = group_controls.get(
            "stones_per_group",
            stone_controls.get("cluster_typical_anchors", cfg.get("cluster_typical_anchors", 8.0)),
        )
        try:
            group_average = float(group_average_value)
        except (TypeError, ValueError):
            group_average = float(cfg.get("cluster_typical_anchors", 8.0))
        group_average = min(1000.0, max(1.0, group_average))
        group_variation_value = group_controls.get(
            "stone_count_variation_percent",
            stone_controls.get("cluster_count_variation_percent", 0.0),
        )
        try:
            group_variation = float(group_variation_value)
        except (TypeError, ValueError):
            group_variation = 0.0
        group_variation = min(100.0, max(0.0, group_variation))

        requested_target = int(round(self._scaled_target(cfg["global_anchor_target"]) * anchor_density / 100.0))
        global_target = requested_target
        cluster_target = round(global_target * cluster_share / 100.0)
        global_cluster_region = np.zeros_like(core)
        candidates = np.argwhere(object_grass & ~core & (objects == 0))
        center_count = (
            min(max(1, int(math.ceil(cluster_target / group_average))), len(candidates))
            if cluster_target
            else 0
        )
        group_regions: list[np.ndarray] = []
        group_centers: list[tuple[int, int, int]] = []
        if center_count:
            for index in rng.choice(len(candidates), center_count, replace=False):
                y, x = map(int, candidates[index])
                radius = int(rng.integers(4, 13))
                region = np.zeros_like(core)
                for fx, fy in _hex_points(self.side, x, y, radius):
                    if object_grass[fy, fx] and not core[fy, fx]:
                        region[fy, fx] = True
                        global_cluster_region[fy, fx] = True
                group_regions.append(region)
                group_centers.append((x, y, radius))

        def group_quotas(total: int, count: int) -> list[int]:
            if total <= 0 or count <= 0:
                return []
            if group_variation <= 0:
                weights = np.ones(count, dtype=float)
            else:
                low = max(0.01, 1.0 - group_variation / 100.0)
                weights = rng.uniform(low, 1.0 + group_variation / 100.0, count)
            raw = total * weights / float(weights.sum())
            quotas = np.floor(raw).astype(int)
            remainder = int(total - int(quotas.sum()))
            if remainder:
                for index in np.argsort(-(raw - quotas))[:remainder]:
                    quotas[int(index)] += 1
            return [int(value) for value in quotas]

        group_targets = group_quotas(cluster_target, len(group_regions))
        group_placed_values: list[int] = []
        global_cluster_placed = 0
        for region, group_target in zip(group_regions, group_targets):
            placed = place(region, group_target, core, "global_group")
            group_placed_values.append(placed)
            global_cluster_placed += placed
        if global_cluster_placed < cluster_target:
            global_cluster_placed += place(
                global_cluster_region,
                cluster_target - global_cluster_placed,
                core,
                "global_group",
            )
        global_placed = global_cluster_placed
        global_remaining = max(0, global_target - global_placed)
        global_placed += place(object_grass & ~global_cluster_region, global_remaining, core, "global")
        if global_placed < global_target:
            global_placed += place(object_grass, global_target - global_placed, core, "global")

        global_records = [record for record in records if str(record["tag"]).startswith("global")]
        exhausted_count = int(rng.binomial(len(global_records), 0.01125))
        exhausted_indices: set[int] = set()
        if exhausted_count:
            exhausted_indices = {
                int(value)
                for value in rng.choice(len(global_records), exhausted_count, replace=False)
            }
        active_global = len(global_records) - exhausted_count
        preserve_profile_distribution = (
            self._custom_sections is None
            or (anchor_density == 100.0 and average_quantity == profile_average)
        )
        if anchor_density == 100.0 and average_quantity == profile_average:
            global_stock_target = int(round(self._scaled_target(profile_stock_target)))
        else:
            global_stock_target = int(round(active_global * average_quantity))
        if preserve_profile_distribution:
            global_quantities = _allocate_quantities(
                active_global,
                global_stock_target,
                rng,
                weighted_fullness=bool(cfg.get("global_stock_weighted_fullness", True)),
                ensure_all_values=True,
            )
            distribution_model = "native_random_balance"
        else:
            global_quantities = _full_range_quantities(
                active_global,
                global_stock_target / active_global if active_global else average_quantity,
                rng,
                minimum=STONE_QUANTITY_MINIMUM,
                maximum=STONE_QUANTITY_MAXIMUM,
            ).astype(np.int16)
            distribution_model = "full_range_mean_tilt"
        active_index = 0
        quantity_by_record: dict[int, int] = {}
        for index, record in enumerate(global_records):
            if index in exhausted_indices:
                quantity_by_record[id(record)] = 0
            else:
                quantity_by_record[id(record)] = int(global_quantities[active_index])
                active_index += 1

        if phase == "global" and self._prioritized_start_stone_state is not None:
            saved = self._prioritized_start_stone_state
            quantity_by_record.update(
                {
                    int(record_id): int(quantity)
                    for record_id, quantity in saved["quantity_by_record"].items()
                }
            )
            start_stock = int(saved["stock"])
        else:
            start_stock = 0
            for player_records in start_records_by_player.values():
                quantities = _full_range_quantities(
                    len(player_records),
                    start_average,
                    rng,
                    minimum=start_min,
                    maximum=start_max,
                )
                for record, quantity in zip(player_records, quantities):
                    quantity_by_record[id(record)] = int(quantity)
                    start_stock += int(quantity)

        for record in records:
            x, y = int(record["x"]), int(record["y"])
            quantity = int(quantity_by_record.get(id(record), 0))
            objects[y, x] = int(cfg["exhausted_id"]) - quantity
            for dx, dy in footprint:
                if quantity > 0:
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
            "anchor_density_percent": anchor_density,
            "global_stock": int(sum(quantity_by_record.get(id(record), 0) for record in global_records)),
            "global_stock_requested": global_stock_target,
            "average_quantity": average_quantity,
            "global_active_average_quantity": round(
                float(sum(global_quantities)) / active_global, 4
            ) if active_global else 0.0,
            "global_quantity_distribution_model": distribution_model,
            "global_active_anchors": active_global,
            "global_exhausted_anchors": exhausted_count,
            "start_bonus_anchors": len(records) - len(global_records),
            "start_bonus_anchor_requested": start_anchor_target * len(state.starts),
            "start_bonus_stock": start_stock,
            "start_bonus_stock_requested": start_stock_per_player * len(state.starts),
            "start_bonus_quantity_distribution_model": "full_range_mean_tilt",
            "start_building_stones_enabled": start_stones_enabled,
            "start_bonus_minimum_required_radius": int(minimum_stone_radius),
            "start_bonus_radius_mode": "derived_from_anchor_count_and_spacing",
            "start_bonus_force_extended_radius": bool(force_extended),
            **({"center_extension_limit": FORCED_CENTER_EXTENSION} if force_extended else {}),
            "start_bonus_extended_radius_used": bool(start_stone_extended_used),
            "global_quota_excludes_start_bonus": True,
            **({"shortfalls": [
                {"player": player, "anchors": start_anchor_target - len(player_records),
                 "reason": "insufficient_legal_support_within_center_limit"}
                for player, player_records in start_records_by_player.items()
                if len(player_records) < start_anchor_target
            ]} if force_extended else {}),
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
            "cluster_share": cluster_share / 100.0,
            "cluster_share_percent": cluster_share,
            "groups_enabled": groups_enabled,
            "group_average": group_average,
            "group_count_variation_percent": group_variation,
            "group_centers": [
                {
                    "center_x": int(x),
                    "center_y": int(y),
                    "radius": int(radius),
                    "requested_stones": int(group_targets[index])
                    if index < len(group_targets)
                    else 0,
                    "placed_stones": int(group_placed_values[index])
                    if index < len(group_placed_values)
                    else 0,
                }
                for index, (x, y, radius) in enumerate(group_centers)
            ],
            "group_targets": group_targets,
            "group_placed": group_placed_values,
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
            if quantity_by_record.get(id(record), 0) > 0
            for dx, dy in footprint
        ]
        self.log("objects.upgraded_building_stones", str(metadata))
        if self._object_hitbox_enforced:
            self._refresh_object_collision_mask(state)
            if self._object_collision_mask is not None:
                self._start_bonus_object_clearance = self._object_collision_mask.copy()

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
