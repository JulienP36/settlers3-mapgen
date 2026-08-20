from __future__ import annotations
from pathlib import Path
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw,ImageFont
from .constants import *
from .model import MapState

WATER_COLORS=[(74,164,237),(63,151,226),(53,138,215),(43,125,204),(34,111,190),(27,98,176),(22,84,160),(17,69,143)]
PALETTE={GRASS:(72,148,69),ROCK_TRANS_1:(112,118,104),ROCK_TRANS_2:(126,130,118),ROCKY:(109,109,103),ROCK_SNOW_TRANS:(152,154,148),SNOW_TRANS:(208,210,205),SNOW:(244,245,242),SHORE:(211,192,131),DESERT:(211,177,80),DESERT_TRANS:(187,157,75),GRASS_DESERT_TRANS:(153,143,87),SWAMP:(76,101,56),SWAMP_TRANS:(94,119,67),GRASS_SWAMP_TRANS:(115,139,78),22:(147,112,72),28:(126,99,66),34:(116,116,108),96:(65,176,221),97:(50,161,210),98:(38,145,196),99:(28,130,182)}

# Settlers III player-color palette validated for v1.6 STABLE.
# Order follows player slots P1..P20; P1 is the canonical S3 red.  The palette
# is intentionally centralized here so the global starts, claims and labels all
# use exactly the same values.
PLAYER_COLORS=(
    (205,30,16),   # P1 red
    (30,110,205),  # P2 blue
    (215,210,32),  # P3 yellow
    (44,160,72),   # P4 green
    (210,118,24),  # P5 orange
    (25,190,190),  # P6 cyan
    (200,40,190),  # P7 magenta
    (72,68,76),    # P8 charcoal
    (238,238,228), # P9 ivory / near-white (in-game reference)
    (45,55,205),   # P10 royal blue
    (168,85,30),   # P11 brown
    (92,98,104),   # P12 graphite
    (150,60,185),  # P13 violet
    (35,120,45),   # P14 dark green
    (215,165,170), # P15 pink
    (115,195,135), # P16 mint
    (165,35,65),   # P17 burgundy
    (180,125,195), # P18 lavender
    (205,180,135), # P19 beige
    (125,160,205), # P20 light blue
)

HEATMAP_RESOURCES={
    'trees':'Trees','building_stones':'Building Stones','fish':'Fish',
    'coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gemstones','sulfur':'Sulfur',
}

START_TERRITORY_RADIUS=35

# Exact canonical initial claim recovered from the native SAV corpus.
# 145 independent 3500-cell regions with a 71x71 extent yielded the same mask.
# Each tuple is inclusive (min_dx,max_dx) for dy=-35..+35 around the original
# start coordinates stored in the SAV v11 player block.
INITIAL_TERRITORY_ROW_RANGES=(
    (-24,-11),(-27,-8),(-28,-5),(-30,-2),(-31,0),(-32,2),(-32,3),(-33,5),(-33,7),(-34,8),
    (-34,9),(-35,11),(-35,12),(-35,13),(-35,14),(-35,15),(-35,16),(-35,17),(-35,18),(-35,19),
    (-35,20),(-35,21),(-35,22),(-35,23),(-35,24),(-34,24),(-34,25),(-34,26),(-34,26),(-33,27),
    (-33,28),(-32,28),(-32,29),(-32,30),(-31,30),(-31,31),(-30,31),(-30,32),(-29,32),(-28,32),
    (-28,33),(-27,33),(-26,34),(-26,34),(-25,34),(-24,34),(-24,35),(-23,35),(-22,35),(-21,35),
    (-20,35),(-19,35),(-18,35),(-17,35),(-16,35),(-15,35),(-14,35),(-13,35),(-12,35),(-11,35),
    (-9,34),(-8,34),(-7,34),(-5,33),(-3,32),(-2,32),(0,31),(2,30),(5,28),(8,27),(11,24),
)

def _canonical_territory_cells():
    out=set()
    for idx,(x0,x1) in enumerate(INITIAL_TERRITORY_ROW_RANGES):
        dy=idx-START_TERRITORY_RADIUS
        for dx in range(x0,x1+1): out.add((dx,dy))
    return frozenset(out)

_CANONICAL_TERRITORY=_canonical_territory_cells()
_CANONICAL_BOUNDARY=frozenset(
    (x,y) for x,y in _CANONICAL_TERRITORY
    if any((x+dx,y+dy) not in _CANONICAL_TERRITORY for dx,dy in HEX6)
)
assert len(_CANONICAL_TERRITORY)==3500
assert len(_CANONICAL_BOUNDARY)==210

def initial_territory_cells(start:tuple[int,int], side:int)->set[tuple[int,int]]:
    cx,cy=start
    return {((cx+dx)%side,(cy+dy)%side) for dx,dy in _CANONICAL_TERRITORY}

def initial_territory_boundary(start:tuple[int,int], side:int)->set[tuple[int,int]]:
    cx,cy=start
    return {((cx+dx)%side,(cy+dy)%side) for dx,dy in _CANONICAL_BOUNDARY}

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
        values[np.isin(O,[68,69,70,71,72,73,74,75,76,77,78,79,80,81,84])]=1.0
    elif resource=='building_stones':
        active=(O>=115)&(O<=126);values[active]=(127-O[active]).astype(np.float32)
    elif resource=='fish':
        water=np.isin(T,WATER_IDS);qty=(R&0x0F).astype(np.float32);m=water&((R&0xF0)==0)&(qty>0);values[m]=qty[m]
    else:
        fam={'coal':0x10,'iron':0x20,'gold':0x30,'gems':0x40,'sulfur':0x50}.get(resource)
        if fam is not None:
            m=(R&0xF0)==fam;values[m]=(R[m]&0x0F).astype(np.float32)
    return ndimage.gaussian_filter(values,sigma=max(4.0,state.side/96.0),mode='nearest')

def _heatmap_rgb(state:MapState,resource:str)->np.ndarray:
    d=_resource_density(state,resource);positive=d[d>0]
    rgb=np.zeros((state.side,state.side,3),np.uint8);rgb[:]=(25,28,32)
    if not len(positive):return rgb
    hi=float(np.percentile(positive,99.0));hi=max(hi,float(positive.max())*0.25,1e-6);x=np.clip(d/hi,0.0,1.0)
    r=np.clip(1.7*x-0.45,0,1);g=np.clip(1.8*x,0,1)*np.clip(1.6-1.1*x,0,1);b=np.clip(1.25-1.5*x,0,1)
    rgb[:,:,0]=np.rint(r*255).astype(np.uint8);rgb[:,:,1]=np.rint(g*255).astype(np.uint8);rgb[:,:,2]=np.rint(b*255).astype(np.uint8);rgb[d<=0]=(25,28,32)
    return rgb

def _overlay_rgb(state:MapState,view:str,heatmap_resource:str='trees')->np.ndarray:
    T,O,R,H,C=state.terrain,state.objects,state.resources,state.height,state.claim;side=state.side
    rgb=np.zeros((side,side,3),np.uint8)
    if view=='heightmap': rgb[:]=np.repeat(H[:,:,None],3,axis=2)
    elif view=='resources':
        rgb[:]=(45,45,45);water=np.isin(T,WATER_IDS);rgb[water]=(36,91,145);fam=R&0xF0
        rgb[fam==0x10]=(0,0,0);rgb[fam==0x20]=(255,148,0);rgb[fam==0x30]=(255,255,0);rgb[fam==0x40]=(206,0,0);rgb[fam==0x50]=(196,178,92)
        fish=water&((R&0xF0)==0)&((R&0x0F)>0);rgb[fish]=(70,210,240)
    elif view=='territories':
        rgb[:]=(65,65,65);palette=np.asarray(PLAYER_COLORS,np.uint8);claimed=C!=255
        if claimed.any():rgb[claimed]=palette[C[claimed]%len(palette)]
    elif view=='paths':
        # Paths view is intentionally restricted to runtime Terrain 28.
        # Terrain 22 is agricultural ground and belongs to the Crops view, not Paths.
        base=_global_rgb(state);rgb[:]=(base.astype(np.float32)*0.35).astype(np.uint8);rgb[T==28]=(235,175,85)
    elif view=='crops':
        base=_global_rgb(state);rgb[:]=(base.astype(np.float32)*0.28).astype(np.uint8)
        wheat=(O>=85)&(O<=93);vine=(O>=94)&(O<=102);rice=(O>=103)&(O<=110)
        rgb[wheat]=(235,205,75);rgb[vine]=(165,85,185);rgb[rice]=(80,205,110)
    elif view=='heatmap': return _heatmap_rgb(state,heatmap_resource)
    else:return _global_rgb(state)
    return rgb

def _blend(global_rgb,overlay_rgb,alpha):
    a=max(0,min(100,int(alpha)))/100.0
    if a<=0:return global_rgb.copy()
    if a>=1:return overlay_rgb.copy()
    return np.rint(global_rgb.astype(np.float32)*(1-a)+overlay_rgb.astype(np.float32)*a).clip(0,255).astype(np.uint8)

def _label_font(size=12):
    try:return ImageFont.truetype('DejaVuSans-Bold.ttf',size)
    except OSError:return ImageFont.load_default()

def _pixel_label(text,color,size=12):
    font=_label_font(size);probe=Image.new('1',(96,32),0);d=ImageDraw.Draw(probe);box=d.textbbox((0,0),text,font=font)
    w=max(1,box[2]-box[0]);h=max(1,box[3]-box[1]);mask=Image.new('1',(w+6,h+6),0);ImageDraw.Draw(mask).text((3-box[0],3-box[1]),text,font=font,fill=1)
    outline=Image.new('1',mask.size,0)
    for ox,oy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)):
        shifted=Image.new('1',mask.size,0);shifted.paste(mask,(ox,oy));outline=Image.fromarray(np.maximum(np.asarray(outline,dtype=np.uint8),np.asarray(shifted,dtype=np.uint8)).astype(np.uint8)*255).convert('1')
    sprite=Image.new('RGB',mask.size,(0,0,0));sprite.paste(color,(0,0),mask);alpha=Image.fromarray(np.maximum(np.asarray(outline,dtype=np.uint8),np.asarray(mask,dtype=np.uint8)).astype(np.uint8)*255,'L');sprite.putalpha(alpha);return sprite

def _paint_initial_territories(rgb:np.ndarray,state:MapState)->None:
    """Paint the exact native initial-territory contour with a black halo.

    The colored center still occupies the exact 210-cell native boundary. The
    neighboring black cells are display-only and make pale player colors (P9
    in particular) readable over any terrain without changing map data.
    """
    side=state.side
    for i,start in enumerate(state.starts):
        boundary=initial_territory_boundary(start,side)
        halo=set()
        for x,y in boundary:
            for dx,dy in HEX6:
                q=((x+dx)%side,(y+dy)%side)
                if q not in boundary:halo.add(q)
        for x,y in halo:rgb[y,x]=(0,0,0)
        color=np.asarray(PLAYER_COLORS[i%len(PLAYER_COLORS)],np.uint8)
        for x,y in boundary:rgb[y,x]=color

def _draw_square_labels(im,state):
    for i,(x,y) in enumerate(state.starts,1):
        color=PLAYER_COLORS[(i-1)%len(PLAYER_COLORS)];label=_pixel_label(f'P {i}',color,12);im.paste(label,((x+START_TERRITORY_RADIUS+2)%state.side,max(0,y-label.height//2)),label)

def _project_point(x,y,source_height):return 2*x+(source_height-1-y),2*y

def _draw_projected_labels(im,state,source_height):
    for i,(x,y) in enumerate(state.starts,1):
        color=PLAYER_COLORS[(i-1)%len(PLAYER_COLORS)];X,Y=_project_point(x,y,source_height);label=_pixel_label(f'P {i}',color,14);im.paste(label,(X+2*START_TERRITORY_RADIUS+4,Y-label.height//2),label)

def project_parallelogram(im):
    src=im.convert('RGBA');w,h=src.size;px=np.asarray(src);expanded=np.repeat(np.repeat(px,2,axis=0),2,axis=1);canvas=np.zeros((2*h,2*w+(h-1),4),dtype=np.uint8)
    for y in range(h):
        shift=h-1-y;canvas[2*y:2*y+2,shift:shift+2*w]=expanded[2*y:2*y+2]
    return Image.fromarray(canvas,'RGBA')

def render(state, output=None, scale=1, labels=True, view='global', overlay_alpha=100, projection='square', heatmap_resource='trees'):
    base=_global_rgb(state);rgb=base if view=='global' else _blend(base,_overlay_rgb(state,view,heatmap_resource),overlay_alpha)
    if labels and view=='global':_paint_initial_territories(rgb,state)
    im=Image.fromarray(rgb,'RGB')
    if labels and view=='global' and projection=='square':_draw_square_labels(im,state)
    if projection=='parallelogram':
        source_height=im.height;im=project_parallelogram(im)
        if labels and view=='global':_draw_projected_labels(im,state,source_height)
    if scale!=1:im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
    if output:im.save(output)
    return im
