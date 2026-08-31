"""Primitives de formes HEX6 pour les familles de terrain Legacy."""

from __future__ import annotations

import heapq
import math

import numpy as np
from scipy import ndimage

from ...core.noise import warped_fractal_field
from ....map_data.hexgrid import HEX6, touching


_HEX_STRUCTURE = np.array(((1, 1, 0), (1, 1, 1), (0, 1, 1)), dtype=bool)


def _neighbours(x:int,y:int,side:int):
    for dx,dy in HEX6:
        xx,yy=x+dx,y+dy
        if 0<=xx<side and 0<=yy<side:
            yield xx,yy


def _sample_sizes(
    total:int,
    count:int,
    rng:np.random.Generator,
    *,
    minimum:int=1,
    maximum:int|None=None,
    sigma:float=0.70,
)->list[int]:
    """Return heavy-tailed positive sizes whose sum is exactly ``total``."""

    total=int(total)
    if total<=0 or count<=0:return []
    minimum=max(1,int(minimum))
    count=min(int(count),total//minimum)
    if count<=0:return [total]
    maximum=max(minimum,int(maximum) if maximum is not None else total)
    if count*maximum<total:maximum=total
    raw=rng.lognormal(mean=0.0,sigma=float(sigma),size=count)
    raw/=max(float(raw.sum()),1e-9)
    sizes=np.clip(np.maximum(minimum,np.rint(raw*total).astype(int)),minimum,maximum)
    surplus=int(sizes.sum())-total
    while surplus>0:
        candidates=np.flatnonzero(sizes>minimum)
        if not len(candidates):break
        for index in candidates[np.argsort(sizes[candidates])[::-1]]:
            if surplus<=0:break
            take=min(surplus,int(sizes[index]-minimum))
            sizes[index]-=take;surplus-=take
    missing=total-int(sizes.sum())
    while missing>0:
        candidates=np.flatnonzero(sizes<maximum)
        if not len(candidates):
            maximum=total;candidates=np.arange(len(sizes))
        for index in candidates[rng.permutation(len(candidates))]:
            if missing<=0:break
            take=min(missing,int(maximum-sizes[index]))
            sizes[index]+=take;missing-=take
    return [int(value) for value in sizes if value>0]


def _grow_component(
    support:np.ndarray,
    occupied:np.ndarray,
    center:tuple[int,int],
    target:int,
    *,
    aspect:float,
    angle:float,
    roughness:np.ndarray,
    rng:np.random.Generator,
    keep_separation:bool,
    occupied_rim:np.ndarray,
)->list[tuple[int,int]]|None:
    """Grow one connected, elongated and irregular component."""

    side=int(support.shape[0]);x0,y0=center
    if not support[y0,x0] or occupied[y0,x0]:return None
    if keep_separation and occupied_rim[y0,x0]:return None
    minor=max(1.0,math.sqrt(float(target)/(math.pi*max(aspect,0.2))))
    major=max(1.0,minor*max(aspect,0.2))
    ca,sa=math.cos(angle),math.sin(angle)
    heap:list[tuple[float,int,int]]=[];seen:set[tuple[int,int]]=set()

    def priority(x:int,y:int)->float:
        dx,dy=x-x0,y-y0
        u=ca*dx+sa*dy;v=-sa*dx+ca*dy
        ellipse=(u/major)**2+(v/minor)**2
        # The native contours are not smooth ellipses.  A warped multi-scale
        # field has enough weight to create coves, shoulders and narrow arms
        # while the ellipse only preserves a plausible component extent.
        ripple=0.115*math.sin(.37*u+.23*v)+.080*math.sin(.71*u-.31*v)
        return ellipse+.47*float(roughness[y,x])+ripple

    heapq.heappush(heap,(priority(x0,y0),x0,y0));seen.add((x0,y0));chosen=[]
    while heap and len(chosen)<int(target):
        _,x,y=heapq.heappop(heap)
        if not support[y,x] or occupied[y,x] or (keep_separation and occupied_rim[y,x]):continue
        chosen.append((x,y))
        for xx,yy in _neighbours(x,y,side):
            if (xx,yy) in seen or not support[yy,xx] or occupied[yy,xx]:continue
            if keep_separation and occupied_rim[yy,xx]:continue
            seen.add((xx,yy))
            heapq.heappush(heap,(priority(xx,yy)+float(rng.random())*.012,xx,yy))
    return chosen if len(chosen)>=int(target) else None


def _grow_micro_component(
    support:np.ndarray,
    occupied:np.ndarray,
    center:tuple[int,int],
    target:int,
    rng:np.random.Generator,
)->list[tuple[int,int]]|None:
    """Fast frontier growth for small native-like external patches."""

    side=int(support.shape[0]);x0,y0=center
    if not support[y0,x0] or occupied[y0,x0]:return None
    chosen=[(x0,y0)];seen={(x0,y0)};frontier=[(x0,y0)]
    while frontier and len(chosen)<int(target):
        index=int(rng.integers(len(frontier)));x,y=frontier[index]
        options=[
            (xx,yy) for xx,yy in _neighbours(x,y,side)
            if support[yy,xx] and not occupied[yy,xx] and (xx,yy) not in seen
        ]
        if not options:
            frontier.pop(index);continue
        xx,yy=options[int(rng.integers(len(options)))]
        seen.add((xx,yy));frontier.append((xx,yy));chosen.append((xx,yy))
    return chosen if len(chosen)>=int(target) else None


def _encloses_forbidden(cells: list[tuple[int, int]], forbidden: np.ndarray) -> bool:
    """Return whether a candidate component encloses a forbidden cell.

    This targeted test keeps the hot component-growth path cheap.  It is used
    for start footprints only: a component that would surround a player is
    rejected as a whole, while ordinary terrain shapes are allowed to retain
    their measured irregular contour.
    """

    if len(cells) < 7 or not forbidden.any():
        return False
    # Keep the test on the local component bounding box, but avoid rebuilding
    # Python coordinate lists and scanning every list once per statistic.  On
    # the 768 map the mountain pass retries this check many times; the
    # vectorized indexing preserves the exact mask semantics while keeping
    # that retry path bounded.
    coordinates = np.asarray(cells, dtype=np.intp)
    xs = coordinates[:, 0]
    ys = coordinates[:, 1]
    min_x = int(xs.min())
    max_x = int(xs.max())
    min_y = int(ys.min())
    max_y = int(ys.max())
    margin = 1
    local = np.zeros(
        (max_y - min_y + 1 + 2 * margin,
         max_x - min_x + 1 + 2 * margin),
        dtype=bool,
    )
    local[ys - min_y + margin, xs - min_x + margin] = True
    filled = ndimage.binary_fill_holes(local, structure=_HEX_STRUCTURE)
    y0 = min_y - margin
    x0 = min_x - margin
    y1 = y0 + local.shape[0]
    x1 = x0 + local.shape[1]
    target = forbidden[max(0, y0):y1, max(0, x0):x1]
    # The component bounding box is always at least one cell from the map
    # border in normal placement; clipping here keeps the helper safe for
    # edge-adjacent calibration calls as well.
    local_y0 = max(0, -y0)
    local_x0 = max(0, -x0)
    local_y1 = local_y0 + target.shape[0]
    local_x1 = local_x0 + target.shape[1]
    holes = filled & ~local
    return bool(np.any(target & holes[local_y0:local_y1, local_x0:local_x1]))


def place_components(
    available:np.ndarray,
    total:int,
    major_count:int,
    micro_count:int,
    rng:np.random.Generator,
    *,
    name:str="family",
    major_min:int=24,
    major_max:int|None=None,
    major_sigma:float=.85,
    micro_cells:int=0,
    micro_max:int=12,
    aspect_range:tuple[float,float]=(1.1,3.0),
    separation:bool=True,
    forbidden:np.ndarray|None=None,
    noise_interpolation_order:int=3,
)->np.ndarray:
    """Place major systems and micro-components on a free HEX6 support.

    This is a procedural construction: no shape, template or image is read at
    runtime.  The same deterministic seed stream only controls sampled sizes,
    centres, orientations and the warped contour field.
    """

    support=np.asarray(available,dtype=bool);out=np.zeros_like(support,dtype=bool)
    # ``forbidden`` is a hard no-overlap mask (currently the exact start
    # footprints).  A component that would touch it is rejected as a whole
    # and sampled again; the shape is never clipped around a player, which
    # would leave a conspicuous artificial hexagonal bite in the terrain.
    forbidden_mask = (
        np.zeros_like(support, dtype=bool)
        if forbidden is None
        else np.asarray(forbidden, dtype=bool)
    )
    total=max(0,min(int(total),int(support.sum())))
    if total==0:return out
    major_count=max(1,min(int(major_count),total));micro_count=max(0,int(micro_count))
    micro_cells=max(0,min(int(micro_cells),total))
    if micro_count and micro_cells<micro_count:micro_count=micro_cells
    if total-micro_cells<major_count*max(1,int(major_min)):
        micro_cells=max(0,total-major_count*max(1,int(major_min)))
    major_cells=total-micro_cells
    major_sizes=_sample_sizes(major_cells,major_count,rng,minimum=max(1,int(major_min)),maximum=major_max,sigma=major_sigma)
    micro_sizes=_sample_sizes(micro_cells,micro_count,rng,minimum=1,maximum=max(1,int(micro_max)),sigma=.65)
    if not major_sizes:major_sizes=[total]

    coarse=warped_fractal_field(support.shape[0],rng,scales=(.025,.070,.165),warp_strength=.07,interpolation_order=noise_interpolation_order)
    fine=warped_fractal_field(support.shape[0],rng,scales=(.070,.18,.38),warp_scale=.045,warp_strength=.16,interpolation_order=noise_interpolation_order)
    roughness=.68*coarse+.32*fine
    occupied=np.zeros_like(support,dtype=bool);occupied_rim=np.zeros_like(support,dtype=bool)

    def choose_center(keep_separation:bool,tiny:bool=False)->tuple[int,int]|None:
        if tiny:
            for _ in range(32):
                x=int(rng.integers(support.shape[1]));y=int(rng.integers(support.shape[0]))
                if support[y,x] and not occupied[y,x] and not forbidden_mask[y,x]:return x,y
            return None
        candidate=support&~occupied&~forbidden_mask
        if keep_separation and occupied.any():candidate&=~occupied_rim
        ys,xs=np.where(candidate)
        if not len(xs):return None
        scores=.35*roughness[ys,xs]+rng.normal(0,.80,len(xs))
        selected=np.argpartition(scores,-max(1,len(scores)//3))[-max(1,len(scores)//3):]
        index=int(selected[int(rng.integers(len(selected)))])
        return int(xs[index]),int(ys[index])

    for index,size in enumerate(major_sizes+micro_sizes):
        major=index<len(major_sizes);keep=bool(separation and major);tiny=not major and int(size)<=int(micro_max)
        placed=None
        for _ in range(48):
            center=choose_center(keep,tiny)
            if center is None:break
            if tiny:
                placed=_grow_micro_component(support,occupied,center,int(size),rng)
            else:
                placed=_grow_component(
                    support,occupied,center,int(size),aspect=float(rng.uniform(*aspect_range)),
                    angle=float(rng.uniform(0,math.pi)),roughness=roughness,rng=rng,
                    keep_separation=keep,occupied_rim=occupied_rim,
                )
            if placed is not None and any(forbidden_mask[y, x] for x, y in placed):
                # Do not crop or subtract the start footprint from an already
                # accepted component: retry the entire shape elsewhere.
                placed = None
            if placed is not None and _encloses_forbidden(placed, forbidden_mask):
                # Do not surround a start with a closed terrain ring either:
                # its exact footprint must remain a natural opening.
                placed = None
            if placed is not None:break
        if placed is None:
            center=choose_center(False)
            if center is not None:
                placed=_grow_component(support,occupied,center,int(size),aspect=1.0,angle=0.0,roughness=roughness,rng=rng,keep_separation=False,occupied_rim=occupied_rim)
                if placed is not None and any(forbidden_mask[y, x] for x, y in placed):
                    placed = None
                if placed is not None and _encloses_forbidden(placed, forbidden_mask):
                    placed = None
        if placed is None:
            free=np.argwhere(support&~occupied&~forbidden_mask)
            if not len(free):break
            y,x=map(int,free[0]);placed=[(x,y)]
        for x,y in placed:occupied[y,x]=True;out[y,x]=True
        if major:occupied_rim=touching(occupied)

    missing=total-int(out.sum())
    while missing>0:
        frontier=support&~occupied&touching(occupied)
        if not frontier.any():frontier=support&~occupied
        ys,xs=np.where(frontier)
        if not len(xs):break
        order=np.argsort(roughness[ys,xs]);take=min(missing,len(order))
        for index in order[:take]:
            x,y=int(xs[index]),int(ys[index]);occupied[y,x]=True;out[y,x]=True
        missing-=take
    return out


__all__=("place_components",)
