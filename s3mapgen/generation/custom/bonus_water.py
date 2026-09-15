"""Geometry helpers for start lakes and their water depth.

The native generator does not draw a perfect geometric disc for a significant
lake: the outline is connected, rounded and varies at a broad scale.  The
Custom start bonus keeps the exact hexagon as an explicit compatibility
option, while this module supplies a bounded native-like footprint and the
small depth field needed to write water levels consistently.
"""

from __future__ import annotations

from collections import deque
import random

import numpy as np

from ...map_data.constants import HEX6
from ...map_data.hexgrid import distance_from, hex_distance
from .bonus_minerals import compact_hex_offsets, hex_disc_offsets, organic_offsets


def native_lake_offsets(
    radius: int,
    rng: random.Random,
    *,
    attempts: int = 32,
) -> list[tuple[int, int]]:
    """Return one connected, rounded lake footprint inside ``radius``.

    ``organic_offsets`` uses the same projected-space compensation as the
    Upgraded mineral blobs.  A lower, varied fill factor leaves broad coves
    and lobes instead of a disc with a noisy edge; clipping is only used as a
    final bounded fallback and never changes the user's radius limit.
    """

    radius = max(1, int(radius))
    full_area = len(hex_disc_offsets(radius))
    if radius <= 2:
        # Small lakes are too small to benefit from a second contour family;
        # keep their complete inner water body stable and easy to route from.
        return compact_hex_offsets(full_area, rng)

    lower = max(1, int(round(full_area * 0.62)))
    upper = max(lower, int(round(full_area * 0.84)))
    for _ in range(max(1, int(attempts))):
        target = rng.randint(lower, upper)
        points = organic_offsets(target, rng, attempts=12)
        bounded = [
            point
            for point in points
            if hex_distance(0, 0, int(point[0]), int(point[1])) <= radius
        ]
        if len(bounded) < lower or (0, 0) not in bounded:
            continue
        # The frontier grown by ``organic_offsets`` is connected; intersecting
        # it with the convex HEX6 disc preserves that property in practice.
        # Verify it explicitly because this function is also used by importers
        # with custom geometry helpers.
        point_set = set(bounded)
        reached = {(0, 0)}
        queue = deque([(0, 0)])
        while queue:
            x, y = queue.popleft()
            for dx, dy in HEX6:
                neighbour = (x + dx, y + dy)
                if neighbour in point_set and neighbour not in reached:
                    reached.add(neighbour)
                    queue.append(neighbour)
        if len(reached) != len(point_set):
            continue
        return bounded

    # Deterministic safety net.  It remains rounded and connected and, unlike
    # an unconstrained organic fallback, can never exceed the requested cap.
    return compact_hex_offsets(max(1, int(round(full_area * 0.70))), rng)


def water_depths(points: list[tuple[int, int]] | set[tuple[int, int]]) -> dict[tuple[int, int], int]:
    """Return Water0..Water7 levels measured inward from a lake shoreline."""

    core = set(points)
    if not core:
        return {}
    boundary = {
        point
        for point in core
        if any((point[0] + dx, point[1] + dy) not in core for dx, dy in HEX6)
    }
    distances = {point: 0 for point in boundary}
    queue = deque(boundary)
    while queue:
        x, y = queue.popleft()
        level = distances[(x, y)] + 1
        for dx, dy in HEX6:
            neighbour = (x + dx, y + dy)
            if neighbour in core and neighbour not in distances:
                distances[neighbour] = level
                queue.append(neighbour)
    return {point: min(7, int(level)) for point, level in distances.items()}


def _native_direction(direction: int) -> int:
    """Wrap a native direction number to the six HEX6 directions."""

    return ((int(direction) - 1) % 6) + 1


def _river_score(height, x: int, y: int, offset: int) -> int:
    """Use the same local relief score as the native river routine."""

    candidate = int(height[y, x])
    score = 0
    for dx, dy in HEX6:
        xx, yy = x + dx, y + dy
        if 0 <= yy < height.shape[0] and 0 <= xx < height.shape[1]:
            neighbour = int(height[yy, xx])
        else:
            neighbour = 0
        score += neighbour - candidate + int(offset)
    return int(score)


def trace_native_river(
    terrain,
    height,
    start: tuple[int, int],
    target: "object",
    passable: "object",
    *,
    rng: random.Random,
    forbidden: "object | None" = None,
    prefix: list[tuple[int, int]] | None = None,
    distance_field: "object | None" = None,
    max_steps: int | None = None,
) -> list[tuple[int, int]] | None:
    """Trace one bonus river with the native river's local decision rules.

    ``start`` is the outside mouth of a bonus lake.  The tracer only writes
    cells selected by the caller as legal grass; it stops immediately before
    the first HEX6 contact with ``target`` (normally native Water or River),
    so it never overwrites an existing hydrology system.  The search keeps
    the native three-direction fan, height score and gentle same-direction
    limit, but adds bounded backtracking and target-distance guidance.  This
    retains the rounded, meandering native character while making a required
    bonus connection deterministic and collision-safe.

    ``prefix`` contains already occupied mouth cells (inner shore, then
    outer shore) and is returned as part of the route.  Those cells are not
    required to be passable because the caller will convert them to River.
    """

    height_array = height
    target_mask = np.asarray(target, dtype=bool)
    passable_mask = np.asarray(passable, dtype=bool).copy()
    forbidden_mask = (
        np.asarray(forbidden, dtype=bool)
        if forbidden is not None
        else np.zeros_like(passable_mask, dtype=bool)
    )
    side_y, side_x = passable_mask.shape
    sx, sy = map(int, start)
    if not (0 <= sx < side_x and 0 <= sy < side_y):
        return None

    prefix_points = list(prefix or [])
    if not prefix_points or prefix_points[-1] != (sx, sy):
        prefix_points.append((sx, sy))
    if any(
        not (0 <= x < side_x and 0 <= y < side_y)
        for x, y in prefix_points
    ):
        return None
    if any(target_mask[y, x] for x, y in prefix_points):
        return None

    # The native routine is deliberately conservative around its marker
    # field.  Bonus routes use an equivalent local exclusion mask for already
    # committed routes, while allowing the immediately adjacent next cell so
    # that the river remains one HEX6-connected chain.
    allowed = passable_mask.copy()
    for x, y in prefix_points:
        allowed[y, x] = True
    if distance_field is None:
        routing_sources = target_mask.copy()
        for x, y in prefix_points:
            routing_sources[y, x] = False
        distances = distance_from(routing_sources, passable=allowed)
    else:
        distances = np.asarray(distance_field)
        if distances.shape != passable_mask.shape:
            return None
    start_distance = int(distances[sy, sx])
    if start_distance >= 32767:
        return None

    def touches_target(x: int, y: int) -> bool:
        return any(
            0 <= x + dx < side_x
            and 0 <= y + dy < side_y
            and bool(target_mask[y + dy, x + dx])
            for dx, dy in HEX6
        )

    if touches_target(sx, sy):
        return prefix_points

    # Native paths are short local systems.  A bonus connection may begin
    # farther from water, so extend only by a bounded margin over the exact
    # target distance; this prevents an accidental map-wide search.
    if max_steps is None:
        max_steps = max(48, start_distance + 32)
    max_steps = max(2, min(int(max_steps), side_x * side_y))

    path = list(prefix_points)
    seen = set(path)
    previous_direction = 0
    same_direction_count = 0
    offset = 2

    def candidate_rows(
        x: int,
        y: int,
        scan_start: int,
        current_distance: int,
        previous_direction: int = 0,
        same_direction_count: int = 0,
    ):
        fan = [
            _native_direction(scan_start + slot)
            for slot in range(3)
        ]
        def collect(directions, enforce_turn: bool = True):
            candidates = []
            for direction in directions:
                dx, dy = HEX6[direction - 1]
                xx, yy = x + dx, y + dy
                if not (1 <= xx < side_x - 1 and 1 <= yy < side_y - 1):
                    continue
                if (xx, yy) in seen or forbidden_mask[yy, xx]:
                    continue
                if not allowed[yy, xx] or target_mask[yy, xx]:
                    continue
                candidate_distance = int(distances[yy, xx])
                # Permit a lateral meander on the same distance contour, but
                # never a step that moves farther from the eventual contact.
                # The native loop changes direction after three repeats; do
                # the same here so a flat relief cannot produce a ruler line.
                if candidate_distance > current_distance:
                    continue
                if same_direction_count < 2 and candidate_distance >= current_distance:
                    continue
                if (
                    same_direction_count >= 2
                    and direction == previous_direction
                    and enforce_turn
                ):
                    continue
                height_delta = int(height_array[y, x]) - int(height_array[yy, xx])
                if height_delta > 1:
                    continue
                score = _river_score(height_array, xx, yy, offset)
                progress = current_distance - candidate_distance
                candidates.append((
                    int(progress), int(score), rng.random(), direction, xx, yy,
                ))
            return candidates

        candidates = collect(fan, enforce_turn=True)
        # When a constrained relief blocks the native fan, use the remaining
        # directions only as a backtracking fallback, still scored identically.
        if not candidates:
            candidates = collect(fan, enforce_turn=False)
        if not candidates:
            candidates = collect(
                (direction for direction in range(1, 7) if direction not in fan),
                enforce_turn=False,
            )
        candidates.sort(key=lambda row: (-row[0], -row[1], row[2]))
        return candidates

    # A small explicit DFS gives the native routine's backtrack behavior but
    # keeps alternate fan directions available after an obstacle.
    first_candidates = []
    for direction, (dx, dy) in enumerate(HEX6, start=1):
        xx, yy = sx + dx, sy + dy
        if (
            0 <= xx < side_x
            and 0 <= yy < side_y
            and allowed[yy, xx]
            and not target_mask[yy, xx]
            and not forbidden_mask[yy, xx]
        ):
            first_candidates.append((int(height_array[yy, xx]), direction))
    if not first_candidates:
        return None
    first_candidates.sort(key=lambda row: row[0])
    first_direction = first_candidates[0][1]
    scan_start = _native_direction(first_direction - 1)

    stack: list[dict[str, object]] = []
    search_budget = max(4096, min(20000, max_steps * 8))
    search_nodes = 0
    current = (sx, sy)
    current_distance = start_distance
    stack.append({
        "point": current,
        "distance": current_distance,
        "scan_start": scan_start,
        "candidates": candidate_rows(sx, sy, scan_start, current_distance),
        "index": 0,
        "incoming": 0,
    })

    while stack:
        search_nodes += 1
        if search_nodes > search_budget:
            break
        frame = stack[-1]
        x, y = frame["point"]  # type: ignore[assignment]
        if touches_target(int(x), int(y)):
            return path
        if len(path) >= max_steps:
            stack.pop()
            if len(path) > len(prefix_points):
                seen.discard(path.pop())
            continue
        candidates = frame["candidates"]  # type: ignore[assignment]
        index = int(frame["index"])
        if index >= len(candidates):
            stack.pop()
            if len(path) > len(prefix_points):
                seen.discard(path.pop())
            continue
        frame["index"] = index + 1
        _progress, _score, _tie, direction, xx, yy = candidates[index]
        point = (int(xx), int(yy))
        if point in seen or forbidden_mask[point[1], point[0]]:
            continue
        path.append(point)
        seen.add(point)
        if direction == previous_direction:
            same_direction_count += 1
        else:
            previous_direction = int(direction)
            same_direction_count = 1
        # Match the native offset update: descending steps relax the next
        # score, while a climb may force a turn after three repeats.
        old_height = int(height_array[int(y), int(x)])
        new_height = int(height_array[point[1], point[0]])
        offset = min(new_height - old_height + 1, 2)
        next_scan = _native_direction(int(direction) - 1)
        if same_direction_count >= 3:
            next_scan = _native_direction(int(direction))
        next_distance = int(distances[point[1], point[0]])
        stack.append({
            "point": point,
            "distance": next_distance,
            "scan_start": next_scan,
            "candidates": candidate_rows(
                point[0],
                point[1],
                next_scan,
                next_distance,
                previous_direction,
                same_direction_count,
            ),
            "index": 0,
            "incoming": int(direction),
        })

    # A constrained relief can exhaust the native backtracking tree even
    # though a legal monotone route exists.  Keep the same fan/height score in
    # a bounded greedy retry so one difficult mouth does not force the caller
    # to scan every possible shoreline candidate.
    fallback_path = list(prefix_points)
    fallback_seen = set(fallback_path)
    current = (sx, sy)
    current_distance = start_distance
    previous_direction = 0
    same_direction_count = 0
    offset = 2
    for _ in range(max_steps):
        if touches_target(*current):
            return fallback_path
        candidates = []
        for direction, (dx, dy) in enumerate(HEX6, start=1):
            xx, yy = current[0] + dx, current[1] + dy
            if not (1 <= xx < side_x - 1 and 1 <= yy < side_y - 1):
                continue
            if (xx, yy) in fallback_seen or forbidden_mask[yy, xx]:
                continue
            if not allowed[yy, xx] or target_mask[yy, xx]:
                continue
            candidate_distance = int(distances[yy, xx])
            if candidate_distance > current_distance:
                continue
            if same_direction_count >= 2 and direction == previous_direction:
                continue
            if int(height_array[current[1], current[0]]) - int(height_array[yy, xx]) > 1:
                continue
            candidates.append((
                candidate_distance,
                _river_score(height_array, xx, yy, offset),
                rng.random(),
                direction,
                xx,
                yy,
            ))
        if not candidates:
            # The native height guard is a preference, not a reason to leave
            # a required bonus unconnected.  Retry the same local fan without
            # that guard before declaring the route impossible.
            for direction, (dx, dy) in enumerate(HEX6, start=1):
                xx, yy = current[0] + dx, current[1] + dy
                if not (1 <= xx < side_x - 1 and 1 <= yy < side_y - 1):
                    continue
                if (xx, yy) in fallback_seen or forbidden_mask[yy, xx]:
                    continue
                if not allowed[yy, xx] or target_mask[yy, xx]:
                    continue
                candidate_distance = int(distances[yy, xx])
                if candidate_distance > current_distance:
                    continue
                if same_direction_count >= 2 and direction == previous_direction:
                    continue
                candidates.append((
                    candidate_distance,
                    _river_score(height_array, xx, yy, offset),
                    rng.random(),
                    direction,
                    xx,
                    yy,
                ))
        if not candidates:
            break
        # Prefer actual progress, but use the native relief score and a random
        # tie-break inside that distance band to retain meanders.
        best_distance = min(row[0] for row in candidates)
        best = [row for row in candidates if row[0] == best_distance]
        best.sort(key=lambda row: (-row[1], row[2]))
        _distance, _score, _tie, direction, xx, yy = best[0]
        point = (int(xx), int(yy))
        fallback_path.append(point)
        fallback_seen.add(point)
        if direction == previous_direction:
            same_direction_count += 1
        else:
            previous_direction = int(direction)
            same_direction_count = 1
        old_height = int(height_array[current[1], current[0]])
        new_height = int(height_array[point[1], point[0]])
        offset = min(new_height - old_height + 1, 2)
        current = point
        current_distance = int(distances[current[1], current[0]])
    return None


__all__ = ("native_lake_offsets", "trace_native_river", "water_depths")
