"""Interior lake generation for the Continental Legacy hydrology layer."""

from __future__ import annotations

import numpy as np

from .shapes import place_components
from ....map_data.constants import GRASS, SHORE, WATER_IDS
from ....map_data.hexgrid import component_labels, dilate, distance_from, neighbor_count


def _rebuild_water_layers(state, protected: np.ndarray | None = None) -> None:
    """Apply the same depth/shore contract to ocean and new inland lakes."""

    terrain = state.terrain
    water = np.isin(terrain, WATER_IDS)
    water_depth = distance_from(~water, max_distance=8)
    terrain[water] = np.minimum(np.maximum(water_depth[water] - 1, 0), 7).astype(np.uint8)
    shore = (terrain == GRASS) & (neighbor_count(water) > 0)
    if protected is not None:
        shore &= ~protected
    terrain[shore] = SHORE
    state.height[water] = 0


def add_lakes(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Add native-scale irregular lakes, all larger than the forbidden micro size."""

    side = state.side
    terrain = state.terrain
    cfg = profile["lakes"]
    target = int(round(side * side * float(cfg["fraction_map_by_side"][str(side)])))
    water = np.isin(terrain, WATER_IDS)
    coast_distance = distance_from(water, max_distance=max(36, side // 8))
    terrain_distance = distance_from(terrain != GRASS, max_distance=8)
    # Lakes stay in actual grass interiors.  That prevents beach tiles from
    # appearing in plains and leaves their own grass shoreline visible.
    eligible = (
        (terrain == GRASS)
        & ~reservation
        # The exact start footprint is restored to Grass after the water
        # rebuild.  Keep a real buffer around it so a lake can never leave a
        # protected Grass cell directly against Water without Shore48.
        & ~dilate(reservation, 2)
        & (coast_distance >= 10)
        # Water, its Shore48 rim and a Grass16 separator must all fit before
        # another terrain family.  This prevents Shore48 from ever touching a
        # mountain transition directly after the lake is painted.
        & (terrain_distance >= 3)
    )
    desired_components = int(cfg["component_target_by_side"][str(side)])
    lake = place_components(
        eligible, target, desired_components, 0, rng, name="lake",
        major_min=max(int(cfg["minimum_component_cells"]), int(target / max(1, desired_components) * .30)),
        major_max=max(int(target / max(1, desired_components) * 4.5), int(cfg["minimum_component_cells"])),
        major_sigma=.72, micro_cells=0, aspect_range=(1.0, 2.8), separation=True,
    )
    terrain[lake] = 0
    # Lake shoreline uses the same explicit Water0..7 -> Shore48 -> Grass16
    # contract as the map edge.  Rebuilding it here also gives wide lakes a
    # real depth gradient instead of a flat cyan water fill.
    _rebuild_water_layers(state, protected=reservation)
    # The exact start footprint is an intentional grass opening.  Rebuilding
    # the surrounding water layers must never turn one of those cells into a
    # Shore48 tile merely because a lake/coast now touches it.
    terrain[reservation] = GRASS
    labels, count = component_labels(lake)
    sizes = np.bincount(labels.ravel())[1:] if count else np.array([], dtype=int)
    return {
        "lake_cells": int(lake.sum()),
        "lake_components": int(count),
        "lake_min_component": int(sizes.min()) if len(sizes) else 0,
    }


__all__ = ("add_lakes",)
