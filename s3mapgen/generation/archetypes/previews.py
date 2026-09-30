"""Deterministic macro previews owned by archetype profiles.

The preview deliberately stops after the native relief pass.  It does not run
resources, objects, starts or bonus content: the Archétype tab is showing the
macro contract, not pretending to be a finished generated map.
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Mapping, MutableMapping
from dataclasses import dataclass
from typing import Final

import numpy as np

from .masses import MacroMassReport, analyze_macro_masses
from .morphology import (
    NoiseLabReport,
    apply_archetype_morphology,
    apply_archetype_noise_morphology,
    build_noise_lab,
    has_active_noise_layers,
    has_active_relief_source,
    has_active_mask_layers,
)
from .profiles import (
    NATIVE_NOISE_MAXIMUM,
    NATIVE_NOISE_MINIMUM,
    RELIEF_SOURCE_CUSTOM_LEGACY,
    RELIEF_SOURCE_DEFAULT,
    normalize_archetype_profile,
    relief_thresholds,
)

MACRO_WATER: Final = 0
MACRO_BEACH: Final = 1
MACRO_GRASS: Final = 2
MACRO_MOUNTAIN: Final = 3
MACRO_SNOW: Final = 4
MACRO_CLASS_COUNT: Final = 5

# These colours are intentionally macro-only and stable.  They are not map
# terrain IDs and are kept separate from the detailed viewer palette.
NOISE_PALETTE: Final = ((0, 0, 0), (255, 255, 255))


def _has_active_native_blocks(profile: Mapping[str, object]) -> bool:
    """Whether editable Legacy relief blocks need a profile-aware pass."""

    morphology = profile.get("morphology", {})
    if not isinstance(morphology, Mapping):
        return False
    if str(morphology.get("relief_source", "native_legacy")) != "native_legacy":
        return False
    try:
        return (
            int(morphology.get("native_coarse_variation_percent", 100)) != 100
            or int(morphology.get("native_refinement_percent", 100)) != 100
            or int(morphology.get("native_large_scale_refinement_percent", 100)) != 100
            or int(morphology.get("native_fine_scale_refinement_percent", 100)) != 100
            or int(morphology.get("native_sculpture_attempts_percent", 100)) != 100
            or int(morphology.get("native_relaxation_strength_percent", 100)) != 100
        )
    except (TypeError, ValueError):
        return False
MACRO_PALETTE: Final = (
    (35, 96, 174),    # water
    (222, 193, 119),  # beach
    (91, 157, 75),    # grass
    (119, 115, 108),  # mountain
    (241, 242, 239),  # snow
)

_HEX_NEIGHBOURS: Final = ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))


@dataclass(frozen=True, slots=True)
class ArchetypePreview:
    """The two deterministic rasters displayed by the Archétype tab."""

    side: int
    seed: int
    mirror_mode: int
    noise: np.ndarray
    macro: np.ndarray
    thresholds: tuple[int, int, int]
    noise_reused: bool = False
    macro_relaxed: bool = True
    mass: MacroMassReport | None = None
    noise_lab: NoiseLabReport | None = None
    # Selected relief source before fusion layers and morphology.  Keeping
    # this separate prevents the source card from reusing the composed field.
    source_noise: np.ndarray | None = None


def _freeze(value):
    if isinstance(value, Mapping):
        return tuple(sorted((str(key), _freeze(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    return value


def _noise_cache_key(
    profile: Mapping[str, object],
    side: int,
    seed: int,
    mirror_mode: int,
    relax_macro: bool = True,
) -> tuple[object, ...]:
    return (
        "native-preview-fields-v9-relaxation",
        profile.get("archetype_key", "continental"),
        profile.get("layout_engine", "native_relief_v1"),
        _freeze(profile.get("noise", {})),
        int(profile.get("morphology", {}).get("native_coarse_variation_percent", 100))
        if isinstance(profile.get("morphology", {}), Mapping)
        else 100,
        int(profile.get("morphology", {}).get("native_refinement_percent", 100))
        if isinstance(profile.get("morphology", {}), Mapping)
        else 100,
        int(profile.get("morphology", {}).get("native_large_scale_refinement_percent", 100))
        if isinstance(profile.get("morphology", {}), Mapping)
        else 100,
        int(profile.get("morphology", {}).get("native_fine_scale_refinement_percent", 100))
        if isinstance(profile.get("morphology", {}), Mapping)
        else 100,
        int(profile.get("morphology", {}).get("native_sculpture_attempts_percent", 100))
        if isinstance(profile.get("morphology", {}), Mapping)
        else 100,
        int(profile.get("morphology", {}).get("native_relaxation_strength_percent", 100))
        if isinstance(profile.get("morphology", {}), Mapping)
        else 100,
        int(side),
        int(seed),
        int(mirror_mode),
        bool(relax_macro),
    )


def _cache_preview_fields(
    cache: MutableMapping,
    key: tuple[object, ...],
    noise: np.ndarray,
    height: np.ndarray,
    maximum: int = 4,
) -> None:
    value = (noise, height)
    if isinstance(cache, OrderedDict):
        cache.pop(key, None)
        cache[key] = value
        while len(cache) > maximum:
            cache.popitem(last=False)
        return
    cache[key] = value
    while len(cache) > maximum:
        first = next(iter(cache))
        del cache[first]


def _cache_noise_field(
    cache: MutableMapping,
    key: tuple[object, ...],
    noise: np.ndarray,
    maximum: int = 4,
) -> None:
    """Cache a raw native noise field with the same bounded LRU policy."""

    if isinstance(cache, OrderedDict):
        cache.pop(key, None)
        cache[key] = noise
        while len(cache) > maximum:
            cache.popitem(last=False)
        return
    cache[key] = noise
    while len(cache) > maximum:
        first = next(iter(cache))
        del cache[first]


def _touching_mask(mask: np.ndarray) -> np.ndarray:
    """Return cells touching a true cell in the native HEX6 topology."""

    result = np.zeros(mask.shape, dtype=bool)
    side = mask.shape[0]
    for dr, dc in _HEX_NEIGHBOURS:
        r0, r1 = max(0, dr), min(side, side + dr)
        c0, c1 = max(0, dc), min(side, side + dc)
        sr0, sr1 = max(0, -dr), min(side, side - dr)
        sc0, sc1 = max(0, -dc), min(side, side - dc)
        result[r0:r1, c0:c1] |= mask[sr0:sr1, sc0:sc1]
    return result


def classify_macro(
    noise: np.ndarray,
    profile: dict | None = None,
    *,
    final_height: np.ndarray | None = None,
) -> np.ndarray:
    """Classify the native relief into five stable macro display classes.

    ``final_height`` is the fully sculpted native game heightmap.  When it is
    provided, it is the source of truth for the default profile, so the macro
    preview cannot drift from the terrain pass.  Signed pre-floor noise is
    consulted only for cells that the game heightmap floors to zero when a
    custom water threshold goes below zero; this keeps the newly exposed
    negative range meaningful without changing the unchanged native result.
    """

    raw_noise = np.asarray(noise, dtype=np.int16)
    if raw_noise.ndim != 2 or raw_noise.shape[0] != raw_noise.shape[1]:
        raise ValueError("La noise map doit être une matrice carrée")
    if final_height is None:
        heights = raw_noise
    else:
        heights = np.asarray(final_height, dtype=np.int16)
        if heights.shape != raw_noise.shape:
            raise ValueError("La hauteur finale doit avoir la taille de la noise map")
    water_threshold, mountain_threshold, snow_threshold = relief_thresholds(profile)
    if final_height is not None and water_threshold < 0:
        heights = np.where(heights == 0, raw_noise, heights)
    macro = np.select(
        (
            heights <= water_threshold,
            heights < mountain_threshold,
            heights < snow_threshold,
        ),
        (MACRO_WATER, MACRO_GRASS, MACRO_MOUNTAIN),
        default=MACRO_SNOW,
    ).astype(np.uint8)
    water = macro == MACRO_WATER
    beach = (macro == MACRO_GRASS) & _touching_mask(water)
    macro[beach] = MACRO_BEACH
    return macro


def generate_archetype_preview(
    profile: dict | None,
    side: int,
    seed: int,
    mirror_mode: int = 0,
    *,
    noise_cache: MutableMapping | None = None,
    progress=None,
    relax_macro: bool = True,
) -> ArchetypePreview:
    """Generate the live preview for the selected archetype profile."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    if normalized.get("layout_engine") != "native_relief_v1":
        raise ValueError(
            f"Moteur de prévisualisation non disponible : {normalized.get('layout_engine')}"
        )
    # Keep the archetype catalogue importable without eagerly importing the
    # complete Legacy/Upgraded generator package (both pipelines consult the
    # catalogue during their own module initialization).
    from ..generators.legacy.native_terrain import (
        finalize_relief_preview_fields,
        finalize_relief_preview_noise,
        generate_relief_preview_fields,
    )

    side = int(side)
    seed = int(seed)
    mirror_mode = int(mirror_mode)
    active_components = (
        has_active_relief_source(normalized)
        or has_active_noise_layers(normalized)
        or has_active_mask_layers(normalized)
        or _has_active_native_blocks(normalized)
    )
    key = _noise_cache_key(
        normalized,
        side,
        seed,
        mirror_mode,
        relax_macro=relax_macro,
    )
    noise_reused = False
    noise = None
    height = None
    noise_lab_sink = {} if active_components else None
    # Active semantic layers are applied inside the native relief pass, so a
    # cache containing only the untouched native fields cannot be reused for
    # them.  Threshold/scale/contrast-only profiles still use the R12 cache.
    if noise_cache is not None and not active_components:
        cached = noise_cache.get(key)
        if cached is not None:
            # Accept the old single-array cache shape for callers that keep a
            # cache object alive while upgrading the application.
            if isinstance(cached, tuple) and len(cached) == 2:
                noise, height = cached
            else:
                noise = cached
                height = np.clip(noise, 0, 255).astype(np.uint8)
            noise_reused = True
            if progress is not None:
                progress(1.0, noise)
    if noise is None or height is None:

        def report_progress(fraction, snapshot):
            if progress is not None:
                progress(fraction, snapshot)

        noise, height = generate_relief_preview_fields(
            side,
            seed,
            mirror_mode,
            progress=report_progress if progress is not None else None,
            # Cache the native fields, then apply Custom morphology outside
            # the expensive native pass.  Threshold, scale and contrast edits
            # can consequently reuse the same generated fields.
            archetype_profile=normalized if active_components else None,
            noise_lab=noise_lab_sink,
            finalize=False,
            relax_relief=relax_macro,
        )
        if noise_cache is not None and not active_components:
            _cache_preview_fields(noise_cache, key, noise, height)
    source_base_noise = np.asarray(noise, dtype=np.int16).copy()
    height, noise = apply_archetype_morphology(
        height,
        noise,
        normalized,
        seed=seed,
        include_noise_layers=not active_components,
    )
    if noise is None:  # pragma: no cover - the preview always supplies noise
        raise RuntimeError("Le bruit signé de la preview n’a pas été conservé")
    noise, height = finalize_relief_preview_fields(noise, height, mirror_mode)
    lab_report = (
        noise_lab_sink.get("report")
        if isinstance(noise_lab_sink, dict)
        and isinstance(noise_lab_sink.get("report"), NoiseLabReport)
        else None
    )
    if lab_report is not None:
        # The lab stores the selected raw source before any fusion.  Convert
        # it to the signed/display domain and apply the same orientation and
        # outer-water frame as the main noise preview.
        source_noise = finalize_relief_preview_noise(
            lab_report.source_height.astype(np.int16) + NATIVE_NOISE_MINIMUM,
            mirror_mode,
        )
    else:
        # For native Legacy there is no composition report: the captured
        # pre-normalization field is the source itself.  Preserve it before
        # morphology so scale/contrast cannot turn this into a composed copy.
        source_noise = finalize_relief_preview_noise(
            source_base_noise,
            mirror_mode,
        )
    if progress is not None:
        progress(1.0, noise)
    macro = classify_macro(noise, normalized, final_height=height)
    return ArchetypePreview(
        side=side,
        seed=seed,
        mirror_mode=mirror_mode,
        noise=noise,
        macro=macro,
        thresholds=relief_thresholds(normalized),
        noise_reused=noise_reused,
        macro_relaxed=bool(relax_macro),
        mass=analyze_macro_masses(macro),
        noise_lab=lab_report,
        source_noise=source_noise,
    )


def generate_archetype_noise_preview(
    profile: dict | None,
    side: int,
    seed: int,
    mirror_mode: int = 0,
    *,
    noise_cache: MutableMapping | None = None,
    lab_sink: MutableMapping[str, object] | None = None,
) -> np.ndarray:
    """Return the completed signed noise preview without native relaxation.

    This is intentionally a preview-only path.  It stops after the exact
    native coarse/refinement field that the normal noise canvas already shows;
    it never changes the final map generation path.
    """

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    if normalized.get("layout_engine") != "native_relief_v1":
        raise ValueError(
            f"Moteur de prévisualisation non disponible : {normalized.get('layout_engine')}"
        )
    from ..generators.legacy.native_terrain import (
        finalize_relief_preview_noise,
        generate_relief_preview_noise_fast,
    )

    side = int(side)
    seed = int(seed)
    mirror_mode = int(mirror_mode)
    active_components = (
        has_active_relief_source(normalized)
        or has_active_noise_layers(normalized)
        or has_active_mask_layers(normalized)
        or _has_active_native_blocks(normalized)
    )
    key = _noise_cache_key(normalized, side, seed, mirror_mode)
    raw_noise = None
    if noise_cache is not None and not active_components:
        cached = noise_cache.get(key)
        if isinstance(cached, np.ndarray):
            raw_noise = cached
    if raw_noise is None:
        raw_noise = generate_relief_preview_noise_fast(
            side,
            seed,
            mirror_mode,
            finalize=False,
            archetype_profile=normalized if active_components else None,
            noise_lab=lab_sink if active_components else None,
        )
        if noise_cache is not None and not active_components:
            _cache_noise_field(noise_cache, key, raw_noise)
    transformed = apply_archetype_noise_morphology(
        raw_noise,
        normalized,
        seed=seed,
        include_noise_layers=not active_components,
    )
    return finalize_relief_preview_noise(transformed, mirror_mode)


def generate_archetype_indicative_preview(
    profile: dict | None,
    side: int,
    seed: int,
    mirror_mode: int = 0,
    *,
    noise_cache: MutableMapping | None = None,
    lab_sink: MutableMapping[str, object] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return fast noise and a clearly indicative pre-relax macro raster.

    The macro raster is classified from the completed fast noise field, not
    from the final sculpted/relaxed game heightmap.  It is suitable for quick
    visual feedback only and is replaced by :func:`generate_archetype_preview`
    when the exact native macro result is ready.
    """

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str((profile or {}).get("archetype_key", "continental")),
    )
    # Autonomous providers do not need the Legacy refinement merely to show
    # their source map.  Compose them directly on a small preview grid; the
    # exact native macro pass continues independently in the background.
    source = str(normalized["morphology"].get("relief_source", RELIEF_SOURCE_DEFAULT))
    if source not in {RELIEF_SOURCE_DEFAULT, RELIEF_SOURCE_CUSTOM_LEGACY}:
        raw = np.zeros((int(side), int(side)), dtype=np.uint8)
        report = build_noise_lab(raw, normalized, seed=int(seed))
        if lab_sink is not None:
            lab_sink["report"] = report
        noise = report.composed_height.astype(np.int16) + int(NATIVE_NOISE_MINIMUM)
        noise = apply_archetype_noise_morphology(
            noise,
            normalized,
            seed=int(seed),
            include_noise_layers=False,
        )
        return noise, classify_macro(noise, normalized)
    noise = generate_archetype_noise_preview(
        normalized,
        side,
        seed,
        mirror_mode,
        noise_cache=noise_cache,
        lab_sink=lab_sink,
    )
    return noise, classify_macro(noise, normalized)


def noise_rgb(noise: np.ndarray) -> np.ndarray:
    """Convert the height/noise field into a neutral grayscale raster."""

    values = np.asarray(noise, dtype=np.int16)
    values = np.clip(
        values - int(NATIVE_NOISE_MINIMUM),
        0,
        int(NATIVE_NOISE_MAXIMUM - NATIVE_NOISE_MINIMUM),
    ).astype(np.uint8)
    return np.repeat(values[:, :, None], 3, axis=2)


def raw_height_rgb(height: np.ndarray) -> np.ndarray:
    """Convert a pre-normalization raw height field into grayscale RGB."""

    values = np.asarray(height, dtype=np.int16)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("La composition brute doit être une matrice carrée")
    values = np.clip(values, 0, 255).astype(np.uint8)
    return np.repeat(values[:, :, None], 3, axis=2)


def noise_delta_rgb(delta: np.ndarray) -> np.ndarray:
    """Render signed component deltas as blue-down / red-up diagnostics."""

    values = np.asarray(delta, dtype=np.float32)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("La contribution de bruit doit être une matrice carrée")
    maximum = float(np.max(np.abs(values))) if values.size else 0.0
    normalized = np.zeros(values.shape, dtype=np.float32)
    if maximum > 1e-6:
        normalized = np.clip(np.abs(values) / maximum, 0.0, 1.0)
    rgb = np.full((*values.shape, 3), 32, dtype=np.uint8)
    positive = values > 1e-6
    negative = values < -1e-6
    intensity = np.rint(70.0 + normalized * 185.0).astype(np.uint8)
    rgb[positive, 0] = intensity[positive]
    rgb[positive, 1] = np.maximum(24, 110 - intensity[positive] // 3)
    rgb[positive, 2] = 32
    rgb[negative, 0] = 32
    rgb[negative, 1] = np.maximum(40, 150 - intensity[negative] // 3)
    rgb[negative, 2] = intensity[negative]
    return rgb


def macro_rgb(macro: np.ndarray) -> np.ndarray:
    """Convert the five macro classes into a display raster."""

    classes = np.asarray(macro, dtype=np.uint8)
    if classes.ndim != 2 or classes.shape[0] != classes.shape[1]:
        raise ValueError("La carte macro doit être une matrice carrée")
    rgb = np.zeros((*classes.shape, 3), dtype=np.uint8)
    for value, colour in enumerate(MACRO_PALETTE):
        rgb[classes == value] = colour
    return rgb


def macro_percentages(macro: np.ndarray) -> tuple[float, ...]:
    """Return the five macro-class shares as percentages."""

    classes = np.asarray(macro, dtype=np.uint8)
    if classes.ndim != 2 or classes.shape[0] != classes.shape[1]:
        raise ValueError("La carte macro doit être une matrice carrée")
    counts = np.bincount(classes.ravel(), minlength=MACRO_CLASS_COUNT)
    total = max(1, int(classes.size))
    return tuple(float(count) * 100.0 / total for count in counts[:MACRO_CLASS_COUNT])


def project_preview_rgb(rgb: np.ndarray, projection: str = "square") -> np.ndarray:
    """Project a square preview using the application's current raster view."""

    values = np.asarray(rgb, dtype=np.uint8)
    if projection == "square":
        return values.copy()
    if projection != "parallelogram":
        raise ValueError(f"Projection inconnue : {projection}")
    if values.ndim != 3 or values.shape[2] != 3:
        raise ValueError("Le rendu de prévisualisation doit être RGB")
    height, width, _channels = values.shape
    expanded = np.repeat(np.repeat(values, 2, axis=0), 2, axis=1)
    canvas = np.zeros(
        (2 * height, 2 * width + (height - 1), 3),
        dtype=np.uint8,
    )
    for row in range(height):
        shift = height - 1 - row
        canvas[2 * row : 2 * row + 2, shift : shift + 2 * width] = expanded[
            2 * row : 2 * row + 2
        ]
    return canvas


__all__ = (
    "MACRO_BEACH",
    "MACRO_CLASS_COUNT",
    "MACRO_GRASS",
    "MACRO_MOUNTAIN",
    "MACRO_PALETTE",
    "MACRO_SNOW",
    "MACRO_WATER",
    "ArchetypePreview",
    "classify_macro",
    "generate_archetype_preview",
    "macro_rgb",
    "macro_percentages",
    "noise_rgb",
    "raw_height_rgb",
    "project_preview_rgb",
)
