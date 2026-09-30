"""Deterministic target matrix and provider qualification for archetypes.

This module is deliberately diagnostic.  It does not alter a profile, add a
provider or decide where starts/resources/objects are placed.  It measures the
same completed macro preview that the Archetype tab displays so the next
provider comparison has explicit, reproducible gates instead of visual guesswork.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass

import numpy as np

from ..core.request import (
    NATIVE_GAME_MAX_SIDE,
    NATIVE_GAME_MIN_SIDE,
    NATIVE_PLAYER_LIMITS,
)
from .previews import (
    MACRO_MOUNTAIN,
    MACRO_SNOW,
    MACRO_WATER,
    ArchetypePreview,
    generate_archetype_preview,
    macro_percentages,
)
from .morphology import generate_mask_component_previews
from .profiles import (
    MASK_LAYER_MANUAL_GRID_SIDE,
    RELIEF_SOURCE_OPTIONS,
    continental_noise_calibration_profile,
    default_archetype_profile,
    mask_layer_parameters,
    normalize_archetype_profile,
)

_HEX_NEIGHBOURS = ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))

# These are representative in-game sizes for the first comparison pass.  The
# complete native range remains in the matrix so a later qualification run can
# expand from the representative set without redefining its targets.
QUALIFICATION_SIZES: tuple[int, ...] = tuple(
    side
    for side in NATIVE_PLAYER_LIMITS
    if NATIVE_GAME_MIN_SIDE <= side <= NATIVE_GAME_MAX_SIDE
)
QUALIFICATION_REPRESENTATIVE_SIZES: tuple[int, ...] = (384, 512, 768)
QUALIFICATION_MIRROR_MODES: tuple[int, ...] = (0, 3)
QUALIFICATION_DEFAULT_SEED = 20260920
MANUAL_MASK_QUALIFICATION_SIZES: tuple[int, ...] = QUALIFICATION_REPRESENTATIVE_SIZES
MANUAL_MASK_QUALIFICATION_SEEDS: tuple[int, ...] = (20260920, 20260921, 20260922)
MANUAL_MASK_QUALIFICATION_MIRROR_MODES: tuple[int, ...] = (0, 1, 2, 3)
MANUAL_MASK_COVERAGE_TOLERANCE_PERCENT = 8.0

# R51 keeps the native Continental contract and calibrates only the two
# morphology controls that are actually applied to the native source.  The
# frame/falloff controls remain identity values here because they belong to
# finite non-native providers, not to the protected native midpoint field.
CONTINENTAL_CALIBRATION_SIZES: tuple[int, ...] = QUALIFICATION_REPRESENTATIVE_SIZES
CONTINENTAL_CALIBRATION_SEEDS: tuple[int, ...] = MANUAL_MASK_QUALIFICATION_SEEDS
CONTINENTAL_CALIBRATION_MIRROR_MODES: tuple[int, ...] = QUALIFICATION_MIRROR_MODES
CONTINENTAL_CALIBRATION_SHAPE_SCALE_PERCENT = 96
CONTINENTAL_CALIBRATION_RELIEF_CONTRAST_PERCENT = 105
CONTINENTAL_CALIBRATION_PROFILE_NAME = "Continental Custom R51 — relief compact"


@dataclass(frozen=True, slots=True)
class ArchetypeTargetSpec:
    """Macro target and first-pass preview gates for one archetype family."""

    key: str
    label: str
    topology_goal: str
    implemented: bool
    land_share_min_percent: float
    land_share_max_percent: float
    largest_mass_min_percent: float
    edge_water_min_percent: float
    coast_contact_max_percent: float
    relief_share_min_percent: float
    relief_share_max_percent: float
    mass_count_guidance: str

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "label": self.label,
            "topology_goal": self.topology_goal,
            "implemented": self.implemented,
            "land_share_percent": [
                self.land_share_min_percent,
                self.land_share_max_percent,
            ],
            "largest_mass_min_percent": self.largest_mass_min_percent,
            "edge_water_min_percent": self.edge_water_min_percent,
            "coast_contact_max_percent": self.coast_contact_max_percent,
            "relief_share_percent": [
                self.relief_share_min_percent,
                self.relief_share_max_percent,
            ],
            "mass_count_guidance": self.mass_count_guidance,
        }


ARCHETYPE_TARGETS: tuple[ArchetypeTargetSpec, ...] = (
    ArchetypeTargetSpec(
        key="continental",
        label="Continental",
        topology_goal="Une masse terrestre principale, séparée de l’océan par une côte continue.",
        implemented=True,
        land_share_min_percent=35.0,
        land_share_max_percent=85.0,
        largest_mass_min_percent=80.0,
        edge_water_min_percent=100.0,
        coast_contact_max_percent=25.0,
        relief_share_min_percent=2.0,
        relief_share_max_percent=45.0,
        mass_count_guidance="Une masse dominante ; les petites composantes restent un diagnostic, pas un gate dur.",
    ),
    ArchetypeTargetSpec(
        key="large_islands",
        label="Grandes îles",
        topology_goal="Plusieurs grandes masses insulaires séparées et jouables.",
        implemented=False,
        land_share_min_percent=25.0,
        land_share_max_percent=75.0,
        largest_mass_min_percent=35.0,
        edge_water_min_percent=100.0,
        coast_contact_max_percent=40.0,
        relief_share_min_percent=2.0,
        relief_share_max_percent=50.0,
        mass_count_guidance="Plusieurs masses de taille comparable ; le nombre exact sera calibré sur les cartes de référence.",
    ),
    ArchetypeTargetSpec(
        key="small_islands",
        label="Petites îles",
        topology_goal="Un archipel de nombreuses masses plus petites, sans confettis injouables.",
        implemented=False,
        land_share_min_percent=15.0,
        land_share_max_percent=65.0,
        largest_mass_min_percent=10.0,
        edge_water_min_percent=100.0,
        coast_contact_max_percent=60.0,
        relief_share_min_percent=1.0,
        relief_share_max_percent=55.0,
        mass_count_guidance="Nombreuses masses, avec une taille minimale à définir avant le générateur dédié.",
    ),
)

_TARGETS_BY_KEY = {target.key: target for target in ARCHETYPE_TARGETS}


@dataclass(frozen=True, slots=True)
class QualificationMetrics:
    """Measured values from one completed deterministic macro preview."""

    side: int
    seed: int
    mirror_mode: int
    source: str
    macro_class_percentages: tuple[float, ...]
    macro_land_percent: float
    edge_water_percent: float
    mass_count: int
    largest_mass_share_percent: float
    land_coast_contact_percent: float
    mountain_snow_percent: float
    raw_source_land_percent: float | None
    raw_source_height_percentiles: tuple[float, float, float] | None

    def to_dict(self) -> dict[str, object]:
        return {
            "side": self.side,
            "seed": self.seed,
            "mirror_mode": self.mirror_mode,
            "source": self.source,
            "macro_class_percentages": list(self.macro_class_percentages),
            "macro_land_percent": self.macro_land_percent,
            "edge_water_percent": self.edge_water_percent,
            "mass_count": self.mass_count,
            "largest_mass_share_percent": self.largest_mass_share_percent,
            "land_coast_contact_percent": self.land_coast_contact_percent,
            "mountain_snow_percent": self.mountain_snow_percent,
            "raw_source_land_percent": self.raw_source_land_percent,
            "raw_source_height_percentiles": (
                list(self.raw_source_height_percentiles)
                if self.raw_source_height_percentiles is not None
                else None
            ),
        }


@dataclass(frozen=True, slots=True)
class QualificationCheck:
    """One transparent comparison gate."""

    key: str
    value: float
    minimum: float | None
    maximum: float | None
    passed: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "value": self.value,
            "minimum": self.minimum,
            "maximum": self.maximum,
            "passed": self.passed,
        }


@dataclass(frozen=True, slots=True)
class ProviderQualification:
    """Qualification result for one provider/size/seed/mirror combination."""

    target: str
    metrics: QualificationMetrics
    checks: tuple[QualificationCheck, ...]
    status: str

    @property
    def passed(self) -> bool:
        return self.status == "PASS"

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "status": self.status,
            "metrics": self.metrics.to_dict(),
            "checks": [check.to_dict() for check in self.checks],
        }


@dataclass(frozen=True, slots=True)
class ManualMaskQualificationCase:
    """One deterministic manual-mask case in the R50 qualification matrix."""

    side: int
    seed: int
    mirror_mode: int
    signal_coverage_percent: float
    signal_min: int
    signal_max: int
    preview_changed_percent: float
    outside_cells_percent: float
    outside_noise_range: float | None
    mirror_delta_percent: float
    macro_land_percent: float
    edge_water_percent: float
    mass_count: int
    largest_mass_share_percent: float
    checks: tuple[QualificationCheck, ...]
    status: str

    @property
    def passed(self) -> bool:
        return self.status == "PASS"

    def to_dict(self) -> dict[str, object]:
        return {
            "side": self.side,
            "seed": self.seed,
            "mirror_mode": self.mirror_mode,
            "signal_coverage_percent": self.signal_coverage_percent,
            "signal_min": self.signal_min,
            "signal_max": self.signal_max,
            "preview_changed_percent": self.preview_changed_percent,
            "outside_cells_percent": self.outside_cells_percent,
            "outside_noise_range": self.outside_noise_range,
            "mirror_delta_percent": self.mirror_delta_percent,
            "macro_land_percent": self.macro_land_percent,
            "edge_water_percent": self.edge_water_percent,
            "mass_count": self.mass_count,
            "largest_mass_share_percent": self.largest_mass_share_percent,
            "status": self.status,
            "checks": [check.to_dict() for check in self.checks],
        }


@dataclass(frozen=True, slots=True)
class ContinentalStartQualificationCase:
    """One R51 generation/start gate for a calibrated Continental profile."""

    mode: str
    side: int
    players: int
    seed: int
    mirror_mode: int
    hard_validation_total: int
    hard_validation_passed: int
    failed_hard_validations: tuple[str, ...]
    start_count: int
    unique_start_count: int
    starts_in_bounds: bool
    startable_mass_passed: bool | None
    grass_mass_count: int | None
    largest_grass_mass_share_percent: float | None
    checks: tuple[QualificationCheck, ...]
    status: str
    error: str | None = None

    @property
    def passed(self) -> bool:
        return self.status == "PASS"

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "side": self.side,
            "players": self.players,
            "seed": self.seed,
            "mirror_mode": self.mirror_mode,
            "hard_validation_total": self.hard_validation_total,
            "hard_validation_passed": self.hard_validation_passed,
            "failed_hard_validations": list(self.failed_hard_validations),
            "start_count": self.start_count,
            "unique_start_count": self.unique_start_count,
            "starts_in_bounds": self.starts_in_bounds,
            "startable_mass_passed": self.startable_mass_passed,
            "grass_mass_count": self.grass_mass_count,
            "largest_grass_mass_share_percent": self.largest_grass_mass_share_percent,
            "status": self.status,
            "error": self.error,
            "checks": [check.to_dict() for check in self.checks],
        }


def manual_mask_fixture_grid() -> np.ndarray:
    """Return a deterministic asymmetric grayscale mask for qualification.

    This is a numeric fixture, not an artwork asset.  It deliberately combines
    a broad lobe, a smaller lobe and a curved stroke so mirror transforms and
    resampling can be measured without relying on a hand-picked image file.
    """

    side = MASK_LAYER_MANUAL_GRID_SIDE
    rows, columns = np.indices((side, side), dtype=np.float32)
    x = (columns - (side - 1) / 2.0) / ((side - 1) / 2.0)
    y = (rows - (side - 1) / 2.0) / ((side - 1) / 2.0)
    left = np.exp(-(((x + 0.25) / 0.48) ** 2 + ((y + 0.08) / 0.56) ** 2))
    lobe = 0.78 * np.exp(
        -(((x - 0.38) / 0.25) ** 2 + ((y - 0.28) / 0.30) ** 2)
    )
    curve = 0.52 * np.exp(
        -(((y - (0.18 * x + 0.08 * np.sin(x * 4.0))) / 0.13) ** 2)
    )
    curve *= np.exp(-((x / 0.88) ** 4))
    field = np.clip(np.maximum.reduce((left, lobe, curve)), 0.0, 1.0)
    return np.rint(field * 255.0).astype(np.uint8)


def manual_mask_profile(
    grid: np.ndarray,
    profile: Mapping[str, object] | None = None,
    *,
    operation: str = "blend",
    strength_percent: int = 100,
    settings: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Build a normalized Continental profile with one active manual mask."""

    array = np.asarray(grid)
    expected = MASK_LAYER_MANUAL_GRID_SIDE * MASK_LAYER_MANUAL_GRID_SIDE
    if array.size != expected:
        raise ValueError(
            "La grille de qualification doit contenir "
            f"{expected} niveaux de gris"
        )
    try:
        array = np.rint(array).astype(np.int16, copy=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("La grille de qualification doit être numérique") from exc
    if np.any(array < 0) or np.any(array > 255):
        raise ValueError("La grille de qualification doit rester entre 0 et 255")
    array = array.reshape(MASK_LAYER_MANUAL_GRID_SIDE, MASK_LAYER_MANUAL_GRID_SIDE)

    source_profile = (
        profile if profile is not None else default_archetype_profile("continental")
    )
    archetype_key = (
        str(source_profile.get("archetype_key", "continental"))
        if isinstance(source_profile, Mapping)
        else "continental"
    )
    base = normalize_archetype_profile(
        source_profile,
        archetype_key=archetype_key,
    )
    morphology = deepcopy(base["morphology"])
    layers = deepcopy(morphology["mask_layers"])
    for layer in layers:
        layer["enabled"] = False
    layer = layers[0]
    layer.update(
        {
            "enabled": True,
            "type": "manual",
            "operation": str(operation),
            "strength_percent": int(strength_percent),
            "provider_settings": {"grid": array.reshape(-1).tolist()},
        }
    )
    common_settings = dict(layer.get("settings", {}))
    common_settings.update(dict(settings or {}))
    layer["settings"] = common_settings
    layers[0] = layer
    morphology["mask_layer_count"] = 1
    morphology["mask_layers"] = layers
    base["morphology"] = morphology
    return normalize_archetype_profile(base, archetype_key=archetype_key)


def manual_mask_report(
    profile: Mapping[str, object],
    *,
    sizes: Sequence[int] = MANUAL_MASK_QUALIFICATION_SIZES,
    seeds: Sequence[int] = MANUAL_MASK_QUALIFICATION_SEEDS,
    mirror_modes: Sequence[int] = MANUAL_MASK_QUALIFICATION_MIRROR_MODES,
) -> dict[str, object]:
    """Qualify one manual mask over sizes, seeds and native mirror modes."""

    normalized = normalize_archetype_profile(
        profile,
        archetype_key=str(profile.get("archetype_key", "continental")),
    )
    layers = mask_layer_parameters(normalized)
    manual_indices = [
        index
        for index, layer in enumerate(layers)
        if str(layer.get("type")) == "manual"
        and bool(layer.get("enabled", False))
        and int(layer.get("strength_percent", 0)) > 0
    ]
    if not manual_indices:
        raise ValueError("Le profil doit contenir un masque manuel actif")
    manual_index = manual_indices[0]
    provider_settings = layers[manual_index].get("provider_settings", {})
    raw_grid = provider_settings.get("grid") if isinstance(provider_settings, Mapping) else None
    if not isinstance(raw_grid, (list, tuple)):
        raise ValueError("Le masque manuel actif ne contient pas de grille")
    grid = np.asarray(raw_grid, dtype=np.uint8).reshape(
        MASK_LAYER_MANUAL_GRID_SIDE,
        MASK_LAYER_MANUAL_GRID_SIDE,
    )

    normalized_sizes = tuple(int(side) for side in sizes)
    normalized_seeds = tuple(int(seed) for seed in seeds)
    normalized_mirrors = tuple(int(mode) for mode in mirror_modes)
    if not normalized_sizes or not normalized_seeds or not normalized_mirrors:
        raise ValueError("La matrice de qualification ne peut pas être vide")
    if any(side < 16 for side in normalized_sizes):
        raise ValueError("Les tailles de qualification doivent être au moins 16")
    if any(mode not in (0, 1, 2, 3) for mode in normalized_mirrors):
        raise ValueError("Les miroirs de qualification doivent être compris entre 0 et 3")

    neutral_profile = deepcopy(normalized)
    neutral_morphology = deepcopy(neutral_profile["morphology"])
    neutral_layers = deepcopy(neutral_morphology["mask_layers"])
    for layer in neutral_layers:
        layer["enabled"] = False
    neutral_morphology["mask_layers"] = neutral_layers
    neutral_profile["morphology"] = neutral_morphology

    signal_cache: dict[tuple[int, int, int], np.ndarray] = {}
    baseline_signals: dict[tuple[int, int], np.ndarray] = {}
    neutral_cache = {}
    cases: list[ManualMaskQualificationCase] = []
    signals_by_side_mirror: dict[tuple[int, int], list[np.ndarray]] = {}
    coverage_by_seed_mirror: dict[tuple[int, int], list[float]] = {}

    def signal_for(side: int, seed: int, mirror_mode: int) -> np.ndarray:
        key = (int(side), int(seed), int(mirror_mode))
        if key not in signal_cache:
            components = generate_mask_component_previews(
                normalized,
                int(side),
                int(seed),
                mirror_mode=int(mirror_mode),
            )
            signal_cache[key] = np.asarray(components[manual_index], dtype=np.uint8)
        return signal_cache[key]

    def baseline_signal(side: int, seed: int) -> np.ndarray:
        key = (int(side), int(seed))
        if key not in baseline_signals:
            baseline_signals[key] = signal_for(side, seed, 0)
        return baseline_signals[key]

    for side in normalized_sizes:
        for seed in normalized_seeds:
            for mirror_mode in normalized_mirrors:
                signal = signal_for(side, seed, mirror_mode)
                neutral_key = (side, seed, mirror_mode)
                neutral = neutral_cache.get(neutral_key)
                if neutral is None:
                    neutral = generate_archetype_preview(
                        neutral_profile,
                        side,
                        seed,
                        mirror_mode,
                    )
                    neutral_cache[neutral_key] = neutral
                masked = generate_archetype_preview(
                    normalized,
                    side,
                    seed,
                    mirror_mode,
                )
                metrics = measure_preview(masked)
                outside = signal == 0
                outside_values = masked.noise[outside]
                outside_range = (
                    float(np.max(outside_values) - np.min(outside_values))
                    if outside_values.size
                    else None
                )
                changed_percent = float(
                    np.mean(masked.noise != neutral.noise) * 100.0
                )
                coverage_percent = float(np.mean(signal > 0) * 100.0)
                mirror_delta_percent = float(
                    np.mean(signal != baseline_signal(side, seed)) * 100.0
                )
                checks = (
                    _check("signal_coverage", coverage_percent, minimum=1.0),
                    _check("signal_minimum", float(signal.min()), minimum=0.0, maximum=255.0),
                    _check("signal_maximum", float(signal.max()), minimum=0.0, maximum=255.0),
                    _check(
                        "signal_dynamic_range",
                        float(int(signal.max()) - int(signal.min())),
                        minimum=1.0,
                    ),
                    _check("preview_effect", changed_percent, minimum=0.01),
                    _check(
                        "outside_variation",
                        float(outside_range or 0.0),
                        minimum=0.0 if outside_range is None else 1.0,
                    ),
                    _check("native_edge_water", metrics.edge_water_percent, minimum=100.0, maximum=100.0),
                )
                case = ManualMaskQualificationCase(
                    side=side,
                    seed=seed,
                    mirror_mode=mirror_mode,
                    signal_coverage_percent=coverage_percent,
                    signal_min=int(signal.min()),
                    signal_max=int(signal.max()),
                    preview_changed_percent=changed_percent,
                    outside_cells_percent=float(np.mean(outside) * 100.0),
                    outside_noise_range=outside_range,
                    mirror_delta_percent=mirror_delta_percent,
                    macro_land_percent=metrics.macro_land_percent,
                    edge_water_percent=metrics.edge_water_percent,
                    mass_count=metrics.mass_count,
                    largest_mass_share_percent=metrics.largest_mass_share_percent,
                    checks=checks,
                    status="PASS" if all(check.passed for check in checks) else "FAIL",
                )
                cases.append(case)
                signals_by_side_mirror.setdefault((side, mirror_mode), []).append(signal)
                coverage_by_seed_mirror.setdefault((seed, mirror_mode), []).append(
                    coverage_percent
                )

    deterministic_key = (
        normalized_sizes[0],
        normalized_seeds[0],
        normalized_mirrors[0],
    )
    deterministic_components = generate_mask_component_previews(
        normalized,
        deterministic_key[0],
        deterministic_key[1],
        mirror_mode=deterministic_key[2],
    )
    deterministic_signal = np.array_equal(
        signal_for(*deterministic_key),
        np.asarray(deterministic_components[manual_index], dtype=np.uint8),
    )
    seed_invariant_signal = all(
        all(np.array_equal(signals[0], other) for other in signals[1:])
        for signals in signals_by_side_mirror.values()
    )
    coverage_ranges = {
        f"{seed}:{mirror_mode}": float(max(values) - min(values))
        for (seed, mirror_mode), values in coverage_by_seed_mirror.items()
    }
    maximum_coverage_range = max(coverage_ranges.values(), default=0.0)
    scale_stable_coverage = maximum_coverage_range <= MANUAL_MASK_COVERAGE_TOLERANCE_PERCENT
    gates = (
        {
            "key": "deterministic_signal",
            "passed": bool(deterministic_signal),
        },
        {
            "key": "seed_invariant_signal",
            "passed": bool(seed_invariant_signal),
        },
        {
            "key": "scale_stable_coverage",
            "passed": bool(scale_stable_coverage),
            "maximum_coverage_range_percent": maximum_coverage_range,
            "tolerance_percent": MANUAL_MASK_COVERAGE_TOLERANCE_PERCENT,
        },
        {
            "key": "all_case_checks",
            "passed": all(case.passed for case in cases),
        },
    )
    gates_passed = sum(bool(gate["passed"]) for gate in gates)
    cases_passed = sum(case.passed for case in cases)
    return {
        "run": {
            "sizes": list(normalized_sizes),
            "seeds": list(normalized_seeds),
            "mirror_modes": list(normalized_mirrors),
            "manual_slot": manual_index + 1,
        },
        "grid": {
            "side": MASK_LAYER_MANUAL_GRID_SIDE,
            "minimum": int(grid.min()),
            "maximum": int(grid.max()),
            "coverage_percent": float(np.mean(grid > 0) * 100.0),
        },
        "cases": [case.to_dict() for case in cases],
        "gates": list(gates),
        "coverage_ranges_percent": coverage_ranges,
        "summary": {
            "rows": len(cases),
            "passed": cases_passed,
            "failed": len(cases) - cases_passed,
            "gates_passed": gates_passed,
            "gates_total": len(gates),
            "status": "PASS" if cases_passed == len(cases) and gates_passed == len(gates) else "FAIL",
        },
    }


def continental_calibration_profile(
    profile: Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Return the provisional R51 Continental profile under calibration.

    R51 deliberately derives from the protected native Continental contract.
    Only the two morphology controls consumed by the native source are tuned;
    the profile is not installed as a new Legacy or Upgraded preset.
    """

    source_profile = (
        profile if profile is not None else default_archetype_profile("continental")
    )
    archetype_key = (
        str(source_profile.get("archetype_key", "continental"))
        if isinstance(source_profile, Mapping)
        else "continental"
    )
    if archetype_key != "continental":
        raise ValueError("Le calibrage R51 attend le profil Continental")
    calibrated = normalize_archetype_profile(
        source_profile,
        archetype_key="continental",
    )
    morphology = deepcopy(calibrated["morphology"])
    morphology.update(
        {
            "shape_scale_percent": CONTINENTAL_CALIBRATION_SHAPE_SCALE_PERCENT,
            "relief_contrast_percent": CONTINENTAL_CALIBRATION_RELIEF_CONTRAST_PERCENT,
        }
    )
    calibrated["profile_name"] = CONTINENTAL_CALIBRATION_PROFILE_NAME
    calibrated["morphology"] = morphology
    return normalize_archetype_profile(calibrated, archetype_key="continental")


def _calibration_player_cases(
    side: int,
    players: Sequence[int] | None,
) -> tuple[int, ...]:
    if players is None:
        return qualification_player_cases(int(side))
    values = tuple(dict.fromkeys(int(value) for value in players))
    maximum = int(NATIVE_PLAYER_LIMITS[int(side)])
    if not values or any(value < 1 or value > maximum for value in values):
        raise ValueError(
            f"Les joueurs de qualification doivent être compris entre 1 et {maximum} pour {side}²"
        )
    return values


def continental_calibration_report(
    profile: Mapping[str, object] | None = None,
    *,
    base_mode: str = "legacy",
    sizes: Sequence[int] = CONTINENTAL_CALIBRATION_SIZES,
    seeds: Sequence[int] = CONTINENTAL_CALIBRATION_SEEDS,
    mirror_modes: Sequence[int] = CONTINENTAL_CALIBRATION_MIRROR_MODES,
    players: Sequence[int] | None = None,
    profile_factory=None,
) -> dict[str, object]:
    """Qualify the provisional R51 Continental profile and its player starts.

    The macro rows retain the raw deterministic preview checks from R27/R50
    and pass the R51 gate when the calibrated profile introduces no new
    failed check versus the native baseline.  This keeps native baseline
    warnings visible without treating them as calibration regressions.  The
    start rows run the selected Custom route and gate hard validations, exact
    start count, uniqueness and map bounds.  ``startable_mass`` remains a
    visible soft diagnostic because the existing native start solver reports
    it as non-hard and its occasional warnings must not be hidden as passes.
    """

    normalized_mode = str(base_mode)
    if normalized_mode not in {"legacy", "upgraded"}:
        raise ValueError("Le calibrage Continental accepte seulement legacy ou upgraded")
    normalized_sizes = tuple(int(side) for side in sizes)
    normalized_seeds = tuple(int(seed) for seed in seeds)
    normalized_mirrors = tuple(int(mode) for mode in mirror_modes)
    if not normalized_sizes or not normalized_seeds or not normalized_mirrors:
        raise ValueError("La matrice de calibrage Continental ne peut pas être vide")
    if any(side not in NATIVE_PLAYER_LIMITS for side in normalized_sizes):
        raise ValueError("Les tailles de calibrage doivent appartenir à la matrice native")
    if any(mode not in (0, 1, 2, 3) for mode in normalized_mirrors):
        raise ValueError("Les miroirs de calibrage doivent être compris entre 0 et 3")

    selected_profile_factory = profile_factory or continental_calibration_profile
    if not callable(selected_profile_factory):
        raise TypeError("profile_factory doit être appelable")
    calibrated = selected_profile_factory(profile)
    baseline = default_archetype_profile("continental")
    macro_results: list[dict[str, object]] = []
    for side in normalized_sizes:
        for seed in normalized_seeds:
            for mirror_mode in normalized_mirrors:
                calibrated_result = qualify_preview(
                    calibrated,
                    side,
                    seed,
                    mirror_mode,
                    target_key="continental",
                )
                baseline_result = qualify_preview(
                    baseline,
                    side,
                    seed,
                    mirror_mode,
                    target_key="continental",
                )
                row = calibrated_result.to_dict()
                row["case"] = {
                    "side": side,
                    "seed": seed,
                    "mirror_mode": mirror_mode,
                }
                baseline_row = baseline_result.to_dict()
                calibrated_failed_checks = {
                    str(check["key"])
                    for check in row["checks"]
                    if not bool(check["passed"])
                }
                baseline_failed_checks = {
                    str(check["key"])
                    for check in baseline_row["checks"]
                    if not bool(check["passed"])
                }
                new_failed_checks = sorted(
                    calibrated_failed_checks - baseline_failed_checks
                )
                row["qualification_status"] = row["status"]
                row["baseline_status"] = baseline_row["status"]
                row["baseline_failed_checks"] = sorted(baseline_failed_checks)
                row["new_failed_checks"] = new_failed_checks
                row["inherited_baseline_warning"] = bool(
                    row["qualification_status"] != "PASS"
                    and not new_failed_checks
                    and baseline_row["status"] != "PASS"
                )
                row["macro_gate_passed"] = not new_failed_checks
                row["status"] = "PASS" if row["macro_gate_passed"] else "FAIL"
                row["baseline_metrics"] = baseline_result.metrics.to_dict()
                row["delta_metrics"] = {
                    "macro_land_percent": (
                        calibrated_result.metrics.macro_land_percent
                        - baseline_result.metrics.macro_land_percent
                    ),
                    "largest_mass_share_percent": (
                        calibrated_result.metrics.largest_mass_share_percent
                        - baseline_result.metrics.largest_mass_share_percent
                    ),
                    "mountain_snow_percent": (
                        calibrated_result.metrics.mountain_snow_percent
                        - baseline_result.metrics.mountain_snow_percent
                    ),
                    "mass_count": (
                        calibrated_result.metrics.mass_count
                        - baseline_result.metrics.mass_count
                    ),
                }
                macro_results.append(row)

    # These imports stay lazy: the catalogue is imported by the generation
    # facade while it is constructing its own engine modules.
    from ...application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
    from ..custom import build_custom_config
    from ..facade import MapGenerator

    generator = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)
    custom_config = build_custom_config(normalized_mode).with_archetype_profile(
        calibrated
    )
    start_results: list[ContinentalStartQualificationCase] = []
    soft_mass_warning_count = 0
    for side in normalized_sizes:
        player_cases = _calibration_player_cases(side, players)
        for seed in normalized_seeds:
            for mirror_mode in normalized_mirrors:
                for player_count in player_cases:
                    try:
                        output = generator.generate(
                            player_count,
                            seed,
                            mode="custom",
                            archetype="continental",
                            side=side,
                            mirror_mode=mirror_mode,
                            custom_config=custom_config,
                        )
                        hard = [
                            validation
                            for validation in output.validations
                            if validation.hard
                        ]
                        hard_passed = sum(validation.passed for validation in hard)
                        failed_hard = tuple(
                            str(validation.rule_id)
                            for validation in hard
                            if not validation.passed
                        )
                        starts = list(output.state.starts)
                        unique_start_count = len(set(starts))
                        starts_in_bounds = all(
                            0 <= int(x) < side and 0 <= int(y) < side
                            for x, y in starts
                        )
                        start_mass = output.state.metadata.get("startable_mass", {})
                        if isinstance(start_mass, Mapping):
                            startable_mass_passed = bool(
                                start_mass.get("all_starts_in_largest_grass_mass", False)
                            )
                            grass_mass_count = int(start_mass.get("grass_mass_count", 0))
                            largest_share = float(
                                start_mass.get("largest_grass_mass_share_percent", 0.0)
                            )
                        else:
                            startable_mass_passed = None
                            grass_mass_count = None
                            largest_share = None
                        if startable_mass_passed is False:
                            soft_mass_warning_count += 1
                        checks = (
                            _check(
                                "hard_validations",
                                float(hard_passed),
                                minimum=float(max(1, len(hard))),
                                maximum=float(len(hard)),
                            ),
                            _check(
                                "start_count",
                                float(len(starts)),
                                minimum=float(player_count),
                                maximum=float(player_count),
                            ),
                            _check(
                                "unique_starts",
                                float(unique_start_count),
                                minimum=float(player_count),
                                maximum=float(player_count),
                            ),
                            _check(
                                "starts_in_bounds",
                                1.0 if starts_in_bounds else 0.0,
                                minimum=1.0,
                                maximum=1.0,
                            ),
                        )
                        start_results.append(
                            ContinentalStartQualificationCase(
                                mode=normalized_mode,
                                side=side,
                                players=player_count,
                                seed=seed,
                                mirror_mode=mirror_mode,
                                hard_validation_total=len(hard),
                                hard_validation_passed=hard_passed,
                                failed_hard_validations=failed_hard,
                                start_count=len(starts),
                                unique_start_count=unique_start_count,
                                starts_in_bounds=starts_in_bounds,
                                startable_mass_passed=startable_mass_passed,
                                grass_mass_count=grass_mass_count,
                                largest_grass_mass_share_percent=largest_share,
                                checks=checks,
                                status="PASS" if all(check.passed for check in checks) else "FAIL",
                            )
                        )
                    except Exception as exc:  # pragma: no cover - exercised by matrix runs
                        checks = (
                            _check("hard_validations", 0.0, minimum=1.0),
                            _check(
                                "start_count",
                                0.0,
                                minimum=float(player_count),
                                maximum=float(player_count),
                            ),
                            _check("unique_starts", 0.0, minimum=float(player_count)),
                            _check("starts_in_bounds", 0.0, minimum=1.0, maximum=1.0),
                        )
                        start_results.append(
                            ContinentalStartQualificationCase(
                                mode=normalized_mode,
                                side=side,
                                players=player_count,
                                seed=seed,
                                mirror_mode=mirror_mode,
                                hard_validation_total=0,
                                hard_validation_passed=0,
                                failed_hard_validations=(),
                                start_count=0,
                                unique_start_count=0,
                                starts_in_bounds=False,
                                startable_mass_passed=None,
                                grass_mass_count=None,
                                largest_grass_mass_share_percent=None,
                                checks=checks,
                                status="FAIL",
                                error=f"{type(exc).__name__}: {exc}",
                            )
                        )

    start_dicts = [case.to_dict() for case in start_results]
    macro_passed = sum(bool(row["macro_gate_passed"]) for row in macro_results)
    macro_raw_passed = sum(
        row["qualification_status"] == "PASS" for row in macro_results
    )
    inherited_macro_warnings = sum(
        bool(row["inherited_baseline_warning"]) for row in macro_results
    )
    start_passed = sum(case.passed for case in start_results)
    deterministic_profile = (
        selected_profile_factory() == selected_profile_factory()
    )
    gates = (
        {
            "key": "macro_targets",
            "passed": macro_passed == len(macro_results),
        },
        {
            "key": "player_start_hard_gate",
            "passed": start_passed == len(start_results),
        },
        {
            "key": "profile_deterministic",
            "passed": deterministic_profile,
        },
    )
    gates_passed = sum(bool(gate["passed"]) for gate in gates)
    return {
        "run": {
            "base_mode": normalized_mode,
            "sizes": list(normalized_sizes),
            "seeds": list(normalized_seeds),
            "mirror_modes": list(normalized_mirrors),
            "players": list(players) if players is not None else "qualification_player_cases",
        },
        "profile": {
            "profile_name": calibrated["profile_name"],
            "morphology": deepcopy(calibrated["morphology"]),
            "relief": deepcopy(calibrated["relief"]),
            "mass": deepcopy(calibrated["mass"]),
            "coast": deepcopy(calibrated["coast"]),
        },
        "baseline_profile": {
            "profile_name": baseline["profile_name"],
            "morphology": deepcopy(baseline["morphology"]),
        },
        "macro_results": macro_results,
        "start_results": start_dicts,
        "gates": list(gates),
        "diagnostics": {
            "macro_gate_rule": "no_new_failures_vs_native_baseline",
            "macro_raw_passed": macro_raw_passed,
            "macro_inherited_baseline_warning_count": inherited_macro_warnings,
            "startable_mass_warning_count": soft_mass_warning_count,
            "startable_mass_is_soft": True,
        },
        "summary": {
            "macro_rows": len(macro_results),
            "macro_passed": macro_passed,
            "macro_failed": len(macro_results) - macro_passed,
            "start_rows": len(start_results),
            "start_passed": start_passed,
            "start_failed": len(start_results) - start_passed,
            "gates_passed": gates_passed,
            "gates_total": len(gates),
            "status": (
                "PASS"
                if macro_passed == len(macro_results)
                and start_passed == len(start_results)
                and gates_passed == len(gates)
                else "FAIL"
            ),
        },
    }


def continental_custom_report(
    profile: Mapping[str, object] | None = None,
    *,
    base_mode: str = "legacy",
    sizes: Sequence[int] = CONTINENTAL_CALIBRATION_SIZES,
    seeds: Sequence[int] = CONTINENTAL_CALIBRATION_SEEDS,
    mirror_modes: Sequence[int] = CONTINENTAL_CALIBRATION_MIRROR_MODES,
    players: Sequence[int] | None = None,
) -> dict[str, object]:
    """Qualify the named R64 noise-composition profile and player starts."""

    return continental_calibration_report(
        profile,
        base_mode=base_mode,
        sizes=sizes,
        seeds=seeds,
        mirror_modes=mirror_modes,
        players=players,
        profile_factory=lambda _profile=None: continental_noise_calibration_profile(),
    )


def target_spec(key: str = "continental") -> ArchetypeTargetSpec:
    """Return one target specification by stable key."""

    try:
        return _TARGETS_BY_KEY[str(key)]
    except KeyError as exc:
        raise ValueError(f"Cible d’archétype inconnue : {key}") from exc


def qualification_player_cases(side: int) -> tuple[int, ...]:
    """Return representative player counts including the native maximum."""

    maximum = int(NATIVE_PLAYER_LIMITS[int(side)])
    return tuple(dict.fromkeys((2, min(4, maximum), maximum)))


def target_matrix() -> dict[str, object]:
    """Return the versioned target matrix used by qualification tools."""

    return {
        "matrix_version": 1,
        "sizes": list(QUALIFICATION_SIZES),
        "representative_sizes": list(QUALIFICATION_REPRESENTATIVE_SIZES),
        "mirror_modes": list(QUALIFICATION_MIRROR_MODES),
        "player_cases": {
            str(side): list(qualification_player_cases(side))
            for side in QUALIFICATION_SIZES
        },
        "archetypes": [target.to_dict() for target in ARCHETYPE_TARGETS],
        "provider_gate_scope": "macro_preview",
        "deferred_gates": (
            "constructibilité",
            "starts",
            "ressources",
            "hydrologie détaillée",
            "éditeur et jeu",
        ),
    }


def _edge_cells(values: np.ndarray) -> np.ndarray:
    side = int(values.shape[0])
    if side <= 1:
        return values.reshape(-1)
    return np.concatenate(
        (
            values[0, :],
            values[-1, :],
            values[1:-1, 0],
            values[1:-1, -1],
        )
    )


def _touching_water(water: np.ndarray) -> np.ndarray:
    result = np.zeros(water.shape, dtype=bool)
    side = int(water.shape[0])
    for dr, dc in _HEX_NEIGHBOURS:
        r0, r1 = max(0, dr), min(side, side + dr)
        c0, c1 = max(0, dc), min(side, side + dc)
        sr0, sr1 = max(0, -dr), min(side, side - dr)
        sc0, sc1 = max(0, -dc), min(side, side - dc)
        result[r0:r1, c0:c1] |= water[sr0:sr1, sc0:sc1]
    return result


def measure_preview(preview: ArchetypePreview) -> QualificationMetrics:
    """Measure macro topology and raw-source diagnostics from a preview."""

    macro = np.asarray(preview.macro, dtype=np.uint8)
    if macro.ndim != 2 or macro.shape[0] != macro.shape[1]:
        raise ValueError("La macro de qualification doit être une matrice carrée")
    percentages = macro_percentages(macro)
    land = macro != MACRO_WATER
    water = ~land
    coast_cells = land & _touching_water(water)
    lab = getattr(preview, "noise_lab", None)
    return QualificationMetrics(
        side=int(preview.side),
        seed=int(preview.seed),
        mirror_mode=int(preview.mirror_mode),
        source=(
            str(lab.source_name)
            if lab is not None
            else "native_legacy"
        ),
        macro_class_percentages=tuple(float(value) for value in percentages),
        macro_land_percent=float(np.mean(land) * 100.0),
        edge_water_percent=float(np.mean(_edge_cells(macro) == MACRO_WATER) * 100.0),
        mass_count=int(preview.mass.mass_count) if preview.mass is not None else 0,
        largest_mass_share_percent=(
            float(preview.mass.largest_mass_share_percent)
            if preview.mass is not None
            else 0.0
        ),
        land_coast_contact_percent=(
            float(np.count_nonzero(coast_cells) * 100.0 / max(1, np.count_nonzero(land)))
        ),
        mountain_snow_percent=float(
            percentages[MACRO_MOUNTAIN] + percentages[MACRO_SNOW]
        ),
        raw_source_land_percent=(
            float(lab.source_land_percent) if lab is not None else None
        ),
        raw_source_height_percentiles=(
            tuple(float(value) for value in lab.source_height_percentiles)
            if lab is not None
            else None
        ),
    )


def _check(
    key: str,
    value: float,
    minimum: float | None = None,
    maximum: float | None = None,
) -> QualificationCheck:
    lower_ok = minimum is None or value >= minimum
    upper_ok = maximum is None or value <= maximum
    return QualificationCheck(
        key=key,
        value=float(value),
        minimum=minimum,
        maximum=maximum,
        passed=bool(lower_ok and upper_ok),
    )


def qualify_preview(
    profile: Mapping[str, object] | None,
    side: int,
    seed: int,
    mirror_mode: int = 0,
    *,
    target_key: str = "continental",
) -> ProviderQualification:
    """Generate and qualify one complete deterministic macro preview."""

    target = target_spec(target_key)
    if not target.implemented:
        raise NotImplementedError(
            f"La cible d’archétype {target.label} n’est pas encore implémentée"
        )
    preview = generate_archetype_preview(
        profile,
        int(side),
        int(seed),
        int(mirror_mode),
    )
    metrics = measure_preview(preview)
    checks = (
        _check(
            "macro_land_share",
            metrics.macro_land_percent,
            target.land_share_min_percent,
            target.land_share_max_percent,
        ),
        _check(
            "largest_mass_share",
            metrics.largest_mass_share_percent,
            target.largest_mass_min_percent,
            100.0,
        ),
        _check(
            "edge_water",
            metrics.edge_water_percent,
            target.edge_water_min_percent,
            100.0,
        ),
        _check(
            "coast_contact",
            metrics.land_coast_contact_percent,
            0.0,
            target.coast_contact_max_percent,
        ),
        _check(
            "mountain_snow_share",
            metrics.mountain_snow_percent,
            target.relief_share_min_percent,
            target.relief_share_max_percent,
        ),
    )
    return ProviderQualification(
        target=target.key,
        metrics=metrics,
        checks=checks,
        status="PASS" if all(check.passed for check in checks) else "FAIL",
    )


def qualify_providers(
    profile: Mapping[str, object] | None = None,
    *,
    sizes: Sequence[int] = QUALIFICATION_REPRESENTATIVE_SIZES,
    seed: int = QUALIFICATION_DEFAULT_SEED,
    mirror_mode: int = 0,
    sources: Sequence[str] = RELIEF_SOURCE_OPTIONS,
    target_key: str = "continental",
) -> tuple[ProviderQualification, ...]:
    """Qualify every requested source over a deterministic size slice."""

    base = deepcopy(dict(profile or default_archetype_profile(target_key)))
    morphology = dict(base.get("morphology", {}))
    results: list[ProviderQualification] = []
    for side in sizes:
        for source in sources:
            current = deepcopy(base)
            current_morphology = dict(morphology)
            current_morphology["relief_source"] = str(source)
            current["morphology"] = current_morphology
            results.append(
                qualify_preview(
                    current,
                    int(side),
                    int(seed),
                    int(mirror_mode),
                    target_key=target_key,
                )
            )
    return tuple(results)


def qualification_report(
    profile: Mapping[str, object] | None = None,
    *,
    sizes: Sequence[int] = QUALIFICATION_REPRESENTATIVE_SIZES,
    seed: int = QUALIFICATION_DEFAULT_SEED,
    mirror_mode: int = 0,
    sources: Sequence[str] = RELIEF_SOURCE_OPTIONS,
    target_key: str = "continental",
) -> dict[str, object]:
    """Return a JSON-ready matrix plus all measured provider rows."""

    results = qualify_providers(
        profile,
        sizes=sizes,
        seed=seed,
        mirror_mode=mirror_mode,
        sources=sources,
        target_key=target_key,
    )
    return {
        "matrix": target_matrix(),
        "run": {
            "target": target_key,
            "seed": int(seed),
            "mirror_mode": int(mirror_mode),
            "sizes": [int(side) for side in sizes],
            "sources": [str(source) for source in sources],
        },
        "results": [result.to_dict() for result in results],
        "summary": {
            "rows": len(results),
            "passed": sum(result.passed for result in results),
            "failed": sum(not result.passed for result in results),
        },
    }


__all__ = (
    "ARCHETYPE_TARGETS",
    "QUALIFICATION_DEFAULT_SEED",
    "QUALIFICATION_MIRROR_MODES",
    "QUALIFICATION_REPRESENTATIVE_SIZES",
    "QUALIFICATION_SIZES",
    "MANUAL_MASK_COVERAGE_TOLERANCE_PERCENT",
    "MANUAL_MASK_QUALIFICATION_MIRROR_MODES",
    "MANUAL_MASK_QUALIFICATION_SEEDS",
    "MANUAL_MASK_QUALIFICATION_SIZES",
    "CONTINENTAL_CALIBRATION_MIRROR_MODES",
    "CONTINENTAL_CALIBRATION_PROFILE_NAME",
    "CONTINENTAL_CALIBRATION_SEEDS",
    "CONTINENTAL_CALIBRATION_SHAPE_SCALE_PERCENT",
    "CONTINENTAL_CALIBRATION_RELIEF_CONTRAST_PERCENT",
    "CONTINENTAL_CALIBRATION_SIZES",
    "ArchetypeTargetSpec",
    "ContinentalStartQualificationCase",
    "ManualMaskQualificationCase",
    "ProviderQualification",
    "QualificationCheck",
    "QualificationMetrics",
    "manual_mask_fixture_grid",
    "manual_mask_profile",
    "manual_mask_report",
    "continental_calibration_profile",
    "continental_calibration_report",
    "continental_custom_report",
    "measure_preview",
    "qualification_player_cases",
    "qualification_report",
    "qualify_preview",
    "qualify_providers",
    "target_matrix",
    "target_spec",
)
