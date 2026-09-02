from s3mapgen.application.rendering.preview import PALETTE, _global_rgb
from s3mapgen.map_data.constants import (
    DRY_GRASS,
    GRASS,
    MUD,
    MUD_TRANS_1,
    MUD_TRANS_2,
    SWAMP,
    SWAMP_TRANS,
)
from s3mapgen.map_data.model import MapState


def test_global_viewer_distinguishes_dry_grass_and_each_mud_tile():
    state = MapState.empty(8)
    terrain_ids = (GRASS, DRY_GRASS, MUD, MUD_TRANS_2, MUD_TRANS_1)
    state.terrain[0, :len(terrain_ids)] = terrain_ids
    rgb = _global_rgb(state)
    colors = [tuple(rgb[0, index]) for index in range(len(terrain_ids))]
    assert len(set(colors)) == len(colors)
    assert colors == [PALETTE[terrain_id] for terrain_id in terrain_ids]


def test_mud_is_lighter_toward_the_exterior_and_swamp_is_teal():
    assert PALETTE[MUD] == (137, 98, 62)
    assert PALETTE[MUD_TRANS_2] == (116, 82, 54)
    assert PALETTE[MUD_TRANS_1] == (86, 61, 45)
    assert sum(PALETTE[MUD]) > sum(PALETTE[MUD_TRANS_2]) > sum(PALETTE[MUD_TRANS_1])
    assert PALETTE[SWAMP] == (25, 89, 79)
    assert PALETTE[SWAMP_TRANS] == (42, 111, 88)
    assert PALETTE[DRY_GRASS][1] > PALETTE[DRY_GRASS][0]
