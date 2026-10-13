"""The complete island source followed by the shared composition controls.

The provider uses its preset calibration. User thresholds classify the result;
they do not force the provider to rebuild mountains or keep every island dry.
"""

from dataclasses import dataclass
from collections.abc import Callable, Mapping

import numpy as np

from .large_islands import generate_independent_islands
from .island_amplitude import resolve_island_profile, calibrated_thresholds, island_radius
from .morphology import (
    NoiseLabReport, apply_archetype_morphology, build_noise_lab,
    has_active_noise_layers, has_active_mask_layers,
)
from .profiles import (
    NATIVE_NOISE_MINIMUM, RELIEF_SOURCE_LARGE_ISLANDS_R21,
    RELIEF_SOURCE_TEAM_ISLANDS, RELIEF_SOURCE_CONTINENTAL, ISLAND_RELIEF_SOURCES,
    default_archetype_profile, normalize_archetype_profile,
)
from .island_teams import group_players_by_team, player_island_labels


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
    player_teams=(),
) -> IslandSourceFields:
    """Build one authoritative field for both preview and terrain engines."""

    normalized = normalize_archetype_profile(
        profile, archetype_key=str(profile.get("archetype_key", "continental")),
    )
    normalized = resolve_island_profile(
        normalized, side, players, player_teams=player_teams,
    )
    continental = normalized["morphology"]["relief_source"] == RELIEF_SOURCE_CONTINENTAL
    preset = default_archetype_profile("large_islands")
    thresholds = preset["relief"]
    amplitude = normalized["morphology"]["island_amplitude_percent"] / 100.
    team_groups = (
        group_players_by_team(int(players), player_teams)
        if normalized["morphology"]["relief_source"] == RELIEF_SOURCE_TEAM_ISLANDS
        else None
    )
    island_player_counts = [len(group) for group in team_groups] if team_groups is not None else None
    continental_land_target = None
    if continental:
        from .large_islands import _continental_land_percent, _continental_ocean_land_percent
        continental_land_target = _continental_ocean_land_percent(side)
        land_cells = side * side * _continental_land_percent(side) / 100.
        # Physical scale units replace player count for a shared continental field.
        island_player_counts = [max(2, min(8, round(land_cells / 60_000)))]
    mountain, snow = calibrated_thresholds(
        0, 140, 200, amplitude,
        island_radius(side, 1, [1]) if continental else island_radius(side, players, island_player_counts),
    )
    thresholds.update(mountain_threshold=mountain, snow_threshold=snow)
    stages = {}
    source_height, labels, report = generate_independent_islands(
        np.zeros((int(side), int(side)), dtype=np.uint8),
        players=1 if continental else len(team_groups) if team_groups is not None else int(players), seed=int(seed),
        water_threshold=thresholds["water_threshold"],
        mountain_threshold=thresholds["mountain_threshold"],
        snow_threshold=thresholds["snow_threshold"],
        native_relaxation=native_relaxation, stage_sink=stages, amplitude=amplitude,
        variant_r21=(normalized["morphology"]["relief_source"] == RELIEF_SOURCE_LARGE_ISLANDS_R21),
        island_player_counts=island_player_counts,
        target_land_percent=continental_land_target,
    )
    if continental:
        report.update(continental_source=True, physical_relief_scale_units=island_player_counts[0],
                      requested_players=int(players), preset_features_required=False)
        report.update(
            land_target_basis="continental_ocean_calibrated_before_lakes",
            continental_ocean_land_correction_percent=(
                continental_land_target - report["continental_reference_land_percent"]
            ),
        )
    if team_groups is not None:
        report.update(
            team_islands=True,
            player_island_labels=player_island_labels(team_groups, int(players)),
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
        if source_mask_active or any(m.get("target") == "source" and m["enabled"] and m["strength_percent"] > 0 for m in morphology["mask_layers"][:morphology["mask_layer_count"]]):
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
    report["preset_island_contract"] = bool(preserves_layout and not continental)
    report["preset_features_required"] = bool(
        not continental and preserves_layout and normalized["relief"] == thresholds
    )
    return IslandSourceFields(
        height=height, noise=noise, source_noise=source_noise,
        source_labels=labels,
        # Team Islands needs its source partition to keep every player's start
        # on the intended island when editable relief layers are active. Any
        # resulting merges or missing land are still checked on the final map.
        topology_labels=(
            labels if not continental and (preserves_layout or team_groups is not None) else None
        ),
        report=report, noise_lab=lab, local_relief=stages["local_relief"],
    )
