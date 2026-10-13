"""Game selection on a fresh map, with explicitly chosen nations and stocks.

Only selection-observable town effects are kept here: claim, height, objects
and PRNG. Actors and construction records belong to the game at MAP load.
The export retains the pre-town Area and writes the selected PlayerInfo.
"""
from __future__ import annotations

import numpy as np
from scipy.signal import fftconvolve

from .generators.legacy.native_content import build_native_pattern_bank
from .generators.legacy.native_terrain import NativeRng16
from .native_start_selection import NativeStartSlot, select_native_starts
from .start_safety import LEVEL_PATTERNS, _centers_matching
from .rules import ValidationResult

# Key 15 of 6AA174 + (57*nation + key)*2400. Ordered native tokens.
_OUTER = (
    ((-2,-3),(-1,-3),(0,-3),(1,-2),(2,-1),(3,0),(3,1),(3,3),
     (3,4),(2,4),(1,3),(0,2),(-1,1),(-2,0),(-2,-1),(4,2),(-2,-2)),
    ((-2,-3),(-1,-3),(0,-3),(1,-2),(2,-1),(3,0),(3,1),(3,3),
     (3,4),(2,4),(1,3),(0,2),(-1,1),(-2,0),(-2,-1),(-2,-2),(4,2)),
    ((-2,-3),(-1,-3),(0,-3),(1,-2),(2,-1),(3,0),(3,1),(3,3),
     (3,4),(2,4),(1,3),(3,2),(-1,1),(-2,0),(-2,-1),(-2,-2),(-1,2)),
    ((-2,-3),(-1,-3),(0,-3),(-2,-2),(1,-2),(-2,-1),(2,-1),
     (-2,0),(3,0),(-1,1),(3,1),(0,2),(4,2),(1,3),(2,3),(3,3),(4,3)),
)
_LEVEL = (LEVEL_PATTERNS[0], LEVEL_PATTERNS[0], LEVEL_PATTERNS[1], LEVEL_PATTERNS[2])
_GROUPS = {
    1: ((1,11,-8,-16),(2,10,-8,-16),(16,0,-8,-16),
        (6,5,8,16),(1,8,14,10),(1,15,-4,10)),
    2: ((2,11,-8,-16),(4,10,-8,-16),(32,0,-8,-16),(10,5,8,16),
        (2,8,14,10),(2,15,-4,10),(4,39,3,6)),
    3: ((3,11,-8,-16),(6,10,-8,-16),(50,0,-8,-16),(12,5,8,16),
        (4,8,14,10),(4,15,-4,10),(6,39,3,6)),
}


def _kernel(offsets):
    radius = int(np.abs(offsets).max())
    kernel = np.zeros((2*radius+1, 2*radius+1), np.float64)
    kernel[radius-offsets[:,1], radius-offsets[:,0]] = 1
    return kernel


def _counts(field, kernel):
    # Integer input/counters; FFT roundoff cannot become a threshold change.
    return np.rint(fftconvolve(field, kernel, mode='same')).astype(np.int32)


def _level_centers(height, pattern):
    side = height.shape[0]
    result = np.zeros(height.shape, bool)
    size = side-30
    def field(dx,dy):
        return height[15+dy:15+dy+size,15+dx:15+dx+size].astype(np.int16)
    target = (sum(field(dx,dy) for dx,dy in pattern)+len(pattern)//2)//len(pattern)
    valid = np.ones((size,size), bool)
    inside = set(pattern)
    # Before this player's first town, every non-template cell has claim !=
    # slot: propagation is locked, including land owned by previous players.
    for dx,dy in pattern:
        for nx,ny,low,high in ((-1,-1,5,7),(0,-1,5,7),(1,1,7,5),(0,1,7,5)):
            if (dx+nx,dy+ny) in inside:
                continue
            neighbour = field(dx+nx,dy+ny)
            valid &= (neighbour+low >= target) & (neighbour-high <= target)
    result[15:side-15,15:side-15] = valid
    return result


class ClassicRuntime:
    def __init__(self, state, nations, goods, seed, mode, slot_types=()):
        if goods not in _GROUPS:
            raise ValueError('Classique : ressources initiales 1, 2 ou 3 requises')
        if not 64 <= state.side <= 768 or not np.all(state.claim == 255):
            raise ValueError('Classique : carte neuve de taille 64..768 requise')
        if len(nations) != state.metadata['players'] or any(n not in (0,1,2,3,255) for n in nations):
            raise ValueError('Classique : définir une nation (0..3) ou Choose (255) pour chaque joueur')
        slot_types = tuple(slot_types or (1,)*len(nations))
        if len(slot_types) != len(nations) or any(t not in (1,2) for t in slot_types):
            raise ValueError('Classique : types de slots natifs 1 ou 2 requis')
        self.side, self.requested_nations = state.side, tuple(nations)
        # Choose is serialized as 255 and resolved later by the game. The
        # selector needs a concrete town profile; use Romans internally and
        # require all four native footprints/levelling profiles for Choose.
        # This extra safety constraint is deliberately identified in metadata.
        self.nations = tuple(0 if n == 255 else n for n in nations)
        self.goods, self.mode = goods, mode
        self.height, self.terrain = state.height.copy(), state.terrain.copy()
        self.objects, self.claim = state.objects.copy(), state.claim.copy()
        self.flags = state.accessibility.copy()
        self.actors = np.zeros(self.height.shape, bool)
        self.rng = NativeRng16(int(seed) & 65535)  # 437050 word +88, then 4FEB40
        self.bank = build_native_pattern_bank()
        self.near = _kernel(self.bank[:3000])
        self.wide = _kernel(self.bank[:9995])
        self.slots = [NativeStartSlot(enabled=slot_types[i] if i < len(nations) else 0,
                      mirror_id=i % (4 if mode == 3 else 2) if mode else 0)
                      for i in range(20)]
        self.attempts = {}
        self._quality_fields()
        self._valid = {}

    def _quality_fields(self):
        obj = self.objects.astype(np.int16)
        grass = _counts((self.terrain & 240) == 16, self.near)
        trees = _counts((obj >= 68) & (obj <= 83), self.near)
        stones = _counts(np.where((obj >= 115) & (obj <= 126), 127-obj, 0), self.near)
        if not hasattr(self, 'minerals'):
            self.minerals = None
        self.grass, self.trees, self.stones = grass, trees, stones
        self.unclaimed = _counts(self.claim == 255, self.near)

    def set_resources(self, resources):
        self.minerals = [_counts((resources & 240) == family, self.wide)
                         for family in (16,32,48,80,64)]

    def valid_centers(self, nation):
        if nation == 255:
            return np.logical_and.reduce([self.valid_centers(n) for n in range(4)])
        family = self.terrain & 240
        allowed = (family == 16)
        if nation == 1:
            allowed |= family == 64
        elif nation == 2:
            allowed |= family == 144
        clear = allowed & (self.claim == 255) & ((self.flags & 13) == 0)
        return (_centers_matching(clear, (*_LEVEL[nation], *_OUTER[nation]))
                & _level_centers(self.height, _LEVEL[nation]))

    def validity(self, slot, x, y):
        if not 0 <= slot < len(self.nations):
            raise ValueError('Groupe miroir natif incomplet')
        if not (0 <= x < self.side and 0 <= y < self.side):
            return False
        nation = self.requested_nations[slot]
        if nation not in self._valid:
            self._valid[nation] = self.valid_centers(nation)
        return bool(self._valid[nation][y,x])

    def quality(self, slot, x, y, attempt):
        if not self.validity(slot,x,y):
            return False
        if attempt >= 100000:
            return True
        g,u,t,s = (int(f[y,x]) for f in (self.grass,self.unclaimed,self.trees,self.stones))
        coal,iron,gold,sulfur,gems = (int(f[y,x]) for f in self.minerals)
        if attempt < 30000:
            return u>=2900 and g>=2000 and 20<=t<=30 and 50<=s<=100 and coal>=40 and iron>=20 and gold>=10 and sulfur>=5 and gems>=5
        if attempt < 60000:
            return u>=2500 and g>=1500 and t>=12 and s>=30 and coal>=30 and iron>=15 and gold>=5
        return u>=1500 and g>=1000 and t>=5 and s>=15 and coal>=20 and iron>=10

    def town(self, slot, x, y):
        nation = self.nations[slot]
        pattern = _LEVEL[nation]
        target = (sum(int(self.height[y+dy,x+dx]) for dx,dy in pattern)+len(pattern)//2)//len(pattern)
        for dx,dy in pattern:
            self.height[y+dy,x+dx] = target
        footprint = (*pattern,*_OUTER[nation])
        for dx,dy in footprint:
            self.flags[y+dy,x+dx] |= 8
        for dx,dy in pattern[:-1]:
            self.objects[y+dy,x+dx] = 0
        dx,dy = pattern[-1]
        self.objects[y+dy,x+dx] = 255  # Native key-15 building anchor
        # 4DBC50 creates a building actor; 506CF0 creates the tower actor.
        # Each 50C9E0 call consumes 503880's draw and its own 4FEB70 draw.
        for _ in range(4):
            self.rng.next()
        # Fresh towns retain each previous owner's live influence. The only
        # claim writes observed by the next selector are unclaimed cells in
        # this key-15 source's first 3500 offsets (519A90 / 51B5D0).
        b = self.bank[:3500]
        xx,yy = b[:,0]+x,b[:,1]+y
        inside = (xx>=1)&(xx<self.side-1)&(yy>=1)&(yy<self.side-1)
        xx,yy = xx[inside],yy[inside]
        free = self.claim[yy,xx] == 255
        self.claim[yy[free],xx[free]] = slot
        # 50CB20 searches ordered offsets; units consume RNG only on actual
        # creation. Word +0 occupancy is separate from building word +2.
        groups = _GROUPS[self.goods]
        if self.slots[slot].enabled == 2:
            groups += ((10,5,8,16),)  # 507466..507487, extra native troops
        for count,kind,dx,dy in groups:
            remaining = count
            for bx,by in self.bank:
                px,py = x+dx+int(bx),y+dy+int(by)
                if not (0<=px<self.side and 0<=py<self.side):
                    continue
                if (self.actors[py,px] or self.terrain[py,px]<16
                        or self.flags[py,px]&15 or self.claim[py,px]!=slot):
                    continue
                self.actors[py,px] = True
                self.rng.next(); self.rng.next()
                remaining -= 1
                if not remaining:
                    break
            if remaining:
                raise RuntimeError('Classique : création des unités natives impossible sur cette carte')
        self.slots[slot].placed = 1
        self.slots[slot].fixed_x, self.slots[slot].fixed_y = x,y
        self._valid.clear()
        self._quality_fields()

    def select(self):
        return select_native_starts(self.side,self.mode,self.slots,self.rng,
            quality=self.quality,create_town=self.town)


def place_classic_starts(state, players, seed, *, nations, goods=2, mirror_mode=0, slot_types=()):
    from .start_diagnostics import capture_departure_source
    capture_departure_source(state, "after_objects")
    runtime = ClassicRuntime(state,nations,goods,seed,mirror_mode,slot_types)
    runtime.set_resources(state.resources)
    outcome = runtime.select()
    state.starts = [(s.fixed_x,s.fixed_y) for s in runtime.slots if s.placed]
    state.metadata.update(start_algorithm_requested='classic', start_algorithm_effective='classic',
        classic_start_nations=[nations[i] for i,s in enumerate(runtime.slots) if s.placed], classic_start_goods=goods,
        classic_requested_nations=list(nations),
        classic_free_choice_slots=[i for i,n in enumerate(nations) if n == 255],
        classic_runtime_nations=list(runtime.nations),
        classic_free_choice_policy="all_four_native_profiles" if 255 in nations else None,
        classic_start_slot_types=list(slot_types or (1,)*players),
        classic_start_rng_final=[runtime.rng.a,runtime.rng.b,runtime.rng.c],
        classic_disabled_slots=list(outcome.disabled_slots), starts_placed_early=False,
        starts_status='native_classic_selection', start_placement_deferred=False,
        starts_placed_provisionally=False,classic_mapgen_start_bonuses=False)
    return np.zeros(state.height.shape, bool)


def validate_classic_starts(state):
    """Check the exported pre-town Area, using each chosen nation's rules.

    The editor's 70-cell footprint and Euclidean separation are not native
    game conditions. They must not silently alter this selection afterwards.
    """
    nations = state.metadata['classic_start_nations']
    runtime = ClassicRuntime(state,state.metadata['classic_requested_nations'],
                             state.metadata['classic_start_goods'],0,0)
    bad = []
    masks = {nation: runtime.valid_centers(nation) for nation in set(nations)}
    for i,((x,y),nation) in enumerate(zip(state.starts,nations,strict=True)):
        if not (0<=x<state.side and 0<=y<state.side and masks[nation][y,x]):
            bad.append(i+1)
    passed = not bad
    policy = ('native_game_with_free_choice_guards' if 255 in nations
              else 'native_game_chosen_nations')
    state.metadata['start_safety'] = dict(policy=policy,
        native_solver=True,native_levelling_checked=True,final_passed=passed)
    if bad:
        raise RuntimeError(f'Départs Classiques devenus invalides : {bad}')
    return [ValidationResult('CLASSIC_START_VALIDITY',passed,'Empreintes et nivellement natifs vérifiés')]
