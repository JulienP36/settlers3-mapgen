"""Height correction ported from the United editor save pre-pass (0x417030).

Only height bytes are changed. Four north/south neighbours, row-major updates
and repeated passes intentionally follow the native routine exactly.
"""
from __future__ import annotations
import numpy as np

def correct_editor_heights(area: np.ndarray) -> dict[str, int]:
    if area.dtype != np.uint8 or area.ndim != 3 or area.shape[2] != 6 or area.shape[0] != area.shape[1]:
        raise ValueError("Expected a square uint8 six-channel Area")
    side = area.shape[0]
    before = area[:, :, 0].copy()
    water = (area[:, :, 1] <= 7) | (area[:, :, 1] == 250)
    area[:, :, 0][water] = 0
    area[:, :, 0][~water & (area[:, :, 0] == 0)] = 1
    values = area[:, :, 0].tolist()
    corrections = compatible_bounds = conflicting_bounds = passes = 0
    while True:
        passes += 1
        changed = 0
        for y, row in enumerate(values):
            north = values[y - 1] if y else None
            south = values[y + 1] if y + 1 < side else None
            for x in range(side):
                center = row[x]
                if north is None:
                    north_max = north_min = center
                else:
                    first = north[x - 1] if x else north[x]
                    second = north[x]
                    north_max = max(first, second)
                    north_min = min(225, first, second)
                if south is None:
                    south_max = south_min = center
                else:
                    first = south[x]
                    second = south[x + 1] if x + 1 < side else first
                    south_max = max(first, second)
                    south_min = min(225, first, second)
                lower_distance = min(center - north_max + 7, center - south_max + 5)
                upper_distance = min(north_min - center + 5, south_min - center + 7)
                if upper_distance >= 0 and lower_distance >= 0:
                    continue
                corrections += 1
                if upper_distance + lower_distance >= 0:
                    if upper_distance < 0:
                        center += upper_distance
                    row[x] = max(0, center) & 255
                    compatible_bounds += 1
                else:
                    if upper_distance < lower_distance:
                        center -= abs(upper_distance)
                    row[x] = max(0, center) & 255
                    conflicting_bounds += 1
                changed += 1
        if not changed:
            break
        if passes >= 1024:
            raise ValueError("Editor height correction did not converge")
    area[:, :, 0] = np.asarray(values, dtype=np.uint8)
    return {"changed_cells": int(np.count_nonzero(before != area[:, :, 0])),
            "corrections": corrections, "compatible_bounds": compatible_bounds,
            "conflicting_bounds": conflicting_bounds, "passes": passes}


def prepare_editor_export(area: np.ndarray) -> dict[str, int]:
    """United save context: 416370(0x10), 417030, 416370(0x20).

    The context pass visits interior cells only. Its water predicate is ID 0,
    not the complete water family and not height zero. Preserve all flag bits
    except bit 0, and never change objects, claims or resources.
    """
    if area.dtype != np.uint8 or area.ndim != 3 or area.shape[2] != 6 or area.shape[0] != area.shape[1]:
        raise ValueError("Expected a square uint8 six-channel Area")
    terrain = area[:, :, 1]
    flags = area[:, :, 4]
    if area.shape[0] > 2:
        interior = terrain[1:-1, 1:-1]
        interior_flags = flags[1:-1, 1:-1]
        height = area[1:-1, 1:-1, 0]
        touches_water0 = ((terrain[:-2, :-2] == 0) | (terrain[:-2, 1:-1] == 0)
                          | (terrain[1:-1, :-2] == 0) | (terrain[1:-1, 2:] == 0)
                          | (terrain[2:, 1:-1] == 0) | (terrain[2:, 2:] == 0))
        shore = interior == 48
        wet_shore = shore & touches_water0
        dry_shore = shore & ~touches_water0
        swamp = (interior == 80) | (interior == 81)
        interior_flags[swamp | dry_shore] &= 254
        interior_flags[wet_shore] |= 1
        interior[wet_shore] = 250
        height[wet_shore] = 0
        height[dry_shore & (height == 0)] = 1
    metrics = correct_editor_heights(area)
    swamp = (terrain == 80) | (terrain == 81)
    temporary_shore = terrain == 250
    flags[swamp] |= 1
    flags[temporary_shore] &= 254
    terrain[temporary_shore] = 48
    return metrics
