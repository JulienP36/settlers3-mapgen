"""Execution helpers for the first user-facing Custom content sections."""

from __future__ import annotations

from collections import deque
import heapq
import math
from typing import Any, Mapping

import numpy as np
from scipy import ndimage

from ...map_data.constants import HEX6, RIVER_IDS, SNOW, SNOW_TRANS, WATER_IDS
from ...map_data.hexgrid import neighbor_count
from .sections import (
    MINERAL_IDS,
    MINERAL_KEYS,
    MINERAL_SPECS,
    RESOURCE_MAXIMUM,
    RESOURCE_MINIMUM,
    DEFAULT_FISH_BAND_THICKNESS,
    UPGRADED_FISH_FILL_PERCENT,
    UPGRADED_RESOURCE_MEAN,
    mineral_shares_as_fractions,
    normalize_sections,
)


_HEX_STRUCTURE = np.array([[1, 1, 0], [1, 1, 1], [0, 1, 1]], dtype=bool)


def _size_bounds(variation: str, algorithm: str) -> tuple[int, int]:
    """Map the friendly size control to safe algorithm-specific ranges."""

    if algorithm == "legacy":
        return {
            "low": (24, 55),
            "normal": (32, 95),
            "high": (48, 143),
        }.get(str(variation), (32, 95))
    return {
        "low": (24, 72),
        "normal": (18, 105),
        "high": (12, 132),
    }.get(str(variation), (18, 105))


def _make_blob_sizes(
    total: int,
    count: int,
    rng: np.random.Generator,
    minimum: int,
    maximum: int,
) -> list[int]:
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
        index = int(rng.integers(0, count))
        if difference > 0 and sizes[index] < maximum:
            sizes[index] += 1
            difference -= 1
        elif difference < 0 and sizes[index] > minimum:
            sizes[index] -= 1
            difference += 1
    return sorted(map(int, sizes), reverse=True)


def _grow_upgraded_blob(
    region: np.ndarray,
    occupied: np.ndarray,
    target: int,
    rng: np.random.Generator,
    shape_space: str,
) -> list[tuple[int, int]] | None:
    """Grow one connected, hole-free Upgraded-style blob."""

    height, width = region.shape
    available = region & ~occupied
    candidates = np.argwhere(available)
    if len(candidates) == 0:
        return None
    for _ in range(180):
        y0, x0 = map(int, candidates[int(rng.integers(0, len(candidates)))])
        radius = math.sqrt(target / math.pi)
        angle = float(rng.random()) * math.pi
        ca, sa = math.cos(angle), math.sin(angle)

        def priority(x: int, y: int) -> float:
            dx, dy = x - x0, y - y0
            if shape_space == "parallelogram_compensated":
                metric_x, metric_y = 2 * dx - dy, 2 * dy
            else:
                metric_x, metric_y = dx, dy
            u = ca * metric_x + sa * metric_y
            v = -sa * metric_x + ca * metric_y
            return (u / (radius + 1e-6)) ** 2 + (v / (radius + 1e-6)) ** 2 + 0.045 * math.sin(.52 * u + .29 * v)

        heap: list[tuple[float, int, int]] = [(0.0, x0, y0)]
        seen = {(x0, y0)}
        chosen: list[tuple[int, int]] = []
        while heap and len(chosen) < int(target):
            _, x, y = heapq.heappop(heap)
            if not available[y, x]:
                continue
            chosen.append((x, y))
            for dx, dy in HEX6:
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen or not (0 <= nx < width and 0 <= ny < height):
                    continue
                seen.add((nx, ny))
                if available[ny, nx]:
                    heapq.heappush(heap, (priority(nx, ny), nx, ny))
        if len(chosen) < int(target):
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


def _target_by_share(total: int, shares: Mapping[str, Any]) -> dict[str, int]:
    fractions = mineral_shares_as_fractions(shares)
    raw = {key: int(total) * fractions[key] for key in MINERAL_KEYS}
    targets = {key: int(math.floor(raw[key])) for key in MINERAL_KEYS}
    remainder = int(total) - sum(targets.values())
    for key in sorted(MINERAL_KEYS, key=lambda item: raw[item] - targets[item], reverse=True)[:remainder]:
        targets[key] += 1
    return targets


def _bounded_quantities(
    count: int,
    mean: float,
    rng: np.random.Generator,
    *,
    minimum: int = RESOURCE_MINIMUM,
    maximum: int = RESOURCE_MAXIMUM,
    spread: int = 3,
    keep_bounds: bool = False,
) -> np.ndarray:
    """Create varied integer quantities around a bounded target mean.

    The target can be fractional, but each placed object still receives an
    integer quantity.  The total is corrected to ``round(mean * count)`` so
    the displayed mean remains the controlling value instead of merely being
    an input to a random draw.
    """

    count = int(count)
    if count <= 0:
        return np.zeros(0, dtype=np.uint8)
    minimum = int(minimum)
    maximum = int(maximum)
    if minimum > maximum:
        raise ValueError("minimum quantity must not exceed maximum quantity")
    mean = max(float(minimum), min(float(maximum), float(mean)))
    spread = max(0, int(spread))
    if keep_bounds:
        low = max(minimum, int(math.ceil(mean - spread)))
        high = min(maximum, int(math.floor(mean + spread)))
    else:
        # Preserve the established mineral-resource distribution for existing
        # callers.  Stone piles opt into the stricter final bounds below.
        low = max(minimum, int(math.floor(mean)) - spread)
        high = min(maximum, int(math.ceil(mean)) + spread)
    values = rng.integers(low, high + 1, count, dtype=np.int16)
    difference = int(round(mean * count)) - int(values.sum())
    while difference:
        if difference > 0:
            eligible = np.flatnonzero(values < (high if keep_bounds else maximum))
            if len(eligible) == 0:
                break
            take = min(len(eligible), difference)
            chosen = rng.choice(eligible, take, replace=False)
            values[chosen] += 1
            difference -= int(take)
        else:
            eligible = np.flatnonzero(values > (low if keep_bounds else minimum))
            if len(eligible) == 0:
                break
            take = min(len(eligible), -difference)
            chosen = rng.choice(eligible, take, replace=False)
            values[chosen] -= 1
            difference += int(take)
    return values.astype(np.uint8)


def _tilted_quantity_probabilities(
    values: np.ndarray,
    target_mean: float,
) -> np.ndarray:
    """Return a smooth full-range distribution with the requested mean.

    The exponential tilt is uniform at the centre of the range and gradually
    favours the lower or upper states as the requested mean moves away from
    that centre.  Every state keeps a non-zero probability; the caller can
    reserve one occurrence of each state when the sample is large enough.
    """

    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return np.zeros(0, dtype=float)
    target_mean = min(float(values.max()), max(float(values.min()), float(target_mean)))
    centre = float(values.mean())
    if abs(target_mean - centre) < 1e-12:
        return np.full(values.size, 1.0 / values.size, dtype=float)

    lower, upper = -20.0, 20.0
    centred = values - centre
    for _ in range(80):
        tilt = (lower + upper) / 2.0
        weights = np.exp(tilt * centred - float(np.max(tilt * centred)))
        probabilities = weights / float(weights.sum())
        current_mean = float(np.dot(probabilities, values))
        if current_mean < target_mean:
            lower = tilt
        else:
            upper = tilt
    tilt = (lower + upper) / 2.0
    weights = np.exp(tilt * centred - float(np.max(tilt * centred)))
    return weights / float(weights.sum())


def _balance_quantity_total(
    quantities: np.ndarray,
    target_total: int,
    rng: np.random.Generator,
    *,
    minimum: int,
    maximum: int,
) -> np.ndarray:
    """Correct a sampled quantity vector to one exact integer total."""

    quantities = np.asarray(quantities, dtype=np.int16)
    difference = int(target_total) - int(quantities.sum())
    while difference:
        if difference > 0:
            eligible = np.flatnonzero(quantities < int(maximum))
            if not len(eligible):
                break
            quantities[int(rng.choice(eligible))] += 1
            difference -= 1
        else:
            eligible = np.flatnonzero(quantities > int(minimum))
            if not len(eligible):
                break
            quantities[int(rng.choice(eligible))] -= 1
            difference += 1
    return quantities


def _full_range_quantities(
    count: int,
    mean: float,
    rng: np.random.Generator,
    *,
    minimum: int = 1,
    maximum: int = 12,
) -> np.ndarray:
    """Generate active stone quantities across the complete ``minimum..maximum`` range.

    ``mean`` controls the exact rounded total, not an artificial interval of
    allowed values.  At the midpoint the distribution is uniform.  Away from
    it, an exponential tilt progressively favours fuller or emptier piles;
    every active state keeps a non-zero statistical probability, without
    forcing one occurrence of each state in a finite map.  The zero/exhausted
    state is deliberately outside this helper.
    """

    count = int(count)
    minimum = int(minimum)
    maximum = int(maximum)
    if count <= 0:
        return np.zeros(0, dtype=np.int16)
    if minimum > maximum:
        raise ValueError("minimum quantity must not exceed maximum quantity")

    mean = min(float(maximum), max(float(minimum), float(mean)))
    target_total = int(round(mean * count))
    if mean <= float(minimum):
        return np.full(count, minimum, dtype=np.int16)
    if mean >= float(maximum):
        return np.full(count, maximum, dtype=np.int16)

    states = np.arange(minimum, maximum + 1, dtype=np.int16)
    probabilities = _tilted_quantity_probabilities(states, mean)
    quantities = rng.choice(
        states,
        size=count,
        replace=True,
        p=probabilities,
    ).astype(np.int16)
    return _balance_quantity_total(
        quantities,
        target_total,
        rng,
        minimum=minimum,
        maximum=maximum,
    )


def _resource_quantities(count: int, mean: int, rng: np.random.Generator) -> np.ndarray:
    """Use the native spread at mean 8 and a bounded spread otherwise.

    Legacy's observed low nibble is a flat ``1..15`` draw (mean 8).  Custom
    values other than that native default, including Upgraded's requested mean
    10, use the editable bounded distribution while preserving the requested
    average and the format limits.
    """

    count = int(count)
    if count <= 0:
        return np.zeros(0, dtype=np.uint8)
    mean = max(RESOURCE_MINIMUM, min(RESOURCE_MAXIMUM, int(mean)))
    if mean == 8:
        return rng.integers(
            RESOURCE_MINIMUM,
            RESOURCE_MAXIMUM + 1,
            count,
            dtype=np.uint8,
        )
    return _bounded_quantities(count, mean, rng)


def _largest_hex_component(points: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """Return the largest HEX6-connected component in ``points``."""

    remaining = set(points)
    largest: set[tuple[int, int]] = set()
    while remaining:
        seed = min(remaining)
        remaining.remove(seed)
        component = {seed}
        stack = [seed]
        while stack:
            x, y = stack.pop()
            for delta_x, delta_y in HEX6:
                neighbour = (x + int(delta_x), y + int(delta_y))
                if neighbour not in remaining:
                    continue
                remaining.remove(neighbour)
                component.add(neighbour)
                stack.append(neighbour)
        if len(component) > len(largest):
            largest = component
    return largest


def _legacy_pattern_cells(
    support: np.ndarray,
    occupied: np.ndarray,
    bank: np.ndarray,
    origin_row: int,
    origin_col: int,
    pattern_count: int,
    fill_probability: float,
    rng: np.random.Generator,
) -> list[tuple[int, int]]:
    """Select a compact connected prefix from one native pattern stamp.

    The native bank is ordered from the centre outwards.  The former
    Custom implementation independently accepted each bank record, turning a
    valid stamp into isolated pixels.  Here the same bank remains the shape
    envelope, but selection grows from one seed through HEX6 neighbours.  A
    small rank/noise term keeps the result irregular without breaking
    connectivity.
    """

    height, width = support.shape
    ranked: dict[tuple[int, int], int] = {}
    for rank, (delta_row, delta_col) in enumerate(bank[: int(pattern_count)]):
        row = int(origin_row) + int(delta_row)
        col = int(origin_col) + int(delta_col)
        if not (1 <= row < height - 1 and 1 <= col < width - 1):
            continue
        if support[row, col] and not occupied[row, col]:
            ranked.setdefault((col, row), int(rank))
    if not ranked:
        return []

    component = _largest_hex_component(set(ranked))
    if not component:
        return []
    desired = min(
        len(component),
        max(1, int(round(int(pattern_count) * float(fill_probability)))),
    )
    seed = min(component, key=lambda point: (ranked[point], point[1], point[0]))
    noise = {point: float(rng.random()) for point in component}

    def priority(point: tuple[int, int]) -> float:
        x, y = point
        radial = abs(x - int(origin_col)) + abs(y - int(origin_row))
        return 0.18 * radial + 0.012 * ranked[point] + 0.35 * noise[point]

    chosen = [seed]
    chosen_set = {seed}
    frontier: list[tuple[float, int, int]] = []

    def add_frontier(x: int, y: int) -> None:
        for delta_x, delta_y in HEX6:
            point = (x + int(delta_x), y + int(delta_y))
            if point in component and point not in chosen_set:
                if not any(item[1] == point[0] and item[2] == point[1] for item in frontier):
                    heapq.heappush(frontier, (priority(point), point[0], point[1]))

    add_frontier(*seed)
    while frontier and len(chosen) < desired:
        _, x, y = heapq.heappop(frontier)
        point = (x, y)
        if point in chosen_set:
            continue
        chosen_set.add(point)
        chosen.append(point)
        add_frontier(x, y)
    return chosen


def _legacy_fallback_cells(
    support: np.ndarray,
    occupied: np.ndarray,
    target: int,
    rng: np.random.Generator,
    patch_limit: int = 64,
    patch_sizes: list[int] | None = None,
) -> list[tuple[int, int]]:
    """Fill unusual support with bounded connected fallback patches.

    A single flood-fill of the complete shortfall becomes one artificial blob
    as soon as the native pattern bank cannot find enough valid stamps.  Keep
    the fallback deterministic, but split it into Legacy-sized patches so the
    occupancy control does not change the method into a pixel soup or a
    continent-sized deposit.
    """

    needed = max(0, int(target))
    reserved = np.zeros_like(support, dtype=bool)
    result: list[tuple[int, int]] = []
    height, width = support.shape
    patch_limit = max(1, int(patch_limit))
    while needed:
        available = np.argwhere(support & ~occupied & ~reserved)
        if len(available) == 0:
            break
        row, col = map(int, available[int(rng.integers(0, len(available)))])
        local: list[tuple[int, int]] = []
        frontier = [(col, row)]
        seen = {(col, row)}
        desired = min(needed, patch_limit)
        while frontier and len(local) < desired:
            index = int(rng.integers(0, len(frontier)))
            x, y = frontier.pop(index)
            if not (0 <= x < width and 0 <= y < height):
                continue
            if not support[y, x] or occupied[y, x] or reserved[y, x]:
                continue
            reserved[y, x] = True
            local.append((x, y))
            for delta_x, delta_y in rng.permutation(HEX6):
                neighbour_x = x + int(delta_x)
                neighbour_y = y + int(delta_y)
                neighbour = (neighbour_x, neighbour_y)
                if (
                    0 <= neighbour_x < width
                    and 0 <= neighbour_y < height
                    and neighbour not in seen
                    and support[neighbour_y, neighbour_x]
                    and not occupied[neighbour_y, neighbour_x]
                    and not reserved[neighbour_y, neighbour_x]
                ):
                    seen.add(neighbour)
                    frontier.append(neighbour)
        result.extend(local)
        if local and patch_sizes is not None:
            patch_sizes.append(len(local))
        needed -= len(local)
    return result


def _place_legacy_minerals(
    terrain: np.ndarray,
    resources: np.ndarray,
    minerals: Mapping[str, Any],
    rng: np.random.Generator,
    *,
    excluded_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Place minerals with the calibrated native R17 method.

    This is the last procedural Legacy implementation before the native game
    pipeline replaced it (commit ``90175ee``).  It paints independent random
    HEX6 zones in coal → iron → gold → gems → sulfur order.  Later families
    may overwrite earlier ones; each family only prevents duplicate *new*
    cells in its own historical paint goal.  The final quota closure below is
    an explicit Custom guarantee, so an occupancy value remains literal even
    when random inter-family overlaps leave holes.
    """

    resources[:] = 0
    support = np.isin(terrain, (32, 33, 34, 35, 128, 129))
    if excluded_mask is not None:
        support &= ~np.asarray(excluded_mask, dtype=bool)
    support_count = int(np.count_nonzero(support))
    requested_occupancy = max(
        0.0,
        min(100.0, float(minerals.get("occupancy_percent", 0.0))),
    )
    total = min(
        support_count,
        int(round(support_count * requested_occupancy / 100.0)),
    )
    targets = _target_by_share(total, minerals.get("shares", {}))
    variation = str(minerals.get("size_variation", "normal"))
    radius_choices = (3, 4, 5)
    radius_weights = {
        "low": (0.50, 0.40, 0.10),
        "normal": (0.30, 0.50, 0.20),
        "high": (0.15, 0.50, 0.35),
    }.get(variation, (0.30, 0.50, 0.20))
    fill_minima = {
        0x10: 0.20,
        0x20: 0.26,
        0x30: 0.29,
        0x40: 0.28,
        0x50: 0.29,
    }
    mineral_families = tuple(int(value) for value in MINERAL_IDS.values())
    average_quantity = minerals.get("average_quantity", {})
    height, width = terrain.shape

    def hex_disk_area(radius: int) -> int:
        radius = max(0, int(radius))
        return 1 + 3 * radius * (radius + 1)

    def hex_distance_mask(
        origin_x: int,
        origin_y: int,
        radius: int,
        xx: np.ndarray,
        yy: np.ndarray,
    ) -> np.ndarray:
        delta_x, delta_y = xx - origin_x, yy - origin_y
        distance = np.where(
            delta_x * delta_y >= 0,
            np.maximum(np.abs(delta_x), np.abs(delta_y)),
            np.abs(delta_x) + np.abs(delta_y),
        )
        return distance <= int(radius)

    def random_available(available: np.ndarray) -> tuple[int, int] | None:
        for _ in range(256):
            row = int(rng.integers(height))
            col = int(rng.integers(width))
            if available[row, col]:
                return col, row
        rows, cols = np.where(available)
        if not len(cols):
            return None
        index = int(rng.integers(len(cols)))
        return int(cols[index]), int(rows[index])

    def choose_radius() -> int:
        weights = np.maximum(np.asarray(radius_weights, dtype=np.float64), 0.0)
        total_weight = float(weights.sum())
        if total_weight <= 0.0:
            weights = np.full(len(radius_choices), 1.0 / len(radius_choices))
        else:
            weights /= total_weight
        return int(rng.choice(np.asarray(radius_choices, dtype=np.int16), p=weights))

    def choose_fill(family: int) -> float:
        low = max(0.0, min(1.0, fill_minima[family]))
        # R16/R17 deliberately used a uniform draw up to a complete HEX.
        return float(rng.uniform(low, 1.0))

    def random_hex_selection(
        candidate: np.ndarray,
        origin_x: int,
        origin_y: int,
        start: tuple[int, int],
        count: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        if count <= 0:
            return np.empty(0, dtype=np.int32), np.empty(0, dtype=np.int32)
        rows, cols = np.where(candidate)
        if len(cols) <= count:
            return rows.astype(np.int32), cols.astype(np.int32)
        local_centre = (int(start[1] - origin_y), int(start[0] - origin_x))
        centre = np.flatnonzero(
            (rows == local_centre[0]) & (cols == local_centre[1])
        )
        centre_index = int(centre[0]) if len(centre) else int(rng.integers(len(rows)))
        remaining = np.delete(np.arange(len(rows), dtype=np.int32), centre_index)
        selected = rng.choice(remaining, size=max(0, count - 1), replace=False)
        indices = np.concatenate((np.asarray([centre_index], dtype=np.int32), selected))
        rng.shuffle(indices)
        return rows[indices].astype(np.int32), cols[indices].astype(np.int32)

    def family_paint_goals() -> dict[str, int]:
        """Compensate expected sequential overwrites as R16/R17 did."""

        if support_count <= 0:
            return {key: 0 for key in MINERAL_KEYS}
        survival = 1.0
        goals: dict[str, int] = {}
        for key in reversed(MINERAL_KEYS):
            desired = max(0.0, float(targets[key]) / support_count)
            probability = min(0.98, desired / max(survival, 1e-9))
            goals[key] = int(round(probability * support_count))
            survival *= max(0.0, 1.0 - probability)
        return goals

    def paint_random_hex_zone(
        zone_support: np.ndarray,
        family: int,
        family_mask: np.ndarray,
        radius: int,
        fill: float,
        remaining_goal: int,
        quantity_mean: int,
    ) -> tuple[int, int, int, tuple[int, int] | None, int, int, int]:
        start = random_available(zone_support & ~family_mask)
        if start is None:
            return 0, 0, 0, None, int(radius), 0, 0
        x_start, x_stop = max(0, start[0] - radius), min(width, start[0] + radius + 1)
        y_start, y_stop = max(0, start[1] - radius), min(height, start[1] + radius + 1)
        local_x, local_y = np.meshgrid(
            np.arange(x_start, x_stop),
            np.arange(y_start, y_stop),
        )
        local_disk = hex_distance_mask(start[0], start[1], radius, local_x, local_y)
        candidate = zone_support[y_start:y_stop, x_start:x_stop] & local_disk
        capacity = int(candidate.sum())
        if not capacity:
            return 0, 0, 0, None, int(radius), 0, 0
        painted = max(1, int(round(capacity * float(fill))))
        painted = min(capacity, painted)
        if remaining_goal > 0:
            painted = min(painted, max(1, int(remaining_goal)))
        chosen_y, chosen_x = random_hex_selection(
            candidate,
            x_start,
            y_start,
            start,
            painted,
        )
        rows, cols = chosen_y + y_start, chosen_x + x_start
        previous_families = resources[rows, cols] & 0xF0
        previous_written = family_mask[rows, cols].copy()
        overwritten = int(
            np.count_nonzero(
                (previous_families != 0) & (previous_families != int(family))
            )
        )
        quantities = _resource_quantities(painted, quantity_mean, rng)
        resources[rows, cols] = int(family) | quantities
        family_mask[rows, cols] = True
        new_cells = int(np.count_nonzero(~previous_written))
        return (
            painted,
            new_cells,
            overwritten,
            start,
            int(radius),
            capacity,
            int(quantities.sum()),
        )

    paint_goals = family_paint_goals()
    details: dict[str, Any] = {}
    for key, family in MINERAL_SPECS:
        goal = int(paint_goals[key])
        family_mask = np.zeros_like(support, dtype=bool)
        painted = 0
        written = 0
        overwritten = 0
        zones = 0
        attempts = 0
        zone_sizes: list[int] = []
        fill_values: list[float] = []
        quantity_sum = 0
        quantity_count = 0
        radius_counts = {str(radius): 0 for radius in radius_choices}
        minimum_progress = max(1, int(round(hex_disk_area(3) * fill_minima[family])))
        max_attempts = max(
            256,
            int(math.ceil(max(1, goal) / minimum_progress)) * 8,
        )
        while written < goal and attempts < max_attempts:
            radius = choose_radius()
            fill = choose_fill(family)
            done, new_cells, replaced, _start, actual_radius, _capacity, quantity_sum_delta = paint_random_hex_zone(
                support,
                family,
                family_mask,
                radius,
                fill,
                goal - written,
                int(average_quantity.get(key, 8)),
            )
            attempts += 1
            if not done:
                break
            painted += done
            written += new_cells
            overwritten += replaced
            zones += 1
            zone_sizes.append(done)
            fill_values.append(fill)
            quantity_sum += quantity_sum_delta
            quantity_count += done
            radius_counts[str(actual_radius)] += 1
        details[key] = {
            "target": int(targets[key]),
            "paint_goal": goal,
            "painted": painted,
            "written": written,
            "placed": written,
            "shortfall": max(0, goal - written),
            "pattern_attempts": attempts,
            "fallback_cells": 0,
            "closure_cells": 0,
            "deposit_count": zones,
            "deposit_size_range": [
                min(zone_sizes) if zone_sizes else 0,
                max(zone_sizes) if zone_sizes else 0,
            ],
            "radius_counts": radius_counts,
            "overwritten_previous": overwritten,
            "fill_distribution": "uniform",
            "fill_range": [
                min(fill_values) if fill_values else 0.0,
                max(fill_values) if fill_values else 0.0,
            ],
            "quantity_mean": quantity_sum / quantity_count if quantity_count else 0.0,
        }

    closure_cells = 0
    closure_zones = 0
    trimmed_cells = 0
    while True:
        final_families = resources & 0xF0
        final_mask = np.isin(final_families, mineral_families)
        current_total = int(np.count_nonzero(final_mask))
        if current_total >= total:
            break
        final_counts = {
            key: int(np.count_nonzero(final_families == int(family)))
            for key, family in MINERAL_SPECS
        }
        deficits = {
            key: max(0, int(targets[key]) - final_counts[key])
            for key in MINERAL_KEYS
        }
        eligible_families = [key for key in MINERAL_KEYS if deficits[key] > 0]
        if not eligible_families:
            eligible_families = [key for key in MINERAL_KEYS if targets[key] > 0]
        if not eligible_families:
            break
        key = max(eligible_families, key=lambda item: (deficits[item], -MINERAL_KEYS.index(item)))
        family = int(MINERAL_IDS[key])
        empty_support = support & ~final_mask
        family_mask = np.zeros_like(support, dtype=bool)
        radius = choose_radius()
        done, new_cells, _replaced, _start, actual_radius, _capacity, _quantity_sum = paint_random_hex_zone(
            empty_support,
            family,
            family_mask,
            radius,
            1.0,
            total - current_total,
            int(average_quantity.get(key, 8)),
        )
        if not done or not new_cells:
            rows, cols = np.where(empty_support)
            if not len(cols):
                break
            index = int(rng.integers(len(cols)))
            quantity = _resource_quantities(1, int(average_quantity.get(key, 8)), rng)[0]
            resources[int(rows[index]), int(cols[index])] = family | int(quantity)
            done = new_cells = 1
            actual_radius = 0
        closure_cells += new_cells
        closure_zones += 1
        details[key]["closure_cells"] += new_cells
        details[key]["placed"] += new_cells
        details[key]["deposit_count"] += 1
        details[key]["deposit_size_range"][0] = min(
            details[key]["deposit_size_range"][0] or done,
            done,
        )
        details[key]["deposit_size_range"][1] = max(
            details[key]["deposit_size_range"][1],
            done,
        )
        if actual_radius in radius_choices:
            details[key]["radius_counts"][str(actual_radius)] += 1

    final_families = resources & 0xF0
    final_mask = np.isin(final_families, mineral_families)
    final_total = int(np.count_nonzero(final_mask))
    if final_total > total:
        excess = final_total - total
        removable: list[tuple[int, int]] = []
        current_counts = {
            key: int(np.count_nonzero(final_families == int(family)))
            for key, family in MINERAL_SPECS
        }
        preferred = np.zeros_like(final_mask)
        for key, family in MINERAL_SPECS:
            preferred |= (final_families == int(family)) & (
                current_counts[key] > int(targets[key])
            )
        rows, cols = np.where(preferred if np.any(preferred) else final_mask)
        order = rng.permutation(len(cols))
        for index in order[:excess]:
            removable.append((int(rows[index]), int(cols[index])))
        for row, col in removable:
            resources[row, col] = 0
        trimmed_cells = len(removable)
        final_families = resources & 0xF0
        final_mask = np.isin(final_families, mineral_families)
        final_total = int(np.count_nonzero(final_mask))

    final_counts = {
        key: int(np.count_nonzero(final_families == int(family)))
        for key, family in MINERAL_SPECS
    }
    for key in MINERAL_KEYS:
        details[key]["final_cells"] = final_counts[key]
        details[key]["final_shortfall"] = max(0, int(targets[key]) - final_counts[key])

    return {
        "model": "custom_legacy_hex_zones_r17",
        "historical_source": "v2.0 DEV_1_R17 / commit 90175ee",
        "algorithm": "legacy",
        "support_cells": support_count,
        "target_total": total,
        "placed_total": final_total,
        "final_total": final_total,
        "targets": targets,
        "paint_goals": paint_goals,
        "families": details,
        "size_variation": variation,
        "radius_choices": list(radius_choices),
        "radius_weights": list(radius_weights),
        "placement": "sequential_random_hex_zones_uniform_fill",
        "fill_distribution": "uniform_min_to_complete_hex",
        "quota_closure_cells": closure_cells,
        "quota_closure_zones": closure_zones,
        "quota_trimmed_cells": trimmed_cells,
        "occupancy_percent": requested_occupancy,
        "actual_occupancy_percent": (
            final_total / support_count * 100.0 if support_count else 0.0
        ),
    }


def _place_upgraded_minerals(
    terrain: np.ndarray,
    resources: np.ndarray,
    minerals: Mapping[str, Any],
    rng: np.random.Generator,
    shape_space: str = "parallelogram_compensated",
    excluded_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Place the user-configured Upgraded-style connected deposits."""

    support = np.isin(terrain, [32, 34, 35, SNOW_TRANS, SNOW])
    if excluded_mask is not None:
        support &= ~np.asarray(excluded_mask, dtype=bool)
    support_count = int(support.sum())
    total = int(round(support_count * float(minerals.get("occupancy_percent", 0.0)) / 100.0))
    targets = _target_by_share(total, minerals.get("shares", {}))
    variation = str(minerals.get("size_variation", "normal"))
    low, high = _size_bounds(variation, "upgraded")
    occupied = np.zeros_like(support, dtype=bool)
    details: dict[str, Any] = {}
    for key, family in MINERAL_SPECS:
        target = int(targets[key])
        family_profile = {"cells": target, "blobs": max(1, round(target / 55))}
        sizes = _make_blob_sizes(target, family_profile["blobs"], rng, low, high)
        cells_for_family: list[tuple[int, int]] = []
        fallback = 0
        for size in sizes:
            cells = _grow_upgraded_blob(support, occupied, size, rng, shape_space)
            if cells is None:
                available = np.argwhere(support & ~occupied)
                if not len(available):
                    continue
                count = min(int(size), len(available))
                selected = available[rng.choice(len(available), count, replace=False)]
                cells = [(int(col), int(row)) for row, col in selected]
                fallback += len(cells)
            for col, row in cells:
                occupied[row, col] = True
            cells_for_family.extend(cells)
        quantities = _resource_quantities(
            len(cells_for_family),
            int(minerals.get("average_quantity", {}).get(key, 10)),
            rng,
        )
        for (col, row), quantity in zip(cells_for_family, quantities):
            resources[row, col] = int(family) | int(quantity)
        details[key] = {
            "target": target,
            "placed": len(cells_for_family),
            "blob_count": len(sizes),
            "fallback_cells": fallback,
        }
    return {
        "model": "custom_upgraded_connected_blobs",
        "algorithm": "upgraded",
        "support_cells": support_count,
        "target_total": total,
        "placed_total": int(sum(item["placed"] for item in details.values())),
        "targets": targets,
        "families": details,
        "size_variation": variation,
        "shape_space": shape_space,
    }


def _place_random_minerals(
    terrain: np.ndarray,
    resources: np.ndarray,
    minerals: Mapping[str, Any],
    rng: np.random.Generator,
    *,
    support_ids: tuple[int, ...] = (32, 33, 34, 35, 128, 129),
    excluded_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Place one mineral pixel at a time, uniformly over valid terrain.

    This deliberately has no deposit shape, radius, growth or overlap pass:
    the requested occupied cells are sampled once from the compatible terrain
    and then split between mineral families according to their shares.  It is
    consequently the fastest and most dispersed Custom strategy.
    """

    resources[:] = 0
    support = np.isin(terrain, support_ids)
    if excluded_mask is not None:
        support &= ~np.asarray(excluded_mask, dtype=bool)
    support_cells = int(np.count_nonzero(support))
    requested_occupancy = max(
        0.0,
        min(100.0, float(minerals.get("occupancy_percent", 0.0))),
    )
    target_total = min(
        support_cells,
        int(round(support_cells * requested_occupancy / 100.0)),
    )
    targets = _target_by_share(target_total, minerals.get("shares", {}))
    average_quantity = minerals.get("average_quantity", {})
    flat_support = np.flatnonzero(support.ravel())
    selected = (
        flat_support[rng.permutation(len(flat_support))[:target_total]]
        if target_total
        else np.empty(0, dtype=np.intp)
    )
    # ``MapState.resources`` is a strided view over the interleaved six-byte
    # Area array, so ``ravel()`` may return a detached copy.  Assign through
    # the flat iterator instead; it preserves the logical row-major indices
    # while writing back to the original resource channel.
    flat_resources = resources.flat
    details: dict[str, Any] = {}
    offset = 0
    for key, family in MINERAL_SPECS:
        target = int(targets[key])
        points = selected[offset:offset + target]
        quantities = _resource_quantities(
            len(points),
            int(average_quantity.get(key, UPGRADED_RESOURCE_MEAN)),
            rng,
        )
        if len(points):
            flat_resources[points] = int(family) | quantities
        details[key] = {
            "target": target,
            "placed": int(len(points)),
            "pixel_count": int(len(points)),
            "quantity_mean": float(np.mean(quantities)) if len(quantities) else 0.0,
        }
        offset += target

    final_families = resources & 0xF0
    final_mask = np.isin(final_families, tuple(int(value) for value in MINERAL_IDS.values()))
    final_total = int(np.count_nonzero(final_mask))
    final_counts = {
        key: int(np.count_nonzero(final_families == int(family)))
        for key, family in MINERAL_SPECS
    }
    for key in MINERAL_KEYS:
        details[key]["final_cells"] = final_counts[key]

    return {
        "model": "custom_random_scatter_pixels",
        "algorithm": "random",
        "support_cells": support_cells,
        "target_total": target_total,
        "placed_total": final_total,
        "final_total": final_total,
        "targets": targets,
        "families": details,
        "size_variation": str(minerals.get("size_variation", "normal")),
        "placement": "uniform_random_independent_pixels",
        "fill_distribution": "none",
        "support_ids": [int(value) for value in support_ids],
        "occupancy_percent": requested_occupancy,
        "actual_occupancy_percent": (
            final_total / support_cells * 100.0 if support_cells else 0.0
        ),
    }


def _shore_distances(terrain: np.ndarray) -> np.ndarray:
    """Return unrestricted HEX6 distances from each water cell to a shore."""

    water = np.isin(terrain, WATER_IDS)
    shore = terrain == 48
    distance = np.full(terrain.shape, 32767, dtype=np.int32)
    seed = water & (neighbor_count(shore) > 0)
    queue: deque[tuple[int, int]] = deque()
    for row, col in np.argwhere(seed):
        row, col = int(row), int(col)
        distance[row, col] = 1
        queue.append((col, row))
    side = terrain.shape[0]
    while queue:
        col, row = queue.popleft()
        next_distance = int(distance[row, col]) + 1
        for delta_col, delta_row in HEX6:
            next_col, next_row = col + delta_col, row + delta_row
            if not (0 <= next_col < side and 0 <= next_row < side):
                continue
            if water[next_row, next_col] and next_distance < distance[next_row, next_col]:
                distance[next_row, next_col] = next_distance
                queue.append((next_col, next_row))
    return distance


def _select_uniform(candidates: np.ndarray, target: int, rng: np.random.Generator) -> np.ndarray:
    if target >= len(candidates):
        return candidates
    return candidates[rng.choice(len(candidates), int(target), replace=False)]


def _place_custom_fish(
    terrain: np.ndarray,
    resources: np.ndarray,
    fish: Mapping[str, Any],
    rng: np.random.Generator,
    *,
    excluded_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Place fish uniformly in the selected global or coastal-band pool."""

    water = np.isin(terrain, WATER_IDS)
    river = np.isin(terrain, RIVER_IDS)
    border = np.zeros_like(water, dtype=bool)
    border[[0, -1], :] = True
    border[:, [0, -1]] = True
    eligible = water & ~river & ~border
    if excluded_mask is not None:
        eligible &= ~np.asarray(excluded_mask, dtype=bool)
    resources[water] = 0
    resources[river] = 0
    eligible_points = np.argwhere(eligible)
    near_shore = bool(fish.get("near_shore", False))
    fill_percent = min(100.0, max(0.0, float(fish.get("fill_percent", 0.0))))
    band_thickness = max(1, int(fish.get("band_thickness", 12)))
    distances = _shore_distances(terrain) if near_shore else None
    candidates = eligible_points
    coastal_band_cells = 0
    max_reachable: int | None = None
    near_shore_effective = False
    selection_mode = "global_uniform"

    if near_shore and distances is not None:
        finite_values = distances[eligible]
        finite_values = finite_values[finite_values < 32767]
        if len(finite_values):
            max_reachable = int(finite_values.max())
        if len(finite_values) and band_thickness <= int(max_reachable):
            coastal_mask = eligible & (distances >= 1) & (distances <= band_thickness)
            coastal_band = np.argwhere(coastal_mask)
            coastal_band_cells = int(len(coastal_band))
            if coastal_band_cells:
                candidates = coastal_band
                near_shore_effective = True
                selection_mode = "coastal_band_uniform"
        elif not len(finite_values):
            selection_mode = "global_uniform_no_shore"
        else:
            selection_mode = "global_uniform_band_exceeded"

    target = int(round(len(candidates) * fill_percent / 100.0))
    target = min(max(0, target), len(candidates))
    chosen = _select_uniform(candidates, target, rng) if target else candidates[:0]

    quantities = _resource_quantities(
        len(chosen),
        int(fish.get("average_quantity", 10)),
        rng,
    )
    for (row, col), quantity in zip(chosen, quantities):
        resources[int(row), int(col)] = int(quantity)
    return {
        "model": "custom_global_or_coastal_band",
        "cells": int(len(chosen)),
        "target_cells": target,
        "eligible_cells": int(len(eligible_points)),
        "candidate_cells": int(len(candidates)),
        "coastal_band_cells": coastal_band_cells,
        "fill_percent": fill_percent,
        "fill_basis": "coastal_band" if near_shore_effective else "eligible_water",
        "near_shore_requested": near_shore,
        "near_shore_effective": near_shore_effective,
        "band_thickness_requested": band_thickness if near_shore else None,
        "band_thickness_effective": band_thickness if near_shore_effective else None,
        "max_reachable_shore_distance": max_reachable,
        "selection_mode": selection_mode,
        "quantity_mean": float(np.mean(quantities)) if len(quantities) else 0.0,
    }


def apply_custom_resource_sections(
    state,
    sections: Mapping[str, Any],
    rng: np.random.Generator,
    *,
    shape_space: str = "parallelogram_compensated",
    excluded_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Apply the two semantic Custom sections to the resource layer."""

    fallback = {
        "minerals": {
            "algorithm": "upgraded",
            "occupancy_percent": 90.0,
            "shares": {key: 20.0 for key in MINERAL_KEYS},
            "size_variation": "normal",
            "average_quantity": {key: UPGRADED_RESOURCE_MEAN for key in MINERAL_KEYS},
        },
        "fish": {
            "fill_percent": UPGRADED_FISH_FILL_PERCENT,
            "average_quantity": UPGRADED_RESOURCE_MEAN,
            "near_shore": True,
            "band_thickness": DEFAULT_FISH_BAND_THICKNESS,
        },
    }
    selected = normalize_sections(sections, fallback=fallback)
    resources = state.resources
    resources[:] = 0
    minerals = selected["minerals"]
    if minerals["algorithm"] == "legacy":
        mineral_meta = _place_legacy_minerals(
            state.terrain,
            resources,
            minerals,
            rng,
            excluded_mask=excluded_mask,
        )
    elif minerals["algorithm"] == "random":
        mineral_meta = _place_random_minerals(
            state.terrain,
            resources,
            minerals,
            rng,
            excluded_mask=excluded_mask,
        )
    else:
        mineral_meta = _place_upgraded_minerals(
            state.terrain,
            resources,
            minerals,
            rng,
            shape_space=shape_space,
            excluded_mask=excluded_mask,
        )
    fish_meta = _place_custom_fish(
        state.terrain,
        resources,
        selected["fish"],
        rng,
        excluded_mask=excluded_mask,
    )
    return {"minerals": mineral_meta, "fish": fish_meta, "sections": selected}


__all__ = ("apply_custom_resource_sections",)
