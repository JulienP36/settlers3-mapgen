"""Reference-calibrated coastal bathymetry for Continental Legacy v2.

The native SAVs have a strict land transition: an ocean/lake cell may touch a
shore tile (or a river mouth), but never ordinary grass directly.  The visible
coastal variation is therefore carried by the water IDs themselves.  The
first water layer is locally skipped in coherent patches and the deeper
layers shift with it; the Shore48 rim is not randomly removed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ...core.noise import warped_fractal_field
from ....map_data.constants import RIVER_IDS, SHORE, WATER_IDS
from ....map_data.hexgrid import component_labels, distance_from, neighbor_count


_BATHYMETRY_DEFAULT = "data/SETTLERS3_CONTINENTAL_COAST_BATHYMETRY_V1.npz"
_BATHYMETRY_CACHE: dict[str, dict[str, np.ndarray]] = {}


def _outer_ocean(water: np.ndarray) -> np.ndarray:
    """Return water components connected to at least one map edge."""

    labels, count = component_labels(water)
    if not count:
        return np.zeros_like(water, dtype=bool)
    border_labels = np.unique(
        np.concatenate((labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]))
    )
    border_labels = border_labels[border_labels > 0]
    return np.isin(labels, border_labels)


def _transform(field: np.ndarray, transform: int) -> np.ndarray:
    """Apply the same four deterministic symmetries as the coast mask bank."""

    if transform == 1:
        return np.rot90(field, 2).copy()
    if transform == 2:
        return field.T.copy()
    if transform == 3:
        return np.rot90(field.T, 2).copy()
    return field.copy()


def _load_bathymetry(path: Path) -> dict[str, np.ndarray] | None:
    """Load only the compact derived residual bank, never native SAV data."""

    key = str(path.resolve())
    cached = _BATHYMETRY_CACHE.get(key)
    if cached is not None:
        return cached
    try:
        with np.load(path, allow_pickle=False) as source:
            loaded = {
                name: np.asarray(source[name], dtype=np.int8).copy()
                for name in ("delta_2p", "delta_20p")
                if name in source.files
            }
    except (OSError, ValueError, KeyError):
        return None
    if not loaded:
        return None
    _BATHYMETRY_CACHE[key] = loaded
    return loaded


def _reference_delta(
    state,
    profile: dict,
    side: int,
    players: int | None,
) -> tuple[np.ndarray | None, str]:
    """Select the residual pattern belonging to the chosen morphology sample."""

    cfg = profile.get("coastal_bands", {}).get("bathymetry_library", {})
    configured = Path(str(cfg.get("path", _BATHYMETRY_DEFAULT)))
    if not configured.is_absolute():
        configured = Path(__file__).resolve().parents[4] / configured
    library = _load_bathymetry(configured)
    if library is None:
        return None, "procedural_fallback"

    split = int(cfg.get("density_split_players", 8))
    bank_key = "delta_20p" if players is not None and int(players) > split else "delta_2p"
    bank = library.get(bank_key)
    if bank is None or bank.ndim != 3 or bank.shape[1:] != (side, side) or not len(bank):
        return None, "procedural_fallback"

    index = int(state.metadata.get("macro_morphology_index", -1))
    transform = int(state.metadata.get("macro_morphology_transform", 0))
    if not 0 <= index < len(bank):
        return None, "procedural_fallback"
    return _transform(bank[index], transform), "reference_residual_v1"


def _procedural_delta(
    side: int,
    ocean: np.ndarray,
    distance: np.ndarray,
    rng: np.random.Generator,
    profile: dict,
) -> np.ndarray:
    """Safe fallback for sizes without a 768 reference residual bank.

    It can only promote a water ID to a deeper ID.  Consequently it changes
    the apparent width of the shallow bands without ever changing the land
    rim or introducing a direct water-to-grass edge.
    """

    cfg = profile.get("coastal_bands", {})
    fraction = float(cfg.get("fallback_deepened_fraction", 0.024))
    field = warped_fractal_field(
        side,
        rng,
        scales=(.012, .030, .075),
        warp_scale=.022,
        warp_strength=.055,
    )
    delta = np.zeros((side, side), dtype=np.int8)
    for layer in range(1, 8):
        support = ocean & (distance == layer)
        if not support.any():
            continue
        threshold = float(np.quantile(field[support], max(0.0, 1.0 - fraction)))
        chosen = support & (field >= threshold)
        # One-cell promotions reproduce the measured dominant residual.  The
        # smooth field makes them short coherent coast patches rather than
        # isolated random pixels.
        delta[chosen] = 1
    return delta


def _transition_violation_cells(terrain: np.ndarray) -> int:
    """Count water-facing land cells that are neither Shore nor river mouth."""

    water = np.isin(terrain, WATER_IDS)
    allowed = np.isin(terrain, (SHORE, *RIVER_IDS))
    return int(np.count_nonzero((~water) & ~allowed & (neighbor_count(water) > 0)))


def refine_coastal_bands(
    state,
    profile: dict,
    rng: np.random.Generator,
) -> dict:
    """Apply variable water-band thickness while freezing the land transition."""

    cfg = profile.get("coastal_bands", {})
    if not bool(cfg.get("enabled", True)):
        return {"coastal_bands_enabled": False}

    terrain = state.terrain
    water = np.isin(terrain, WATER_IDS)
    ocean = _outer_ocean(water)
    if not ocean.any():
        return {"coastal_bands_enabled": True, "coastal_bands_ocean_cells": 0}

    before_shore = terrain == SHORE
    before_violation = _transition_violation_cells(terrain)
    if before_violation:
        raise RuntimeError(
            "Transition côtière invalide avant bathymétrie: "
            f"{before_violation} cellules eau-vers-terrain sans rive"
        )

    # Distance is measured against all existing land.  Only the outer ocean
    # is rewritten; inland lakes remain owned by the lake pass.
    distance = distance_from(~water, max_distance=8)
    shallow_band = ocean & (distance >= 1) & (distance <= 8)
    base = np.clip(distance - 1, 0, 7).astype(np.uint8)
    terrain[shallow_band] = base[shallow_band]

    delta, variation_source = _reference_delta(
        state,
        profile,
        int(state.side),
        state.metadata.get("players"),
    )
    if delta is None:
        delta = _procedural_delta(int(state.side), ocean, distance, rng, profile)
    delta = np.maximum(delta.astype(np.int16), 0)
    candidate = np.minimum(base.astype(np.int16) + delta, 7).astype(np.uint8)
    changed = shallow_band & (candidate != base)
    terrain[changed] = candidate[changed]

    # Never let this pass modify the beach/rim topology.  Any violation here
    # is a programming error and aborts generation instead of exporting a
    # visually broken map.
    if not np.array_equal(before_shore, terrain == SHORE):
        raise RuntimeError("La passe bathymétrique a modifié la rive Shore48")
    after_violation = _transition_violation_cells(terrain)
    if after_violation:
        raise RuntimeError(
            "Transition côtière invalide après bathymétrie: "
            f"{after_violation} cellules eau-vers-terrain sans rive"
        )

    deepened = int(np.count_nonzero(changed))
    # Keep the old counters as compatibility aliases for UI/report consumers;
    # both now describe the same legal operation: skipping a shallow water
    # layer, never removing Shore48.
    return {
        "coastal_bands_enabled": True,
        "coastal_bands_ocean_cells": int(ocean.sum()),
        "coastal_bands_coast_cells": int((~water & (neighbor_count(ocean) > 0)).sum()),
        "coastal_bands_variation_source": variation_source,
        "coastal_bands_reference_residual_cells": deepened,
        "coastal_bands_deepened_cells": deepened,
        "coastal_bands_thinned_cells": deepened,
        "coastal_bands_thickened_cells": deepened,
        "coastal_bands_shore_break_cells": 0,
        "coastal_bands_singleton_shore_removed": 0,
        "coastal_bands_singleton_water0_removed": 0,
        "coastal_bands_transition_violations": 0,
    }


__all__ = ("refine_coastal_bands",)
