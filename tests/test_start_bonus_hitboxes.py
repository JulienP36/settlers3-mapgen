import numpy as np

from s3mapgen.application.paths import LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE
from s3mapgen.generation import MapGenerator
from s3mapgen.generation.custom import build_custom_config
from s3mapgen.map_data.hexgrid import dilate, hex_distance


START_PACKAGES = (
    "start_forest",
    "start_building_stones",
    "start_mini_swamp",
    "start_rocky_minerals",
    "start_lake_fish_river",
)


def _generator():
    return MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_REFERENCE)


def _bonus_object_cells(output, mode):
    state = output.state
    if mode == "legacy":
        forests = state.metadata["legacy_start_forest"]["forests"]
        tree_points = {
            (int(x), int(y))
            for forest in forests
            for x, y in forest["adult_points"] + forest["small_points"]
        }
        stone_groups = state.metadata["legacy_start_building_stones"]["groups"]
        stone_points = {
            (int(x), int(y))
            for group in stone_groups
            for x, y in group["points"]
        }
        stone_cells = {
            (int(x), int(y))
            for x, y in state.metadata["legacy_start_building_stone_footprint_cells"]
        }
    else:
        forests = state.metadata["upgraded_trees"]["start_forests"]
        tree_points = {
            (int(x), int(y))
            for forest in forests
            for x, y in forest["adult_points"] + forest["small_points"]
        }
        stone_records = [
            record
            for record in state.metadata["building_stone_anchors"]
            if record[3] == "start_bonus"
        ]
        stone_points = {(int(record[0]), int(record[1])) for record in stone_records}
        footprint = build_custom_config(mode).runtime_profile()["building_stones"][
            "footprint"
        ]
        stone_cells = {
            (x + int(dx), y + int(dy))
            for x, y in stone_points
            for dx, dy in footprint
            if 0 <= x + int(dx) < state.side and 0 <= y + int(dy) < state.side
        }
    return tree_points, stone_points, stone_cells


def test_global_objects_respect_all_start_bonus_hitboxes():
    for mode in ("legacy", "upgraded"):
        config = build_custom_config(mode).with_start_packages(START_PACKAGES)
        output = _generator().generate(
            2,
            20260911,
            mode="custom",
            archetype="continental",
            side=256,
            custom_config=config,
        )
        state = output.state
        tree_points, stone_points, stone_cells = _bonus_object_cells(output, mode)
        bonus_anchors = tree_points | stone_points
        bonus_cells = bonus_anchors | stone_cells
        bonus_mask = np.zeros((state.side, state.side), dtype=bool)
        for x, y in bonus_cells:
            bonus_mask[y, x] = True
        bonus_halo = dilate(bonus_mask, 2)

        object_cells = {
            (int(x), int(y)) for y, x in np.argwhere(state.objects != 0)
        }
        global_objects = object_cells - bonus_anchors
        assert global_objects
        assert all(not bonus_halo[y, x] for x, y in global_objects)
        assert min(
            hex_distance(x1, y1, x2, y2)
            for index, (x1, y1) in enumerate(object_cells)
            for x2, y2 in list(object_cells)[index + 1 :]
        ) >= 3
        assert all(
            state.objects[y, x] == 0
            for x, y in stone_cells - stone_points
        )
        assert all(value.passed for value in output.validations if value.hard)
