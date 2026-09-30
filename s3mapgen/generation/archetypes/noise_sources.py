"""Fast deterministic 2-D noise sources for the archetype editor.

Every provider returns an autonomous scalar field.  Providers do not know
about Settlers terrain classes, coastlines or the Legacy land mask: they only
produce values in ``[-1, 1]`` inside a finite rectangular domain.  The native
generator remains responsible for turning the composed elevation map into a
macro map.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np


NOISE_SOURCE_OPTIONS = (
    "white",
    "value",
    "perlin",
    "simplex",
    "fbm",
    "hybrid_fbm",
    "heterogeneous_fbm",
    "billow",
    "turbulence",
    "ridged",
    "ridged_multifractal",
    "worley",
    "worley_f1",
    "worley_f2",
    "worley_f2_minus_f1",
    "domain_warp",
)

NOISE_FREQUENCY_REFERENCE_SIDE = 768
NOISE_FREQUENCY_SIZE_EXPONENT = 0.1
NOISE_FREQUENCY_MIN_CELLS_PER_PERIOD = 4.0
NOISE_FREQUENCY_FADE_FULL_WEIGHT_PERIOD_MULTIPLIER = 2.0

_COMMON_OUTPUT_TRANSFORM_SETTINGS = frozenset(
    {
        "inversion_percent",
        "absolute_percent",
        "gamma_percent",
        "terrace_steps",
        "terrace_blend_percent",
        "remap_low_percent",
        "remap_high_percent",
        "threshold_low_percent",
        "threshold_high_percent",
        "threshold_softness_percent",
        "clamp_low_percent",
        "clamp_high_percent",
        "curve_bias_percent",
    }
)

_COORDINATE_TRANSFORM_SETTINGS = frozenset(
    {
        "offset_x_percent",
        "offset_y_percent",
        "scale_x_percent",
        "scale_y_percent",
        "repeat_x",
        "repeat_y",
        "symmetry_x_percent",
        "symmetry_y_percent",
    }
)

# Keep the editor honest about which controls a provider actually consumes.
# A single-source provider should not appear to react to octave/lacunarity
# controls that it never reads.  The common bias/contrast/seed controls are
# deliberately kept available wherever they have a meaningful effect.
NOISE_SOURCE_SETTING_APPLICABILITY = {
    "white": frozenset(
        {
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "value": frozenset(
        {
            "frequency",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "perlin": frozenset(
        {
            "frequency",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "simplex": frozenset(
        {
            "frequency",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "fbm": frozenset(
        {
            "frequency",
            "octaves",
            "lacunarity",
            "gain",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "hybrid_fbm": frozenset(
        {
            "frequency",
            "octaves",
            "lacunarity",
            "gain",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "heterogeneous_fbm": frozenset(
        {
            "frequency",
            "octaves",
            "lacunarity",
            "gain",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "billow": frozenset(
        {
            "frequency",
            "octaves",
            "lacunarity",
            "gain",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "turbulence": frozenset(
        {
            "frequency",
            "octaves",
            "lacunarity",
            "gain",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "ridged": frozenset(
        {
            "frequency",
            "octaves",
            "lacunarity",
            "gain",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "ridged_multifractal": frozenset(
        {
            "frequency",
            "octaves",
            "lacunarity",
            "gain",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "worley": frozenset(
        {
            "frequency",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "worley_f1": frozenset(
        {
            "frequency",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "worley_f2": frozenset(
        {
            "frequency",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "worley_f2_minus_f1": frozenset(
        {
            "frequency",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "seed_offset",
        }
    ),
    "domain_warp": frozenset(
        {
            "frequency",
            "octaves",
            "lacunarity",
            "gain",
            "rotation_degrees",
            "stretch_percent",
            "bias_percent",
            "contrast_percent",
            "warp_strength_percent",
            "warp_frequency",
            "seed_offset",
        }
    ),
}
# These remapping controls are provider-independent. They are applied after
# each provider's own bias/contrast stage and therefore keep the same meaning
# for every autonomous noise family.
NOISE_SOURCE_SETTING_APPLICABILITY = {
    source: settings | _COMMON_OUTPUT_TRANSFORM_SETTINGS | _COORDINATE_TRANSFORM_SETTINGS
    for source, settings in NOISE_SOURCE_SETTING_APPLICABILITY.items()
}


def noise_source_setting_applies(source: str, setting: str) -> bool:
    """Return whether one visible setting is consumed by ``source``."""

    return str(setting) in NOISE_SOURCE_SETTING_APPLICABILITY.get(
        str(source), frozenset()
    )


def _hash2(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    """Return a stable uint32 hash for integer 2-D coordinates."""

    x = np.asarray(x, dtype=np.int64)
    y = np.asarray(y, dtype=np.int64)
    value = (
        x * np.int64(0x1F123BB5)
        + y * np.int64(0x5F356495)
        + np.int64(int(seed) & 0xFFFFFFFF) * np.int64(0x6C8E9CF5)
    ) & np.int64(0xFFFFFFFF)
    value ^= value >> np.int64(16)
    value = (value * np.int64(0x7FEB352D)) & np.int64(0xFFFFFFFF)
    value ^= value >> np.int64(15)
    value = (value * np.int64(0x846CA68B)) & np.int64(0xFFFFFFFF)
    value ^= value >> np.int64(16)
    return value.astype(np.uint32)


def _hash_unit(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    return _hash2(x, y, seed).astype(np.float64).astype(np.float32) / np.float32(
        4294967295.0
    )


def _fade(value: np.ndarray) -> np.ndarray:
    return value * value * value * (value * (value * 6.0 - 15.0) + 10.0)


def _lerp(a: np.ndarray, b: np.ndarray, amount: np.ndarray) -> np.ndarray:
    return a + (b - a) * amount


def _value_noise(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    tx = _fade((x - x0).astype(np.float32))
    ty = _fade((y - y0).astype(np.float32))
    v00 = _hash_unit(x0, y0, seed)
    v10 = _hash_unit(x0 + 1, y0, seed)
    v01 = _hash_unit(x0, y0 + 1, seed)
    v11 = _hash_unit(x0 + 1, y0 + 1, seed)
    return (_lerp(_lerp(v00, v10, tx), _lerp(v01, v11, tx), ty) * 2.0 - 1.0)


def _gradient_noise(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    x0 = np.floor(x).astype(np.int64)
    y0 = np.floor(y).astype(np.int64)
    tx = (x - x0).astype(np.float32)
    ty = (y - y0).astype(np.float32)
    u = _fade(tx)
    v = _fade(ty)

    def dot(ix: np.ndarray, iy: np.ndarray, dx, dy) -> np.ndarray:
        angle = _hash_unit(ix, iy, seed) * np.float32(2.0 * np.pi)
        return np.cos(angle) * dx + np.sin(angle) * dy

    n00 = dot(x0, y0, tx, ty)
    n10 = dot(x0 + 1, y0, tx - 1.0, ty)
    n01 = dot(x0, y0 + 1, tx, ty - 1.0)
    n11 = dot(x0 + 1, y0 + 1, tx - 1.0, ty - 1.0)
    return np.clip(_lerp(_lerp(n00, n10, u), _lerp(n01, n11, u), v) * 1.5, -1.0, 1.0)


_SIMPLEX_GRADIENTS = np.asarray(
    (
        (1.0, 1.0),
        (-1.0, 1.0),
        (1.0, -1.0),
        (-1.0, -1.0),
        (1.0, 0.0),
        (-1.0, 0.0),
        (0.0, 1.0),
        (0.0, -1.0),
    ),
    dtype=np.float32,
)


def _simplex_noise(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    """Vectorized 2-D simplex noise with deterministic coordinate hashing."""

    f2 = np.float32(0.3660254037844386)
    g2 = np.float32(0.21132486540518713)
    skew = (x + y) * f2
    i = np.floor(x + skew).astype(np.int64)
    j = np.floor(y + skew).astype(np.int64)
    unskew = (i + j).astype(np.float32) * g2
    x0 = x - (i.astype(np.float32) - unskew)
    y0 = y - (j.astype(np.float32) - unskew)
    i1 = (x0 > y0).astype(np.int64)
    j1 = 1 - i1
    x1 = x0 - i1.astype(np.float32) + g2
    y1 = y0 - j1.astype(np.float32) + g2
    x2 = x0 - 1.0 + 2.0 * g2
    y2 = y0 - 1.0 + 2.0 * g2

    def corner(ix, iy, dx, dy):
        attenuation = 0.5 - dx * dx - dy * dy
        gradient = _SIMPLEX_GRADIENTS[(_hash2(ix, iy, seed) & 7).astype(np.intp)]
        dot = gradient[..., 0] * dx + gradient[..., 1] * dy
        return np.where(attenuation > 0.0, attenuation**4 * dot, 0.0)

    result = (
        corner(i, j, x0, y0)
        + corner(i + i1, j + j1, x1, y1)
        + corner(i + 1, j + 1, x2, y2)
    )
    return np.clip(result * 70.0, -1.0, 1.0).astype(np.float32)


def _worley_noise(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    cell_x = np.floor(x).astype(np.int64)
    cell_y = np.floor(y).astype(np.int64)
    minimum = np.full(x.shape, np.inf, dtype=np.float32)
    for offset_y in (-1, 0, 1):
        for offset_x in (-1, 0, 1):
            neighbour_x = cell_x + offset_x
            neighbour_y = cell_y + offset_y
            point_x = neighbour_x.astype(np.float32) + _hash_unit(
                neighbour_x, neighbour_y, seed
            )
            point_y = neighbour_y.astype(np.float32) + _hash_unit(
                neighbour_x, neighbour_y, seed ^ 0xA511E9B3
            )
            distance = np.sqrt((x - point_x) ** 2 + (y - point_y) ** 2)
            minimum = np.minimum(minimum, distance)
    return np.clip(1.0 - minimum * 1.45, -1.0, 1.0) * 2.0 - 1.0


def _worley_distance_pair(
    x: np.ndarray,
    y: np.ndarray,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Return the first and second feature-point distances for one domain."""

    cell_x = np.floor(x).astype(np.int64)
    cell_y = np.floor(y).astype(np.int64)
    first = np.full(x.shape, np.inf, dtype=np.float32)
    second = np.full(x.shape, np.inf, dtype=np.float32)
    for offset_y in (-1, 0, 1):
        for offset_x in (-1, 0, 1):
            neighbour_x = cell_x + offset_x
            neighbour_y = cell_y + offset_y
            point_x = neighbour_x.astype(np.float32) + _hash_unit(
                neighbour_x, neighbour_y, seed
            )
            point_y = neighbour_y.astype(np.float32) + _hash_unit(
                neighbour_x, neighbour_y, seed ^ 0xA511E9B3
            )
            distance = np.sqrt((x - point_x) ** 2 + (y - point_y) ** 2)
            closer = distance < first
            second = np.where(closer, first, np.minimum(second, distance))
            first = np.minimum(first, distance)
    return first, second


def _worley_metric_noise(
    x: np.ndarray,
    y: np.ndarray,
    seed: int,
    metric: str,
) -> np.ndarray:
    """Return one normalized Worley distance metric in ``[-1, 1]``."""

    first, second = _worley_distance_pair(x, y, seed)
    if metric == "f1":
        normalized = np.clip(1.0 - first / np.float32(np.sqrt(2.0)), 0.0, 1.0)
    elif metric == "f2":
        normalized = np.clip(1.0 - second / np.float32(np.sqrt(2.0)), 0.0, 1.0)
    elif metric == "f2_minus_f1":
        normalized = np.clip((second - first) * 2.0, 0.0, 1.0)
    else:  # pragma: no cover - dispatch is kept closed by the provider list
        raise ValueError(f"Métrique Worley inconnue : {metric}")
    return (normalized * 2.0 - 1.0).astype(np.float32, copy=False)


def _fractal(
    algorithm,
    x: np.ndarray,
    y: np.ndarray,
    seed: int,
    frequency: float,
    octaves: int,
    lacunarity: float,
    gain: float,
    adaptive_domain: tuple[int, int] | None = None,
) -> np.ndarray:
    octave_weights = _adaptive_octave_fade_weights(
        adaptive_domain,
        frequency,
        octaves,
        lacunarity,
    )
    result = np.zeros(x.shape, dtype=np.float32)
    amplitude = 1.0
    amplitude_sum = 0.0
    current_frequency = float(frequency)
    for octave in range(max(1, int(octaves))):
        sample = algorithm(
            x * current_frequency,
            y * current_frequency,
            (int(seed) + octave * 0x9E3779B9) & 0xFFFFFFFF,
        )
        if octave_weights is None:
            result += sample * amplitude
        else:
            result += sample * (amplitude * octave_weights[octave])
        amplitude_sum += amplitude
        current_frequency *= float(lacunarity)
        amplitude *= float(gain)
    return result / max(amplitude_sum, 1e-6)


def _turbulence(
    algorithm,
    x: np.ndarray,
    y: np.ndarray,
    seed: int,
    frequency: float,
    octaves: int,
    lacunarity: float,
    gain: float,
    adaptive_domain: tuple[int, int] | None = None,
) -> np.ndarray:
    """Accumulate absolute gradient octaves before the final signed remap."""

    octave_weights = _adaptive_octave_fade_weights(
        adaptive_domain,
        frequency,
        octaves,
        lacunarity,
    )
    result = np.zeros(x.shape, dtype=np.float32)
    amplitude = 1.0
    amplitude_sum = 0.0
    current_frequency = float(frequency)
    for octave in range(max(1, int(octaves))):
        sample = np.clip(
            algorithm(
                x * current_frequency,
                y * current_frequency,
                (int(seed) + octave * 0x9E3779B9) & 0xFFFFFFFF,
            )
            * 2.0,
            -1.0,
            1.0,
        )
        absolute_sample = np.abs(sample)
        if octave_weights is None:
            result += absolute_sample * amplitude
        else:
            result += _fade_octave_sample(
                absolute_sample,
                octave_weights[octave],
            ) * amplitude
        amplitude_sum += amplitude
        current_frequency *= float(lacunarity)
        amplitude *= float(gain)
    normalized = result / max(amplitude_sum, 1e-6)
    return np.clip(normalized * 2.0 - 1.0, -1.0, 1.0).astype(
        np.float32,
        copy=False,
    )


def _hybrid_fractal(
    algorithm,
    x: np.ndarray,
    y: np.ndarray,
    seed: int,
    frequency: float,
    octaves: int,
    lacunarity: float,
    gain: float,
    adaptive_domain: tuple[int, int] | None = None,
) -> np.ndarray:
    """Return a signal-dependent hybrid multifractal field.

    Each octave contributes less in regions where the preceding octave is low.
    That keeps fine detail attached to broad land/relief structures instead of
    adding the same amount of roughness everywhere, while remaining an
    autonomous source with the same finite coordinate contract as fBm.
    """

    current_frequency = float(frequency)
    octave_count = max(1, int(octaves))
    octave_weights = _adaptive_octave_fade_weights(
        adaptive_domain,
        frequency,
        octave_count,
        lacunarity,
    )
    signal = np.clip(
        (
            np.clip(
                algorithm(
                    x * current_frequency,
                    y * current_frequency,
                    int(seed) & 0xFFFFFFFF,
                )
                * 2.0,
                -1.0,
                1.0,
            )
            + 1.0
        )
        * 0.5,
        0.0,
        1.0,
    )
    if octave_weights is not None:
        signal = _fade_octave_sample(signal, octave_weights[0])
    result = signal.copy()
    weight_sum = np.ones(x.shape, dtype=np.float32)
    weight = np.clip(signal * float(gain), 0.0, 1.0)
    current_frequency *= float(lacunarity)

    for octave in range(1, octave_count):
        signal = np.clip(
            (
                np.clip(
                    algorithm(
                        x * current_frequency,
                        y * current_frequency,
                        (int(seed) + octave * 0x9E3779B9) & 0xFFFFFFFF,
                    )
                    * 2.0,
                    -1.0,
                    1.0,
                )
                + 1.0
            )
            * 0.5,
            0.0,
            1.0,
        )
        if octave_weights is not None:
            signal = _fade_octave_sample(signal, octave_weights[octave])
        result += signal * weight
        weight_sum += weight
        weight = np.clip(signal * float(gain), 0.0, 1.0)
        current_frequency *= float(lacunarity)

    return np.clip(result / np.maximum(weight_sum, 1e-6) * 2.0 - 1.0, -1.0, 1.0).astype(
        np.float32,
        copy=False,
    )


def _heterogeneous_fractal(
    algorithm,
    x: np.ndarray,
    y: np.ndarray,
    seed: int,
    frequency: float,
    octaves: int,
    lacunarity: float,
    gain: float,
    adaptive_domain: tuple[int, int] | None = None,
) -> np.ndarray:
    """Return fBm whose detail amplitude follows the broad relief.

    Unlike ``hybrid_fbm``, which gates each new octave by the preceding
    signal, this variant keeps the broad signal in place and modulates the
    *contrast* of later detail with it.  Low areas therefore stay calmer while
    high areas accumulate more broken relief.  It is useful for testing a
    natural-looking mountain/plateau split without adding a second mask.
    """

    octave_count = max(1, int(octaves))
    current_frequency = float(frequency)
    octave_weights = _adaptive_octave_fade_weights(
        adaptive_domain,
        frequency,
        octave_count,
        lacunarity,
    )
    base = np.clip(
        algorithm(
            x * current_frequency,
            y * current_frequency,
            int(seed) & 0xFFFFFFFF,
        )
        * 2.0,
        -1.0,
        1.0,
    )
    if octave_weights is not None:
        base = _fade_octave_sample(base, octave_weights[0])
    result = (base + 1.0) * 0.5
    detail_amplitude = max(0.0, float(gain))
    current_frequency *= float(lacunarity)

    for octave in range(1, octave_count):
        detail = np.clip(
            algorithm(
                x * current_frequency,
                y * current_frequency,
                (int(seed) + octave * 0x9E3779B9) & 0xFFFFFFFF,
            )
            * 2.0,
            -1.0,
            1.0,
        )
        if octave_weights is not None:
            detail = _fade_octave_sample(detail, octave_weights[octave])
        detail = (detail + 1.0) * 0.5
        modulation = detail_amplitude * (0.25 + 0.75 * result)
        result = np.clip(result + (detail - 0.5) * modulation, 0.0, 1.0)
        current_frequency *= float(lacunarity)
        detail_amplitude *= float(gain)

    return np.clip(result * 2.0 - 1.0, -1.0, 1.0).astype(
        np.float32,
        copy=False,
    )


def _ridged_multifractal(
    algorithm,
    x: np.ndarray,
    y: np.ndarray,
    seed: int,
    frequency: float,
    octaves: int,
    lacunarity: float,
    gain: float,
    adaptive_domain: tuple[int, int] | None = None,
) -> np.ndarray:
    """Return a ridge field whose fine ridges follow broader ridges.

    The existing ``ridged`` provider applies one ridge transform after a
    conventional fBm sum.  This provider performs the ridge transform per
    octave and uses the previous ridge as a weight, producing narrower,
    connected crest lines and leaving valleys comparatively quiet.
    """

    def ridge_sample(current_frequency: float, octave: int) -> np.ndarray:
        sample = np.clip(
            algorithm(
                x * current_frequency,
                y * current_frequency,
                (int(seed) + octave * 0x9E3779B9) & 0xFFFFFFFF,
            )
            * 2.0,
            -1.0,
            1.0,
        )
        ridge = 1.0 - np.abs(sample)
        return np.clip(ridge * ridge, 0.0, 1.0)

    octave_count = max(1, int(octaves))
    octave_weights = _adaptive_octave_fade_weights(
        adaptive_domain,
        frequency,
        octave_count,
        lacunarity,
    )
    current_frequency = float(frequency)
    signal = ridge_sample(current_frequency, 0)
    if octave_weights is not None:
        signal = _fade_octave_sample(signal, octave_weights[0])
    result = signal.copy()
    amplitude = max(0.0, float(gain))
    amplitude_sum = 1.0
    weight = np.clip(signal * 2.0, 0.0, 1.0)
    current_frequency *= float(lacunarity)

    for octave in range(1, octave_count):
        signal = ridge_sample(current_frequency, octave)
        if octave_weights is not None:
            signal = _fade_octave_sample(signal, octave_weights[octave])
        weighted = signal * weight
        result += weighted * amplitude
        amplitude_sum += amplitude
        weight = np.clip(weighted * 2.0, 0.0, 1.0)
        current_frequency *= float(lacunarity)
        amplitude *= float(gain)

    return np.clip(result / max(amplitude_sum, 1e-6) * 2.0 - 1.0, -1.0, 1.0).astype(
        np.float32,
        copy=False,
    )


def _adaptive_octave_fade_weights(
    adaptive_domain: tuple[int, int] | None,
    frequency: float,
    octaves: int,
    lacunarity: float,
) -> tuple[float, ...] | None:
    """Fade fine octave variation smoothly as the real map domain shrinks.

    The minimum useful wavelength grows continuously below the reference map.
    Each octave between one and two times that wavelength fades with smoothstep;
    coarser octaves keep their full weight.  Weights affect the octave signal,
    while the original amplitude sum remains fixed so the remaining broad
    octaves are not renormalized upward.
    """

    if adaptive_domain is None:
        return None
    target_side = max(1, int(adaptive_domain[0]))
    reference_side = max(1, int(adaptive_domain[1]))
    if target_side >= reference_side:
        return None

    octave_count = max(1, int(octaves))
    ratio = float(target_side) / float(reference_side)
    minimum_period = NOISE_FREQUENCY_MIN_CELLS_PER_PERIOD / ratio
    base_frequency = max(1e-6, abs(float(frequency)))
    octave_lacunarity = max(1.0, float(lacunarity))
    current_frequency = base_frequency
    weights: list[float] = []
    for _octave in range(octave_count):
        period = float(target_side) / current_frequency
        blend = float(
            np.clip(
                period / minimum_period - 1.0,
                0.0,
                NOISE_FREQUENCY_FADE_FULL_WEIGHT_PERIOD_MULTIPLIER - 1.0,
            )
            / max(
                NOISE_FREQUENCY_FADE_FULL_WEIGHT_PERIOD_MULTIPLIER - 1.0,
                1e-6,
            )
        )
        weight = blend * blend * (3.0 - 2.0 * blend)
        weights.append(float(weight))
        current_frequency *= octave_lacunarity

    if all(weight >= 1.0 for weight in weights):
        return None
    return tuple(weights)


def _fade_octave_sample(sample: np.ndarray, weight: float) -> np.ndarray:
    """Reduce one octave's spatial contrast while preserving its mean."""

    weight = float(np.clip(weight, 0.0, 1.0))
    if weight >= 1.0:
        return sample
    center = float(np.mean(sample, dtype=np.float64))
    return center + (sample - center) * weight


def _coordinate_grid(side: int, rotation_degrees: float, stretch_percent: float):
    coordinates = np.linspace(-0.5, 0.5, int(side), dtype=np.float32)
    x = np.broadcast_to(coordinates[None, :], (int(side), int(side)))
    y = np.broadcast_to(coordinates[:, None], (int(side), int(side)))
    angle = np.deg2rad(float(rotation_degrees))
    cosine = np.float32(np.cos(angle))
    sine = np.float32(np.sin(angle))
    rotated_x = x * cosine - y * sine
    rotated_y = x * sine + y * cosine
    stretch = max(0.05, float(stretch_percent) / 100.0)
    return rotated_x * stretch, rotated_y / stretch


def _apply_coordinate_transforms(
    x: np.ndarray,
    y: np.ndarray,
    settings: Mapping[str, object],
) -> tuple[np.ndarray, np.ndarray]:
    """Apply provider-independent spatial transforms in normalized space.

    The default values are an exact identity.  Scaling changes the sampled
    feature size, offsets move the sampling window, repeat tiles it inside
    the provider's finite domain, and symmetry folds one axis around its
    centre.  The outer finite-domain frame is applied by the caller after
    this provider field is generated, so these transforms cannot create an
    infinite map or bypass the edge falloff.
    """

    offset_x = float(settings.get("offset_x_percent", 0.0)) / 100.0
    offset_y = float(settings.get("offset_y_percent", 0.0)) / 100.0
    scale_x = max(0.01, float(settings.get("scale_x_percent", 100.0)) / 100.0)
    scale_y = max(0.01, float(settings.get("scale_y_percent", 100.0)) / 100.0)
    x = np.asarray(x, dtype=np.float32) / np.float32(scale_x) + np.float32(offset_x)
    y = np.asarray(y, dtype=np.float32) / np.float32(scale_y) + np.float32(offset_y)

    symmetry_x = np.clip(
        float(settings.get("symmetry_x_percent", 0.0)) / 100.0,
        0.0,
        1.0,
    )
    symmetry_y = np.clip(
        float(settings.get("symmetry_y_percent", 0.0)) / 100.0,
        0.0,
        1.0,
    )
    if symmetry_x > 0.0:
        x = x * np.float32(1.0 - symmetry_x) + np.abs(x) * np.float32(symmetry_x)
    if symmetry_y > 0.0:
        y = y * np.float32(1.0 - symmetry_y) + np.abs(y) * np.float32(symmetry_y)

    repeat_x = max(1, int(round(float(settings.get("repeat_x", 1)))))
    repeat_y = max(1, int(round(float(settings.get("repeat_y", 1)))))
    if repeat_x > 1:
        x = np.mod((x + 0.5) * float(repeat_x) + 0.5, 1.0) - 0.5
    if repeat_y > 1:
        y = np.mod((y + 0.5) * float(repeat_y) + 0.5, 1.0) - 0.5
    return x.astype(np.float32, copy=False), y.astype(np.float32, copy=False)


def _apply_common_output_transforms(
    field: np.ndarray,
    settings: Mapping[str, object],
) -> np.ndarray:
    """Apply shared, provider-independent shaping to a signed field.

    The advanced controls operate on a normalized ``0..1`` copy of the
    provider field.  Their identity values are deliberately cheap and return
    the old clipped signed field unchanged.  This keeps the default path
    byte-stable while making the non-identity path useful for deliberately
    asymmetric coast/plateau distributions:

    * black/white points remap an input window to the full range;
    * low/high thresholds create hard or softened plateaus;
    * clamp floor/ceiling bound the final response;
    * curve bias bends the lower and upper halves in opposite directions.
    """

    inversion = np.clip(
        float(settings.get("inversion_percent", 0.0)) / 100.0,
        0.0,
        1.0,
    )
    absolute = np.clip(
        float(settings.get("absolute_percent", 0.0)) / 100.0,
        0.0,
        1.0,
    )
    gamma_percent = float(settings.get("gamma_percent", 100.0))
    terrace_steps = int(round(float(settings.get("terrace_steps", 0))))
    terrace_blend = np.clip(
        float(settings.get("terrace_blend_percent", 100.0)) / 100.0,
        0.0,
        1.0,
    )
    remap_low = np.clip(
        float(settings.get("remap_low_percent", 0.0)) / 100.0,
        0.0,
        1.0,
    )
    remap_high = np.clip(
        float(settings.get("remap_high_percent", 100.0)) / 100.0,
        0.0,
        1.0,
    )
    threshold_low = np.clip(
        float(settings.get("threshold_low_percent", 0.0)) / 100.0,
        0.0,
        1.0,
    )
    threshold_high = np.clip(
        float(settings.get("threshold_high_percent", 100.0)) / 100.0,
        0.0,
        1.0,
    )
    threshold_softness = np.clip(
        float(settings.get("threshold_softness_percent", 0.0)) / 100.0,
        0.0,
        1.0,
    )
    clamp_low = np.clip(
        float(settings.get("clamp_low_percent", 0.0)) / 100.0,
        0.0,
        1.0,
    )
    clamp_high = np.clip(
        float(settings.get("clamp_high_percent", 100.0)) / 100.0,
        0.0,
        1.0,
    )
    curve_bias = np.clip(
        float(settings.get("curve_bias_percent", 0.0)) / 100.0,
        -1.0,
        1.0,
    )
    advanced_identity = (
        remap_low <= 0.0
        and remap_high >= 1.0
        and threshold_low <= 0.0
        and threshold_high >= 1.0
        and threshold_softness <= 0.0
        and clamp_low <= 0.0
        and clamp_high >= 1.0
        and abs(curve_bias) <= 1e-6
    )
    values = np.asarray(field, dtype=np.float32)
    if (
        inversion <= 0.0
        and absolute <= 0.0
        and abs(gamma_percent - 100.0) <= 1e-6
        and terrace_steps < 2
        and advanced_identity
    ):
        return np.clip(values, -1.0, 1.0).astype(np.float32, copy=False)

    values = values * (1.0 - inversion) - values * inversion
    values = values * (1.0 - absolute) + np.abs(values) * absolute
    exponent = max(0.05, gamma_percent / 100.0)
    values = np.sign(values) * np.power(np.abs(values), exponent)

    if terrace_steps >= 2 and terrace_blend > 0.0:
        normalized = np.clip((values + 1.0) * 0.5, 0.0, 1.0)
        stepped = np.round(normalized * float(terrace_steps - 1)) / float(
            terrace_steps - 1
        )
        normalized = normalized * (1.0 - terrace_blend) + stepped * terrace_blend
        values = normalized * 2.0 - 1.0

    # Preserve the exact R36 path whenever only the previously shipped
    # controls are active.  The advanced stage is then truly opt-in.
    if advanced_identity:
        return np.clip(values, -1.0, 1.0).astype(np.float32, copy=False)

    normalized = np.clip((values + 1.0) * 0.5, 0.0, 1.0)

    # Avoid a discontinuous divide-by-zero when a user intentionally crosses
    # the two points.  The resulting one-cell-wide interval behaves as a
    # steep remap instead of crashing or producing NaNs.
    remap_span = max(1e-6, float(remap_high - remap_low))
    normalized = np.clip((normalized - remap_low) / remap_span, 0.0, 1.0)

    if abs(curve_bias) > 1e-6:
        lower_exponent = max(0.1, 1.0 + float(curve_bias) * 1.5)
        upper_exponent = max(0.1, 1.0 - float(curve_bias) * 1.5)
        lower_half = 0.5 * np.power(np.clip(normalized * 2.0, 0.0, 1.0), lower_exponent)
        upper_half = 1.0 - 0.5 * np.power(
            np.clip((1.0 - normalized) * 2.0, 0.0, 1.0),
            upper_exponent,
        )
        normalized = np.where(normalized < 0.5, lower_half, upper_half)

    threshold_high = max(threshold_low, threshold_high)
    if threshold_low > 0.0:
        if threshold_softness <= 0.0:
            normalized = np.where(normalized < threshold_low, 0.0, normalized)
        else:
            width = min(0.25, max(0.01, threshold_low * 0.5)) * float(
                threshold_softness
            )
            start = max(0.0, threshold_low - width)
            stop = min(1.0, threshold_low + width)
            amount = np.clip((normalized - start) / max(1e-6, stop - start), 0.0, 1.0)
            amount = amount * amount * (3.0 - 2.0 * amount)
            normalized *= amount
    if threshold_high < 1.0:
        if threshold_softness <= 0.0:
            normalized = np.where(normalized > threshold_high, 1.0, normalized)
        else:
            width = min(0.25, max(0.01, (1.0 - threshold_high) * 0.5)) * float(
                threshold_softness
            )
            start = max(0.0, threshold_high - width)
            stop = min(1.0, threshold_high + width)
            amount = np.clip((normalized - start) / max(1e-6, stop - start), 0.0, 1.0)
            amount = amount * amount * (3.0 - 2.0 * amount)
            normalized = normalized + (1.0 - normalized) * amount

    clamp_high = max(clamp_low, clamp_high)
    normalized = np.clip(normalized, clamp_low, clamp_high)
    values = normalized * 2.0 - 1.0
    return np.clip(values, -1.0, 1.0).astype(np.float32, copy=False)


def generate_noise_source(
    source: str,
    side: int,
    seed: int,
    settings: Mapping[str, object],
    *,
    adaptive_domain: tuple[int, int] | None = None,
) -> np.ndarray:
    """Generate one source field in ``[-1, 1]`` at the requested resolution.

    ``adaptive_domain`` carries the real map domain and the 768-cell reference
    domain.  It is intentionally separate from ``side`` because previews may
    render a small thumbnail for a much larger (or smaller) target map.
    """

    source = str(source)
    if source not in NOISE_SOURCE_OPTIONS:
        raise ValueError(f"Source de bruit non implémentée : {source}")
    x, y = _coordinate_grid(
        int(side),
        float(settings.get("rotation_degrees", 0.0)),
        float(settings.get("stretch_percent", 100.0)),
    )
    x, y = _apply_coordinate_transforms(x, y, settings)
    frequency = float(settings.get("frequency", 4.0))
    octaves = int(settings.get("octaves", 5))
    lacunarity = float(settings.get("lacunarity", 2.0))
    gain = float(settings.get("gain", 0.5))
    source_seed = (int(seed) + int(settings.get("seed_offset", 0))) & 0xFFFFFFFF

    if source == "white":
        columns = np.rint((x + 0.5) * float(int(side) - 1)).astype(np.int64)
        rows = np.rint((y + 0.5) * float(int(side) - 1)).astype(np.int64)
        field = _hash_unit(columns, rows, source_seed) * 2.0 - 1.0
    elif source == "value":
        field = _value_noise(x * frequency, y * frequency, source_seed)
    elif source == "perlin":
        field = _gradient_noise(x * frequency, y * frequency, source_seed)
    elif source == "simplex":
        field = _simplex_noise(x * frequency, y * frequency, source_seed)
    elif source in {"fbm", "billow", "ridged"}:
        field = _fractal(
            _gradient_noise,
            x,
            y,
            source_seed,
            frequency,
            octaves,
            lacunarity,
            gain,
            adaptive_domain,
        )
        # Gradient octaves have a deliberately conservative theoretical
        # amplitude.  Expand the useful range before the user-controlled bias
        # and contrast so fBm/Billow/Ridged are visibly different at defaults.
        field = np.clip(field * 2.0, -1.0, 1.0)
        if source == "billow":
            field = np.abs(field) * 2.0 - 1.0
        elif source == "ridged":
            ridge = 1.0 - np.abs(field)
            field = ridge * ridge * 2.0 - 1.0
    elif source == "hybrid_fbm":
        field = _hybrid_fractal(
            _gradient_noise,
            x,
            y,
            source_seed,
            frequency,
            octaves,
            lacunarity,
            gain,
            adaptive_domain,
        )
    elif source == "heterogeneous_fbm":
        field = _heterogeneous_fractal(
            _gradient_noise,
            x,
            y,
            source_seed,
            frequency,
            octaves,
            lacunarity,
            gain,
            adaptive_domain,
        )
    elif source == "turbulence":
        field = _turbulence(
            _gradient_noise,
            x,
            y,
            source_seed,
            frequency,
            octaves,
            lacunarity,
            gain,
            adaptive_domain,
        )
    elif source == "ridged_multifractal":
        field = _ridged_multifractal(
            _gradient_noise,
            x,
            y,
            source_seed,
            frequency,
            octaves,
            lacunarity,
            gain,
            adaptive_domain,
        )
    elif source == "worley":
        field = _worley_noise(x * frequency, y * frequency, source_seed)
    elif source in {"worley_f1", "worley_f2", "worley_f2_minus_f1"}:
        metric = {
            "worley_f1": "f1",
            "worley_f2": "f2",
            "worley_f2_minus_f1": "f2_minus_f1",
        }[source]
        field = _worley_metric_noise(
            x * frequency,
            y * frequency,
            source_seed,
            metric,
        )
    else:  # domain_warp
        warp_frequency = float(settings.get("warp_frequency", 2.0))
        warp_strength = float(settings.get("warp_strength_percent", 80.0)) / 100.0
        warp_x = _fractal(
            _simplex_noise,
            x,
            y,
            source_seed ^ 0xC2B2AE35,
            warp_frequency,
            min(4, octaves),
            lacunarity,
            gain,
            adaptive_domain,
        )
        warp_y = _fractal(
            _simplex_noise,
            x,
            y,
            source_seed ^ 0x85EBCA6B,
            warp_frequency,
            min(4, octaves),
            lacunarity,
            gain,
            adaptive_domain,
        )
        field = _fractal(
            _gradient_noise,
            x + warp_x * warp_strength * 0.18,
            y + warp_y * warp_strength * 0.18,
            source_seed,
            frequency,
            octaves,
            lacunarity,
            gain,
            adaptive_domain,
        )
        field = np.clip(field * 2.0, -1.0, 1.0)

    bias = float(settings.get("bias_percent", 0.0)) / 100.0
    contrast = float(settings.get("contrast_percent", 100.0)) / 100.0
    field = np.clip((field + bias) * contrast, -1.0, 1.0).astype(np.float32)
    return _apply_common_output_transforms(field, settings)


def adapt_noise_settings_for_domain_size(
    source: str,
    settings: Mapping[str, object],
    domain_side: int,
    *,
    reference_domain_side: int = NOISE_FREQUENCY_REFERENCE_SIDE,
) -> dict[str, object]:
    """Derive size-aware frequency values without mutating saved settings.

    Frequencies are authored for the 768-cell reference domain.  A gentle
    power curve lowers them on smaller domains and raises them on larger ones,
    keeping terrain features from shrinking with the map without abruptly
    changing the profile.  Octave bands above four cells per period are
    removed and the remaining base frequencies are capped to the sample grid.
    """

    result = dict(settings)
    source = str(source)
    applicable = NOISE_SOURCE_SETTING_APPLICABILITY.get(source, frozenset())
    if "frequency" not in applicable:
        return result

    target_side = max(1, int(domain_side))
    reference_side = max(1, int(reference_domain_side))
    multiplier = (float(target_side) / float(reference_side)) ** (
        NOISE_FREQUENCY_SIZE_EXPONENT
    )
    frequency = float(settings.get("frequency", 4.0)) * multiplier
    if target_side < reference_side:
        maximum_frequency = max(
            1.0,
            float(target_side) / NOISE_FREQUENCY_MIN_CELLS_PER_PERIOD,
        )
        has_octaves = "octaves" in applicable
        octaves = max(1, int(settings.get("octaves", 1)))
        lacunarity = max(1.0, float(settings.get("lacunarity", 2.0)))
        warp_frequency = None
        if source == "domain_warp" and "warp_frequency" in applicable:
            warp_frequency = float(settings.get("warp_frequency", 2.0)) * multiplier

        def highest_frequency(octave_count: int) -> float:
            highest = frequency * lacunarity ** (octave_count - 1)
            if warp_frequency is not None:
                warp_octaves = min(4, octave_count)
                highest = max(
                    highest,
                    warp_frequency * lacunarity ** (warp_octaves - 1),
                )
            return highest

        if has_octaves:
            while octaves > 1 and highest_frequency(octaves) > maximum_frequency:
                octaves -= 1
            result["octaves"] = octaves
        frequency = min(frequency, maximum_frequency)
        result["frequency"] = frequency
        if warp_frequency is not None:
            result["warp_frequency"] = min(warp_frequency, maximum_frequency)
    else:
        result["frequency"] = frequency
        if source == "domain_warp" and "warp_frequency" in applicable:
            result["warp_frequency"] = (
                float(settings.get("warp_frequency", 2.0)) * multiplier
            )
    return result


__all__ = (
    "NOISE_SOURCE_OPTIONS",
    "NOISE_SOURCE_SETTING_APPLICABILITY",
    "NOISE_FREQUENCY_REFERENCE_SIDE",
    "NOISE_FREQUENCY_SIZE_EXPONENT",
    "NOISE_FREQUENCY_MIN_CELLS_PER_PERIOD",
    "adapt_noise_settings_for_domain_size",
    "generate_noise_source",
    "noise_source_setting_applies",
)
