"""Resource-aware placement on completed global content, without island quotas.

Quality is a preference, never a new condition of departure admissibility.
Local HEX6 flood fills exclude sea and blocked cells; no Voronoi/team simulation.
"""
from __future__ import annotations
import numpy as np
from scipy.ndimage import binary_propagation, label
from ..map_data.constants import MOUNTAIN_FAMILY_IDS, WATER_IDS, HEX_STRUCTURE
from .start_safety import candidate_centers, start_terrain_reservation, EDITOR_MIN_SPACING

METRIC_NAMES = ('coal', 'iron', 'gold', 'gems', 'sulfur')
QUALITY_RADIUS = 75


def local_metrics(state, point, *, radius=QUALITY_RADIUS, fields=None):
    """Count nearby buildable land and deposits reachable on land inside radius.

    A blocked mountain component counts when its frontier touches reachable
    land; only its cells inside the local observation radius count. This is
    an evaluation heuristic, not a game expansion/mining simulation.
    """
    if fields is None:
        fields = _fields(state)
    land, buildable, mountains, deposits = fields
    x, y = point
    x0, x1 = max(0,x-radius), min(state.side,x+radius+1)
    y0, y1 = max(0,y-radius), min(state.side,y+radius+1)
    yy, xx = np.mgrid[y0:y1,x0:x1]
    dx, dy = xx-x, yy-y
    disk = np.maximum(np.maximum(abs(dx),abs(dy)),abs(dx-dy)) <= radius
    seed = np.zeros(disk.shape, bool); seed[y-y0,x-x0] = True
    reached = binary_propagation(seed, structure=HEX_STRUCTURE,
                                 mask=land[y0:y1,x0:x1] & disk)
    from scipy.ndimage import binary_dilation
    frontier = binary_dilation(reached, structure=HEX_STRUCTURE) & disk
    local_mountains = mountains[y0:y1,x0:x1]
    ids = np.unique(local_mountains[frontier]); ids = ids[ids != 0]
    mineable = np.isin(local_mountains,ids) & disk
    resources = deposits[y0:y1,x0:x1]
    return np.array([int((resources & 15)[mineable & ((resources & 240)==family)].sum())
                     for family in (16,32,48,64,80)], float)


def _fields(state):
    land = ~np.isin(state.terrain, WATER_IDS) & (state.accessibility == 0)
    buildable = None  # Land is used for reachability/spacing, never as a richness score.
    mountains,_ = label(np.isin(state.terrain,MOUNTAIN_FAMILY_IDS),structure=HEX_STRUCTURE)
    return land, buildable, mountains, state.resources


def arrangement_score(values, scale):
    quality = np.minimum(values/scale,2.0)
    means = quality.mean(axis=0)
    active = means > 0
    disparity = float((quality[:,active].std(axis=0)/means[active]).mean()) if active.any() else 0.0
    strength = quality.mean(axis=1)
    return float(strength.min()+.25*strength.mean()-.5*disparity)


def spacing_penalty(squared_distances, preferred):
    """Soft proximity preference; do not discard valid, tightly packed starts."""
    if len(squared_distances)<2:
        return 0.0
    distances=np.asarray(squared_distances, dtype=float).copy()
    np.fill_diagonal(distances, np.inf)
    nearest=np.sqrt(distances.min(axis=1))
    deficits=np.maximum(0.0, 1.0-nearest/preferred)
    # No reward beyond the target: preserve good resource arrangements there.
    return .75*(.65*float(deficits.max())+.35*float(deficits.mean()))


def _farthest_combination(points, players, first_choices, minimum):
    """Try the complete valid pool, retaining the best partial valid result."""
    longest=[]
    for first in first_choices:
        chosen=[int(first)]
        distances=((points-points[first]).astype(float)**2).sum(axis=1)
        while len(chosen)<players and distances.max()>=minimum**2:
            i=int(distances.argmax());chosen.append(i)
            distances=np.minimum(distances,((points-points[i]).astype(float)**2).sum(axis=1))
        if len(chosen)>len(longest):longest=chosen
        if len(chosen)==players:break
    return longest


def _refine_resources(selected, values, candidates, metrics, scale, minimum, preferred):
    """Improve a full-pool spacing solution without bringing players closer."""
    for _ in range(2):
        changed=False
        for slot in range(len(selected)):
            others=np.delete(selected,slot,axis=0)
            squared=((candidates[:,None,:]-others[None,:,:]).astype(float)**2).sum(axis=2)
            allowed=np.flatnonzero((squared>=minimum**2).all(axis=1))
            def score(positions, measures):
                d=((positions[:,None,:]-positions[None,:,:]).astype(float)**2).sum(axis=2)
                return arrangement_score(measures,scale)-spacing_penalty(d,preferred)
            current=score(selected,values)
            winner=None
            for i in allowed:
                positions=selected.copy();positions[slot]=candidates[i]
                measures=values.copy();measures[slot]=metrics[i]
                quality=score(positions,measures)
                if quality>current+1e-12:current,winner=quality,int(i)
            if winner is not None:
                selected[slot]=candidates[winner];values[slot]=metrics[winner];changed=True
        if not changed:break
    return selected,values


def place_fair_starts(state, players, rng):
    from .start_diagnostics import capture_departure_source
    capture_departure_source(state, "before_objects")
    valid = candidate_centers(state)
    points = np.argwhere(valid)[:,::-1].astype(np.int32)
    if not len(points):
        state.starts = []
        state.metadata.update(start_algorithm_requested='fair', start_algorithm_effective='fair',
            start_disabled_slots=list(range(players)), starts_placed_early=False,
            start_placement_deferred=True, starts_status='no_valid_start_map_retained')
        state.metadata['fair_starts'] = {'valid_candidates':0, 'scored_candidates':0,
            'island_quotas':False, 'evaluation_before_start_bonuses':True, 'evaluation_before_objects':True, 'players':[]}
        return start_terrain_reservation(state)
    # Retain the entire admissible pool for the valid-spacing fallback. The
    # expensive resource scoring uses a geographically spread sample only.
    shuffled = rng.permutation(len(points))
    cells = points[shuffled]//12
    _, unique = np.unique(cells,axis=0,return_index=True)
    sample = shuffled[np.sort(unique)]
    if len(sample)>256:
        sample = sample[rng.choice(len(sample),256,replace=False)]
    fields = _fields(state)
    preferred_spacing=float(np.clip(.65*np.sqrt(np.count_nonzero(fields[0])/max(1,players)),
                                     EDITOR_MIN_SPACING, 2*QUALITY_RADIUS))
    metrics = np.asarray([local_metrics(state,tuple(points[i]),fields=fields) for i in sample])
    scale = np.maximum(np.percentile(metrics,75,axis=0),1.0)
    distance = ((points[sample,None,:]-points[None,sample,:]).astype(float)**2).sum(axis=2)
    attempts=min(64,len(sample))
    first_choices=rng.permutation(len(sample))[:attempts]
    levels=list(dict.fromkeys(max(EDITOR_MIN_SPACING,preferred_spacing*factor)
                              for factor in (1.0,.85,.70,0.0)))
    spacing_trials=[]
    selected=values=None
    fallback=False
    accepted_spacing=EDITOR_MIN_SPACING
    for minimum in levels:
        best,best_score=None,-np.inf
        for first in first_choices:
            chosen=[int(first)]
            while len(chosen)<players:
                allowed=np.flatnonzero((distance[:,chosen]>=minimum**2).all(axis=1))
                if not len(allowed):break
                scores=np.array([arrangement_score(metrics[chosen+[int(i)]],scale)
                    - spacing_penalty(distance[np.ix_(chosen+[int(i)],chosen+[int(i)])],preferred_spacing)
                    for i in allowed])
                scores+=.025*np.minimum(distance[allowed][:,chosen].min(axis=1)**.5/100,2)
                chosen.append(int(allowed[np.argmax(scores)]))
            if len(chosen)==players:
                score=arrangement_score(metrics[chosen],scale)-spacing_penalty(distance[np.ix_(chosen,chosen)],preferred_spacing)
                if score>best_score:best,best_score=chosen,score
        trial={'minimum_coordinates':round(float(minimum),3),'scored_solution':best is not None}
        spacing_trials.append(trial)
        if best is not None:
            selected=points[sample[best]].copy();values=metrics[best].copy()
            accepted_spacing=minimum
            break
        # Before relaxing spacing, try all admissible centres, not just the
        # 256 centres scored for resources. This remains a bounded heuristic.
        longest=_farthest_combination(points,players,shuffled[:min(64,len(points))],minimum)
        trial['full_pool_solution']=len(longest)==players
        if len(longest)==players:
            selected=points[longest].copy()
            values=np.asarray([local_metrics(state,tuple(p),fields=fields) for p in selected])
            selected,values=_refine_resources(selected,values,points[sample],metrics,scale,minimum,preferred_spacing)
            accepted_spacing=minimum;fallback=True
            break
    if selected is None:
        # The last level is the original mandatory clearance. Preserve its
        # longest partial valid layout instead of rejecting the whole map.
        selected=points[longest].copy()
        values=np.asarray([local_metrics(state,tuple(p),fields=fields) for p in selected])
        fallback=True
    # Player assignment is seeded, independent of score ordering/civilization.
    order=rng.permutation(len(selected)); selected=selected[order]; values=values[order]
    achieved_spacing=None
    if len(selected)>1:
        squared=((selected[:,None,:]-selected[None,:,:]).astype(float)**2).sum(axis=2)
        np.fill_diagonal(squared,np.inf)
        achieved_spacing=round(float(np.sqrt(squared.min())),3)
    state.starts=[tuple(map(int,p)) for p in selected]
    state.metadata.update(start_algorithm_requested='fair',start_algorithm_effective='fair',
                          starts_placed_early=False,start_placement_deferred=True,
                          starts_status='resource_balanced_before_objects')
    state.metadata['start_disabled_slots'] = list(range(len(selected), players))
    state.metadata['fair_starts']={'radius_hex':QUALITY_RADIUS,'valid_candidates':len(points),
        'scored_candidates':len(sample),'arrangement_attempts':attempts*len(spacing_trials),'valid_spacing_fallback':fallback,
        'preferred_spacing_coordinates':round(preferred_spacing,3),
        'minimum_spacing_coordinates':achieved_spacing,
        'accepted_spacing_coordinates':round(float(accepted_spacing),3),
        'preferred_spacing_relaxed':accepted_spacing<preferred_spacing,
        'spacing_search':spacing_trials,
        'island_quotas':False,'evaluation_before_start_bonuses':True, 'evaluation_before_objects':True,
        'players':[dict(player=i+1,x=x,y=y,**dict(zip(METRIC_NAMES,map(int,v))))
                   for i,((x,y),v) in enumerate(zip(state.starts,values))]}
    return start_terrain_reservation(state)
