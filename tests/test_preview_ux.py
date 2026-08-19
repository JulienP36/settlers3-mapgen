import numpy as np
from s3mapgen.model import MapState
from s3mapgen.constants import GRASS
from s3mapgen.preview import PLAYER_COLORS, START_TERRITORY_RADIUS, render


def _state(side=96):
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


def test_start_territory_ring_uses_sav_calibrated_radius_and_player_color():
    s=_state();s.starts=[(48,48)]
    a=np.asarray(render(s,labels=True))
    color=np.asarray(PLAYER_COLORS[0],dtype=np.uint8)
    assert START_TERRITORY_RADIUS==35
    assert np.array_equal(a[48,48+START_TERRITORY_RADIUS],color)
    assert not np.array_equal(a[48,48],color)


def test_player_marker_palette_supports_twenty_players():
    assert len(PLAYER_COLORS)>=20
