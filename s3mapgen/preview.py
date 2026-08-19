from __future__ import annotations
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from .constants import *
from .model import MapState

WATER_COLORS=[(74,164,237),(63,151,226),(53,138,215),(43,125,204),(34,111,190),(27,98,176),(22,84,160),(17,69,143)]
PALETTE={GRASS:(72,148,69),ROCK_TRANS_1:(112,118,104),ROCK_TRANS_2:(126,130,118),ROCKY:(109,109,103),ROCK_SNOW_TRANS:(152,154,148),SNOW_TRANS:(208,210,205),SNOW:(244,245,242),SHORE:(211,192,131),DESERT:(211,177,80),DESERT_TRANS:(187,157,75),GRASS_DESERT_TRANS:(153,143,87),SWAMP:(76,101,56),SWAMP_TRANS:(94,119,67),GRASS_SWAMP_TRANS:(115,139,78),96:(65,176,221),97:(50,161,210),98:(38,145,196),99:(28,130,182)}


def _font(scale):
    try:return ImageFont.truetype('DejaVuSans-Bold.ttf',max(10,9*scale))
    except:return ImageFont.load_default()


def _global_rgb(state:MapState)->np.ndarray:
    T,O=state.terrain,state.objects;side=state.side
    rgb=np.zeros((side,side,3),np.uint8)
    for i,c in enumerate(WATER_COLORS):rgb[T==i]=c
    for tid,c in PALETTE.items():rgb[T==tid]=c
    rgb[rgb.sum(axis=2)==0]=(150,150,150)
    for oid in (68,69,70,71,72):rgb[O==oid]=(25,88,34)
    rgb[O==84]=(81,145,73);rgb[(O>=115)&(O<=126)]=(205,205,198)
    return rgb


def _overlay_rgb(state:MapState,view:str)->np.ndarray:
    T,R,H,C=state.terrain,state.resources,state.height,state.claim;side=state.side
    rgb=np.zeros((side,side,3),np.uint8)
    if view=='heightmap':
        rgb[:]=np.repeat(H[:,:,None],3,axis=2)
    elif view=='resources':
        rgb[:]=(45,45,45)
        water=np.isin(T,WATER_IDS);rgb[water]=(36,91,145)
        fam=R&0xF0
        rgb[fam==0x10]=(50,50,50);rgb[fam==0x20]=(168,120,84);rgb[fam==0x30]=(230,190,55);rgb[fam==0x40]=(76,190,220);rgb[fam==0x50]=(214,214,70)
        fish=water&((R&0xF0)==0)&((R&0x0F)>0);rgb[fish]=(70,210,240)
    elif view=='territories':
        rgb[:]=(65,65,65)
        palette=np.array([(220,70,70),(70,120,230),(70,190,90),(225,190,60),(180,80,210),(50,190,190),(230,120,50),(120,120,220)],np.uint8)
        claimed=C!=255
        if claimed.any():rgb[claimed]=palette[C[claimed]%len(palette)]
    else:
        return _global_rgb(state)
    return rgb


def _blend(global_rgb:np.ndarray,overlay_rgb:np.ndarray,alpha:int)->np.ndarray:
    a=max(0,min(100,int(alpha)))/100.0
    if a<=0:return global_rgb.copy()
    if a>=1:return overlay_rgb.copy()
    return np.rint(global_rgb.astype(np.float32)*(1-a)+overlay_rgb.astype(np.float32)*a).clip(0,255).astype(np.uint8)


def project_parallelogram(im:Image.Image,shear:float=0.5)->Image.Image:
    """Deterministic row shear matching the game's parallelogram-style map footprint."""
    src=im.convert('RGBA');w,h=src.size
    max_shift=int(round((h-1)*shear));px=np.asarray(src)
    canvas=np.zeros((h,w+max_shift,4),dtype=np.uint8)
    for y in range(h):
        shift=int(round((h-1-y)*shear));canvas[y,shift:shift+w]=px[y]
    return Image.fromarray(canvas,'RGBA')


def render(state:MapState, output:Path|str|None=None, scale:int=1, labels:bool=True,
           view:str='global', overlay_alpha:int=100, projection:str='square')->Image.Image:
    base=_global_rgb(state)
    rgb=base if view=='global' else _blend(base,_overlay_rgb(state,view),overlay_alpha)
    im=Image.fromarray(rgb,'RGB')
    if scale!=1:im=im.resize((state.side*scale,state.side*scale),Image.Resampling.NEAREST)
    if labels and view=='global':
        d=ImageDraw.Draw(im);font=_font(scale)
        for i,(x,y) in enumerate(state.starts,1):
            X,Y=x*scale,y*scale;r=max(4,5*scale);d.ellipse((X-r,Y-r,X+r,Y+r),outline='white',width=max(1,scale));d.text((X+r+2,Y-r),f'P{i}',fill='white',font=font,stroke_width=max(1,scale//2),stroke_fill='black')
    if projection=='parallelogram':im=project_parallelogram(im)
    if output:im.save(output)
    return im
