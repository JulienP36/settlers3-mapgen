"""Deterministic complete noise sources and noisemap composition.

The Legacy raw relief field remains the reference and the default profile is
byte-for-byte unchanged.  R29 generates each provider directly in a finite
inner rectangle, then combines autonomous fields before native normalization,
sculpture, relaxation and classification.
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass

import numpy as np

from .noise_sources import (
    NOISE_FREQUENCY_REFERENCE_SIDE,
    adapt_noise_settings_for_domain_size,
    generate_noise_source,
)
from .profiles import (
    FINITE_DOMAIN_MODE_NATIVE_CALIBRATED,
    MASK_LAYER_MANUAL_GRID_SIDE,
    NATIVE_NOISE_MAXIMUM,
    NATIVE_NOISE_MINIMUM,
    RELIEF_SOURCE_CUSTOM_LEGACY,
    SHAPE_TEMPLATE_DEFAULTS,
    finite_domain_parameters,
    mask_layer_parameters,
    morphology_parameters,
    noise_layer_parameters,
    normalize_archetype_profile,
    relief_source_parameter,
    relief_source_mask,
    relief_source_settings,
    shape_template,
    has_active_mask_layers,
)


NATIVE_RAW_WATER_FLOOR = 0x1F
NOISE_LAYER_RAW_AMPLITUDE = 48.0
NATIVE_RELIEF_SOURCE = "native_legacy"
RELIEF_SOURCE_FRACTAL = "fractal_fbm"
RELIEF_SOURCE_WARPED = "warped_fbm"
RELIEF_SOURCE_RIDGED = "ridged_fbm"
RELIEF_SOURCE_FRAME_REFERENCE_CELLS = 40
RELIEF_SOURCE_FRAME_MINIMUM_MARGIN = 8
_COMPONENT_CACHE_LIMIT = 48


def _component_cache_key(value):
    """Freeze a normalized thumbnail payload, including manual mask pixels."""

    if isinstance(value, Mapping):
        return tuple(sorted((str(key), _component_cache_key(item)) for key, item in value.items()))
    if isinstance(value, (tuple, list)):
        return tuple(_component_cache_key(item) for item in value)
    return value


def _component_cache_get(cache: MutableMapping | None, key):
    if cache is None or key not in cache:
        return None
    if isinstance(cache, OrderedDict):
        cache.move_to_end(key)
    return cache[key].copy()


def _component_cache_put(cache: MutableMapping | None, key, value: np.ndarray) -> None:
    if cache is None:
        return
    cache[key] = value.copy()
    if isinstance(cache, OrderedDict):
        cache.move_to_end(key)
        while len(cache) > _COMPONENT_CACHE_LIMIT:
            cache.popitem(last=False)
    else:
        while len(cache) > _COMPONENT_CACHE_LIMIT:
            del cache[next(iter(cache))]


@dataclass(frozen=True, slots=True)
class NoiseLayerDiagnostic:
    """Inspectable result for one semantic noise layer."""

    index: int
    source: str
    role: str
    mask: str
    operation: str
    stage: str
    order: int
    enabled: bool
    domain_mask: np.ndarray
    component: np.ndarray
    delta: np.ndarray
    affected_cell_count: int
    affected_percent: float
    delta_minimum: float
    delta_maximum: float
    delta_mean: float
    positive_cell_count: int
    negative_cell_count: int


@dataclass(frozen=True, slots=True)
class NoiseLabReport:
    """Raw-field laboratory output shared by previews and tests.

    ``raw_height`` is the Legacy reference field. ``source_height`` is the
    selected complete source field before fusion sources. The composed field
    remains pre-normalization, pre-sculpture and pre-relaxation.
    """

    raw_height: np.ndarray
    source_height: np.ndarray
    composed_height: np.ndarray
    land_mask: np.ndarray
    total_delta: np.ndarray
    layer_delta: np.ndarray
    layers: tuple[NoiseLayerDiagnostic, ...]
    source_delta: np.ndarray | None = None
    reference_land_mask: np.ndarray | None = None
    source_name: str = NATIVE_RELIEF_SOURCE

    @property
    def active_layers(self) -> tuple[NoiseLayerDiagnostic, ...]:
        return tuple(layer for layer in self.layers if layer.enabled)

    @property
    def source_active(self) -> bool:
        return self.source_height is not self.raw_height and bool(
            np.any(self.source_height != self.raw_height)
        )

    @property
    def active_components(self) -> bool:
        return self.source_active or bool(self.active_layers)

    @property
    def source_land_percent(self) -> float:
        """Return the selected raw source's terrestrial share."""

        if not self.source_height.size:
            return 0.0
        return 100.0 * float(np.count_nonzero(self.land_mask)) / float(
            self.source_height.size
        )

    @property
    def source_height_percentiles(self) -> tuple[float, float, float]:
        """Return P10/P50/P90 of non-water raw source elevations."""

        values = self.source_height[self.land_mask]
        if values.size == 0:
            values = self.source_height.reshape(-1)
        if values.size == 0:
            return (0.0, 0.0, 0.0)
        percentiles = np.percentile(values.astype(np.float32), (10.0, 50.0, 90.0))
        return tuple(float(value) for value in percentiles)


def _validate_square_field(field: np.ndarray, label: str) -> np.ndarray:
    values = np.asarray(field)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError(f"{label} doit être une matrice carrée")
    return values


def _resample_centered(field: np.ndarray, scale_percent: int) -> np.ndarray:
    """Resample a field around its centre to change the spatial form scale.

    Values above 100 make structures broader by sampling a smaller central
    portion of the native field.  Values below 100 expose a wider portion and
    therefore produce smaller/more numerous structures.  Bilinear sampling is
    used for the scalar relief field; the native classification still happens
    afterwards on integer heights.
    """

    values = _validate_square_field(field, "Le champ de morphologie")
    scale_percent = int(scale_percent)
    if scale_percent == 100:
        return values.copy()

    side = int(values.shape[0])
    coordinates = np.arange(side, dtype=np.float32)
    center = (float(side) - 1.0) / 2.0
    source = center + (coordinates - center) * (100.0 / float(scale_percent))
    source = np.clip(source, 0.0, float(side - 1))
    lower = np.floor(source).astype(np.intp)
    upper = np.minimum(lower + 1, side - 1)
    fraction = source - lower

    top_left = values[np.ix_(lower, lower)].astype(np.float32, copy=False)
    top_right = values[np.ix_(lower, upper)].astype(np.float32, copy=False)
    bottom_left = values[np.ix_(upper, lower)].astype(np.float32, copy=False)
    bottom_right = values[np.ix_(upper, upper)].astype(np.float32, copy=False)
    row_fraction = fraction[:, None]
    column_fraction = fraction[None, :]
    result = (
        top_left * (1.0 - row_fraction) * (1.0 - column_fraction)
        + top_right * (1.0 - row_fraction) * column_fraction
        + bottom_left * row_fraction * (1.0 - column_fraction)
        + bottom_right * row_fraction * column_fraction
    )
    return result


def _apply_contrast(
    height: np.ndarray,
    signed_noise: np.ndarray | None,
    contrast_percent: int,
) -> tuple[np.ndarray, np.ndarray | None]:
    if int(contrast_percent) == 100:
        height_result = np.rint(np.clip(height, 0.0, 255.0)).astype(np.uint8)
        noise_result = (
            None
            if signed_noise is None
            else np.rint(signed_noise).astype(np.int16)
        )
        return height_result, noise_result

    height_values = np.asarray(height, dtype=np.float32)
    height_result = 128.0 + (height_values - 128.0) * (float(contrast_percent) / 100.0)
    # Water is represented by a hard zero in the game heightmap.  Preserve
    # that floor while changing the amplitude of land relief.
    height_result = np.where(height_values <= 0.0, 0.0, height_result)
    height_result = np.rint(np.clip(height_result, 0.0, 255.0)).astype(np.uint8)

    if signed_noise is None:
        return height_result, None
    noise_values = np.asarray(signed_noise, dtype=np.float32)
    noise_center = (float(NATIVE_NOISE_MINIMUM) + float(NATIVE_NOISE_MAXIMUM)) / 2.0
    noise_result = noise_center + (noise_values - noise_center) * (
        float(contrast_percent) / 100.0
    )
    return height_result, np.rint(noise_result).astype(np.int16)


def _interpolated_lattice(
    side: int,
    seed: int,
    cell_size: int,
    *,
    boundary_value: float | None = None,
) -> np.ndarray:
    """Build one smooth deterministic value-noise octave.

    ``boundary_value`` is a generation constraint, not a post-process: when
    supplied, the lattice itself owns the value of its four outer sides.
    """

    cell_size = max(4, int(cell_size))
    lattice_side = max(2, (int(side) - 1) // cell_size + 2)
    lattice = np.random.default_rng(int(seed) & 0xFFFFFFFF).random(
        (lattice_side, lattice_side),
    ).astype(np.float32)
    if boundary_value is not None:
        boundary_value = float(boundary_value)
        lattice[0, :] = boundary_value
        lattice[-1, :] = boundary_value
        lattice[:, 0] = boundary_value
        lattice[:, -1] = boundary_value
    if boundary_value is None:
        coordinates = np.arange(int(side), dtype=np.float32) / float(cell_size)
    else:
        # A finite provider must reach both boundary lattice sides.  The
        # ordinary pixel/cell-size coordinates stop short of the terminal
        # lattice point for many octave sizes and make the opposite edge
        # asymmetric.
        coordinates = np.linspace(
            0.0,
            float(lattice_side - 1),
            int(side),
            dtype=np.float32,
        )
    lower = np.floor(coordinates).astype(np.intp)
    upper = np.minimum(lower + 1, lattice_side - 1)
    fraction = coordinates - lower
    # Smoothstep removes the visible linear interpolation bands without
    # changing the deterministic grid topology.
    fraction = fraction * fraction * (3.0 - 2.0 * fraction)
    top_left = lattice[np.ix_(lower, lower)]
    top_right = lattice[np.ix_(lower, upper)]
    bottom_left = lattice[np.ix_(upper, lower)]
    bottom_right = lattice[np.ix_(upper, upper)]
    row_fraction = fraction[:, None]
    column_fraction = fraction[None, :]
    result = (
        top_left * (1.0 - row_fraction) * (1.0 - column_fraction)
        + top_right * (1.0 - row_fraction) * column_fraction
        + bottom_left * row_fraction * (1.0 - column_fraction)
        + bottom_right * row_fraction * column_fraction
    )
    if boundary_value is not None:
        # The last sample coordinate usually stops just before the last
        # lattice point.  Pin all four sampled sides explicitly so the finite
        # domain owns its complete frame, including the bottom and right edges.
        sampled_boundary = float(boundary_value)
        result[0, :] = sampled_boundary
        result[-1, :] = sampled_boundary
        result[:, 0] = sampled_boundary
        result[:, -1] = sampled_boundary
    return result * 2.0 - 1.0


def _smooth_noise_field(side: int, seed: int, layer_index: int, scale_percent: int) -> np.ndarray:
    """Build a deterministic multi-scale value-noise field in ``[-1, 1]``."""

    base_cell_size = max(8, round(96.0 * 100.0 / float(scale_percent)))
    octaves = (
        (base_cell_size, 1.0),
        (max(4, base_cell_size // 2), 0.5),
        (max(4, base_cell_size // 4), 0.25),
    )
    field = np.zeros((int(side), int(side)), dtype=np.float32)
    weight_total = 0.0
    for octave_index, (cell_size, weight) in enumerate(octaves):
        octave_seed = (
            (int(seed) & 0xFFFFFFFF)
            ^ (0x9E3779B9 * (int(layer_index) + 1))
            ^ (0x85EBCA6B * int(scale_percent))
            ^ (0xC2B2AE35 * (octave_index + 1))
        ) & 0xFFFFFFFF
        field += _interpolated_lattice(int(side), octave_seed, cell_size) * float(weight)
        weight_total += float(weight)
    return field / max(weight_total, 1.0)


def _value_fbm_field(
    side: int,
    seed: int,
    *,
    boundary_value: float | None = None,
) -> np.ndarray:
    """Build an independent four-octave value/fBm field in one domain."""

    side = int(side)
    octaves = (
        (max(16, side // 2), 1.0),
        (max(8, side // 4), 0.55),
        (max(4, side // 8), 0.30),
        (max(4, side // 16), 0.15),
    )
    field = np.zeros((side, side), dtype=np.float32)
    weight_total = 0.0
    for octave_index, (cell_size, weight) in enumerate(octaves):
        octave_seed = (
            (int(seed) & 0xFFFFFFFF)
            ^ 0xA511E9B3
            ^ (0x9E3779B9 * (octave_index + 1))
            ^ (0x63D83595 * (side + 1))
        ) & 0xFFFFFFFF
        field += _interpolated_lattice(
            side,
            octave_seed,
            cell_size,
            boundary_value=boundary_value,
        ) * float(weight)
        weight_total += float(weight)
    return field / max(weight_total, 1.0)


def _bilinear_sample(
    field: np.ndarray,
    row_coordinates: np.ndarray,
    column_coordinates: np.ndarray,
) -> np.ndarray:
    """Sample one square field at floating-point row/column coordinates."""

    values = _validate_square_field(field, "Le champ à échantillonner").astype(
        np.float32,
        copy=False,
    )
    side = int(values.shape[0])
    rows = np.clip(row_coordinates, 0.0, float(side - 1))
    columns = np.clip(column_coordinates, 0.0, float(side - 1))
    row_lower = np.floor(rows).astype(np.intp)
    column_lower = np.floor(columns).astype(np.intp)
    row_upper = np.minimum(row_lower + 1, side - 1)
    column_upper = np.minimum(column_lower + 1, side - 1)
    row_fraction = rows - row_lower
    column_fraction = columns - column_lower
    top_left = values[row_lower, column_lower]
    top_right = values[row_lower, column_upper]
    bottom_left = values[row_upper, column_lower]
    bottom_right = values[row_upper, column_upper]
    return (
        top_left * (1.0 - row_fraction) * (1.0 - column_fraction)
        + top_right * (1.0 - row_fraction) * column_fraction
        + bottom_left * row_fraction * (1.0 - column_fraction)
        + bottom_right * row_fraction * column_fraction
    )


def _warped_fbm_field(
    side: int,
    seed: int,
    *,
    finite_boundary: bool = False,
) -> np.ndarray:
    """Build a domain-warped field with broad, non-axis-aligned masses."""

    side = int(side)
    base_boundary = 0.0 if finite_boundary else None
    base = _value_fbm_field(
        side,
        int(seed) ^ 0xA511E9B3,
        boundary_value=base_boundary,
    )
    warp_cell = max(12, side // 3)
    warp_x = _interpolated_lattice(
        side,
        (int(seed) ^ 0xC2B2AE35) & 0xFFFFFFFF,
        warp_cell,
        boundary_value=0.5 if finite_boundary else None,
    )
    warp_y = _interpolated_lattice(
        side,
        (int(seed) ^ 0x85EBCA6B) & 0xFFFFFFFF,
        warp_cell,
        boundary_value=0.5 if finite_boundary else None,
    )
    coordinates = np.arange(side, dtype=np.float32)
    warp_amplitude = max(6, side // 8)
    # ``_interpolated_lattice`` already returns [-1, 1].  With the finite
    # boundary value 0.5, its sampled boundary is therefore exactly 0 and
    # must remain an immobile frame for the domain warp.
    rows = np.broadcast_to(
        coordinates[:, None] + warp_y * warp_amplitude,
        (side, side),
    )
    columns = np.broadcast_to(
        coordinates[None, :] + warp_x * warp_amplitude,
        (side, side),
    )
    warped = _bilinear_sample(base, rows, columns)
    detail = _value_fbm_field(
        side,
        int(seed) ^ 0x27D4EB2D,
        boundary_value=base_boundary,
    )
    return warped * 0.72 + detail * 0.28


def _smoothstep(values: np.ndarray) -> np.ndarray:
    clipped = np.clip(np.asarray(values, dtype=np.float32), 0.0, 1.0)
    return clipped * clipped * (3.0 - 2.0 * clipped)


def _shape_template_field(
    side: int,
    settings: Mapping[str, object] | None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(occupancy, relief_profile)`` for one shape template.

    ``occupancy`` is a soft spatial domain in ``[0, 1]``.  It is deliberately
    independent from any noise provider: the provider fills the mould instead
    of being used to manufacture the mould.  ``relief_profile`` is neutral for
    ordinary silhouettes and gives the dome template its broad cone/crater
    profile.
    """

    values = settings if isinstance(settings, Mapping) else {}
    shape_type = str(values.get("type", "none"))
    side = max(2, int(side))
    if shape_type == "none":
        neutral = np.ones((side, side), dtype=np.float32)
        return neutral, neutral.copy()

    coordinates = np.linspace(-1.0, 1.0, side, dtype=np.float32)
    x = np.broadcast_to(coordinates[None, :], (side, side)).copy()
    y = np.broadcast_to(coordinates[:, None], (side, side)).copy()
    x -= float(values.get("offset_x_percent", 0)) / 100.0
    y -= float(values.get("offset_y_percent", 0)) / 100.0

    angle = np.deg2rad(float(values.get("rotation_degrees", 0)))
    cosine = np.float32(np.cos(angle))
    sine = np.float32(np.sin(angle))
    local_x = x * cosine + y * sine
    local_y = -x * sine + y * cosine
    width = max(0.05, float(values.get("width_percent", 84)) / 100.0)
    height = max(0.05, float(values.get("height_percent", 84)) / 100.0)
    u = local_x / np.float32(width)
    v = local_y / np.float32(height)

    radius = np.sqrt(u * u + v * v)
    relief_profile = np.ones((side, side), dtype=np.float32)
    if shape_type == "ellipse":
        signed_distance = 1.0 - radius
    elif shape_type == "ring":
        thickness = np.clip(
            float(values.get("thickness_percent", 22)) / 100.0,
            0.05,
            0.45,
        )
        inner_radius = 1.0 - thickness
        signed_distance = np.minimum(1.0 - radius, radius - inner_radius)
    elif shape_type == "star":
        points = max(3, int(round(float(values.get("points", 5)))))
        inner = np.clip(
            float(values.get("inner_radius_percent", 42)) / 100.0,
            0.05,
            0.95,
        )
        theta = np.arctan2(v, u)
        point_wave = 0.5 + 0.5 * np.cos(float(points) * theta)
        boundary = inner + (1.0 - inner) * point_wave
        signed_distance = boundary - radius
    elif shape_type == "dome":
        signed_distance = 1.0 - radius
        cone = np.clip(1.0 - radius, 0.0, 1.0)
        crater_strength = np.clip(
            float(values.get("crater_percent", 18)) / 100.0,
            0.0,
            0.60,
        )
        crater_radius = 0.08 + crater_strength * 0.42
        crater = np.exp(-((radius / max(crater_radius, 0.01)) ** 2))
        relief_profile = np.clip(cone - crater * crater_strength * 0.70, 0.0, 1.0)
    else:  # pragma: no cover - profile normalization rejects this
        neutral = np.ones((side, side), dtype=np.float32)
        return neutral, neutral.copy()

    softness = np.clip(float(values.get("softness_percent", 8)) / 100.0, 0.0, 0.30)
    if softness <= 0.0:
        occupancy = (signed_distance >= 0.0).astype(np.float32)
    else:
        edge = max(0.004, float(softness) * 0.16)
        occupancy = _smoothstep((signed_distance + edge) / (2.0 * edge))
    return occupancy.astype(np.float32, copy=False), relief_profile


def _apply_preview_mirror(values: np.ndarray, mirror_mode: int) -> np.ndarray:
    """Apply the native preview mirror copies to a grayscale raster."""

    preview = np.asarray(values).copy()
    side = preview.shape[0]
    mirror_mode = int(mirror_mode)
    if mirror_mode & 0x02:
        for outer in range(side - 1):
            for inner in range(side - outer - 1):
                preview[side - 1 - outer, side - 1 - inner] = preview[
                    inner, outer
                ]
    if mirror_mode & 0x01:
        for source_col in range(1, side):
            for source_row in range(source_col):
                preview[source_col, source_row] = preview[source_row, source_col]
    return preview


def generate_shape_template_preview(
    profile: Mapping[str, object] | None,
    side: int,
    mirror_mode: int = 0,
) -> np.ndarray:
    """Return the current shape mould as an inexpensive grayscale preview.

    The mould is normally displayed before the native outer-water frame is
    applied, but it still follows the selected native mirror orientation so
    that its silhouette remains comparable with the main preview.
    """

    occupancy, _relief_profile = _shape_template_field(
        int(side), shape_template(profile)
    )
    preview = np.rint(np.clip(occupancy, 0.0, 1.0) * 255.0).astype(np.uint8)
    return _apply_preview_mirror(preview, mirror_mode)


def _apply_shape_template_to_field(
    field: np.ndarray,
    settings: Mapping[str, object] | None,
) -> np.ndarray:
    """Fill one independent normalized source inside the shape mould."""

    values = np.clip(np.asarray(field, dtype=np.float32), 0.0, 1.0)
    shape_type = str((settings or {}).get("type", "none"))
    if shape_type == "none":
        return values
    occupancy, relief_profile = _shape_template_field(values.shape[0], settings)
    if shape_type == "dome":
        strength = np.clip(
            float((settings or {}).get("relief_percent", 75)) / 100.0,
            0.0,
            1.0,
        )
        values = values * (1.0 - strength) + relief_profile * strength
    return np.clip(values * occupancy, 0.0, 1.0).astype(np.float32, copy=False)


def _soft_band_mask(
    values: np.ndarray,
    center_percent: int,
    width_percent: int,
    softness_percent: int,
) -> np.ndarray:
    """Return a soft finite band over a normalized control field."""

    values = np.asarray(values, dtype=np.float32)
    center = np.clip(float(center_percent) / 100.0, 0.0, 1.0)
    half_width = max(0.005, float(width_percent) / 200.0)
    lower = center - half_width
    upper = center + half_width
    if int(softness_percent) <= 0:
        return ((values >= lower) & (values <= upper)).astype(np.float32)
    edge = max(0.0025, half_width * float(softness_percent) / 100.0)
    lower_gate = _smoothstep((values - (lower - edge)) / (2.0 * edge))
    upper_gate = _smoothstep(((upper + edge) - values) / (2.0 * edge))
    return np.clip(lower_gate * upper_gate, 0.0, 1.0)


def _normalized_gradient_magnitude(values: np.ndarray) -> np.ndarray:
    gradients = np.gradient(np.asarray(values, dtype=np.float32))
    magnitude = np.sqrt(gradients[0] * gradients[0] + gradients[1] * gradients[1])
    scale = float(np.percentile(magnitude, 98.0)) if magnitude.size else 1.0
    if scale <= 1e-6:
        return np.zeros_like(magnitude, dtype=np.float32)
    return np.clip(magnitude / scale, 0.0, 1.0).astype(np.float32, copy=False)


def _normalized_curvature(values: np.ndarray) -> np.ndarray:
    values = np.asarray(values, dtype=np.float32)
    padded = np.pad(values, 1, mode="edge")
    laplacian = (
        padded[:-2, 1:-1]
        + padded[2:, 1:-1]
        + padded[1:-1, :-2]
        + padded[1:-1, 2:]
        - 4.0 * values
    )
    magnitude = np.abs(laplacian)
    scale = float(np.percentile(magnitude, 98.0)) if magnitude.size else 1.0
    if scale <= 1e-6:
        return np.zeros_like(magnitude, dtype=np.float32)
    return np.clip(magnitude / scale, 0.0, 1.0).astype(np.float32, copy=False)


def _apply_source_mask(
    field: np.ndarray,
    mask_settings: Mapping[str, object] | None,
    seed: int,
    source_settings: Mapping[str, object],
    *,
    adaptive_domain: tuple[int, int] | None = None,
) -> np.ndarray:
    """Modulate one source without leaving its finite rectangular domain."""

    values = np.clip(np.asarray(field, dtype=np.float32), 0.0, 1.0)
    settings = mask_settings if isinstance(mask_settings, Mapping) else {}
    mask_type = str(settings.get("type", "none"))
    if mask_type == "none":
        return values

    side = int(values.shape[0])
    rows, columns = np.indices(values.shape, dtype=np.float32)
    x = columns / max(1.0, float(side - 1))
    y = rows / max(1.0, float(side - 1))
    angle = np.deg2rad(float(settings.get("angle_degrees", 0)))
    direction = x * float(np.cos(angle)) + y * float(np.sin(angle))
    direction = np.clip(direction, 0.0, 1.0).astype(np.float32, copy=False)

    if mask_type == "height":
        control = values
        mask = _soft_band_mask(
            control,
            int(settings.get("center_percent", 50)),
            int(settings.get("width_percent", 100)),
            int(settings.get("softness_percent", 50)),
        )
    elif mask_type == "edge":
        distance = np.minimum.reduce((x, y, 1.0 - x, 1.0 - y))
        width = max(0.01, float(settings.get("width_percent", 100)) / 100.0)
        mask = _smoothstep(distance / (0.5 * width))
    elif mask_type in {"band_x", "band_y", "direction"}:
        control = x if mask_type == "band_x" else y
        if mask_type == "direction":
            control = direction
        mask = _soft_band_mask(
            control,
            int(settings.get("center_percent", 50)),
            int(settings.get("width_percent", 100)),
            int(settings.get("softness_percent", 50)),
        )
    elif mask_type == "slope":
        mask = _soft_band_mask(
            _normalized_gradient_magnitude(values),
            int(settings.get("center_percent", 50)),
            int(settings.get("width_percent", 100)),
            int(settings.get("softness_percent", 50)),
        )
    elif mask_type == "curvature":
        mask = _soft_band_mask(
            _normalized_curvature(values),
            int(settings.get("center_percent", 50)),
            int(settings.get("width_percent", 100)),
            int(settings.get("softness_percent", 50)),
        )
    elif mask_type == "noise":
        mask_source = str(settings.get("source", "perlin"))
        mask_seed = int(seed) + int(settings.get("seed_offset", 0)) + 0x51ED2705
        if adaptive_domain is None:
            mask_field = generate_noise_source(
                mask_source,
                side,
                mask_seed,
                source_settings,
            )
        else:
            mask_field = generate_noise_source(
                mask_source,
                side,
                mask_seed,
                source_settings,
                adaptive_domain=adaptive_domain,
            )
        mask = _soft_band_mask(
            np.clip((mask_field + 1.0) * 0.5, 0.0, 1.0),
            int(settings.get("center_percent", 50)),
            int(settings.get("width_percent", 100)),
            int(settings.get("softness_percent", 50)),
        )
    else:  # pragma: no cover - profile normalization rejects this
        return values

    invert = np.clip(float(settings.get("invert_percent", 0)) / 100.0, 0.0, 1.0)
    mask = mask * (1.0 - invert) + (1.0 - mask) * invert
    strength = np.clip(float(settings.get("strength_percent", 100)) / 100.0, 0.0, 1.0)
    factor = 1.0 - strength + strength * np.clip(mask, 0.0, 1.0)
    return np.clip(values * factor, 0.0, 1.0).astype(np.float32, copy=False)


def _ridged_fbm_field(
    side: int,
    seed: int,
    *,
    finite_boundary: bool = False,
) -> np.ndarray:
    """Build a ridged multifractal elevation source in one domain."""

    side = int(side)
    octaves = (
        (max(20, side // 2), 1.0),
        (max(10, side // 4), 0.55),
        (max(5, side // 8), 0.30),
        (max(4, side // 16), 0.15),
    )
    field = np.zeros((side, side), dtype=np.float32)
    weight_total = 0.0
    for octave_index, (cell_size, weight) in enumerate(octaves):
        value = _interpolated_lattice(
            side,
            (
                (int(seed) & 0xFFFFFFFF)
                ^ 0xB5297A4D
                ^ (0x9E3779B9 * (octave_index + 1))
            ) & 0xFFFFFFFF,
            cell_size,
            boundary_value=1.0 if finite_boundary else None,
        )
        ridge = 1.0 - np.abs(value)
        field += ((ridge * ridge) * 2.0 - 1.0) * float(weight)
        weight_total += float(weight)
    return field / max(weight_total, 1.0)


def _source_field_to_raw(field: np.ndarray, source_name: str) -> np.ndarray:
    """Map a complete source field to native unsigned raw elevation."""

    values = _validate_square_field(field, "Le champ de source").astype(
        np.float32,
        copy=False,
    )
    quantile_bounds = {
        RELIEF_SOURCE_FRACTAL: (0.14, 0.90),
        RELIEF_SOURCE_WARPED: (0.16, 0.91),
        RELIEF_SOURCE_RIDGED: (0.12, 0.88),
    }
    lower_quantile, upper_quantile = quantile_bounds[source_name]
    lower, upper = np.quantile(values, (lower_quantile, upper_quantile))
    span = max(float(upper - lower), 1e-6)
    normalized = np.clip((values - float(lower)) / span, 0.0, 1.0)
    if source_name == RELIEF_SOURCE_WARPED:
        normalized = np.power(normalized, 0.94)
    elif source_name == RELIEF_SOURCE_RIDGED:
        normalized = np.power(normalized, 0.82)
    return np.rint(normalized * 255.0).astype(np.uint8)


def _generate_complete_relief_source(
    side: int,
    seed: int,
    source_name: str,
) -> np.ndarray:
    """Generate one complete raw-elevation source in a finite inner domain."""

    side = int(side)
    margin = _relief_source_frame_margin(side)
    active_side = side - 2 * margin
    if active_side < 8:  # pragma: no cover - native map sizes stay above this
        raise ValueError("Le cadre intérieur est trop grand pour cette taille")

    if source_name == RELIEF_SOURCE_FRACTAL:
        field = _value_fbm_field(
            active_side,
            seed,
            boundary_value=0.0,
        )
    elif source_name == RELIEF_SOURCE_WARPED:
        field = _warped_fbm_field(
            active_side,
            seed,
            finite_boundary=True,
        )
    elif source_name == RELIEF_SOURCE_RIDGED:
        field = _ridged_fbm_field(
            active_side,
            seed,
            finite_boundary=True,
        )
    else:  # pragma: no cover - profile normalization guards this
        raise ValueError(f"Source de relief non implémentée : {source_name}")
    active_source = _source_field_to_raw(field, source_name)
    source = np.zeros((side, side), dtype=np.uint8)
    source[margin : side - margin, margin : side - margin] = active_source
    return source


def _configured_source_field(
    side: int,
    seed: int,
    source_name: str,
    settings: Mapping[str, object],
    profile: Mapping[str, object] | None,
    mask_settings: Mapping[str, object] | None = None,
    *,
    reference_side: int | None = None,
    domain_parameters: tuple[int, int] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return one bounded source in ``[0, 1]`` and its active-domain mask.

    The rectangular frame is part of the provider's sampling domain.  Values
    approach zero before the edge of that domain, so the generator never sees
    an infinite field abruptly cut at the map boundary.
    """

    side = int(side)
    margin, falloff_cells = (
        domain_parameters
        if domain_parameters is not None
        else finite_domain_parameters(profile, side=side, reference_side=reference_side)
    )
    margin = max(0, min(side // 3, int(margin)))
    active_side = side - margin * 2
    if active_side < 8:
        raise ValueError("Le domaine intérieur du bruit est trop petit")

    effective_settings = settings
    adaptive_domain = None
    morphology = profile.get("morphology", {}) if isinstance(profile, Mapping) else {}
    if (
        isinstance(morphology, Mapping)
        and morphology.get("size_adaptive_frequency", False) is True
    ):
        target_map_side = int(reference_side) if reference_side is not None else side
        target_margin = (
            int(margin)
            if reference_side is None
            else finite_domain_parameters(profile, side=target_map_side)[0]
        )
        target_domain_side = max(1, target_map_side - target_margin * 2)
        reference_margin = finite_domain_parameters(
            profile,
            side=NOISE_FREQUENCY_REFERENCE_SIDE,
        )[0]
        reference_domain_side = max(
            1,
            NOISE_FREQUENCY_REFERENCE_SIDE - reference_margin * 2,
        )
        adaptive_domain = (target_domain_side, reference_domain_side)
        effective_settings = adapt_noise_settings_for_domain_size(
            source_name,
            settings,
            target_domain_side,
            reference_domain_side=reference_domain_side,
        )

    if adaptive_domain is None:
        field = generate_noise_source(
            source_name,
            active_side,
            int(seed),
            effective_settings,
        )
    else:
        field = generate_noise_source(
            source_name,
            active_side,
            int(seed),
            effective_settings,
            adaptive_domain=adaptive_domain,
        )
    normalized = np.clip((field + 1.0) * 0.5, 0.0, 1.0)

    # Square distance-to-edge, deliberately not a radial/island mask.  It is
    # applied while constructing the finite source domain and therefore only
    # controls the boundary condition; it does not invent a second land shape.
    rows, columns = np.indices((active_side, active_side), dtype=np.int32)
    distance = np.minimum.reduce(
        (rows, columns, active_side - 1 - rows, active_side - 1 - columns)
    ).astype(np.float32)
    falloff_cells = max(1, int(falloff_cells))
    amount = np.clip(distance / float(falloff_cells), 0.0, 1.0)
    amount = amount * amount * (3.0 - 2.0 * amount)
    normalized *= amount
    if adaptive_domain is None:
        normalized = _apply_source_mask(
            normalized,
            mask_settings,
            int(seed),
            effective_settings,
        )
    else:
        normalized = _apply_source_mask(
            normalized,
            mask_settings,
            int(seed),
            effective_settings,
            adaptive_domain=adaptive_domain,
        )

    result = np.zeros((side, side), dtype=np.float32)
    domain = np.zeros((side, side), dtype=bool)
    target = np.s_[margin : margin + active_side, margin : margin + active_side]
    result[target] = normalized
    domain[target] = True
    return result, domain


def _source_to_raw(
    raw_height: np.ndarray,
    profile: Mapping[str, object] | None,
    source_name: str,
    settings: Mapping[str, object],
    seed: int,
    *,
    reference_side: int | None = None,
    domain_parameters: tuple[int, int] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return raw uint8 values, normalized source and its finite domain."""

    raw = _validate_square_field(raw_height, "Le champ natif brut").astype(
        np.uint8, copy=False
    )
    if source_name == NATIVE_RELIEF_SOURCE:
        normalized = raw.astype(np.float32) / 255.0
        return raw.copy(), normalized, np.ones(raw.shape, dtype=bool)
    if source_name == RELIEF_SOURCE_CUSTOM_LEGACY:
        normalized = raw.astype(np.float32) / 255.0
        return raw.copy(), normalized, np.ones(raw.shape, dtype=bool)
    normalized, domain = _configured_source_field(
        raw.shape[0],
        int(seed),
        source_name,
        settings,
        profile,
        relief_source_mask(profile),
        reference_side=reference_side,
        domain_parameters=domain_parameters,
    )
    return np.rint(normalized * 255.0).astype(np.uint8), normalized, domain


def _fuse_source(
    current: np.ndarray,
    source: np.ndarray,
    domain: np.ndarray,
    operation: str,
    strength_percent: int,
) -> np.ndarray:
    """Fuse an autonomous source into a normalized elevation field."""

    amount = max(0.0, min(2.0, float(strength_percent) / 100.0))
    before = np.asarray(current, dtype=np.float32)
    candidate = before.copy()
    if operation == "replace":
        changed = source
    elif operation == "blend":
        changed = before + (source - before) * min(1.0, amount)
    elif operation == "add":
        changed = before + source * amount
    elif operation == "subtract":
        changed = before - source * amount
    elif operation == "multiply":
        changed = before * (1.0 + (source - 1.0) * min(1.0, amount))
    elif operation == "min":
        changed = before + (np.minimum(before, source) - before) * min(1.0, amount)
    elif operation == "max":
        changed = before + (np.maximum(before, source) - before) * min(1.0, amount)
    else:  # pragma: no cover - profile validation rejects this first
        raise ValueError(f"Fusion de bruit non implémentée : {operation}")
    candidate[domain] = np.clip(changed[domain], 0.0, 1.0)
    return candidate


def _native_calibrated_envelope(
    side: int,
    profile: Mapping[str, object] | None,
    *,
    reference_side: int | None = None,
    domain_parameters: tuple[int, int] | None = None,
) -> np.ndarray:
    """Return the R53 outer envelope for masks and reduced thumbnails.

    The mask stack is applied after source/fusion composition, so it cannot
    receive the source provider's finite-domain mask automatically.  Keeping
    the same soft envelope here prevents a mask from reintroducing influence
    in the ocean frame.  Older percentage-domain profiles retain their
    historical mask behavior.
    """

    side = max(2, int(side))
    morphology = profile.get("morphology", {}) if isinstance(profile, Mapping) else {}
    if not isinstance(morphology, Mapping):
        return np.ones((side, side), dtype=np.float32)
    if str(morphology.get("finite_domain_mode", "percent")) != FINITE_DOMAIN_MODE_NATIVE_CALIBRATED:
        return np.ones((side, side), dtype=np.float32)

    margin, falloff_cells = (
        domain_parameters
        if domain_parameters is not None
        else finite_domain_parameters(profile, side=side, reference_side=reference_side)
    )
    margin = max(0, min(side // 3, int(margin)))
    active_side = side - margin * 2
    if active_side < 2:
        return np.zeros((side, side), dtype=np.float32)
    rows, columns = np.indices((active_side, active_side), dtype=np.int32)
    distance = np.minimum.reduce(
        (rows, columns, active_side - 1 - rows, active_side - 1 - columns)
    ).astype(np.float32)
    falloff_cells = max(1, int(falloff_cells))
    amount = np.clip(distance / float(falloff_cells), 0.0, 1.0)
    amount = amount * amount * (3.0 - 2.0 * amount)
    envelope = np.zeros((side, side), dtype=np.float32)
    target = np.s_[margin : margin + active_side, margin : margin + active_side]
    envelope[target] = amount
    return envelope


def _mask_layer_signal(
    side: int,
    layer: Mapping[str, object],
    profile: Mapping[str, object] | None = None,
    *,
    reference_side: int | None = None,
    envelope: np.ndarray | None = None,
) -> np.ndarray:
    """Return one soft 0..1 mask signal without clipping the base field."""

    # The mask editor owns only the common spatial contract.  Provider data is
    # merged here, at the provider boundary, so a future drawn/imported mask
    # can carry a completely different payload without adding shape-specific
    # controls to every mask card.
    settings = dict(SHAPE_TEMPLATE_DEFAULTS)
    provider_settings = layer.get("provider_settings", {})
    if isinstance(provider_settings, Mapping):
        settings.update(provider_settings)
    common_settings = layer.get("settings", {})
    if isinstance(common_settings, Mapping):
        settings.update(common_settings)
    mask_type = str(layer.get("type", "star"))
    settings["type"] = mask_type
    if mask_type == "manual":
        occupancy = _manual_mask_field(
            int(side),
            settings,
            provider_settings,
        )
        relief_profile = np.ones(occupancy.shape, dtype=np.float32)
    else:
        occupancy, relief_profile = _shape_template_field(int(side), settings)
    if mask_type == "dome":
        # Keep the cone/crater profile visible, but retain a non-zero shoulder
        # inside the silhouette so the mask does not behave like a hard cut.
        occupancy = occupancy * (0.45 + 0.55 * relief_profile)
    occupancy = occupancy * (
        envelope
        if envelope is not None
        else _native_calibrated_envelope(int(side), profile, reference_side=reference_side)
    )
    return np.clip(occupancy, 0.0, 1.0).astype(np.float32, copy=False)


def _manual_mask_field(
    side: int,
    settings: Mapping[str, object],
    provider_settings: Mapping[str, object] | None,
) -> np.ndarray:
    """Sample a portable manual grayscale mask in the common spatial frame."""

    provider = provider_settings if isinstance(provider_settings, Mapping) else {}
    raw_grid = provider.get("grid")
    expected = MASK_LAYER_MANUAL_GRID_SIDE * MASK_LAYER_MANUAL_GRID_SIDE
    if not isinstance(raw_grid, (list, tuple)) or len(raw_grid) != expected:
        return np.zeros((int(side), int(side)), dtype=np.float32)
    grid = np.asarray(raw_grid, dtype=np.float32).reshape(
        MASK_LAYER_MANUAL_GRID_SIDE,
        MASK_LAYER_MANUAL_GRID_SIDE,
    ) / 255.0

    coordinates = np.linspace(-1.0, 1.0, int(side), dtype=np.float32)
    x = np.broadcast_to(coordinates[None, :], (int(side), int(side))).copy()
    y = np.broadcast_to(coordinates[:, None], (int(side), int(side))).copy()
    x -= float(settings.get("offset_x_percent", 0)) / 100.0
    y -= float(settings.get("offset_y_percent", 0)) / 100.0

    angle = np.deg2rad(float(settings.get("rotation_degrees", 0)))
    cosine = np.float32(np.cos(angle))
    sine = np.float32(np.sin(angle))
    local_x = x * cosine + y * sine
    local_y = -x * sine + y * cosine
    width = max(0.05, float(settings.get("width_percent", 84)) / 100.0)
    height = max(0.05, float(settings.get("height_percent", 84)) / 100.0)
    u = local_x / np.float32(width)
    v = local_y / np.float32(height)
    valid = (np.abs(u) <= 1.0) & (np.abs(v) <= 1.0)

    source_x = (np.clip(u, -1.0, 1.0) + 1.0) * 0.5
    source_y = (np.clip(v, -1.0, 1.0) + 1.0) * 0.5
    source_x *= float(MASK_LAYER_MANUAL_GRID_SIDE - 1)
    source_y *= float(MASK_LAYER_MANUAL_GRID_SIDE - 1)
    occupancy = _bilinear_sample(grid, source_y, source_x)
    occupancy = np.where(valid, occupancy, 0.0)

    softness = np.clip(
        float(settings.get("softness_percent", 8)) / 100.0,
        0.0,
        0.30,
    )
    if softness > 0.0:
        edge = max(0.004, float(softness) * 0.16)
        distance = 1.0 - np.maximum(np.abs(u), np.abs(v))
        occupancy *= _smoothstep((distance + edge) / (2.0 * edge))
    return np.clip(occupancy, 0.0, 1.0).astype(np.float32, copy=False)


def _apply_mask_operation(
    current: np.ndarray,
    signal: np.ndarray,
    operation: str,
    strength_percent: int,
) -> np.ndarray:
    """Modulate every cell with one mask, preserving outside variation."""

    before = np.asarray(current, dtype=np.float32)
    signal = np.clip(np.asarray(signal, dtype=np.float32), 0.0, 1.0)
    amount = np.clip(float(strength_percent) / 100.0, 0.0, 2.0)
    blend_amount = min(1.0, amount)
    influence = signal * blend_amount
    if operation in {"blend", "replace"}:
        # Zero is the neutral value outside the shape.  Weighting the target
        # by the mask signal keeps the source field alive around and beyond
        # the silhouette instead of turning the exterior into a flat floor.
        changed = before + (signal - before) * influence
    elif operation == "add":
        changed = before + signal * amount
    elif operation == "subtract":
        changed = before - signal * amount
    elif operation == "multiply":
        centered = signal * 2.0 - 1.0
        changed = before * (1.0 + centered * 0.55 * influence)
    elif operation == "min":
        changed = before + (np.minimum(before, signal) - before) * influence
    elif operation == "max":
        changed = before + (np.maximum(before, signal) - before) * influence
    else:  # pragma: no cover - profile normalization rejects this first
        raise ValueError(f"Opération de masque non implémentée : {operation}")
    return np.clip(changed, 0.0, 1.0).astype(np.float32, copy=False)


def _apply_mask_layers_to_field(
    current: np.ndarray,
    profile: Mapping[str, object] | None,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply the independent mask stack after source/fusion composition."""

    values = np.clip(np.asarray(current, dtype=np.float32), 0.0, 1.0)
    total_delta = np.zeros(values.shape, dtype=np.float32)
    for index, layer in enumerate(mask_layer_parameters(profile)):
        enabled = bool(layer.get("enabled", False)) and int(
            layer.get("strength_percent", 0)
        ) > 0
        if not enabled:
            continue
        before = values.copy()
        signal = _mask_layer_signal(values.shape[0], layer, profile)
        values = _apply_mask_operation(
            values,
            signal,
            str(layer["operation"]),
            int(layer["strength_percent"]),
        )
        total_delta += values - before
    return values, total_delta


def _compose_noise_layers(
    source_height: np.ndarray,
    profile: Mapping[str, object] | None,
    seed: int,
) -> tuple[np.ndarray, tuple[NoiseLayerDiagnostic, ...], np.ndarray]:
    current = np.asarray(source_height, dtype=np.uint8).astype(np.float32) / 255.0
    reports: list[NoiseLayerDiagnostic] = []
    total_delta = np.zeros(current.shape, dtype=np.float32)
    for index, layer in _ordered_noise_layers(noise_layer_parameters(profile)):
        enabled = bool(layer.get("enabled", False)) and int(
            layer.get("strength_percent", 0)
        ) > 0
        before = current.copy()
        if enabled:
            component, domain = _configured_source_field(
                current.shape[0],
                int(seed) ^ (0x9E3779B9 * (index + 1)),
                str(layer["source"]),
                layer["settings"],
                profile,
                layer.get("mask_settings"),
            )
            current = _fuse_source(
                current,
                component,
                domain,
                str(layer["operation"]),
                int(layer["strength_percent"]),
            )
        else:
            component = np.zeros(current.shape, dtype=np.float32)
            domain = np.zeros(current.shape, dtype=bool)
        mask_settings = layer.get("mask_settings", {})
        mask_type = (
            str(mask_settings.get("type", "none"))
            if isinstance(mask_settings, Mapping)
            else "none"
        )
        mask_label = "finite_domain" if mask_type == "none" else mask_type
        delta = (current - before) * 255.0
        total_delta += delta
        affected = int(np.count_nonzero(np.abs(delta) > 1e-6))
        values = delta[domain] if np.any(domain) else np.asarray([], dtype=np.float32)
        reports.append(
            NoiseLayerDiagnostic(
                index=index,
                source=str(layer["source"]),
                role="full_field",
                mask=mask_label,
                operation=str(layer["operation"]),
                stage="source_composition",
                order=int(layer["order"]),
                enabled=enabled,
                domain_mask=domain,
                component=component * 2.0 - 1.0,
                delta=delta,
                affected_cell_count=affected,
                affected_percent=(100.0 * affected / float(delta.size)) if delta.size else 0.0,
                delta_minimum=float(np.min(values)) if values.size else 0.0,
                delta_maximum=float(np.max(values)) if values.size else 0.0,
                delta_mean=float(np.mean(values)) if values.size else 0.0,
                positive_cell_count=int(np.count_nonzero(delta > 1e-6)),
                negative_cell_count=int(np.count_nonzero(delta < -1e-6)),
            )
            )
    current, mask_delta = _apply_mask_layers_to_field(
        current,
        profile,
        int(seed),
    )
    total_delta += mask_delta
    composed = np.rint(np.clip(current, 0.0, 1.0) * 255.0).astype(np.uint8)
    return composed, tuple(reports), total_delta


def _relief_source_frame_margin(side: int) -> int:
    """Return the finite source-domain margin at a native map size."""

    side = int(side)
    reference = round(
        float(side) * float(RELIEF_SOURCE_FRAME_REFERENCE_CELLS) / 768.0
    )
    return min(
        max(RELIEF_SOURCE_FRAME_MINIMUM_MARGIN, reference),
        max(RELIEF_SOURCE_FRAME_MINIMUM_MARGIN, side // 4 - 1),
    )


def _center_noise_component(component: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Center and normalize one component before applying its amplitude."""

    values = np.asarray(component, dtype=np.float32)
    if mask is not None and np.any(mask):
        center = float(np.mean(values[mask]))
    else:
        center = float(np.mean(values))
    values = values - center
    maximum = (
        float(np.max(np.abs(values[mask])))
        if mask is not None and np.any(mask)
        else float(np.max(np.abs(values)))
    )
    if maximum > 1e-6:
        values = values / maximum
    return np.clip(values, -1.0, 1.0)


def apply_native_relief_source(
    raw_height: np.ndarray,
    profile: Mapping[str, object] | None = None,
    *,
    seed: int = 0,
) -> np.ndarray:
    """Return the raw field selected by the profile.

    Complete independent providers replace water and land. Legacy Custom is
    assembled earlier from its own anchors and macro blocks, so this later
    source-selection step is an identity for it, like Native Legacy.
    """

    raw = _validate_square_field(raw_height, "Le champ natif brut").astype(
        np.uint8,
        copy=True,
    )
    source_name = relief_source_parameter(profile)
    if source_name in {NATIVE_RELIEF_SOURCE, RELIEF_SOURCE_CUSTOM_LEGACY}:
        return raw
    source, _normalized, _domain = _source_to_raw(
        raw,
        profile,
        source_name,
        relief_source_settings(profile),
        int(seed),
    )
    return source


def _ordered_noise_layers(
    layers: tuple[dict, ...],
) -> tuple[tuple[int, dict], ...]:
    """Return layers in their explicit deterministic execution order."""

    return tuple(
        sorted(
            enumerate(layers),
            key=lambda item: (int(item[1].get("order", item[0])), item[0]),
        )
    )


def _noise_layer_contribution(
    side: int,
    seed: int,
    index: int,
    layer: dict,
    mask: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Return one centered component and its signed height contribution."""

    component = np.zeros((int(side), int(side)), dtype=np.float32)
    delta = np.zeros((int(side), int(side)), dtype=np.float32)
    if not bool(layer.get("enabled", False)):
        return component, delta
    strength = int(layer.get("strength_percent", 0))
    if strength <= 0:
        return component, delta

    component = _smooth_noise_field(
        int(side),
        int(seed),
        int(index),
        int(layer["scale_percent"]),
    )
    source_name = str(layer.get("source", layer.get("family", "smooth")))
    if source_name == "ridged":
        # Ridges are centered after shaping so they do not introduce a
        # hidden global height offset when combined with other layers.
        component = (1.0 - np.abs(component)) * 2.0 - 1.0
    component = _center_noise_component(component, mask)
    operation_sign = -1.0 if layer.get("operation") == "subtract" else 1.0
    delta = (
        component
        * (NOISE_LAYER_RAW_AMPLITUDE * float(strength) / 100.0)
        * operation_sign
    )
    delta[~mask] = 0.0
    return component, delta


def _noise_layer_delta(
    side: int,
    seed: int,
    layers: tuple[dict, ...],
    mask: np.ndarray,
) -> np.ndarray:
    """Return the ordered centered semantic noise delta."""

    delta = np.zeros((int(side), int(side)), dtype=np.float32)
    for index, layer in _ordered_noise_layers(layers):
        _component, contribution = _noise_layer_contribution(
            int(side),
            int(seed),
            index,
            layer,
            mask,
        )
        delta += contribution
    delta[~mask] = 0.0
    return delta


def build_noise_lab(
    raw_height: np.ndarray,
    profile: Mapping[str, object] | None = None,
    *,
    seed: int = 0,
) -> NoiseLabReport:
    """Build an inspectable report for the semantic layer stack.

    The laboratory deliberately stops before native normalization and terrain
    classification.  It is therefore useful for answering four separate
    questions: which cells a layer can touch, what source field it generated,
    what signed delta it contributed, and what the ordered raw result became.
    """

    raw = _validate_square_field(raw_height, "Le champ natif brut").astype(
        np.uint8,
        copy=True,
    )
    source_name = relief_source_parameter(profile)
    source_height, _source_normalized, _source_domain = _source_to_raw(
        raw,
        profile,
        source_name,
        relief_source_settings(profile),
        int(seed),
    )
    source_delta = source_height.astype(np.float32) - raw.astype(np.float32)
    reference_land_mask = raw >= NATIVE_RAW_WATER_FLOOR
    land_mask = source_height >= NATIVE_RAW_WATER_FLOOR
    composed, reports, layer_delta = _compose_noise_layers(
        source_height, profile, int(seed)
    )
    total_delta = source_delta + layer_delta
    return NoiseLabReport(
        raw_height=raw,
        source_height=source_height,
        composed_height=composed,
        land_mask=land_mask,
        total_delta=total_delta,
        layer_delta=layer_delta,
        layers=reports,
        source_delta=source_delta,
        reference_land_mask=reference_land_mask,
        source_name=source_name,
    )


def generate_noise_component_previews(
    profile: Mapping[str, object] | None,
    side: int,
    seed: int,
    *,
    mirror_mode: int = 0,
    include_principal: bool = True,
    source_height: np.ndarray | None = None,
    domain_side: int | None = None,
    component_cache: MutableMapping | None = None,
) -> tuple[np.ndarray, tuple[np.ndarray, ...]]:
    """Return cheap raw thumbnails for the principal source and fusion slots.

    Fusion fields are generated even when their slot is disabled, because the
    editor must let the user inspect a source before deciding to activate it.
    This path never runs native normalization, sculpture or relaxation.
    """

    side = max(16, int(side))
    seed = int(seed)
    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    morphology = normalized["morphology"]
    source_name = str(morphology["relief_source"])
    domain_parameters = finite_domain_parameters(
        normalized, side=side, reference_side=domain_side
    )
    if not include_principal:
        principal = np.zeros((side, side), dtype=np.uint8)
    elif source_height is None:
        if source_name == NATIVE_RELIEF_SOURCE:
            # The Legacy source is not a configurable provider.  Rebuilding
            # it through ``_source_to_raw(zeros)`` would produce a black
            # thumbnail, while reusing the composed display noise would make
            # the source card depend on morphology/fusions.  Use the same
            # native pre-sculpture field as the noise preview, at the nearest
            # valid native side, then downsample it for the card.
            from ..generators.legacy.native_terrain import (
                generate_relief_preview_noise_fast,
            )

            native_side = max(64, int(np.ceil(side / 64.0)) * 64)
            native_noise = generate_relief_preview_noise_fast(
                native_side,
                seed,
                int(mirror_mode),
                finalize=True,
                archetype_profile=(
                    normalized
                    if (
                        int(morphology.get("native_coarse_variation_percent", 100)) != 100
                        or int(morphology.get("native_refinement_percent", 100)) != 100
                        or int(morphology.get("native_large_scale_refinement_percent", 100)) != 100
                        or int(morphology.get("native_fine_scale_refinement_percent", 100)) != 100
                        or int(morphology.get("native_sculpture_attempts_percent", 100)) != 100
                        or int(morphology.get("native_relaxation_strength_percent", 100)) != 100
                    )
                    else None
                ),
            )
            native_values = np.clip(
                np.asarray(native_noise, dtype=np.int16)
                - int(NATIVE_NOISE_MINIMUM),
                0,
                255,
            ).astype(np.uint8)
            indices = np.rint(
                np.linspace(0.0, float(native_values.shape[0] - 1), side)
            ).astype(np.intp)
            principal = native_values[np.ix_(indices, indices)]
        elif source_name == RELIEF_SOURCE_CUSTOM_LEGACY:
            from ..generators.legacy.native_terrain import (
                generate_relief_preview_noise_fast,
            )

            native_side = max(64, int(np.ceil(side / 64.0)) * 64)
            native_noise = generate_relief_preview_noise_fast(
                native_side,
                seed,
                int(mirror_mode),
                finalize=True,
                archetype_profile=normalized,
            )
            native_values = np.clip(
                np.asarray(native_noise, dtype=np.int16)
                - int(NATIVE_NOISE_MINIMUM),
                0,
                255,
            ).astype(np.uint8)
            indices = np.rint(
                np.linspace(0.0, float(native_values.shape[0] - 1), side)
            ).astype(np.intp)
            principal = native_values[np.ix_(indices, indices)]
        else:
            raw = np.zeros((side, side), dtype=np.uint8)
            principal, _normalized, _domain = _source_to_raw(
                raw,
                normalized,
                source_name,
                morphology["relief_source_settings"],
                seed,
                reference_side=domain_side,
                domain_parameters=domain_parameters,
            )
    else:
        values = _validate_square_field(source_height, "La miniature de source")
        indices = np.rint(
            np.linspace(0.0, float(values.shape[0] - 1), side)
        ).astype(np.intp)
        principal = np.clip(values[np.ix_(indices, indices)], 0, 255).astype(
            np.uint8,
            copy=False,
        )

    components: list[np.ndarray] = []
    active_layers = morphology["noise_layers"][: int(morphology["noise_layer_count"])]
    for index, layer in enumerate(active_layers):
        layer_seed = seed ^ (0x9E3779B9 * (index + 1))
        cache_key = (
            "fusion",
            side,
            layer_seed,
            int(domain_side) if domain_side is not None else side,
            bool(morphology.get("size_adaptive_frequency", False)),
            str(morphology.get("finite_domain_mode", "percent")),
            int(morphology.get("frame_margin_percent", 5)),
            domain_parameters,
            str(layer["source"]),
            _component_cache_key(layer["settings"]),
            _component_cache_key(layer.get("mask_settings")),
        ) if component_cache is not None else None
        if cache_key is not None:
            try:
                hash(cache_key)
            except TypeError:
                cache_key = None  # Unknown extension payload: calculate normally.
        cached = (
            _component_cache_get(component_cache, cache_key)
            if cache_key is not None else None
        )
        if cached is not None:
            components.append(cached)
            continue
        component, _domain = _configured_source_field(
            side,
            layer_seed,
            str(layer["source"]),
            layer["settings"],
            normalized,
            layer.get("mask_settings"),
            reference_side=domain_side,
            domain_parameters=domain_parameters,
        )
        thumbnail = np.rint(np.clip(component, 0.0, 1.0) * 255.0).astype(np.uint8)
        if cache_key is not None:
            _component_cache_put(component_cache, cache_key, thumbnail)
        components.append(thumbnail)
    return principal.copy(), tuple(components)


def generate_mask_component_previews(
    profile: Mapping[str, object] | None,
    side: int,
    seed: int,
    *,
    mirror_mode: int = 0,
    domain_side: int | None = None,
    component_cache: MutableMapping | None = None,
) -> tuple[np.ndarray, ...]:
    """Return cheap grayscale previews for every visible mask slot."""

    del seed  # Parametric masks are deterministic from their profile settings.
    side = max(16, int(side))
    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    morphology = normalized["morphology"]
    domain_parameters = finite_domain_parameters(
        normalized, side=side, reference_side=domain_side
    )
    envelope = _native_calibrated_envelope(
        side, normalized, domain_parameters=domain_parameters
    )
    previews: list[np.ndarray] = []
    active_masks = morphology["mask_layers"][: int(morphology["mask_layer_count"])]
    for layer in active_masks:
        cache_key = (
            "mask",
            side,
            int(mirror_mode),
            morphology["finite_domain_mode"],
            domain_parameters,
            str(layer["type"]),
            _component_cache_key(layer["settings"]),
            _component_cache_key(layer["provider_settings"]),
        ) if component_cache is not None else None
        if cache_key is not None:
            try:
                hash(cache_key)
            except TypeError:
                cache_key = None
        cached = (
            _component_cache_get(component_cache, cache_key)
            if cache_key is not None else None
        )
        if cached is not None:
            previews.append(cached)
            continue
        signal = _mask_layer_signal(
            side,
            layer,
            normalized,
            reference_side=domain_side,
            envelope=envelope,
        )
        preview = np.rint(np.clip(signal, 0.0, 1.0) * 255.0).astype(np.uint8)
        thumbnail = _apply_preview_mirror(preview, mirror_mode)
        if cache_key is not None:
            _component_cache_put(component_cache, cache_key, thumbnail)
        previews.append(thumbnail)
    return tuple(previews)


def has_active_noise_layers(profile: Mapping[str, object] | None = None) -> bool:
    """Return whether a profile requests a non-zero semantic noise layer."""

    return any(
        bool(layer.get("enabled", False))
        and int(layer.get("strength_percent", 0)) > 0
        for layer in noise_layer_parameters(profile)
    )


def has_active_relief_source(profile: Mapping[str, object] | None = None) -> bool:
    """Return whether a non-native relief path is selected."""

    return relief_source_parameter(profile) != NATIVE_RELIEF_SOURCE


def apply_native_noise_layers(
    raw_height: np.ndarray,
    profile: Mapping[str, object] | None = None,
    *,
    seed: int = 0,
    lab_sink: MutableMapping[str, object] | None = None,
) -> np.ndarray:
    """Fuse autonomous sources into the selected complete elevation field."""

    raw = _validate_square_field(raw_height, "Le champ natif brut")
    if lab_sink is not None:
        report = build_noise_lab(raw_height, profile, seed=seed)
        lab_sink["report"] = report
        return report.composed_height.copy()

    if not has_active_noise_layers(profile) and not has_active_mask_layers(profile):
        return raw.astype(np.uint8, copy=True)
    composed, _reports, _delta = _compose_noise_layers(raw, profile, int(seed))
    return composed


def _apply_noise_layers(
    height: np.ndarray,
    signed_noise: np.ndarray | None,
    layers: tuple[dict, ...],
    seed: int,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Apply semantic layers to an already normalized field.

    This compatibility path remains available to callers that already own a
    normalized field.  The native generators use :func:`apply_native_noise_layers`
    earlier, before normalization and relaxation.
    """

    if not any(
        bool(layer.get("enabled", False))
        and int(layer.get("strength_percent", 0)) > 0
        for layer in layers
    ):
        return (
            np.asarray(height, dtype=np.uint8).copy(),
            None if signed_noise is None else np.asarray(signed_noise, dtype=np.int16).copy(),
        )

    side = int(height.shape[0])
    land_mask = np.asarray(height, dtype=np.uint8) > 0
    delta = _noise_layer_delta(side, int(seed), layers, land_mask)

    height_values = np.asarray(height, dtype=np.float32) + delta
    height_values[~land_mask] = np.asarray(height, dtype=np.float32)[~land_mask]
    transformed_height = np.rint(np.clip(height_values, 0.0, 255.0)).astype(np.uint8)
    if signed_noise is None:
        return transformed_height, None
    noise_values = np.asarray(signed_noise, dtype=np.float32) + delta
    noise_values[~land_mask] = np.asarray(signed_noise, dtype=np.float32)[~land_mask]
    return transformed_height, np.rint(noise_values).astype(np.int16)

def apply_archetype_morphology(
    height: np.ndarray,
    signed_noise: np.ndarray | None = None,
    profile: Mapping[str, object] | None = None,
    *,
    seed: int = 0,
    include_noise_layers: bool = True,
) -> tuple[np.ndarray, np.ndarray | None]:
    """Apply the profile's morphology to native height/noise fields.

    The return values are new arrays.  ``signed_noise`` may be omitted by the
    final Upgraded engine, which only needs the transformed game heightmap.
    """

    height_values = _validate_square_field(height, "La hauteur native")
    noise_values = None
    if signed_noise is not None:
        noise_values = _validate_square_field(signed_noise, "Le bruit signé")
        if noise_values.shape != height_values.shape:
            raise ValueError("Le bruit signé doit avoir la taille de la hauteur native")

    scale_percent, contrast_percent = morphology_parameters(profile)
    if relief_source_parameter(profile) == RELIEF_SOURCE_CUSTOM_LEGACY:
        # A block-built field has real cell-scale geometry. Do not resample it
        # through the unrelated experimental noise-map scaling control.
        scale_percent = 100
    layers = noise_layer_parameters(profile)
    has_active_layers = include_noise_layers and has_active_noise_layers(profile)
    has_active_masks = include_noise_layers and has_active_mask_layers(profile)
    if (
        scale_percent == 100
        and contrast_percent == 100
        and not has_active_layers
        and not has_active_masks
    ):
        return height_values.copy(), None if noise_values is None else noise_values.copy()

    transformed_height = _resample_centered(height_values, scale_percent)
    transformed_noise = (
        _resample_centered(noise_values, scale_percent)
        if noise_values is not None
        else None
    )
    if has_active_layers:
        transformed_height, transformed_noise = _apply_noise_layers(
            transformed_height,
            transformed_noise,
            layers,
            int(seed),
        )
    if has_active_masks:
        normalized_height = transformed_height.astype(np.float32) / 255.0
        masked_height, mask_delta = _apply_mask_layers_to_field(
            normalized_height,
            profile,
            int(seed),
        )
        transformed_height = np.rint(
            np.clip(masked_height, 0.0, 1.0) * 255.0
        ).astype(np.uint8)
        if transformed_noise is not None:
            transformed_noise = np.rint(
                np.asarray(transformed_noise, dtype=np.float32)
                + mask_delta
                * float(NATIVE_NOISE_MAXIMUM - NATIVE_NOISE_MINIMUM)
            ).astype(np.int16)
    transformed_height, transformed_noise = _apply_contrast(
        transformed_height,
        transformed_noise,
        contrast_percent,
    )
    if transformed_noise is not None:
        transformed_noise = np.asarray(transformed_noise, dtype=np.int16)
    return transformed_height, transformed_noise


def apply_archetype_noise_morphology(
    signed_noise: np.ndarray,
    profile: Mapping[str, object] | None = None,
    *,
    seed: int = 0,
    include_noise_layers: bool = True,
) -> np.ndarray:
    """Apply only the profile transform needed by the signed noise preview."""

    noise_values = _validate_square_field(signed_noise, "Le bruit signé")
    scale_percent, contrast_percent = morphology_parameters(profile)
    if relief_source_parameter(profile) == RELIEF_SOURCE_CUSTOM_LEGACY:
        scale_percent = 100
    layers = noise_layer_parameters(profile)
    has_active_layers = include_noise_layers and has_active_noise_layers(profile)
    has_active_masks = include_noise_layers and has_active_mask_layers(profile)
    if (
        scale_percent == 100
        and contrast_percent == 100
        and not has_active_layers
        and not has_active_masks
    ):
        return noise_values.astype(np.int16, copy=True)
    transformed = _resample_centered(noise_values, scale_percent).astype(
        np.float32,
        copy=False,
    )
    if has_active_layers:
        _unused_height, transformed = _apply_noise_layers(
            np.zeros_like(transformed, dtype=np.uint8),
            transformed,
            layers,
            int(seed),
        )
        if transformed is None:  # pragma: no cover - signed noise is supplied
            raise RuntimeError("La couche de bruit n’a pas produit de champ signé")
    if has_active_masks:
        noise_range = float(NATIVE_NOISE_MAXIMUM - NATIVE_NOISE_MINIMUM)
        normalized = (
            np.asarray(transformed, dtype=np.float32)
            - float(NATIVE_NOISE_MINIMUM)
        ) / noise_range
        _masked, mask_delta = _apply_mask_layers_to_field(
            normalized,
            profile,
            int(seed),
        )
        transformed = np.asarray(transformed, dtype=np.float32) + mask_delta * noise_range
    if contrast_percent != 100:
        noise_center = (
            float(NATIVE_NOISE_MINIMUM) + float(NATIVE_NOISE_MAXIMUM)
        ) / 2.0
        transformed = noise_center + (transformed - noise_center) * (
            float(contrast_percent) / 100.0
        )
    return np.rint(transformed).astype(np.int16)


__all__ = (
    "apply_archetype_morphology",
    "apply_archetype_noise_morphology",
    "apply_native_relief_source",
    "apply_native_noise_layers",
    "build_noise_lab",
    "generate_noise_component_previews",
    "generate_mask_component_previews",
    "generate_shape_template_preview",
    "has_active_relief_source",
    "has_active_noise_layers",
    "NoiseLabReport",
    "NoiseLayerDiagnostic",
)
