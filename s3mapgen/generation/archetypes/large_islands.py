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


def _coastal_progression(depth, maximum_depth):
    """A continuous rise: almost black at sea, accelerating further inland.

    No upper envelope is intersected with an already-built height field. The
    island's depth sets the length scale, without creating a constant-height
    interior or imposing a peak at a geometric centre.
    """
    scale = max(16., float(maximum_depth) * .45)
    relative_depth = np.asarray(depth, dtype=np.float32) / scale
    return -np.expm1(-np.power(relative_depth, 2.4))


def _local_island_relief(signal, depth, radius, water_threshold):
    """Keep coastal byte slopes and inland noise amplitude across island sizes.

    Weight the noise statistics towards land where relief can develop. This
    removes whole-island height bias without painting or enforcing mountain
    areas. A separate low initial rise survives integer rounding at the coast;
    its 24-cell decay length does not grow with the island.
    """
    depth = np.asarray(depth, dtype=np.float32)
    progression = _coastal_progression(depth, depth.max())
    mean = float(np.average(signal, weights=progression))
    deviation = float(np.sqrt(np.average(
        (signal - mean) ** 2, weights=progression,
    )))
    normalized = (signal - mean) / max(.1, deviation) * .8
    # The native relaxation has a fixed cell scale. Smaller islands need a
    # higher source mean to retain broad hills after that same relaxation.
    source_mean = np.float32(147. + 48. * min(1., 45. / radius) ** 2)
    threshold = int(water_threshold)
    level = np.float32(threshold + (225. - threshold) * float(source_mean) / 225.)
    raw_relief = level + (225. - level) * np.tanh(normalized)
    coastal_rise = 1.5 * depth * np.exp(-depth / 24.)
    # Only the highest source altitudes are compressed; foothills retain their
    # span and the snow threshold remains an ordinary user-controlled threshold.
    knee = threshold + (225. - threshold) * (175. / 225.)
    raw_relief -= .32 * np.maximum(raw_relief - knee, 0.)
    relief = threshold + (raw_relief - threshold) * progression + coastal_rise
    return raw_relief, relief


def _smooth_noise(x, y, wavelength, seed):
    # Simplex has no axis-aligned cell edges; wavelengths are measured in map
    # cells, relative to each island rather than the complete continental map.
    from .noise_sources import _simplex_noise
    return _simplex_noise(x / wavelength, y / wavelength, int(seed) & 0xFFFFFFFF)


def _island_layout(side, count, seed):
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
    target = len(points) / count
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
            weights[n] += (target - len(owned)) / target * spacing ** 2 * .15
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


def build_island_masks(side, players, seed, *, variant_r21=False):
    """Grow comparable, connected islands independently to ~56.5% source land, leaving room for native shores."""
    signal_provider = midpoint_signal_r21 if variant_r21 else simplex_signal
    count = int(players)
    if count < 2:
        raise ValueError("Grandes îles exige au moins deux joueurs")
    target = round(side * side * .565 / count)
    channel = max(8, round(side * .015))
    yy, xx = np.indices((side, side), dtype=np.float32)
    radius = np.sqrt(target / np.pi)
    for attempt in range(8):
        centers, territories = _island_layout(side, count, int(seed) + attempt * 104729)
        labels = np.zeros((side, side), np.int16)
        for n, (cx, cy) in enumerate(centers, 1):
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
    raise RuntimeError("Impossible de répartir des îles comparables avec des chenaux navigables")


def generate_independent_islands(
    height, *, players, water_threshold, mountain_threshold, snow_threshold, seed,
    native_relaxation: Callable[[np.ndarray], tuple[np.ndarray, int]] | None = None,
    stage_sink: dict | None = None,
    variant_r21: bool = False,
):
    """Pack independent masks, generate local relief, then relax natively.

    The input supplies the map dimensions only. No continental height sample,
    quantile remapping or post-smoothing mountain uplift is retained from R3.
    """
    source = np.asarray(height, dtype=np.uint8)
    if source.ndim != 2 or source.shape[0] != source.shape[1]:
        raise ValueError("Le relief doit être carré")
    side = source.shape[0]
    count = int(players)
    threshold = max(0, int(water_threshold))
    labels, centers, mask, channel, layout_attempt = build_island_masks(side, count, seed, variant_r21=variant_r21)
    signal_provider = midpoint_signal_r21 if variant_r21 else simplex_signal
    yy, xx = np.indices(source.shape, dtype=np.float32)
    sizes = [int(np.count_nonzero(labels == n)) for n in range(1, count + 1)]
    depths = distance_from(labels == 0).astype(np.float32)
    output = np.zeros_like(source)
    raw_output = np.zeros_like(source)
    selected = np.zeros_like(source)
    attempts = [0] * count
    missing = set(range(1, count + 1))
    native_passes = 0
    # Retry only a deficient island's own noise. The mask and other islands
    # remain fixed; mountains are consequences of broad local relief.
    for attempt in range(32):
        for n in sorted(missing):
            radius = np.sqrt(sizes[n - 1] / np.pi)
            local_seed = int(seed) + n * 7919 + attempt * 104729
            island = labels == n
            local_x, local_y = xx[island], yy[island]
            if variant_r21:
                signal = signal_provider(local_x, local_y, radius * .8, local_seed + 919)
            else:
                signal = signal_provider(local_x, local_y, radius * .8, local_seed + 919, rounded_relief=True)
            raw_relief, relief = _local_island_relief(
                signal, depths[island], radius, threshold,
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
        "retained_land_cells": int(np.count_nonzero(labels)),
        "island_sizes": sizes, "island_centers": centers.tolist(),
        "construction": ("balanced_rotated_midpoint_with_uniform_contour_detail" if variant_r21
                         else "balanced_multiscale_simplex_with_rounded_contour_detail"),
        "coastal_profile": "nonzero_initial_slope_midpoint_soft_summits",
        "target_land_percent": 56.5, "boat_channel_cells": channel,
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


def place_island_starts(state, players, rng, labels, technical_clear):
    """Pick safe grass footprints independently on each already-created island."""
    if int(labels.max()) != int(players):
        raise RuntimeError("Le nombre d’îles ne correspond pas aux joueurs")
    side, terrain = state.side, state.terrain
    yy, xx = np.indices(terrain.shape)
    edge = max(technical_clear + 8, side // 18)
    object_distance = distance_from(state.objects != 0, max_distance=max(technical_clear, 8))
    starts = []
    considered = 0
    for n in range(1, players + 1):
        island = labels == n
        candidates = []
        for clearance in (8, 6, 4, 2, 0):
            mask = island & (terrain == GRASS) & (xx >= edge) & (yy >= edge) & (xx < side - edge) & (yy < side - edge)
            if clearance:
                mask &= ~dilate(terrain != GRASS, clearance)
            points = np.argwhere(mask)
            if len(points) > max(1, 16000 // players):
                points = points[rng.choice(len(points), max(1, 16000 // players), replace=False)]
            candidates = [
                (int(x), int(y)) for y, x in points
                if all(
                    0 <= x + dx < side and 0 <= y + dy < side
                    and terrain[y + dy, x + dx] == GRASS
                    and labels[y + dy, x + dx] == n
                    and state.objects[y + dy, x + dx] == 0
                    for dx, dy in START_FOOTPRINT
                )
            ]
            if candidates:
                break
        if not candidates:
            raise RuntimeError(f"Aucun départ admissible sur l’île {n}")
        considered += len(candidates)
        best = max(int(object_distance[y, x]) for x, y in candidates)
        candidates = [(x, y) for x, y in candidates if int(object_distance[y, x]) == best]
        cy, cx = np.argwhere(island).mean(axis=0)
        nearest = min(hex_distance(x, y, int(round(cx)), int(round(cy))) for x, y in candidates)
        candidates = [(x, y) for x, y in candidates if hex_distance(x, y, int(round(cx)), int(round(cy))) == nearest]
        starts.append(candidates[int(rng.integers(len(candidates)))])
    state.starts = starts
    state.metadata["large_island_starts"] = {"one_start_per_island": True, "island_labels": list(range(1, players + 1))}
    state.metadata["startable_mass"] = analyze_startable_masses(terrain, starts, candidate_centers_considered=considered)
    reservation = np.zeros_like(terrain, dtype=bool)
    for x, y in starts:
        for dx, dy in START_FOOTPRINT:
            reservation[y + dy, x + dx] = True
    state.metadata.update(starts_placed_early=True, start_footprint_cells=int(reservation.sum()))
    state.metadata["start_min_spacing"] = min(hex_distance(*a, *b) for i, a in enumerate(starts) for b in starts[i + 1:])
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
    count = int(state.metadata.get("players", len(state.starts)))
    land_labels, mass_count = component_labels(~np.isin(state.terrain, WATER_IDS))
    start_masses = [int(land_labels[y, x]) for x, y in state.starts]
    separate = mass_count == count and len(start_masses) == count and 0 not in start_masses and len(set(start_masses)) == count
    validations = [
        ValidationResult("ISLAND_STARTS", separate and bool(starts.get("one_start_per_island")) and len(features) == count, "one start per island", True),
    ]
    # Mountains/rivers are preset promises, not constraints on a user's
    # thresholds or generator settings. Legal topology remains validated.
    if not state.metadata.get("large_island_topology", {}).get("preset_features_required", True):
        return validations
    return validations + [
        ValidationResult("ISLAND_MOUNTAINS", all(row["mountain_cells"] > 0 for row in features), str([row["mountain_cells"] for row in features]), True),
        *([ValidationResult("ISLAND_SWAMPS", all(row["swamp_cells"] > 0 for row in features), str([row["swamp_cells"] for row in features]), True)]
          if state.metadata["large_island_topology"].get("start_swamp_required", True) else []),
        ValidationResult("ISLAND_RIVERS", all(row["river_cells"] > 0 for row in features), str([row["river_cells"] for row in features]), True),
    ]
