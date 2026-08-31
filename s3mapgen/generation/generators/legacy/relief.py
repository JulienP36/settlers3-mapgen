"""Height field and summit snow for procedural Continental Legacy maps."""

from __future__ import annotations

import numpy as np
from scipy import ndimage

from .profile import load_profile
from ...core.noise import warped_fractal_field
from ....map_data.constants import ROCK_SNOW_TRANS, ROCKY, SNOW, SNOW_TRANS, WATER_IDS
from ....map_data.hexgrid import HEX6, component_labels, depth, distance_from, neighbor_count


_HEX = np.array(((1, 1, 0), (1, 1, 1), (0, 1, 1)), dtype=bool)


def _band_height(distance: np.ndarray, cfg: dict) -> np.ndarray:
    result = np.full(distance.shape, float(cfg["81_160"]), dtype=float)
    for label, value in (("0_2", cfg["0_2"]), ("3_5", cfg["3_5"]), ("6_10", cfg["6_10"]), ("11_20", cfg["11_20"]), ("21_40", cfg["21_40"]), ("41_80", cfg["41_80"])):
        low, high = (int(v) for v in label.split("_"))
        result[(distance >= low) & (distance <= high)] = float(value)
    return result


def _limit_hex_slopes(height: np.ndarray, max_delta: int = 5) -> np.ndarray:
    """Conservatively cap local height deltas without flattening the map."""

    work = height.astype(np.int16, copy=True)
    for _ in range(7):
        # The former implementation rebuilt six complete shifted arrays per
        # pass in Python.  This is the same operation expressed as one C-level
        # HEX6 minimum filter: current height must not exceed the lowest
        # neighbour by more than ``max_delta``.  Keeping the seven passes
        # preserves the terrain rule while removing the 768² performance cliff.
        previous = work
        neighbour_minimum = ndimage.minimum_filter(
            previous,
            footprint=_HEX,
            mode="constant",
            cval=255,
        )
        work = np.minimum(previous, neighbour_minimum + max_delta)
    return np.clip(work, 0, 255).astype(np.uint8)


def add_relief(state, profile: dict, rng: np.random.Generator) -> dict:
    """Create a coast-to-interior elevation field plus mountain massifs."""

    terrain = state.terrain
    water = np.isin(terrain, WATER_IDS)
    distance = distance_from(water, max_distance=180)
    base = _band_height(distance, profile["relief"]["grass_height_by_water_distance"])
    noise = warped_fractal_field(state.side, rng, scales=(.012, .032, .082), warp_scale=.018, warp_strength=.050)
    height = base + 5.5 * noise

    mountain = np.isin(terrain, (17, 33, 32, 35, 129, 128))
    mdepth = depth(mountain)
    mountain_cfg = profile["relief"]["mountain_height_by_depth"]
    mountain_base = np.full(mdepth.shape, float(mountain_cfg["33_plus"]), dtype=float)
    for label, value in (("1_2", mountain_cfg["1_2"]), ("3_4", mountain_cfg["3_4"]), ("5_8", mountain_cfg["5_8"]), ("9_16", mountain_cfg["9_16"]), ("17_32", mountain_cfg["17_32"])):
        low, high = (int(v) for v in label.split("_"))
        mountain_base[(mdepth >= low) & (mdepth <= high)] = float(value)
    height[mountain] = mountain_base[mountain] + 6.0 * noise[mountain]
    height[water] = 0
    state.height[:] = _limit_hex_slopes(np.rint(np.clip(height, 0, 220)).astype(np.uint8))
    state.height[water] = 0
    return {
        "height_max": int(state.height.max()),
        "height_mean_land": float(state.height[~water].mean()) if (~water).any() else 0.0,
    }


def add_snow(state, profile: dict, rng: np.random.Generator) -> dict:
    """Paint snow only on high, deep mountain cores with explicit transitions."""

    terrain, height = state.terrain, state.height
    mountain = np.isin(terrain, (17, 33, 32))
    mdepth = depth(mountain)
    cfg = profile["snow"]
    candidates = (terrain == ROCKY) & (mdepth >= int(cfg["minimum_mountain_depth"])) & (height >= int(cfg["minimum_height"]))
    if candidates.any():
        threshold = np.percentile(height[candidates], float(cfg["massif_height_percentile"]))
        texture = warped_fractal_field(state.side, rng, scales=(.020, .055, .120), warp_scale=.030, warp_strength=.038)
        snow = candidates & ((height.astype(float) + 7.0 * texture) >= threshold)
        labels, count = component_labels(snow)
        for component in range(1, count + 1):
            part = labels == component
            if int(part.sum()) < int(cfg["minimum_raw_component_cells"]):
                snow[part] = False
    else:
        snow = np.zeros_like(terrain, dtype=bool)
    terrain[snow] = SNOW
    snow_depth = depth(snow)
    terrain[snow & (snow_depth == 1)] = SNOW_TRANS
    rock_snow = (terrain == ROCKY) & (neighbor_count(snow) > 0)
    terrain[rock_snow] = ROCK_SNOW_TRANS
    return {"snow_family_cells": int(np.isin(terrain, (SNOW, SNOW_TRANS, ROCK_SNOW_TRANS)).sum())}


__all__ = ("add_relief", "add_snow")
