"""Optional improvements to the native upstream river walk.

The native scan, relief score, marker routing, minimum lengths, confluences
and painting remain owned by each engine. This policy only filters coastal
steps, adjusts forward candidate scores, and regulates new mouths using map
size and land area. It neither
modifies heights nor consumes the engine PRNG.
"""

from __future__ import annotations

from collections import deque
from math import sqrt

import numpy as np

from ..map_data.hexgrid import component_labels, neighbor_count


class ImprovedRiverPolicy:
    """General HEX6 policy, independent of island labels and archetype names."""

    def __init__(self, terrain: np.ndarray):
        # Freeze the water mask before mouths are painted as river cells.
        # Otherwise a later branch could creep along a former coastline.
        self.near_water = neighbor_count(terrain <= 7) > 0
        self.inland = ~self.near_water
        self.history: deque[tuple[int, int]] = deque(maxlen=12)
        self.continuation = False
        self.length_scale = terrain.shape[0] / 512.0
        # One frozen HEX6 labelling per pass. Both mouths and branches use
        # their actual connected land area, independently of archetype/players.
        self.land_components, _ = component_labels(terrain > 7)
        areas = np.bincount(self.land_components.ravel())
        # A mass occupying ~14% of a 512 map retains the calibrated length
        # potential (roughly one of four large islands). Larger continents
        # retain the map scale; smaller masses shorten continuously.
        self.component_length_scales = np.clip(
            np.sqrt(areas / (.14 * 512.0 ** 2)),
            min(.35, self.length_scale), self.length_scale,
        )
        self.component_length_scales[0] = self.length_scale
        self.local_length_scale = self.length_scale

    def quantity(self, side: int, terrain: np.ndarray, rate_percent: float) -> None:
        # Calibration against classic relief: counts grow faster than
        # the side, adjusted by the actual terrestrial share. No island labels,
        # coastline measurement, or target allocation per component is needed.
        self.land_cells = int(np.count_nonzero(terrain > 7))
        size_factor = (side / 512.0) ** 1.3
        self.mouth_target = 0.30 * self.land_cells / side * size_factor * rate_percent / 100.0
        self.mouths = 0
        self.branches = 0
        self.mouth_length_total = 0
        self.max_mouth_length = 0

    def proposal_threshold(self, native_threshold: int) -> int:
        # More chances for new mouths on large maps compensate routes refused
        # by the improved policy. Branches keep the user's original threshold.
        return round(native_threshold * max(1.0, self.length_scale))

    def mouth_threshold(self, native_threshold: int) -> int:
        if self.mouth_target <= 0:
            return 0
        # Leave sparse maps alone, progressively thin new mouths once enough
        # have succeeded. A 20% allowance avoids an exact imposed quota.
        pressure = max(0.0, (self.mouths / self.mouth_target - 0.8) / 0.4)
        return round(native_threshold * max(0.0, 1.0 - pressure))

    def committed(self, continuation: bool, length: int) -> None:
        if continuation:
            self.branches += 1
        else:
            self.mouths += 1
            self.mouth_length_total += length
            self.max_mouth_length = max(self.max_mouth_length, length)

    def start(self, row: int, col: int, continuation: bool) -> None:
        self.history.clear()
        self.history.append((row, col))
        self.continuation = continuation
        component = int(self.land_components[row, col])
        self.local_length_scale = float(self.component_length_scales[component])

    def advance(self, row: int, col: int) -> None:
        self.history.append((row, col))

    def score(self, native_score: int, row: int, col: int, path_count: int) -> int:
        # The first land step is the mouth. Every following step, including
        # branches, must leave the coast; lakes obey the same rule as oceans.
        if self.near_water[row, col]:
            return 0
        score = int(native_score)
        if len(self.history) >= 8:
            origin_row, origin_col = self.history[0]
            dr, dc = row - origin_row, col - origin_col
            # Metric of the axial (+1,+1) HEX6 basis. Unlike simply counting
            # repeated directions, this detects long alternating zigzags
            # which still look almost straight in the actual map projection.
            efficiency = sqrt(dr * dr + dc * dc - dr * dc) / len(self.history)
            score -= round(8 * max(0.0, (efficiency - 0.75) / 0.25))
        # A soft, progressive headwater penalty avoids an endless coherent
        # uphill corridor. Strong local valleys can still support a longer
        # route: this is a score cost, not a hard length truncation.
        onset = round((16 if self.continuation else 24) * self.local_length_scale)
        score -= int(max(0, path_count - onset) / (2.0 * self.local_length_scale))
        return max(0, score)
