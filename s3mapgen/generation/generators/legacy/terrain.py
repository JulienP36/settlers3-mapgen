"""Ordered terrain-family passes and legal Settlers III transition chains."""

from __future__ import annotations

import numpy as np
from scipy import ndimage

from .shapes import place_components
from ....map_data.constants import (
    DESERT,
    DESERT_TRANS,
    GRASS,
    GRASS_DESERT_TRANS,
    GRASS_SWAMP_TRANS,
    ROCK_TRANS_1,
    ROCK_TRANS_2,
    ROCKY,
    SWAMP,
    SWAMP_TRANS,
)
from ....map_data.hexgrid import depth, distance_from


_HEX = np.array(((1, 1, 0), (1, 1, 1), (0, 1, 1)), dtype=bool)


def _side_value(values: dict, side: int) -> float:
    return float(values[str(side)])


def _fill_internal_holes(mask: np.ndarray) -> np.ndarray:
    """Remove accidental cavities without merging independent components."""

    return ndimage.binary_fill_holes(mask, structure=_HEX)


def _paint_family(
    terrain: np.ndarray,
    family: np.ndarray,
    core_id: int,
    outer_to_inner: tuple[int, ...],
) -> None:
    """Paint one coherent mask from its outer transition ring inward.

    ``depth == 1`` is the exterior rim.  The terrain chains therefore need to
    be supplied in *outer-to-inner* order: Mountain ``17, 33, 32`` for
    example.  Keeping that convention in one place prevents a visual ring
    from being legal-looking but semantically reversed.
    """

    terrain[family] = core_id
    family_depth = depth(family)
    for ring_depth, terrain_id in enumerate(outer_to_inner, start=1):
        terrain[family & (family_depth == ring_depth)] = terrain_id


def _mountain_mask(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    side = state.side
    terrain = state.terrain
    cfg = profile["biomes"]["mountain"]
    land = terrain == GRASS
    water_distance = distance_from(~land, max_distance=max(40, side // 9))
    target = int(round(float(land.sum()) * float(cfg["fraction_land"]["mean"])))
    support = land & ~reservation & (water_distance >= int(cfg["minimum_water_distance"]))
    mountain = place_components(
        support,
        target,
        int(cfg["significant_components_by_side"][str(side)]),
        int(cfg["micro_components_by_side"][str(side)]),
        rng,
        name="mountain",
        major_min=max(24, int(cfg["major_min"] * (side / 768) ** 2)),
        major_max=int(cfg["major_max"]),
        major_sigma=float(cfg["major_sigma"]),
        micro_cells=int(cfg["micro_cells_by_side"][str(side)]),
        micro_max=int(cfg["micro_max"]),
        aspect_range=tuple(cfg["aspect_range"]),
        separation=bool(cfg["major_separation"]),
        forbidden=reservation,
        noise_interpolation_order=2,
    )
    return _fill_internal_holes(mountain)


def add_mountains(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Place the complete mountain family before every other terrain family."""

    mountain = _mountain_mask(state, profile, reservation, rng)
    _paint_family(state.terrain, mountain, ROCKY, (ROCK_TRANS_1, ROCK_TRANS_2))
    return {
        "mountain_core_cells": int(mountain.sum()),
        "mountain_family_cells": int(np.isin(state.terrain, (ROCKY, ROCK_TRANS_2, ROCK_TRANS_1)).sum()),
    }


def _surface_family_mask(
    state,
    profile: dict,
    reservation: np.ndarray,
    rng: np.random.Generator,
    family_name: str,
) -> np.ndarray:
    """Build an independent, grass-only surface-family mask."""

    side = state.side
    terrain = state.terrain
    cfg = profile["biomes"][family_name]
    water_distance = distance_from(terrain != GRASS, max_distance=max(36, side // 8))
    target = int(round(float((terrain == GRASS).sum()) * _side_value(cfg["fraction_land_by_side"], side)))
    minimum_water_distance = 8 if family_name == "desert" else 6
    support = (terrain == GRASS) & ~reservation & (water_distance >= minimum_water_distance)
    family = place_components(
        support,
        target,
        int(cfg["significant_components_by_side"][str(side)]),
        int(cfg["micro_components_by_side"][str(side)]),
        rng,
        name=family_name,
        major_min=max(4, int(cfg["major_min"] * (side / 768) ** 2)),
        major_max=int(cfg["major_max"]),
        major_sigma=float(cfg["major_sigma"]),
        micro_cells=int(cfg["micro_cells_by_side"][str(side)]),
        micro_max=int(cfg["micro_max"]),
        aspect_range=tuple(cfg["aspect_range"]),
        separation=bool(cfg["major_separation"]),
        forbidden=reservation,
        noise_interpolation_order=2,
    )
    return _fill_internal_holes(family)


def add_swamps(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Place marshes after hydrology, only on the still-free grass support."""

    swamp = _surface_family_mask(state, profile, reservation, rng, "swamp")
    _paint_family(state.terrain, swamp, SWAMP, (GRASS_SWAMP_TRANS, SWAMP_TRANS))
    return {
        "swamp_core_cells": int(swamp.sum()),
        "swamp_family_cells": int(np.isin(state.terrain, (SWAMP, SWAMP_TRANS, GRASS_SWAMP_TRANS)).sum()),
    }


def add_other_terrains(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Place remaining enabled Legacy surface families after marshes."""

    desert = _surface_family_mask(state, profile, reservation, rng, "desert")
    _paint_family(state.terrain, desert, DESERT, (GRASS_DESERT_TRANS, DESERT_TRANS))
    return {
        "desert_core_cells": int(desert.sum()),
        "desert_family_cells": int(np.isin(state.terrain, (DESERT, DESERT_TRANS, GRASS_DESERT_TRANS)).sum()),
    }


def add_biomes(state, profile: dict, reservation: np.ndarray, rng: np.random.Generator) -> dict:
    """Compatibility wrapper for callers that need the three terrain families."""

    metadata = add_mountains(state, profile, reservation, rng)
    metadata.update(add_swamps(state, profile, reservation, rng))
    metadata.update(add_other_terrains(state, profile, reservation, rng))
    return metadata


__all__ = ("add_biomes", "add_mountains", "add_other_terrains", "add_swamps")
