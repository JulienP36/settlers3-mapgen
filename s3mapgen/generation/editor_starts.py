"""Fresh-map local editor admission, ported from the supplied United editor.

70 iterator positions; exact terrain IDs and Area flags; auxiliary occupation
rebuilt from object dimensions. No levelling test and no MapGen safety halo.
Existing-player separation is evaluated separately, only for placed starts.
"""
from functools import lru_cache
from pathlib import Path
import json
import numpy as np
from .start_safety import EDITOR_START_OFFSETS

@lru_cache(maxsize=1)
def _rules():
    return json.loads((Path(__file__).resolve().parents[2]/'data/editor_start_rules.json').read_text())

def editor_occupation(objects):
    rules = _rules()
    sizes = np.asarray(rules['object_sizes'],dtype=np.int16)[objects]
    occupied = np.zeros(objects.shape,bool)
    side = len(objects)
    known = not np.any((objects != 0) & (sizes > len(rules['counts'])))
    for size, count in enumerate(rules['counts'],1):
        anchors = (objects != 0) & (sizes == size)
        if not anchors.any():
            continue
        for dx,dy in rules['offsets'][:count]:
            x0,x1=max(0,-dx),min(side,side-dx)
            y0,y1=max(0,-dy),min(side,side-dy)
            occupied[y0+dy:y1+dy,x0+dx:x1+dx] |= anchors[y0:y1,x0:x1]
    return occupied, known

def _matching_inside(field):
    # The native iterator advances only after an in-bounds successful check.
    # The first out-of-bounds offset stalls it for the remaining iterations.
    side = len(field)
    result = np.ones(field.shape,bool)
    active = np.ones(field.shape,bool)
    for dx,dy in EDITOR_START_OFFSETS:
        x0,x1=max(0,-dx),min(side,side-dx)
        y0,y1=max(0,-dy),min(side,side-dy)
        inside=np.zeros(field.shape,bool)
        inside[y0:y1,x0:x1]=True
        active &= inside
        shifted=np.ones(field.shape,bool)
        shifted[y0:y1,x0:x1]=field[y0+dy:y1+dy,x0+dx:x1+dx]
        result &= ~active | shifted
    return result

def editor_start_checks(state,nations):
    occupied, known = editor_occupation(state.objects)
    known = known and not state.metadata.get('native_start_context_unavailable',False)
    terrains,clearances=[],[]
    for nation in nations:
        allowed = state.terrain == 16
        if nation == 1:
            allowed |= np.isin(state.terrain,(20,64,65))
        terrains.append(_matching_inside(allowed))
        clearances.append(_matching_inside(allowed & (state.accessibility == 0)
                          & ~occupied & (state.claim == 255)))
    terrain=np.logical_and.reduce(terrains)
    clearance=np.logical_and.reduce(clearances)
    return dict(terrain=terrain,clearance=clearance,valid=clearance,available=known)

def _game_point(state,nation,x,y):
    from .classic_starts import _LEVEL,_OUTER
    if not (15 <= x < state.side-15 and 15 <= y < state.side-15):
        return False
    pattern=_LEVEL[nation]
    for dx,dy in (*pattern,*_OUTER[nation]):
        terrain=int(state.terrain[y+dy,x+dx]) & 240
        allowed = terrain == 16 or (nation == 1 and terrain == 64) or (nation == 2 and terrain == 144)
        if not allowed or int(state.accessibility[y+dy,x+dx]) & 13 or state.claim[y+dy,x+dx] != 255:
            return False
    target=(sum(int(state.height[y+dy,x+dx]) for dx,dy in pattern)+len(pattern)//2)//len(pattern)
    inside=set(pattern)
    for dx,dy in pattern:
        for nx,ny,low,high in ((-1,-1,5,7),(0,-1,5,7),(1,1,7,5),(0,1,7,5)):
            if (dx+nx,dy+ny) in inside:
                continue
            value=int(state.height[y+dy+ny,x+dx+nx])
            if value+low < target or value-high > target:
                return False
    return True

def _editor_point(state,nation,x,y,occupied):
    terrain_ok=clear_ok=True
    for dx,dy in EDITOR_START_OFFSETS:
        xx,yy=x+dx,y+dy
        if not (0 <= xx < state.side and 0 <= yy < state.side):
            break  # Exact native stalled-iterator border behaviour.
        terrain=int(state.terrain[yy,xx])
        allowed=terrain == 16 or (nation == 1 and terrain in (20,64,65))
        terrain_ok &= allowed
        clear_ok &= bool(allowed and state.accessibility[yy,xx] == 0
                         and not occupied[yy,xx] and state.claim[yy,xx] == 255)
    return bool(terrain_ok),bool(clear_ok)

def placed_start_checks(state):
    """Actual Area/nations, with editor pair spacing; no export restriction."""
    from .start_diagnostics import departure_source
    state, _ = departure_source(state, 'current') if 64 <= state.side <= 768 else (state, '')
    # Keep actual start records/nations; diagnostic geography is export-ready,
    # and its analysis copy has already neutralized historical/runtime claims.
    fresh=(64 <= state.side <= 768 and bool(np.all(state.claim == 255))
           and not state.metadata.get('native_start_context_unavailable',False)
           and not state.metadata.get('start_nations_unavailable',False))
    nations=state.metadata.get('classic_start_nations')
    if nations is None:
        selected=state.metadata.get('player_nations')
        indices=state.metadata.get('start_slot_indices',range(len(state.starts)))
        nations=[selected[i] for i in indices] if selected is not None else [255]*len(state.starts)
    occupied,known=editor_occupation(state.objects)
    known=known and not state.metadata.get('native_start_context_unavailable',False)
    rows=[]
    for i,(x,y) in enumerate(state.starts):
        nation=int(nations[i]) if i < len(nations) else 255
        key=nation if nation in (0,1,2,3) else 255
        in_bounds=0 <= x < state.side and 0 <= y < state.side
        game=all(_game_point(state,n,x,y) for n in (range(4) if key == 255 else (key,))) if fresh else None
        terrain_ok,clear_ok = _editor_point(state,0 if key == 255 else key,x,y,occupied) if in_bounds else (False,False)
        local=clear_ok if in_bounds and known else None
        spacing=all((x-xx)**2+(y-yy)**2 >= 2500 for j,(xx,yy) in enumerate(state.starts) if i != j)
        accepted=None if local is None else local and spacing
        reason='unavailable' if local is None else ('terrain' if not terrain_ok else 'occupation' if not local else 'spacing' if not spacing else 'valid')
        status='unknown' if game is None or accepted is None else 'green' if accepted else 'yellow' if game else 'invalid'
        rows.append(dict(player=i+1,x=x,y=y,nation=key,game=game,game_exact=game,
                         relocation_possible=bool(accepted and game is False),editor=accepted,editor_local=local,editor_spacing=spacing,editor_reason=reason,status=status))
    return rows
