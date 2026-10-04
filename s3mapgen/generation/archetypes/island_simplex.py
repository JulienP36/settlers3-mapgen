"""Local multiscale island noise with no field-dependent coordinate warp."""

from __future__ import annotations

import numpy as np

from .noise_sources import _simplex_noise, _SIMPLEX_GRADIENTS


# Keep the old direction associated with the low hash bits, but spread it
# over four angles. Equal lengths remove the stronger diagonal gradients;
# RMS length matches the previous table's energy, rather than raising relief.
_indices = np.arange(32)
_base = _SIMPLEX_GRADIENTS[_indices & 7]
_angles = np.arctan2(_base[:, 1], _base[:, 0]) + ((_indices >> 3) - 1.5) * (np.pi / 16.)
_RELIEF_GRADIENTS = (np.column_stack((np.cos(_angles), np.sin(_angles))) * np.sqrt(1.5)).astype(np.float32)


def simplex_signal(x, y, wavelength: float, seed: int, *, rounded_relief=False) -> np.ndarray:
    """Combine broad shapes and weaker details at a bounded local cost.

    Each octave uses an independent seed and a fixed affine rotation/phase.
    Coordinates never depend on sampled noise. Wavelength follows the island's
    radius continuously; details below two cells are not evaluated. At most
    six vectorized octaves are needed, with no padded refinement grids.
    """
    x, y = np.asarray(x, np.float32), np.asarray(y, np.float32)
    if not x.size:
        return np.empty(x.shape, np.float32)
    rng = np.random.default_rng(int(seed) & 0xFFFFFFFF)
    dx, dy = x - float(x.min()), y - float(y.min())
    period = max(8., float(wavelength) * 1.6)
    result = np.zeros(x.shape, np.float32)
    amplitude, total = 1., 0.
    for octave in range(6):
        if period < 2.:
            break
        angle = rng.uniform(0., 2. * np.pi)
        phase_x, phase_y = rng.uniform(0., 256., 2)
        cosine, sine = np.cos(angle), np.sin(angle)
        u = (cosine * dx - sine * dy) / period + phase_x
        v = (sine * dx + cosine * dy) / period + phase_y
        local_seed = (int(seed) + octave * 104729) & 0xFFFFFFFF
        if rounded_relief:
            sample = _simplex_noise(u, v, local_seed, gradients=_RELIEF_GRADIENTS)
        else:
            sample = _simplex_noise(u, v, local_seed)
        result += amplitude * sample
        total += amplitude
        amplitude *= .52
        period *= .5
    # Fixed amplitude calibration; no domain-dependent quantile remapping.
    return (result / total).astype(np.float32)
