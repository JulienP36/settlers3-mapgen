"""Custom continental relief on the native midpoint lattice.

Interior anchors follow one stationary, asymmetric distribution at a fixed 32-cell
spacing. A single coastal ring connects that field to the native zero edge.
The height thresholds, rather than any masks or stamped landforms, produce
the coastline, lakes and mountains.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

from ...map_data.hexgrid import component_labels
from .morphology import _bilinear_sample, _interpolated_lattice


CUSTOM_ANCHOR_SPACING = 32
# Reduce only scales 4/2/1 for Custom; keep the broader terrain forms intact.
CUSTOM_FINE_SCALE_BASE_PERCENT = 75
CUSTOM_CENTER_CORNER_BLEND_PERCENT = 75


def seed_custom_legacy_anchors(
    height: np.ndarray,
    rng,
    *,
    variation_percent: int = 100,
) -> None:
    """Seed a stationary inland field and a one-ring coastal transition.

    A continuous low-to-high range replaces the former empty interval between
    45 and 125. The native midpoint steps interpolate between anchors; there
    are no interior distance bands or placed lakes/mountains.
    """
    values = np.asarray(height)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("Le champ d’ancres doit être une matrice carrée")
    side = int(values.shape[0])
    if side < 128 or side % 64:
        raise ValueError("Le relief Legacy Custom exige un côté multiple de 64")

    variation = max(0, min(200, int(variation_percent)))

    def anchor(coastal: bool) -> int:
        sample = int(rng.next())
        low_cutoff = 19661  # 30 % of the native 16-bit samples.
        middle_cutoff = 29491  # A further 15 % crosses the old 45–125 gap.
        if sample < low_cutoff:
            value = sample * 45 // low_cutoff
        elif sample < middle_cutoff:
            value = 45 + (sample - low_cutoff) * 80 // (middle_cutoff - low_cutoff)
        else:
            value = 125 + (sample - middle_cutoff) * 130 // (65536 - middle_cutoff)
        if coastal:
            value = value * 150 // 255
        center = 75 if coastal else 135
        value = center + (value - center) * variation // 100
        return min(255, max(0, value))

    for col in range(CUSTOM_ANCHOR_SPACING, side, CUSTOM_ANCHOR_SPACING):
        for row in range(CUSTOM_ANCHOR_SPACING, side, CUSTOM_ANCHOR_SPACING):
            coastal = min(row, col, side - row, side - col) == CUSTOM_ANCHOR_SPACING
            values[row, col] = np.uint8(anchor(coastal))


def soften_custom_legacy_relief(height: np.ndarray, *, seed: int) -> np.ndarray:
    """Break up square contours and reduce the actual Custom altitude range.

    The curl displacement is smooth and has no preferred horizontal or vertical
    direction. It fades at the native sea border. Peak erosion only lowers
    elevations above their local neighbourhood; the shallow curve lowers the
    first 80 raw levels above the native water floor and joins with slope one.
    All positive elevations are reduced to 65 percent of their former value,
    preserving the water mask. Classification thresholds for this Custom source
    are recalibrated visibly in the archetype profile. This compression also
    lowers the physical heightmap consumed by native river routing.
    """

    raw = np.asarray(height, dtype=np.uint8)
    side = int(raw.shape[0])
    potential = _interpolated_lattice(
        side, (int(seed) ^ 0x5D40C4AB) & 0xFFFFFFFF, 48,
    )
    potential = gaussian_filter(potential, sigma=10)
    row_gradient, col_gradient = np.gradient(potential)
    gradient_scale = max(float(np.percentile(np.hypot(row_gradient, col_gradient), 90)), 1e-6)
    row_gradient = np.clip(row_gradient / gradient_scale * 12, -18, 18)
    col_gradient = np.clip(col_gradient / gradient_scale * 12, -18, 18)
    coordinates = np.arange(side, dtype=np.float32)
    taper = np.clip(np.minimum(coordinates, side - 1 - coordinates) / 48, 0, 1)
    taper = taper * taper * (3 - 2 * taper)
    interior = np.minimum(taper[:, None], taper[None, :])
    warped = np.rint(_bilinear_sample(
        raw,
        coordinates[:, None] + col_gradient * interior,
        coordinates[None, :] - row_gradient * interior,
    )).clip(0, 255).astype(np.uint8)

    values = warped.astype(np.float32)
    neighbourhood = gaussian_filter(values, sigma=6, mode="nearest")
    values -= 0.5 * np.maximum(values - neighbourhood, 0)
    above_water = np.maximum(values - 30, 0)
    fraction = np.minimum(above_water / 80, 1)
    values -= 0.45 * above_water * (1 - fraction) ** 2

    result = np.rint(values).clip(0, 255).astype(np.uint8)
    result[warped <= 30] = warped[warped <= 30]
    result[warped > 30] = np.maximum(result[warped > 30], 31)
    positive = result > 30
    result[positive] = 30 + np.rint(
        (result[positive].astype(np.float32) - 30) * 0.65
    ).astype(np.uint8)
    result[0, :] = result[-1, :] = 0
    result[:, 0] = result[:, -1] = 0
    return result


def retain_largest_land_component(
    height: np.ndarray,
    *,
    water_threshold: int,
    signed_noise: np.ndarray | None = None,
) -> dict[str, int]:
    """Turn detached land fragments into water without shaping the continent.

    The terrain field itself determines the coastline. This final HEX6
    topology rule only removes land components disconnected from the largest
    mainland; it never moves or stamps the mainland boundary.
    """

    values = np.asarray(height)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("Le champ de relief doit être une matrice carrée")
    threshold = int(water_threshold)
    signed = None if signed_noise is None else np.asarray(signed_noise)
    if signed is not None and signed.shape != values.shape:
        raise ValueError("Le bruit signé doit avoir la même taille que le relief")

    if threshold < 0 and signed is not None:
        land = (values > 0) | ((values == 0) & (signed > threshold))
    elif threshold < 0:
        land = values > 0
    else:
        land = values > threshold

    labels, count = component_labels(land)
    if count <= 1:
        return {"components_before": int(count), "removed_cells": 0}

    sizes = np.bincount(labels.ravel(), minlength=count + 1)
    mainland = int(np.argmax(sizes[1:]) + 1)
    detached = (labels > 0) & (labels != mainland)
    removed_cells = int(np.count_nonzero(detached))
    values[detached] = 0
    if signed is not None:
        signed[detached] = threshold
    return {
        "components_before": int(count),
        "removed_cells": removed_cells,
    }


__all__ = (
    "CUSTOM_ANCHOR_SPACING",
    "CUSTOM_FINE_SCALE_BASE_PERCENT",
    "CUSTOM_CENTER_CORNER_BLEND_PERCENT",
    "retain_largest_land_component",
    "seed_custom_legacy_anchors",
    "soften_custom_legacy_relief",
)
