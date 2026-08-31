"""Champs de bruit déterministes utilisés par les générateurs procéduraux."""

from __future__ import annotations

import numpy as np
from scipy import ndimage


def fractal_value_field(
    side:int,
    rng:np.random.Generator,
    scales:tuple[float,...]=(0.012,0.030,0.070),
    interpolation_order:int=3,
)->np.ndarray:
    """Return a smooth multi-scale field derived only from ``rng``.

    The grid sizes are relative to the requested map side.  The function
    therefore synthesises a new field on every seed/size rather than resizing
    or consulting any native map silhouette.
    """

    field=np.zeros((side,side),dtype=float)
    weights=(0.58,0.29,0.13)
    for scale,weight in zip(scales,weights):
        cells=max(3,int(round(side*scale)))
        coarse=rng.normal(size=(cells+2,cells+2))
        layer=ndimage.zoom(coarse,(side/cells,side/cells),order=int(interpolation_order),mode="reflect")[:side,:side]
        layer=ndimage.gaussian_filter(layer,sigma=max(1.0,side/(cells*8)))
        field+=weight*layer/max(float(layer.std()),1e-9)
    return field/max(float(field.std()),1e-9)


def warped_fractal_field(
    side:int,
    rng:np.random.Generator,
    scales:tuple[float,...]=(0.012,0.030,0.070),
    warp_scale:float=0.020,
    warp_strength:float=0.055,
    interpolation_order:int=3,
)->np.ndarray:
    """Return a domain-warped deterministic fractal field."""

    source=fractal_value_field(side,rng,scales=scales,interpolation_order=interpolation_order)
    dx=fractal_value_field(side,rng,scales=(warp_scale,warp_scale*2.4,warp_scale*5.0),interpolation_order=interpolation_order)
    dy=fractal_value_field(side,rng,scales=(warp_scale*1.2,warp_scale*2.8,warp_scale*5.8),interpolation_order=interpolation_order)
    yy,xx=np.mgrid[:side,:side]
    amplitude=side*warp_strength
    coordinates=np.array((
        np.clip(yy+dy*amplitude,0,side-1),
        np.clip(xx+dx*amplitude,0,side-1),
    ))
    result=ndimage.map_coordinates(source,coordinates,order=int(interpolation_order),mode="reflect")
    return result/max(float(result.std()),1e-9)
