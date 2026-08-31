"""Legacy mineral and fish layers, independent from terrain morphology input."""

from __future__ import annotations

import math

import numpy as np

from ....map_data.constants import RIVER_IDS, WATER_IDS


def _random_available(available: np.ndarray, rng: np.random.Generator) -> tuple[int, int] | None:
    side = available.shape[0]
    for _ in range(256):
        x, y = int(rng.integers(side)), int(rng.integers(side))
        if available[y, x]:
            return x, y
    ys, xs = np.where(available)
    if not len(xs):
        return None
    index = int(rng.integers(len(xs)))
    return int(xs[index]), int(ys[index])


def _random_unreserved(
    support: np.ndarray,
    reserved: np.ndarray,
    rng: np.random.Generator,
    anchor: tuple[int, int] | None = None,
    window: int = 0,
) -> tuple[int, int] | None:
    """Choose a support cell, optionally close to a preceding HEX centre.

    ``reserved`` is a same-family occupancy guard, not a complete patch
    envelope. Native-looking large deposits are made from several nearby
    envelopes, so forbidding the whole previous disk would remove the very
    overlaps that make those deposits read as groups. Selected cells remain
    unique within a family; later families can still overwrite them.
    """

    side = support.shape[0]
    if anchor is not None and window > 0:
        ax, ay = anchor
        x_start, x_stop = max(0, ax - window), min(side, ax + window + 1)
        y_start, y_stop = max(0, ay - window), min(side, ay + window + 1)
        local_x, local_y = np.meshgrid(
            np.arange(x_start, x_stop),
            np.arange(y_start, y_stop),
        )
        local_mask = (
            support[y_start:y_stop, x_start:x_stop]
            & ~reserved[y_start:y_stop, x_start:x_stop]
            & _hex_distance_mask(ax, ay, window, local_x, local_y)
        )
        local_ys, local_xs = np.where(local_mask)
        if len(local_xs):
            index = int(rng.integers(len(local_xs)))
            return int(local_xs[index] + x_start), int(local_ys[index] + y_start)
    for _ in range(512):
        x, y = int(rng.integers(side)), int(rng.integers(side))
        if support[y, x] and not reserved[y, x]:
            return x, y
    return _random_available(support & ~reserved, rng)


def _density_key(cfg: dict, players: int) -> str:
    return "low" if players <= int(cfg["density_split_players"]) else "high"


def _hex_disk_area(radius: int) -> int:
    """Return the number of cells in a compact HEX disk."""

    radius = max(0, int(radius))
    return 1 + 3 * radius * (radius + 1)


def _choose_mineral_radius(cfg: dict, rng: np.random.Generator) -> int:
    """Choose one of the measured native-like radii, never a giant envelope."""

    choices = tuple(int(value) for value in cfg.get("mineral_hex_radius_choices", (3, 4, 5)))
    weights = np.asarray(
        cfg.get("mineral_hex_radius_weights", (0.30, 0.50, 0.20)),
        dtype=np.float64,
    )
    if not choices or len(weights) != len(choices) or any(value < 1 for value in choices):
        choices = (3, 4, 5)
        weights = np.asarray((0.30, 0.50, 0.20), dtype=np.float64)
    weights = np.maximum(weights, 0.0)
    total = float(weights.sum())
    if total <= 0.0:
        weights = np.full(len(choices), 1.0 / len(choices), dtype=np.float64)
    else:
        weights /= total
    return int(rng.choice(np.asarray(choices, dtype=np.int16), p=weights))


def _hex_patch_sizes(target: int, cfg: dict, scale: float, rng: np.random.Generator) -> list[int]:
    """Sample the painted-cell sizes of the native-looking HEX patches."""

    count = max(1, int(round(int(cfg["hex_count"]) * scale)))
    p25 = max(1, int(cfg["raw_p25"]))
    median = max(p25, int(cfg["raw_median"]))
    p75 = max(median, int(cfg["raw_p75"]))
    p90 = max(p75, int(cfg["raw_p90"]))
    p95 = max(p90, int(cfg["raw_p95"]))
    p99 = max(p95, int(cfg["raw_p99"]))
    maximum = max(p99, int(cfg["raw_max"]))
    quantiles = rng.random(count)
    sizes = np.empty(count, dtype=np.int32)
    bands = (
        (quantiles < .25, 1, p25),
        ((quantiles >= .25) & (quantiles < .50), p25, median),
        ((quantiles >= .50) & (quantiles < .75), median, p75),
        ((quantiles >= .75) & (quantiles < .90), p75, p90),
        ((quantiles >= .90) & (quantiles < .95), p90, p95),
        ((quantiles >= .95) & (quantiles < .99), p95, p99),
    )
    for mask, low, high in bands:
        sizes[mask] = rng.integers(low, high + 1, int(mask.sum()))
    tail = quantiles >= .99
    tail_count = int(tail.sum())
    if tail_count:
        sizes[tail] = np.rint(p99 * np.exp(rng.uniform(0.0, math.log(maximum / p99), tail_count))).astype(np.int32)
    # The SAV quantiles describe final grouped cells, not a literal radius
    # for every native hex.  Keep their signal for the fill curve, but damp
    # the conversion into individual envelopes: native-looking diversity is
    # carried mainly by fill and sequential overwrites, not giant radii.
    spread = float(cfg.get("size_spread", 0.22))
    spread = max(0.0, min(1.0, spread))
    mean = max(1.0, float(target) / max(1, count))
    sizes = np.rint(mean + (sizes.astype(np.float64) - mean) * spread).astype(np.int32)
    sizes = np.maximum(sizes, 1)
    difference = int(target - sizes.sum())
    order = np.argsort(sizes)[::-1]
    if difference > 0:
        base, remainder = divmod(difference, count)
        sizes += base
        sizes[order[:remainder]] += 1
    elif difference < 0:
        for index in order:
            if difference == 0:
                break
            removable = min(int(sizes[index] - 1), -difference)
            sizes[index] -= removable
            difference += removable
    return [int(size) for size in sizes]


def _hex_patch_fill(raw_size: int, cfg: dict, rng: np.random.Generator) -> float:
    """Return a size-dependent fill rate, with native-like local variation."""

    breakpoints = np.log(np.asarray((1, 10, 20, 50, 100, 1000), dtype=np.float64))
    curve = np.asarray(cfg["fill_curve"], dtype=np.float64)
    value = float(np.interp(math.log(max(1, raw_size)), breakpoints, curve))
    low = float(cfg.get("fill_min", 0.08))
    high = float(cfg.get("fill_max", 0.70))
    if high < low:
        low, high = high, low
    return float(np.clip(value + rng.normal(0.0, float(cfg["fill_jitter"])), low, high))


def _hex_distance_mask(x0: int, y0: int, radius: int, xx: np.ndarray, yy: np.ndarray) -> np.ndarray:
    """Return a compact axial-style HEX disk around one map cell."""

    dx, dy = xx - x0, yy - y0
    distance = np.where(
        dx * dy >= 0,
        np.maximum(np.abs(dx), np.abs(dy)),
        np.abs(dx) + np.abs(dy),
    )
    return distance <= radius


def _mark_hex_disk(reserved: np.ndarray, x0: int, y0: int, radius: int) -> None:
    """Reserve one patch envelope locally for the current family only."""

    side = reserved.shape[0]
    x_start, x_stop = max(0, x0 - radius), min(side, x0 + radius + 1)
    y_start, y_stop = max(0, y0 - radius), min(side, y0 + radius + 1)
    local_x, local_y = np.meshgrid(
        np.arange(x_start, x_stop),
        np.arange(y_start, y_stop),
    )
    reserved[y_start:y_stop, x_start:x_stop] |= _hex_distance_mask(
        x0,
        y0,
        radius,
        local_x,
        local_y,
    )


def _compact_hex_selection(
    candidate: np.ndarray,
    origin_x: int,
    origin_y: int,
    start: tuple[int, int],
    count: int,
    rng: np.random.Generator,
    local_coherence: float = 0.48,
    compactness_bias: float = 0.30,
) -> tuple[np.ndarray, np.ndarray]:
    """Select a locally correlated irregular subset of a HEX envelope.

    The native-looking irregularity is not a radial gradient: a low-fill HEX
    can have holes throughout its interior while still retaining short
    connected runs.  Give every candidate an independent random score, blend
    it lightly with the mean score of its HEX6 neighbours, then take the
    lowest scores.  This keeps the omissions random without reducing the
    deposit to isolated cells or a dense artificial core.
    """

    if count <= 0:
        return np.empty(0, dtype=np.int32), np.empty(0, dtype=np.int32)
    ys, xs = np.where(candidate)
    if len(xs) <= count:
        return ys.astype(np.int32), xs.astype(np.int32)

    local_start = (int(start[1] - origin_y), int(start[0] - origin_x))
    cells = [(int(y), int(x)) for y, x in zip(ys, xs)]
    available = set(cells)
    if local_start not in available:
        # This should not happen because ``start`` comes from the same
        # support/reservation mask, but retaining a deterministic fallback is
        # safer than silently dropping a patch at a terrain boundary.
        index = int(rng.integers(len(ys)))
        local_start = (int(ys[index]), int(xs[index]))

    # The score field is generated on the actual support mask, so terrain
    # holes and reservations do not create phantom neighbours.  One HEX6
    # averaging pass is deliberately weak: local runs survive, but there is
    # no preferred direction and no radial falloff from ``start``.
    raw = rng.random(len(cells))
    index_by_cell = {cell: index for index, cell in enumerate(cells)}
    neighbour_mean = raw.copy()
    for index, (cy, cx) in enumerate(cells):
        neighbours = [
            index_by_cell[(cy + dy, cx + dx)]
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1))
            if (cy + dy, cx + dx) in index_by_cell
        ]
        if neighbours:
            neighbour_mean[index] = float(np.mean(raw[neighbours]))
    coherence = max(0.0, min(1.0, float(local_coherence)))
    priorities_by_cell = (1.0 - coherence) * raw + coherence * neighbour_mean
    # A small compactness term keeps an elementary HEX readable when its fill
    # is low.  It is intentionally a minority of the score: the local random
    # field still decides most of the omissions, so this is not R13's strong
    # radial core.
    distance_by_cell = np.empty(len(cells), dtype=np.float64)
    start_y, start_x = local_start
    for index, (cell_y, cell_x) in enumerate(cells):
        dx, dy = cell_x - start_x, cell_y - start_y
        distance_by_cell[index] = (
            max(abs(dx), abs(dy)) if dx * dy >= 0 else abs(dx) + abs(dy)
        )
    max_distance = max(1.0, float(distance_by_cell.max()))
    distance_by_cell /= max_distance
    compactness = max(0.0, min(1.0, float(compactness_bias)))
    priorities_by_cell = (
        (1.0 - compactness) * priorities_by_cell
        + compactness * distance_by_cell
    )
    priorities = np.asarray(
        [priorities_by_cell[index_by_cell[cell]] for cell in cells if cell != local_start],
        dtype=np.float64,
    )
    remaining = [cell for cell in cells if cell != local_start]
    order = np.argsort(priorities, kind="stable")[: max(0, count - 1)]
    selected = [local_start] + [remaining[int(index)] for index in order]
    chosen_y = np.asarray([cell[0] for cell in selected], dtype=np.int32)
    chosen_x = np.asarray([cell[1] for cell in selected], dtype=np.int32)
    return chosen_y, chosen_x


def _paint_hex_patch(
    support: np.ndarray,
    resources: np.ndarray,
    family: int,
    raw_size: int,
    fill: float,
    rng: np.random.Generator,
    quantity_multiplier: float,
    quantity_cap: int,
    reserved: np.ndarray,
    *,
    radius: int | None = None,
    anchor: tuple[int, int] | None = None,
    anchor_window: int = 0,
    local_coherence: float = 0.48,
    compactness_bias: float = 0.30,
) -> tuple[int, int, tuple[int, int] | None, int]:
    """Paint one variably filled HEX patch, allowing intentional overwrite."""

    start = _random_unreserved(support, reserved, rng, anchor=anchor, window=anchor_window)
    if start is None:
        return 0, 0, None, 0
    # When a radius is supplied it is a measured native-like elementary HEX.
    # The old dynamic conversion of a grouped cell count into a radius is
    # intentionally retained only as a compatibility fallback for callers
    # outside the Legacy mineral planner.
    if radius is None:
        nominal_area = max(1, int(math.ceil(raw_size / max(.08, fill))))
        radius = max(1, int(math.ceil((math.sqrt(12 * nominal_area - 3) - 3) / 6)))
    radius = max(1, int(radius))
    side = support.shape[0]
    x0, x1 = max(0, start[0] - radius), min(side, start[0] + radius + 1)
    y0, y1 = max(0, start[1] - radius), min(side, start[1] + radius + 1)
    local_x, local_y = np.meshgrid(np.arange(x0, x1), np.arange(y0, y1))
    local_disk = _hex_distance_mask(start[0], start[1], radius, local_x, local_y)
    candidate = support[y0:y1, x0:x1] & ~reserved[y0:y1, x0:x1] & local_disk
    available_count = int(candidate.sum())
    if not available_count:
        return 0, 0, None, 0
    painted = min(raw_size, available_count)
    y0, x0 = max(0, start[1] - radius), max(0, start[0] - radius)
    chosen_y, chosen_x = _compact_hex_selection(
        candidate,
        x0,
        y0,
        start,
        painted,
        rng,
        local_coherence,
        compactness_bias,
    )
    py, px = chosen_y + y0, chosen_x + x0
    previous_families = resources[py, px] & 0xF0
    overwritten = int(np.count_nonzero((previous_families != 0) & (previous_families != family)))
    quantities = np.minimum(
        quantity_cap,
        np.floor(rng.integers(1, 16, painted) * quantity_multiplier + .5),
    ).astype(np.uint8)
    resources[py, px] = family | quantities
    reserved[py, px] = True
    return painted, overwritten, start, radius


def _add_minerals_r15_grouped(state, profile: dict, rng: np.random.Generator) -> dict:
    """Historical R15 grouped-pocket implementation kept for comparison only.

    The native-looking order is significant: a later family may replace a
    cell painted by an earlier one.  Consequently no ``available`` mask is
    used between families.  The active R16/R17 implementation is defined below;
    this function is deliberately not exported or called by the pipeline.
    """

    terrain, resources = state.terrain, state.resources
    resources[:] = 0
    cfg = profile["legacy_content"]["resources"]
    scale = (state.side / 768.0) ** 2
    support = np.isin(terrain, (17, 32, 33, 34, 35, 128, 129))
    density_key = _density_key(cfg, int(state.metadata["players"]))
    targets = cfg["mineral_targets_768_by_density"][density_key]
    patches = cfg["mineral_hexes_768_by_density"][density_key]
    family_counts: dict[str, int] = {}
    painted_counts: dict[str, int] = {}
    overwrite_counts: dict[str, int] = {}
    patch_counts: dict[str, int] = {}
    elementary_patch_counts: dict[str, int] = {}
    radius_counts: dict[str, dict[str, int]] = {}
    patch_shortfalls: dict[str, int] = {}
    center_gap = max(0, int(cfg.get("mineral_hex_center_gap", 1)))
    cluster_window = max(0, int(cfg.get("mineral_hex_cluster_window", 6)))
    local_coherence = max(0.0, min(1.0, float(cfg.get("mineral_hex_local_coherence", 0.48))))
    compactness_bias = max(0.0, min(1.0, float(cfg.get("mineral_hex_compactness_bias", 0.30))))
    for family_text, family_cfg in targets.items():
        family = int(family_text)
        patch_cfg = patches[family_text]
        target = int(round(int(family_cfg["cells"]) * scale * float(patch_cfg["paint_multiplier"])))
        sizes = _hex_patch_sizes(target, patch_cfg, scale, rng)
        painted = 0
        overwritten = 0
        reserved = np.zeros_like(support)
        elementary = 0
        family_radius_counts = {str(radius): 0 for radius in (3, 4, 5)}
        shortfall = 0
        for size in sizes:
            # A grouped native-looking pocket is a short chain of elementary
            # HEXes.  Its centres are close, while every elementary envelope
            # keeps the measured radius palette and its own fill rate.
            remaining = int(size)
            # Keep all elementary HEX centres of one logical pocket close to
            # one fixed seed.  Advancing the anchor after every elementary
            # HEX creates a random walk and the long ribbons visible in R14.
            pocket_anchor: tuple[int, int] | None = None
            attempts = 0
            max_attempts = max(8, remaining + 8)
            while remaining > 0 and attempts < max_attempts:
                radius = _choose_mineral_radius(cfg, rng)
                fill = _hex_patch_fill(remaining, patch_cfg, rng)
                desired = min(
                    remaining,
                    max(1, int(round(_hex_disk_area(radius) * fill))),
                )
                done, replaced, start, actual_radius = _paint_hex_patch(
                    support,
                    resources,
                    family,
                    desired,
                    fill,
                    rng,
                    float(cfg["quantity_multiplier"]),
                    int(cfg["quantity_cap"]),
                    reserved,
                    radius=radius,
                    anchor=pocket_anchor,
                    anchor_window=cluster_window,
                    local_coherence=local_coherence,
                    compactness_bias=compactness_bias,
                )
                attempts += 1
                if not done:
                    break
                remaining -= done
                painted += done
                overwritten += replaced
                elementary += 1
                family_radius_counts[str(actual_radius)] = family_radius_counts.get(str(actual_radius), 0) + 1
                if start is not None:
                    if pocket_anchor is None:
                        pocket_anchor = start
                    # Protect only the exact centre.  A full-disk reservation
                    # would prevent the nearby/overlapping elementary HEXes
                    # seen in the native masks; painted cells are already
                    # protected by _paint_hex_patch itself.
                    _mark_hex_disk(reserved, start[0], start[1], center_gap)
            shortfall += remaining
        painted_counts[f"{family:02x}"] = painted
        overwrite_counts[f"{family:02x}"] = max(0, overwritten)
        patch_counts[f"{family:02x}"] = len(sizes)
        elementary_patch_counts[f"{family:02x}"] = elementary
        radius_counts[f"{family:02x}"] = family_radius_counts
        patch_shortfalls[f"{family:02x}"] = shortfall
    final_families = resources & 0xF0
    for family_text in targets:
        family_counts[family_text] = int(np.count_nonzero(final_families == int(family_text)))
    return {
        "mineral_support_cells": int(support.sum()),
        "mineral_density_profile": density_key,
        "mineral_family_cells": family_counts,
        "mineral_painted_cells": painted_counts,
        "mineral_patch_counts": patch_counts,
        "mineral_elementary_patch_counts": elementary_patch_counts,
        "mineral_hex_radius_counts": radius_counts,
        "mineral_hex_radius_choices": list(cfg.get("mineral_hex_radius_choices", (3, 4, 5))),
        "mineral_hex_center_gap": center_gap,
        "mineral_hex_local_coherence": local_coherence,
        "mineral_hex_compactness_bias": compactness_bias,
        "mineral_patch_shortfalls": patch_shortfalls,
        "mineral_overwrite_cells": overwrite_counts,
    }


def _choose_mineral_fill_r16(
    cfg: dict,
    family: int,
    rng: np.random.Generator,
) -> float:
    """Choose a zone fill between its provisional minimum and 100 percent.

    The SAV does not retain the native minimum fill of an elementary zone.
    The values in the profile are therefore explicit provisional lower bounds,
    while the upper bound remains the measured natural maximum: a complete
    HEX.  R16/R17 intentionally uses a uniform draw in that interval so the
    effect can be inspected without another hidden curve or bias.
    """

    minimums = cfg.get("mineral_zone_fill_min_by_family", {})
    low = max(0.0, min(1.0, float(minimums.get(str(int(family)), 0.20))))
    high = max(0.0, min(1.0, float(cfg.get("mineral_zone_fill_max", 1.0))))
    if high < low:
        low, high = high, low
    distribution = str(cfg.get("mineral_zone_fill_distribution", "uniform")).lower()
    if distribution == "uniform":
        return float(rng.uniform(low, high))
    if distribution == "beta":
        alpha = max(0.05, float(cfg.get("mineral_zone_fill_beta_alpha", 2.0)))
        beta = max(0.05, float(cfg.get("mineral_zone_fill_beta_beta", 2.0)))
        return float(low + (high - low) * rng.beta(alpha, beta))
    raise ValueError(f"Unsupported mineral zone fill distribution: {distribution!r}")


def _random_hex_selection_r16(
    candidate: np.ndarray,
    origin_x: int,
    origin_y: int,
    start: tuple[int, int],
    count: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    """Select a uniformly random subset from one HEX zone.

    A radius-3/4/5 HEX6 disk is intersected with the mountain support, then a
    random fraction is painted.  Retaining the centre keeps a low-fill zone
    visible; no radial falloff, neighbour smoothing, chain, moat or
    same-family reservation is introduced.
    """

    if count <= 0:
        return np.empty(0, dtype=np.int32), np.empty(0, dtype=np.int32)
    ys, xs = np.where(candidate)
    if len(xs) <= count:
        return ys.astype(np.int32), xs.astype(np.int32)
    local_centre = (int(start[1] - origin_y), int(start[0] - origin_x))
    centre = np.flatnonzero((ys == local_centre[0]) & (xs == local_centre[1]))
    centre_index = int(centre[0]) if len(centre) else int(rng.integers(len(ys)))
    remaining = np.delete(np.arange(len(ys), dtype=np.int32), centre_index)
    selected = rng.choice(remaining, size=max(0, count - 1), replace=False)
    indices = np.concatenate((np.asarray([centre_index], dtype=np.int32), selected))
    rng.shuffle(indices)
    return ys[indices].astype(np.int32), xs[indices].astype(np.int32)


def _allocate_integer_total_r16(weights: dict[str, float], total: int) -> dict[str, int]:
    """Allocate an integer total with largest-remainder rounding."""

    keys = list(weights)
    if not keys:
        return {}
    total = max(0, int(total))
    values = np.asarray([max(0.0, float(weights[key])) for key in keys], dtype=np.float64)
    if not float(values.sum()):
        values = np.ones(len(keys), dtype=np.float64)
    raw = values / float(values.sum()) * total
    result = np.floor(raw).astype(np.int64)
    remainder = total - int(result.sum())
    if remainder > 0:
        order = np.argsort(-(raw - result), kind="stable")
        result[order[:remainder]] += 1
    return {key: int(value) for key, value in zip(keys, result)}


def _family_paint_goals_r16(
    final_targets: dict[str, int],
    support_cells: int,
) -> dict[str, int]:
    """Convert desired final family counts into sequential paint coverage."""

    if support_cells <= 0:
        return {key: 0 for key in final_targets}
    survival = 1.0
    goals: dict[str, int] = {}
    for key in reversed(list(final_targets)):
        desired_probability = max(0.0, float(final_targets[key]) / support_cells)
        probability = min(0.98, desired_probability / max(survival, 1e-9))
        goals[key] = int(round(probability * support_cells))
        survival *= max(0.0, 1.0 - probability)
    return {key: goals[key] for key in final_targets}


def _paint_random_hex_zone_r16(
    support: np.ndarray,
    resources: np.ndarray,
    family: int,
    rng: np.random.Generator,
    quantity_multiplier: float,
    quantity_cap: int,
    family_mask: np.ndarray,
    radius: int,
    fill: float,
    remaining_goal: int,
) -> tuple[int, int, int, tuple[int, int] | None, int, int]:
    """Paint one random, variably filled HEX zone for the R16/R17 candidate."""

    start = _random_available(support & ~family_mask, rng)
    if start is None:
        return 0, 0, 0, None, int(radius), 0
    radius = max(1, int(radius))
    side = support.shape[0]
    x0, x1 = max(0, start[0] - radius), min(side, start[0] + radius + 1)
    y0, y1 = max(0, start[1] - radius), min(side, start[1] + radius + 1)
    local_x, local_y = np.meshgrid(np.arange(x0, x1), np.arange(y0, y1))
    local_disk = _hex_distance_mask(start[0], start[1], radius, local_x, local_y)
    candidate = support[y0:y1, x0:x1] & local_disk
    candidate_capacity = int(candidate.sum())
    if not candidate_capacity:
        return 0, 0, 0, None, int(radius), 0
    painted = max(1, int(round(candidate_capacity * float(fill))))
    painted = min(candidate_capacity, painted)
    if remaining_goal > 0:
        painted = min(painted, max(1, int(remaining_goal)))
    chosen_y, chosen_x = _random_hex_selection_r16(
        candidate,
        x0,
        y0,
        start,
        painted,
        rng,
    )
    py, px = chosen_y + y0, chosen_x + x0
    previous_families = resources[py, px] & 0xF0
    previous_written = family_mask[py, px].copy()
    overwritten = int(np.count_nonzero((previous_families != 0) & (previous_families != family)))
    quantities = np.minimum(
        quantity_cap,
        np.floor(rng.integers(1, 16, painted) * quantity_multiplier + .5),
    ).astype(np.uint8)
    resources[py, px] = family | quantities
    family_mask[py, px] = True
    new_cells = int(np.count_nonzero(~previous_written))
    return painted, new_cells, overwritten, start, int(radius), candidate_capacity


def add_minerals(state, profile: dict, rng: np.random.Generator) -> dict:
    """Paint Legacy minerals as independent random HEX zones.

    R16/R17 follows the deliberately testable reconstruction selected from the
    SAV evidence: inner mountain support, coal → iron → gold → gems → sulfur,
    discrete radii 3/4/5, random fill between a provisional minimum and 100%,
    natural inter-family overwrites, no start halo, and a bounded loop.
    """

    terrain, resources = state.terrain, state.resources
    resources[:] = 0
    cfg = profile["legacy_content"]["resources"]
    scale = (state.side / 768.0) ** 2
    family_order = (0x10, 0x20, 0x30, 0x40, 0x50)
    support_ids = tuple(int(value) for value in cfg.get("mineral_support_ids", (32, 33, 34, 35, 128, 129)))
    support = np.isin(terrain, support_ids)
    density_key = _density_key(cfg, int(state.metadata["players"]))
    targets = cfg["mineral_targets_768_by_density"][density_key]
    profile_targets = {
        str(family): max(0.0, float(targets.get(str(family), {}).get("cells", 0)) * scale)
        for family in family_order
    }
    occupancy_target = max(0.0, min(1.0, float(cfg.get("mineral_mountain_occupancy_target", 0.53))))
    support_cells = int(support.sum())
    target_total = min(support_cells, int(round(support_cells * occupancy_target)))
    final_targets = _allocate_integer_total_r16(profile_targets, target_total)
    paint_goals = _family_paint_goals_r16(final_targets, support_cells)
    family_counts: dict[str, int] = {}
    painted_counts: dict[str, int] = {}
    written_counts: dict[str, int] = {}
    overwrite_counts: dict[str, int] = {}
    zone_counts: dict[str, int] = {}
    radius_counts: dict[str, dict[str, int]] = {}
    fill_values: dict[str, list[float]] = {}
    zone_shortfalls: dict[str, int] = {}
    max_attempt_factor = max(2, int(cfg.get("mineral_zone_attempt_limit_factor", 8)))

    for family in family_order:
        family_key = f"{family:02x}"
        goal = int(paint_goals.get(str(family), 0))
        painted = 0
        family_mask = np.zeros_like(support)
        written_count = 0
        overwritten = 0
        zones = 0
        attempts = 0
        fills: list[float] = []
        family_radius_counts = {str(radius): 0 for radius in (3, 4, 5)}
        minimum_progress = max(1, int(round(_hex_disk_area(3) * 0.20)))
        max_attempts = max(256, int(math.ceil(max(1, goal) / minimum_progress)) * max_attempt_factor)
        while written_count < goal and attempts < max_attempts:
            radius = _choose_mineral_radius(cfg, rng)
            fill = _choose_mineral_fill_r16(cfg, family, rng)
            done, new_cells, replaced, _start, actual_radius, _capacity = _paint_random_hex_zone_r16(
                support,
                resources,
                family,
                rng,
                float(cfg["quantity_multiplier"]),
                int(cfg["quantity_cap"]),
                family_mask,
                radius,
                fill,
                goal - written_count,
            )
            attempts += 1
            if not done:
                break
            painted += done
            written_count += new_cells
            overwritten += replaced
            zones += 1
            fills.append(fill)
            family_radius_counts[str(actual_radius)] += 1
        zone_shortfalls[family_key] = max(0, goal - written_count)
        painted_counts[family_key] = painted
        written_counts[family_key] = written_count
        overwrite_counts[family_key] = max(0, overwritten)
        zone_counts[family_key] = zones
        radius_counts[family_key] = family_radius_counts
        fill_values[family_key] = fills

    final_families = resources & 0xF0
    for family in family_order:
        family_counts[f"{family:02x}"] = int(np.count_nonzero(final_families == family))
    final_minerals = final_families != 0
    rocky32 = terrain == 32
    rocky32_cells = int(rocky32.sum())
    rocky32_mineral_cells = int(np.count_nonzero(final_minerals & rocky32))
    fill_summary = {
        family: {
            "count": len(values),
            "min": float(min(values)) if values else 0.0,
            "median": float(np.median(values)) if values else 0.0,
            "max": float(max(values)) if values else 0.0,
        }
        for family, values in fill_values.items()
    }
    return {
        "mineral_support_ids": list(support_ids),
        "mineral_support_cells": support_cells,
        "mineral_density_profile": density_key,
        "mineral_mountain_occupancy_target": occupancy_target,
        "mineral_mountain_target_cells": target_total,
        "mineral_mountain_final_cells": int(final_minerals.sum()),
        "mineral_mountain_occupancy": float(final_minerals.sum() / support_cells) if support_cells else 0.0,
        "mineral_rocky32_cells": rocky32_cells,
        "mineral_rocky32_mineral_cells": rocky32_mineral_cells,
        "mineral_rocky32_occupancy": float(rocky32_mineral_cells / rocky32_cells) if rocky32_cells else 0.0,
        "mineral_target_family_cells": final_targets,
        "mineral_family_paint_goals": paint_goals,
        "mineral_family_cells": family_counts,
        "mineral_painted_cells": painted_counts,
        "mineral_written_cells": written_counts,
        "mineral_patch_counts": zone_counts,
        "mineral_elementary_patch_counts": zone_counts,
        "mineral_hex_radius_counts": radius_counts,
        "mineral_hex_radius_choices": list(cfg.get("mineral_hex_radius_choices", (3, 4, 5))),
        "mineral_zone_fill_min_by_family": dict(cfg.get("mineral_zone_fill_min_by_family", {})),
        "mineral_zone_fill_max": float(cfg.get("mineral_zone_fill_max", 1.0)),
        "mineral_zone_fill_distribution": str(cfg.get("mineral_zone_fill_distribution", "uniform")),
        "mineral_zone_fill_summary": fill_summary,
        "mineral_patch_shortfalls": zone_shortfalls,
        "mineral_zone_shortfalls": zone_shortfalls,
        "mineral_overwrite_cells": overwrite_counts,
    }


def add_fish(state, profile: dict, rng: np.random.Generator) -> dict:
    """Place Legacy fish across valid water, never on rivers."""

    terrain, resources = state.terrain, state.resources
    cfg = profile["legacy_content"]["resources"]
    water = np.isin(terrain, WATER_IDS)
    river = np.isin(terrain, RIVER_IDS)
    resources[water | river] = 0
    eligible = water & ~river
    density_key = _density_key(cfg, int(state.metadata["players"]))
    target = min(int(round(int(cfg["fish_target_768_by_density"][density_key]) * (state.side / 768.0) ** 2)), int(eligible.sum()))
    selected = np.zeros_like(water)
    if target:
        ys, xs = np.where(eligible)
        chosen = rng.choice(len(xs), target, replace=False)
        selected[ys[chosen], xs[chosen]] = True
        quantity = np.minimum(
            int(cfg["quantity_cap"]),
            np.floor(rng.integers(1, 16, target) * float(cfg["quantity_multiplier"]) + .5),
        ).astype(np.uint8)
        resources[selected] = quantity
    return {
        "fish_cells": int(selected.sum()),
        "fish_target": target,
        "fish_density_profile": density_key,
    }


__all__ = ("add_minerals", "add_fish")
