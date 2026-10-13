import itertools

import numpy as np
import pytest

from s3mapgen.generation.archetypes.large_islands import (
    _separated_island_assignment, place_island_starts,
)
from s3mapgen.generation.start_safety import candidate_centers, validate_start_safety
from s3mapgen.map_data.model import MapState


def test_all_island_candidates_are_kept_without_sampling():
    state = MapState.empty(256)
    labels = np.zeros((256, 256), dtype=np.uint8)
    labels[10:246, 10:120] = 1
    labels[10:246, 136:246] = 2
    state.terrain[labels != 0] = 16
    place_island_starts(state, 2, np.random.default_rng(42), labels, 14)
    counts = state.metadata['island_start_search']['candidate_counts']
    assert min(counts) > 16000 // 2
    assert counts == [int((candidate_centers(state) & (labels == n)).sum())
                      for n in (1, 2)]
    assert [int(labels[y, x]) for x, y in state.starts] == [1, 2]
    assert all(check.passed for check in validate_start_safety(state))


def test_valid_positions_inside_former_margin_are_not_rejected():
    state = MapState.empty(192)
    labels = np.zeros((192, 192), dtype=np.uint8)
    labels[45:76, 7:25] = 1
    labels[115:146, 110:141] = 2
    state.terrain[labels != 0] = 16
    place_island_starts(state, 2, np.random.default_rng(42), labels, 14)
    assert state.starts[0][0] < 22
    assert all(check.passed for check in validate_start_safety(state))


def test_assignment_revisits_choices_and_reports_true_impossibility():
    # Choosing the first point of A prevents both alternatives of B/C;
    # a complete assignment exists only after changing A.
    domains = [np.array([(0, 0), (200, 0)]),
               np.array([(0, 40), (40, 0)]),
               np.array([(40, 40), (0, -40)])]
    result = _separated_island_assignment(domains)
    assert result is not None and result[0] == (200, 0)
    assert all((a[0]-b[0])**2 + (a[1]-b[1])**2 >= 2500
               for a, b in itertools.combinations(result, 2))
    impossible = [np.array([(0, 0), (1, 0)]), np.array([(0, 1), (1, 1)])]
    assert _separated_island_assignment(impossible) is None


def test_failure_distinguishes_relief_from_no_clear_footprint():
    state = MapState.empty(64)
    state.terrain[:] = 16
    labels = np.ones((64, 64), dtype=np.uint8)
    state.height[:] = np.arange(64, dtype=np.uint16)[None, :] * 3
    original = state.area.copy()
    place_island_starts(state, 1, np.random.default_rng(42), labels, 14)
    assert np.array_equal(state.area, original)
    assert state.metadata['start_disabled_slots'] == [0]
    assert state.starts == []
    state.terrain[:] = 0
    place_island_starts(state, 1, np.random.default_rng(42), labels, 14)
    assert state.starts == []
