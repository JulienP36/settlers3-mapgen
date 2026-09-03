from s3mapgen.application.analysis.charts import DECORATIVE_FAMILY_COLORS
from s3mapgen.application.rendering.preview import PALETTE, REEF_COLOR, _global_rgb, render_square_base
from s3mapgen.map_data.constants import (
    DRY_GRASS,
    GRASS,
    MUD,
    MUD_TRANS_1,
    MUD_TRANS_2,
    REEF_IDS,
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


def test_reefs_use_the_dark_rock_palette_on_map_and_chart():
    state = MapState.empty(8)
    state.terrain[0, 0] = 7
    state.objects[0, 0] = REEF_IDS[0]
    assert tuple(_global_rgb(state)[0, 0]) == REEF_COLOR
    assert tuple(render_square_base(state, view='resources', overlay_alpha=100).getpixel((0, 0))) == REEF_COLOR
    assert DECORATIVE_FAMILY_COLORS['reefs'] == REEF_COLOR
