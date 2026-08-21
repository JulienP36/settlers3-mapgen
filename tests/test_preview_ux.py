import numpy as np
from s3mapgen.model import MapState
from s3mapgen.constants import GRASS
from s3mapgen.preview import PLAYER_COLORS, START_TERRITORY_RADIUS, INITIAL_TERRITORY_ROW_RANGES, initial_territory_cells, initial_territory_boundary, render

def _state(side=128):
    s=MapState.empty(side);s.terrain[:]=GRASS;s.height[:]=np.arange(side,dtype=np.uint8)[:,None];s.resources[8:12,8:12]=0x1f;s.claim[4:20,4:20]=0;return s

def test_overlay_alpha_zero_matches_global():
    s=_state();assert np.array_equal(np.asarray(render(s,view='heightmap',overlay_alpha=0,labels=False)),np.asarray(render(s,view='global',labels=False)))

def test_overlay_alpha_changes_visualization():
    s=_state();a=np.asarray(render(s,view='resources',overlay_alpha=25));b=np.asarray(render(s,view='resources',overlay_alpha=100));assert not np.array_equal(a,b)

def test_parallelogram_projection_uses_exact_half_cell_row_offset():
    s=_state(32);im=render(s,projection='parallelogram',labels=False);assert im.height==64 and im.width==95 and im.mode=='RGBA'

def test_native_initial_territory_mask_is_exact_3500_cells():
    assert START_TERRITORY_RADIUS==35 and len(INITIAL_TERRITORY_ROW_RANGES)==71
    assert len(initial_territory_cells((64,64),128))==3500
    assert len(initial_territory_boundary((64,64),128))==210

def test_initial_territory_wraps_without_losing_cells():
    assert len(initial_territory_cells((3,3),128))==3500

def test_player_marker_palette_supports_twenty_players():
    assert len(PLAYER_COLORS)==20 and len(set(PLAYER_COLORS))==20

def test_global_outline_uses_player_color_on_exact_boundary():
    s=_state();s.starts=[(64,64)];a=np.asarray(render(s,labels=True,projection='square'));color=np.asarray(PLAYER_COLORS[0],dtype=np.uint8)
    x,y=next(iter(initial_territory_boundary((64,64),128)));assert np.array_equal(a[y,x,:3],color)

def test_crops_view_uses_distinct_wheat_vine_rice_colors():
    s=_state(32)
    s.objects[5,5]=88
    s.objects[6,6]=98
    s.objects[7,7]=106
    rgb=np.asarray(render(s,view='crops',labels=False))[:,:,:3]
    assert tuple(rgb[5,5])==(235,205,75)
    assert tuple(rgb[6,6])==(165,85,185)
    assert tuple(rgb[7,7])==(80,205,110)
    assert len({tuple(rgb[5,5]),tuple(rgb[6,6]),tuple(rgb[7,7])})==3


def test_paths_view_does_not_highlight_agricultural_terrain_22():
    s=_state(32)
    s.terrain[5,5]=22
    s.terrain[6,6]=28
    rgb=np.asarray(render(s,view='paths',labels=False))[:,:,:3]
    # Terrain 28 remains the dedicated path highlight.
    assert tuple(rgb[6,6])==(235,175,85)
    # Terrain 22 must not use the former dedicated agricultural highlight.
    assert tuple(rgb[5,5])!=(195,135,75)

def test_resource_view_uses_requested_mineral_colors():
    s=_state(32)
    for x,raw in enumerate((0x11,0x21,0x31,0x41,0x51),start=5):
        s.resources[10,x]=raw
    rgb=np.asarray(render(s,view='resources',labels=False))[:,:,:3]
    assert tuple(rgb[10,5])==(0,0,0)          # coal: editor black
    assert tuple(rgb[10,6])==(255,148,0)      # iron: editor orange
    assert tuple(rgb[10,7])==(255,255,0)      # gold: editor yellow
    assert tuple(rgb[10,8])==(206,0,0)        # gems: editor red
    assert tuple(rgb[10,9])==(196,178,92)     # sulfur: lighter beige/ochre for separation


def test_player_9_is_near_white_and_distinct():
    assert min(PLAYER_COLORS[8]) >= 225
    assert len(set(PLAYER_COLORS)) == 20

def test_initial_territory_colored_center_survives_black_halo():
    s=_state();s.starts=[(64,64)]
    a=np.asarray(render(s,labels=True,projection='square'))[:,:,:3]
    boundary=initial_territory_boundary((64,64),128)
    x,y=next(iter(boundary))
    assert tuple(a[y,x])==PLAYER_COLORS[0]
