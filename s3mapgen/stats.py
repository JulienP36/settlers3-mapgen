from __future__ import annotations
from collections import Counter
import numpy as np
from .constants import *

def summarize(state):
    T,O,R,C=state.terrain,state.objects,state.resources,state.claim
    n=state.side*state.side; water=np.isin(T,WATER_IDS);land=~water
    fish=water&((R&0xF0)==0)&((R&15)>0)
    ore={name:int(np.count_nonzero((R&0xF0)==fam)) for name,fam in [('Coal',0x10),('Iron',0x20),('Gold',0x30),('Gems',0x40),('Sulfur',0x50)]}
    claims=C[C!=255]
    claim_counts=Counter(map(int,claims.tolist())) if claims.size else {}
    return {
        'side':state.side,'cells':n,'water_cells':int(water.sum()),'water_pct':round(100*water.mean(),3),'land_cells':int(land.sum()),
        'mountain_cells':int(np.isin(T,[17,33,32,35,129,128]).sum()),'desert_cells':int(np.isin(T,[20,65,64]).sum()),'swamp_cells':int(np.isin(T,[21,81,80]).sum()),'river_cells':int(np.isin(T,[96,97,98,99]).sum()),
        'fish_cells':int(fish.sum()),'adult_trees':int(np.isin(O,[68,69,70,71,72]).sum()),'small_tree84':int((O==84).sum()),'building_stones':int(((O>=115)&(O<=126)).sum()),
        'ore_cells':ore,'starts':len(state.starts),'claims':dict(claim_counts)
    }

def format_stats(state):
    s=summarize(state);o=s['ore_cells']
    lines=[f"Carte: {s['side']}×{s['side']}  ({s['cells']:,} cases)",f"Terre: {s['land_cells']:,} | Eau: {s['water_cells']:,} ({s['water_pct']}%)",f"Montagne: {s['mountain_cells']:,} | Désert: {s['desert_cells']:,} | Marais: {s['swamp_cells']:,} | Rivière: {s['river_cells']:,}",f"Poisson: {s['fish_cells']:,} cases",f"Minerais: Coal {o['Coal']:,} | Iron {o['Iron']:,} | Gold {o['Gold']:,} | Gems {o['Gems']:,} | Sulfur {o['Sulfur']:,}",f"Arbres adultes: {s['adult_trees']:,} | SmallTree84: {s['small_tree84']:,} | Building Stones: {s['building_stones']:,}",f"Starts: {s['starts']}"]
    if s['claims']: lines.append('Territoires: '+', '.join(f'P{k+1}={v:,}' for k,v in sorted(s['claims'].items())))
    return '\n'.join(lines)
