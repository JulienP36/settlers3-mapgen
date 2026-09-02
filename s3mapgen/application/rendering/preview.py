"""Deterministic map rendering from real MapState data and validated overlays."""

from __future__ import annotations
import math
import numpy as np
from scipy import ndimage
from PIL import Image,ImageDraw
from ...map_data.constants import *
from ...map_data.hexgrid import hex_distance
from ...map_data.model import MapState
from ..paths import START_MARKER_SHEET

WATER_COLORS=[(74,164,237),(63,151,226),(53,138,215),(43,125,204),(34,111,190),(27,98,176),(22,84,160),(17,69,143)]
PALETTE={GRASS:(72,148,69),18:(101,166,78),19:(116,177,88),DRY_GRASS:(155,166,80),ROCK_TRANS_1:(112,118,104),ROCK_TRANS_2:(126,130,118),ROCKY:(109,109,103),ROCK_SNOW_TRANS:(152,154,148),SNOW_TRANS:(208,210,205),SNOW:(244,245,242),SHORE:(211,192,131),DESERT:(211,177,80),DESERT_TRANS:(187,157,75),GRASS_DESERT_TRANS:(153,143,87),SWAMP:(25,89,79),SWAMP_TRANS:(42,111,88),GRASS_SWAMP_TRANS:(79,132,73),MUD:(137,98,62),MUD_TRANS_2:(116,82,54),MUD_TRANS_1:(86,61,45),22:(147,112,72),28:(126,99,66),34:(116,116,108),96:(65,176,221),97:(50,161,210),98:(38,145,196),99:(28,130,182)}

# Settlers III player-color palette validated for v1.6 STABLE.
# Order follows player slots P1..P20; P1 is the canonical S3 red.  The palette
# is intentionally centralized here so Starts, Territories and Batch markers
# all use exactly the same player-slot order.
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

def _load_player_start_markers(path=START_MARKER_SHEET)->tuple[Image.Image,...]:
    """Extract the 20 user-provided native start markers without inventing pixels.

    The reference has a flat editor-grass background. Connected components give
    the exact two rows J1..J10 then J11..J20; the background becomes alpha.
    """
    try:
        sheet=Image.open(path).convert('RGBA')
    except OSError:
        return ()
    rgba=np.asarray(sheet);background=rgba[0,0,:3]
    foreground=np.any(rgba[:,:,:3]!=background,axis=2)
    labels,count=ndimage.label(foreground,structure=np.ones((3,3),dtype=np.uint8))
    boxes=[]
    for component in range(1,count+1):
        ys,xs=np.where(labels==component)
        if len(xs)<100:continue
        boxes.append((int(ys.min()),int(xs.min()),int(ys.max()+1),int(xs.max()+1),component))
    boxes.sort(key=lambda box:(box[0],box[1]))
    if len(boxes)!=20:return ()
    sprites=[]
    for y0,x0,y1,x1,component in boxes:
        crop=rgba[y0:y1,x0:x1].copy()
        crop[:,:,3]=np.where(labels[y0:y1,x0:x1]==component,255,0).astype(np.uint8)
        sprites.append(Image.fromarray(crop,'RGBA'))
    return tuple(sprites)

PLAYER_START_MARKERS=_load_player_start_markers()

HEATMAP_RESOURCES={
    'trees':'Trees','building_stones':'Building Stones','fish':'Fish',
    'coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gemstones','sulfur':'Sulfur',
}

START_TERRITORY_RADIUS=35

# Historical reconstruction reference only; this is not a native field.
# 145 independent 3500-cell regions with a 71x71 extent yielded the same shape,
# but the complete per-file mask is still intentionally not inferred here.
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
    # Static world-decor families are single-cell anchors in the preview.  The
    # colors are intentionally restrained so they remain legible over their
    # ecological support without pretending to be the game's sprites.
    rgb[np.isin(O,range(1,29))]=(130,130,126)      # stones
    rgb[np.isin(O,range(29,34))]=(126,91,58)       # wrecks
    rgb[O==34]=(112,106,106)                      # graves
    rgb[np.isin(O,range(35,43))]=(86,132,62)      # plants / fungi / stumps
    rgb[np.isin(O,range(43,45))]=(72,84,58)       # dead trees
    rgb[np.isin(O,range(45,50))]=(180,134,52)     # desert props
    rgb[np.isin(O,range(50,62))]=(66,137,58)      # flowers / bushes
    rgb[np.isin(O,range(62,68))]=(55,130,92)      # reeds
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
        rgb[:]=(65,65,65);palette=np.asarray(PLAYER_COLORS,np.uint8)
        # SAV claims are the authoritative runtime raster.  MAP/EDM files do
        # not carry claims, so show the known initial claim footprint instead
        # of leaving the validated Frontières view empty.
        claims=C if np.any(C<len(palette)) else _estimated_initial_claim_raster(state)
        claimed=claims<len(palette)
        if claimed.any():rgb[claimed]=palette[claims[claimed]]
    elif view=='initial_territory':
        rgb[:]=(65,65,65);palette=np.asarray(PLAYER_COLORS,np.uint8)
        # This view is intentionally stricter than ``territories``: it only
        # paints coordinates explicitly supplied by the SAV decoder.  Missing
        # direct cells stay neutral; no start/radius/canonical fallback is
        # permitted.
        claims=_direct_initial_claim_raster(state)
        claimed=claims<len(palette)
        if claimed.any():
            rgb[claimed]=palette[claims[claimed]]
            # A solid player-colour fill is too easy to confuse with the
            # runtime Territories view.  Add deterministic white diagonal
            # hatch marks only inside the direct mask, without changing any
            # source cell or implying an additional gameplay field.
            yy,xx=np.indices((side,side))
            hatch=claimed & (((xx+yy)%8)<2)
            rgb[hatch]=(245,245,245)
    elif view=='paths':
        # Paths view is intentionally restricted to runtime Terrain 28.
        # Terrain 22 is agricultural ground and belongs to the Crops view, not Paths.
        base=_global_rgb(state);rgb[:]=(base.astype(np.float32)*0.35).astype(np.uint8);rgb[T==28]=(235,175,85)
    elif view=='crops':
        base=_global_rgb(state);rgb[:]=(base.astype(np.float32)*0.28).astype(np.uint8)
        wheat=(O>=85)&(O<=93);vine=(O>=94)&(O<=102);rice=(O>=103)&(O<=110);bee_nests=(O>=247)&(O<=253)
        rgb[wheat]=(235,205,75);rgb[vine]=(165,85,185);rgb[rice]=(80,205,110);rgb[bee_nests]=(205,118,24)
    elif view=='heatmap': return _heatmap_rgb(state,heatmap_resource)
    else:return _global_rgb(state)
    return rgb

def _blend(global_rgb,overlay_rgb,alpha):
    a=max(0,min(100,int(alpha)))/100.0
    if a<=0:return global_rgb.copy()
    if a>=1:return overlay_rgb.copy()
    return np.rint(global_rgb.astype(np.float32)*(1-a)+overlay_rgb.astype(np.float32)*a).clip(0,255).astype(np.uint8)

def _project_point(x,y,source_height):return 2*x+(source_height-1-y),2*y

def _fallback_start_marker(player_index:int,projected:bool=False,scale:int=1)->Image.Image:
    base=(36,48) if projected else (18,24);size=(base[0]*scale,base[1]*scale);w,h=size;color=PLAYER_COLORS[player_index%len(PLAYER_COLORS)]
    marker=Image.new('RGBA',size,(0,0,0,0));draw=ImageDraw.Draw(marker)
    draw.ellipse((1,1,w-2,w-2),fill=color,outline=(0,0,0,255),width=max(1,w//12))
    draw.polygon(((w//2,h-1),(w//2-w//5,w-2),(w//2+w//5,w-2)),fill=color,outline=(0,0,0,255))
    return marker

BOUNDARY_START_MARKER_SIZE_SQUARE=(1,1)
BOUNDARY_START_MARKER_SIZE_PROJECTED=(2,2)

def _apply_marker_opacity(marker:Image.Image,opacity:int)->Image.Image:
    opacity=max(0,min(100,int(opacity)))
    if opacity>=100:return marker
    marker=marker.copy();alpha=np.asarray(marker.getchannel('A'),dtype=np.uint16)
    marker.putalpha(Image.fromarray(((alpha*opacity+50)//100).astype(np.uint8),'L'))
    return marker

def _start_marker(player_index:int,projected:bool=False,scale:int=1,opacity:int=100)->Image.Image:
    if PLAYER_START_MARKERS:
        marker=PLAYER_START_MARKERS[player_index%len(PLAYER_START_MARKERS)]
        base=(marker.width,marker.height) if projected else (max(1,marker.width//2),max(1,marker.height//2))
        target=(base[0]*scale,base[1]*scale)
        if marker.size!=target:marker=marker.resize(target,Image.Resampling.NEAREST)
        return _apply_marker_opacity(marker,opacity)
    return _apply_marker_opacity(_fallback_start_marker(player_index,projected,scale),opacity)

def _boundary_start_marker(player_index:int,projected:bool,opacity:int)->Image.Image:
    marker=_start_marker(player_index,projected,1,opacity)
    target=BOUNDARY_START_MARKER_SIZE_PROJECTED if projected else BOUNDARY_START_MARKER_SIZE_SQUARE
    return marker if marker.size==target else marker.resize(target,Image.Resampling.NEAREST)

def _centered_marker_origin(marker:Image.Image,x:int,y:int)->tuple[int,int]:
    """Anchor a marker by its geometric centre, never by a corner or its foot."""
    return int(x)-marker.width//2,int(y)-marker.height//2

def _ordered_boundary_offsets(projected:bool)->tuple[tuple[int,int],...]:
    """Return the historical reconstructed boundary in deterministic order.

    Kept as an analysis reference only; rendering uses explicit direct cells
    supplied by a format decoder instead of this table.
    """
    def screen_point(offset):
        x,y=offset
        return (2*x-y,2*y) if projected else (x,y)
    return tuple(sorted(_CANONICAL_BOUNDARY,key=lambda p:(math.atan2(screen_point(p)[1],screen_point(p)[0]),screen_point(p)[0],screen_point(p)[1])))

def _draw_square_start_markers(im:Image.Image,state:MapState,scale:int=1,include_boundaries:bool=False,opacity:int=100)->None:
    for i,(x,y) in enumerate(state.starts):
        marker=_start_marker(i,False,scale,opacity)
        if include_boundaries:
            boundary_marker=_boundary_start_marker(i,False,opacity)
            for bx,by in _ordered_initial_boundary(state,i,False):
                im.paste(boundary_marker,_centered_marker_origin(boundary_marker,bx,by),boundary_marker)
        im.paste(marker,_centered_marker_origin(marker,x,y),marker)

def _draw_projected_start_markers(im:Image.Image,state:MapState,source_height:int,scale:int=1,include_boundaries:bool=False,opacity:int=100)->None:
    for i,(x,y) in enumerate(state.starts):
        marker=_start_marker(i,True,scale,opacity)
        if include_boundaries:
            boundary_marker=_boundary_start_marker(i,True,opacity)
            for bx,by in _ordered_initial_boundary(state,i,True):
                X,Y=_project_point(bx,by,source_height)
                im.paste(boundary_marker,_centered_marker_origin(boundary_marker,X,Y),boundary_marker)
        X,Y=_project_point(x,y,source_height)
        im.paste(marker,_centered_marker_origin(marker,X,Y),marker)

def _draw_start_marker_layer(im:Image.Image,state:MapState,projection:str='square',scale:int=1,include_boundaries:bool=False,opacity:int=100)->None:
    """Draw only the start-marker layer on an already rendered map image."""
    scale=max(1,int(scale))
    include_boundaries=bool(include_boundaries and _has_initial_mask_or_estimate(state))
    if projection=='parallelogram':
        _draw_projected_start_markers(im,state,state.side,scale,include_boundaries,opacity)
    else:
        _draw_square_start_markers(im,state,scale,include_boundaries,opacity)

def _has_direct_initial_mask(state:MapState)->bool:
    """Return whether the source supplied actual initial-mask cells.

    A start coordinate, a runtime claim raster, and the historical canonical
    shape are not sufficient evidence for the native mask.  The reader keeps
    this opt-in until a format-specific decoder supplies the complete cells.
    """
    cells=state.metadata.get('initial_territory_direct_cells')
    if not isinstance(cells,(list,tuple,dict)) or not cells:return False
    return any(_direct_initial_mask_cells(state,i) for i in range(len(state.starts)))

def _source_format(state:MapState)->str:
    return str(state.metadata.get('source_format','')).upper()

def _allows_estimated_initial_mask(state:MapState)->bool:
    """Return whether the known start radius may stand in for missing SAV data.

    MAP/EDM and generated states have no native claim raster, but their start
    coordinates are sufficient to display the validated initial footprint.
    A SAV is deliberately excluded: its claims are runtime data and must not
    be guessed when the decoder did not expose them.
    """
    return _source_format(state) != 'SAV' and bool(state.starts)

def _allows_estimated_start_boundary(state:MapState)->bool:
    """Allow Starts to show the known-radius outline for every decoded start.

    A SAV may not expose its initial claim raster in the current decoder, but
    its decoded start coordinates still justify the established visual
    boundary.  This fallback is deliberately limited to the Starts overlay;
    the Territories view keeps SAV runtime claims authoritative.
    """
    return bool(state.starts)

def _has_initial_mask_or_estimate(state:MapState)->bool:
    return _has_direct_initial_mask(state) or _allows_estimated_start_boundary(state)

def _direct_initial_mask_cells(state:MapState,player_index:int)->set[tuple[int,int]]:
    """Read exact absolute cells supplied by a future format decoder.

    The metadata contract is intentionally strict: a mapping keyed by player
    number (or a sequence parallel to ``state.starts``), containing explicit
    ``(x, y)`` cells in map coordinates.  No shape, radius, count, or start
    coordinate is used to fill missing cells.
    """
    raw=state.metadata.get('initial_territory_direct_cells')
    value=None
    if isinstance(raw,dict):
        value=raw.get(player_index+1,raw.get(str(player_index+1)))
    elif isinstance(raw,(list,tuple)) and player_index<len(raw):
        value=raw[player_index]
    if not isinstance(value,(list,tuple,set,frozenset)):return set()
    out=set()
    for cell in value:
        if isinstance(cell,(list,tuple)) and len(cell)==2:
            x,y=cell
            if isinstance(x,(int,np.integer)) and isinstance(y,(int,np.integer)) and 0<=int(x)<state.side and 0<=int(y)<state.side:
                out.add((int(x),int(y)))
    return out


def _direct_initial_claim_raster(state:MapState)->np.ndarray:
    """Build a raster from the explicit direct-cell metadata only."""
    claims=np.full((state.side,state.side),255,dtype=np.uint8)
    for player_index in range(len(state.starts)):
        cells=_direct_initial_mask_cells(state,player_index)
        if cells:
            ys=np.fromiter((y for _x,y in cells),dtype=np.intp,count=len(cells))
            xs=np.fromiter((x for x,_y in cells),dtype=np.intp,count=len(cells))
            claims[ys,xs]=player_index
    return claims

def _estimated_initial_claim_raster(state:MapState)->np.ndarray:
    """Estimate the initial claim for non-SAV sources from the known radius."""
    claims=np.full((state.side,state.side),255,dtype=np.uint8)
    if not _allows_estimated_initial_mask(state):return claims
    for player_index,start in enumerate(state.starts):
        cells=initial_territory_cells(start,state.side)
        if not cells:continue
        ys=np.fromiter((y for _x,y in cells),dtype=np.intp,count=len(cells))
        xs=np.fromiter((x for x,_y in cells),dtype=np.intp,count=len(cells))
        claims[ys,xs]=player_index
    return claims

def _initial_boundary_cells(state:MapState,player_index:int)->set[tuple[int,int]]:
    direct=_direct_initial_mask_cells(state,player_index)
    if direct:return direct
    if _allows_estimated_start_boundary(state) and player_index<len(state.starts):
        return initial_territory_cells(state.starts[player_index],state.side)
    return set()

def _ordered_initial_boundary(state:MapState,player_index:int,projected:bool)->tuple[tuple[int,int],...]:
    cells=_initial_boundary_cells(state,player_index)
    if not cells:return ()
    boundary=frozenset(
        (x,y) for x,y in cells
        if any(((x+dx)%state.side,(y+dy)%state.side) not in cells for dx,dy in HEX6)
    )
    sx,sy=state.starts[player_index]
    def screen_point(point):
        x,y=point
        dx=((x-int(sx)+state.side//2)%state.side)-state.side//2
        dy=((y-int(sy)+state.side//2)%state.side)-state.side//2
        return (2*dx-dy,2*dy) if projected else (dx,dy)
    return tuple(sorted(boundary,key=lambda p:(math.atan2(screen_point(p)[1],screen_point(p)[0]),screen_point(p)[0],screen_point(p)[1])))

def _ordered_direct_initial_boundary(state:MapState,player_index:int,projected:bool)->tuple[tuple[int,int],...]:
    cells=_direct_initial_mask_cells(state,player_index)
    if not cells:return ()
    boundary=frozenset(
        (x,y) for x,y in cells
        if any(((x+dx)%state.side,(y+dy)%state.side) not in cells for dx,dy in HEX6)
    )
    sx,sy=state.starts[player_index]
    def screen_point(point):
        x,y=point
        dx=((x-int(sx)+state.side//2)%state.side)-state.side//2
        dy=((y-int(sy)+state.side//2)%state.side)-state.side//2
        return (2*dx-dy,2*dy) if projected else (dx,dy)
    return tuple(sorted(boundary,key=lambda p:(math.atan2(screen_point(p)[1],screen_point(p)[0]),screen_point(p)[0],screen_point(p)[1])))

def compose_start_markers(base:Image.Image,state:MapState,projection:str='square',scale:int=1,include_boundaries:bool=False,opacity:int=100)->Image.Image:
    """Return a copy of a marker-free raster with the start layer composed over it."""
    image=base.copy()
    _draw_start_marker_layer(image,state,projection,scale,include_boundaries,opacity)
    return image

def project_parallelogram(im):
    src=im.convert('RGBA');w,h=src.size;px=np.asarray(src);expanded=np.repeat(np.repeat(px,2,axis=0),2,axis=1);canvas=np.zeros((2*h,2*w+(h-1),4),dtype=np.uint8)
    for y in range(h):
        shift=h-1-y;canvas[2*y:2*y+2,shift:shift+2*w]=expanded[2*y:2*y+2]
    return Image.fromarray(canvas,'RGBA')

def render_square_base(state,view='global',overlay_alpha=100,heatmap_resource='trees')->Image.Image:
    """Colorize one map/view into its reusable, marker-free square raster."""
    base=_global_rgb(state);rgb=base.copy() if view in ('global','starts') else _blend(base,_overlay_rgb(state,view,heatmap_resource),overlay_alpha)
    return Image.fromarray(rgb,'RGB')

def compose_rendered_map(base:Image.Image,state,labels=True,view='global',overlay_alpha=100,projection='square',start_markers=False,start_marker_scale=1)->Image.Image:
    """Project and decorate a cached square raster without mutating that base."""
    im=project_parallelogram(base) if projection=='parallelogram' else base.copy()
    draw_start_markers=(labels and view=='starts') or bool(start_markers)
    # Starts use direct cells when decoded, otherwise the known-radius outline.
    # Territories remains conservative for SAVs; batch marker mode remains
    # centre-only.
    draw_start_boundaries=labels and view=='starts' and _has_initial_mask_or_estimate(state)
    marker_opacity=overlay_alpha if draw_start_boundaries else 100
    if draw_start_markers:_draw_start_marker_layer(im,state,projection,start_marker_scale,draw_start_boundaries,marker_opacity)
    return im

def render(state, output=None, scale=1, labels=True, view='global', overlay_alpha=100, projection='square', heatmap_resource='trees', start_markers=False, start_marker_scale=1):
    base=render_square_base(state,view,overlay_alpha,heatmap_resource)
    im=compose_rendered_map(base,state,labels,view,overlay_alpha,projection,start_markers,start_marker_scale)
    if scale!=1:im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
    if output:im.save(output)
    return im
