import numpy as np
from s3mapgen.model import MapState
from s3mapgen.constants import GRASS
from s3mapgen.preview import render


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
