import numpy as np
from s3mapgen.model import MapState
from s3mapgen.constants import GRASS
from s3mapgen.preview import PLAYER_COLORS, render


def _state():
    s=MapState.empty(32)
    s.terrain[:]=GRASS
    s.height[:]=np.arange(32,dtype=np.uint8)[:,None]
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


def test_parallelogram_projection_changes_width_without_height():
    s=_state();im=render(s,projection='parallelogram')
    assert im.height==32 and im.width==48 and im.mode=='RGBA'


def test_start_territory_ring_uses_player_color():
    s=_state();s.starts=[(16,16)]
    a=np.asarray(render(s,labels=True))
    color=np.asarray(PLAYER_COLORS[0],dtype=np.uint8)
    # Native footprint ring is six pixels from the start anchor in square view.
    assert np.array_equal(a[16,22],color)
    assert not np.array_equal(a[16,16],color)


def test_player_marker_palette_supports_twenty_players():
    assert len(PLAYER_COLORS)>=20
