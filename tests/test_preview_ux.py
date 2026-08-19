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
    # Top/bottom of a circle in projected space is shifted by r/2 in square array space.
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
