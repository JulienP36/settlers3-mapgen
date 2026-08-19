from __future__ import annotations
from pathlib import Path
import math
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
from .constants import *
from .model import MapState

WATER_COLORS=[(74,164,237),(63,151,226),(53,138,215),(43,125,204),(34,111,190),(27,98,176),(22,84,160),(17,69,143)]
PALETTE={GRASS:(72,148,69),ROCK_TRANS_1:(112,118,104),ROCK_TRANS_2:(126,130,118),ROCKY:(109,109,103),ROCK_SNOW_TRANS:(152,154,148),SNOW_TRANS:(208,210,205),SNOW:(244,245,242),SHORE:(211,192,131),DESERT:(211,177,80),DESERT_TRANS:(187,157,75),GRASS_DESERT_TRANS:(153,143,87),SWAMP:(76,101,56),SWAMP_TRANS:(94,119,67),GRASS_SWAMP_TRANS:(115,139,78),22:(147,112,72),28:(126,99,66),34:(116,116,108),96:(65,176,221),97:(50,161,210),98:(38,145,196),99:(28,130,182)}

PLAYER_COLORS=(
    (220,70,70),(70,120,230),(70,190,90),(225,190,60),(180,80,210),
    (50,190,190),(230,120,50),(120,120,220),(235,105,160),(125,190,55),
    (235,155,80),(80,165,225),(165,110,65),(190,190,190),(115,75,180),
    (70,150,115),(210,95,115),(150,155,55),(95,105,190),(200,135,205),
)

HEATMAP_RESOURCES={
    'trees':'Trees','building_stones':'Building Stones','fish':'Fish',
    'coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gemstones','sulfur':'Sulfur',
}

# Immediate-start native SAV calibration: each 4P initial claim contains exactly
# 3500 cells and spans 71x71 array coordinates. Radius 35 is expressed in the
# oblique/in-game visual lattice. Its square-array preview is therefore sheared.
START_TERRITORY_RADIUS=35


def _global_rgb(state:MapState)->np.ndarray:
    T,O=state.terrain,state.objects;side=state.side
    rgb=np.zeros((side,side,3),np.uint8)
    for i,c in enumerate(WATER_COLORS):rgb[T==i]=c
    for tid,c in PALETTE.items():rgb[T==tid]=c
    rgb[rgb.sum(axis=2)==0]=(150,150,150)
    adult=(O>=68)&(O<=81)&~np.isin(O,[78,79])
    rgb[adult]=(25,88,34);rgb[np.isin(O,[78,79])]=(46,113,51);rgb[O==84]=(81,145,73)
    rgb[(O>=115)&(O<=126)]=(205,205,198);rgb[O==127]=(150,150,145)
    return rgb


def _resource_density(state:MapState,resource:str)->np.ndarray:
    T,O,R=state.terrain,state.objects,state.resources
    values=np.zeros((state.side,state.side),np.float32)
    if resource=='trees':
        ids=[68,69,70,71,72,73,74,75,76,77,78,79,80,81,84]
        values[np.isin(O,ids)]=1.0
    elif resource=='building_stones':
        active=(O>=115)&(O<=126)
        values[active]=(127-O[active]).astype(np.float32)
    elif resource=='fish':
        water=np.isin(T,WATER_IDS);qty=(R&0x0F).astype(np.float32)
        values[water&((R&0xF0)==0)&(qty>0)]=qty[water&((R&0xF0)==0)&(qty>0)]
    else:
        fam={'coal':0x10,'iron':0x20,'gold':0x30,'gems':0x40,'sulfur':0x50}.get(resource)
        if fam is not None:
            mask=(R&0xF0)==fam
            values[mask]=(R[mask]&0x0F).astype(np.float32)
    # Broad enough to reveal strategically rich zones, local enough to compare starts/regions.
    return ndimage.gaussian_filter(values,sigma=max(4.0,state.side/96.0),mode='nearest')


def _heatmap_rgb(state:MapState,resource:str)->np.ndarray:
    d=_resource_density(state,resource)
    positive=d[d>0]
    rgb=np.zeros((state.side,state.side,3),np.uint8);rgb[:]=(25,28,32)
    if not len(positive):return rgb
    # Robust normalization prevents one extreme cluster from flattening the whole map.
    hi=float(np.percentile(positive,99.0));hi=max(hi,float(positive.max())*0.25,1e-6)
    x=np.clip(d/hi,0.0,1.0)
    # Deterministic blue -> cyan -> yellow -> red heat scale.
    r=np.clip(1.7*x-0.45,0,1)
    g=np.clip(1.8*x,0,1)*np.clip(1.6-1.1*x,0,1)
    b=np.clip(1.25-1.5*x,0,1)
    rgb[:,:,0]=np.rint(r*255).astype(np.uint8)
    rgb[:,:,1]=np.rint(g*255).astype(np.uint8)
    rgb[:,:,2]=np.rint(b*255).astype(np.uint8)
    rgb[d<=0]=(25,28,32)
    return rgb


def _overlay_rgb(state:MapState,view:str,heatmap_resource:str='trees')->np.ndarray:
    T,O,R,H,C=state.terrain,state.objects,state.resources,state.height,state.claim;side=state.side
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
        palette=np.asarray(PLAYER_COLORS,np.uint8)
        claimed=C!=255
        if claimed.any():rgb[claimed]=palette[C[claimed]%len(palette)]
    elif view=='paths':
        base=_global_rgb(state);rgb[:]=(base.astype(np.float32)*0.35).astype(np.uint8)
        rgb[T==28]=(235,175,85);rgb[T==22]=(195,135,75)
    elif view=='crops':
        base=_global_rgb(state);rgb[:]=(base.astype(np.float32)*0.28).astype(np.uint8)
        wheat=(O>=85)&(O<=93);vine=(O>=94)&(O<=102);rice=(O>=103)&(O<=110)
        rgb[wheat]=(235,205,75);rgb[vine]=(165,85,185);rgb[rice]=(80,205,110)
    elif view=='heatmap':
        return _heatmap_rgb(state,heatmap_resource)
    else:
        return _global_rgb(state)
    return rgb


def _blend(global_rgb:np.ndarray,overlay_rgb:np.ndarray,alpha:int)->np.ndarray:
    a=max(0,min(100,int(alpha)))/100.0
    if a<=0:return global_rgb.copy()
    if a>=1:return overlay_rgb.copy()
    return np.rint(global_rgb.astype(np.float32)*(1-a)+overlay_rgb.astype(np.float32)*a).clip(0,255).astype(np.uint8)


def _pixel_label(text:str,color:tuple[int,int,int])->Image.Image:
    font=ImageFont.load_default()
    probe=Image.new('1',(64,20),0);d=ImageDraw.Draw(probe)
    box=d.textbbox((0,0),text,font=font,stroke_width=0)
    w=max(1,box[2]-box[0]);h=max(1,box[3]-box[1])
    mask=Image.new('1',(w+4,h+4),0);md=ImageDraw.Draw(mask)
    md.text((2-box[0],2-box[1]),text,font=font,fill=1)
    outline=Image.new('1',mask.size,0)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
        shifted=Image.new('1',mask.size,0);shifted.paste(mask,(ox,oy))
        outline=Image.fromarray(np.maximum(np.asarray(outline,dtype=np.uint8),np.asarray(shifted,dtype=np.uint8)).astype(np.uint8)*255).convert('1')
    sprite=Image.new('RGB',mask.size,(0,0,0));sprite.paste(color,(0,0),mask)
    alpha=Image.fromarray(np.maximum(np.asarray(outline,dtype=np.uint8),np.asarray(mask,dtype=np.uint8)).astype(np.uint8)*255,'L')
    sprite.putalpha(alpha)
    return sprite


def _square_territory_points(x:int,y:int,r:int)->list[tuple[int,int]]:
    pts=[]
    for n in range(144):
        a=2.0*math.pi*n/144.0
        dx=r*math.cos(a)+(r/2.0)*math.sin(a)
        dy=r*math.sin(a)
        pts.append((int(round(x+dx)),int(round(y+dy))))
    return pts


def _draw_square_territories(im:Image.Image,state:MapState)->None:
    d=ImageDraw.Draw(im)
    for i,(x,y) in enumerate(state.starts,1):
        color=PLAYER_COLORS[(i-1)%len(PLAYER_COLORS)]
        pts=_square_territory_points(x,y,START_TERRITORY_RADIUS)
        d.line(pts+[pts[0]],fill=color,width=1)


def _draw_square_labels(im:Image.Image,state:MapState)->None:
    for i,(x,y) in enumerate(state.starts,1):
        color=PLAYER_COLORS[(i-1)%len(PLAYER_COLORS)]
        label=_pixel_label(f'P{i}',color)
        im.paste(label,(x+START_TERRITORY_RADIUS+2,y-label.height//2),label)


def _project_point(x:int,y:int,source_height:int)->tuple[int,int]:
    return 2*x+(source_height-1-y),2*y


def _draw_projected_territories(im:Image.Image,state:MapState,source_height:int)->None:
    d=ImageDraw.Draw(im);r=2*START_TERRITORY_RADIUS
    for i,(x,y) in enumerate(state.starts,1):
        color=PLAYER_COLORS[(i-1)%len(PLAYER_COLORS)]
        X,Y=_project_point(x,y,source_height)
        d.ellipse((X-r,Y-r,X+r,Y+r),outline=color,width=2)


def _draw_projected_labels(im:Image.Image,state:MapState,source_height:int)->None:
    for i,(x,y) in enumerate(state.starts,1):
        color=PLAYER_COLORS[(i-1)%len(PLAYER_COLORS)]
        X,Y=_project_point(x,y,source_height)
        base=_pixel_label(f'P{i}',color)
        label=base.resize((base.width*2,base.height*2),Image.Resampling.NEAREST)
        im.paste(label,(X+2*START_TERRITORY_RADIUS+4,Y-label.height//2),label)


def project_parallelogram(im:Image.Image)->Image.Image:
    src=im.convert('RGBA');w,h=src.size
    px=np.asarray(src)
    expanded=np.repeat(np.repeat(px,2,axis=0),2,axis=1)
    canvas=np.zeros((2*h,2*w+(h-1),4),dtype=np.uint8)
    for y in range(h):
        shift=h-1-y
        canvas[2*y:2*y+2,shift:shift+2*w]=expanded[2*y:2*y+2]
    return Image.fromarray(canvas,'RGBA')


def render(state:MapState, output:Path|str|None=None, scale:int=1, labels:bool=True,
           view:str='global', overlay_alpha:int=100, projection:str='square',
           heatmap_resource:str='trees')->Image.Image:
    base=_global_rgb(state)
    rgb=base if view=='global' else _blend(base,_overlay_rgb(state,view,heatmap_resource),overlay_alpha)
    im=Image.fromarray(rgb,'RGB')
    if labels and view=='global' and projection=='square':
        _draw_square_territories(im,state)
        _draw_square_labels(im,state)
    if projection=='parallelogram':
        source_height=im.height
        im=project_parallelogram(im)
        if labels and view=='global':
            _draw_projected_territories(im,state,source_height)
            _draw_projected_labels(im,state,source_height)
    if scale!=1:im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
    if output:im.save(output)
    return im
