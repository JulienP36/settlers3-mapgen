"""Declarative macro-layout profiles owned by map archetypes.

The generator profiles in :mod:`s3mapgen.generation.custom` describe content
and rules that run after the macro form.  This module deliberately keeps the
archetype-owned values separate so a Custom archetype can be copied from a
built-in one without silently mixing terrain, resources or start bonuses into
the macro contract.

R32 models one principal source and up to six optional autonomous fusion sources.
Each source owns a complete finite-domain noisemap before the native
normalization and classification pipeline.  Fusion never inherits the Legacy
coast or a pre-existing land mask.
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Any

from .noise_sources import NOISE_SOURCE_OPTIONS

ARCHETYPE_PROFILE_SCHEMA_VERSION = 20

# The native relief pass first builds an unsigned 0..255 field and then
# applies ``raw - 0x1E`` while flooring water at zero.  The signed value shown
# by the archetype noise preview therefore has a real native lower bound of
# -30 and an upper bound of 225.  Keep those bounds explicit instead of
# allowing the preview renderer to wrap negative values through uint8.
NATIVE_NOISE_MINIMUM = -0x1E
NATIVE_NOISE_MAXIMUM = 0xFF - 0x1E

# The native summit-to-snow transition is not a single height delta: it is a
# two-cell terrain transition (Rocky32 -> 35 -> 129 -> Snow128).  The macro
# editor nevertheless needs a scalar guard, so keep two height units between
# the mountain and snow thresholds.  This is a UI/profile invariant, not a
# claim that the native terrain IDs encode a two-unit height difference.
MIN_MOUNTAIN_SNOW_THRESHOLD_GAP = 2

MORPHOLOGY_DEFAULTS = {
    "shape_scale_percent": 100,
    "relief_contrast_percent": 100,
    "native_coarse_variation_percent": 100,
    "native_refinement_percent": 100,
    "native_large_scale_refinement_percent": 100,
    "native_fine_scale_refinement_percent": 100,
    "native_sculpture_attempts_percent": 100,
    "native_relaxation_strength_percent": 100,
    "frame_margin_percent": 0,
    "edge_falloff_percent": 8,
}

MORPHOLOGY_BOUNDS = {
    "shape_scale_percent": (50, 100),
    "relief_contrast_percent": (25, 200),
    "native_coarse_variation_percent": (0, 200),
    "native_refinement_percent": (0, 300),
    "native_large_scale_refinement_percent": (0, 200),
    "native_fine_scale_refinement_percent": (0, 200),
    "native_sculpture_attempts_percent": (0, 200),
    "native_relaxation_strength_percent": (0, 100),
    "frame_margin_percent": (0, 25),
    "edge_falloff_percent": (1, 30),
}

MORPHOLOGY_TOGGLE_DEFAULTS = {
    "size_adaptive_frequency": False,
}

FINITE_DOMAIN_MODE_DEFAULT = "percent"
FINITE_DOMAIN_MODE_NATIVE_CALIBRATED = "native_calibrated"
FINITE_DOMAIN_MODE_OPTIONS = (
    FINITE_DOMAIN_MODE_DEFAULT,
    FINITE_DOMAIN_MODE_NATIVE_CALIBRATED,
)

# The native 768 corpus keeps the main land mass roughly 18–21 cells away
# from the serialized perimeter, with the usable coast becoming established
# around 28–30 cells.  The Custom source domain expresses that same envelope
# in absolute cells so it does not grow into an oversized ocean at 768×768.
NATIVE_CALIBRATED_FRAME_CELLS = 18
NATIVE_CALIBRATED_FALLOFF_CELLS = 31
# The Custom margin slider is rebased by one percentage point: new 0% gives
# the small R66 envelope, while new 4% preserves the former 5% / 18-cell point.
NATIVE_CALIBRATED_FRAME_REFERENCE_PERCENT = 5
NATIVE_CALIBRATED_FRAME_BASE_PERCENT = 1

RELIEF_SOURCE_DEFAULT = "native_legacy"
RELIEF_SOURCE_CUSTOM_LEGACY = "legacy_blocks"
CUSTOM_LEGACY_MOUNTAIN_THRESHOLD = 98
CUSTOM_LEGACY_SNOW_THRESHOLD = 125
RELIEF_SOURCE_OPTIONS = (
    RELIEF_SOURCE_DEFAULT,
    RELIEF_SOURCE_CUSTOM_LEGACY,
    *NOISE_SOURCE_OPTIONS,
)


def thresholds_on_relief_source_change(
    current: str, selected: str, mountain: int, snow: int,
) -> tuple[int, int]:
    """Rebase only untouched source defaults; preserve manually edited thresholds."""

    pair = (int(mountain), int(snow))
    if (
        selected != current
        and selected == RELIEF_SOURCE_CUSTOM_LEGACY
        and pair == (140, 190)
    ):
        return CUSTOM_LEGACY_MOUNTAIN_THRESHOLD, CUSTOM_LEGACY_SNOW_THRESHOLD
    if (
        current == RELIEF_SOURCE_CUSTOM_LEGACY
        and selected != current
        and pair == (CUSTOM_LEGACY_MOUNTAIN_THRESHOLD, CUSTOM_LEGACY_SNOW_THRESHOLD)
    ):
        return 140, 190
    return pair

# Named, inspectable profiles available in the Archetype tab.
CONTINENTAL_CUSTOM_PROFILE_KEY = "continental_custom_r82"
CONTINENTAL_CUSTOM_PROFILE_NAME = "Continental"
CLASSIC_PROFILE_NAME = "Classique"

NOISE_LAYER_DEFAULT_COUNT = 0
NOISE_LAYER_COUNT = 6
NOISE_LAYER_COUNT_BOUNDS = (0, NOISE_LAYER_COUNT)
NOISE_LAYER_FAMILY_OPTIONS = NOISE_SOURCE_OPTIONS
NOISE_LAYER_SOURCE_OPTIONS = NOISE_SOURCE_OPTIONS
NOISE_LAYER_ROLE_OPTIONS = ("full_field",)
NOISE_LAYER_MASK_OPTIONS = ("finite_domain",)
NOISE_LAYER_OPERATION_OPTIONS = (
    "replace",
    "blend",
    "add",
    "subtract",
    "multiply",
    "min",
    "max",
)
NOISE_LAYER_STAGE_OPTIONS = ("source_composition",)
NOISE_LAYER_SCALE_BOUNDS = (1, 32)
NOISE_LAYER_STRENGTH_BOUNDS = (0, 200)
NOISE_LAYER_ORDER_BOUNDS = (0, 99)

# R43 compatibility fields.  They remain readable so an old profile can still
# be inspected, but the editor no longer presents them as the shape system.
# The R44 shape contract below is deliberately independent from source fusion.
NOISE_MASK_TYPE_OPTIONS = (
    "none",
    "height",
    "edge",
    "band_x",
    "band_y",
    "direction",
    "slope",
    "curvature",
    "noise",
)
NOISE_MASK_SOURCE_OPTIONS = NOISE_SOURCE_OPTIONS
NOISE_MASK_DEFAULTS: dict[str, str | int] = {
    "type": "none",
    "source": "perlin",
    "strength_percent": 100,
    "invert_percent": 0,
    "center_percent": 50,
    "width_percent": 100,
    "angle_degrees": 0,
    "softness_percent": 50,
    "seed_offset": 0,
}
NOISE_MASK_BOUNDS: dict[str, tuple[int, int]] = {
    "strength_percent": (0, 100),
    "invert_percent": (0, 100),
    "center_percent": (0, 100),
    "width_percent": (1, 100),
    "angle_degrees": (0, 359),
    "softness_percent": (0, 100),
    "seed_offset": (-999999, 999999),
}
NOISE_MASK_INCREMENTS: dict[str, int] = {
    "strength_percent": 5,
    "invert_percent": 5,
    "center_percent": 5,
    "width_percent": 5,
    "angle_degrees": 5,
    "softness_percent": 5,
    "seed_offset": 1,
}

# A shape template is an archetype-level spatial mould.  It is not a second
# noise source and it is not owned by an individual fusion row.  The provider
# field is generated independently, then sampled inside this mould before the
# native raw-height normalization/classification pipeline.
SHAPE_TEMPLATE_TYPE_OPTIONS = (
    "none",
    "ellipse",
    "ring",
    "star",
    "dome",
)
_RETIRED_SHAPE_TEMPLATE_ALIASES = {
    "heart": "ellipse",
    "serpent": "ellipse",
    "volcano": "dome",
}
SHAPE_TEMPLATE_DEFAULTS: dict[str, str | int] = {
    "type": "none",
    "width_percent": 84,
    "height_percent": 84,
    "offset_x_percent": 0,
    "offset_y_percent": 0,
    "rotation_degrees": 0,
    "softness_percent": 8,
    "points": 5,
    "inner_radius_percent": 42,
    "thickness_percent": 22,
    "turns": 2,
    "amplitude_percent": 38,
    "taper_percent": 10,
    "crater_percent": 18,
    "relief_percent": 75,
}
SHAPE_TEMPLATE_BOUNDS: dict[str, tuple[int, int]] = {
    "width_percent": (20, 100),
    "height_percent": (20, 100),
    "offset_x_percent": (-50, 50),
    "offset_y_percent": (-50, 50),
    "rotation_degrees": (0, 359),
    "softness_percent": (0, 30),
    "points": (3, 12),
    "inner_radius_percent": (10, 90),
    "thickness_percent": (5, 45),
    "turns": (1, 6),
    "amplitude_percent": (0, 70),
    "taper_percent": (0, 100),
    "crater_percent": (0, 60),
    "relief_percent": (0, 100),
}
SHAPE_TEMPLATE_INCREMENTS: dict[str, int] = {
    "width_percent": 5,
    "height_percent": 5,
    "offset_x_percent": 5,
    "offset_y_percent": 5,
    "rotation_degrees": 5,
    "softness_percent": 1,
    "points": 1,
    "inner_radius_percent": 5,
    "thickness_percent": 1,
    "turns": 1,
    "amplitude_percent": 5,
    "taper_percent": 5,
    "crater_percent": 5,
    "relief_percent": 5,
}

# The mask stack deliberately exposes only these provider-independent spatial
# controls.  A provider may keep its own payload separately, but the core mask
# contract must not grow a new UI field every time a new shape is added.
MASK_LAYER_COMMON_DEFAULTS: dict[str, int] = {
    key: int(SHAPE_TEMPLATE_DEFAULTS[key])
    for key in (
        "width_percent",
        "height_percent",
        "offset_x_percent",
        "offset_y_percent",
        "rotation_degrees",
        "softness_percent",
    )
}
MASK_LAYER_COMMON_BOUNDS: dict[str, tuple[int, int]] = {
    key: SHAPE_TEMPLATE_BOUNDS[key] for key in MASK_LAYER_COMMON_DEFAULTS
}
MASK_LAYER_COMMON_INCREMENTS: dict[str, int] = {
    key: SHAPE_TEMPLATE_INCREMENTS[key] for key in MASK_LAYER_COMMON_DEFAULTS
}
_MASK_LAYER_PROVIDER_SETTING_KEYS = tuple(
    key
    for key in SHAPE_TEMPLATE_DEFAULTS
    if key not in MASK_LAYER_COMMON_DEFAULTS and key != "type"
)

# R46 mask stack.  A mask is a complete archetype-level modulation layer,
# separate from the noise fusion stack.  Its shape provider is currently
# parametric; manual/imported providers can be added later without changing
# the composition contract.
MASK_LAYER_COUNT = 6
MASK_LAYER_DEFAULT_COUNT = 0
MASK_LAYER_COUNT_BOUNDS = (0, MASK_LAYER_COUNT)
MASK_LAYER_MANUAL_GRID_SIDE = 64
MASK_LAYER_TYPE_OPTIONS = (*SHAPE_TEMPLATE_TYPE_OPTIONS[1:], "manual")
MASK_LAYER_OPERATION_OPTIONS = (
    "blend",
    "add",
    "subtract",
    "multiply",
    "min",
    "max",
    "replace",
)
MASK_LAYER_STRENGTH_BOUNDS = (0, 200)
MASK_LAYER_ORDER_BOUNDS = (0, 99)
MASK_LAYER_DEFAULTS: tuple[dict[str, Any], ...]

NOISE_SOURCE_SETTING_DEFAULTS: dict[str, int | float] = {
    "frequency": 4.0,
    "octaves": 5,
    "lacunarity": 2.0,
    "gain": 0.5,
    "rotation_degrees": 0,
    "stretch_percent": 100,
    "bias_percent": -20,
    "contrast_percent": 140,
    "warp_strength_percent": 80,
    "warp_frequency": 2.0,
    "seed_offset": 0,
    # Shared output remapping. Identity defaults preserve existing profiles.
    "inversion_percent": 0,
    "absolute_percent": 0,
    "gamma_percent": 100,
    "terrace_steps": 0,
    "terrace_blend_percent": 100,
    # Advanced provider-independent remapping. Identity values preserve the
    # R37 field exactly while exposing asymmetric ranges, plateaus and curves.
    "remap_low_percent": 0,
    "remap_high_percent": 100,
    "threshold_low_percent": 0,
    "threshold_high_percent": 100,
    "threshold_softness_percent": 0,
    "clamp_low_percent": 0,
    "clamp_high_percent": 100,
    "curve_bias_percent": 0,
    # Provider-independent coordinate transforms. Identity defaults preserve
    # all R37 profiles while exposing spatial control before field remapping.
    "offset_x_percent": 0,
    "offset_y_percent": 0,
    "scale_x_percent": 100,
    "scale_y_percent": 100,
    "repeat_x": 1,
    "repeat_y": 1,
    "symmetry_x_percent": 0,
    "symmetry_y_percent": 0,
}

NOISE_SOURCE_SETTING_BOUNDS: dict[str, tuple[int | float, int | float]] = {
    "frequency": (0.5, 32.0),
    "octaves": (1, 8),
    "lacunarity": (1.2, 4.0),
    "gain": (0.1, 0.9),
    "rotation_degrees": (0, 359),
    "stretch_percent": (25, 400),
    "bias_percent": (-100, 100),
    "contrast_percent": (25, 400),
    "warp_strength_percent": (0, 200),
    "warp_frequency": (0.5, 16.0),
    "seed_offset": (-999999, 999999),
    "inversion_percent": (0, 100),
    "absolute_percent": (0, 100),
    "gamma_percent": (25, 400),
    "terrace_steps": (0, 16),
    "terrace_blend_percent": (0, 100),
    "remap_low_percent": (0, 100),
    "remap_high_percent": (0, 100),
    "threshold_low_percent": (0, 100),
    "threshold_high_percent": (0, 100),
    "threshold_softness_percent": (0, 100),
    "clamp_low_percent": (0, 100),
    "clamp_high_percent": (0, 100),
    "curve_bias_percent": (-100, 100),
    "offset_x_percent": (-100, 100),
    "offset_y_percent": (-100, 100),
    "scale_x_percent": (25, 400),
    "scale_y_percent": (25, 400),
    "repeat_x": (1, 8),
    "repeat_y": (1, 8),
    "symmetry_x_percent": (0, 100),
    "symmetry_y_percent": (0, 100),
}

NOISE_SOURCE_SETTING_INCREMENTS: dict[str, int | float] = {
    "frequency": 0.5,
    "octaves": 1,
    "lacunarity": 0.1,
    "gain": 0.05,
    "rotation_degrees": 5,
    "stretch_percent": 5,
    "bias_percent": 5,
    "contrast_percent": 5,
    "warp_strength_percent": 5,
    "warp_frequency": 0.5,
    "seed_offset": 1,
    "inversion_percent": 5,
    "absolute_percent": 5,
    "gamma_percent": 5,
    "terrace_steps": 1,
    "terrace_blend_percent": 5,
    "remap_low_percent": 5,
    "remap_high_percent": 5,
    "threshold_low_percent": 5,
    "threshold_high_percent": 5,
    "threshold_softness_percent": 5,
    "clamp_low_percent": 5,
    "clamp_high_percent": 5,
    "curve_bias_percent": 5,
    "offset_x_percent": 5,
    "offset_y_percent": 5,
    "scale_x_percent": 5,
    "scale_y_percent": 5,
    "repeat_x": 1,
    "repeat_y": 1,
    "symmetry_x_percent": 5,
    "symmetry_y_percent": 5,
}

_NOISE_LAYER_SEEDS: tuple[dict[str, Any], ...] = (
    {
        "enabled": False,
        "source": "perlin",
        "family": "perlin",
        "role": "full_field",
        "mask": "finite_domain",
        "operation": "add",
        "stage": "source_composition",
        "order": 0,
        "scale_percent": 4,
        "strength_percent": 45,
        "mask_settings": deepcopy(NOISE_MASK_DEFAULTS),
        "settings": deepcopy(NOISE_SOURCE_SETTING_DEFAULTS),
    },
    {
        "enabled": False,
        "source": "ridged",
        "family": "ridged",
        "role": "full_field",
        "mask": "finite_domain",
        "operation": "max",
        "stage": "source_composition",
        "order": 1,
        "scale_percent": 8,
        "strength_percent": 55,
        "mask_settings": deepcopy(NOISE_MASK_DEFAULTS),
        "settings": {
            **deepcopy(NOISE_SOURCE_SETTING_DEFAULTS),
            "frequency": 8.0,
            "bias_percent": -10,
        },
    },
)


def _noise_layer_default(index: int) -> dict[str, Any]:
    """Return one independent default slot for a dynamic fusion stack."""

    value = deepcopy(_NOISE_LAYER_SEEDS[int(index) % len(_NOISE_LAYER_SEEDS)])
    value["order"] = int(index)
    return value


NOISE_LAYER_DEFAULTS: tuple[dict[str, Any], ...] = tuple(
    _noise_layer_default(index) for index in range(NOISE_LAYER_COUNT)
)


_MASK_LAYER_SEEDS: tuple[dict[str, Any], ...] = (
    {
        "type": "ellipse",
        "operation": "blend",
        "strength_percent": 45,
    },
    {
        "type": "ring",
        "operation": "add",
        "strength_percent": 35,
    },
    {
        "type": "star",
        "operation": "blend",
        "strength_percent": 40,
    },
    {
        "type": "dome",
        "operation": "add",
        "strength_percent": 50,
    },
)


def _mask_layer_default(index: int) -> dict[str, Any]:
    """Return one detached default slot for the independent mask stack."""

    seed = deepcopy(_MASK_LAYER_SEEDS[int(index) % len(_MASK_LAYER_SEEDS)])
    settings = deepcopy(MASK_LAYER_COMMON_DEFAULTS)
    provider_settings = {
        key: deepcopy(SHAPE_TEMPLATE_DEFAULTS[key])
        for key in _MASK_LAYER_PROVIDER_SETTING_KEYS
    }
    return {
        "enabled": False,
        "type": seed["type"],
        "operation": seed["operation"],
        "strength_percent": seed["strength_percent"],
        "order": int(index),
        "settings": settings,
        # This payload is intentionally not part of the common editor
        # contract.  It keeps the current parametric providers reproducible
        # while leaving room for manual/imported providers later.
        "provider_settings": provider_settings,
    }


MASK_LAYER_DEFAULTS = tuple(
    _mask_layer_default(index) for index in range(MASK_LAYER_COUNT)
)

# These are the thresholds currently used by the native Legacy and copied
# Upgraded relief classifiers:
#   height == 0       -> water
#   height < 0x8C (140) -> grass
#   height < 0xBE (190) -> rocky/mountain
#   otherwise         -> snow
# Keep the values in one declarative source so the built-in profile and the
# native classifier cannot drift silently.
CONTINENTAL_ARCHETYPE_PROFILE: dict[str, Any] = {
    "schema_version": ARCHETYPE_PROFILE_SCHEMA_VERSION,
    "profile_name": CLASSIC_PROFILE_NAME,
    "profile_kind": "archetype",
    "archetype_key": "continental",
    "layout_engine": "native_relief_v1",
    "noise": {
        "family": "native_midpoint",
        "editable": False,
        "display_range": {
            "minimum": NATIVE_NOISE_MINIMUM,
            "maximum": NATIVE_NOISE_MAXIMUM,
        },
    },
    "relief": {
        "water_threshold": 0,
        "mountain_threshold": 140,
        "snow_threshold": 190,
    },
    "morphology": {
        **MORPHOLOGY_DEFAULTS,
        **MORPHOLOGY_TOGGLE_DEFAULTS,
        "finite_domain_mode": FINITE_DOMAIN_MODE_DEFAULT,
        "relief_source": RELIEF_SOURCE_DEFAULT,
        "relief_source_settings": deepcopy(NOISE_SOURCE_SETTING_DEFAULTS),
        "relief_source_mask": deepcopy(NOISE_MASK_DEFAULTS),
        "shape_template": deepcopy(SHAPE_TEMPLATE_DEFAULTS),
        "noise_layer_count": NOISE_LAYER_DEFAULT_COUNT,
        "noise_layers": deepcopy(list(NOISE_LAYER_DEFAULTS)),
        "mask_layer_count": MASK_LAYER_DEFAULT_COUNT,
        "mask_layers": deepcopy(list(MASK_LAYER_DEFAULTS)),
    },
    "coast": {
        "derived": True,
        "rule": "water_to_shore_to_land",
    },
    "mass": {
        "layout": "mainland",
        "micro_islands": False,
    },
}

_CONTINENTAL_LOCKED_CONTRACT = {
    "layout_engine": "native_relief_v1",
    "noise_family": "native_midpoint",
    "noise_editable": False,
    "noise_minimum": NATIVE_NOISE_MINIMUM,
    "noise_maximum": NATIVE_NOISE_MAXIMUM,
    "coast_derived": True,
    "coast_rule": "water_to_shore_to_land",
    "mass_layout": "mainland",
    "micro_islands": False,
}


@dataclass(frozen=True, slots=True)
class ArchetypeParameterDescriptor:
    """Description of an editable scalar owned by an archetype profile."""

    path: tuple[str, ...]
    value_type: str
    default: int | float
    minimum: int | float
    maximum: int | float
    increment: int | float
    group: str
    label_key: str

    @property
    def key(self) -> str:
        return ".".join(self.path)


CONTINENTAL_PARAMETER_DESCRIPTORS: tuple[ArchetypeParameterDescriptor, ...] = (
    ArchetypeParameterDescriptor(
        ("morphology", "shape_scale_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["shape_scale_percent"],
        MORPHOLOGY_BOUNDS["shape_scale_percent"][0],
        MORPHOLOGY_BOUNDS["shape_scale_percent"][1],
        5,
        "morphology",
        "archetype_shape_scale",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "relief_contrast_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["relief_contrast_percent"],
        MORPHOLOGY_BOUNDS["relief_contrast_percent"][0],
        MORPHOLOGY_BOUNDS["relief_contrast_percent"][1],
        5,
        "morphology",
        "archetype_relief_contrast",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "native_coarse_variation_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["native_coarse_variation_percent"],
        MORPHOLOGY_BOUNDS["native_coarse_variation_percent"][0],
        MORPHOLOGY_BOUNDS["native_coarse_variation_percent"][1],
        5,
        "legacy_blocks",
        "archetype_native_coarse_variation",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "native_refinement_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["native_refinement_percent"],
        MORPHOLOGY_BOUNDS["native_refinement_percent"][0],
        MORPHOLOGY_BOUNDS["native_refinement_percent"][1],
        5,
        "legacy_blocks",
        "archetype_native_refinement",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "native_large_scale_refinement_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["native_large_scale_refinement_percent"],
        MORPHOLOGY_BOUNDS["native_large_scale_refinement_percent"][0],
        MORPHOLOGY_BOUNDS["native_large_scale_refinement_percent"][1],
        5,
        "legacy_blocks",
        "archetype_native_large_scale_refinement",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "native_fine_scale_refinement_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["native_fine_scale_refinement_percent"],
        MORPHOLOGY_BOUNDS["native_fine_scale_refinement_percent"][0],
        MORPHOLOGY_BOUNDS["native_fine_scale_refinement_percent"][1],
        5,
        "legacy_blocks",
        "archetype_native_fine_scale_refinement",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "native_sculpture_attempts_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["native_sculpture_attempts_percent"],
        MORPHOLOGY_BOUNDS["native_sculpture_attempts_percent"][0],
        MORPHOLOGY_BOUNDS["native_sculpture_attempts_percent"][1],
        5,
        "legacy_blocks",
        "archetype_native_sculpture_attempts",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "native_relaxation_strength_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["native_relaxation_strength_percent"],
        MORPHOLOGY_BOUNDS["native_relaxation_strength_percent"][0],
        MORPHOLOGY_BOUNDS["native_relaxation_strength_percent"][1],
        5,
        "legacy_blocks",
        "archetype_native_relaxation_strength",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "frame_margin_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["frame_margin_percent"],
        MORPHOLOGY_BOUNDS["frame_margin_percent"][0],
        MORPHOLOGY_BOUNDS["frame_margin_percent"][1],
        1,
        "morphology",
        "archetype_frame_margin",
    ),
    ArchetypeParameterDescriptor(
        ("morphology", "edge_falloff_percent"),
        "int",
        MORPHOLOGY_DEFAULTS["edge_falloff_percent"],
        MORPHOLOGY_BOUNDS["edge_falloff_percent"][0],
        MORPHOLOGY_BOUNDS["edge_falloff_percent"][1],
        1,
        "morphology",
        "archetype_edge_falloff",
    ),
    ArchetypeParameterDescriptor(
        ("relief", "water_threshold"),
        "int",
        0,
        NATIVE_NOISE_MINIMUM,
        139,
        1,
        "relief",
        "archetype_water_threshold",
    ),
    ArchetypeParameterDescriptor(
        ("relief", "mountain_threshold"),
        "int",
        140,
        1,
        188,
        1,
        "relief",
        "archetype_mountain_threshold",
    ),
    ArchetypeParameterDescriptor(
        ("relief", "snow_threshold"),
        "int",
        190,
        142,
        255,
        1,
        "relief",
        "archetype_snow_threshold",
    ),
)


def _deep_merge(base: Mapping[str, Any], overlay: Mapping[str, Any]) -> dict[str, Any]:
    result = deepcopy(dict(base))
    for key, value in overlay.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[str(key)] = deepcopy(value)
    return result


def _normalize_noise_source_settings(raw_settings: Any) -> dict[str, int | float]:
    if raw_settings is None:
        raw_settings = {}
    if not isinstance(raw_settings, Mapping):
        raise TypeError("Les paramètres d’une source de bruit doivent être un objet")
    normalized: dict[str, int | float] = {}
    for key, default in NOISE_SOURCE_SETTING_DEFAULTS.items():
        try:
            raw = float(raw_settings.get(key, default))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Le paramètre de bruit {key} doit être numérique") from exc
        minimum, maximum = NOISE_SOURCE_SETTING_BOUNDS[key]
        if not float(minimum) <= raw <= float(maximum):
            raise ValueError(
                f"Le paramètre de bruit {key} doit être compris entre {minimum} et {maximum}"
            )
        normalized[key] = int(round(raw)) if isinstance(default, int) else float(raw)
    return normalized


def _normalize_noise_mask(raw_mask: Any) -> dict[str, str | int]:
    """Normalize one optional finite-domain mask configuration."""

    if raw_mask is None:
        raw_mask = {}
    if not isinstance(raw_mask, Mapping):
        raise TypeError("Les paramètres du masque doivent être un objet")
    mask_type = str(raw_mask.get("type", NOISE_MASK_DEFAULTS["type"]))
    if mask_type not in NOISE_MASK_TYPE_OPTIONS:
        raise ValueError(f"Type de masque inconnu : {mask_type}")
    source = str(raw_mask.get("source", NOISE_MASK_DEFAULTS["source"]))
    if source not in NOISE_MASK_SOURCE_OPTIONS:
        raise ValueError(f"Source de masque inconnue : {source}")
    normalized: dict[str, str | int] = {
        "type": mask_type,
        "source": source,
    }
    for key, default in NOISE_MASK_DEFAULTS.items():
        if key in {"type", "source"}:
            continue
        try:
            value = round(float(raw_mask.get(key, default)))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Le paramètre de masque {key} doit être numérique") from exc
        minimum, maximum = NOISE_MASK_BOUNDS[key]
        if not minimum <= value <= maximum:
            raise ValueError(
                f"Le paramètre de masque {key} doit être compris entre "
                f"{minimum} et {maximum}"
            )
        normalized[key] = int(value)
    return normalized


def _normalize_shape_template(raw_template: Any) -> dict[str, str | int]:
    """Normalize one archetype-level parametric shape template."""

    if raw_template is None:
        raw_template = {}
    if not isinstance(raw_template, Mapping):
        raise TypeError("Le gabarit de forme doit être un objet")
    shape_type = str(raw_template.get("type", SHAPE_TEMPLATE_DEFAULTS["type"]))
    shape_type = _RETIRED_SHAPE_TEMPLATE_ALIASES.get(shape_type, shape_type)
    if shape_type not in SHAPE_TEMPLATE_TYPE_OPTIONS:
        raise ValueError(f"Type de gabarit inconnu : {shape_type}")
    normalized: dict[str, str | int] = {"type": shape_type}
    for key, default in SHAPE_TEMPLATE_DEFAULTS.items():
        if key == "type":
            continue
        try:
            value = round(float(raw_template.get(key, default)))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Le paramètre de gabarit {key} doit être numérique"
            ) from exc
        minimum, maximum = SHAPE_TEMPLATE_BOUNDS[key]
        if not minimum <= value <= maximum:
            raise ValueError(
                f"Le paramètre de gabarit {key} doit être compris entre "
                f"{minimum} et {maximum}"
            )
        normalized[key] = int(value)
    return normalized


def _normalize_mask_common_settings(
    raw_settings: Any,
    defaults: Mapping[str, Any] | None = None,
) -> dict[str, int]:
    """Normalize only the provider-independent spatial mask settings."""

    if raw_settings is None:
        raw_settings = {}
    if not isinstance(raw_settings, Mapping):
        raise TypeError("Les paramètres spatiaux du masque doivent être un objet")
    fallback = defaults if isinstance(defaults, Mapping) else MASK_LAYER_COMMON_DEFAULTS
    normalized: dict[str, int] = {}
    for key, default in MASK_LAYER_COMMON_DEFAULTS.items():
        try:
            value = round(float(raw_settings.get(key, fallback.get(key, default))))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Le paramètre spatial du masque {key} doit être numérique"
            ) from exc
        minimum, maximum = MASK_LAYER_COMMON_BOUNDS[key]
        if not minimum <= value <= maximum:
            raise ValueError(
                f"Le paramètre spatial du masque {key} doit être compris entre "
                f"{minimum} et {maximum}"
            )
        normalized[key] = int(value)
    return normalized


def _normalize_manual_mask_provider_settings(
    raw_settings: Mapping[str, Any],
) -> dict[str, Any]:
    """Normalize the portable grayscale grid used by a manual mask."""

    normalized = deepcopy(dict(raw_settings))
    if "grid" not in normalized:
        return normalized
    raw_grid = normalized["grid"]
    if isinstance(raw_grid, (list, tuple)):
        if len(raw_grid) == MASK_LAYER_MANUAL_GRID_SIDE and all(
            isinstance(row, (list, tuple)) for row in raw_grid
        ):
            flattened = [value for row in raw_grid for value in row]
        else:
            flattened = list(raw_grid)
    else:
        raise TypeError("La grille du masque manuel doit être une liste")
    expected = MASK_LAYER_MANUAL_GRID_SIDE * MASK_LAYER_MANUAL_GRID_SIDE
    if len(flattened) != expected:
        raise ValueError(
            "La grille du masque manuel doit contenir "
            f"{expected} niveaux de gris"
        )
    values: list[int] = []
    for value in flattened:
        try:
            numeric = round(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Les niveaux de gris du masque manuel doivent être numériques"
            ) from exc
        if not 0 <= numeric <= 255:
            raise ValueError(
                "Les niveaux de gris du masque manuel doivent être compris entre 0 et 255"
            )
        values.append(int(numeric))
    normalized["grid"] = values
    normalized["grid_side"] = MASK_LAYER_MANUAL_GRID_SIDE
    return normalized


def _normalize_noise_layers(raw_layers: Any) -> list[dict[str, Any]]:
    """Normalize the inspectable semantic noise-layer catalogue.

    ``family`` is retained as an R17 compatibility key.  New profiles should
    use ``source``; both keys are normalized to the same source identifier so
    old Custom profiles continue to load without changing their meaning.
    """

    if raw_layers is None:
        raw_layers = NOISE_LAYER_DEFAULTS
    if isinstance(raw_layers, Mapping):
        raw_layers = (raw_layers,)
    if not isinstance(raw_layers, (list, tuple)):
        raise TypeError("Les couches de bruit doivent être une liste")
    if len(raw_layers) > NOISE_LAYER_COUNT:
        raise ValueError(
            f"Le profil accepte au maximum {NOISE_LAYER_COUNT} couches de bruit"
        )

    normalized: list[dict[str, Any]] = []
    for index, defaults in enumerate(NOISE_LAYER_DEFAULTS):
        source = raw_layers[index] if index < len(raw_layers) else defaults
        if not isinstance(source, Mapping):
            raise TypeError(f"La couche de bruit {index + 1} doit être un objet")
        source_name = str(source.get("source", source.get("family", defaults["source"])))
        source_name = {"smooth": "fbm", "fractal_fbm": "fbm", "warped_fbm": "domain_warp", "ridged_fbm": "ridged"}.get(source_name, source_name)
        if source_name not in NOISE_LAYER_SOURCE_OPTIONS:
            raise ValueError(
                f"Source de bruit inconnue pour la couche {index + 1} : {source_name}"
            )
        role = "full_field"
        mask = "finite_domain"
        operation = str(source.get("operation", defaults["operation"]))
        if operation not in NOISE_LAYER_OPERATION_OPTIONS:
            raise ValueError(
                f"Opération de bruit inconnue pour la couche {index + 1} : {operation}"
            )
        stage = "source_composition"
        try:
            order = round(float(source.get("order", defaults["order"])))
            legacy_scale = float(source.get("scale_percent", defaults["scale_percent"]))
            scale = max(1, min(32, round(legacy_scale if legacy_scale <= 32 else 400.0 / legacy_scale)))
            strength = round(
                float(source.get("strength_percent", defaults["strength_percent"]))
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("Les paramètres des couches de bruit doivent être numériques") from exc
        if not NOISE_LAYER_ORDER_BOUNDS[0] <= order <= NOISE_LAYER_ORDER_BOUNDS[1]:
            raise ValueError(
                f"L’ordre de la couche de bruit {index + 1} doit être compris entre "
                f"{NOISE_LAYER_ORDER_BOUNDS[0]} et {NOISE_LAYER_ORDER_BOUNDS[1]}"
            )
        if not NOISE_LAYER_SCALE_BOUNDS[0] <= scale <= NOISE_LAYER_SCALE_BOUNDS[1]:
            raise ValueError(
                f"L’échelle de la couche de bruit {index + 1} doit être comprise entre "
                f"{NOISE_LAYER_SCALE_BOUNDS[0]} et {NOISE_LAYER_SCALE_BOUNDS[1]} %"
            )
        if not NOISE_LAYER_STRENGTH_BOUNDS[0] <= strength <= NOISE_LAYER_STRENGTH_BOUNDS[1]:
            raise ValueError(
                f"La force de la couche de bruit {index + 1} doit être comprise entre "
                f"{NOISE_LAYER_STRENGTH_BOUNDS[0]} et {NOISE_LAYER_STRENGTH_BOUNDS[1]} %"
            )
        source_settings = (
            dict(source.get("settings", {}))
            if isinstance(source.get("settings", {}), Mapping)
            else {}
        )
        source_settings.setdefault("frequency", scale)
        normalized.append(
            {
                "enabled": bool(source.get("enabled", defaults["enabled"])),
                "source": source_name,
                # Compatibility alias kept for R17 profiles and callers.
                "family": source_name,
                "role": role,
                "mask": mask,
                "operation": operation,
                "stage": stage,
                "order": int(order),
                "scale_percent": int(scale),
                "strength_percent": int(strength),
                "mask_settings": _normalize_noise_mask(source.get("mask_settings")),
                "settings": _normalize_noise_source_settings(source_settings),
            }
        )
    return normalized


def _normalize_mask_layers(raw_layers: Any) -> list[dict[str, Any]]:
    """Normalize the independent archetype-level mask stack.

    ``settings`` is the stable, provider-independent contract.  R46 shape
    controls are accepted as a compatibility input and moved into
    ``provider_settings`` so loading an existing profile does not silently
    change its silhouette, while the editor no longer presents those fields
    as if they applied to every future mask provider.
    """

    if raw_layers is None:
        raw_layers = MASK_LAYER_DEFAULTS
    if isinstance(raw_layers, Mapping):
        raw_layers = (raw_layers,)
    if not isinstance(raw_layers, (list, tuple)):
        raise TypeError("Les couches de masques doivent être une liste")
    if len(raw_layers) > MASK_LAYER_COUNT:
        raise ValueError(
            f"Le profil accepte au maximum {MASK_LAYER_COUNT} couches de masques"
        )

    normalized: list[dict[str, Any]] = []
    for index, defaults in enumerate(MASK_LAYER_DEFAULTS):
        source = raw_layers[index] if index < len(raw_layers) else defaults
        if not isinstance(source, Mapping):
            raise TypeError(f"La couche de masque {index + 1} doit être un objet")
        mask_type = str(source.get("type", defaults["type"]))
        mask_type = _RETIRED_SHAPE_TEMPLATE_ALIASES.get(mask_type, mask_type)
        if mask_type not in MASK_LAYER_TYPE_OPTIONS:
            raise ValueError(
                f"Type de masque inconnu pour la couche {index + 1} : {mask_type}"
            )
        operation = str(source.get("operation", defaults["operation"]))
        if operation not in MASK_LAYER_OPERATION_OPTIONS:
            raise ValueError(
                f"Opération de masque inconnue pour la couche {index + 1} : {operation}"
            )
        try:
            order = round(float(source.get("order", defaults["order"])))
            strength = round(
                float(source.get("strength_percent", defaults["strength_percent"]))
            )
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Les paramètres des couches de masques doivent être numériques"
            ) from exc
        if not MASK_LAYER_ORDER_BOUNDS[0] <= order <= MASK_LAYER_ORDER_BOUNDS[1]:
            raise ValueError(
                f"L’ordre de la couche de masque {index + 1} doit être compris entre "
                f"{MASK_LAYER_ORDER_BOUNDS[0]} et {MASK_LAYER_ORDER_BOUNDS[1]}"
            )
        if not MASK_LAYER_STRENGTH_BOUNDS[0] <= strength <= MASK_LAYER_STRENGTH_BOUNDS[1]:
            raise ValueError(
                f"La force de la couche de masque {index + 1} doit être comprise entre "
                f"{MASK_LAYER_STRENGTH_BOUNDS[0]} et {MASK_LAYER_STRENGTH_BOUNDS[1]} %"
            )
        raw_settings = source.get("settings", {})
        if not isinstance(raw_settings, Mapping):
            raise TypeError(
                f"Les paramètres du masque {index + 1} doivent être un objet"
            )
        settings = _normalize_mask_common_settings(
            raw_settings,
            defaults.get("settings"),
        )
        raw_provider_settings = source.get("provider_settings", {})
        if not isinstance(raw_provider_settings, Mapping):
            raise TypeError(
                f"Les paramètres du fournisseur du masque {index + 1} doivent être un objet"
            )
        provider_settings = deepcopy(
            dict(defaults.get("provider_settings", {}))
            if isinstance(defaults.get("provider_settings", {}), Mapping)
            else {}
        )
        provider_settings.update(deepcopy(dict(raw_provider_settings)))
        # R46 stored the shape-specific values directly beside the common
        # settings.  Preserve them as a provider payload during migration.
        for key in _MASK_LAYER_PROVIDER_SETTING_KEYS:
            if key in raw_settings and key not in raw_provider_settings:
                provider_settings[key] = deepcopy(raw_settings[key])
        if mask_type == "manual":
            provider_settings = {
                key: value
                for key, value in provider_settings.items()
                if key not in _MASK_LAYER_PROVIDER_SETTING_KEYS
            }
            provider_settings = _normalize_manual_mask_provider_settings(
                provider_settings
            )
        elif mask_type in SHAPE_TEMPLATE_TYPE_OPTIONS:
            shape_settings = {
                "type": mask_type,
                **MASK_LAYER_COMMON_DEFAULTS,
                **settings,
                **provider_settings,
            }
            normalized_shape = _normalize_shape_template(shape_settings)
            provider_extras = {
                key: value
                for key, value in provider_settings.items()
                if key not in _MASK_LAYER_PROVIDER_SETTING_KEYS
            }
            provider_settings = {
                key: normalized_shape[key]
                for key in _MASK_LAYER_PROVIDER_SETTING_KEYS
            }
            provider_settings.update(provider_extras)
        normalized.append(
            {
                "enabled": bool(source.get("enabled", defaults["enabled"])),
                "type": mask_type,
                "operation": operation,
                "strength_percent": int(strength),
                "order": int(order),
                "settings": settings,
                "provider_settings": provider_settings,
            }
        )
    return normalized


def _editable_noise_layer_stack(raw_layers: Any) -> list[dict[str, Any]]:
    """Return a complete, detached stack suitable for editor operations."""

    if not isinstance(raw_layers, (list, tuple)):
        raise TypeError("Les couches de bruit doivent être une liste")
    if len(raw_layers) > NOISE_LAYER_COUNT:
        raise ValueError(
            f"Le profil accepte au maximum {NOISE_LAYER_COUNT} couches de bruit"
        )
    stack: list[dict[str, Any]] = []
    for index in range(NOISE_LAYER_COUNT):
        value = raw_layers[index] if index < len(raw_layers) else NOISE_LAYER_DEFAULTS[index]
        if not isinstance(value, Mapping):
            raise TypeError(f"La couche de bruit {index + 1} doit être un objet")
        stack.append(deepcopy(dict(value)))
    return stack


def _renumber_noise_layer_stack(stack: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Make the visible slot order the persisted execution order."""

    for index, layer in enumerate(stack):
        layer["order"] = int(index)
    return stack


def _validate_noise_layer_position(count: int, index: int) -> tuple[int, int]:
    try:
        normalized_count = int(count)
        normalized_index = int(index)
    except (TypeError, ValueError) as exc:
        raise ValueError("La position d’une fusion doit être entière") from exc
    if not NOISE_LAYER_COUNT_BOUNDS[0] <= normalized_count <= NOISE_LAYER_COUNT:
        raise ValueError(
            f"Le nombre de fusions doit être compris entre "
            f"{NOISE_LAYER_COUNT_BOUNDS[0]} et {NOISE_LAYER_COUNT}"
        )
    if not 0 <= normalized_index < normalized_count:
        raise IndexError("La fusion sélectionnée n’est pas active")
    return normalized_count, normalized_index


def reorder_noise_layers(
    raw_layers: Any,
    count: int,
    index: int,
    direction: int,
) -> list[dict[str, Any]]:
    """Move one active fusion one slot up or down.

    The returned six-slot stack is detached from the input.  A move beyond
    either visible boundary is a harmless no-op, which keeps the operation
    safe when a UI button is invoked during a count change.
    """

    normalized_count, normalized_index = _validate_noise_layer_position(count, index)
    try:
        step = int(direction)
    except (TypeError, ValueError) as exc:
        raise ValueError("La direction de fusion doit être entière") from exc
    if step not in (-1, 1):
        raise ValueError("La direction de fusion doit valoir -1 ou 1")
    stack = _editable_noise_layer_stack(raw_layers)
    target = normalized_index + step
    if 0 <= target < normalized_count:
        stack[normalized_index], stack[target] = stack[target], stack[normalized_index]
    return _renumber_noise_layer_stack(stack)


def duplicate_noise_layer(
    raw_layers: Any,
    count: int,
    index: int,
) -> tuple[list[dict[str, Any]], int]:
    """Insert a copy of one active fusion immediately after it."""

    normalized_count, normalized_index = _validate_noise_layer_position(count, index)
    stack = _editable_noise_layer_stack(raw_layers)
    if normalized_count < NOISE_LAYER_COUNT:
        target = normalized_index + 1
        for position in range(normalized_count, target, -1):
            stack[position] = deepcopy(stack[position - 1])
        stack[target] = deepcopy(stack[normalized_index])
        normalized_count += 1
    return _renumber_noise_layer_stack(stack), normalized_count


def remove_noise_layer(
    raw_layers: Any,
    count: int,
    index: int,
) -> tuple[list[dict[str, Any]], int]:
    """Remove one active fusion and reset the newly hidden trailing slot."""

    normalized_count, normalized_index = _validate_noise_layer_position(count, index)
    stack = _editable_noise_layer_stack(raw_layers)
    for position in range(normalized_index, normalized_count - 1):
        stack[position] = deepcopy(stack[position + 1])
    stack[normalized_count - 1] = deepcopy(
        NOISE_LAYER_DEFAULTS[normalized_count - 1]
    )
    return _renumber_noise_layer_stack(stack), normalized_count - 1


def _editable_mask_layer_stack(raw_layers: Any) -> list[dict[str, Any]]:
    """Return a complete detached mask stack for editor operations."""

    if not isinstance(raw_layers, (list, tuple)):
        raise TypeError("Les couches de masques doivent être une liste")
    if len(raw_layers) > MASK_LAYER_COUNT:
        raise ValueError(
            f"Le profil accepte au maximum {MASK_LAYER_COUNT} couches de masques"
        )
    stack: list[dict[str, Any]] = []
    for index in range(MASK_LAYER_COUNT):
        value = raw_layers[index] if index < len(raw_layers) else MASK_LAYER_DEFAULTS[index]
        if not isinstance(value, Mapping):
            raise TypeError(f"La couche de masque {index + 1} doit être un objet")
        stack.append(deepcopy(dict(value)))
    return stack


def _renumber_mask_layer_stack(stack: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Make visible mask order equal its persisted execution order."""

    for index, layer in enumerate(stack):
        layer["order"] = int(index)
    return stack


def _validate_mask_layer_position(count: int, index: int) -> tuple[int, int]:
    try:
        normalized_count = int(count)
        normalized_index = int(index)
    except (TypeError, ValueError) as exc:
        raise ValueError("La position d’un masque doit être entière") from exc
    if not MASK_LAYER_COUNT_BOUNDS[0] <= normalized_count <= MASK_LAYER_COUNT:
        raise ValueError(
            f"Le nombre de masques doit être compris entre "
            f"{MASK_LAYER_COUNT_BOUNDS[0]} et {MASK_LAYER_COUNT}"
        )
    if not 0 <= normalized_index < normalized_count:
        raise IndexError("Le masque sélectionné n’est pas actif")
    return normalized_count, normalized_index


def reorder_mask_layers(
    raw_layers: Any,
    count: int,
    index: int,
    direction: int,
) -> list[dict[str, Any]]:
    """Move one visible mask one slot up or down."""

    normalized_count, normalized_index = _validate_mask_layer_position(count, index)
    try:
        step = int(direction)
    except (TypeError, ValueError) as exc:
        raise ValueError("La direction de masque doit être entière") from exc
    if step not in (-1, 1):
        raise ValueError("La direction de masque doit valoir -1 ou 1")
    stack = _editable_mask_layer_stack(raw_layers)
    target = normalized_index + step
    if 0 <= target < normalized_count:
        stack[normalized_index], stack[target] = stack[target], stack[normalized_index]
    return _renumber_mask_layer_stack(stack)


def duplicate_mask_layer(
    raw_layers: Any,
    count: int,
    index: int,
) -> tuple[list[dict[str, Any]], int]:
    """Insert a copy of one visible mask immediately after it."""

    normalized_count, normalized_index = _validate_mask_layer_position(count, index)
    stack = _editable_mask_layer_stack(raw_layers)
    if normalized_count < MASK_LAYER_COUNT:
        target = normalized_index + 1
        for position in range(normalized_count, target, -1):
            stack[position] = deepcopy(stack[position - 1])
        stack[target] = deepcopy(stack[normalized_index])
        normalized_count += 1
    return _renumber_mask_layer_stack(stack), normalized_count


def remove_mask_layer(
    raw_layers: Any,
    count: int,
    index: int,
) -> tuple[list[dict[str, Any]], int]:
    """Remove one visible mask and reset the hidden trailing slot."""

    normalized_count, normalized_index = _validate_mask_layer_position(count, index)
    stack = _editable_mask_layer_stack(raw_layers)
    for position in range(normalized_index, normalized_count - 1):
        stack[position] = deepcopy(stack[position + 1])
    stack[normalized_count - 1] = deepcopy(MASK_LAYER_DEFAULTS[normalized_count - 1])
    return _renumber_mask_layer_stack(stack), normalized_count - 1


def _reserved_profile(key: str) -> dict[str, Any]:
    """Return a structurally complete placeholder for an unimplemented key."""

    result = deepcopy(CONTINENTAL_ARCHETYPE_PROFILE)
    result.update(
        {
            "profile_name": f"{key} reserved",
            "archetype_key": str(key),
            "layout_engine": "reserved",
            "mass": {"layout": str(key), "micro_islands": True},
        }
    )
    return result


def default_archetype_profile(key: str = "continental") -> dict[str, Any]:
    """Return a fresh built-in profile for an archetype key."""

    key = str(key)
    if key == "continental":
        return deepcopy(CONTINENTAL_ARCHETYPE_PROFILE)
    return _reserved_profile(key)


def normalize_archetype_profile(
    profile: Mapping[str, Any] | None,
    *,
    archetype_key: str = "continental",
) -> dict[str, Any]:
    """Merge and validate an archetype profile without mutating its source."""

    key = str(archetype_key)
    source = profile if isinstance(profile, Mapping) else {}
    try:
        source_schema_version = int(source.get("schema_version", 0))
    except (TypeError, ValueError):
        source_schema_version = 0
    result = _deep_merge(default_archetype_profile(key), source)
    # Normalization is also the migration boundary for persisted R31 profiles.
    result["schema_version"] = ARCHETYPE_PROFILE_SCHEMA_VERSION
    result["profile_kind"] = "archetype"
    result["archetype_key"] = key

    relief = result.get("relief")
    if not isinstance(relief, Mapping):
        raise TypeError("Le profil d’archétype doit contenir relief")
    try:
        water = round(float(relief.get("water_threshold", 0)))
        mountain = round(float(relief.get("mountain_threshold", 140)))
        snow = round(float(relief.get("snow_threshold", 190)))
    except (TypeError, ValueError) as exc:
        raise ValueError("Les seuils du relief doivent être numériques") from exc
    source_morphology = result.get("morphology", {})
    source_relief = (
        str(source_morphology.get("relief_source", RELIEF_SOURCE_DEFAULT))
        if isinstance(source_morphology, Mapping) else RELIEF_SOURCE_DEFAULT
    )
    if (
        0 < source_schema_version < 20
        and source_relief in {RELIEF_SOURCE_CUSTOM_LEGACY, "legacy_derived"}
    ):
        # Old saved Custom profiles express their terrain thresholds in the
        # pre-R82 altitude range. Migrate the visible numbers once so that
        # reloading a profile does not silently remove its mountains.
        mountain = max(water + 1, min(188, round(mountain * 0.70)))
        snow = max(
            mountain + MIN_MOUNTAIN_SNOW_THRESHOLD_GAP,
            CUSTOM_LEGACY_SNOW_THRESHOLD,
            round(snow * 0.66),
        )
    if not (
        NATIVE_NOISE_MINIMUM <= water < mountain
        and mountain + MIN_MOUNTAIN_SNOW_THRESHOLD_GAP <= snow <= 255
    ):
        raise ValueError(
            "Les seuils du relief doivent respecter eau < montagne < neige "
            f"avec au moins {MIN_MOUNTAIN_SNOW_THRESHOLD_GAP} unités entre "
            f"montagne et neige dans l’intervalle {NATIVE_NOISE_MINIMUM}..255"
        )
    result["relief"] = dict(relief)
    result["relief"].update(
        water_threshold=water,
        mountain_threshold=mountain,
        snow_threshold=snow,
    )
    morphology = result.get("morphology")
    if not isinstance(morphology, Mapping):
        raise TypeError("Le profil d’archétype doit contenir morphology")
    normalized_morphology: dict[str, Any] = {}
    for name, default in MORPHOLOGY_DEFAULTS.items():
        try:
            value = round(float(morphology.get(name, default)))
        except (TypeError, ValueError) as exc:
            raise ValueError("Les paramètres de morphologie doivent être numériques") from exc
        minimum, maximum = MORPHOLOGY_BOUNDS[name]
        if not minimum <= value <= maximum:
            raise ValueError(
                f"Le paramètre de morphologie {name} doit être compris entre "
                f"{minimum} et {maximum}"
            )
        normalized_morphology[name] = int(value)
    adaptive_frequency = morphology.get(
        "size_adaptive_frequency",
        MORPHOLOGY_TOGGLE_DEFAULTS["size_adaptive_frequency"],
    )
    if not isinstance(adaptive_frequency, bool):
        raise ValueError("Le réglage size_adaptive_frequency doit être booléen")
    normalized_morphology["size_adaptive_frequency"] = adaptive_frequency
    finite_domain_mode = str(
        morphology.get("finite_domain_mode", FINITE_DOMAIN_MODE_DEFAULT)
    )
    if finite_domain_mode not in FINITE_DOMAIN_MODE_OPTIONS:
        raise ValueError(
            "Le mode de domaine fini doit être l’un de : "
            + ", ".join(FINITE_DOMAIN_MODE_OPTIONS)
        )
    normalized_morphology["finite_domain_mode"] = finite_domain_mode
    relief_source = str(
        morphology.get("relief_source", RELIEF_SOURCE_DEFAULT)
    )
    relief_source = {
        "fractal_fbm": "fbm",
        "warped_fbm": "domain_warp",
        "ridged_fbm": "ridged",
        # R73's temporary rank-redistribution experiment is retired. Keep
        # saved profiles loadable by migrating that choice to the block-based
        # Legacy Custom generator introduced in R74.
        "legacy_derived": RELIEF_SOURCE_CUSTOM_LEGACY,
    }.get(relief_source, relief_source)
    if relief_source not in RELIEF_SOURCE_OPTIONS:
        raise ValueError(f"Source de relief inconnue : {relief_source}")
    normalized_morphology["relief_source"] = relief_source
    normalized_morphology["relief_source_settings"] = _normalize_noise_source_settings(
        morphology.get("relief_source_settings")
    )
    normalized_morphology["relief_source_mask"] = _normalize_noise_mask(
        morphology.get("relief_source_mask")
    )
    normalized_morphology["shape_template"] = _normalize_shape_template(
        morphology.get("shape_template")
    )
    try:
        layer_count = round(
            float(morphology.get("noise_layer_count", NOISE_LAYER_DEFAULT_COUNT))
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("Le nombre de fusions doit être numérique") from exc
    if not NOISE_LAYER_COUNT_BOUNDS[0] <= layer_count <= NOISE_LAYER_COUNT_BOUNDS[1]:
        raise ValueError(
            f"Le nombre de fusions doit être compris entre "
            f"{NOISE_LAYER_COUNT_BOUNDS[0]} et {NOISE_LAYER_COUNT_BOUNDS[1]}"
        )
    normalized_morphology["noise_layer_count"] = int(layer_count)
    normalized_morphology["noise_layers"] = _normalize_noise_layers(
        morphology.get("noise_layers")
    )
    try:
        mask_layer_count = round(
            float(
                morphology.get(
                    "mask_layer_count",
                    MASK_LAYER_DEFAULT_COUNT,
                )
            )
        )
    except (TypeError, ValueError) as exc:
        raise ValueError("Le nombre de masques doit être numérique") from exc
    if not MASK_LAYER_COUNT_BOUNDS[0] <= mask_layer_count <= MASK_LAYER_COUNT_BOUNDS[1]:
        raise ValueError(
            f"Le nombre de masques doit être compris entre "
            f"{MASK_LAYER_COUNT_BOUNDS[0]} et {MASK_LAYER_COUNT_BOUNDS[1]}"
        )
    normalized_morphology["mask_layer_count"] = int(mask_layer_count)
    normalized_morphology["mask_layers"] = _normalize_mask_layers(
        morphology.get("mask_layers")
    )
    if source_schema_version and source_schema_version < 13:
        # R43 masks were source-local influence experiments.  They are not
        # silently carried into the R44 shape contract because doing so would
        # make a migrated profile change through a hidden nested modulation.
        normalized_morphology["relief_source_mask"] = deepcopy(NOISE_MASK_DEFAULTS)
        for layer in normalized_morphology["noise_layers"]:
            layer["mask_settings"] = deepcopy(NOISE_MASK_DEFAULTS)
    if source_schema_version < 14:
        # R44's global shape was a hard occupancy mould.  Carry it forward as
        # the first independent, soft mask instead of silently keeping the old
        # source-clipping behaviour.  The migration intentionally changes the
        # edge semantics to the new modulation contract.
        legacy_shape = normalized_morphology["shape_template"]
        if (
            str(legacy_shape.get("type", "none")) != "none"
            and int(normalized_morphology["mask_layer_count"]) == 0
        ):
            legacy_shape = _normalize_shape_template(legacy_shape)
            migrated = deepcopy(MASK_LAYER_DEFAULTS[0])
            migrated.update(
                enabled=True,
                type=str(legacy_shape["type"]),
                operation="blend",
                strength_percent=45,
                order=0,
                settings={
                    key: legacy_shape[key]
                    for key in MASK_LAYER_COMMON_DEFAULTS
                },
                provider_settings={
                    key: legacy_shape[key]
                    for key in _MASK_LAYER_PROVIDER_SETTING_KEYS
                },
            )
            normalized_morphology["mask_layers"][0] = migrated
            normalized_morphology["mask_layer_count"] = 1
        # Do not leave a second hidden global shape active after migration.
        normalized_morphology["shape_template"] = deepcopy(SHAPE_TEMPLATE_DEFAULTS)
    result["morphology"] = normalized_morphology
    if key == "continental":
        noise = result.get("noise")
        coast = result.get("coast")
        mass = result.get("mass")
        actual_contract = {
            "layout_engine": result.get("layout_engine"),
            "noise_family": noise.get("family") if isinstance(noise, Mapping) else None,
            "noise_editable": noise.get("editable") if isinstance(noise, Mapping) else None,
            "noise_minimum": (
                noise.get("display_range", {}).get("minimum")
                if isinstance(noise, Mapping)
                and isinstance(noise.get("display_range"), Mapping)
                else None
            ),
            "noise_maximum": (
                noise.get("display_range", {}).get("maximum")
                if isinstance(noise, Mapping)
                and isinstance(noise.get("display_range"), Mapping)
                else None
            ),
            "coast_derived": coast.get("derived") if isinstance(coast, Mapping) else None,
            "coast_rule": coast.get("rule") if isinstance(coast, Mapping) else None,
            "mass_layout": mass.get("layout") if isinstance(mass, Mapping) else None,
            "micro_islands": mass.get("micro_islands") if isinstance(mass, Mapping) else None,
        }
        if actual_contract != _CONTINENTAL_LOCKED_CONTRACT:
            raise ValueError(
                "Le contrat macro Continental natif est verrouillé : "
                "les contrôles de morphologie s’appliquent au champ de relief "
                "sans remplacer le moteur natif"
            )
    return result


def continental_legacy_blocks_profile() -> dict[str, Any]:
    """Return the named Continental profile derived from the native Legacy blocks.

    It uses the R82 field and thresholds already available in the editor.  The
    native Legacy profile remains the separate Classique choice; no extra
    terrain rules or hand-authored geometry are introduced here.
    """

    profile = default_archetype_profile("continental")
    profile["profile_name"] = CONTINENTAL_CUSTOM_PROFILE_NAME
    profile["profile_preset_key"] = CONTINENTAL_CUSTOM_PROFILE_KEY
    morphology = deepcopy(profile["morphology"])
    morphology["relief_source"] = RELIEF_SOURCE_CUSTOM_LEGACY
    morphology["relief_source_settings"] = deepcopy(NOISE_SOURCE_SETTING_DEFAULTS)
    morphology["relief_source_mask"] = deepcopy(NOISE_MASK_DEFAULTS)
    morphology["shape_template"] = deepcopy(SHAPE_TEMPLATE_DEFAULTS)
    morphology["noise_layer_count"] = NOISE_LAYER_DEFAULT_COUNT
    morphology["noise_layers"] = deepcopy(list(NOISE_LAYER_DEFAULTS))
    morphology["mask_layer_count"] = MASK_LAYER_DEFAULT_COUNT
    morphology["mask_layers"] = deepcopy(list(MASK_LAYER_DEFAULTS))
    profile["morphology"] = morphology
    profile["relief"].update(
        water_threshold=0,
        mountain_threshold=CUSTOM_LEGACY_MOUNTAIN_THRESHOLD,
        snow_threshold=CUSTOM_LEGACY_SNOW_THRESHOLD,
    )
    return normalize_archetype_profile(profile, archetype_key="continental")


def continental_noise_calibration_profile() -> dict[str, Any]:
    """Return the noise-only diagnostic composition used by qualification tools."""

    profile = default_archetype_profile("continental")
    profile["profile_name"] = "Continental noise calibration"
    morphology = deepcopy(profile["morphology"])
    settings = deepcopy(NOISE_SOURCE_SETTING_DEFAULTS)
    settings.update(
        frequency=4.0,
        octaves=5,
        lacunarity=2.0,
        gain=0.5,
        bias_percent=-20,
        contrast_percent=140,
    )
    morphology["finite_domain_mode"] = FINITE_DOMAIN_MODE_NATIVE_CALIBRATED
    morphology["relief_source"] = "fbm"
    morphology["relief_source_settings"] = settings
    layers = deepcopy(list(NOISE_LAYER_DEFAULTS))
    layers[0].update(
        enabled=True,
        source="domain_warp",
        family="domain_warp",
        operation="blend",
        order=0,
        scale_percent=3,
        strength_percent=15,
    )
    layers[0]["settings"].update(
        frequency=3.0,
        octaves=4,
        lacunarity=2.0,
        gain=0.5,
        warp_strength_percent=35,
        warp_frequency=2.0,
    )
    layers[1].update(
        enabled=True,
        source="ridged",
        family="ridged",
        operation="add",
        order=1,
        scale_percent=6,
        strength_percent=12,
    )
    layers[1]["settings"].update(
        frequency=6.0,
        octaves=4,
        lacunarity=2.0,
        gain=0.55,
        bias_percent=-10,
        contrast_percent=140,
    )
    morphology["noise_layer_count"] = 2
    morphology["noise_layers"] = layers
    morphology["mask_layer_count"] = MASK_LAYER_DEFAULT_COUNT
    morphology["mask_layers"] = deepcopy(list(MASK_LAYER_DEFAULTS))
    profile["morphology"] = morphology
    return normalize_archetype_profile(profile, archetype_key="continental")


def archetype_contract_values(
    profile: Mapping[str, Any] | None = None,
) -> dict[str, object]:
    """Return the normalized macro contract shown by the Archetype editor."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    noise = normalized.get("noise", {})
    coast = normalized.get("coast", {})
    mass = normalized.get("mass", {})
    display_range = noise.get("display_range", {}) if isinstance(noise, Mapping) else {}
    return {
        "layout_engine": normalized.get("layout_engine", ""),
        "noise_family": noise.get("family", "") if isinstance(noise, Mapping) else "",
        "noise_editable": bool(noise.get("editable", False))
        if isinstance(noise, Mapping)
        else False,
        "noise_minimum": display_range.get("minimum", NATIVE_NOISE_MINIMUM)
        if isinstance(display_range, Mapping)
        else NATIVE_NOISE_MINIMUM,
        "noise_maximum": display_range.get("maximum", NATIVE_NOISE_MAXIMUM)
        if isinstance(display_range, Mapping)
        else NATIVE_NOISE_MAXIMUM,
        "coast_derived": bool(coast.get("derived", False)) if isinstance(coast, Mapping) else False,
        "coast_rule": coast.get("rule", "") if isinstance(coast, Mapping) else "",
        "mass_layout": mass.get("layout", "") if isinstance(mass, Mapping) else "",
        "micro_islands": bool(mass.get("micro_islands", False)) if isinstance(mass, Mapping) else False,
    }


def iter_archetype_parameter_descriptors(
    profile: Mapping[str, Any] | None = None,
) -> tuple[ArchetypeParameterDescriptor, ...]:
    """Return the editable macro parameters for the current native contract."""

    # Keep this function profile-aware from the beginning: future archetypes
    # can select a different descriptor catalogue without changing the UI
    # contract.  R8 has one Continental catalogue only.  The bounds are
    # relational so the editor cannot offer a snow threshold below the
    # mountain threshold or a water threshold outside the observed native
    # signed range.
    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    water, mountain, snow = relief_thresholds(normalized)
    bounds = {
        ("relief", "water_threshold"): {
            "minimum": NATIVE_NOISE_MINIMUM,
            "maximum": mountain - 1,
        },
        ("relief", "mountain_threshold"): {
            "minimum": water + 1,
            "maximum": snow - MIN_MOUNTAIN_SNOW_THRESHOLD_GAP,
        },
        ("relief", "snow_threshold"): {
            "minimum": mountain + MIN_MOUNTAIN_SNOW_THRESHOLD_GAP,
            "maximum": 255,
        },
    }
    return tuple(
        replace(descriptor, **bounds[descriptor.path])
        if descriptor.path in bounds
        else descriptor
        for descriptor in CONTINENTAL_PARAMETER_DESCRIPTORS
    )


def relief_thresholds(profile: Mapping[str, Any] | None = None) -> tuple[int, int, int]:
    """Return ``(water, mountain, snow)`` thresholds for a classifier."""

    normalized = normalize_archetype_profile(profile, archetype_key="continental")
    relief = normalized["relief"]
    return (
        int(relief["water_threshold"]),
        int(relief["mountain_threshold"]),
        int(relief["snow_threshold"]),
    )


def morphology_parameters(
    profile: Mapping[str, Any] | None = None,
) -> tuple[int, int]:
    """Return the two post-source native morphology parameters."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    morphology = normalized["morphology"]
    return (
        int(morphology["shape_scale_percent"]),
        int(morphology["relief_contrast_percent"]),
    )


def relief_source_parameter(
    profile: Mapping[str, Any] | None = None,
) -> str:
    """Return the selected complete raw-elevation source."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    return str(normalized["morphology"]["relief_source"])


def noise_layer_parameters(
    profile: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Return normalized semantic noise layers for the morphology engine."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    morphology = normalized["morphology"]
    count = int(morphology["noise_layer_count"])
    return tuple(deepcopy(morphology["noise_layers"][:count]))


def mask_layer_parameters(
    profile: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Return normalized independent archetype mask layers."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    morphology = normalized["morphology"]
    count = int(morphology["mask_layer_count"])
    return tuple(deepcopy(morphology["mask_layers"][:count]))


def has_active_mask_layers(profile: Mapping[str, Any] | None = None) -> bool:
    """Return whether at least one independent mask is enabled."""

    return any(
        bool(layer.get("enabled", False))
        and int(layer.get("strength_percent", 0)) > 0
        for layer in mask_layer_parameters(profile)
    )


def relief_source_settings(
    profile: Mapping[str, Any] | None = None,
) -> dict[str, int | float]:
    """Return normalized settings for the principal autonomous source."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    return deepcopy(normalized["morphology"]["relief_source_settings"])


def shape_template(
    profile: Mapping[str, Any] | None = None,
) -> dict[str, str | int]:
    """Return the normalized archetype-level spatial shape template."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    return deepcopy(normalized["morphology"]["shape_template"])


def has_active_shape_template(profile: Mapping[str, Any] | None = None) -> bool:
    """Compatibility alias for the new independent mask stack."""

    return has_active_mask_layers(profile)


def relief_source_mask(
    profile: Mapping[str, Any] | None = None,
) -> dict[str, str | int]:
    """Return the normalized finite-domain mask for the principal source."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    return deepcopy(normalized["morphology"]["relief_source_mask"])


def finite_domain_parameters(
    profile: Mapping[str, Any] | None = None,
    *,
    side: int | None = None,
    reference_side: int | None = None,
) -> tuple[int, int]:
    """Return finite-domain widths, optionally resolved to map cells.

    Without ``side`` the historical percentage pair is returned for the
    editor/API.  With a side, the named native-calibrated Continental preset
    resolves those controls against the measured absolute native envelope;
    ordinary profiles retain their original percentage-of-map behavior.  A
    ``reference_side`` is used only by reduced previews: it scales the
    absolute calibrated cells to the thumbnail while preserving the same
    spatial framing as the full map.
    """

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    morphology = normalized["morphology"]
    margin_percent = int(morphology["frame_margin_percent"])
    falloff_percent = int(morphology["edge_falloff_percent"])
    if side is None:
        return margin_percent, falloff_percent
    if morphology.get("finite_domain_mode") == FINITE_DOMAIN_MODE_NATIVE_CALIBRATED:
        preview_scale = 1.0
        if reference_side is not None:
            preview_scale = float(side) / max(1.0, float(reference_side))
        margin = round(
            NATIVE_CALIBRATED_FRAME_CELLS
            * preview_scale
            * (margin_percent + NATIVE_CALIBRATED_FRAME_BASE_PERCENT)
            / NATIVE_CALIBRATED_FRAME_REFERENCE_PERCENT
        )
        falloff = round(
            NATIVE_CALIBRATED_FALLOFF_CELLS
            * preview_scale
            * falloff_percent
            / max(1, MORPHOLOGY_DEFAULTS["edge_falloff_percent"])
        )
        return int(margin), int(falloff)
    return (
        round(int(side) * margin_percent / 100.0),
        round(int(side) * falloff_percent / 100.0),
    )


__all__ = (
    "ARCHETYPE_PROFILE_SCHEMA_VERSION",
    "CLASSIC_PROFILE_NAME",
    "CONTINENTAL_ARCHETYPE_PROFILE",
    "CONTINENTAL_CUSTOM_PROFILE_KEY",
    "CONTINENTAL_CUSTOM_PROFILE_NAME",
    "continental_legacy_blocks_profile",
    "continental_noise_calibration_profile",
    "CONTINENTAL_PARAMETER_DESCRIPTORS",
    "FINITE_DOMAIN_MODE_DEFAULT",
    "FINITE_DOMAIN_MODE_NATIVE_CALIBRATED",
    "FINITE_DOMAIN_MODE_OPTIONS",
    "MIN_MOUNTAIN_SNOW_THRESHOLD_GAP",
    "MORPHOLOGY_BOUNDS",
    "MORPHOLOGY_DEFAULTS",
    "RELIEF_SOURCE_DEFAULT",
    "RELIEF_SOURCE_CUSTOM_LEGACY",
    "CUSTOM_LEGACY_MOUNTAIN_THRESHOLD",
    "CUSTOM_LEGACY_SNOW_THRESHOLD",
    "thresholds_on_relief_source_change",
    "RELIEF_SOURCE_OPTIONS",
    "NOISE_LAYER_COUNT",
    "NOISE_LAYER_COUNT_BOUNDS",
    "NOISE_LAYER_DEFAULT_COUNT",
    "NOISE_LAYER_DEFAULTS",
    "NOISE_LAYER_FAMILY_OPTIONS",
    "NOISE_LAYER_MASK_OPTIONS",
    "NOISE_LAYER_OPERATION_OPTIONS",
    "NOISE_LAYER_ORDER_BOUNDS",
    "NOISE_LAYER_ROLE_OPTIONS",
    "NOISE_LAYER_SOURCE_OPTIONS",
    "NOISE_LAYER_SCALE_BOUNDS",
    "NOISE_LAYER_STAGE_OPTIONS",
    "NOISE_LAYER_STRENGTH_BOUNDS",
    "NOISE_MASK_BOUNDS",
    "NOISE_MASK_DEFAULTS",
    "NOISE_MASK_INCREMENTS",
    "NOISE_MASK_SOURCE_OPTIONS",
    "NOISE_MASK_TYPE_OPTIONS",
    "SHAPE_TEMPLATE_BOUNDS",
    "SHAPE_TEMPLATE_DEFAULTS",
    "SHAPE_TEMPLATE_INCREMENTS",
    "SHAPE_TEMPLATE_TYPE_OPTIONS",
    "MASK_LAYER_COUNT",
    "MASK_LAYER_COUNT_BOUNDS",
    "MASK_LAYER_COMMON_BOUNDS",
    "MASK_LAYER_COMMON_DEFAULTS",
    "MASK_LAYER_COMMON_INCREMENTS",
    "MASK_LAYER_DEFAULT_COUNT",
    "MASK_LAYER_DEFAULTS",
    "MASK_LAYER_MANUAL_GRID_SIDE",
    "MASK_LAYER_OPERATION_OPTIONS",
    "MASK_LAYER_ORDER_BOUNDS",
    "MASK_LAYER_STRENGTH_BOUNDS",
    "MASK_LAYER_TYPE_OPTIONS",
    "NOISE_SOURCE_OPTIONS",
    "NOISE_SOURCE_SETTING_BOUNDS",
    "NOISE_SOURCE_SETTING_DEFAULTS",
    "NOISE_SOURCE_SETTING_INCREMENTS",
    "NATIVE_NOISE_MAXIMUM",
    "NATIVE_NOISE_MINIMUM",
    "NATIVE_CALIBRATED_FRAME_CELLS",
    "NATIVE_CALIBRATED_FRAME_BASE_PERCENT",
    "NATIVE_CALIBRATED_FRAME_REFERENCE_PERCENT",
    "NATIVE_CALIBRATED_FALLOFF_CELLS",
    "ArchetypeParameterDescriptor",
    "archetype_contract_values",
    "default_archetype_profile",
    "iter_archetype_parameter_descriptors",
    "normalize_archetype_profile",
    "morphology_parameters",
    "finite_domain_parameters",
    "noise_layer_parameters",
    "mask_layer_parameters",
    "has_active_mask_layers",
    "duplicate_noise_layer",
    "remove_noise_layer",
    "reorder_noise_layers",
    "duplicate_mask_layer",
    "remove_mask_layer",
    "reorder_mask_layers",
    "relief_source_settings",
    "relief_source_parameter",
    "shape_template",
    "has_active_shape_template",
    "relief_source_mask",
    "relief_thresholds",
)
