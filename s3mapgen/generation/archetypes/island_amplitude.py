"""Resolve visible island-source amplitude and classification thresholds."""

from functools import lru_cache
from math import pi, sqrt

from .profiles import (
    ISLAND_RELIEF_SOURCES,
    RELIEF_SOURCE_CONTINENTAL,
    RELIEF_SOURCE_TEAM_ISLANDS,
    normalize_archetype_profile,
)


def calibrated_thresholds(water, mountain, snow, amplitude, radius):
    correction = max(0.0, min(1.0, (100.0 - radius) / 40.0))
    compensation = min(amplitude, 1.0 - amplitude)
    mountain = round(
        water + (mountain - water) * amplitude + 30.0 * compensation * correction
    )
    snow = round(water + (snow - water) * amplitude + 16.0 * compensation * correction)
    mountain = max(int(water) + 1, min(253, mountain))
    return mountain, max(mountain + 2, min(255, snow))


def amplitude_for_radius(radius):
    t = max(0.0, min(1.0, (radius - 60.0) / 40.0))
    return round(50.0 + 50.0 * t * t * (3.0 - 2.0 * t))


@lru_cache(maxsize=64)
def _contour_areas(side, players, seed, counts, variant):
    import numpy as np

    from .large_islands import build_island_masks

    labels, *_ = build_island_masks(
        side,
        len(counts) if counts else players,
        seed,
        island_player_counts=counts,
        variant_r21=variant,
    )
    return tuple(int(v) for v in np.bincount(labels.ravel())[1:])


def resolve_island_profile(profile, side, players, *, player_teams=(), seed=0):
    """Resolve each actual source contour before lakes, without editing controls.

    The scalar controls summarize the minimum effective values. Per-island
    values remain in this runtime-only copy, shared by source and classification.
    """
    if (
        not profile
        or profile.get("morphology", {}).get("relief_source")
        not in ISLAND_RELIEF_SOURCES
    ):
        return profile
    result = normalize_archetype_profile(
        profile, archetype_key=profile.get("archetype_key", "large_islands")
    )
    morphology = result["morphology"]
    if morphology["relief_source"] == RELIEF_SOURCE_CONTINENTAL:
        # Ignore inherited island switches, including in saved older profiles.
        if morphology["island_amplitude_auto"]:
            morphology["island_amplitude_percent"] = 100
        if morphology["island_thresholds_auto"]:
            result["relief"].update(mountain_threshold=140, snow_threshold=200)
        morphology.update(island_amplitude_auto=False, island_thresholds_auto=False)
        result.pop("_island_relief_values", None)
        return result
    if (
        not morphology["island_amplitude_auto"]
        and not morphology["island_thresholds_auto"]
    ):
        return result
    from .island_teams import group_players_by_team
    from .profiles import RELIEF_SOURCE_LARGE_ISLANDS_R21

    counts = None
    if morphology["relief_source"] == RELIEF_SOURCE_TEAM_ISLANDS:
        counts = [
            len(group) for group in group_players_by_team(int(players), player_teams)
        ]
    areas = _contour_areas(
        int(side),
        int(players),
        int(seed),
        tuple(counts) if counts else None,
        morphology["relief_source"] == RELIEF_SOURCE_LARGE_ISLANDS_R21,
    )
    relief = result["relief"]
    values = []
    for area in areas:
        radius = sqrt(int(area) / pi)
        percent = (
            amplitude_for_radius(radius)
            if morphology["island_amplitude_auto"]
            else morphology["island_amplitude_percent"]
        )
        mountain, snow = (
            calibrated_thresholds(
                relief["water_threshold"],
                max(140, relief["water_threshold"] + 1),
                max(200, relief["water_threshold"] + 3),
                percent / 100.0,
                radius,
            )
            if morphology["island_thresholds_auto"]
            else (relief["mountain_threshold"], relief["snow_threshold"])
        )
        values.append(
            {
                "area": int(area),
                "radius": radius,
                "amplitude": percent,
                "mountain": mountain,
                "snow": snow,
            }
        )
    result["_island_relief_values"] = values
    morphology["island_amplitude_percent"] = min(v["amplitude"] for v in values)
    relief.update(
        mountain_threshold=min(v["mountain"] for v in values),
        snow_threshold=min(v["snow"] for v in values),
    )
    morphology.update(island_amplitude_auto=False, island_thresholds_auto=False)
    return result


def island_threshold_fields(profile, labels):
    """Return local classification thresholds, or None for a scalar profile."""
    values = (profile or {}).get("_island_relief_values")
    if not values:
        return None
    import numpy as np

    relief = profile["relief"]
    mountain = np.full(labels.shape, relief["mountain_threshold"], dtype=np.int16)
    snow = np.full(labels.shape, relief["snow_threshold"], dtype=np.int16)
    for n, value in enumerate(values, 1):
        mountain[labels == n] = value["mountain"]
        snow[labels == n] = value["snow"]
    return mountain, snow


def effective_island_value(profile, name, fallback):
    values = [v[name] for v in profile.get("_island_relief_values", ())]
    if not values:
        return fallback
    low, high = min(values), max(values)
    return low if low == high else f"{low}–{high}"
