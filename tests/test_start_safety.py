import numpy as np
import pytest

from s3mapgen.map_data.model import MapState
from s3mapgen.generation.start_safety import (
    candidate_centers, require_start_safety, start_terrain_reservation,
    EDITOR_START_OFFSETS, separated,
)
from s3mapgen.generation.generators.legacy.starts import place_starts as legacy
from s3mapgen.generation.generators.upgraded.starts import place_starts as upgraded


def grass(side=128):
    state = MapState.empty(side)
    state.terrain[:] = 16
    return state


@pytest.mark.parametrize('solver', [legacy, upgraded])
def test_continental_solver_rejects_occupied_grass(solver):
    state = grass()
    state.objects[:] = 68
    original = state.area.copy()
    solver(state, 2, np.random.default_rng(42))
    assert state.starts == []
    assert state.metadata["start_disabled_slots"] == [0, 1]
    assert np.array_equal(state.area, original)


def test_editor_checks_far_corner_outside_native_base():
    state = grass()
    assert candidate_centers(state)[64, 64]
    state.terrain[60, 59] = 64  # (-5,-4): in editor scan, outside 33-cell base.
    assert not candidate_centers(state)[64, 64]
    assert len(EDITOR_START_OFFSETS) == len(set(EDITOR_START_OFFSETS)) == 70


@pytest.mark.parametrize('channel,value', [('terrain',64), ('objects',68), ('accessibility',1), ('height',255)])
def test_final_map_rechecks_changes_after_placement(channel,value):
    state = grass()
    state.starts = [(64,64)]
    assert all(v.passed for v in require_start_safety(state))
    getattr(state, channel)[64,64] = value
    with pytest.raises(RuntimeError, match='Départ invalide'):
        require_start_safety(state)


def test_stone_neighbour_footprint_and_collision_are_checked():
    state = grass()
    state.objects[64, 71] = 115
    # The stone is outside the base; its neighbour footprint + hitbox reaches
    # the editor's eastern cells. A plain anchor-only check would miss it.
    assert not candidate_centers(state)[64,64]


def test_reservation_protects_both_editor_area_and_native_base():
    state = grass()
    state.starts = [(64,64)]
    mask = start_terrain_reservation(state)
    assert mask[60,59] and mask[68,66]
    assert not mask[50,50]
    assert separated(50,0,[(0,0)])
    assert not separated(49,0,[(0,0)])
    assert separated(30,40,[(0,0)])  # exact Euclidean threshold, not HEX6.
