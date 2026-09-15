"""Bounded centre search and write-free plans for forced start bonuses."""
from dataclasses import dataclass

import numpy as np

from ...map_data.hexgrid import hex_distance

FORCED_CENTER_EXTENSION = 34


def ordered_centers(support, sx, sy, desired, shuffle):
    """Shuffle the normal band, then each successive HEX6 ring separately."""
    desired = max(1, int(desired))
    ys, xs = np.nonzero(support)
    dx, dy = xs - int(sx), ys - int(sy)
    distances = np.maximum(np.maximum(np.abs(dx), np.abs(dy)), np.abs(dx - dy))
    for low, high in [(max(1, desired - 2), desired + 2)] + [
        (r, r) for r in range(desired + 3, desired + FORCED_CENTER_EXTENSION + 1)
    ]:
        indices = np.flatnonzero((distances >= low) & (distances <= high))
        points = [(int(xs[i]), int(ys[i])) for i in indices]
        shuffle(points)
        yield from points


def radius_center_pairs(centers, radii, sx, sy, desired, forced):
    """Try all accepted sizes in the nearest band before moving outward."""
    if not forced:
        for radius in radii:
            for cx, cy in centers:
                yield radius, cx, cy
        return
    bands = {}
    for cx, cy in centers:
        distance = hex_distance(sx, sy, cx, cy)
        bands.setdefault(max(desired + 2, distance), []).append((cx, cy))
    for points in bands.values():
        for radius in radii:
            for cx, cy in points:
                yield radius, cx, cy


@dataclass
class ObjectPlan:
    center: tuple[int, int]
    adults: list[tuple[int, int]]
    saplings: list[tuple[int, int]]
    radius: int
    adult_radius: int


def plan_objects(centers, legal_cells, blocked_anchors, counts, spacing, footprint,
                 minimum_radius, minimum_adult_radius, rng):
    """Pack on temporary occupancy only; callers commit the selected plan once.

    The object envelope retains its existing automatic growth. Only the centre
    search is bounded. All footprint cells must be legal, including tower
    protection; minimum spacing also applies between tentative anchors.
    """
    side = legal_cells.shape[0]
    legal_cells = legal_cells.copy()
    if len(footprint) > 1:
        legal_cells[[0, -1], :] = False
        legal_cells[:, [0, -1]] = False
    legal = legal_cells.copy()
    for dx, dy in footprint:
        shifted = np.zeros_like(legal)
        y0, y1 = max(0, -dy), min(side, side - dy)
        x0, x1 = max(0, -dx), min(side, side - dx)
        shifted[y0:y1, x0:x1] = legal_cells[y0+dy:y1+dy, x0+dx:x1+dx]
        legal &= shifted
    legal &= ~blocked_anchors
    ys, xs = np.nonzero(legal)
    first_count, second_count = counts
    best = None
    best_count = -1
    for cx, cy in centers:
        dx, dy = xs - cx, ys - cy
        distances = np.maximum(np.maximum(np.abs(dx), np.abs(dy)), np.abs(dx - dy))
        # Randomness only among points in the same expanding envelope.
        tie_order = rng.permutation(len(xs))
        order = tie_order[np.argsort(np.maximum(distances[tie_order], minimum_adult_radius), kind='stable')]
        selected = []
        occupied = set()
        def take(index):
            x, y = int(xs[index]), int(ys[index])
            if any(hex_distance(x, y, xx, yy) < spacing for xx, yy in selected):
                return False
            cells = {(x + dx, y + dy) for dx, dy in footprint}
            if cells & occupied:
                return False
            selected.append((x, y))
            occupied.update(cells)
            return True
        adults = []
        adult_radius = minimum_adult_radius
        for i in order:
            if len(adults) >= first_count:
                break
            if take(i):
                adults.append(selected[-1])
                adult_radius = max(adult_radius, int(distances[i]))
        saplings = []
        if len(adults) == first_count:
            for i in order:
                if len(saplings) >= second_count:
                    break
                if first_count and distances[i] <= adult_radius:
                    continue
                if take(i):
                    saplings.append(selected[-1])
        radius = max([minimum_radius] + [hex_distance(cx, cy, x, y) for x, y in selected])
        plan = ObjectPlan((cx, cy), adults, saplings, radius, adult_radius)
        count = len(selected)
        if count > best_count:
            best, best_count = plan, count
        if len(adults) == first_count and len(saplings) == second_count:
            return plan
        if len(xs) < first_count + second_count:
            # Even ignoring collisions, no centre can satisfy this request.
            break
    return best
