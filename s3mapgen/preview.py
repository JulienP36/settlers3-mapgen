from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .constants import *
from .model import MapState

WATER_COLORS=[(74,164,237),(63,151,226),(53,138,215),(43,125,204),(34,111,190),(27,98,176),(22,84,160),(17,69,143)]
PALETTE={
    GRASS:(72,148,69),ROCK_TRANS_1:(112,118,104),ROCK_TRANS_2:(126,130,118),ROCKY:(109,109,103),
    ROCK_SNOW_TRANS:(152,154,148),SNOW_TRANS:(208,210,205),SNOW:(244,245,242),SHORE:(211,192,131),
    DESERT:(211,177,80),DESERT_TRANS:(187,157,75),GRASS_DESERT_TRANS:(153,143,87),
    SWAMP:(76,101,56),SWAMP_TRANS:(94,119,67),GRASS_SWAMP_TRANS:(115,139,78),
    96:(65,176,221),97:(50,161,210),98:(38,145,196),99:(28,130,182)
}

def render(state:MapState, output:Path|str|None=None, scale:int=1, labels:bool=True)->Image.Image:
    T,O=state.terrain,state.objects;side=state.side
    rgb=np.zeros((side,side,3),np.uint8)
    for i,c in enumerate(WATER_COLORS):rgb[T==i]=c
    for tid,c in PALETTE.items():rgb[T==tid]=c
    rgb[rgb.sum(axis=2)==0]=(150,150,150)
    for oid in (68,69,70,71,72):rgb[O==oid]=(25,88,34)
    rgb[O==84]=(81,145,73);rgb[(O>=115)&(O<=126)]=(205,205,198)
    im=Image.fromarray(rgb,'RGB')
    if scale!=1:im=im.resize((side*scale,side*scale),Image.Resampling.NEAREST)
    if labels:
        d=ImageDraw.Draw(im)
        try:font=ImageFont.truetype('DejaVuSans-Bold.ttf',max(10,9*scale))
        except:font=ImageFont.load_default()
        for i,(x,y) in enumerate(state.starts,1):
            X,Y=x*scale,y*scale;r=max(4,5*scale)
            d.ellipse((X-r,Y-r,X+r,Y+r),outline='white',width=max(1,scale))
            d.text((X+r+2,Y-r),f'P{i}',fill='white',font=font,stroke_width=max(1,scale//2),stroke_fill='black')
    if output:im.save(output)
    return im
