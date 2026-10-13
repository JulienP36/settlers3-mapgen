"""Shared departure safety for provisional solvers; not the native game solver.

Editor offsets are transcribed from 0x41F3B0 (S3Editor.exe).
Includes native levelling feasibility restricted to unclaimed new-map domains.
This is not the full Classic selection/town runtime.
"""
from __future__ import annotations

import numpy as np
from ..map_data.constants import GRASS, HEX6, START_FOOTPRINT
from ..map_data.hexgrid import dilate
from .rules import ValidationResult

EDITOR_START_OFFSETS = ((0,0),(-1,0),(-1,-1),(0,-1),(1,0),(1,1),(0,1),(-1,1),(-2,0),(-2,-1),(-2,-2),(-1,-2),(0,-2),(1,-1),(2,0),(2,1),(2,2),(1,2),(0,2),(-1,2),(-2,1),(-3,0),(-3,-1),(-3,-2),(-3,-3),(-2,-3),(-1,-3),(0,-3),(1,-2),(2,-1),(3,0),(3,1),(3,2),(3,3),(2,3),(1,3),(0,3),(-1,3),(-2,2),(-3,1),(-4,0),(-4,-1),(-4,-2),(-4,-3),(-4,-4),(-3,-4),(-2,-4),(-1,-4),(0,-4),(1,-3),(2,-2),(3,-1),(4,0),(4,1),(4,2),(4,3),(4,4),(3,4),(2,4),(1,4),(0,4),(-1,4),(-2,3),(-3,2),(-4,1),(-5,0),(-5,-1),(-5,-2),(-5,-3),(-5,-4))
START_TERRAIN_OFFSETS = tuple(dict.fromkeys((*EDITOR_START_OFFSETS, *START_FOOTPRINT)))
EDITOR_MIN_SPACING = 50


def _centers_matching(field, offsets):
    """All offsets must be in bounds and true; never wrap at map edges."""
    side = field.shape[0]
    result = np.ones(field.shape, dtype=bool)
    for dx, dy in offsets:
        shifted = np.zeros(field.shape, dtype=bool)
        x0, x1 = max(0, -dx), min(side, side - dx)
        y0, y1 = max(0, -dy), min(side, side - dy)
        shifted[y0:y1, x0:x1] = field[y0+dy:y1+dy, x0+dx:x1+dx]
        result &= shifted
    return result


def candidate_centers(state, *, include_levelling=True):
    """Conservative normal-profile validity on actual terrain and occupation."""
    occupied = state.objects != 0
    stones = (state.objects >= 115) & (state.objects <= 127)
    # Construction stones reserve the complete anchor + six neighbours.
    occupied = occupied | dilate(stones, 1)
    # Existing object collision policy: two HEX6 cells around actual writes.
    occupied = dilate(occupied, 2)
    clear = (state.terrain == GRASS) & ~occupied
    access = getattr(state, "accessibility", None)
    if access is not None:
        clear &= access == 0
    claim = getattr(state, "claim", None)
    if claim is not None:
        clear &= claim == 255
    centers = _centers_matching(clear, START_TERRAIN_OFFSETS)
    if include_levelling:
        centers &= unclaimed_level_centers(state.height, state.claim)
    return centers


def start_terrain_reservation(state):
    mask = np.zeros((state.side, state.side), dtype=bool)
    for x, y in state.starts:
        for dx, dy in START_TERRAIN_OFFSETS:
            xx, yy = x + dx, y + dy
            if 0 <= xx < state.side and 0 <= yy < state.side:
                mask[yy, xx] = True
    return mask


def start_object_reservation(state):
    return dilate(start_terrain_reservation(state), 2)


def separated(x, y, starts):
    return all((x-sx)**2 + (y-sy)**2 >= EDITOR_MIN_SPACING**2 for sx, sy in starts)


def validate_start_safety(state):
    valid = candidate_centers(state)
    bad = [i+1 for i, (x,y) in enumerate(state.starts)
           if not (0 <= x < state.side and 0 <= y < state.side and valid[y,x])]
    spacing = all(separated(x,y,state.starts[:i]) for i,(x,y) in enumerate(state.starts))
    return [
        ValidationResult("START_FINAL_CLEARANCE", not bad,
                         "Départs dégagés sur le terrain final" if not bad
                         else f"Terrain, occupation ou relief incompatible pour les joueurs {bad}"),
        ValidationResult("START_EDITOR_SPACING", spacing,
                         "Séparation des départs ≥ 50 coordonnées carte" if spacing
                         else "Départs trop proches pour le contrôle de l’éditeur"),
    ]


def require_start_safety(state):
    if state.metadata.get("start_algorithm_effective") == "classic":
        from .classic_starts import validate_classic_starts
        return validate_classic_starts(state)
    checks = validate_start_safety(state)
    errors = [v.message for v in checks if not v.passed]
    state.metadata["start_safety"] = {
        "policy": "editor_conservative_and_unclaimed_native_level",
        "native_solver": False,
        "native_levelling_checked": True,
        "final_passed": not errors,
    }
    if errors:
        raise RuntimeError("Départ invalide après génération : " + "; ".join(errors))
    if state.metadata.get("start_disabled_slots"):
        checks.append(ValidationResult("START_PLAYER_COUNT", False,
            f"Carte conservée : {len(state.starts)} départs valides pour {state.metadata.get('players', len(state.starts)+len(state.metadata['start_disabled_slots']))} joueurs ; export incomplet bloqué"))
    return checks



LEVEL_OFFSETS = ((-1,-2),(0,-2),(-1,-1),(0,-1),(1,-1),(-1,0),
                 (0,0),(1,0),(2,0),(0,1),(1,1),(2,1),(1,2),(2,2))
LEVEL_PATTERNS = (LEVEL_OFFSETS+((2,3),(3,2)),
                  LEVEL_OFFSETS+((2,3),(0,2)),
                  LEVEL_OFFSETS+((3,2),))

def unclaimed_level_centers(height,claim):
    """4DA440 feasibility on a completely unclaimed 31x31 domain.

    All non-template cells are locked by claim != slot (slot 0..19).
    Only the initial template height writes can occur; propagation cannot
    change a locked neighbour. This is not the general runtime leveller.
    All three distinct patterns (profiles 0/1, 2, 3) must be feasible.
    """
    side=height.shape[0]
    result=np.zeros(height.shape,dtype=bool)
    if side<31:return result
    size=side-30
    def field(dx,dy):
        return height[15+dy:15+dy+size,15+dx:15+dx+size].astype(np.int16)
    feasible=np.ones((size,size),dtype=bool)
    for pattern in LEVEL_PATTERNS:
        target=(sum(field(dx,dy) for dx,dy in pattern)+len(pattern)//2)//len(pattern)
        inside=set(pattern)
        for dx,dy in pattern:
            for nx,ny,low,high in ((-1,-1,5,7),(0,-1,5,7),(1,1,7,5),(0,1,7,5)):
                neighbour=(dx+nx,dy+ny)
                if neighbour in inside:continue
                value=field(*neighbour)
                feasible &= (value+low>=target)&(value-high<=target)
    result[15:side-15,15:side-15]=feasible
    if not np.all(claim==255):
        from scipy.ndimage import minimum_filter
        result &= minimum_filter(claim==255,size=31,mode='constant',cval=0)
    return result
