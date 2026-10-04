"""The complete island source followed by the shared composition controls.

The provider uses its preset calibration. User thresholds classify the result;
they do not force the provider to rebuild mountains or keep every island dry.
"""

from dataclasses import dataclass
from collections.abc import Callable, Mapping

import numpy as np

from .large_islands import generate_independent_islands
from .morphology import (
    NoiseLabReport, apply_archetype_morphology, build_noise_lab,
    has_active_noise_layers, has_active_mask_layers,
)
from .profiles import (
    NATIVE_NOISE_MINIMUM, RELIEF_SOURCE_LARGE_ISLANDS_R21, ISLAND_RELIEF_SOURCES,
    default_archetype_profile, normalize_archetype_profile,
)


@dataclass(frozen=True)
class IslandSourceFields:
    height: np.ndarray
    noise: np.ndarray
    source_noise: np.ndarray
    source_labels: np.ndarray
    topology_labels: np.ndarray | None
    report: dict
    noise_lab: NoiseLabReport | None
    local_relief: np.ndarray


def uses_island_source(profile: Mapping | None) -> bool:
    morphology = (profile or {}).get("morphology", {})
    return morphology.get("relief_source") in ISLAND_RELIEF_SOURCES


def generate_island_source(
    side: int, players: int, seed: int, profile: Mapping,
    *, native_relaxation: Callable | None,
) -> IslandSourceFields:
    """Build one authoritative field for both preview and terrain engines."""

    normalized = normalize_archetype_profile(
        profile, archetype_key=str(profile.get("archetype_key", "continental")),
    )
    preset = default_archetype_profile("large_islands")
    thresholds = preset["relief"]
    stages = {}
    source_height, labels, report = generate_independent_islands(
        np.zeros((int(side), int(side)), dtype=np.uint8),
        players=int(players), seed=int(seed),
        water_threshold=thresholds["water_threshold"],
        mountain_threshold=thresholds["mountain_threshold"],
        snow_threshold=thresholds["snow_threshold"],
        native_relaxation=native_relaxation, stage_sink=stages,
        variant_r21=(normalized["morphology"]["relief_source"] == RELIEF_SOURCE_LARGE_ISLANDS_R21),
    )
    morphology = normalized["morphology"]
    source_noise = source_height.astype(np.int16)
    source_noise[labels == 0] = NATIVE_NOISE_MINIMUM
    height, noise = source_height.copy(), source_noise.copy()
    source_mask = morphology["relief_source_mask"]
    source_mask_active = source_mask["type"] != "none" and source_mask["strength_percent"] > 0
    has_composition = (
        has_active_noise_layers(normalized)
        or has_active_mask_layers(normalized)
        or source_mask_active
    )
    has_morphology = (
        morphology["shape_scale_percent"] != 100
        or morphology["relief_contrast_percent"] != 100
    )
    lab = None
    if has_composition:
        # Convert the calibrated final source back to the common unsigned
        # source domain. No-op composition remains exactly the preset field.
        raw = np.clip(source_noise - NATIVE_NOISE_MINIMUM, 0, 255).astype(np.uint8)
        lab = build_noise_lab(raw, normalized, seed=int(seed))
        noise = lab.composed_height.astype(np.int16) + NATIVE_NOISE_MINIMUM
        height = np.clip(noise, 0, 255).astype(np.uint8)
        if source_mask_active:
            source_noise = lab.source_height.astype(np.int16) + NATIVE_NOISE_MINIMUM
    if has_morphology:
        height, noise = apply_archetype_morphology(
            height, noise, normalized, seed=int(seed), include_noise_layers=False,
        )
    if (has_composition or has_morphology) and native_relaxation is not None:
        height, passes = native_relaxation(height)
        report["composition_relaxation_passes"] = int(passes)
        # Keep signed submerged values, and use the relaxed heights on land.
        noise = np.where(height > 0, height, np.minimum(noise, 0)).astype(np.int16)
    preserves_layout = (
        not has_composition and not has_morphology
        and normalized["relief"]["water_threshold"] == thresholds["water_threshold"]
    )
    report["composed"] = bool(has_composition or has_morphology)
    report["preset_island_contract"] = bool(preserves_layout)
    report["preset_features_required"] = bool(
        preserves_layout and normalized["relief"] == thresholds
    )
    return IslandSourceFields(
        height=height, noise=noise, source_noise=source_noise,
        source_labels=labels, topology_labels=labels if preserves_layout else None,
        report=report, noise_lab=lab, local_relief=stages["local_relief"],
    )
