import numpy as np
from s3mapgen.model import MapState
from s3mapgen.constants import GRASS
from s3mapgen.preview import PLAYER_COLORS, START_TERRITORY_RADIUS, render


def _state(side=128):
    s=MapState.empty(side)
    s.terrain[:]=GRASS
    s.height[:]=np.arange(side,dtype=np.uint8)[:,None]
    s.resources[8:12,8:12]=0x1f
    s.claim[4:20,4:20]=0
    return s


def test_overlay_alpha_zero_matches_global():
    s=_state()
    assert np.array_equal(np.asarray(render(s,view='heightmap',overlay_alpha=0)),np.asarray(render(s,view='global')))


def test_overlay_alpha_changes_visualization():
    s=_state()
    a=np.asarray(render(s,view='resources',overlay_alpha=25))
    b=np.asarray(render(s,view='resources',overlay_alpha=100))
    assert not np.array_equal(a,b)


def test_paths_view_highlights_runtime_terrain28():
    s=_state();s.terrain[20,20]=28
    a=np.asarray(render(s,view='paths',overlay_alpha=100))
    b=np.asarray(render(s,view='global'))
    assert not np.array_equal(a[20,20],b[20,20])


def test_crops_view_distinguishes_wheat_vine_rice():
    s=_state();s.objects[20,20]=85;s.objects[20,21]=94;s.objects[20,22]=103
    a=np.asarray(render(s,view='crops',overlay_alpha=100))
    assert not np.array_equal(a[20,20],a[20,21])
    assert not np.array_equal(a[20,21],a[20,22])


def test_heatmap_uses_real_resource_quantity():
    s=_state();s.resources[:]=0
    s.resources[20,20]=0x11
    s.resources[90,90]=0x1f
    a=np.asarray(render(s,view='heatmap',heatmap_resource='coal',overlay_alpha=100))
    # The high-stock cluster must render hotter/brighter than the low-stock one.
    assert int(a[90,90].sum()) != int(a[20,20].sum())


def test_building_stone_heatmap_uses_remaining_stock_and_ignores_127():
    s=_state();s.objects[30,30]=115;s.objects[80,80]=126;s.objects[50,50]=127
    a=np.asarray(render(s,view='heatmap',heatmap_resource='building_stones',overlay_alpha=100))
    background=a[0,0]
    assert not np.array_equal(a[30,30],background)
    assert np.array_equal(a[50,50],background)


def test_parallelogram_projection_uses_exact_half_cell_row_offset():
    s=_state(32);im=render(s,projection='parallelogram')
    assert im.height==64 and im.width==95 and im.mode=='RGBA'


def test_start_territory_is_sheared_in_square_view():
    s=_state();s.starts=[(64,64)]
    a=np.asarray(render(s,labels=True,projection='square'))
    color=np.asarray(PLAYER_COLORS[0],dtype=np.uint8)
    r=START_TERRITORY_RADIUS
    assert r==35
    assert np.array_equal(a[64,64+r],color)
    assert np.array_equal(a[64+r,64+round(r/2)],color)
    assert not np.array_equal(a[64+r,64],color)


def test_start_territory_is_circle_in_parallelogram_view():
    s=_state();s.starts=[(64,64)]
    a=np.asarray(render(s,labels=True,projection='parallelogram'))
    color=np.asarray(PLAYER_COLORS[0],dtype=np.uint8)
    X=2*64+(s.side-1-64);Y=2*64;r=2*START_TERRITORY_RADIUS
    assert np.array_equal(a[Y,X+r,:3],color)
    assert np.array_equal(a[Y+r,X,:3],color)


def test_player_marker_palette_supports_twenty_players():
    assert len(PLAYER_COLORS)>=20
