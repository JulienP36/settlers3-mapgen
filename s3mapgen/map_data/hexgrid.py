"""Vectorized HEX6 distance, neighborhood and component operations."""

from __future__ import annotations
import numpy as np
from scipy import ndimage
from .constants import HEX6

HEX_STRUCTURE = np.array([[1,1,0],[1,1,1],[0,1,1]], dtype=bool)
HEX_DISTANCE_METRIC = np.array([[1,1,0],[1,0,1],[0,1,1]], dtype=np.int8)

def hex_distance(x1:int,y1:int,x2:int,y2:int)->int:
    dx=x2-x1; dy=y2-y1
    return max(abs(dx),abs(dy)) if dx*dy >= 0 else abs(dx)+abs(dy)

def neighbor_count(mask:np.ndarray)->np.ndarray:
    h,w=mask.shape
    out=np.zeros(mask.shape,np.int16)
    for dx,dy in HEX6:
        y0=max(0,dy); y1=min(h,h+dy); x0=max(0,dx); x1=min(w,w+dx)
        sy0=max(0,-dy); sy1=min(h,h-dy); sx0=max(0,-dx); sx1=min(w,w-dx)
        out[y0:y1,x0:x1]+=mask[sy0:sy1,sx0:sx1]
    return out

def touching(mask:np.ndarray)->np.ndarray:
    """Return the HEX6 rim adjacent to ``mask`` without including it."""

    return neighbor_count(mask)>0


def distance_from(
    mask:np.ndarray,
    max_distance:int|None=None,
    passable:np.ndarray|None=None,
)->np.ndarray:
    """Return an exact HEX6 distance field.

    The unconstrained case uses SciPy's C-level chamfer transform with the
    exact HEX6 metric. ``passable`` optionally constrains propagation for
    bounded routing such as Legacy rivers.
    """

    inf=np.int16(32767)
    source=np.asarray(mask,dtype=bool)
    if passable is None:
        distance=ndimage.distance_transform_cdt(
            ~source,
            metric=HEX_DISTANCE_METRIC,
        ).astype(np.int16)
        if max_distance is not None:
            distance[distance > int(max_distance)] = inf
        return distance

    distance=np.full(mask.shape,inf,dtype=np.int16)
    frontier=source.copy()
    allowed=np.asarray(passable,dtype=bool)|source
    frontier&=allowed
    distance[frontier]=0
    level=0
    while frontier.any():
        if max_distance is not None and level>=max_distance:break
        frontier=touching(frontier)&(distance==inf)
        frontier&=allowed
        if not frontier.any():break
        level+=1
        distance[frontier]=level
    return distance

def component_labels(mask:np.ndarray):
    return ndimage.label(mask, structure=HEX_STRUCTURE)

def component_sizes(mask:np.ndarray):
    lab,n=component_labels(mask)
    return lab,[int((lab==i).sum()) for i in range(1,n+1)]

def depth(mask:np.ndarray, max_levels:int=512)->np.ndarray:
    d=np.zeros(mask.shape,np.int16)
    rem=mask.copy(); level=1
    while rem.any() and level<=max_levels:
        er=ndimage.binary_erosion(rem, structure=HEX_STRUCTURE, border_value=0)
        d[rem & ~er]=level
        rem=er; level+=1
    return d

def dilate(mask:np.ndarray, iterations:int)->np.ndarray:
    if iterations<=0: return mask.copy()
    return ndimage.binary_dilation(mask, structure=HEX_STRUCTURE, iterations=iterations)
