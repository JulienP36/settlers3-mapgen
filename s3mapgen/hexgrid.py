"""Vectorized HEX6 distance, neighborhood and component operations."""

from __future__ import annotations
from collections import deque
import numpy as np
from scipy import ndimage
from .constants import HEX6

HEX_STRUCTURE = np.array([[1,1,0],[1,1,1],[0,1,1]], dtype=bool)

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

def distance_from(mask:np.ndarray, max_distance:int|None=None)->np.ndarray:
    h,w=mask.shape
    inf=32767
    d=np.full(mask.shape,inf,np.int16)
    q=deque()
    for y,x in np.argwhere(mask):
        d[y,x]=0; q.append((int(x),int(y)))
    while q:
        x,y=q.popleft(); nd=int(d[y,x])+1
        if max_distance is not None and nd>max_distance: continue
        for dx,dy in HEX6:
            xx,yy=x+dx,y+dy
            if 0<=xx<w and 0<=yy<h and nd<d[yy,xx]:
                d[yy,xx]=nd; q.append((xx,yy))
    return d

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
