from __future__ import annotations

from dataclasses import dataclass, asdict
from collections import Counter
from typing import Any
import json
import csv
import io
import numpy as np

from .constants import (
    WATER_IDS, GRASS, GRASS_DESERT_TRANS, GRASS_SWAMP_TRANS, ROCKY,
    ROCK_TRANS_1, ROCK_TRANS_2, ROCK_SNOW_TRANS, SHORE, DESERT,
    DESERT_TRANS, SWAMP, SWAMP_TRANS, RIVER_IDS, SNOW, SNOW_TRANS,
    MOUNTAIN_IDS, DESERT_IDS, SWAMP_IDS,
)
from .hexgrid import component_labels, hex_distance, neighbor_count


MINERALS = {
    'coal': (0x10, 'Charbon', 'Coal'),
    'iron': (0x20, 'Fer', 'Iron'),
    'gold': (0x30, 'Or', 'Gold'),
    'gems': (0x40, 'Gemmes', 'Gemstones'),
    'sulfur': (0x50, 'Soufre', 'Sulfur'),
}

ADULT_TREE_IDS = tuple(range(68, 78)) + (80, 81)
TREE_FAMILIES = {
    'birch': ((68, 69), 'Bouleaux', 'Birch'),
    'elm': ((70, 71), 'Ormes', 'Elm'),
    'oak': ((72,), 'Chênes', 'Oak'),
    # The validated profiles classify 73–77 and 80–81 as adult trees.
    # Their exact visual species names are not all locked yet, so Stats keeps
    # the correct semantic family without inventing species labels.
    'other_adult': ((73, 74, 75, 76, 77, 80, 81), 'Autres arbres adultes', 'Other adult trees'),
    'palm': ((78, 79), 'Palmiers', 'Palm'),
}
SAPLING_IDS = (84,)
MUD_IDS = (23, 144, 145)
MOUNTAIN_ANALYSIS_IDS = tuple(sorted(set(MOUNTAIN_IDS + (34,))))

LOCAL_RADII = (10, 20, 30, 40, 50, 100)
DRY_GRASS = 24


def _hex_distance_grid(side: int, x0: int, y0: int) -> np.ndarray:
    """Vectorized distance for the project HEX6 coordinate system."""
    yy, xx = np.indices((side, side), dtype=np.int32)
    dx = xx - int(x0)
    dy = yy - int(y0)
    same_sign = (dx * dy) >= 0
    return np.where(same_sign, np.maximum(np.abs(dx), np.abs(dy)), np.abs(dx) + np.abs(dy)).astype(np.int16)


def _component_details(mask: np.ndarray) -> list[dict[str, Any]]:
    labels, n = component_labels(mask)
    if not n:
        return []
    neigh = neighbor_count(mask)
    flat_labels = labels.ravel()
    sizes = np.bincount(flat_labels, minlength=n + 1)
    edge_weight = np.zeros(mask.shape, dtype=np.int16)
    edge_weight[mask] = 6 - neigh[mask]
    perimeters = np.bincount(flat_labels, weights=edge_weight.ravel(), minlength=n + 1)
    slices = __import__('scipy').ndimage.find_objects(labels)
    details: list[dict[str, Any]] = []
    for cid, sl in enumerate(slices, start=1):
        size = int(sizes[cid])
        if not size or sl is None:
            continue
        sub = labels[sl] == cid
        ly, lx = np.where(sub)
        yoff, xoff = sl[0].start, sl[1].start
        xs = lx.astype(np.float64) + xoff
        ys = ly.astype(np.float64) + yoff
        perimeter = int(round(float(perimeters[cid])))
        if size >= 2:
            coords = np.column_stack((xs, ys))
            cov = np.cov(coords, rowvar=False)
            vals = np.linalg.eigvalsh(cov)
            elongation = float(np.sqrt(max(vals[-1], 0.0) / max(vals[0], 1e-9))) if vals.size == 2 else 1.0
        else:
            elongation = 1.0
        compactness = float(min(1.0, (12.0 * size) / max(1.0, float(perimeter * perimeter))))
        details.append({
            'id': cid, 'cells': size, 'perimeter_hex_edges': perimeter,
            'bbox': [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
            'centroid': [round(float(xs.mean()), 3), round(float(ys.mean()), 3)],
            'compactness': round(compactness, 6), 'elongation': round(elongation, 4),
        })
    details.sort(key=lambda r: (-r['cells'], r['id']))
    return details


def _component_summary(details: list[dict[str, Any]]) -> dict[str, Any]:
    sizes = np.asarray([d['cells'] for d in details], dtype=np.int32)
    perimeters = np.asarray([d['perimeter_hex_edges'] for d in details], dtype=np.int32)
    elongations = np.asarray([d['elongation'] for d in details], dtype=np.float64)
    return {
        'count': len(details),
        'size_distribution': _percentiles(sizes),
        'perimeter_distribution': _percentiles(perimeters),
        'elongation_distribution': _percentiles(elongations),
        'largest': details[0] if details else None,
    }


def _local_player_stats(state, terrain: np.ndarray, objects: np.ndarray, resources: np.ndarray) -> list[dict[str, Any]]:
    side = int(state.side)
    max_radius = max(LOCAL_RADII)
    players=[]
    for i,(x,y) in enumerate(state.starts):
        x=int(x); y=int(y)
        x0=max(0,x-max_radius); x1=min(side,x+max_radius+1)
        y0=max(0,y-max_radius); y1=min(side,y+max_radius+1)
        t=terrain[y0:y1,x0:x1]; o=objects[y0:y1,x0:x1]; r=resources[y0:y1,x0:x1]
        yy,xx=np.indices(t.shape,dtype=np.int16)
        dx=xx + x0 - x; dy=yy + y0 - y
        dist=np.where((dx*dy)>=0,np.maximum(np.abs(dx),np.abs(dy)),np.abs(dx)+np.abs(dy)).astype(np.int16)
        mountain=np.isin(t,MOUNTAIN_ANALYSIS_IDS); desert=np.isin(t,DESERT_IDS); swamp=np.isin(t,SWAMP_IDS); water=np.isin(t,WATER_IDS)
        adult=np.isin(o,ADULT_TREE_IDS) | np.isin(o,TREE_FAMILIES['palm'][0]); saplings=np.isin(o,SAPLING_IDS)
        stone_anchor=(o>=115)&(o<=127); stone_units=np.where(stone_anchor,np.maximum(0,127-o.astype(np.int16)),0)
        fish=water & ((r&0xF0)==0) & ((r&0x0F)>0); fish_qty=np.where(fish,r&0x0F,0)
        # Local mining availability is a gameplay-oriented metric: ore hidden under
        # the Snow family is intentionally excluded here. Global Stats still retain
        # the full open/snow-covered split.
        snow_family=np.isin(t,(ROCK_SNOW_TRANS,SNOW_TRANS,SNOW))
        mineral_masks={k:(((r&0xF0)==fam) & ~snow_family) for k,(fam,_fr,_en) in MINERALS.items()}; mineral_qty=(r&0x0F).astype(np.int16)
        radii={}
        for radius in LOCAL_RADII:
            m=dist<=radius
            metrics={
                'cells':int(m.sum()), 'adult_trees':int((adult&m).sum()), 'saplings':int((saplings&m).sum()),
                'building_stone_anchors':int((stone_anchor&m).sum()), 'building_stone_stock':int(stone_units[m].sum()),
                'fish_cells':int((fish&m).sum()), 'fish_stock':int(fish_qty[m].sum()),
                'mountain_cells':int((mountain&m).sum()), 'desert_cells':int((desert&m).sum()),
                'swamp_cells':int((swamp&m).sum()), 'water_cells':int((water&m).sum()), 'minerals':{},
            }
            for key,mm in mineral_masks.items():
                om=mm&m; metrics['minerals'][key]={'cells':int(om.sum()),'stock':int(mineral_qty[om].sum())}
            radii[str(radius)]=metrics
        players.append({'player':i+1,'x':x,'y':y,'radii':radii})
    return players


TERRAIN_FAMILIES = (
    ('water', WATER_IDS, 'Eau', 'Water'),
    ('grass', (GRASS, DRY_GRASS), 'Herbe', 'Grass'),
    ('desert', DESERT_IDS, 'Désert', 'Desert'),
    ('mountain', MOUNTAIN_ANALYSIS_IDS, 'Montagne', 'Mountain'),
    ('snow', (ROCK_SNOW_TRANS, SNOW_TRANS, SNOW), 'Neige', 'Snow'),
    ('swamp', SWAMP_IDS, 'Marais', 'Swamp'),
    ('mud', MUD_IDS, 'Boue', 'Mud'),
    ('shore', (SHORE,), 'Rivage', 'Shore'),
    ('river', RIVER_IDS, 'Rivière', 'River'),
    ('path_runtime', (28,), 'Chemins runtime', 'Runtime paths'),
    ('agriculture_runtime', (22,), 'Agriculture runtime', 'Runtime agriculture'),
)

TERRAIN_NAMES = {
    16: ('Herbe', 'Grass'), 17: ('Transition roche 1', 'Rock transition 1'),
    20: ('Transition herbe/désert', 'Grass/desert transition'),
    21: ('Transition herbe/marais', 'Grass/swamp transition'),
    22: ('Agriculture runtime', 'Runtime agriculture'), 23: ('Boue', 'Mud'), 24: ('Herbe sèche', 'Dry grass'),
    28: ('Chemin runtime', 'Runtime path'), 32: ('Roche', 'Rocky'),
    33: ('Transition roche 2', 'Rock transition 2'), 34: ('Détail roche', 'Rocky detail'),
    35: ('Transition roche/neige', 'Rock/snow transition'), 48: ('Rivage', 'Shore'),
    64: ('Désert', 'Desert'), 65: ('Transition désert', 'Desert transition'),
    80: ('Marais', 'Swamp'), 81: ('Transition marais', 'Swamp transition'),
    96: ('Rivière 1', 'River 1'), 97: ('Rivière 2', 'River 2'),
    98: ('Rivière 3', 'River 3'), 99: ('Rivière 4', 'River 4'),
    128: ('Neige', 'Snow'), 129: ('Transition neige', 'Snow transition'),
    144: ('Boue / transition 144', 'Mud / transition 144'),
    145: ('Boue / transition 145', 'Mud / transition 145'),
}
for i in WATER_IDS:
    TERRAIN_NAMES.setdefault(i, (f'Eau {i+1}', f'Water {i+1}'))

OBJECT_NAMES = {
    68: ('Bouleau 1', 'Birch 1'), 69: ('Bouleau 2', 'Birch 2'),
    70: ('Orme 1', 'Elm 1'), 71: ('Orme 2', 'Elm 2'), 72: ('Chêne', 'Oak'),
    78: ('Palmier 1', 'Palm 1'), 79: ('Palmier 2', 'Palm 2'),
    84: ("Pousse d’arbre", 'Tree sapling'),
}
for _oid in (73, 74, 75, 76, 77, 80, 81):
    OBJECT_NAMES.setdefault(_oid, (f'Arbre adulte {_oid}', f'Adult tree {_oid}'))

for i in range(85, 94): OBJECT_NAMES[i] = (f'Blé {i-84}', f'Wheat {i-84}')
for i in range(94, 103): OBJECT_NAMES[i] = (f'Vigne {i-93}', f'Vine {i-93}')
for i in range(103, 111): OBJECT_NAMES[i] = (f'Riz {i-102}', f'Rice {i-102}')
for i in range(111, 115): OBJECT_NAMES[i] = (f'Récif {i-110}', f'Reef {i-110}')
for i in range(115, 128): OBJECT_NAMES[i] = (f'Pierre de construction {i-114}', f'Building Stone {i-114}')


def _pct(part: int | float, total: int | float) -> float:
    return round((100.0 * float(part) / float(total)), 4) if total else 0.0


def _percentiles(values: np.ndarray) -> dict[str, float]:
    if values.size == 0:
        return {k: 0.0 for k in ('min','p10','p25','median','mean','p75','p90','p95','p99','max')}
    a = values.astype(np.float64, copy=False)
    ps = np.percentile(a, [10,25,50,75,90,95,99])
    return {
        'min': float(a.min()), 'p10': float(ps[0]), 'p25': float(ps[1]),
        'median': float(ps[2]), 'mean': float(a.mean()), 'p75': float(ps[3]),
        'p90': float(ps[4]), 'p95': float(ps[5]), 'p99': float(ps[6]),
        'max': float(a.max()),
    }


def _component_sizes(mask: np.ndarray) -> list[int]:
    labels, n = component_labels(mask)
    if not n:
        return []
    counts = np.bincount(labels.ravel())[1:]
    return [int(x) for x in counts.tolist()]


def _edge_component_ids(labels: np.ndarray) -> set[int]:
    vals = np.concatenate((labels[0,:], labels[-1,:], labels[:,0], labels[:,-1]))
    return {int(v) for v in np.unique(vals) if int(v) != 0}


def _object_family_counts(objects: np.ndarray) -> dict[str, int]:
    out: dict[str, int] = {}
    for key, (ids, _fr, _en) in TREE_FAMILIES.items():
        out[key] = int(np.isin(objects, ids).sum())
    out['saplings'] = int(np.isin(objects, SAPLING_IDS).sum())
    out['building_stones'] = int(((objects >= 115) & (objects <= 127)).sum())
    out['reefs'] = int(((objects >= 111) & (objects <= 114)).sum())
    out['wheat'] = int(((objects >= 85) & (objects <= 93)).sum())
    out['vine'] = int(((objects >= 94) & (objects <= 102)).sum())
    out['rice'] = int(((objects >= 103) & (objects <= 110)).sum())
    known = np.zeros(objects.shape, dtype=bool)
    for ids, _, _ in TREE_FAMILIES.values(): known |= np.isin(objects, ids)
    known |= np.isin(objects, SAPLING_IDS)
    known |= ((objects >= 85) & (objects <= 127))
    out['other_nonzero'] = int(((objects != 0) & ~known).sum())
    return out


def analyze_map(state) -> dict[str, Any]:
    T = np.asarray(state.terrain)
    O = np.asarray(state.objects)
    R = np.asarray(state.resources)
    C = np.asarray(state.claim)
    H = np.asarray(state.height)
    n = int(state.side * state.side)

    water = np.isin(T, WATER_IDS)
    land = ~water
    land_n = int(land.sum())

    terrain_counter = Counter(map(int, T.ravel().tolist()))
    terrain_ids = []
    for tid, count in sorted(terrain_counter.items(), key=lambda kv: (-kv[1], kv[0])):
        fr, en = TERRAIN_NAMES.get(tid, (f'Terrain {tid}', f'Terrain {tid}'))
        terrain_ids.append({'id': tid, 'name_fr': fr, 'name_en': en, 'cells': int(count), 'pct_map': _pct(count, n), 'pct_land': _pct(count, land_n) if tid not in WATER_IDS else 0.0})

    family_used = np.zeros(T.shape, dtype=bool)
    terrain_families = []
    for key, ids, fr, en in TERRAIN_FAMILIES:
        mask = np.isin(T, ids)
        # Snow is a deliberate overlapping analytical family inside Mountain.
        overlap = key == 'snow'
        if not overlap: family_used |= mask
        count = int(mask.sum())
        terrain_families.append({'key': key, 'name_fr': fr, 'name_en': en, 'cells': count, 'pct_map': _pct(count, n), 'pct_land': _pct(count, land_n)})
    other_mask = ~family_used
    terrain_families.append({'key': 'other', 'name_fr': 'Autres terrains', 'name_en': 'Other terrain', 'cells': int(other_mask.sum()), 'pct_map': _pct(int(other_mask.sum()), n), 'pct_land': _pct(int((other_mask & land).sum()), land_n)})

    object_counter = Counter(map(int, O.ravel().tolist()))
    object_ids = []
    for oid, count in sorted(object_counter.items(), key=lambda kv: (-kv[1], kv[0])):
        if oid == 0: continue
        fr, en = OBJECT_NAMES.get(oid, (f'Objet {oid}', f'Object {oid}'))
        object_ids.append({'id': oid, 'name_fr': fr, 'name_en': en, 'count': int(count), 'pct_map': _pct(count, n)})

    object_families = _object_family_counts(O)
    tree_adults = sum(object_families[k] for k in ('birch','elm','oak','other_adult'))
    tree_all_adults = tree_adults + object_families['palm']

    stones_by_state = []
    active_stones = 0
    stone_stock = 0
    for oid in range(115, 128):
        anchors = int((O == oid).sum())
        units_each = max(0, 127 - oid)
        stock = anchors * units_each
        if oid < 127: active_stones += anchors
        stone_stock += stock
        stones_by_state.append({'object_id': oid, 'state': oid - 114, 'anchors': anchors, 'units_each': units_each, 'stock': stock})

    minerals: dict[str, Any] = {}
    mining_support = np.isin(T, MOUNTAIN_ANALYSIS_IDS)
    support_n = int(mining_support.sum())
    ore_any = np.zeros(R.shape, dtype=bool)
    for key, (family, fr, en) in MINERALS.items():
        mask = (R & 0xF0) == family
        qty = (R[mask] & 0x0F).astype(np.uint8)
        ore_any |= mask
        snow_mask = mask & np.isin(T, (ROCK_SNOW_TRANS, SNOW_TRANS, SNOW))
        open_mask = mask & ~np.isin(T, (ROCK_SNOW_TRANS, SNOW_TRANS, SNOW))
        minerals[key] = {
            'name_fr': fr, 'name_en': en, 'cells': int(mask.sum()),
            'stock': int(qty.sum()) if qty.size else 0,
            'open_cells': int(open_mask.sum()), 'snow_covered_cells': int(snow_mask.sum()),
            'open_stock': int((R[open_mask] & 0x0F).sum()) if open_mask.any() else 0,
            'snow_covered_stock': int((R[snow_mask] & 0x0F).sum()) if snow_mask.any() else 0,
            'avg_per_occupied_cell': round(float(qty.mean()), 4) if qty.size else 0.0,
            'pct_mining_support': _pct(int(mask.sum()), support_n),
            'quantity_distribution': _percentiles(qty),
        }
    ore_on_support = ore_any & mining_support

    fish_mask = water & ((R & 0xF0) == 0) & ((R & 0x0F) > 0)
    fish_qty = (R[fish_mask] & 0x0F).astype(np.uint8)

    labels, n_water_components = component_labels(water)
    edge_ids = _edge_component_ids(labels)
    inland_sizes = []
    ocean_sizes = []
    for cid in range(1, n_water_components + 1):
        size = int((labels == cid).sum())
        (ocean_sizes if cid in edge_ids else inland_sizes).append(size)
    ocean_mask = np.isin(labels, list(edge_ids)) if edge_ids else np.zeros_like(water)
    inland_water_mask = water & ~ocean_mask
    ocean_cells = int(ocean_mask.sum())
    inland_water_cells = int(inland_water_mask.sum())
    snow_family_mask = np.isin(T, (ROCK_SNOW_TRANS, SNOW_TRANS, SNOW))
    mountain_non_snow_mask = mining_support & ~snow_family_mask

    river_details = _component_details(np.isin(T, RIVER_IDS))
    mountain_details = _component_details(np.isin(T, MOUNTAIN_ANALYSIS_IDS))
    swamp_details = _component_details(np.isin(T, SWAMP_IDS))
    desert_details = _component_details(np.isin(T, DESERT_IDS))
    forest_details = _component_details(np.isin(O, ADULT_TREE_IDS + TREE_FAMILIES['palm'][0] + SAPLING_IDS))
    mineral_component_details = {key: _component_details((R & 0xF0) == family) for key, (family, _fr, _en) in MINERALS.items()}
    local_players = _local_player_stats(state, T, O, R) if state.starts else []

    claims = C[C != 255]
    claim_counts = Counter(map(int, claims.tolist())) if claims.size else Counter()

    starts = [{'player': i+1, 'x': int(x), 'y': int(y)} for i, (x, y) in enumerate(state.starts)]
    nearest = []
    pair_distances = []
    for i, (x1, y1) in enumerate(state.starts):
        distances = []
        opponents = []
        for j, (x2, y2) in enumerate(state.starts):
            if i == j: continue
            d = int(hex_distance(int(x1), int(y1), int(x2), int(y2)))
            distances.append(d); opponents.append((d,j+1))
            if i < j: pair_distances.append(d)
        nearest_distance = min(distances) if distances else 0
        nearest_player = min(opponents)[1] if opponents else None
        nearest.append({'player': i+1, 'distance': nearest_distance, 'nearest_player': nearest_player})

    source = {
        'format': state.metadata.get('source_format', 'GENERATED'),
        'path': state.metadata.get('source_path'),
        'mode': state.metadata.get('mode'), 'archetype': state.metadata.get('archetype'),
        'seed': state.metadata.get('seed'),
    }

    result = {
        'schema_version': 7,
        'source': source,
        'general': {
            'side': int(state.side), 'cells': n, 'players': len(state.starts) or int(state.metadata.get('players', 0) or 0),
            'land_cells': land_n, 'water_cells': int(water.sum()),
            'ocean_cells': ocean_cells, 'inland_water_cells': inland_water_cells,
            'land_pct': _pct(land_n, n), 'water_pct': _pct(int(water.sum()), n),
            'green_grass_cells': int((T == GRASS).sum()), 'dry_grass_cells': int((T == DRY_GRASS).sum()),
            'mountain_cells': support_n, 'mountain_pct_land': _pct(support_n, land_n),
            'mountain_non_snow_cells': int(mountain_non_snow_mask.sum()), 'snow_family_cells': int(snow_family_mask.sum()),
            'desert_cells': int(np.isin(T, DESERT_IDS).sum()), 'swamp_cells': int(np.isin(T, SWAMP_IDS).sum()),
            'mud_cells': int(np.isin(T, MUD_IDS).sum()),
            'river_cells': int(np.isin(T, RIVER_IDS).sum()), 'shore_cells': int((T == SHORE).sum()),
        },
        'terrain': {'ids': terrain_ids, 'families': terrain_families},
        'objects': {'ids': object_ids, 'families': object_families},
        'vegetation': {
            'adult_wood_trees': int(tree_adults), 'adult_trees_including_palms': int(tree_all_adults),
            'saplings': int(object_families['saplings']),
            'sapling_label_fr': "Pousses d’arbre", 'sapling_label_en': 'Tree saplings',
            'families': {k: object_families[k] for k in ('birch','elm','oak','other_adult','palm')},
            'adult_density_per_1000_land': round(1000.0 * tree_all_adults / land_n, 4) if land_n else 0.0,
            'sapling_to_adult_pct': _pct(object_families['saplings'], tree_adults),
        },
        'building_stones': {
            'anchors_total': int(((O >= 115) & (O <= 127)).sum()),
            'anchors_active': int(active_stones), 'anchors_exhausted_127': int((O == 127).sum()),
            'stock_total': int(stone_stock), 'states': stones_by_state,
        },
        'resources': {
            'minerals': minerals,
            'mining_support_cells': support_n,
            'mining_occupied_cells': int(ore_on_support.sum()),
            'mining_support_occupancy_pct': _pct(int(ore_on_support.sum()), support_n),
            'fish_cells': int(fish_mask.sum()), 'fish_stock': int(fish_qty.sum()) if fish_qty.size else 0,
            'fish_density_per_1000_water': round(1000.0 * int(fish_mask.sum()) / int(water.sum()), 4) if water.any() else 0.0,
        },
        'agriculture': {
            'wheat': int(((O >= 85) & (O <= 93)).sum()),
            'vine': int(((O >= 94) & (O <= 102)).sum()),
            'rice': int(((O >= 103) & (O <= 110)).sum()),
        },
        # Normalized debug metrics. Each denominator matches the gameplay support
        # of the measured resource instead of blindly using total map cells.
        'densities': {
            'adult_trees_per_1000_land': round(1000.0 * tree_adults / land_n, 4) if land_n else 0.0,
            'palms_per_1000_land': round(1000.0 * object_families['palm'] / land_n, 4) if land_n else 0.0,
            'saplings_per_1000_land': round(1000.0 * object_families['saplings'] / land_n, 4) if land_n else 0.0,
            'building_stone_stock_per_1000_land': round(1000.0 * stone_stock / land_n, 4) if land_n else 0.0,
            'fish_stock_per_1000_water': round(1000.0 * (int(fish_qty.sum()) if fish_qty.size else 0) / int(water.sum()), 4) if water.any() else 0.0,
            'mineral_stock_per_1000_mountain': round(1000.0 * sum(v['stock'] for v in minerals.values()) / support_n, 4) if support_n else 0.0,
            'agriculture_cells_per_1000_land': round(1000.0 * (int(((O >= 85) & (O <= 110)).sum())) / land_n, 4) if land_n else 0.0,
        },
        'height': {'distribution': _percentiles(H.ravel()), 'land_distribution': _percentiles(H[land])},
        'hydrology': {
            'water_components': int(n_water_components), 'ocean_components': len(ocean_sizes),
            'inland_water_components': len(inland_sizes), 'inland_water_sizes': inland_sizes,
            'largest_inland_water': max(inland_sizes) if inland_sizes else 0,
            'river_components': len(river_details), 'river_sizes': [d['cells'] for d in river_details],
            'river_component_stats': _component_summary(river_details), 'river_details': river_details,
        },
        'spatial': {
            'mountain_components': len(mountain_details), 'mountain_sizes': [d['cells'] for d in mountain_details],
            'desert_components': len(desert_details), 'desert_sizes': [d['cells'] for d in desert_details],
            'swamp_components': len(swamp_details), 'swamp_sizes': [d['cells'] for d in swamp_details],
            'mountains': {'summary': _component_summary(mountain_details), 'components': mountain_details},
            'deserts': {'summary': _component_summary(desert_details), 'components': desert_details},
            'swamps': {'summary': _component_summary(swamp_details), 'components': swamp_details},
            'forests': {'summary': _component_summary(forest_details), 'components': forest_details},
            'minerals': {key: {'summary': _component_summary(rows), 'components': rows} for key, rows in mineral_component_details.items()},
        },
        'players': {
            'starts': starts, 'claims': {str(k+1): int(v) for k, v in sorted(claim_counts.items())},
            'nearest_start': nearest, 'pair_distance_distribution': _percentiles(np.asarray(pair_distances, dtype=np.int32)),
            'local_radii': list(LOCAL_RADII), 'local_resources': local_players,
        },
    }
    return result


def stats_json(stats: dict[str, Any]) -> str:
    return json.dumps(stats, ensure_ascii=False, indent=2, default=str)


def stats_csv(stats: dict[str, Any]) -> str:
    """Compact long-form CSV suitable for spreadsheets and quick comparisons."""
    out = io.StringIO(newline='')
    w = csv.writer(out)
    w.writerow(['section','metric','key','value'])
    for k, v in stats['general'].items(): w.writerow(['general', k, '', v])
    for row in stats['terrain']['families']:
        w.writerow(['terrain_family', 'cells', row['key'], row['cells']])
        w.writerow(['terrain_family', 'pct_map', row['key'], row['pct_map']])
    for row in stats['terrain']['ids']:
        w.writerow(['terrain_id', 'cells', row['id'], row['cells']])
    for key, data in stats['resources']['minerals'].items():
        w.writerow(['mineral', 'cells', key, data['cells']]); w.writerow(['mineral', 'stock', key, data['stock']])
    for row in stats['building_stones']['states']:
        w.writerow(['building_stone', 'anchors', row['object_id'], row['anchors']]); w.writerow(['building_stone', 'stock', row['object_id'], row['stock']])
    for key, value in stats['vegetation']['families'].items(): w.writerow(['vegetation', 'count', key, value])
    w.writerow(['vegetation', 'count', 'saplings', stats['vegetation']['saplings']])
    for key, value in stats['agriculture'].items(): w.writerow(['agriculture', 'cells', key, value])
    for key, value in stats.get('densities', {}).items(): w.writerow(['density', 'per_1000', key, value])
    for player in stats.get('players', {}).get('local_resources', []):
        for radius, metrics in player['radii'].items():
            prefix=f"P{player['player']}_r{radius}"
            for key in ('adult_trees','saplings','building_stone_stock','fish_stock','mountain_cells','desert_cells','swamp_cells','water_cells'):
                w.writerow(['player_local', key, prefix, metrics[key]])
            for mineral, data in metrics['minerals'].items():
                w.writerow(['player_local_mineral', f'{mineral}_stock', prefix, data['stock']])
    return out.getvalue()


def format_stats_report(stats: dict[str, Any], lang: str = 'fr') -> str:
    fr = lang != 'en'
    g = stats['general']; r = stats['resources']; v = stats['vegetation']; bs = stats['building_stones']; h = stats['height'].get('land_distribution', stats['height']['distribution']); hy = stats['hydrology']; p = stats['players']; ag = stats['agriculture']
    lines = []
    lines.append(('RÉSUMÉ' if fr else 'SUMMARY'))
    lines.append('=' * 72)
    lines.append(f"{g['side']}×{g['side']} — {g['cells']:,} " + ('cellules' if fr else 'cells'))
    lines.append((f"Terre {g['land_cells']:,} ({g['land_pct']:.2f} %) | Eau {g['water_cells']:,} ({g['water_pct']:.2f} %) = mer {g.get('ocean_cells',0):,} + lacs {g.get('inland_water_cells',0):,}" if fr else f"Land {g['land_cells']:,} ({g['land_pct']:.2f} %) | Water {g['water_cells']:,} ({g['water_pct']:.2f} %) = ocean {g.get('ocean_cells',0):,} + lakes {g.get('inland_water_cells',0):,}"))
    lines.append((f"Montagne {g['mountain_cells']:,} ({g['mountain_pct_land']:.2f} % de la terre) | Désert {g['desert_cells']:,} | Marais {g['swamp_cells']:,} | Boue {g['mud_cells']:,} | Rivière {g['river_cells']:,}" if fr else f"Mountain {g['mountain_cells']:,} ({g['mountain_pct_land']:.2f} % of land) | Desert {g['desert_cells']:,} | Swamp {g['swamp_cells']:,} | Mud {g['mud_cells']:,} | River {g['river_cells']:,}"))
    lines.append('')
    lines.append('RESSOURCES' if fr else 'RESOURCES'); lines.append('-' * 72)
    for key, data in r['minerals'].items():
        name = data['name_fr' if fr else 'name_en']
        lines.append(f"{name:<12} {data['cells']:>8,} " + ('cases' if fr else 'cells') + f" | stock {data['stock']:>9,} | " + (f"ouvert {data.get('open_stock',data['stock']):,} / sous neige {data.get('snow_covered_stock',0):,}" if fr else f"open {data.get('open_stock',data['stock']):,} / snow-covered {data.get('snow_covered_stock',0):,}"))
    lines.append((f"Occupation support minier : {r['mining_occupied_cells']:,}/{r['mining_support_cells']:,} ({r['mining_support_occupancy_pct']:.2f} %)" if fr else f"Mining support occupancy: {r['mining_occupied_cells']:,}/{r['mining_support_cells']:,} ({r['mining_support_occupancy_pct']:.2f} %)"))
    lines.append((f"Poissons : {r['fish_cells']:,} cases | stock {r['fish_stock']:,}" if fr else f"Fish: {r['fish_cells']:,} cells | stock {r['fish_stock']:,}"))
    lines.append('')
    lines.append('RESSOURCES FORESTIÈRES & PIERRES' if fr else 'FORESTRY RESOURCES & STONES'); lines.append('-' * 72)
    lines.append((f"Arbres adultes : {v['adult_wood_trees']:,} | Palmiers : {v['families']['palm']:,} | Pousses d’arbre : {v['saplings']:,}" if fr else f"Adult trees: {v['adult_wood_trees']:,} | Palms: {v['families']['palm']:,} | Tree saplings: {v['saplings']:,}"))
    lines.append((f"Pierres de construction : {bs['anchors_total']:,} piles ({bs['anchors_exhausted_127']:,} épuisées) | stock {bs['stock_total']:,}" if fr else f"Building stones: {bs['anchors_total']:,} piles ({bs['anchors_exhausted_127']:,} exhausted) | stock {bs['stock_total']:,}"))
    d1000=stats.get('densities', {})
    if d1000:
        lines.append(''); lines.append('DENSITÉS NORMALISÉES / 1000' if fr else 'NORMALIZED DENSITIES / 1000'); lines.append('-' * 72)
        if fr:
            lines.append(f"Arbres adultes : {d1000.get('adult_trees_per_1000_land',0):.2f} / 1000 terre")
            lines.append(f"Palmiers : {d1000.get('palms_per_1000_land',0):.2f} / 1000 terre")
            lines.append(f"Pousses : {d1000.get('saplings_per_1000_land',0):.2f} / 1000 terre")
            lines.append(f"Pierre stock : {d1000.get('building_stone_stock_per_1000_land',0):.2f} / 1000 terre")
            lines.append(f"Poisson stock : {d1000.get('fish_stock_per_1000_water',0):.2f} / 1000 eau")
            lines.append(f"Minerai stock : {d1000.get('mineral_stock_per_1000_mountain',0):.2f} / 1000 montagne")
            lines.append(f"Agriculture : {d1000.get('agriculture_cells_per_1000_land',0):.2f} / 1000 terre")
        else:
            lines.append(f"Adult trees: {d1000.get('adult_trees_per_1000_land',0):.2f} / 1000 land")
            lines.append(f"Palms: {d1000.get('palms_per_1000_land',0):.2f} / 1000 land")
            lines.append(f"Saplings: {d1000.get('saplings_per_1000_land',0):.2f} / 1000 land")
            lines.append(f"Stone stock: {d1000.get('building_stone_stock_per_1000_land',0):.2f} / 1000 land")
            lines.append(f"Fish stock: {d1000.get('fish_stock_per_1000_water',0):.2f} / 1000 water")
            lines.append(f"Mining stock: {d1000.get('mineral_stock_per_1000_mountain',0):.2f} / 1000 mountain")
            lines.append(f"Agriculture: {d1000.get('agriculture_cells_per_1000_land',0):.2f} / 1000 land")
    lines.append('')
    lines.append('HYDROLOGIE / RELIEF' if fr else 'HYDROLOGY / HEIGHT'); lines.append('-' * 72)
    lines.append((f"Eaux intérieures : {hy['inland_water_components']} composantes | plus grande {hy['largest_inland_water']:,} cases | rivières {hy['river_components']} composantes" if fr else f"Inland waters: {hy['inland_water_components']} components | largest {hy['largest_inland_water']:,} cells | rivers {hy['river_components']} components"))
    lines.append((f"Hauteurs terrestres P10 {h['p10']:.1f} | P25 {h['p25']:.1f} | médiane {h['median']:.1f} | P75 {h['p75']:.1f} | P95 {h['p95']:.1f} | max {h['max']:.0f}" if fr else f"Land heights P10 {h['p10']:.1f} | P25 {h['p25']:.1f} | median {h['median']:.1f} | P75 {h['p75']:.1f} | P95 {h['p95']:.1f} | max {h['max']:.0f}"))
    sp=stats.get('spatial',{})
    if sp.get('mountains'):
        ms=sp['mountains']['summary']; ds=sp['deserts']['summary']; ss=sp['swamps']['summary']; fs=sp['forests']['summary']
        if fr:
            lines.append(f"Composantes : massifs {ms['count']} (max {int(ms['size_distribution']['max']):,}) | déserts {ds['count']} | marais {ss['count']} | forêts {fs['count']}")
        else:
            lines.append(f"Components: mountains {ms['count']} (max {int(ms['size_distribution']['max']):,}) | deserts {ds['count']} | swamps {ss['count']} | forests {fs['count']}")
    if any(ag.values()):
        lines.append(''); lines.append('AGRICULTURE' if fr else 'AGRICULTURE'); lines.append('-' * 72)
        lines.append((f"Blé {ag['wheat']:,} | Vigne {ag['vine']:,} | Riz {ag['rice']:,}" if fr else f"Wheat {ag['wheat']:,} | Vine {ag['vine']:,} | Rice {ag['rice']:,}"))
    if p['starts']:
        lines.append(''); lines.append('JOUEURS / STARTS' if fr else 'PLAYERS / STARTS'); lines.append('-' * 72)
        for row in p['nearest_start']:
            lines.append((f"P{row['player']}: adversaire le plus proche = {row['distance']} HEX" if fr else f"P{row['player']}: nearest opponent = {row['distance']} HEX"))
        if p.get('local_resources'):
            lines.append(''); lines.append('RESSOURCES LOCALES — 0–50 / 50–100' if fr else 'LOCAL RESOURCES — 0–50 / 50–100'); lines.append('-' * 72)
            for row in p['local_resources']:
                m=row['radii'].get('50', {})
                ore=sum(v['stock'] for v in m.get('minerals',{}).values())
                if fr:
                    lines.append(f"P{row['player']}: arbres {m.get('adult_trees',0):,} | pousses {m.get('saplings',0):,} | pierre {m.get('building_stone_stock',0):,} | poisson {m.get('fish_stock',0):,} | minerai {ore:,}")
                else:
                    lines.append(f"P{row['player']}: trees {m.get('adult_trees',0):,} | saplings {m.get('saplings',0):,} | stone {m.get('building_stone_stock',0):,} | fish {m.get('fish_stock',0):,} | ore {ore:,}")
    lines.append(''); lines.append('DEBUG — TOUS LES TERRAIN IDs PRÉSENTS' if fr else 'DEBUG — ALL PRESENT TERRAIN IDs'); lines.append('-' * 72)
    for row in stats['terrain']['ids']:
        lines.append(f"{row['id']:>3}  {row['name_fr' if fr else 'name_en']:<28} {row['cells']:>9,}  {row['pct_map']:>7.3f} %")
    lines.append(''); lines.append('DEBUG — TOUS LES OBJECT IDs PRÉSENTS' if fr else 'DEBUG — ALL PRESENT OBJECT IDs'); lines.append('-' * 72)
    for row in stats['objects']['ids']:
        lines.append(f"{row['id']:>3}  {row['name_fr' if fr else 'name_en']:<28} {row['count']:>9,}")
    return '\n'.join(lines)
