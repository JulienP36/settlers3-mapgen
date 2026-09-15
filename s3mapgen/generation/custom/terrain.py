"""Semantic terrain controls and diagnostics for the Custom generator.

The actual terrain scaling is deliberately owned by the native terrain
passes.  This module only normalizes the public rates, clears explicitly
disabled families, and reports the result.  It must never manufacture a
second family of candidate blobs: at ``100 %`` the native generator runs its
original recipe unchanged, and every other value only changes the number of
native brush probes and expansions in that same recipe.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any

import numpy as np

from ...map_data.constants import (
    DESERT,
    DESERT_IDS,
    DRY_GRASS,
    GRASS,
    GRASS_DETAIL_IDS,
    MUD_IDS,
    ROCKY,
    ROCKY_DETAIL,
    SWAMP,
    SWAMP_IDS,
)
from ...map_data.hexgrid import HEX6, component_labels


TERRAIN_RATE_MIN = 0.0
TERRAIN_RATE_MAX = 500.0
# Zero has one unambiguous meaning in the editor: the family is disabled.
# An enabled family therefore starts at the smallest representable positive
# rate.  The explicit switch remains responsible for the native zero case.
TERRAIN_ENABLED_RATE_MIN = 1.0
TERRAIN_FAMILY_KEYS = ("mud", "desert", "dry_grass", "details", "swamp")


# These are semantic families, not editable ID lists.  The IDs stay here as
# implementation details so the UI cannot accidentally turn a transition into
# an independent terrain type.
TERRAIN_FAMILY_SPECS: dict[str, dict[str, Any]] = {
    "mud": {
        "ids": MUD_IDS,
        "core_id": 144,
        "outer_id": 23,
        "inner_id": 145,
        "fallback_id": GRASS,
    },
    "desert": {
        "ids": DESERT_IDS,
        "core_id": DESERT,
        "outer_id": 20,
        "inner_id": 65,
        "fallback_id": GRASS,
    },
    "swamp": {
        "ids": SWAMP_IDS,
        "core_id": SWAMP,
        "outer_id": 21,
        "inner_id": 81,
        "fallback_id": GRASS,
    },
    "dry_grass": {
        "ids": (DRY_GRASS,),
        "core_id": DRY_GRASS,
        "fallback_id": GRASS,
    },
    "details": {
        "ids": (*GRASS_DETAIL_IDS, ROCKY_DETAIL),
        "fallback_ids": {18: GRASS, 19: GRASS, ROCKY_DETAIL: ROCKY},
    },
}


# These object families require the corresponding surface to exist.  They are
# used both by the UI dependency state and by the content passes so a disabled
# terrain cannot leave an orphaned decoration rate active in the engine.
TERRAIN_DECORATION_DEPENDENCIES = {
    "desert": ("cacti", "dead_trees", "skeletons"),
    "swamp": ("reeds",),
}


# A transition ID is legal only beside the IDs listed here.  The native
# terrain pass creates these IDs in the same order as the native pipeline; this
# table is a strict diagnostic, not a second painting algorithm.
TERRAIN_TRANSITION_ALLOWED: dict[int, frozenset[int]] = {
    17: frozenset((16, 17, 33)),
    20: frozenset((16, 20, 65)),
    21: frozenset((16, 21, 81)),
    23: frozenset((16, 23, 145)),
    24: frozenset((16, 24)),
    33: frozenset((17, 33, 32)),
    34: frozenset((32, 34)),
    35: frozenset((32, 35, 129)),
    65: frozenset((20, 65, 64)),
    81: frozenset((21, 81, 80)),
    129: frozenset((35, 129, 128)),
    144: frozenset((144, 145)),
    145: frozenset((23, 144, 145)),
    128: frozenset((128, 129)),
    64: frozenset((64, 65)),
    80: frozenset((80, 81)),
}


def _as_rate(value: Any, default: float = 100.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = float(default)
    return min(TERRAIN_RATE_MAX, max(TERRAIN_RATE_MIN, number))


def effective_terrain_rates(sections: Mapping[str, Any] | None) -> dict[str, float]:
    """Return the effective rates, applying the explicit enabled switches."""

    source: Any = sections.get("terrains", {}) if isinstance(sections, Mapping) else {}
    if not isinstance(source, Mapping):
        source = {}
    rates: dict[str, float] = {}
    for key in TERRAIN_FAMILY_KEYS:
        entry = source.get(key, {})
        if isinstance(entry, Mapping):
            enabled = bool(entry.get("enabled", True))
            rate = _as_rate(entry.get("rate_percent", 100.0))
        else:
            enabled = True
            rate = _as_rate(entry)
        rates[key] = max(TERRAIN_ENABLED_RATE_MIN, rate) if enabled else 0.0
    return rates


def effective_decoration_rates(sections: Mapping[str, Any] | None) -> dict[str, float]:
    """Return decoration rates with terrain-dependent families disabled."""

    raw = sections.get("decorations", {}) if isinstance(sections, Mapping) else {}
    raw = raw if isinstance(raw, Mapping) else {}
    rates = {str(key): _as_rate(value, 100.0) for key, value in raw.items()}
    terrain_rates = effective_terrain_rates(sections)
    for terrain_key, decoration_keys in TERRAIN_DECORATION_DEPENDENCIES.items():
        if terrain_rates.get(terrain_key, 0.0) <= 0.0:
            for decoration_key in decoration_keys:
                rates[decoration_key] = 0.0
    return rates


def _clear_family(
    terrain: np.ndarray,
    key: str,
    protected_mask: np.ndarray | None = None,
) -> None:
    """Remove one explicitly disabled family while preserving its substrate."""

    spec = TERRAIN_FAMILY_SPECS[key]
    if key == "details":
        for terrain_id, fallback in spec["fallback_ids"].items():
            mask = terrain == int(terrain_id)
            if protected_mask is not None:
                mask &= ~protected_mask
            terrain[mask] = int(fallback)
        return
    mask = np.isin(terrain, tuple(int(value) for value in spec["ids"]))
    if protected_mask is not None:
        mask &= ~protected_mask
    terrain[mask] = int(spec["fallback_id"])


def _family_counts(terrain: np.ndarray, key: str) -> tuple[np.ndarray, int]:
    ids = tuple(int(value) for value in TERRAIN_FAMILY_SPECS[key]["ids"])
    mask = np.isin(terrain, ids)
    return mask, int(mask.sum())


def _family_metrics(
    terrain: np.ndarray,
    reference: np.ndarray,
    key: str,
    rate: float,
) -> dict[str, int | float]:
    before_mask, before = _family_counts(reference, key)
    after_mask, after = _family_counts(terrain, key)
    _, zones_before = component_labels(before_mask)
    labels, zones_after = component_labels(after_mask)
    target = int(round(before * rate / 100.0))
    return {
        "requested_rate_percent": float(rate),
        "before_cells": int(before),
        "target_cells": int(target),
        "after_cells": int(after),
        "zones_before": int(zones_before),
        "zones_added": max(0, int(zones_after) - int(zones_before)),
        "zones_after": int(zones_after),
        "largest_zone": int(
            max(
                (int((labels == label).sum()) for label in range(1, zones_after + 1)),
                default=0,
            )
        ),
        "shortfall": max(0, int(target) - int(after)),
        "overshoot": max(0, int(after) - int(target)),
    }


def terrain_transition_violations(terrain: np.ndarray) -> dict[str, Any]:
    """Return strict HEX6 transition violations for a terrain field."""

    invalid_cells = np.zeros(terrain.shape, dtype=bool)
    pairs: Counter[tuple[int, int]] = Counter()
    height, width = terrain.shape
    total = 0
    for source, allowed in TERRAIN_TRANSITION_ALLOWED.items():
        for dx, dy in HEX6:
            y0, y1 = max(0, dy), min(height, height + dy)
            x0, x1 = max(0, dx), min(width, width + dx)
            sy0, sy1 = max(0, -dy), min(height, height - dy)
            sx0, sx1 = max(0, -dx), min(width, width - dx)
            source_slice = terrain[sy0:sy1, sx0:sx1] == int(source)
            neighbour_slice = terrain[y0:y1, x0:x1]
            bad = source_slice & ~np.isin(neighbour_slice, tuple(allowed))
            if not bad.any():
                continue
            total += int(bad.sum())
            invalid_cells[sy0:sy1, sx0:sx1] |= bad
            for value in neighbour_slice[bad]:
                pairs[(int(source), int(value))] += 1
    return {
        "total": int(total),
        "unique_cells": int(invalid_cells.sum()),
        "pairs": {
            f"{source}->{target}": int(count)
            for (source, target), count in sorted(pairs.items())
        },
    }


def apply_custom_terrain_rates(
    terrain: np.ndarray,
    sections: Mapping[str, Any] | None,
    *,
    seed: int = 0,
    protected_mask: np.ndarray | None = None,
    native_surface_base: np.ndarray | None = None,
    reference_terrain: np.ndarray | None = None,
) -> dict[str, Any]:
    """Clear disabled families and report a native terrain pass.

    The native generator performs every non-zero rate directly inside its
    existing brush/expansion routine.  This function intentionally does not
    create or select terrain zones.  ``reference_terrain`` is the unscaled
    native pass used for diagnostics; ``native_surface_base`` is retained as
    a compatibility alias for callers from the previous candidate.

    When called directly without a reference, the input snapshot is used for
    the report.  That keeps the helper useful for format-level checks while
    leaving generation exclusively to the native engine.
    """

    del seed
    rates = effective_terrain_rates(sections)
    reference = reference_terrain
    if reference is None:
        reference = native_surface_base
    if reference is None:
        reference = terrain.copy()
    reference = np.asarray(reference, dtype=np.uint8)

    for key, rate in rates.items():
        if rate <= 0.0:
            _clear_family(terrain, key, protected_mask)

    families = {
        key: _family_metrics(terrain, reference, key, float(rate))
        for key, rate in rates.items()
    }
    return {
        "rates": rates,
        "families": families,
        "changed": any(
            int(values["before_cells"]) != int(values["after_cells"])
            for values in families.values()
        ),
        "transition_violations": terrain_transition_violations(terrain),
        "model": "native_surface_direct_scaling_v1",
        "reference_source": (
            "native_unscaled_pass"
            if reference_terrain is not None or native_surface_base is not None
            else "input_snapshot"
        ),
    }


__all__ = (
    "TERRAIN_DECORATION_DEPENDENCIES",
    "TERRAIN_FAMILY_KEYS",
    "TERRAIN_FAMILY_SPECS",
    "TERRAIN_ENABLED_RATE_MIN",
    "TERRAIN_TRANSITION_ALLOWED",
    "TERRAIN_RATE_MAX",
    "TERRAIN_RATE_MIN",
    "apply_custom_terrain_rates",
    "effective_decoration_rates",
    "effective_terrain_rates",
    "terrain_transition_violations",
)
