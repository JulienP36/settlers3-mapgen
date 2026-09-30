"""Non-mutating mass diagnostics for archetype previews and start placement."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import numpy as np

from ...map_data.constants import GRASS
from ...map_data.hexgrid import component_labels


@dataclass(frozen=True, slots=True)
class MacroMassReport:
    """Connected-land summary for the five-class archetype preview."""

    land_cells: int
    water_cells: int
    mass_count: int
    largest_mass_cells: int
    largest_mass_share_percent: float


def analyze_macro_masses(macro: np.ndarray) -> MacroMassReport:
    """Measure connected non-water macro masses without changing the raster."""

    values = np.asarray(macro, dtype=np.uint8)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("La carte macro doit être une matrice carrée")
    land = values != 0
    labels, count = component_labels(land)
    sizes = np.bincount(labels.ravel(), minlength=int(count) + 1)[1:]
    land_cells = int(np.count_nonzero(land))
    largest = int(sizes.max(initial=0)) if sizes.size else 0
    share = (largest * 100.0 / land_cells) if land_cells else 0.0
    return MacroMassReport(
        land_cells=land_cells,
        water_cells=int(values.size - land_cells),
        mass_count=int(count),
        largest_mass_cells=largest,
        largest_mass_share_percent=float(share),
    )


def analyze_startable_masses(
    terrain: np.ndarray,
    starts: Iterable[tuple[int, int]] = (),
    *,
    candidate_centers_considered: int | None = None,
) -> dict[str, object]:
    """Report the grass masses used by the current start bridge.

    This is deliberately diagnostic.  It does not move starts, merge islands
    or alter the validated terrain.  The future start solver can consume the
    report once its distribution rules are defined.
    """

    values = np.asarray(terrain, dtype=np.uint8)
    if values.ndim != 2 or values.shape[0] != values.shape[1]:
        raise ValueError("Le terrain doit être une matrice carrée")
    grass = values == GRASS
    labels, count = component_labels(grass)
    sizes = np.bincount(labels.ravel(), minlength=int(count) + 1)[1:]
    grass_cells = int(np.count_nonzero(grass))
    largest_label = int(np.argmax(sizes) + 1) if sizes.size else 0
    largest_cells = int(sizes.max(initial=0)) if sizes.size else 0
    starts_list = [(int(x), int(y)) for x, y in starts]
    component_labels_for_starts = []
    for x, y in starts_list:
        if 0 <= x < values.shape[1] and 0 <= y < values.shape[0]:
            component_labels_for_starts.append(int(labels[y, x]))
        else:
            component_labels_for_starts.append(0)
    starts_in_largest = sum(
        label == largest_label and label != 0
        for label in component_labels_for_starts
    )
    result: dict[str, object] = {
        "terrain_basis": "grass",
        "grass_cells": grass_cells,
        "grass_mass_count": int(count),
        "largest_grass_mass_cells": largest_cells,
        "largest_grass_mass_share_percent": (
            float(largest_cells * 100.0 / grass_cells) if grass_cells else 0.0
        ),
        "start_count": len(starts_list),
        "starts_in_largest_grass_mass": int(starts_in_largest),
        "all_starts_in_largest_grass_mass": bool(
            starts_list and starts_in_largest == len(starts_list)
        ),
        "start_component_labels": component_labels_for_starts,
    }
    if candidate_centers_considered is not None:
        result["candidate_centers_considered"] = int(candidate_centers_considered)
    return result


__all__ = ("MacroMassReport", "analyze_macro_masses", "analyze_startable_masses")
