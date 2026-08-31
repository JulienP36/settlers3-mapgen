"""Connected Continental Legacy macro-topology with a calibrated coast library."""

from __future__ import annotations

import heapq
from pathlib import Path

import numpy as np
from scipy import ndimage

from .shapes import place_components
from ...core.noise import warped_fractal_field
from ....map_data.constants import GRASS, SHORE
from ....map_data.hexgrid import HEX6, component_labels, distance_from, neighbor_count


_HEX = np.array(((1, 1, 0), (1, 1, 1), (0, 1, 1)), dtype=bool)
_COAST_LIBRARY_DEFAULT = "data/SETTLERS3_CONTINENTAL_COAST_MORPHOLOGY_V2.npz"
_COAST_LIBRARY_CACHE: dict[str, dict[str, np.ndarray]] = {}


def _neighbours(x: int, y: int, side: int):
    for dx, dy in HEX6:
        xx, yy = x + dx, y + dy
        if 0 <= xx < side and 0 <= yy < side:
            yield xx, yy


def _fill_holes(mask: np.ndarray) -> np.ndarray:
    return ndimage.binary_fill_holes(mask, structure=_HEX)


def _component_count(mask: np.ndarray) -> int:
    return int(component_labels(mask)[1])


def _connected_order(score: np.ndarray, allowed: np.ndarray, count: int) -> np.ndarray:
    """Return a connected mainland growth order from its best centre.

    The old score-threshold/re-add approach restored missing land as arbitrary
    disconnected pixels.  This frontier construction can only create one
    mainland and consequently cannot turn Continental into an archipelago.
    """

    count = max(0, min(int(count), int(allowed.sum())))
    if not count:
        return np.empty(0, dtype=np.intp)
    selected = np.zeros_like(allowed, dtype=bool)
    queued_mask = np.zeros_like(allowed, dtype=bool)
    ys, xs = np.where(allowed)
    start = int(np.argmax(score[ys, xs]))
    x0, y0 = int(xs[start]), int(ys[start])
    heap: list[tuple[float, int, int]] = [(-float(score[y0, x0]), x0, y0)]
    queued_mask[y0, x0] = True
    side = int(allowed.shape[0])
    order: list[int] = []
    while heap and len(order) < count:
        _, x, y = heapq.heappop(heap)
        if selected[y, x] or not allowed[y, x]:
            continue
        selected[y, x] = True
        order.append(y * side + x)
        for xx, yy in _neighbours(x, y, side):
            if not allowed[yy, xx] or selected[yy, xx] or queued_mask[yy, xx]:
                continue
            queued_mask[yy, xx] = True
            heapq.heappush(heap, (-float(score[yy, xx]), xx, yy))
    return np.asarray(order, dtype=np.intp)


def _mainland_mask(score: np.ndarray, allowed: np.ndarray, target: int) -> tuple[np.ndarray, int]:
    """Fill cavities while retaining the requested mainland area as closely as possible."""

    order = _connected_order(score, allowed, target)
    if not len(order):
        return np.zeros_like(allowed, dtype=bool), -int(target)
    lower = max(1, int(len(order) * .72))
    upper = len(order)
    best_mask = np.zeros_like(allowed, dtype=bool)
    best_error = -int(target)
    flat_size = int(allowed.size)
    for _ in range(15):
        prefix = (lower + upper) // 2
        candidate = np.zeros(flat_size, dtype=bool)
        candidate[order[:prefix]] = True
        filled = _fill_holes(candidate.reshape(allowed.shape))
        error = int(filled.sum()) - int(target)
        if abs(error) < abs(best_error):
            best_mask, best_error = filled, error
        if error < 0:
            lower = min(upper, prefix + 1)
        else:
            upper = max(lower, prefix - 1)
        if abs(error) <= 1 or lower >= upper:
            break
    if best_error > 0:
        best_mask = _trim_connected_coast(best_mask, score, target)
        best_error = int(best_mask.sum()) - int(target)
    return best_mask, best_error


def _trim_connected_coast(mask: np.ndarray, score: np.ndarray, target: int) -> np.ndarray:
    """Remove only exterior low-score coast cells until the target is met.

    Every removal is adjacent to the existing ocean, so trimming cannot create
    an enclosed water hole.  A component check preserves the mainland as one
    connected body while retaining the irregular score-driven outline.
    """

    work = mask.copy()
    remaining = int(work.sum()) - int(target)
    while remaining > 0:
        boundary = work & (neighbor_count(~work) > 0)
        ys, xs = np.where(boundary)
        if not len(xs):
            break
        ranked = np.argsort(score[ys, xs])
        batch = min(remaining, len(ranked))
        proposal = work.copy()
        proposal[ys[ranked[:batch]], xs[ranked[:batch]]] = False
        labels, count = component_labels(proposal)
        if count > 1:
            sizes = np.bincount(labels.ravel())
            proposal = labels == int(np.argmax(sizes[1:]) + 1)
        work = proposal
        remaining = int(work.sum()) - int(target)
    return work


def _edge_allowed(side: int, profile: dict, rng: np.random.Generator) -> tuple[np.ndarray, int]:
    """Return an irregular, procedural safety envelope for the continent.

    The native 768 samples keep a deep outer-water frame, but the frame is
    not a rectangle: each edge has several broad coves and a few columns do
    not reach land at all.  A single 2-D field tied to the four map borders
    tended to leave long straight runs.  Four independent smooth edge
    profiles keep the minimum frame legal while making the boundary vary
    continuously along every side.
    """

    cfg = profile["macro"]
    margin_cfg = cfg["shore_edge_distance"]
    base_margin = int(rng.integers(int(margin_cfg["min"]), int(margin_cfg["max"]) + 1))
    yy, xx = np.mgrid[:side, :side]
    hard_margin = float(cfg.get("hard_edge_margin", max(10, side // 64)))
    edge_variation = float(cfg.get("hard_edge_jitter", 20.0))

    def profile_1d() -> np.ndarray:
        field = np.zeros(side, dtype=float)
        for scale, weight in ((.010, .58), (.025, .29), (.055, .13)):
            cells = max(3, int(round(side * scale)))
            coarse = rng.normal(size=cells + 2)
            layer = ndimage.zoom(coarse, side / cells, order=3, mode="reflect")[:side]
            layer = ndimage.gaussian_filter1d(
                layer, sigma=max(1.0, side / (cells * 8)), mode="reflect"
            )
            field += weight * layer / max(float(layer.std()), 1e-9)
        field /= max(float(field.std()), 1e-9)
        # Do not clip a standardised field at zero.  That was the source of
        # the long constant sections in the first R6 envelope.  The bounded
        # sigmoid gives every side a gradual, non-flat margin profile.
        return (np.tanh(field / 1.65) + 1.0) * .5

    top, bottom, left, right = (profile_1d() for _ in range(4))
    allowed = (
        (yy >= hard_margin + edge_variation * top[None, :])
        & (side - 1 - yy >= hard_margin + edge_variation * bottom[None, :])
        & (xx >= hard_margin + edge_variation * left[:, None])
        & (side - 1 - xx >= hard_margin + edge_variation * right[:, None])
    )
    return allowed, base_margin


def _coastal_cove_pressure(
    side: int, cfg: dict, rng: np.random.Generator
) -> np.ndarray:
    """Build a continuous pressure field for ocean-connected coastal coves.

    The field is applied before mainland growth, rather than carving ellipses
    into a finished mask.  Area compensation therefore produces shoulders and
    peninsulas on the opposite coast while retaining one connected mainland.
    Two lobe scales are deliberately combined: a few deep native-like bays
    and a denser set of shallow notches that keep the shoreline from becoming
    a long, nearly monotone curve.
    """

    yy, xx = np.mgrid[:side, :side]
    pressure = np.zeros((side, side), dtype=float)
    tiers = (
        (
            int(cfg.get("coastal_cove_count_by_side", {}).get(str(side), 2)),
            float(cfg.get("coastal_cove_width_min", max(14, side / 42))),
            float(cfg.get("coastal_cove_width_max", max(36, side / 16))),
            float(cfg.get("coastal_cove_depth_min", max(30, side / 18))),
            float(cfg.get("coastal_cove_depth_max", max(72, side / 6))),
            float(cfg.get("coastal_cove_pressure", 1.7)),
            float(cfg.get("coastal_cove_cutoff", 6.0)),
        ),
        (
            int(cfg.get("coastal_cove_small_count_by_side", {}).get(str(side), max(4, side // 96))),
            float(cfg.get("coastal_cove_small_width_min", max(6, side / 110))),
            float(cfg.get("coastal_cove_small_width_max", max(16, side / 38))),
            float(cfg.get("coastal_cove_small_depth_min", max(18, side / 32))),
            float(cfg.get("coastal_cove_small_depth_max", max(42, side / 14))),
            float(cfg.get("coastal_cove_small_pressure", .45)),
            float(cfg.get("coastal_cove_small_cutoff", 4.0)),
        ),
    )

    for count, width_min, width_max, depth_min, depth_max, strength, cutoff in tiers:
        for edge in range(4):
            for _ in range(max(0, count)):
                centre = float(rng.uniform(.08, .92) * side)
                width = float(rng.uniform(width_min, width_max))
                depth = float(rng.uniform(depth_min, depth_max))
                decay = float(rng.uniform(.45, .75) * depth)
                amplitude = float(rng.uniform(.78, 1.22) * strength)
                if edge < 2:
                    tangent = xx
                    distance = yy if edge == 0 else side - 1 - yy
                else:
                    tangent = yy
                    distance = xx if edge == 2 else side - 1 - xx
                lateral = (tangent - centre) / max(width, 1.0)
                lobe = np.exp(-.5 * lateral * lateral)
                lobe *= np.exp(-distance / max(decay, 1.0))
                # A logistic tail avoids the hard ellipse edge while keeping a
                # selected cove from becoming an implausibly long inland fjord.
                lobe *= 1.0 / (1.0 + np.exp((distance - depth) / max(cutoff, 1.0)))
                pressure = np.maximum(pressure, amplitude * lobe)
    return pressure


def _coastal_profile_pressure(
    side: int, cfg: dict, rng: np.random.Generator
) -> np.ndarray:
    """Give each coast side its own continuous, irregular depth profile.

    A radial threshold naturally produces long horizontal and vertical runs
    when the requested land fraction is high.  Native Continental coastlines
    instead have a mostly shallow frame with a few deeper reaches.  This
    pressure describes that depth along each side without drawing a polygon
    or clipping a finished continent.
    """

    yy, xx = np.mgrid[:side, :side]
    base = float(cfg.get("coastal_profile_base", 18.0))
    variation = float(cfg.get("coastal_profile_variation", 42.0))
    minimum = float(cfg.get("coastal_profile_min", 10.0))
    maximum = float(cfg.get("coastal_profile_max", max(64.0, side / 8)))
    cutoff = float(cfg.get("coastal_profile_cutoff", 8.0))
    strength = float(cfg.get("coastal_profile_pressure", .55))

    def depth_profile() -> np.ndarray:
        field = np.zeros(side, dtype=float)
        for scale, weight in ((.010, .46), (.024, .29), (.060, .17), (.145, .08)):
            cells = max(3, int(round(side * scale)))
            coarse = rng.normal(size=cells + 2)
            layer = ndimage.zoom(coarse, side / cells, order=3, mode="reflect")[:side]
            layer = ndimage.gaussian_filter1d(
                layer, sigma=max(1.0, side / (cells * 8)), mode="reflect"
            )
            field += weight * layer / max(float(layer.std()), 1e-9)
        field /= max(float(field.std()), 1e-9)
        fraction = (np.tanh(field / 1.35) + 1.0) * .5
        return np.clip(base + variation * fraction, minimum, maximum)

    top, bottom, left, right = (depth_profile() for _ in range(4))
    top_lobe = 1.0 / (1.0 + np.exp((yy - top[None, :]) / max(cutoff, 1.0)))
    bottom_lobe = 1.0 / (
        1.0 + np.exp(((side - 1 - yy) - bottom[None, :]) / max(cutoff, 1.0))
    )
    left_lobe = 1.0 / (1.0 + np.exp((xx - left[:, None]) / max(cutoff, 1.0)))
    right_lobe = 1.0 / (
        1.0 + np.exp(((side - 1 - xx) - right[:, None]) / max(cutoff, 1.0))
    )
    return strength * np.maximum.reduce((top_lobe, bottom_lobe, left_lobe, right_lobe))


def _coastal_morphology_score(
    side: int,
    profile: dict,
    rng: np.random.Generator,
    allowed: np.ndarray,
    target: int,
    players: int | None,
) -> tuple[np.ndarray, dict] | None:
    """Return a score anchored to a measured native coast silhouette.

    The binary library is derived from the supplied SAV corpus offline.  It
    contains only filled outer-mainland masks, never terrain, objects or
    player claims.  At runtime a density-appropriate mask is transformed by
    one of the four HEX-safe symmetries and given a small smooth boundary
    displacement.  The normal connected growth step still owns the final
    cell count and connectivity.
    """

    if int(side) != 768:
        return None
    library_cfg = profile.get("morphology_library", {})
    configured = Path(str(library_cfg.get("path", _COAST_LIBRARY_DEFAULT)))
    if not configured.is_absolute():
        configured = Path(__file__).resolve().parents[4] / configured
    cache_key = str(configured.resolve())
    try:
        library = _COAST_LIBRARY_CACHE.get(cache_key)
        if library is None:
            with np.load(configured, allow_pickle=False) as source:
                library = {
                    key: np.asarray(source[key], dtype=bool).copy()
                    for key in ("masks_2p", "masks_20p")
                    if key in source.files
                }
            if not library:
                return None
            _COAST_LIBRARY_CACHE[cache_key] = library
    except (OSError, ValueError, KeyError):
        # Smaller sizes remain fully procedural when the optional 768
        # calibration asset is not present in a source-only checkout.
        return None

    split = int(library_cfg.get("density_split_players", 8))
    bank_key = "masks_20p" if players is not None and int(players) > split else "masks_2p"
    bank = library.get(bank_key)
    if bank is None or bank.ndim != 3 or bank.shape[1:] != (side, side) or not len(bank):
        return None
    index = int(rng.integers(len(bank)))
    transform = int(rng.integers(4))
    template = bank[index]
    if transform == 1:
        template = np.rot90(template, 2).copy()
    elif transform == 2:
        template = template.T.copy()
    elif transform == 3:
        template = np.rot90(template.T, 2).copy()
    template &= allowed

    signed_distance = (
        ndimage.distance_transform_edt(template)
        - ndimage.distance_transform_edt(~template)
    )
    deformation = warped_fractal_field(
        side,
        rng,
        scales=(.016, .040, .105),
        warp_scale=.026,
        warp_strength=.065,
    )
    band_width = float(library_cfg.get("deformation_band_cells", 36.0))
    amplitude = float(library_cfg.get("deformation_amplitude", 5.5))
    coast_band = np.exp(-((np.abs(signed_distance) / max(1.0, band_width)) ** 2))
    score = signed_distance + amplitude * deformation * coast_band
    return score, {
        "macro_morphology_source": "derived_native_coast_library_v2",
        "macro_morphology_bank": bank_key,
        "macro_morphology_index": index,
        "macro_morphology_transform": transform,
        "macro_morphology_deformation_cells": amplitude,
    }


def _coastal_inlet_pressure(
    side: int, cfg: dict, rng: np.random.Generator
) -> np.ndarray:
    """Build narrow, curved ocean inlets before connected land growth.

    The reference coast is not made only of rounded bays.  It also contains
    short branching arms of water that cut into the mainland and leave narrow
    peninsulas between them.  These walks are a score pressure, not a later
    mask cut, so the connected mainland selector can keep the result as one
    mass while choosing the compensating shoulders naturally.
    """

    pressure = np.zeros((side, side), dtype=float)
    count = int(cfg.get("coastal_inlet_count_by_side", {}).get(str(side), max(2, side // 160)))
    length_min = float(cfg.get("coastal_inlet_length_min", max(24, side / 22)))
    length_max = float(cfg.get("coastal_inlet_length_max", max(72, side / 6)))
    width_min = float(cfg.get("coastal_inlet_width_min", max(3, side / 190)))
    width_max = float(cfg.get("coastal_inlet_width_max", max(8, side / 70)))
    strength = float(cfg.get("coastal_inlet_pressure", .90))
    branch_chance = float(cfg.get("coastal_inlet_branch_chance", .35))

    def walk(
        edge: int,
        x: float,
        y: float,
        length: int,
        initial_drift: float,
    ) -> tuple[np.ndarray, list[tuple[float, float]]]:
        path = np.zeros((side, side), dtype=bool)
        if edge == 0:
            inward = (0.0, 1.0)
            tangent = (1.0, 0.0)
        elif edge == 1:
            inward = (0.0, -1.0)
            tangent = (1.0, 0.0)
        elif edge == 2:
            inward = (1.0, 0.0)
            tangent = (0.0, 1.0)
        else:
            inward = (-1.0, 0.0)
            tangent = (0.0, 1.0)

        drift = float(initial_drift)
        points: list[tuple[float, float]] = []
        for _ in range(max(1, int(length))):
            ix, iy = int(round(x)), int(round(y))
            if not (0 <= ix < side and 0 <= iy < side):
                break
            path[iy, ix] = True
            points.append((x, y))
            drift = .78 * drift + .22 * float(rng.normal(0.0, .75))
            drift = float(np.clip(drift, -1.7, 1.7))
            x += inward[0] + tangent[0] * drift
            y += inward[1] + tangent[1] * drift
            if x < 2 or x >= side - 3 or y < 2 or y >= side - 3:
                break
        return path, points

    for edge in range(4):
        for _ in range(max(0, count)):
            tangent_start = float(rng.uniform(.08, .92) * side)
            length = int(round(rng.uniform(length_min, length_max)))
            width = float(rng.uniform(width_min, width_max))
            if edge == 0:
                start = (tangent_start, 0.0)
            elif edge == 1:
                start = (tangent_start, float(side - 1))
            elif edge == 2:
                start = (0.0, tangent_start)
            else:
                start = (float(side - 1), tangent_start)
            main_path, points = walk(
                edge, start[0], start[1], length, float(rng.normal(0.0, .45))
            )
            local = main_path
            if rng.random() < branch_chance and len(points) >= 20:
                branch_index = int(rng.integers(max(5, len(points) // 4), max(6, len(points) * 3 // 4)))
                branch_x, branch_y = points[branch_index]
                branch_length = int(round(rng.uniform(.20, .42) * length))
                branch_sign = -1.0 if rng.random() < .5 else 1.0
                branch_path, _ = walk(
                    edge,
                    branch_x,
                    branch_y,
                    branch_length,
                    branch_sign * rng.uniform(.65, 1.35),
                )
                local |= branch_path
            distance = ndimage.distance_transform_edt(~local)
            lobe = np.exp(-.5 * (distance / max(width, 1.0)) ** 2)
            pressure = np.maximum(pressure, strength * rng.uniform(.78, 1.18) * lobe)
    return pressure


def _macro_target_land(side: int, profile: dict) -> tuple[int, int, int]:
    """Reserve the measured inland-lake share before shaping the ocean."""

    total = side * side
    water_fraction = float(profile["supported_sizes"][str(side)]["water_fraction"]["mean"])
    lake_fraction = float(profile["lakes"]["fraction_map_by_side"][str(side)])
    satellite = int(round(total * float(profile["macro"].get("satellite_island_fraction", 0.0))))
    mainland = int(round(total * (1.0 - max(0.0, water_fraction - lake_fraction)))) - satellite
    return max(1, mainland), satellite, int(round(total * water_fraction))


def _carve_coastal_bays(mainland: np.ndarray, profile: dict, rng: np.random.Generator) -> tuple[np.ndarray, int]:
    """Open a small number of irregular bays from the existing ocean.

    The carving support is deliberately restricted to a shallow coastal band
    and every retained component must touch pre-existing water.  It therefore
    adds coastline variation without manufacturing inland lakes or cutting
    terrain with a rectangular map limit.
    """

    side = int(mainland.shape[0])
    cfg = profile["macro"]
    fraction = float(cfg.get("coastal_bay_fraction", 0.0))
    target = int(round(side * side * fraction))
    if target <= 0:
        return mainland, 0
    water = ~mainland
    maximum_depth = int(cfg.get("coastal_bay_max_depth", max(18, side // 18)))
    support = mainland & (distance_from(water, max_distance=maximum_depth) <= maximum_depth)
    requested = place_components(
        support,
        target,
        int(cfg.get("coastal_bay_count_by_side", {}).get(str(side), max(4, side // 96))),
        0,
        rng,
        name="coastal_bay",
        major_min=max(16, side // 38),
        major_max=max(96, side // 5),
        major_sigma=.70,
        aspect_range=(1.0, 3.4),
        separation=True,
    )
    labels, count = component_labels(requested)
    touches_water = neighbor_count(water) > 0
    keep = np.zeros_like(requested, dtype=bool)
    for label in range(1, count + 1):
        component = labels == label
        if np.any(component & touches_water):
            keep |= component
    carved = mainland & ~keep
    # A bay may occasionally cut a thin peninsula.  Continental keeps only
    # the true mainland; any detached remnant returns to the ocean instead of
    # becoming an accidental extra island.
    labels, count = component_labels(carved)
    if count > 1:
        sizes = np.bincount(labels.ravel())
        carved = labels == int(np.argmax(sizes[1:]) + 1)
    return carved, int(keep.sum())


def create_macro_topology(
    side: int,
    profile: dict,
    rng: np.random.Generator,
    players: int | None = None,
) -> tuple[np.ndarray, dict]:
    """Build a single irregular mainland and a deliberately small satellite set.

    Runtime inputs are limited to the side, player density, profile and
    deterministic seed stream.  The 768 coast asset is a compact derived
    morphology library; raw SAVs, images and complete native maps are never
    read during execution.
    """

    side = int(side)
    mainland_target, satellite_target, target_water = _macro_target_land(side, profile)
    allowed, margin = _edge_allowed(side, profile, rng)
    if int(allowed.sum()) < mainland_target:
        raise RuntimeError("Marge océanique incompatible avec la surface continentale demandée")

    cfg = profile["macro"]
    yy, xx = np.mgrid[:side, :side]
    # Resolve the calibrated 768 morphology before preparing the generic
    # fallback score.  When it is available, that score is replaced below;
    # keeping the decision early lets the expensive fallback fields stay lazy.
    morphology_result = _coastal_morphology_score(
        side, profile, rng, allowed, mainland_target, players
    )
    use_morphology = morphology_result is not None
    cx = (side - 1) * (0.50 + rng.uniform(-0.035, 0.035)) if not use_morphology else 0.0
    cy = (side - 1) * (0.50 + rng.uniform(-0.035, 0.035)) if not use_morphology else 0.0
    angle = float(rng.uniform(0.0, np.pi)) if not use_morphology else 0.0
    ca, sa = np.cos(angle), np.sin(angle)
    dx = (xx - cx) / side
    dy = (yy - cy) / side
    u = ca * dx + sa * dy
    v = -sa * dx + ca * dy
    aspect = float(rng.uniform(0.89, 1.12)) if not use_morphology else 1.0
    radial = np.sqrt((u / aspect) ** 2 + (v * aspect) ** 2)

    # The native contour is a broad, asymmetric lobe system with medium bays
    # and a visibly toothed fine edge.  R5 put most of its coast detail on
    # map-border lines, which made the one-cell/short-run perimeter much too
    # high.  These fields are all two-dimensional and are blended before the
    # connected growth step.
    broad = np.zeros((side, side), dtype=float) if use_morphology else warped_fractal_field(
        side, rng, scales=(0.0045, 0.010, 0.024), warp_scale=.020, warp_strength=.100,
    )
    contour = np.zeros((side, side), dtype=float) if use_morphology else warped_fractal_field(
        side, rng, scales=(0.014, 0.035, 0.080), warp_scale=.036, warp_strength=.080,
    )
    coast_detail = np.zeros((side, side), dtype=float) if use_morphology else warped_fractal_field(
        side, rng, scales=(0.045, 0.105, 0.240), warp_scale=.045, warp_strength=.085,
    )
    edge_distance = np.minimum.reduce((xx, yy, side - 1 - xx, side - 1 - yy)).astype(float)
    # The measured ~40-cell native margin is used as a soft pressure, not as
    # a square mask.  Local 2-D variation permits broad protrusions while
    # retaining water on every map edge.
    border_field = np.zeros((side, side), dtype=float) if use_morphology else warped_fractal_field(
        side, rng, scales=(0.008, 0.020, 0.050), warp_scale=.025, warp_strength=.080,
    )
    soft_margin = (
        float(margin)
        + float(cfg.get("soft_edge_offset", 10.0))
        + float(cfg.get("soft_edge_jitter", 4.0)) * border_field
    )
    border_pressure = np.clip(
        (soft_margin - edge_distance) / float(cfg.get("soft_edge_falloff", 36.0)),
        0.0,
        1.5,
    )
    cove_pressure = np.zeros((side, side), dtype=float) if use_morphology else _coastal_cove_pressure(side, cfg, rng)
    profile_pressure = np.zeros((side, side), dtype=float) if use_morphology else _coastal_profile_pressure(side, cfg, rng)
    inlet_pressure = np.zeros((side, side), dtype=float) if use_morphology else _coastal_inlet_pressure(side, cfg, rng)
    theta = np.arctan2(dy, dx)
    harmonics = np.zeros((side, side), dtype=float) if use_morphology else float(cfg.get("coast_harmonic_weight", 1.0)) * (
        .070 * np.sin(3.0 * theta + rng.uniform(0, 2 * np.pi))
        + .046 * np.sin(5.0 * theta + rng.uniform(0, 2 * np.pi))
        + .026 * np.sin(9.0 * theta + rng.uniform(0, 2 * np.pi))
    )
    radial_fraction = min(.99, max(.01, float(mainland_target) / max(1, int(allowed.sum()))))
    coast_radius = float(np.quantile(radial[allowed], radial_fraction))
    coast_band = np.exp(-((radial - coast_radius) / .075) ** 2)
    score = (
        -radial
        + float(cfg.get("coast_broad_weight", .360)) * broad
        + float(cfg.get("coast_contour_weight", .200)) * contour
        + float(cfg.get("coast_detail_weight", .095)) * coast_detail * coast_band
        + harmonics
        - float(cfg.get("soft_edge_pressure", .60)) * border_pressure
        - cove_pressure
        - profile_pressure
        - inlet_pressure
    )
    morphology_meta = {}
    if morphology_result is not None:
        score, morphology_meta = morphology_result
    score = ndimage.gaussian_filter(
        score,
        sigma=float(cfg.get("coast_score_smoothing", 1.0)),
        mode="reflect",
    )
    score[~allowed] = -np.inf
    mainland, mainland_target_error = _mainland_mask(score, allowed, mainland_target)
    # R6 no longer punches independent ellipse-like bays into the completed
    # continent.  The same field that builds the outer silhouette now creates
    # its coves and shoulders, so no later shape can be visibly laid over it.
    bay_cells = 0
    coast_band = allowed & ~mainland
    distance = distance_from(mainland, max_distance=max(14, side // 10))
    coast_band &= (distance >= int(profile["macro"].get("satellite_min_distance", 6)))
    coast_band &= (distance <= int(profile["macro"].get("satellite_max_distance", max(12, side // 12))))
    satellites = np.zeros_like(mainland)
    if satellite_target and coast_band.any():
        components = int(profile["macro"].get("satellite_component_count", 7))
        satellites = place_components(
            coast_band,
            satellite_target,
            components,
            0,
            rng,
            name="satellite",
            major_min=max(12, side // 58),
            major_max=max(44, side // 7),
            major_sigma=.62,
            aspect_range=(1.0, 2.5),
            separation=True,
        )
        satellites = _fill_holes(satellites)
    land = mainland | satellites
    water_mask = ~land

    terrain = np.full((side, side), GRASS, dtype=np.uint8)
    ocean_distance = distance_from(land, max_distance=8)
    terrain[water_mask] = np.minimum(np.maximum(ocean_distance[water_mask] - 1, 0), 7).astype(np.uint8)
    terrain[land & (neighbor_count(water_mask) > 0)] = SHORE
    return terrain, {
        "macro_target_water": target_water,
        "macro_target_mainland": mainland_target,
        "macro_land": int(land.sum()),
        "macro_water": int(water_mask.sum()),
        "macro_margin": margin,
        "macro_mainland_components": _component_count(mainland),
        "macro_satellite_components": _component_count(satellites),
        "macro_satellite_target": satellite_target,
        "macro_mainland_target_error": mainland_target_error,
        "macro_coastal_bay_cells": bay_cells,
        **morphology_meta,
    }


__all__ = ("create_macro_topology",)
