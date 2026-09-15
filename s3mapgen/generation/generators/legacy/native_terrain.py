"""Native Settlers III terrain-generation core.

This module is deliberately narrower than the application-facing generator.
It owns the native map pass: the temporary native work bytes, height
refinement, rivers, terrain-family transitions, global static objects,
mountain resources, fish and the two mirror-axis copies.  Player-start
objects/resources, settlers and SAV-only records belong to later layers and
remain intentionally deferred.

The implementation follows the established native behavior.  The native PRNG is
reproduced exactly.  The application seed is passed to the PRNG as its 32-bit
input; the active map side remains an independent argument so the project can
expose deterministic seeds while the unresolved call-site seed transform stays
explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


MAX_SIDE = 1024

WATER = 0x00
GRASS = 0x10
ROCK = 0x20
SHORE = 0x30
DESERT = 0x40
SWAMP = 0x50
RIVER_FIRST = 0x60
RIVER_LAST = 0x63
SNOW = 0x80
MUD = 0x90

TEMP_70 = 0x70
TEMP_F0 = 0xF0
TEMP_F3 = 0xF3

# This is the native memory order, not a renderer's clockwise order.
HEX6 = ((1, 0), (1, 1), (0, 1), (-1, 0), (-1, -1), (0, -1))


@dataclass
class NativeTerrainGrid:
    """Primary native working fields for one active square."""

    side: int
    height: np.ndarray
    terrain: np.ndarray
    marker: np.ndarray
    variant: np.ndarray
    objects: np.ndarray
    resources: np.ndarray
    object_flags: np.ndarray

    @classmethod
    def empty(cls, side: int) -> "NativeTerrainGrid":
        shape = (int(side), int(side))
        return cls(
            int(side),
            np.zeros(shape, dtype=np.uint8),
            np.zeros(shape, dtype=np.uint8),
            np.full(shape, 0x1F, dtype=np.uint8),
            np.zeros(shape, dtype=np.uint8),
            np.zeros(shape, dtype=np.uint8),
            np.zeros(shape, dtype=np.uint8),
            np.zeros(shape, dtype=np.uint8),
        )


@dataclass(frozen=True)
class NativeTerrainResult:
    """Terrain fields returned to the MAP/EDM-facing layer."""

    height: np.ndarray
    terrain: np.ndarray
    variant: np.ndarray
    marker: np.ndarray
    metadata: dict[str, object]
    objects: np.ndarray | None = None
    resources: np.ndarray | None = None
    object_flags: np.ndarray | None = None
    deferred: "DeferredTerrainPass | None" = None


class NativeRng16:
    """Three-word 16-bit generator used by the native pipeline."""

    __slots__ = ("a", "b", "c")

    def __init__(self, value: int) -> None:
        value = int(value) & 0xFFFFFFFF
        self.a = value & 0xFFFF
        self.b = (value + 1000) & 0xFFFF
        self.c = (value + 2000) & 0xFFFF

    @staticmethod
    def _ror16(value: int, count: int = 1) -> int:
        value &= 0xFFFF
        return ((value >> count) | (value << (16 - count))) & 0xFFFF

    def next(self) -> int:
        sum_ab = (self.b + self.a) & 0xFFFF
        next_a = (sum_ab ^ self.c) & 0xFFFF
        next_c_before_rotate = (self.c + self.b) & 0xFFFF
        # The native call site always rotates once.  Inline that fixed rotate
        # here; keeping the standalone helper above preserves its useful
        # calibration/API semantics without paying two Python calls per RNG
        # sample in the generator hot path.
        rotated_b = (self.b ^ next_c_before_rotate) & 0xFFFF
        next_b = ((rotated_b >> 1) | (rotated_b << 15)) & 0xFFFF
        next_c = (
            (next_c_before_rotate >> 1) | (next_c_before_rotate << 15)
        ) & 0xFFFF
        self.a, self.b, self.c = next_a, next_b, next_c
        return self.a


def _byte(value: int) -> int:
    return int(value) & 0xFF


def _random_scaled(rng: NativeRng16, span: int) -> int:
    return (rng.next() * int(span)) >> 16


def _midpoint_value(rng: NativeRng16, first: int, second: int, scale: int) -> int:
    middle = (int(first) + int(second)) >> 1
    delta = (110 * int(scale)) >> 6
    low = max(middle - delta, 0)
    high = min(middle + delta, 255)
    return low + ((rng.next() * (high - low)) >> 16)


def _inside(grid: NativeTerrainGrid, row: int, col: int) -> bool:
    return 0 <= int(row) < grid.side and 0 <= int(col) < grid.side


def _interior(grid: NativeTerrainGrid, row: int, col: int) -> bool:
    return 1 <= int(row) < grid.side - 1 and 1 <= int(col) < grid.side - 1


def _height_at(grid: NativeTerrainGrid, row: int, col: int) -> int:
    # The original object reserves a 768-wide backing store.  Reads outside
    # the active square are treated as zero here rather than risking Python's
    # negative-index wrapping; valid native-size paths never depend on their
    # contents for the primary result.
    row, col = int(row), int(col)
    return int(grid.height[row, col]) if 0 <= row < grid.side and 0 <= col < grid.side else 0


def _terrain_at(grid: NativeTerrainGrid, row: int, col: int) -> int:
    row, col = int(row), int(col)
    return int(grid.terrain[row, col]) if 0 <= row < grid.side and 0 <= col < grid.side else WATER


def _marker_at(grid: NativeTerrainGrid, row: int, col: int) -> int:
    row, col = int(row), int(col)
    return int(grid.marker[row, col]) if 0 <= row < grid.side and 0 <= col < grid.side else 0


def _set_height(grid: NativeTerrainGrid, row: int, col: int, value: int) -> None:
    if _inside(grid, row, col):
        grid.height[row, col] = _byte(value)


def _set_terrain(grid: NativeTerrainGrid, row: int, col: int, value: int) -> None:
    if _inside(grid, row, col):
        grid.terrain[row, col] = _byte(value)


def _set_marker(grid: NativeTerrainGrid, row: int, col: int, value: int) -> None:
    if _inside(grid, row, col):
        grid.marker[row, col] = _byte(value)


def _set_variant(grid: NativeTerrainGrid, row: int, col: int, value: int) -> None:
    if _inside(grid, row, col):
        grid.variant[row, col] = _byte(value)


def _has_neighbour(grid: NativeTerrainGrid, row: int, col: int, terrain: int) -> bool:
    return any(
        _terrain_at(grid, row + dr, col + dc) == int(terrain)
        for dr, dc in HEX6
    )


def _neighbour_mask(field: np.ndarray, value: int) -> np.ndarray:
    """Return cells touching ``value`` in the native HEX6 topology."""

    result = np.zeros(field.shape, dtype=bool)
    side = field.shape[0]
    for dr, dc in HEX6:
        r0, r1 = max(0, dr), min(side, side + dr)
        c0, c1 = max(0, dc), min(side, side + dc)
        sr0, sr1 = max(0, -dr), min(side, side - dr)
        sc0, sc1 = max(0, -dc), min(side, side - dc)
        result[r0:r1, c0:c1] |= field[sr0:sr1, sc0:sc1] == int(value)
    return result


def _initialize_cells(grid: NativeTerrainGrid) -> None:
    grid.height.fill(0)
    grid.terrain.fill(WATER)
    grid.marker.fill(0x1F)
    grid.variant.fill(0)
    grid.objects.fill(0)
    grid.resources.fill(0)
    grid.object_flags.fill(0)


def _seed_coarse_relief(grid: NativeTerrainGrid, rng: NativeRng16) -> None:
    if grid.side <= 64:
        return
    for col in range(64, grid.side, 64):
        for row in range(64, grid.side, 64):
            outer_band = (
                row < 65 or row > grid.side - 65
                or col < 65 or col > grid.side - 65
            )
            inner_band = (
                row < 129 or row > grid.side - 129
                or col < 129 or col > grid.side - 129
            )
            if outer_band:
                value = _random_scaled(rng, 120)
            elif inner_band:
                value = _random_scaled(rng, 250)
            else:
                value = 50 + _random_scaled(rng, 200)
            grid.height[row, col] = value


def _refine_relief(grid: NativeTerrainGrid, rng: NativeRng16) -> None:
    for scale in (32, 16, 8, 4, 2, 1):
        step = 2 * scale
        for col in range(0, grid.side, step):
            for row in range(0, grid.side, step):
                nominal_row_end = row + step
                nominal_col_end = col + step
                if nominal_row_end > grid.side or nominal_col_end > grid.side:
                    raise ValueError(
                        "native relief refinement requires a side divisible by 64"
                    )
                row_end = grid.side - 1 if nominal_row_end == grid.side else nominal_row_end
                col_end = grid.side - 1 if nominal_col_end == grid.side else nominal_col_end
                zero_vertical = col == 0 or (
                    scale <= 16 and (row == 0 or row_end == grid.side - 1)
                )
                zero_horizontal = row == 0 or (
                    scale <= 16 and (col == 0 or col_end == grid.side - 1)
                )
                zero_diagonal = scale <= 16 and (
                    row == 0 or row_end == grid.side - 1
                    or col == 0 or col_end == grid.side - 1
                )
                top_left = int(grid.height[row, col])
                grid.height[row + scale, col] = (
                    0 if zero_vertical else _midpoint_value(
                        rng, top_left, int(grid.height[row_end, col]), scale
                    )
                )
                grid.height[row, col + scale] = (
                    0 if zero_horizontal else _midpoint_value(
                        rng, top_left, int(grid.height[row, col_end]), scale
                    )
                )
                grid.height[row + scale, col + scale] = (
                    0 if zero_diagonal else _midpoint_value(
                        rng, top_left, int(grid.height[row_end, col_end]), scale
                    )
                )


def _normalize_relief(grid: NativeTerrainGrid) -> None:
    raw = grid.height.astype(np.int16)
    grid.height[:] = np.where(raw < 0x1F, 0, raw - 0x1E).astype(np.uint8)


def _sculpt_density_guard(grid: NativeTerrainGrid, row: int, col: int) -> bool:
    count = sum(
        _terrain_at(grid, row + dr, col + dc) in (TEMP_70, TEMP_F0)
        for dr, dc in HEX6
    )
    return count <= 2


def _sculpt_proximity_guard(grid: NativeTerrainGrid, row: int, col: int) -> bool:
    positions = (
        (0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (-1, -1), (0, 2), (-1, 1), (1, 2),
    )
    return not any(_terrain_at(grid, row + dr, col + dc) == TEMP_70 for dr, dc in positions)


def _sculpt_candidate(grid: NativeTerrainGrid, row: int, col: int) -> None:
    height = _height_at(grid, row, col)
    diagonal_height = _height_at(grid, row, col + 1)
    if not (height > 30 and height < 100 and height - 10 > diagonal_height):
        return
    if not _sculpt_proximity_guard(grid, row, col):
        return

    _set_terrain(grid, row, col, TEMP_70)
    _set_terrain(grid, row, col + 1, TEMP_F0)
    current_row, current_col = row, col
    state = 3
    pass_index = 0
    failed = False
    steps = 0
    max_steps = max(64, grid.side * 8)

    while True:
        steps += 1
        if steps > max_steps:
            raise RuntimeError(
                f"La sculpture native du relief ne progresse pas autour de "
                f"({row},{col}) pour {grid.side}x{grid.side} "
                f"(limite de {max_steps} étapes)"
            )
        if pass_index == 0:
            if state == 4:
                delta = _height_at(grid, current_row - 1, current_col - 1) - _height_at(grid, current_row - 1, current_col)
                if delta <= 5 or not _sculpt_density_guard(grid, current_row - 1, current_col - 1):
                    failed = True
                else:
                    _set_terrain(grid, current_row - 1, current_col - 1, TEMP_70)
                    current_row -= 1
                    current_col -= 1
                    state = 3
            elif state == 3:
                if not _sculpt_density_guard(grid, current_row - 1, current_col):
                    failed = True
                else:
                    d1 = _height_at(grid, current_row, current_col) - _height_at(grid, current_row - 1, current_col)
                    d2 = _height_at(grid, current_row - 1, current_col) - _height_at(grid, current_row, current_col + 1)
                    if d2 <= d1:
                        if d1 <= 5:
                            failed = True
                        else:
                            _set_terrain(grid, current_row - 1, current_col, TEMP_F0)
                            state = 4
                    elif d2 <= 5:
                        failed = True
                    else:
                        _set_terrain(grid, current_row - 1, current_col, TEMP_70)
                        current_row -= 1
                        state = 2
            elif state == 2:
                if not _sculpt_density_guard(grid, current_row, current_col + 1):
                    failed = True
                else:
                    d1 = _height_at(grid, current_row, current_col) - _height_at(grid, current_row, current_col + 1)
                    d2 = _height_at(grid, current_row, current_col + 1) - _height_at(grid, current_row + 1, current_col)
                    if d2 <= d1:
                        if d1 <= 5:
                            failed = True
                        else:
                            # This apparently asymmetric target is present in
                            # the native block and is intentional.
                            _set_terrain(grid, current_row - 1, current_col, TEMP_F0)
                            state = 4
                    elif d2 <= 5:
                        failed = True
                    else:
                        _set_terrain(grid, current_row - 1, current_col, TEMP_70)
                        current_row -= 1
                        state = 2
            elif state == 1:
                delta = _height_at(grid, current_row, current_col) - _height_at(grid, current_row + 1, current_col)
                if delta <= 5 or not _sculpt_density_guard(grid, current_row + 1, current_col + 1):
                    failed = True
                else:
                    _set_terrain(grid, current_row + 1, current_col + 1, TEMP_F0)
                    state = 2
            else:
                failed = True
        else:
            if state == 4:
                delta = _height_at(grid, current_row, current_col) - _height_at(grid, current_row, current_col + 1)
                if delta <= 5 or not _sculpt_density_guard(grid, current_row, current_col + 1):
                    failed = True
                else:
                    _set_terrain(grid, current_row, current_col + 1, TEMP_F0)
                    state = 3
            elif state == 3:
                if not _sculpt_density_guard(grid, current_row + 1, current_col + 1):
                    failed = True
                else:
                    d1 = _height_at(grid, current_row, current_col) - _height_at(grid, current_row + 1, current_col)
                    d2 = _height_at(grid, current_row + 1, current_col) - _height_at(grid, current_row, current_col + 1)
                    if d2 <= d1:
                        if d1 <= 5:
                            failed = True
                        else:
                            _set_terrain(grid, current_row + 1, current_col, TEMP_F0)
                            state = 2
                    elif d2 <= 5:
                        failed = True
                    else:
                        _set_terrain(grid, current_row + 1, current_col + 1, TEMP_70)
                        current_row += 1
                        current_col += 1
                        state = 4
            elif state == 2:
                if not _sculpt_density_guard(grid, current_row + 1, current_col):
                    failed = True
                else:
                    d1 = _height_at(grid, current_row, current_col) - _height_at(grid, current_row, current_col + 1)
                    d2 = _height_at(grid, current_row, current_col + 1) - _height_at(grid, current_row + 1, current_col)
                    if d2 <= d1:
                        if d1 <= 5:
                            failed = True
                        else:
                            _set_terrain(grid, current_row + 1, current_col, TEMP_F0)
                            state = 1
                    elif d2 <= 5:
                        failed = True
                    else:
                        _set_terrain(grid, current_row + 1, current_col, TEMP_70)
                        current_row += 1
                        state = 3
            elif state == 1:
                delta = _height_at(grid, current_row, current_col - 1) - _height_at(grid, current_row - 1, current_col)
                if delta <= 5 or not _sculpt_density_guard(grid, current_row, current_col - 1):
                    failed = True
                else:
                    _set_terrain(grid, current_row, current_col - 1, TEMP_70)
                    # The native block decrements the current column before
                    # entering state 2.  Omitting this update makes the
                    # state-1/state-2 pair revisit the same cell forever on
                    # some reliefs (notably seed 297650040 at 256x256).
                    current_col -= 1
                    state = 2
            else:
                failed = True

        current_height = _height_at(grid, current_row, current_col)
        if 30 <= current_height <= 100 and not failed:
            continue
        pass_index += 1
        if pass_index > 1:
            break
        current_row, current_col = row, col
        state = 3
        failed = False


def _consume_sculpture_markers(grid: NativeTerrainGrid) -> None:
    for row in range(1, grid.side - 1):
        for col in range(1, grid.side - 1):
            terrain = int(grid.terrain[row, col])
            if terrain == TEMP_70:
                grid.height[row, col] = _byte(int(grid.height[row, col]) + 8)
            elif terrain == TEMP_F0:
                grid.terrain[row, col] = TEMP_70
                grid.height[row, col] = _byte(int(grid.height[row, col]) - 8)


def _relax_relief(grid: NativeTerrainGrid, alternate_mode: bool) -> int:
    # This pass is intentionally kept in-place and ordered: the native
    # routine uses each write immediately for the following cell.  Binding
    # the three fields locally removes millions of bounds-check helper calls
    # while preserving that exact update order and uint8 wrapping.
    side = grid.side
    height = grid.height
    terrain = grid.terrain
    temp70 = terrain == TEMP_70
    changed = True
    passes = 0
    max_passes = 128
    while changed:
        passes += 1
        if passes > max_passes:
            raise RuntimeError(
                f"La relaxation native du relief ne converge pas pour {side}x{side} "
                f"(limite de {max_passes} passes)"
            )
        changed = False
        if not alternate_mode:
            for col in range(2, side):
                for row in range(1, side - 1):
                    left = int(height[row, col - 1])
                    low, high = left - 7, left + 5
                    center = int(height[row, col])
                    if center > high:
                        height[row, col] = high & 0xFF
                        changed = True
                        center = high
                    first_square = (
                        temp70[row, col - 1]
                        and temp70[row, col]
                        and temp70[row - 1, col - 1]
                        and temp70[row + 1, col]
                    )
                    if first_square:
                        if center < low - 16:
                            height[row, col - 1] = (center + 23) & 0xFF
                            changed = True
                    elif center < low:
                        height[row, col - 1] = (center + 7) & 0xFF
                        changed = True

                    south = int(height[row + 1, col])
                    if south > high:
                        height[row + 1, col] = high & 0xFF
                        changed = True
                        south = high
                    second_square = (
                        temp70[row, col - 1]
                        and temp70[row + 1, col]
                        and temp70[row, col]
                        and temp70[row + 1, col - 1]
                    )
                    if second_square:
                        if south < low - 16:
                            height[row, col - 1] = (south + 23) & 0xFF
                            changed = True
                    elif south < low:
                        height[row, col - 1] = (south + 7) & 0xFF
                        changed = True
        else:
            for col in range(2, side):
                for row in range(2, side):
                    northwest = int(height[row - 1, col - 1])
                    low, high = northwest - 5, northwest + 5
                    north = int(height[row - 1, col])
                    if north > high:
                        height[row - 1, col] = high & 0xFF
                        changed = True
                        north = high
                    if north < low:
                        height[row - 1, col - 1] = (north + 5) & 0xFF
                        changed = True
                    center = int(height[row, col])
                    if center > high:
                        height[row, col] = high & 0xFF
                        changed = True
                        center = high
                    if center < low:
                        height[row - 1, col - 1] = (center + 5) & 0xFF
                        changed = True
                    west = int(height[row, col - 1])
                    if west > high:
                        height[row, col - 1] = high & 0xFF
                        changed = True
                        west = high
                    if west < low:
                        height[row, col - 1] = (west + 5) & 0xFF
                        changed = True
    return passes


def _classify_relief(grid: NativeTerrainGrid) -> None:
    interior = (slice(1, -1), slice(1, -1))
    heights = grid.height[interior]
    grid.terrain[interior] = np.select(
        (heights == 0, heights < 0x8C, heights < 0xBE),
        (WATER, GRASS, ROCK),
        default=SNOW,
    ).astype(np.uint8)


def _clear_pre_river_fields(grid: NativeTerrainGrid) -> None:
    grid.variant.fill(0)
    grid.marker.fill(0)


def _normalize_outer_ocean_edge(grid: NativeTerrainGrid) -> None:
    """Keep the external rectangular edge on native deep-water level 7.

    Relief classification only writes the active interior, leaving the
    backing border at raw terrain 0 (the UI's ``Eau 1``).  Native maps keep
    that outer edge at raw water level 7 instead.  This pass is deliberately
    last because the mirror copies can write edge cells as part of their
    triangular traversal.
    """

    deep_edge = 0x07
    grid.terrain[0, :] = deep_edge
    grid.terrain[-1, :] = deep_edge
    grid.terrain[:, 0] = deep_edge
    grid.terrain[:, -1] = deep_edge
    grid.height[0, :] = 0
    grid.height[-1, :] = 0
    grid.height[:, 0] = 0
    grid.height[:, -1] = 0


def _route_free(grid: NativeTerrainGrid, row: int, col: int) -> bool:
    if not (0 <= row < grid.side and 0 <= col < grid.side):
        return False
    marker = grid.marker
    if int(marker[row, col]) != 0:
        return False
    if 1 <= row < grid.side - 1 and 1 <= col < grid.side - 1:
        return (
            int(marker[row + 1, col]) == 0
            and int(marker[row + 1, col + 1]) == 0
            and int(marker[row, col + 1]) == 0
            and int(marker[row - 1, col]) == 0
            and int(marker[row - 1, col - 1]) == 0
            and int(marker[row, col - 1]) == 0
        )
    return all(_marker_at(grid, row + dr, col + dc) == 0 for dr, dc in HEX6)


def _river_candidate_filter(
    grid: NativeTerrainGrid, row: int, col: int
) -> tuple[bool, bool]:
    if row < 8 or col < 8 or row > grid.side - 8 or col > grid.side - 8:
        return False, False
    # The margin check above guarantees that the following ±4 window is
    # inside the active square.  This is a hot filter (4*area probes), so
    # direct array reads retain the same values without helper dispatch.
    marker = int(grid.marker[row, col])
    terrain = int(grid.terrain[row, col])
    if terrain != WATER and marker < 2:
        return False, False
    continuation = marker >= 2
    if continuation:
        return True, True
    low_terrain_count = int(
        np.count_nonzero(grid.terrain[row - 4:row + 5, col - 4:col + 5] < 0x10)
    )
    return low_terrain_count > 25, False


def _choose_first_river_step(
    grid: NativeTerrainGrid, row: int, col: int, continuation: bool
) -> int:
    best_direction = 0
    best_height = 256
    marker = grid.marker
    terrain = grid.terrain
    height = grid.height
    saved_marker = int(marker[row, col])
    if continuation:
        marker[row, col] = 0
    for direction, (dr, dc) in enumerate(HEX6, start=1):
        next_row, next_col = row + dr, col + dc
        if (
            int(terrain[next_row, next_col]) == GRASS
            and int(marker[next_row, next_col]) == 0
            and int(marker[next_row + 1, next_col]) == 0
            and int(marker[next_row + 1, next_col + 1]) == 0
            and int(marker[next_row, next_col + 1]) == 0
            and int(marker[next_row - 1, next_col]) == 0
            and int(marker[next_row - 1, next_col - 1]) == 0
            and int(marker[next_row, next_col - 1]) == 0
        ):
            next_height = int(height[next_row, next_col])
            if next_height < best_height:
                best_height = next_height
                best_direction = direction
        if continuation:
            marker[row, col] = saved_marker
    if continuation:
        marker[row, col] = saved_marker
    return best_direction


def _wrap_direction(direction: int) -> int:
    return ((int(direction) - 1) % 6) + 1


def _river_window_conflict(grid: NativeTerrainGrid, row: int, col: int) -> bool:
    # Candidate filtering guarantees this 9x9 window is in-bounds.
    return bool(np.any(grid.marker[row - 4:row + 5, col - 4:col + 5] >= 8))


def _generate_rivers(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    *,
    rate_percent: float = 100.0,
) -> dict[str, int | float]:
    side = grid.side
    area = side * side
    height = grid.height
    terrain = grid.terrain
    marker = grid.marker
    river_rate = min(500.0, max(0.0, float(rate_percent)))
    # Keep the native attempt loop and its PRNG consumption unchanged.  A
    # Custom rate only scales the native acceptance threshold: at 100% the
    # native behavior is byte-for-byte on the same path, while 0%
    # and higher values remain variations of that same river algorithm.
    acceptance_threshold = int(round(0x07D0 * river_rate / 100.0))
    index = 0x600
    systems = 0
    river_cells = 0
    attempts = 4 * area

    for _ in range(attempts):
        q, r = divmod(index, side)
        index += 0x97
        if index >= area:
            index -= area
        if rng.next() >= acceptance_threshold:
            continue

        accepted, continuation = _river_candidate_filter(grid, r, q)
        if not accepted:
            continue
        first_direction = _choose_first_river_step(grid, r, q, continuation)
        if first_direction == 0 or _river_window_conflict(grid, r, q):
            continue

        start_row, start_col = r, q
        current_row, current_col = r, q
        path_limit = 7 if continuation else 16
        path_count = 1
        offset = 2
        previous_direction = 0
        same_direction_count = 0
        scan_start = _wrap_direction(first_direction - 1)
        if not continuation:
            marker[r, q] = 1
        first_dr, first_dc = HEX6[first_direction - 1]
        current_row += first_dr
        current_col += first_dc

        forward_steps = 0
        while True:
            forward_steps += 1
            if forward_steps > area + 1:
                raise RuntimeError(
                    f"La génération native des rivières ne progresse pas autour de "
                    f"({start_row},{start_col}) pour {grid.side}x{grid.side}"
                )
            scores = [0, 0, 0]
            direction = scan_start
            for slot in range(3):
                if not (same_direction_count >= 3 and direction == previous_direction):
                    dr, dc = HEX6[direction - 1]
                    candidate_row, candidate_col = current_row + dr, current_col + dc
                    candidate_inside = (
                        0 <= candidate_row < side and 0 <= candidate_col < side
                    )
                    candidate_height = (
                        int(height[candidate_row, candidate_col])
                        if candidate_inside else 0
                    )
                    height_delta = int(height[current_row, current_col]) - candidate_height
                    if (
                        candidate_inside
                        and int(terrain[candidate_row, candidate_col]) == GRASS
                        and _route_free(grid, candidate_row, candidate_col)
                        and height_delta <= 1
                    ):
                        if (
                            1 <= candidate_row < side - 1
                            and 1 <= candidate_col < side - 1
                        ):
                            score = (
                                int(height[candidate_row + 1, candidate_col])
                                + int(height[candidate_row + 1, candidate_col + 1])
                                + int(height[candidate_row, candidate_col + 1])
                                + int(height[candidate_row - 1, candidate_col])
                                + int(height[candidate_row - 1, candidate_col - 1])
                                + int(height[candidate_row, candidate_col - 1])
                                - (6 * candidate_height)
                                + (6 * offset)
                            )
                        else:
                            score = sum(
                                _height_at(grid, candidate_row + ndr, candidate_col + ndc)
                                - candidate_height + offset
                                for ndr, ndc in HEX6
                            )
                        scores[slot] = score
                direction = _wrap_direction(direction + 1)

            best_score = 0
            chosen_direction = 0
            direction = scan_start
            for slot in range(3):
                if scores[slot] > best_score:
                    best_score = scores[slot]
                    chosen_direction = direction
                direction = _wrap_direction(direction + 1)

            path_count += 1
            marker[current_row, current_col] = 1
            if chosen_direction:
                dr, dc = HEX6[chosen_direction - 1]
                old_height = int(height[current_row, current_col])
                next_row, next_col = current_row + dr, current_col + dc
                new_height = int(height[next_row, next_col])
                offset = min(new_height - old_height + 1, 2)
                if chosen_direction == previous_direction:
                    same_direction_count += 1
                else:
                    previous_direction = chosen_direction
                    same_direction_count = 1
                current_row, current_col = next_row, next_col
                scan_start = _wrap_direction(chosen_direction - 1)
                continue

            backtrack_direction = 0
            current_row, current_col = start_row, start_col
            backtrack_steps = 0
            while path_count < path_limit:
                backtrack_steps += 1
                if backtrack_steps > area + 1:
                    raise RuntimeError(
                        f"Le retour arrière natif d'une rivière boucle autour de "
                        f"({start_row},{start_col}) pour {grid.side}x{grid.side}"
                    )
                if backtrack_direction:
                    marker[current_row, current_col] = 0
                next_direction = 0
                for candidate_direction, (dr, dc) in enumerate(HEX6, start=1):
                    if _marker_at(grid, current_row + dr, current_col + dc) == 1:
                        next_direction = candidate_direction
                if not next_direction:
                    break
                dr, dc = HEX6[next_direction - 1]
                current_row += dr
                current_col += dc
                backtrack_direction = next_direction
            if path_count < path_limit:
                break

            current_row, current_col = start_row, start_col
            incoming_direction = 0
            trace_steps = 0
            while True:
                trace_steps += 1
                if trace_steps > area + 1:
                    raise RuntimeError(
                        f"Le tracé natif d'une rivière boucle autour de "
                        f"({start_row},{start_col}) pour {grid.side}x{grid.side}"
                    )
                terrain[current_row, current_col] = RIVER_FIRST
                if incoming_direction:
                    reverse = incoming_direction + 3
                    if reverse > 6:
                        reverse -= 6
                    marker[current_row, current_col] = reverse + 1
                elif not continuation:
                    marker[current_row, current_col] = 0x0E
                else:
                    marker[current_row, current_col] = int(marker[current_row, current_col]) + 6
                next_direction = 0
                for candidate_direction, (dr, dc) in enumerate(HEX6, start=1):
                    if _marker_at(grid, current_row + dr, current_col + dc) == 1:
                        next_direction = candidate_direction
                if not next_direction:
                    break
                dr, dc = HEX6[next_direction - 1]
                current_row += dr
                current_col += dc
                incoming_direction = next_direction

            if not continuation:
                break

            current_row, current_col = start_row, start_col
            continuation_steps = 0
            while True:
                continuation_steps += 1
                if continuation_steps > area + 1:
                    raise RuntimeError(
                        f"La reprise native d'une rivière boucle autour de "
                        f"({start_row},{start_col}) pour {grid.side}x{grid.side}"
                    )
                terrain_value = int(terrain[current_row, current_col])
                if terrain_value == 0x62:
                    terrain[current_row, current_col] = 0x63
                if terrain_value == 0x61:
                    terrain[current_row, current_col] = 0x62
                if terrain_value == 0x60:
                    terrain[current_row, current_col] = 0x61
                marker_value = int(marker[current_row, current_col])
                if marker_value < 2 or marker_value > 0x0E:
                    if _inside(grid, current_row, current_col):
                        grid.variant[current_row, current_col] = 1
                    break
                if marker_value == 0x0E:
                    break
                direction = marker_value - 1
                if direction > 6:
                    direction -= 6
                dr, dc = HEX6[direction - 1]
                current_row += dr
                current_col += dc
            break

        systems += 1
        river_cells += path_count

    for row in range(grid.side):
        for col in range(grid.side):
            if not RIVER_FIRST <= int(grid.terrain[row, col]) <= RIVER_LAST:
                continue
            incompatible = any(
                not _inside(grid, row + dr, col + dc)
                or not (
                    RIVER_FIRST <= _terrain_at(grid, row + dr, col + dc) <= RIVER_LAST
                    or _terrain_at(grid, row + dr, col + dc) in (GRASS, SHORE, WATER)
                )
                for dr, dc in HEX6
            )
            if incompatible:
                grid.terrain[row, col] = GRASS

    return {
        "river_attempts": attempts,
        "river_systems": systems,
        "river_cells": river_cells,
        "river_rate_percent": river_rate,
        "river_acceptance_threshold": acceptance_threshold,
    }


def _replace_global(grid: NativeTerrainGrid, source: int, target: int) -> None:
    interior = np.zeros(grid.terrain.shape, dtype=bool)
    interior[1:-1, 1:-1] = grid.terrain[1:-1, 1:-1] == int(source)
    grid.terrain[interior] = _byte(target)


def _replace_if_neighbour(
    grid: NativeTerrainGrid, source: int, trigger: int, target: int
) -> None:
    touching = _neighbour_mask(grid.terrain, trigger)
    region = np.zeros(grid.terrain.shape, dtype=bool)
    region[1:-1, 1:-1] = (
        (grid.terrain[1:-1, 1:-1] == int(source))
        & touching[1:-1, 1:-1]
    )
    grid.terrain[region] = _byte(target)


def _expand(
    grid: NativeTerrainGrid,
    target: int,
    source: int,
    protected_mask: np.ndarray | None = None,
) -> None:
    touching = _neighbour_mask(grid.terrain, target)
    region = np.zeros(grid.terrain.shape, dtype=bool)
    region[1:-1, 1:-1] = (
        (grid.terrain[1:-1, 1:-1] == int(source))
        & touching[1:-1, 1:-1]
    )
    if protected_mask is not None:
        region &= ~protected_mask
    grid.terrain[region] = TEMP_F0
    _replace_global(grid, TEMP_F0, target)


def _erode(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    target: int,
    source: int,
    chance: int,
    protected_mask: np.ndarray | None = None,
) -> None:
    touching = _neighbour_mask(grid.terrain, source)
    candidate = np.zeros(grid.terrain.shape, dtype=bool)
    candidate[1:-1, 1:-1] = (
        (grid.terrain[1:-1, 1:-1] == int(target))
        & touching[1:-1, 1:-1]
    )
    if protected_mask is not None:
        candidate[1:-1, 1:-1] &= ~protected_mask[1:-1, 1:-1]
    for row, col in np.argwhere(candidate):
        if ((rng.next() * 100) >> 16) < int(chance):
            grid.terrain[int(row), int(col)] = TEMP_F0
    _replace_global(grid, TEMP_F0, source)


def _brush_source_is_homogeneous(
    grid: NativeTerrainGrid, row: int, col: int, source: int
) -> bool:
    # ``_brush`` calls this only for interior cells, so every HEX6 read is
    # in-bounds.  Keep the short-circuit order of the native check while
    # avoiding a generator/helper call for each of the eight brush probes.
    terrain = grid.terrain
    source = int(source)
    return (
        int(terrain[row, col]) == source
        and int(terrain[row + 1, col]) == source
        and int(terrain[row + 1, col + 1]) == source
        and int(terrain[row, col + 1]) == source
        and int(terrain[row - 1, col]) == source
        and int(terrain[row - 1, col - 1]) == source
        and int(terrain[row, col - 1]) == source
    )


def _brush(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    source: int,
    target: int,
    coefficient: int,
    protected_mask: np.ndarray | None = None,
) -> int:
    n64 = (grid.side + (grid.side & 0x3F)) // 64
    groups = (n64 * n64 * int(coefficient)) // 8
    changed = 0
    for _ in range(groups):
        center_row = (rng.next() * grid.side) >> 16
        center_col = (rng.next() * grid.side) >> 16
        for _ in range(8):
            row = center_row + (rng.next() & 0x1F) - 0x10
            col = center_col + (rng.next() & 0x1F) - 0x10
            if not _interior(grid, row, col):
                continue
            if protected_mask is not None and protected_mask[row, col]:
                continue
            if int(grid.variant[row, col]) != 0:
                continue
            if _brush_source_is_homogeneous(grid, row, col, source):
                grid.terrain[row, col] = _byte(target)
                changed += 1
    return changed


def _protect_grass_boundary(grid: NativeTerrainGrid) -> None:
    """Temporarily mark Grass cells touching another terrain family.

    Grass and TEMP_F3 are equivalent for this predicate, so marking one
    cell cannot change whether a later cell is a boundary: it only changes
    one allowed value into the other.  The row-major loop can therefore be
    evaluated as one vectorized mask without changing the result.
    """

    terrain = grid.terrain
    interior = terrain[1:-1, 1:-1]
    boundary = interior == GRASS
    touching_invalid = np.zeros(boundary.shape, dtype=bool)
    side = grid.side
    for dr, dc in HEX6:
        neighbour = terrain[1 + dr:side - 1 + dr, 1 + dc:side - 1 + dc]
        touching_invalid |= (neighbour != GRASS) & (neighbour != TEMP_F3)
    boundary &= touching_invalid
    interior[boundary] = TEMP_F3


@dataclass(frozen=True)
class _FamilyPlan:
    target: int
    brushes: tuple[int, ...]
    expansions: tuple[int, ...]
    transition_chain: bool


_FAMILY_PLANS = (
    _FamilyPlan(DESERT, (2, 1), (5, 6), True),
    _FamilyPlan(SWAMP, (1, 1, 1), (2, 2, 1), True),
    _FamilyPlan(MUD, (1, 1), (3, 3), True),
    _FamilyPlan(0x18, (3, 2, 1), (2, 2, 3), False),
)


_FAMILY_PLAN_KEYS = ("desert", "swamp", "mud", "dry_grass")


def _scale_native_count(count: int, rate: float, *, expansion: bool = False) -> int:
    """Scale one native operation count without changing its operation type."""

    if rate <= 0.0:
        return 0
    if rate == 100.0:
        return int(count)
    factor = float(rate) / 100.0
    if expansion:
        # Brush probes control the number of zones.  Expansion changes more
        # gently so a high rate produces larger varied zones, not one huge
        # flood or a set of one-cell fragments.
        factor = (
            factor**0.75
            if factor < 1.0
            else 1.0 + min(0.8, (factor - 1.0) * 0.2)
        )
    return max(1, int(round(int(count) * factor)))


def _apply_family_plan(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    plan: _FamilyPlan,
    rate: float = 100.0,
    protected_mask: np.ndarray | None = None,
) -> None:
    _protect_grass_boundary(grid)
    for coefficient, expansion_count in zip(plan.brushes, plan.expansions):
        scaled_coefficient = _scale_native_count(coefficient, rate)
        if scaled_coefficient <= 0:
            continue
        _brush(
            grid,
            rng,
            GRASS,
            plan.target,
            scaled_coefficient,
            protected_mask,
        )
        scaled_expansions = _scale_native_count(
            expansion_count,
            rate,
            expansion=True,
        )
        for _ in range(scaled_expansions):
            _expand(grid, plan.target, GRASS, protected_mask)
    _replace_global(grid, TEMP_F3, GRASS)
    for chance in (80, 60, 40, 20):
        _erode(grid, rng, plan.target, GRASS, chance, protected_mask)
    if plan.transition_chain:
        if plan.target == DESERT:
            _replace_if_neighbour(grid, DESERT, GRASS, 0x14)
            _replace_if_neighbour(grid, DESERT, 0x14, 0x41)
        elif plan.target == SWAMP:
            _replace_if_neighbour(grid, SWAMP, GRASS, 0x15)
            _replace_if_neighbour(grid, SWAMP, 0x15, 0x51)
        elif plan.target == MUD:
            _replace_if_neighbour(grid, MUD, GRASS, 0x17)
            _replace_if_neighbour(grid, MUD, 0x17, 0x91)


def _copy_native_grid(grid: NativeTerrainGrid) -> NativeTerrainGrid:
    """Copy the fields needed for a diagnostic native reference pass."""

    return NativeTerrainGrid(
        grid.side,
        grid.height.copy(),
        grid.terrain.copy(),
        grid.marker.copy(),
        grid.variant.copy(),
        grid.objects.copy(),
        grid.resources.copy(),
        grid.object_flags.copy(),
    )


def _copy_native_rng(rng: NativeRng16) -> NativeRng16:
    clone = NativeRng16(0)
    clone.a, clone.b, clone.c = rng.a, rng.b, rng.c
    return clone


@dataclass
class DeferredTerrainPass:
    """Continuation used only by the bonus-priority generation route."""

    grid: NativeTerrainGrid
    rng: NativeRng16
    mode: int
    seed: int
    surface_rates: object
    custom_rates: dict[str, float] | None
    native_default_rates: dict[str, float]
    custom_mud_rate: float
    relief_relax_passes: int
    river_meta: dict[str, object]
    reference_grid: NativeTerrainGrid | None
    reference_rng: NativeRng16 | None
    disabled_object_families: tuple[str, ...]


def _apply_micro_terrain_brushes(
    grid: NativeTerrainGrid,
    rng: NativeRng16,
    rate: float = 100.0,
    protected_mask: np.ndarray | None = None,
) -> tuple[int, int, int]:
    if rate <= 0.0:
        return 0, 0, 0
    coefficient = _scale_native_count(2, rate)
    return (
        _brush(grid, rng, GRASS, 0x12, coefficient, protected_mask),
        _brush(grid, rng, GRASS, 0x13, coefficient, protected_mask),
        _brush(grid, rng, ROCK, 0x22, coefficient, protected_mask),
    )


def _apply_structural_transitions(grid: NativeTerrainGrid) -> None:
    _replace_if_neighbour(grid, WATER, GRASS, 0xFF)
    _replace_if_neighbour(grid, GRASS, 0xFF, 0xFE)
    _replace_global(grid, 0xFF, SHORE)
    _replace_global(grid, 0xFE, SHORE)

    _replace_if_neighbour(grid, WATER, SHORE, 0xFF)
    _replace_if_neighbour(grid, WATER, 0xFF, 0x01)
    _replace_if_neighbour(grid, WATER, 0x01, 0x02)
    _replace_if_neighbour(grid, WATER, 0x02, 0x03)
    _replace_if_neighbour(grid, WATER, 0x03, 0x04)
    _replace_if_neighbour(grid, WATER, 0x04, 0x05)
    _replace_if_neighbour(grid, WATER, 0x05, 0x06)
    _replace_if_neighbour(grid, WATER, 0x06, 0x07)
    _replace_global(grid, WATER, 0x07)
    _replace_global(grid, 0xFF, WATER)

    _replace_if_neighbour(grid, ROCK, GRASS, 0x11)
    _replace_if_neighbour(grid, ROCK, 0x11, 0x21)
    _replace_if_neighbour(grid, SNOW, ROCK, 0x23)
    _replace_if_neighbour(grid, SNOW, 0x23, 0x81)


def _set_mode_variant_sentinels(grid: NativeTerrainGrid, mode: int) -> None:
    if mode & 0x01:
        for i in range(grid.side):
            grid.variant[i, i] = 0xFF
    if mode & 0x02:
        for i in range(grid.side):
            grid.variant[i, grid.side - 1 - i] = 0xFF
        for i in range(grid.side - 1):
            grid.variant[i, grid.side - 2 - i] = 0xFF
            grid.variant[i + 1, grid.side - 1 - i] = 0xFF


def _clear_mode_variant_sentinels(grid: NativeTerrainGrid, mode: int) -> None:
    if mode & 0x01:
        for i in range(grid.side):
            grid.variant[i, i] = 0
    if mode & 0x02:
        for i in range(grid.side):
            grid.variant[i, grid.side - 1 - i] = 0
        for i in range(grid.side - 1):
            grid.variant[i, grid.side - 2 - i] = 0
            grid.variant[i + 1, grid.side - 1 - i] = 0


def _copy_mode_fields(
    grid: NativeTerrainGrid, source_row: int, source_col: int, dest_row: int, dest_col: int
) -> None:
    grid.height[dest_row, dest_col] = grid.height[source_row, source_col]
    grid.terrain[dest_row, dest_col] = grid.terrain[source_row, source_col]
    grid.variant[dest_row, dest_col] = grid.variant[source_row, source_col]
    grid.objects[dest_row, dest_col] = grid.objects[source_row, source_col]
    grid.resources[dest_row, dest_col] = grid.resources[source_row, source_col]
    grid.object_flags[dest_row, dest_col] = grid.object_flags[source_row, source_col]


def _copy_anti_diagonal(grid: NativeTerrainGrid) -> None:
    for outer in range(grid.side - 1):
        for inner in range(grid.side - outer - 1):
            _copy_mode_fields(
                grid,
                inner,
                outer,
                grid.side - 1 - outer,
                grid.side - 1 - inner,
            )


def _copy_main_diagonal(grid: NativeTerrainGrid) -> None:
    for source_col in range(1, grid.side):
        for source_row in range(source_col):
            _copy_mode_fields(grid, source_row, source_col, source_col, source_row)


def _mirror_terrain_only(grid: NativeTerrainGrid, mode: int) -> None:
    """Finish the archetype orientation before bonus terrain is painted."""

    if mode:
        _set_mode_variant_sentinels(grid, mode)
        _clear_mode_variant_sentinels(grid, mode)
        if mode & 0x02:
            _copy_anti_diagonal(grid)
        if mode & 0x01:
            _copy_main_diagonal(grid)
    _normalize_outer_ocean_edge(grid)


def generate_primary_terrain(
    side: int,
    seed: int,
    mode: int = 0,
    *,
    progress=None,
    surface_rates=None,
    disabled_object_families=None,
    defer_non_archetype: bool = False,
    defer_global_content: bool = False,
) -> NativeTerrainResult:
    """Generate the primary native terrain field.

    ``mode`` is the native low-bit mask, not the application's
    ``legacy``/``upgraded`` label.  In the UI the bits are exposed as
    Axe long (1), Axe court (2), and Les deux (3).  The native pass applies the
    mirror after the global static-content/resource pass.  Player
    start records remain outside this result for the future SAV workflow.
    """

    side = int(side)
    mode = int(mode)
    if side <= 0 or side > MAX_SIDE or side % 64:
        raise ValueError(f"Le cœur natif exige une taille positive multiple de 64 (maximum {MAX_SIDE})")
    if mode < 0 or mode > 3:
        raise ValueError("Le mode miroir natif doit être compris entre 0 et 3")

    grid = NativeTerrainGrid.empty(side)
    rng = NativeRng16(int(seed))

    def report(stage: str) -> None:
        if progress is not None:
            progress(stage)

    report("initialize")
    _initialize_cells(grid)
    report("coarse_relief")
    _seed_coarse_relief(grid, rng)
    report("relief_refinement")
    _refine_relief(grid, rng)
    _normalize_relief(grid)

    relief_relax_passes = 0
    if mode == 0:
        report("relief_sculpture")
        attempts = side * side // 16
        for _ in range(attempts):
            # The first native expression is signed and truncates toward zero.
            numerator = rng.next() * side - 2
            row = 1 + math.trunc(numerator / 65536)
            col = 1 + ((rng.next() * (side - 3)) >> 16)
            if _interior(grid, row, col):
                _sculpt_candidate(grid, row, col)
        _consume_sculpture_markers(grid)
        relief_relax_passes = _relax_relief(grid, False)
    else:
        report("relief_relaxation_alternate")
        relief_relax_passes = _relax_relief(grid, True)

    report("relief_classification")
    _classify_relief(grid)
    _clear_pre_river_fields(grid)
    report("rivers")
    river_rate = 100.0
    if isinstance(surface_rates, dict):
        river_section = surface_rates.get("rivers", {})
        if isinstance(river_section, dict):
            try:
                river_rate = min(500.0, max(0.0, float(river_section.get("rate_percent", 100.0))))
            except (TypeError, ValueError):
                river_rate = 100.0
    river_meta = _generate_rivers(grid, rng, rate_percent=river_rate)
    report("structural_transitions")
    _apply_structural_transitions(grid)
    report("terrain_families")
    custom_rates = None
    if isinstance(surface_rates, dict) and isinstance(surface_rates.get("terrains"), dict):
        from ...custom.terrain import effective_terrain_rates

        custom_rates = effective_terrain_rates(surface_rates)
    native_default_rates = {
        "desert": 100.0,
        "swamp": 100.0,
        "mud": 100.0,
        "dry_grass": 100.0,
        "details": 100.0,
    }
    custom_mud_rate = (
        float(custom_rates["mud"])
        if custom_rates is not None
        else 100.0
    )
    if defer_non_archetype:
        reference_grid = _copy_native_grid(grid)
        reference_rng = _copy_native_rng(rng)
        _mirror_terrain_only(grid, mode)
        continuation = DeferredTerrainPass(
            grid=grid,
            rng=rng,
            mode=mode,
            seed=int(seed),
            surface_rates=surface_rates,
            custom_rates=custom_rates,
            native_default_rates=native_default_rates,
            custom_mud_rate=custom_mud_rate,
            relief_relax_passes=relief_relax_passes,
            river_meta=river_meta,
            reference_grid=reference_grid,
            reference_rng=reference_rng,
            disabled_object_families=tuple(
                str(value) for value in (disabled_object_families or ())
            ),
        )
        report("terrain_families_deferred")
        metadata: dict[str, object] = {
            "native_terrain_core": "native_calibrated",
            "native_rng_input": int(seed) & 0xFFFFFFFF,
            "native_mode_mask": mode,
            "native_mirror_main_diagonal": bool(mode & 0x01),
            "native_mirror_anti_diagonal": bool(mode & 0x02),
            "native_mirror_north_south": bool(mode & 0x01),
            "native_mirror_east_west": bool(mode & 0x02),
            "native_mirror_scope": "terrain_height_and_content",
            "custom_mud_parameter_percent": float(custom_mud_rate),
            "native_relief_relax_passes": int(relief_relax_passes),
            "native_micro_terrain_12_cells": 0,
            "native_micro_terrain_13_cells": 0,
            "native_micro_terrain_22_cells": 0,
            "native_micro_brush_hits": {"0x12": 0, "0x13": 0, "0x22": 0},
            "terrain_families_deferred": True,
            "global_content_deferred": bool(defer_global_content),
            **river_meta,
        }
        return NativeTerrainResult(
            grid.height.copy(),
            grid.terrain.copy(),
            grid.variant.copy(),
            grid.marker.copy(),
            metadata,
            grid.objects.copy(),
            grid.resources.copy(),
            grid.object_flags.copy(),
            continuation,
        )
    native_reference_terrain = None
    if custom_rates is not None:
        reference_needed = any(
            float(custom_rates[key]) != float(native_default_rates[key])
            for key in custom_rates
        )
        if reference_needed:
            reference_grid = _copy_native_grid(grid)
            reference_rng = _copy_native_rng(rng)
            for plan, key in zip(_FAMILY_PLANS, _FAMILY_PLAN_KEYS):
                if native_default_rates[key] <= 0.0:
                    continue
                _apply_family_plan(reference_grid, reference_rng, plan, 100.0)
            _apply_micro_terrain_brushes(reference_grid, reference_rng, 100.0)
            native_reference_terrain = reference_grid.terrain.copy()

    for plan, key in zip(_FAMILY_PLANS, _FAMILY_PLAN_KEYS):
        rate = (
            float(custom_rates[key])
            if custom_rates is not None
            else float(native_default_rates[key])
        )
        if rate <= 0.0:
            continue
        _apply_family_plan(grid, rng, plan, rate)

    if mode:
        _set_mode_variant_sentinels(grid, mode)
    report("micro_terrain_brushes")
    details_rate = (
        float(custom_rates["details"])
        if custom_rates is not None
        else float(native_default_rates["details"])
    )
    micro_12, micro_13, micro_22 = _apply_micro_terrain_brushes(
        grid,
        rng,
        details_rate,
    )

    custom_terrain_meta = None
    if custom_rates is not None:
        from ...custom.terrain import apply_custom_terrain_rates

        if native_reference_terrain is None:
            native_reference_terrain = grid.terrain.copy()
        custom_terrain_meta = apply_custom_terrain_rates(
            grid.terrain,
            surface_rates,
            seed=int(seed) ^ 0x54455252,
            reference_terrain=native_reference_terrain,
        )

    # The native generator continues with the same PRNG state.  This pass is
    # deliberately limited to global MAP/EDM content; player-start objects,
    # start resources and settlers are SAV-only and remain deferred.
    from .native_content import populate_native_content

    content_meta = populate_native_content(
        grid,
        rng,
        mode,
        disabled_object_families=disabled_object_families,
    )

    if mode:
        _clear_mode_variant_sentinels(grid, mode)
        report("mirror_axis_copy")
        if mode & 0x02:
            _copy_anti_diagonal(grid)
        if mode & 0x01:
            _copy_main_diagonal(grid)

    # Must follow mirror copies: both triangular traversals can write onto
    # the outer edge.  Keep the final serialized perimeter deep Water7.
    _normalize_outer_ocean_edge(grid)

    metadata: dict[str, object] = {
        "native_terrain_core": "native_calibrated",
        "native_rng_input": int(seed) & 0xFFFFFFFF,
        "native_mode_mask": mode,
        "native_mirror_main_diagonal": bool(mode & 0x01),
        "native_mirror_anti_diagonal": bool(mode & 0x02),
        "native_mirror_north_south": bool(mode & 0x01),
        "native_mirror_east_west": bool(mode & 0x02),
        "native_mirror_scope": "terrain_height_and_content",
        "native_relief_relax_passes": int(relief_relax_passes),
        "native_micro_terrain_12_cells": int(np.count_nonzero(grid.terrain == 0x12)),
        "native_micro_terrain_13_cells": int(np.count_nonzero(grid.terrain == 0x13)),
        "native_micro_terrain_22_cells": int(np.count_nonzero(grid.terrain == 0x22)),
        "native_micro_brush_hits": {
            "0x12": int(micro_12),
            "0x13": int(micro_13),
            "0x22": int(micro_22),
        },
        **river_meta,
        **content_meta,
    }
    if custom_terrain_meta is not None:
        metadata["custom_terrain"] = custom_terrain_meta
    return NativeTerrainResult(
        grid.height.copy(),
        grid.terrain.copy(),
        grid.variant.copy(),
        grid.marker.copy(),
        metadata,
        grid.objects.copy(),
        grid.resources.copy(),
        grid.object_flags.copy(),
    )


def resume_deferred_terrain(
    result: NativeTerrainResult,
    *,
    height: np.ndarray | None = None,
    terrain: np.ndarray | None = None,
    objects: np.ndarray | None = None,
    resources: np.ndarray | None = None,
    object_flags: np.ndarray | None = None,
    protected_mask: np.ndarray | None = None,
    include_native_content: bool = False,
    protected_object_mask: np.ndarray | None = None,
    protected_resource_mask: np.ndarray | None = None,
    include_native_resources: bool = True,
    preserve_existing_resources: bool = False,
    object_hitbox_radius: int | None = None,
    before_native_content=None,
    progress=None,
) -> NativeTerrainResult:
    """Finish deferred terrain and, for Legacy, the deferred native content."""

    continuation = result.deferred
    if continuation is None:
        return result
    grid = continuation.grid
    if height is not None:
        grid.height[:] = height
    if terrain is not None:
        grid.terrain[:] = terrain
    if objects is not None:
        grid.objects[:] = objects
    if resources is not None:
        grid.resources[:] = resources
    if object_flags is not None:
        grid.object_flags[:] = object_flags

    if progress is not None:
        progress("terrain_families")
    custom_rates = continuation.custom_rates
    native_default_rates = continuation.native_default_rates
    native_reference_terrain = None
    if custom_rates is not None:
        reference_needed = any(
            float(custom_rates[key]) != float(native_default_rates[key])
            for key in custom_rates
        )
        if reference_needed and continuation.reference_grid is not None:
            reference_grid = _copy_native_grid(continuation.reference_grid)
            reference_rng = (
                _copy_native_rng(continuation.reference_rng)
                if continuation.reference_rng is not None
                else NativeRng16(continuation.seed)
            )
            for plan, key in zip(_FAMILY_PLANS, _FAMILY_PLAN_KEYS):
                if native_default_rates[key] <= 0.0:
                    continue
                _apply_family_plan(reference_grid, reference_rng, plan, 100.0)
            _apply_micro_terrain_brushes(reference_grid, reference_rng, 100.0)
            _mirror_terrain_only(reference_grid, continuation.mode)
            native_reference_terrain = reference_grid.terrain.copy()

    for plan, key in zip(_FAMILY_PLANS, _FAMILY_PLAN_KEYS):
        rate = (
            float(custom_rates[key])
            if custom_rates is not None
            else float(native_default_rates[key])
        )
        if rate <= 0.0:
            continue
        _apply_family_plan(
            grid,
            continuation.rng,
            plan,
            rate,
            protected_mask,
        )

    if progress is not None:
        progress("micro_terrain_brushes")
    details_rate = (
        float(custom_rates["details"])
        if custom_rates is not None
        else float(native_default_rates["details"])
    )
    micro_12, micro_13, micro_22 = _apply_micro_terrain_brushes(
        grid,
        continuation.rng,
        details_rate,
        protected_mask,
    )

    custom_terrain_meta = None
    if custom_rates is not None:
        from ...custom.terrain import apply_custom_terrain_rates

        if native_reference_terrain is None:
            native_reference_terrain = grid.terrain.copy()
        custom_terrain_meta = apply_custom_terrain_rates(
            grid.terrain,
            continuation.surface_rates,
            seed=int(continuation.seed) ^ 0x54455252,
            protected_mask=protected_mask,
            reference_terrain=native_reference_terrain,
        )

    content_meta: dict[str, object] = {}
    if include_native_content:
        from .native_content import populate_native_content

        callback_result = (
            before_native_content(grid)
            if before_native_content is not None
            else None
        )
        if isinstance(callback_result, dict):
            protected_object_mask = callback_result.get(
                "protected_object_mask",
                protected_object_mask,
            )
            protected_resource_mask = callback_result.get(
                "protected_resource_mask",
                protected_resource_mask,
            )

        content_meta = populate_native_content(
            grid,
            continuation.rng,
            continuation.mode,
            disabled_object_families=continuation.disabled_object_families,
            protected_object_mask=protected_object_mask,
            protected_resource_mask=protected_resource_mask,
            include_resources=include_native_resources,
            preserve_existing_resources=preserve_existing_resources,
            object_hitbox_radius=object_hitbox_radius,
        )

    metadata = dict(result.metadata)
    metadata.update(
        {
            "native_micro_terrain_12_cells": int(np.count_nonzero(grid.terrain == 0x12)),
            "native_micro_terrain_13_cells": int(np.count_nonzero(grid.terrain == 0x13)),
            "native_micro_terrain_22_cells": int(np.count_nonzero(grid.terrain == 0x22)),
            "native_micro_brush_hits": {
                "0x12": int(micro_12),
                "0x13": int(micro_13),
                "0x22": int(micro_22),
            },
            "terrain_families_deferred": False,
            "global_content_deferred": False,
        }
    )
    metadata.update(content_meta)
    if custom_terrain_meta is not None:
        metadata["custom_terrain"] = custom_terrain_meta
    return NativeTerrainResult(
        grid.height.copy(),
        grid.terrain.copy(),
        grid.variant.copy(),
        grid.marker.copy(),
        metadata,
        grid.objects.copy(),
        grid.resources.copy(),
        grid.object_flags.copy(),
    )


__all__ = (
    "MAX_SIDE",
    "NativeRng16",
    "NativeTerrainGrid",
    "NativeTerrainResult",
    "DeferredTerrainPass",
    "generate_primary_terrain",
    "resume_deferred_terrain",
)
