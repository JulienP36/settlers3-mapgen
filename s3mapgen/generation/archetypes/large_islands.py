"""Balanced masks and independent local relief for the Great Islands archetype."""

from __future__ import annotations

from collections.abc import Callable
from heapq import heapify, heappop, heappush

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

from ...map_data.constants import (
    GRASS, HEX6, MOUNTAIN_FAMILY_IDS, RIVER_IDS, START_FOOTPRINT, SWAMP_IDS, WATER_IDS,
)
from ...map_data.hexgrid import component_labels, dilate, distance_from, hex_distance
from .masses import analyze_startable_masses
from .island_detail import add_plain_detail
from .island_simplex import simplex_signal
from .island_midpoint_r21 import midpoint_signal as midpoint_signal_r21
from .noise_sources import _ridged_multifractal, _simplex_noise

_TEAM_RIDGE_SIGNAL_WEIGHT = .28
_TEAM_CONTINENTAL_REFERENCE_SIZE = 8
_ISLAND_BASE_LAND_PERCENT = 56.5
_CONTINENTAL_LAND_REFERENCE = (
    (384, 61.77),
    (448, 67.54),
    (512, 70.33),
    (576, 74.61),
    (640, 77.08),
    (704, 78.51),
    (768, 79.78),
)
_NATIVE_EFFECTIVE_OCEAN_MARGIN = 40.26
# R61 paired ocean-only measurements (three seeds per size, both engines).
# This source-budget correction belongs to the named Continental alone;
# the historical team-island and solo-island budgets remain unchanged.
_CONTINENTAL_OCEAN_LAND_CORRECTION = (
    (256, 0.0), (384, 3.0), (512, 2.25), (768, 1.5),
)
_INLAND_LAKE_LAND_CELLS_PER_BASIN = 125_000
_INLAND_LAKE_MAX_PER_ISLAND = 3
_INLAND_LAKE_CENTER_DEPTH_FRACTION = .50
_INLAND_LAKE_MIN_DEPTH_FRACTION = .35
_INLAND_LAKE_SIGNAL_RADIUS_RATIO = .35


def _inland_lake_count(land_cells, *, distributed=True):
    """Use physical land area for small distributed basins; retain old solo policy."""
    return min(
        8 if distributed else _INLAND_LAKE_MAX_PER_ISLAND,
        max(0, int(land_cells) // (60_000 if distributed else _INLAND_LAKE_LAND_CELLS_PER_BASIN)),
    )


def _coastal_progression(depth, maximum_depth):
    """A continuous rise: almost black at sea, accelerating further inland.

    No upper envelope is intersected with an already-built height field. The
    island's depth sets the length scale, without creating a constant-height
    interior or imposing a peak at a geometric centre.
    """
    scale = max(16., float(maximum_depth) * .45)
    relative_depth = np.asarray(depth, dtype=np.float32) / scale
    return -np.expm1(-np.power(relative_depth, 2.4))


def _team_relief_parameters(team_size):
    """Scale one continuous island field gradually toward continental relief.

    Frequency follows the size of the whole team up to the eight-player
    continental scale; beyond that, growing team size does not keep subdividing
    the same map. No region, summit, or range is assigned to an individual
    player. A singleton retains the exact R52 wavelength.
    """
    count = max(1, int(team_size))
    # At the supported map limit, an eight-player team's island already uses
    # almost the full land budget. Larger teams do not need one new relief
    # scale per additional player; keep the whole-island noise at that broad
    # continental scale and let the lake count continue to grow separately.
    relief_size = min(count, _TEAM_CONTINENTAL_REFERENCE_SIZE)
    blend = float(np.log2(relief_size) / np.log2(20.))
    wavelength_ratio = .8 / relief_size ** .45
    progression_power = 1. - .55 * blend
    return float(wavelength_ratio), float(progression_power)


def _team_relief_progression(depth, maximum_depth, team_size):
    """Broaden inland elevation gradually without dividing the island."""
    # A fixed coastal band lets hills develop throughout a large island,
    # rather than scaling the coast ramp with its central depth.
    scale = min(40., max(16., float(maximum_depth) * .45))
    base = -np.expm1(-np.power(np.asarray(depth, dtype=np.float32) / scale, 2.4))
    _wavelength_ratio, progression_power = _team_relief_parameters(team_size)
    if progression_power >= 1.:
        return base
    return np.power(base, progression_power).astype(np.float32)


def _team_ridged_relief(signal, x, y, radius, seed):
    """Add one warped, island-wide ridge field to a shared team's relief.

    The ridges are a continuous noise component over the whole island, not
    regions or centers allocated to players. A broad domain warp bends their
    paths so the resulting mountain systems read as ranges rather than smooth
    noise peaks or parallel stripes.
    """
    x = np.asarray(x, dtype=np.float32)
    y = np.asarray(y, dtype=np.float32)
    if not x.size:
        return np.asarray(signal, dtype=np.float32)

    center_x = (float(x.min()) + float(x.max())) * .5
    center_y = (float(y.min()) + float(y.max())) * .5
    dx, dy = x - center_x, y - center_y
    wavelength = max(28., float(radius) * .45)
    warp_wavelength = max(48., float(radius) * .9)
    seed = int(seed) & 0xFFFFFFFF
    warp_x = .10 * _simplex_noise(
        dx / warp_wavelength, dy / warp_wavelength, (seed + 7919) & 0xFFFFFFFF,
    )
    warp_y = .10 * _simplex_noise(
        dx / warp_wavelength, dy / warp_wavelength, (seed + 1543) & 0xFFFFFFFF,
    )
    ridge = _ridged_multifractal(
        _simplex_noise,
        dx / wavelength + warp_x,
        dy / wavelength + warp_y,
        (seed ^ 0xA53C9E17) & 0xFFFFFFFF,
        1., 4, 2., .5,
    )
    # Keep the existing broad island field in charge of elevation while the
    # ridge signal gives high terrain connected, irregular range structure.
    return (
        np.asarray(signal, dtype=np.float32) + _TEAM_RIDGE_SIGNAL_WEIGHT * ridge
    ).astype(np.float32)


def _grow_inland_lake(island, allowed, score, center, target):
    """Grow one connected, irregular lake while keeping it enclosed by land."""
    lake = np.zeros(island.shape, dtype=bool)
    queued = np.zeros(island.shape, dtype=bool)
    height, width = island.shape
    x, y = map(int, center)
    if not (0 <= y < height and 0 <= x < width and allowed[y, x]):
        return lake
    frontier = [(float(score[y, x]), y, x)]
    queued[y, x] = True
    lake_cells = 0
    while len(frontier) and lake_cells < int(target):
        _, cy, cx = heappop(frontier)
        if lake[cy, cx]:
            continue
        lake[cy, cx] = True
        lake_cells += 1
        for dy, dx in HEX6:
            ny, nx = cy + dy, cx + dx
            if (0 <= ny < height and 0 <= nx < width
                    and allowed[ny, nx] and not queued[ny, nx]):
                queued[ny, nx] = True
                heappush(frontier, (float(score[ny, nx]), ny, nx))
    if int(lake.sum()) < int(target):
        return np.zeros(island.shape, dtype=bool)
    return lake


def _island_lakes(island, depth, signal, seed, signal_provider, *, distributed=True):
    """Carve size-scaled basins well inside an island's outer coastline.

    Lake count depends only on the island's actual land area. Candidate centers
    must be at least halfway from the coast toward the island's deepest point,
    and every lake cell stays beyond a substantial outer-shore buffer.
    """
    lake = np.zeros(island.shape, dtype=bool)
    island_area = int(np.count_nonzero(island))
    count = _inland_lake_count(island_area, distributed=distributed)
    if count == 0:
        return lake, 0, 0
    ys, xs = np.nonzero(island)
    if not len(xs):
        return lake, 0, 0
    target = (int(np.clip(round(island_area * .0025), 160, 900))
              if distributed else max(64, int(round(island_area * .0075))))
    lake_radius = float(np.sqrt(target / np.pi))
    max_depth = float(np.max(depth[island]))
    minimum_center_depth = max(
        24., lake_radius * 2.,
        max_depth * _INLAND_LAKE_CENTER_DEPTH_FRACTION,
    )
    minimum_lake_depth = max(
        15., lake_radius * 1.4,
        max_depth * _INLAND_LAKE_MIN_DEPTH_FRACTION,
    )
    center_domain = island & (depth >= minimum_center_depth)
    _, cx = np.nonzero(center_domain)
    if len(cx) < target * count:
        return lake, 0, 0

    low, high = np.quantile(signal, (.05, .95))
    field = np.zeros(island.shape, dtype=np.float32)
    normalized_signal = np.clip((signal - low) / max(float(high - low), 1e-6), 0., 1.)
    field[ys, xs] = normalized_signal
    yy, xx = np.indices(island.shape, dtype=np.float32)
    candidate_y, candidate_x = np.nonzero(center_domain)
    order = np.argsort(field[candidate_y, candidate_x], kind="stable")
    centers = []
    island_radius = float(np.sqrt(island_area / np.pi))
    minimum_spacing = max(lake_radius * 3.8, island_radius * (.32 if distributed else .66))
    spacing_squared = minimum_spacing ** 2
    for index in order:
        point = (int(candidate_x[index]), int(candidate_y[index]))
        if all((point[0] - old_x) ** 2 + (point[1] - old_y) ** 2 >= spacing_squared
               for old_x, old_y in centers):
            centers.append(point)
            if len(centers) >= count:
                break

    actual_count = 0
    for lake_index, center in enumerate(centers):
        edge_values = signal_provider(
            xs, ys, max(8., lake_radius * .9),
            (int(seed) + lake_index * 15485863 + 811) & 0xFFFFFFFF,
        )
        edge_low, edge_high = np.quantile(edge_values, (.05, .95))
        edge_field = np.zeros(island.shape, dtype=np.float32)
        edge_field[ys, xs] = np.clip(
            (edge_values - edge_low) / max(float(edge_high - edge_low), 1e-6),
            0., 1.,
        )
        angle = float(np.random.default_rng(int(seed) + lake_index).uniform(0., np.pi))
        dx, dy = xx - center[0], yy - center[1]
        major = np.cos(angle) * dx + np.sin(angle) * dy
        minor = -np.sin(angle) * dx + np.cos(angle) * dy
        distance = lake_radius * np.sqrt(
            (major / (lake_radius * 1.35)) ** 2
            + (minor / (lake_radius * .74)) ** 2
        )
        score = distance + lake_radius * (.80 * field + .75 * edge_field)
        allowed = island & (depth >= minimum_lake_depth) & ~dilate(lake, 5)
        addition = _grow_inland_lake(island, allowed, score, center, target)
        if addition.any():
            lake |= addition
            actual_count += 1
    return lake, actual_count, int(np.count_nonzero(lake))


def _local_island_relief(signal, depth, radius, water_threshold, amplitude=1.,
                         progression_override=None, source_mean_shift=0.):
    """Keep coastal byte slopes and inland noise amplitude across island sizes.

    Weight the noise statistics towards land where relief can develop. This
    removes whole-island height bias without painting or enforcing mountain
    areas. A separate low initial rise survives integer rounding at the coast;
    its 24-cell decay length does not grow with the island.
    """
    depth = np.asarray(depth, dtype=np.float32)
    progression = (
        _coastal_progression(depth, depth.max())
        if progression_override is None
        else np.asarray(progression_override, dtype=np.float32)
    )
    mean = float(np.average(signal, weights=progression))
    deviation = float(np.sqrt(np.average(
        (signal - mean) ** 2, weights=progression,
    )))
    normalized = (signal - mean) / max(.1, deviation) * .8
    # The native relaxation has a fixed cell scale. Smaller islands need a
    # higher source mean to retain broad hills after that same relaxation.
    source_mean = np.float32(147. + float(source_mean_shift) + 48. * min(1., 45. / radius) ** 2)
    threshold = int(water_threshold)
    ceiling = threshold + float(amplitude) * (225. - threshold)
    level = np.float32(threshold + (ceiling - threshold) * float(source_mean) / 225.)
    raw_relief = level + (ceiling - level) * np.tanh(normalized)
    coastal_rise = float(amplitude) * 1.5 * depth * np.exp(-depth / 24.)
    # Only the highest source altitudes are compressed; foothills retain their
    # span and the snow threshold remains an ordinary user-controlled threshold.
    knee = threshold + (ceiling - threshold) * (175. / 225.)
    raw_relief -= .32 * np.maximum(raw_relief - knee, 0.)
    relief = threshold + (raw_relief - threshold) * progression + coastal_rise
    return raw_relief, relief


def _smooth_noise(x, y, wavelength, seed):
    # Simplex has no axis-aligned cell edges; wavelengths are measured in map
    # cells, relative to each island rather than the complete continental map.
    from .noise_sources import _simplex_noise
    return _simplex_noise(x / wavelength, y / wavelength, int(seed) & 0xFFFFFFFF)


def _island_layout(side, count, seed, *, capacities=None):
    """Relax random anchors, then balance their available construction space.

    These territories are only packing constraints. Their boundaries are
    warped and separated by water; they never become the island coastline.
    """
    rng = np.random.default_rng(int(seed) & 0xFFFFFFFF)
    spacing = side / np.sqrt(count)
    step = max(2, side // 96)
    margin = max(8, round(side * .018))
    axis = np.arange(margin, side - margin, step, dtype=np.float32)
    yy, xx = np.meshgrid(axis, axis, indexing="ij")
    points = np.column_stack((xx.ravel(), yy.ravel()))
    centers = points[rng.choice(len(points), count, replace=False)].copy()
    weights = np.zeros(count, dtype=np.float32)
    capacity = np.ones(count, dtype=np.float32) if capacities is None else np.asarray(capacities, dtype=np.float32)
    if capacity.shape != (count,) or np.any(capacity <= 0):
        raise ValueError("Chaque île doit avoir une capacité positive")
    targets = len(points) * capacity / float(capacity.sum())
    for _ in range(50):
        # Two coordinate planes avoid the interleaved (points, players, 2)
        # temporary and its axis reduction; arithmetic/order stay identical.
        dx = points[:, 0, None] - centers[None, :, 0]
        dy = points[:, 1, None] - centers[None, :, 1]
        costs = dx * dx + dy * dy - weights
        owners = costs.argmin(axis=1)
        for n in range(count):
            owned = points[owners == n]
            if len(owned):
                centers[n] += .65 * (owned.mean(axis=0) - centers[n])
            else:
                centers[n] = points[int(rng.integers(len(points)))]
            weights[n] += (targets[n] - len(owned)) / targets[n] * spacing ** 2 * .15
        weights -= weights.mean()
    # Keep the spacing balanced without converging to a visible lattice.
    centers += rng.normal(0., spacing * .055, centers.shape)
    centers = np.clip(centers, margin + spacing * .28, side - margin - spacing * .28)
    yy, xx = np.indices((side, side), dtype=np.float32)
    # Warp packing borders as well as the coasts to avoid straight clipped
    # bays when a large island approaches the edge of its allotted space.
    wx = xx + spacing * .22 * _smooth_noise(xx, yy, spacing * .7, seed + 811)
    wy = yy + spacing * .22 * _smooth_noise(xx, yy, spacing * .7, seed + 977)
    best = np.full(xx.shape, np.inf, np.float32)
    owners = np.zeros(xx.shape, np.int16)
    for n, (cx, cy) in enumerate(centers):
        cost = (wx - cx) ** 2 + (wy - cy) ** 2 - weights[n]
        better = cost < best
        owners[better] = n + 1
        best[better] = cost[better]
    owners[:margin] = owners[-margin:] = 0
    owners[:, :margin] = owners[:, -margin:] = 0
    return np.rint(centers).astype(int), owners


def _growth_arrival_score(safe, score, center, radius):
    """Propagate a positive-cost front through the source contour potential.

    A lower potential beyond a saddle cannot admit an entire lobe at once:
    each additional cell costs travel time. This is source construction, not
    a repair of the finished coastline. Eight Euclidean directions reduce
    metric bias; the contour selection below retains native HEX6 connectivity.
    """
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import dijkstra

    height, width = safe.shape
    indexes = np.arange(height * width, dtype=np.int32).reshape(safe.shape)
    rows, columns, weights = [], [], []
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        ya, yb = slice(0, height - dy), slice(dy, height)
        xa = slice(max(0, -dx), min(width, width - dx))
        xb = slice(max(0, dx), min(width, width + dx))
        valid = safe[ya, xa] & safe[yb, xb]
        a, b = indexes[ya, xa][valid], indexes[yb, xb][valid]
        step = float(np.hypot(dy, dx))
        delta = 2. * (score[yb, xb][valid] - score[ya, xa][valid])
        rows.extend((a, b))
        columns.extend((b, a))
        weights.extend((
            np.maximum(step * .45, step + delta).astype(np.float32),
            np.maximum(step * .45, step - delta).astype(np.float32),
        ))
    graph = coo_matrix(
        (np.concatenate(weights), (np.concatenate(rows), np.concatenate(columns))),
        shape=(height * width, height * width),
    ).tocsr()
    y, x = center
    arrival = dijkstra(graph, directed=True, indices=int(indexes[y, x])).reshape(safe.shape)
    reachable = safe & np.isfinite(arrival)
    # Unreachable territorial fragments cannot enter the center component.
    # Keep the threshold interval finite; all selection stays inside safe.
    arrival[~reachable] = float(arrival[reachable].max()) + float(radius)
    return arrival.astype(np.float32)


def _finish_connected_mask(retained, safe, score, target):
    """Complete a threshold component without jumping to a detached basin.

    Binary thresholds can merge an entire bay at once. Grow only the missing
    cells from the selected component, by score, instead of retrying all
    territories. Every accepted cell touches land; safe bounds stay exact.
    """
    retained = retained.copy()
    frontier = dilate(retained, 1) & safe & ~retained
    queued = retained | frontier
    rows, columns = np.nonzero(frontier)
    heap = [(float(score[y, x]), int(y), int(x)) for y, x in zip(rows, columns)]
    heapify(heap)
    remaining = int(target) - int(np.count_nonzero(retained))
    height, width = safe.shape
    while remaining > 0 and heap:
        _, y, x = heappop(heap)
        retained[y, x] = True
        remaining -= 1
        for dy, dx in HEX6:
            ny, nx = y + dy, x + dx
            if 0 <= ny < height and 0 <= nx < width and safe[ny, nx] and not queued[ny, nx]:
                queued[ny, nx] = True
                heappush(heap, (float(score[ny, nx]), ny, nx))
    return retained


def _coast_detail(coast, safe):
    """Reuse the existing field's fine scales without new random samples."""
    fine = coast - gaussian_filter(coast, 3., mode="nearest")
    deviation = float(np.sqrt(np.mean(fine[safe] ** 2)))
    if deviation < 1e-6:
        return np.zeros_like(coast)
    return np.tanh(fine / deviation)


def _coast_guard_depth(free_depth, coast, safe, approach_band, *, detail=None, amplitude=2.):
    """Carry the existing field's fine detail into territorial setbacks.

    A bounded displacement of at most 2 cells roughens only the nearby
    setback. The packing domain itself is unchanged and remains a hard guard.
    No new noise evaluation or change of large-scale island layout is needed.
    """
    if detail is None:
        detail = _coast_detail(coast, safe)
    proximity = (approach_band / (free_depth + approach_band)) ** 2
    return np.maximum(1., free_depth + amplitude * detail * proximity)


def _detail_contour_score(score, detail, *, amplitude=1.1):
    """Apply fine coast displacement in cell units, including enclosed bays.

    The radial core and territorial barrier can dominate the random field's
    fine scales. Weight detail by the local broad score gradient, so a steep
    contour does not lose its texture. The 1.1-cell perturbation also follows
    lake rims; it neither selects water bodies nor evaluates another noise.
    Exact area, connectivity and safe territories are still enforced below.
    """
    broad = gaussian_filter(score, 2., mode="nearest")
    dy, dx = np.gradient(broad)
    return score - amplitude * detail * np.hypot(dx, dy)


def _island_feature_distance_fields(terrain, island):
    """Measure candidate distance to mountain and river cells on this island."""

    mountain = island & np.isin(terrain, MOUNTAIN_FAMILY_IDS)
    river = island & np.isin(terrain, RIVER_IDS)
    return (
        distance_from(mountain) if mountain.any() else None,
        distance_from(river) if river.any() else None,
    )


def _rank_island_start_candidates(
    points_yx, island, mountain_distance, river_distance,
    object_distance, clearance_rank, preferred_margin, rng,
):
    """Rank legal centers by both resource fronts, then existing preferences."""

    ys, xs = points_yx.T
    cy, cx = np.argwhere(island).mean(axis=0)
    dx = xs.astype(np.int32) - int(round(cx))
    dy = ys.astype(np.int32) - int(round(cy))
    center_distance = np.where(
        dx * dy >= 0,
        np.maximum(np.abs(dx), np.abs(dy)),
        np.abs(dx) + np.abs(dy),
    )
    mountain_values = (
        mountain_distance[ys, xs].astype(np.int32)
        if mountain_distance is not None else np.zeros(len(xs), dtype=np.int32)
    )
    river_values = (
        river_distance[ys, xs].astype(np.int32)
        if river_distance is not None else np.zeros(len(xs), dtype=np.int32)
    )
    object_values = object_distance[ys, xs].astype(np.int32)
    clearance_values = clearance_rank[ys, xs].astype(np.int32)
    margin_values = preferred_margin[ys, xs].astype(np.int32)

    legacy_order = np.lexsort((
        center_distance, -object_values, -clearance_values, -margin_values,
    ))
    feature_order = np.lexsort((
        center_distance, -object_values, -clearance_values, -margin_values,
        mountain_values + river_values,
        np.maximum(mountain_values, river_values),
    ))

    def randomize_first_tie(order, keys):
        first = int(order[0])
        tied = order
        for values in keys:
            tied = tied[values[tied] == values[first]]
        selected = int(tied[int(rng.integers(len(tied)))])
        position = int(np.flatnonzero(order == selected)[0])
        order[0], order[position] = order[position], order[0]
        return order

    legacy_order = randomize_first_tie(
        legacy_order,
        (center_distance, object_values, clearance_values, margin_values),
    )
    feature_order = randomize_first_tie(
        feature_order,
        (np.maximum(mountain_values, river_values), mountain_values + river_values,
         margin_values, clearance_values, object_values, center_distance),
    )
    return (
        points_yx[feature_order, ::-1].astype(np.int64),
        mountain_values[feature_order], river_values[feature_order],
        np.maximum(mountain_values, river_values)[feature_order],
        (mountain_values + river_values)[feature_order],
        points_yx[legacy_order, ::-1].astype(np.int64),
    )


def _start_feature_record(mountain_distance, river_distance):
    return {
        "mountain_distance_hex": (
            None if mountain_distance is None else int(mountain_distance)
        ),
        "river_distance_hex": (
            None if river_distance is None else int(river_distance)
        ),
    }


def _continental_land_percent(side):
    """Return the native measured continental land share for this map size."""

    side = int(side)
    sizes, shares = np.asarray(_CONTINENTAL_LAND_REFERENCE, dtype=np.float64).T
    if side < int(sizes[0]):
        # Extend the measured constant-width ocean envelope to the smaller
        # supported maps. The existing island profile remains the lower bound.
        inland = max(0., 1. - 2. * _NATIVE_EFFECTIVE_OCEAN_MARGIN / side)
        return max(_ISLAND_BASE_LAND_PERCENT, inland * inland * 100.)
    return float(np.interp(side, sizes, shares))


def _continental_ocean_land_percent(side):
    """Calibrate the outer land mask against sea, independently of lake carving.

    The interpolated correction is applied before contour growth. Inland
    lakes retain their existing area-based policy, without a final-water quota.
    """
    sizes, corrections = np.asarray(_CONTINENTAL_OCEAN_LAND_CORRECTION).T
    correction = float(np.interp(int(side), sizes, corrections))
    return _continental_land_percent(side) + correction


def _island_target_land_percent(side, island_count):
    """Blend from the island-heavy profile to continental cover by island count."""

    count = int(island_count)
    if count < 1:
        raise ValueError("Le nombre d’îles doit être positif")
    continental = _continental_land_percent(side)
    return _ISLAND_BASE_LAND_PERCENT + (continental - _ISLAND_BASE_LAND_PERCENT) / count


def _proportional_island_targets(side, player_counts, *, target_land_percent=None):
    """Allocate a map-wide land budget exactly in proportion to team sizes."""

    player_counts = np.asarray(player_counts, dtype=np.int64)
    if target_land_percent is None:
        target_land_percent = _island_target_land_percent(side, len(player_counts))
    total = int(round(side * side * float(target_land_percent) / 100.))
    exact = total * player_counts.astype(np.float64) / float(player_counts.sum())
    targets = np.floor(exact).astype(np.int64)
    remainder = total - int(targets.sum())
    order = np.argsort(-(exact - targets), kind="stable")
    targets[order[:remainder]] += 1
    return targets.tolist()


def build_island_masks(side, players, seed, *, variant_r21=False, island_player_counts=None,
                       target_land_percent=None):
    """Build connected masks with the historical or an explicit outer land budget."""
    signal_provider = midpoint_signal_r21 if variant_r21 else simplex_signal
    count = int(players)
    if count < 1:
        raise ValueError("Les îles exigent au moins un groupe")
    adaptive_land_target = island_player_counts is not None
    group_sizes = [1] * count if island_player_counts is None else [int(value) for value in island_player_counts]
    if len(group_sizes) != count or any(value < 1 for value in group_sizes):
        raise ValueError("Chaque île doit correspondre à au moins un joueur")
    if sum(group_sizes) < 2:
        raise ValueError("Les îles exigent au moins deux joueurs")
    explicit_land_target = target_land_percent is not None
    if target_land_percent is None:
        target_land_percent = (
            _island_target_land_percent(side, count)
            if adaptive_land_target else _ISLAND_BASE_LAND_PERCENT
        )
    if not 0. < float(target_land_percent) < 100.:
        raise ValueError("La proportion de terre doit être comprise entre 0 et 100 %")
    if not explicit_land_target and not adaptive_land_target and all(value == group_sizes[0] for value in group_sizes):
        # Retain the independently validated per-island rounding for the
        # standalone Large Islands archetype, including its exact mask output.
        targets = [
            round(side * side * _ISLAND_BASE_LAND_PERCENT / 100. / count)
        ] * count
    else:
        targets = _proportional_island_targets(
            side, group_sizes, target_land_percent=target_land_percent,
        )
    channel = max(8, round(side * .015))
    yy, xx = np.indices((side, side), dtype=np.float32)
    for attempt in range(12):
        centers, territories = _island_layout(
            side, count, int(seed) + attempt * 104729,
            capacities=group_sizes,
        )
        labels = np.zeros((side, side), np.int16)
        for n, (cx, cy) in enumerate(centers, 1):
            target = targets[n - 1]
            radius = np.sqrt(target / np.pi)
            safe = distance_from(territories != n) > (channel + 1) // 2
            if np.count_nonzero(safe) < target * 1.04 or not safe[cy, cx]:
                break
            # Noise and connected-component scans stay inside this island's
            # packing territory, instead of rescanning the complete map.
            rows, columns = np.nonzero(safe)
            y0, y1 = int(rows.min()), int(rows.max()) + 1
            x0, x1 = int(columns.min()), int(columns.max()) + 1
            box = np.s_[y0:y1, x0:x1]
            local_safe = safe[box]
            lx, ly = xx[box], yy[box]
            coast = signal_provider(lx, ly, radius * .7, int(seed) + n * 7919)
            if not variant_r21:
                # Round sub-cell interpolation corners before contour selection,
                # without filtering the final mask or changing the broad field.
                coast = gaussian_filter(coast, .65, mode="nearest")
            # The hierarchical field determines the contour's irregularities;
            # distance keeps a compact core suitable for native slope rules.
            distance = np.hypot(lx - cx, ly - cy)
            # Keep enough central width for legal mountain slopes, while the
            # whole outer contour still follows the refined random field.
            coast_weight = np.clip((distance - radius * .5) / (radius * .5), 0., 1.)
            score = distance - radius * 1.6 * coast * coast_weight
            # Deflect the growing contour well before the reserved boat gap.
            # The hard territory remains only a final safety guard, rather
            # than becoming an abrupt cut along the island shoreline.
            free_depth = distance_transform_edt(np.pad(local_safe, 1))[1:-1, 1:-1].astype(np.float32)
            approach_band = max(6., radius * .22)
            detail = _coast_detail(coast, local_safe)
            guard_depth = _coast_guard_depth(
                free_depth, coast, local_safe, approach_band, detail=detail,
                amplitude=2.5 if variant_r21 else 2.,
            )
            score += approach_band ** 2 / (guard_depth + 1.)
            if adaptive_land_target:
                score = _growth_arrival_score(
                    local_safe, score, (cy - y0, cx - x0), radius,
                )
            score = _detail_contour_score(score, detail, amplitude=1.5 if variant_r21 else 1.1)
            low, high = float(score[local_safe].min()) - 1., float(score[local_safe].max())
            retained = None
            below = np.zeros_like(local_safe)
            for _ in range(17):
                cutoff = (low + high) * .5
                pieces, _ = component_labels(local_safe & (score <= cutoff))
                center_piece = int(pieces[cy - y0, cx - x0])
                retained = pieces == center_piece if center_piece else np.zeros_like(local_safe)
                if np.count_nonzero(retained) < target:
                    below = retained
                    low = cutoff
                else:
                    high = cutoff
            if np.count_nonzero(retained) != target:
                if not below.any():
                    below[cy - y0, cx - x0] = True
                retained = _finish_connected_mask(below, local_safe, score, target)
            if np.count_nonzero(retained) != target:
                break
            labels[box][retained] = n
        else:
            # Geometry only: relief now constructs its continuous coastal
            # progression directly. This mask is no longer a displayed weight.
            mask = np.where(labels > 0, 255, 0).astype(np.uint8)
            return labels, centers, mask, channel, attempt
    raise RuntimeError("Impossible de répartir des îles proportionnelles avec des chenaux navigables")


def generate_independent_islands(
    height, *, players, water_threshold, mountain_threshold, snow_threshold, seed,
    native_relaxation: Callable[[np.ndarray], tuple[np.ndarray, int]] | None = None,
    stage_sink: dict | None = None,
    variant_r21: bool = False,
    amplitude: float = 1.,
    island_player_counts=None,
    target_land_percent=None,
):
    """Pack independent masks, generate local relief, then relax natively.

    The input supplies the map dimensions only. No continental height sample,
    quantile remapping or post-smoothing mountain uplift is retained from R3.
    """
    source = np.asarray(height, dtype=np.uint8)
    if source.ndim != 2 or source.shape[0] != source.shape[1]:
        raise ValueError("Le relief doit être carré")
    side = source.shape[0]
    adaptive_land_target = island_player_counts is not None
    group_sizes = [1] * int(players) if island_player_counts is None else [int(value) for value in island_player_counts]
    count = len(group_sizes)
    threshold = max(0, int(water_threshold))
    labels, centers, mask, channel, layout_attempt = build_island_masks(
        side, count, seed, variant_r21=variant_r21,
        island_player_counts=(group_sizes if adaptive_land_target else None),
        target_land_percent=target_land_percent,
    )
    signal_provider = midpoint_signal_r21 if variant_r21 else simplex_signal
    yy, xx = np.indices(source.shape, dtype=np.float32)
    outer_depth = distance_from(labels == 0).astype(np.float32)
    inland_lake_counts = [0] * count
    inland_lake_cells = [0] * count
    for n in range(1, count + 1):
        island = labels == n
        ys, xs = np.nonzero(island)
        island_area = len(xs)
        lake_count = _inland_lake_count(island_area, distributed=adaptive_land_target)
        if lake_count == 0:
            continue
        radius = np.sqrt(island_area / np.pi)
        lake_wavelength = max(24., radius * _INLAND_LAKE_SIGNAL_RADIUS_RATIO)
        lake_seed = int(seed) + n * 7919 + 919
        if variant_r21:
            lake_signal = signal_provider(
                xs, ys, lake_wavelength, lake_seed,
            )
        else:
            lake_signal = signal_provider(
                xs, ys, lake_wavelength, lake_seed,
                rounded_relief=True,
            )
        lake_mask, actual_lake_count, lake_cells = _island_lakes(
            island, outer_depth, lake_signal, lake_seed + 32771,
            signal_provider, distributed=adaptive_land_target,
        )
        if lake_cells:
            labels[lake_mask] = 0
            inland_lake_counts[n - 1] = actual_lake_count
            inland_lake_cells[n - 1] = lake_cells
    mask = np.where(labels > 0, 255, 0).astype(np.uint8)
    sizes = [int(np.count_nonzero(labels == n)) for n in range(1, count + 1)]
    # Keep the relief tied to the open-sea coastline. The new lake basins add
    # water and shorelines without making the surrounding island look like a
    # second artificial coast for elevation calibration.
    depths = outer_depth
    output = np.zeros_like(source)
    raw_output = np.zeros_like(source)
    selected = np.zeros_like(source)
    attempts = [0] * count
    team_relief_profiles = [None] * count
    missing = set(range(1, count + 1))
    native_passes = 0
    # Retry only a deficient island's own noise. The mask and other islands
    # remain fixed; mountains are consequences of broad local relief.
    for attempt in range(32):
        for n in sorted(missing):
            radius = np.sqrt(sizes[n - 1] / np.pi)
            team_size = group_sizes[n - 1]
            wavelength_ratio, progression_power = _team_relief_parameters(team_size)
            local_seed = int(seed) + n * 7919 + attempt * 104729
            island = labels == n
            local_x, local_y = xx[island], yy[island]
            relief_progression = None
            source_mean_shift = 0.
            if team_size > 1:
                local_depth = depths[island]
                relief_progression = _team_relief_progression(
                    local_depth, float(local_depth.max()), team_size,
                )
                # Center the source field as the coastal ramp broadens. This
                # balances its mean without selecting mountain cells, changing
                # thresholds or compressing a completed heightmap.
                old_progression = np.power(
                    _coastal_progression(local_depth, float(local_depth.max())),
                    progression_power,
                )
                source_mean_shift = -170. * max(
                    0., float(relief_progression.mean() - old_progression.mean()),
                )
                team_relief_profiles[n - 1] = {
                    "team_size": int(team_size),
                    "continuous_fields": 1,
                    "wavelength_ratio": round(float(wavelength_ratio), 4),
                    "coastal_progression_power": round(float(progression_power), 4),
                    "coastal_rise_scale_cells": min(40., max(16., float(local_depth.max()) * .45)),
                    "source_mean_shift": round(source_mean_shift, 4),
                }
            wavelength = float(radius) * wavelength_ratio
            if variant_r21:
                signal = signal_provider(local_x, local_y, wavelength, local_seed + 919)
            else:
                signal = signal_provider(
                    local_x, local_y, wavelength, local_seed + 919,
                    rounded_relief=True,
                )
            ridge_weight = _TEAM_RIDGE_SIGNAL_WEIGHT if team_size >= 4 else 0.
            if ridge_weight:
                signal = _team_ridged_relief(
                    signal, local_x, local_y, radius, local_seed + 1543,
                )
                team_relief_profiles[n - 1]["range_signal"] = "warped_continuous_ridges"
            if team_relief_profiles[n - 1] is not None:
                team_relief_profiles[n - 1]["player_scoped_fields"] = 0
                team_relief_profiles[n - 1]["ridge_weight"] = ridge_weight
            raw_relief, relief = _local_island_relief(
                signal, depths[island], radius, threshold, amplitude=amplitude,
                progression_override=relief_progression,
                source_mean_shift=source_mean_shift,
            )
            raw_output[island] = np.rint(raw_relief).astype(np.uint8)
            # One above water is only the byte-grid land representation at the
            # immediate shoreline; no inland height floor is retained.
            selected[island] = np.maximum(threshold + 1, np.rint(relief)).astype(np.uint8)
            attempts[n - 1] = attempt + 1
        if native_relaxation is not None:
            output, passes = native_relaxation(selected.copy())
            native_passes += int(passes)
            output = np.asarray(output, dtype=np.uint8)
            if output.shape != source.shape:
                raise ValueError("La relaxation native doit préserver la taille de la carte")
        else:
            output = selected.copy()
        output[labels == 0] = 0
        missing = {n for n in range(1, count + 1)
                   if np.count_nonzero((labels == n) & (output >= mountain_threshold + 3)) < 20}
        if not missing:
            break
    if missing:
        raise RuntimeError(f"Relief montagneux insuffisant sur les îles {sorted(missing)}")
    # Near-coast values stay above the water threshold by construction; verify
    # rather than silently deleting or reconnecting land fragments.
    if np.any(output[labels > 0] <= threshold):
        raise RuntimeError("La relaxation a noyé une partie du masque d’île")
    output, detail_report = add_plain_detail(
        output, labels, seed=seed, water_threshold=threshold,
        mountain_threshold=mountain_threshold,
    )
    if stage_sink is not None:
        stage_sink.update(mask=mask, local_relief=raw_output.copy(), coastal_relief=selected.copy())
    report = {
        "requested_islands": count,
        "requested_players": int(sum(group_sizes)),
        "island_player_counts": list(group_sizes),
        "team_relief_profiles_by_island": team_relief_profiles,
        "inland_lake_counts_by_island": inland_lake_counts,
        "inland_lake_cells_by_island": inland_lake_cells,
        # Retained as aliases for R54 integrations that read these fields.
        "team_lake_counts_by_island": inland_lake_counts,
        "team_lake_cells_by_island": inland_lake_cells,
        "retained_land_cells": int(np.count_nonzero(labels)),
        "island_sizes": sizes, "island_centers": centers.tolist(),
        "contour_growth": ("positive_cost_potential_front" if adaptive_land_target else "connected_threshold"),
        "construction": ("balanced_rotated_midpoint_with_uniform_contour_detail" if variant_r21
                         else "balanced_multiscale_simplex_with_rounded_contour_detail"),
        "relief_distribution": (
            "team_scaled_continuous_field" if any(value > 1 for value in group_sizes)
            else "single_continuous_field_per_island"
        ),
        "retained_land_percent_after_lakes": (
            100. * int(np.count_nonzero(labels)) / float(side * side)
        ),
        "coastal_profile": "nonzero_initial_slope_midpoint_soft_summits",
        "source_amplitude_percent": float(amplitude) * 100.,
        "source_mountain_threshold": int(mountain_threshold),
        "source_snow_threshold": int(snow_threshold),
        "base_island_land_percent": _ISLAND_BASE_LAND_PERCENT,
        "continental_reference_land_percent": _continental_land_percent(side),
        "target_land_percent": (
            float(target_land_percent) if target_land_percent is not None else
            _island_target_land_percent(side, count) if adaptive_land_target else
            _ISLAND_BASE_LAND_PERCENT
        ),
        "land_target_basis": (
            "continental_reference_blended_by_island_count"
            if adaptive_land_target else "fixed_large_island_profile"
        ),
        "boat_channel_cells": channel,
        "layout_attempts": layout_attempt + 1, "local_relief_attempts": attempts,
        "post_island_native_relaxation_passes": native_passes,
        "plain_detail": detail_report,
    }
    return output, labels, report


def summarize_island_terrain_features(terrain, labels):
    return [
        {"island": n, "land_cells": int(np.count_nonzero(labels == n)),
         "mountain_cells": int(np.count_nonzero((labels == n) & np.isin(terrain, MOUNTAIN_FAMILY_IDS))),
         "river_cells": int(np.count_nonzero((labels == n) & np.isin(terrain, RIVER_IDS))),
         "swamp_cells": int(np.count_nonzero((labels == n) & np.isin(terrain, SWAMP_IDS)))}
        for n in range(1, int(labels.max()) + 1)
    ]


def _separated_island_assignment(domains):
    """Complete search over island domains, with forward checking.

    Each domain is an ordered N x 2 array of (x, y) candidates. Preferences
    affect visit order only; no candidate or combination is truncated.
    """
    from ..start_safety import EDITOR_MIN_SPACING
    minimum_squared = EDITOR_MIN_SPACING ** 2

    def visit(remaining, assigned):
        if not remaining:
            return assigned
        # Start with the most constrained island; keep output in player order.
        island = min(remaining, key=lambda n: (len(remaining[n]), n))
        for point in remaining[island]:
            following = {}
            for n, candidates in remaining.items():
                if n == island:
                    continue
                delta = candidates - point
                allowed = candidates[(delta * delta).sum(axis=1) >= minimum_squared]
                if not len(allowed):
                    break
                following[n] = allowed
            else:
                result = visit(following, {**assigned, island: point})
                if result is not None:
                    return result
        return None

    assigned = visit(dict(enumerate(domains)), {})
    if assigned is None:
        return None
    return [tuple(map(int, assigned[n])) for n in range(len(domains))]


def _compact_resource_indices(points, feature_max, feature_total, occupied, count):
    """Reference packing protects the last teammate's access in narrow terrain."""
    chosen = []
    occupied = list(occupied)
    for _ in range(count):
        nearest = np.full(len(points), np.iinfo(np.int64).max, dtype=np.int64)
        for sx, sy in occupied:
            nearest = np.minimum(nearest, (points[:, 0] - sx) ** 2 + (points[:, 1] - sy) ** 2)
        allowed = nearest >= 50 ** 2
        if not np.any(allowed):
            break
        allowed &= feature_max == feature_max[allowed].min()
        allowed &= feature_total == feature_total[allowed].min()
        allowed &= nearest == nearest[allowed].min()
        index = int(np.flatnonzero(allowed)[0])
        chosen.append(index)
        occupied.append(tuple(map(int, points[index])))
    return chosen


def _spread_team_arrangement(points, feature_max, feature_total, chosen,
                             reference, occupied, preferred_spacing):
    """Reduce close-pair pressure across the whole team within resource bounds.

    The preferred spacing is soft. Each relocation strictly lowers the sum
    of squared pair deficits; the 50-cell editor minimum and the reference
    team's mountain/river envelope remain hard constraints.
    """
    chosen = list(chosen)
    if len(chosen) < 2:
        return chosen
    pool = np.flatnonzero(
        (feature_max <= feature_max[reference].max() + 8)
        & (feature_total <= feature_total[reference].max() + 12)
    )
    candidates = points[pool]
    external_safe = np.ones(len(pool), dtype=bool)
    for sx, sy in occupied:
        external_safe &= (candidates[:, 0] - sx) ** 2 + (candidates[:, 1] - sy) ** 2 >= 50 ** 2
    for _ in range(4):
        selected = points[chosen]
        distances = np.hypot(selected[:, None, 0] - selected[None, :, 0],
                             selected[:, None, 1] - selected[None, :, 1])
        np.fill_diagonal(distances, np.inf)
        order = np.argsort(distances.min(axis=1), kind="stable")
        moved = False
        for slot in order:
            others = points[[index for n, index in enumerate(chosen) if n != slot]]
            current = points[chosen[slot]]
            old_distance = np.hypot(others[:, 0] - current[0], others[:, 1] - current[1])
            old_penalty = float(np.square(np.maximum(0., 1. - old_distance / preferred_spacing)).sum())
            if old_penalty <= 1e-12:
                continue
            squared = ((candidates[:, None, 0] - others[None, :, 0]) ** 2
                       + (candidates[:, None, 1] - others[None, :, 1]) ** 2)
            valid = external_safe & (squared.min(axis=1) >= 50 ** 2)
            if not np.any(valid):
                continue
            penalty = np.square(np.maximum(0., 1. - np.sqrt(squared) / preferred_spacing)).sum(axis=1)
            best = float(penalty[valid].min())
            if best >= old_penalty - 1e-12:
                continue
            eligible = valid & (penalty == best)
            eligible &= feature_max[pool] == feature_max[pool[eligible]].min()
            eligible &= feature_total[pool] == feature_total[pool[eligible]].min()
            chosen[slot] = int(pool[int(np.flatnonzero(eligible)[0])])
            moved = True
        if not moved:
            break
    return chosen


def _place_team_island_starts(state, players, rng, labels, technical_clear):
    """Place every teammate near mountain and river terrain, then spread them."""

    from ..start_safety import candidate_centers, _centers_matching

    topology = state.metadata.get("large_island_topology", {})
    player_labels = [int(value) for value in topology.get("player_island_labels", ())]
    island_count = int(np.max(labels)) if labels is not None and labels.size else 0
    if len(player_labels) != int(players) or not island_count:
        raise ValueError("Îles par équipe : correspondance joueurs/îles absente")
    if any(value < 1 or value > island_count for value in player_labels):
        raise ValueError("Îles par équipe : correspondance joueurs/îles incohérente")
    members_by_island = {
        island: [slot for slot, value in enumerate(player_labels) if value == island]
        for island in range(1, island_count + 1)
    }
    if any(not members for members in members_by_island.values()):
        raise ValueError("Îles par équipe : une île n’a aucun joueur")

    side, terrain = state.side, state.terrain
    safe = candidate_centers(state)
    yy, xx = np.indices(terrain.shape)
    edge = max(technical_clear + 8, side // 18)
    preferred_margin = (
        (xx >= edge) & (yy >= edge)
        & (xx < side - edge) & (yy < side - edge)
    )
    object_distance = distance_from(
        state.objects != 0, max_distance=max(technical_clear, 8),
    )
    clearance_rank = np.zeros_like(terrain, dtype=np.uint8)
    for clearance in (2, 4, 6, 8):
        clearance_rank[~dilate(terrain != GRASS, clearance)] = clearance

    starts_by_player: dict[int, tuple[int, int]] = {}
    starts_all: list[tuple[int, int]] = []
    candidate_counts: list[int] = []
    selected_by_player = []
    used_spacing_fallback = False
    resource_guard_islands = []
    spacing_refined_islands = []
    for island_number, members in members_by_island.items():
        island = labels == island_number
        domain = island & safe & _centers_matching(island, START_FOOTPRINT)
        points_yx = np.argwhere(domain)
        candidate_counts.append(len(points_yx))
        if not len(points_yx):
            continue
        mountain_distance, river_distance = _island_feature_distance_fields(
            terrain, island,
        )
        (
            points_xy, mountain_values, river_values,
            feature_max, feature_total, legacy_points,
        ) = _rank_island_start_candidates(
            points_yx, island, mountain_distance, river_distance,
            object_distance, clearance_rank, preferred_margin, rng,
        )
        compact_indices = _compact_resource_indices(
            points_xy, feature_max, feature_total, starts_all, len(members),
        )
        selected_indices = []
        local_starts: list[tuple[int, int]] = []
        for player in members:
            nearest_squared = np.full(
                len(points_xy), np.iinfo(np.int64).max, dtype=np.int64,
            )
            for sx, sy in starts_all:
                dx = points_xy[:, 0] - sx
                dy = points_xy[:, 1] - sy
                nearest_squared = np.minimum(
                    nearest_squared, dx * dx + dy * dy,
                )
            allowed = nearest_squared >= 50 ** 2
            if not np.any(allowed):
                break

            # Allow a bounded resource compromise to avoid packing every
            # teammate against the same optimum. Density limits the desired
            # spacing; 50 remains the hard editor minimum and maximin fallback.
            best_max = int(feature_max[allowed].min())
            best_total = int(feature_total[allowed & (feature_max == best_max)].min())
            feature_tier = (allowed & (feature_max <= best_max + 8)
                            & (feature_total <= best_total + 12))
            preferred_spacing = float(np.clip(
                .65 * np.sqrt(np.count_nonzero(island) / len(members)), 65., 130.,
            ))
            spacing_credit = np.minimum(nearest_squared, preferred_spacing ** 2)
            feature_tier &= spacing_credit == spacing_credit[feature_tier].max()
            feature_tier &= feature_max == feature_max[feature_tier].min()
            feature_tier &= feature_total == feature_total[feature_tier].min()
            best_spacing = int(nearest_squared[feature_tier].min())
            tied = np.flatnonzero(feature_tier & (nearest_squared == best_spacing))
            chosen_index = int(tied[0])
            selected_indices.append(chosen_index)
            point = tuple(map(int, points_xy[chosen_index]))
            starts_by_player[player] = point
            local_starts.append(point)
            starts_all.append(point)

        # A locally good spread can push the last teammate far from resources.
        # Compare the complete team against resource-first compact packing.
        if len(compact_indices) == len(members) and (
            len(selected_indices) < len(members)
            or feature_max[selected_indices].max() > feature_max[compact_indices].max() + 8
            or feature_total[selected_indices].max() > feature_total[compact_indices].max() + 12
        ):
            resource_guard_islands.append(int(island_number))
            if local_starts:
                del starts_all[-len(local_starts):]
            selected_indices = list(compact_indices)
            local_starts = [tuple(map(int, points_xy[index])) for index in compact_indices]
            starts_all.extend(local_starts)
            for player, point in zip(members, local_starts):
                starts_by_player[player] = point

        if len(local_starts) < len(members):
            # Resource-first greedy choices can rarely consume a crowded
            # island's last legal packing slot. Retry that island with the
            # previous maximin order while keeping every hard safety rule.
            used_spacing_fallback = True
            for player in members:
                starts_by_player.pop(player, None)
            if local_starts:
                del starts_all[-len(local_starts):]
            local_starts = []
            for player in members:
                nearest_squared = np.full(
                    len(legacy_points), np.iinfo(np.int64).max, dtype=np.int64,
                )
                local_distance = np.full_like(nearest_squared, np.iinfo(np.int64).max)
                for sx, sy in starts_all:
                    dx = legacy_points[:, 0] - sx
                    dy = legacy_points[:, 1] - sy
                    nearest_squared = np.minimum(
                        nearest_squared, dx * dx + dy * dy,
                    )
                allowed = nearest_squared >= 50 ** 2
                if not np.any(allowed):
                    break
                if local_starts:
                    local_distance[:] = np.iinfo(np.int64).max
                    for sx, sy in local_starts:
                        dx = legacy_points[:, 0] - sx
                        dy = legacy_points[:, 1] - sy
                        local_distance = np.minimum(
                            local_distance, dx * dx + dy * dy,
                        )
                    best_distance = int(local_distance[allowed].max())
                    allowed &= local_distance == best_distance
                point = tuple(map(int, legacy_points[int(np.flatnonzero(allowed)[0])]))
                local_starts.append(point)
                starts_all.append(point)

        if len(selected_indices) == len(members) and len(local_starts) == len(members):
            refined = _spread_team_arrangement(
                points_xy, feature_max, feature_total, selected_indices,
                compact_indices if len(compact_indices) == len(members) else selected_indices,
                starts_all[:-len(local_starts)], preferred_spacing,
            )
            if refined != selected_indices:
                spacing_refined_islands.append(int(island_number))
                del starts_all[-len(local_starts):]
                local_starts = [tuple(map(int, points_xy[index])) for index in refined]
                starts_all.extend(local_starts)

        for player, (sx, sy) in zip(members, local_starts):
            starts_by_player[player] = (sx, sy)
            selected_by_player.append({
                "player_slot": int(player),
                "island": int(island_number),
                **_start_feature_record(
                    mountain_distance[sy, sx] if mountain_distance is not None else None,
                    river_distance[sy, sx] if river_distance is not None else None,
                ),
            })

    active = sorted(starts_by_player)
    starts = [starts_by_player[player] for player in active]
    state.metadata["start_slot_indices"] = active
    state.metadata["start_disabled_slots"] = [
        player for player in range(int(players)) if player not in starts_by_player
    ]
    active_island_labels = [player_labels[player] for player in active]
    state.metadata["island_start_search"] = {
        "candidate_scan_complete": True,
        "strategy": "mountain_and_river_access_with_soft_spacing",
        "resource_max_slack_hex": 8,
        "resource_total_slack_hex": 12,
        "resource_guard_islands": resource_guard_islands,
        "spacing_refined_islands": spacing_refined_islands,
        "candidate_counts_per_island": candidate_counts,
        "optional_map_margin": edge,
        "spacing_fallback_used": used_spacing_fallback,
        "selected_by_player": sorted(
            selected_by_player, key=lambda item: item["player_slot"],
        ),
    }
    state.starts = starts
    state.metadata["large_island_starts"] = {
        "team_islands": True,
        "one_start_per_island": False,
        "island_labels": active_island_labels,
        "player_island_labels": player_labels,
        "players_per_island": [len(members_by_island[n]) for n in members_by_island],
    }
    state.metadata["startable_mass"] = analyze_startable_masses(
        terrain, starts,
        candidate_centers_considered=sum(candidate_counts),
    )
    reservation = np.zeros_like(terrain, dtype=bool)
    for x, y in starts:
        for dx, dy in START_FOOTPRINT:
            reservation[y + dy, x + dx] = True
    state.metadata.update(
        starts_placed_early=True,
        start_footprint_cells=int(reservation.sum()),
        start_min_spacing=min(
            hex_distance(*a, *b)
            for i, a in enumerate(starts)
            for b in starts[i + 1:]
        ) if len(starts) > 1 else 0,
    )
    return reservation


def place_island_starts(state, players, rng, labels, technical_clear):
    """Search every admissible center, one start per island, before failing."""
    if labels is None:
        labels, _ = component_labels(~np.isin(state.terrain, WATER_IDS))
    topology = state.metadata.get("large_island_topology", {})
    prioritize_team_resources = bool(topology.get("team_islands"))
    player_island_labels = [
        int(value) for value in topology.get("player_island_labels", ())
    ]
    if topology.get("team_islands") and len(set(player_island_labels)) < int(players):
        return _place_team_island_starts(
            state, players, rng, labels, technical_clear,
        )
    from ..start_safety import candidate_centers, _centers_matching
    side, terrain = state.side, state.terrain
    safe = candidate_centers(state)
    yy, xx = np.indices(terrain.shape)
    edge = max(technical_clear + 8, side // 18)
    preferred_margin = (xx >= edge) & (yy >= edge) & (xx < side - edge) & (yy < side - edge)
    object_distance = distance_from(state.objects != 0, max_distance=max(technical_clear, 8))
    # Larger clearances are preferences, never additional validity conditions.
    clearance_rank = np.zeros_like(terrain, dtype=np.uint8)
    for clearance in (2, 4, 6, 8):
        clearance_rank[~dilate(terrain != GRASS, clearance)] = clearance
    domains = []
    domain_feature_distances = []
    feature_availability = []
    counts = []
    for n in range(1, players + 1):
        island = labels == n
        footprint_inside = _centers_matching(island, START_FOOTPRINT)
        points_yx = np.argwhere(island & safe & footprint_inside)
        count = len(points_yx)
        counts.append(count)
        if not count:
            domains.append(np.empty((0, 2), dtype=np.int64))
            domain_feature_distances.append(np.empty((0, 2), dtype=np.int16))
            feature_availability.append((False, False))
            continue
        if prioritize_team_resources:
            mountain_distance, river_distance = _island_feature_distance_fields(
                terrain, island,
            )
            (
                points_xy, mountain_values, river_values,
                _feature_max, _feature_total, _legacy_points,
            ) = _rank_island_start_candidates(
                points_yx, island, mountain_distance, river_distance,
                object_distance, clearance_rank, preferred_margin, rng,
            )
            domains.append(points_xy)
            domain_feature_distances.append(
                np.column_stack((mountain_values, river_values))
            )
            feature_availability.append((
                mountain_distance is not None, river_distance is not None,
            ))
        else:
            # Keep the established standalone Large Islands ordering and RNG
            # consumption exactly as before R56.
            ys, xs = points_yx.T
            cy, cx = np.argwhere(island).mean(axis=0)
            centre_distance = np.array([
                hex_distance(int(x), int(y), int(round(cx)), int(round(cy)))
                for x, y in zip(xs, ys)
            ])
            order = np.lexsort((
                centre_distance,
                -object_distance[ys, xs].astype(np.int32),
                -clearance_rank[ys, xs].astype(np.int32),
                -preferred_margin[ys, xs].astype(np.int32),
            ))
            top = order[0]
            tied = order[
                (centre_distance[order] == centre_distance[top])
                & (object_distance[ys[order], xs[order]] == object_distance[ys[top], xs[top]])
                & (clearance_rank[ys[order], xs[order]] == clearance_rank[ys[top], xs[top]])
                & (preferred_margin[ys[order], xs[order]] == preferred_margin[ys[top], xs[top]])
            ]
            chosen = int(rng.integers(len(tied)))
            order[0], order[chosen] = order[chosen], order[0]
            domains.append(points_yx[order, ::-1].astype(np.int64))
            domain_feature_distances.append(np.empty((0, 2), dtype=np.int16))
            feature_availability.append((False, False))
    active = [i for i, domain in enumerate(domains) if len(domain)]
    starts = _separated_island_assignment([domains[i] for i in active])
    if starts is None:
        # A complete separated assignment was exhausted. Retain a safe partial
        # result instead of discarding the generated geography.
        from ..start_safety import separated
        starts, retained = [], []
        for i in sorted(active, key=lambda i: (len(domains[i]), i)):
            for x, y in domains[i]:
                if separated(int(x), int(y), starts):
                    starts.append((int(x), int(y))); retained.append(i)
                    break
        ordered = sorted(zip(retained, starts))
        active = [i for i, _ in ordered]
        starts = [point for _, point in ordered]
    state.metadata["start_slot_indices"] = active
    state.metadata["start_disabled_slots"] = [i for i in range(players) if i not in active]
    considered = sum(counts)
    island_start_search = {
        "exhaustive_candidates": True,
        "backtracking": True,
        "candidate_counts": counts,
        "optional_map_margin": edge,
    }
    if prioritize_team_resources:
        island_start_search.update(
            strategy="mountain_and_river_proximity_then_editor_spacing",
            selected_by_player=[],
        )
        selected_by_player = []
        for assignment_index, player in enumerate(active):
            point = starts[assignment_index]
            domain = domains[player]
            matches = np.flatnonzero(
                (domain[:, 0] == point[0]) & (domain[:, 1] == point[1])
            )
            if not len(matches):
                raise RuntimeError("Départ d’île absent du domaine de candidats")
            mountain_value, river_value = domain_feature_distances[player][int(matches[0])]
            has_mountain, has_river = feature_availability[player]
            selected_by_player.append({
                "player_slot": int(player),
                "island": int(player + 1),
                **_start_feature_record(
                    mountain_value if has_mountain else None,
                    river_value if has_river else None,
                ),
            })
        island_start_search["selected_by_player"] = selected_by_player
    state.metadata["island_start_search"] = island_start_search
    state.starts = starts
    state.metadata["large_island_starts"] = {"one_start_per_island": True, "island_labels": [i + 1 for i in active]}
    if topology.get("team_islands"):
        state.metadata["large_island_starts"].update(
            team_islands=True,
            one_start_per_island=False,
            player_island_labels=player_island_labels,
            players_per_island=[1] * int(players),
        )
    state.metadata["startable_mass"] = analyze_startable_masses(terrain, starts, candidate_centers_considered=considered)
    reservation = np.zeros_like(terrain, dtype=bool)
    for x, y in starts:
        for dx, dy in START_FOOTPRINT:
            reservation[y + dy, x + dx] = True
    state.metadata.update(starts_placed_early=True, start_footprint_cells=int(reservation.sum()))
    state.metadata["start_min_spacing"] = min(hex_distance(*a, *b) for i, a in enumerate(starts) for b in starts[i + 1:]) if len(starts) > 1 else 0
    return reservation


def complete_missing_island_rivers(grid, labels, *, seed, generate_native, rng_factory):
    """Retry the native river pass only in islands missed by its first scan."""
    terrain = grid.terrain
    missing = [
        island for island in range(1, int(labels.max()) + 1)
        if not np.any((labels == island) & np.isin(terrain, RIVER_IDS))
    ]
    if not missing:
        return {"island_river_fallback_passes": 0, "island_river_fallback_cells": 0, "island_river_fallback_missing": []}
    allowed = np.isin(labels, missing)
    outside = ~allowed
    saved_terrain = terrain[outside].copy()
    saved_marker = grid.marker[outside].copy()
    saved_variant = grid.variant[outside].copy()
    terrain[outside] = 0
    grid.marker[outside] = 0
    initial = int(np.isin(terrain, RIVER_IDS).sum())
    passes = 0
    try:
        for attempt in range(3):
            generate_native(
                grid,
                rng_factory((int(seed) ^ (0x6D2B79F5 + attempt * 0x9E3779B9)) & 0xFFFFFFFF),
                rate_percent=500.0,
                allow_water_start=False,
            )
            passes += 1
            absent = [
                island for island in missing
                if not np.any((labels == island) & np.isin(terrain, RIVER_IDS))
            ]
            if not absent:
                break
    finally:
        terrain[outside] = saved_terrain
        grid.marker[outside] = saved_marker
        grid.variant[outside] = saved_variant
    absent = [
        island for island in missing
        if not np.any((labels == island) & np.isin(terrain, RIVER_IDS))
    ]
    added = int(np.isin(terrain, RIVER_IDS).sum()) - initial
    return {
        "island_river_fallback_passes": passes,
        "island_river_fallback_cells": max(0, added),
        "island_river_fallback_missing": absent,
    }

def validate_island_contract(state):
    """Report per-island features; native rivers remain a diagnostic in R1."""
    from ..rules import ValidationResult
    features = state.metadata.get("large_island_features")
    if features is None:
        return []
    starts = state.metadata.get("large_island_starts", {})
    topology = state.metadata.get("large_island_topology", {})
    team_mode = bool(topology.get("team_islands"))
    count = (
        int(topology.get("requested_islands", len(features)))
        if team_mode
        else int(state.metadata.get("players", len(state.starts)))
    )
    land_labels, mass_count = component_labels(~np.isin(state.terrain, WATER_IDS))
    start_masses = [int(land_labels[y, x]) for x, y in state.starts]
    if team_mode:
        player_island_labels = [
            int(value) for value in topology.get("player_island_labels", ())
        ]
        slots = [
            int(value) for value in state.metadata.get(
                "start_slot_indices", range(len(state.starts)),
            )
        ]
        placed_island_labels = [
            int(value) for value in starts.get("island_labels", ())
        ]
        labels_match = (
            len(player_island_labels) == int(state.metadata.get("players", len(player_island_labels)))
            and len(slots) == len(state.starts)
            and len(placed_island_labels) == len(state.starts)
            and all(
                0 <= slot < len(player_island_labels)
                and placed_island_labels[index] == player_island_labels[slot]
                for index, slot in enumerate(slots)
            )
        )
        represented = set(placed_island_labels)
        all_groups_have_starts = represented == set(range(1, count + 1))
        component_sets: dict[int, set[int]] = {}
        for island, mass in zip(placed_island_labels, start_masses):
            component_sets.setdefault(island, set()).add(mass)
        group_masses = [component_sets.get(island, set()) for island in range(1, count + 1)]
        no_shared_land_components = all(
            not (group_masses[left] & group_masses[right])
            for left in range(count)
            for right in range(left + 1, count)
        )
        separate = (
            labels_match and all_groups_have_starts and 0 not in start_masses
            and no_shared_land_components and len(features) == count
        )
        start_message = (
            f"coéquipiers groupés sur {count} île(s) distincte(s); "
            f"départs={len(state.starts)}/{state.metadata.get('players', len(state.starts))}"
        )
    else:
        separate = (
            mass_count == count and len(start_masses) == count
            and 0 not in start_masses and len(set(start_masses)) == count
        )
        start_message = "one start per island"
    validations = [
        ValidationResult(
            "ISLAND_STARTS",
            separate and (
                bool(starts.get("team_islands")) if team_mode
                else bool(starts.get("one_start_per_island"))
            ),
            start_message,
            True,
        ),
    ]
    # Mountains/rivers are preset promises, not constraints on a user's
    # thresholds or generator settings. Legal topology remains validated.
    if not state.metadata.get("large_island_topology", {}).get("preset_features_required", True):
        return validations
    from ..start_bonus_policy import swamp_bonus_players
    required_islands = {island for island, eligible in zip(
        starts.get("island_labels", ()), swamp_bonus_players(state)) if eligible}
    swamp_features = [row for row in features if row["island"] in required_islands]
    return validations + [
        ValidationResult("ISLAND_MOUNTAINS", all(row["mountain_cells"] > 0 for row in features), str([row["mountain_cells"] for row in features]), True),
        *([ValidationResult("ISLAND_SWAMPS", all(row["swamp_cells"] > 0 for row in swamp_features), str([row["swamp_cells"] for row in swamp_features]), True)]
          if state.metadata["large_island_topology"].get("start_swamp_required", True) else []),
        ValidationResult("ISLAND_RIVERS", all(row["river_cells"] > 0 for row in features), str([row["river_cells"] for row in features]), True),
    ]
