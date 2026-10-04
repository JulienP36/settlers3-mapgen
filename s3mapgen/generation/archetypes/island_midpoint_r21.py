"""Independent, local hierarchical relief inspired by Classic's midpoints."""
from __future__ import annotations

import numpy as np
from scipy.ndimage import map_coordinates

from .noise_sources import _simplex_noise


def midpoint_signal(x, y, wavelength: float, seed: int) -> np.ndarray:
    """Refine random anchors down to one cell, then sample a rotated grid.

    Only the requested local domain is constructed. Random offsets/rotation
    and a blend of diagonal and four-corner centres avoid a shared grid of
    aligned peaks. This neither builds a continent nor uses the native PRNG.
    Perturbations decrease linearly with the cell scale, as in Classic.
    """
    x, y = np.asarray(x, np.float32), np.asarray(y, np.float32)
    if not x.size:
        return np.empty(x.shape, np.float32)
    rng = np.random.default_rng(int(seed) & 0xFFFFFFFF)
    spacing = 2 ** int(np.clip(round(np.log2(max(8., wavelength))), 3, 7))
    angle = rng.uniform(0., 2 * np.pi)
    cosine, sine = np.cos(angle), np.sin(angle)
    # Distort the refinement coordinates at the anchor scale, so coarse
    # interpolated ridges do not remain straight triangular facets.
    dx = x - float(x.min())
    dy = y - float(y.min())
    nx, ny = dx / spacing, dy / spacing
    warped_x = dx + spacing * .55 * _simplex_noise(nx, ny, (int(seed) + 811) & 0xFFFFFFFF)
    warped_y = dy + spacing * .55 * _simplex_noise(nx, ny, (int(seed) + 977) & 0xFFFFFFFF)
    dx, dy = warped_x, warped_y
    u, v = cosine * dx - sine * dy, sine * dx + cosine * dy
    u = u - u.min() + rng.uniform(0, spacing)
    v = v - v.min() + rng.uniform(0, spacing)
    width = (int(np.ceil(float(u.max()) / spacing)) + 1) * spacing + 1
    height = (int(np.ceil(float(v.max()) / spacing)) + 1) * spacing + 1
    field = _refined_grid(height, width, spacing, rng)
    return map_coordinates(field, [v, u], order=1, mode='nearest', prefilter=False).astype(np.float32)


def _refined_grid(height: int, width: int, spacing: int, rng) -> np.ndarray:
    """Vectorize each refinement level over this local padded grid."""
    field = np.zeros((height, width), np.float32)
    field[::spacing, ::spacing] = rng.uniform(-1., 1., field[::spacing, ::spacing].shape)
    scale = spacing // 2
    while scale:
        step = 2 * scale
        a = field[::step, ::step].copy()
        delta = 1.1 * scale / spacing
        field[scale::step, ::step] = (a[:-1] + a[1:]) * .5 + rng.uniform(-delta, delta, (a.shape[0]-1, a.shape[1]))
        field[::step, scale::step] = (a[:, :-1] + a[:, 1:]) * .5 + rng.uniform(-delta, delta, (a.shape[0], a.shape[1]-1))
        # Keep Classic's opposite-corner principle without its fixed diagonal.
        centre = (a[:-1, :-1] + a[1:, 1:]) * .375 + (a[:-1, 1:] + a[1:, :-1]) * .125
        field[scale::step, scale::step] = centre + rng.uniform(-delta, delta, centre.shape)
        scale //= 2
    return field
