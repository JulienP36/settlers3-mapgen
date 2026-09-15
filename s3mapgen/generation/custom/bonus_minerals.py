"""Geometry helpers for the start mineral bonus.

The normal R47 path is deliberately kept in ``upgraded.content`` for the
legacy-compatible hexagonal discs.  This module contains only the additional
geometry needed by R48: exact compact surfaces, a connected organic outline,
and transition rings derived from the complete core footprint.
"""

from __future__ import annotations

import random
from collections import deque
import heapq
import math

from ...map_data.constants import HEX6
from ...map_data.hexgrid import hex_distance


def hex_disc_offsets(radius: int) -> list[tuple[int, int]]:
    """Return all relative cells in a HEX6 disc, including the centre."""

    radius = max(0, int(radius))
    return [
        (x, y)
        for y in range(-radius, radius + 1)
        for x in range(-radius, radius + 1)
        if hex_distance(0, 0, x, y) <= radius
    ]


def _ring_offsets(radius: int) -> list[tuple[int, int]]:
    points = [
        (x, y)
        for y in range(-radius, radius + 1)
        for x in range(-radius, radius + 1)
        if hex_distance(0, 0, x, y) == radius
    ]
    # A stable angular-ish ordering makes a partial last ring remain one
    # compact cap instead of six independently scattered cells.
    points.sort(key=lambda point: (point[1], point[0]))
    return points


def compact_hex_offsets(target: int, rng: random.Random | None = None) -> list[tuple[int, int]]:
    """Return a connected, hole-free hexagonal footprint of exactly ``target``.

    Canonical disc sizes remain exact discs.  A non-canonical custom surface
    takes the complete inner discs and a contiguous prefix of the next ring;
    this preserves the requested area without changing the user's selected
    ``Hexagone`` shape into a noisy blob.
    """

    target = max(1, int(target))
    radius = 0
    while len(hex_disc_offsets(radius)) < target:
        radius += 1
    inner = set(hex_disc_offsets(max(0, radius - 1)))
    if len(inner) >= target:
        return list(inner)[:target]
    ring = _ring_offsets(radius)
    remaining = target - len(inner)
    if rng is not None and remaining < len(ring):
        # Rotating, rather than shuffling, keeps the cap contiguous and only
        # varies its orientation between starts.
        offset = rng.randrange(len(ring))
        ring = ring[offset:] + ring[:offset]
    return list(inner) + ring[:remaining]


def _has_hole(points: set[tuple[int, int]]) -> bool:
    """Return whether the finite bounding box contains an enclosed gap."""

    if not points:
        return False
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    min_x, max_x = min(xs) - 1, max(xs) + 1
    min_y, max_y = min(ys) - 1, max(ys) + 1
    outside = {(min_x, min_y)}
    queue = deque(outside)
    while queue:
        x, y = queue.popleft()
        for dx, dy in HEX6:
            neighbour = (x + dx, y + dy)
            nx, ny = neighbour
            if not (min_x <= nx <= max_x and min_y <= ny <= max_y):
                continue
            if neighbour in points or neighbour in outside:
                continue
            outside.add(neighbour)
            queue.append(neighbour)
    for y in range(min_y + 1, max_y):
        for x in range(min_x + 1, max_x):
            if (x, y) not in points and (x, y) not in outside:
                return True
    return False


def organic_offsets(target: int, rng: random.Random, *, attempts: int = 24) -> list[tuple[int, int]]:
    """Return an exact, rounded Upgraded-style mineral blob.

    Upgraded deposits are grown through the six-neighbour frontier rather than
    assembling a noisy set of boundary pixels.  The priority is evaluated in
    the same ``X = 2*x-y, Y = 2*y`` space as the normal parallelogram preview;
    this compensates the display projection instead of stretching every blob
    along its native-grid axis.  Several low-frequency angular waves and two
    broad 2-D waves vary the contour from seed to seed without introducing
    single-cell saw teeth.  The frontier itself guarantees one connected
    component; the fill check rejects enclosed gaps and the compactness check
    prevents a rare thin tail from being accepted.
    """

    target = max(1, int(target))
    if target <= 3:
        return compact_hex_offsets(target, rng)

    radius = math.sqrt(target / math.pi)
    # The metric is expressed in projected pixels, while the frontier still
    # walks native HEX6 neighbours.  A generous native search domain prevents
    # large, oblique blobs from clipping at the edge of the candidate space.
    domain_radius = max(4, int(math.ceil(radius * 2.6)) + 5)
    for _ in range(min(24, max(1, int(attempts)))):
        angle = rng.random() * math.pi
        phase = rng.random() * math.tau
        phase_two = rng.random() * math.tau
        phase_three = rng.random() * math.tau
        phase_four = rng.random() * math.tau
        phase_five = rng.random() * math.tau
        phase_six = rng.random() * math.tau
        phase_seven = rng.random() * math.tau
        ca, sa = math.cos(angle), math.sin(angle)
        # Keep the result rounded in screen space while allowing genuinely
        # different silhouettes.  The wider range is compensated by the
        # projected metric above, so it does not become a fixed parallelogram.
        aspect = rng.uniform(0.68, 1.42)
        axis_u = radius * math.sqrt(aspect)
        axis_v = radius / math.sqrt(aspect)
        wave_one = rng.uniform(0.04, 0.13)
        wave_two = rng.uniform(0.16, 0.34)
        wave_three = rng.uniform(0.08, 0.22)
        wave_four = rng.uniform(0.035, 0.12)
        wave_five = rng.uniform(0.015, 0.075)

        def priority(x: int, y: int) -> float:
            # Keep this transform in sync with ``project_parallelogram``.
            metric_x, metric_y = 2 * x - y, 2 * y
            u = ca * metric_x + sa * metric_y
            v = -sa * metric_x + ca * metric_y
            theta = math.atan2(v, u) if (u or v) else phase
            # Angular harmonics move complete arcs at once.  The two broad
            # spatial waves provide additional smooth variation at larger
            # deposits, while staying far below a one-cell random perturbation.
            wave = wave_one * math.sin(theta + phase_four)
            wave += wave_two * math.sin(2.0 * theta + phase)
            wave += wave_three * math.sin(3.0 * theta + phase_two)
            wave += wave_four * math.sin(4.0 * theta + phase_three)
            wave += wave_five * math.sin(5.0 * theta + phase_five)
            wave += 0.055 * math.sin(0.29 * u + 0.17 * v + phase_six)
            wave += 0.035 * math.cos(0.21 * u - 0.27 * v + phase_seven)
            return (u / (axis_u + 1e-6)) ** 2 + (v / (axis_v + 1e-6)) ** 2 + wave

        heap: list[tuple[float, int, int]] = [(priority(0, 0), 0, 0)]
        seen = {(0, 0)}
        chosen: list[tuple[int, int]] = []
        while heap and len(chosen) < target:
            _, x, y = heapq.heappop(heap)
            chosen.append((x, y))
            for dx, dy in HEX6:
                nx, ny = x + dx, y + dy
                if (nx, ny) in seen:
                    continue
                if hex_distance(0, 0, nx, ny) > domain_radius:
                    continue
                seen.add((nx, ny))
                heapq.heappush(heap, (priority(nx, ny), nx, ny))
        if len(chosen) != target:
            continue
        points = set(chosen)
        xs = [x for x, _ in chosen]
        ys = [y for _, y in chosen]
        footprint_area = (max(xs) - min(xs) + 1) * (max(ys) - min(ys) + 1)
        if _has_hole(points) or target / max(1, footprint_area) < 0.28:
            continue
        return chosen

    # This fallback is deterministic and retains the exact-area guarantee if a
    # caller supplies an unusual RNG or an unexpectedly constrained target.
    return compact_hex_offsets(target, rng)


def transition_rings(
    core: list[tuple[int, int]] | set[tuple[int, int]],
    depth: int = 2,
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    """Return the first and second HEX6 rings around a complete core."""

    occupied = set(core)
    frontier = set(core)
    rings: list[list[tuple[int, int]]] = []
    for _ in range(max(0, int(depth))):
        next_ring = {
            (x + dx, y + dy)
            for x, y in frontier
            for dx, dy in HEX6
            if (x + dx, y + dy) not in occupied
        }
        occupied.update(next_ring)
        frontier = next_ring
        rings.append(sorted(next_ring))
    first = rings[0] if rings else []
    second = rings[1] if len(rings) > 1 else []
    return first, second
