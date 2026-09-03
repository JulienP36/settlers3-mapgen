"""Semantic chart-to-map focus masks and deterministic highlighting.

Charts expose small, language-independent ``focus`` dictionaries on their
hit regions.  This module is the rendering-side interpreter for those
dictionaries: it selects the exact source cells and paints a temporary,
non-exported emphasis layer over the current preview.
"""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from PIL import Image

from ...map_data.constants import (
    ADULT_TREE_IDS,
    BEE_NEST_IDS,
    DESERT_IDS,
    MOUNTAIN_FAMILY_IDS,
    PALM_TREE_IDS,
    PLANTATION_IDS,
    REEF_IDS,
    RIVER_IDS,
    SAPLING_STAGE_1_IDS,
    SAPLING_STAGE_2_IDS,
    SWAMP_IDS,
    WATER_IDS,
)
from ...map_data.hexgrid import component_labels


MINERAL_FAMILIES = {
    'coal': 0x10,
    'iron': 0x20,
    'gold': 0x30,
    'gems': 0x40,
    'sulfur': 0x50,
}
SNOW_TERRAIN_IDS = (35, 128, 129)
TREE_FOCUS_IDS = ADULT_TREE_IDS + PALM_TREE_IDS + PLANTATION_IDS + SAPLING_STAGE_2_IDS + SAPLING_STAGE_1_IDS
STONE_FOCUS_IDS = tuple(range(115, 128))
AGRICULTURE_FOCUS_IDS = tuple(range(85, 111)) + BEE_NEST_IDS

_OBJECT_FAMILY_IDS = {
    'decorative_stones': tuple(range(1, 29)),
    'wrecks': tuple(range(29, 34)),
    'graves': (34,),
    'plants_fungi': tuple(range(35, 41)),
    'stumps': tuple(range(41, 43)),
    'dead_trees': tuple(range(43, 45)),
    'desert_props': tuple(range(45, 50)),
    'flowers_bushes': tuple(range(50, 62)),
    'reeds': tuple(range(62, 68)),
    'adult_trees': ADULT_TREE_IDS + PALM_TREE_IDS,
    'small_trees': PLANTATION_IDS,
    'reefs': REEF_IDS,
    'building_stones': STONE_FOCUS_IDS,
}


def _freeze(value):
    """Return a stable, hashable representation for a semantic payload."""
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, Mapping):
        return tuple(sorted((str(key), _freeze(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return tuple(sorted((_freeze(item) for item in value), key=repr))
    return value


def focus_signature(focus) -> tuple | None:
    """Return a cache-safe identity for a chart focus payload."""
    return None if not focus else _freeze(focus)


def _empty(state) -> np.ndarray:
    return np.zeros(np.asarray(state.terrain).shape, dtype=bool)


def _ids(value) -> tuple[int, ...]:
    if isinstance(value, (int, np.integer)):
        value = (value,)
    if not isinstance(value, (list, tuple, range, set, frozenset)):
        return ()
    return tuple(int(item) for item in value)


def _hex_distance_grid(shape: tuple[int, int], x0: int, y0: int) -> np.ndarray:
    yy, xx = np.indices(shape, dtype=np.int32)
    dx = xx - int(x0)
    dy = yy - int(y0)
    return np.where(
        (dx * dy) >= 0,
        np.maximum(np.abs(dx), np.abs(dy)),
        np.abs(dx) + np.abs(dy),
    ).astype(np.int16)


def _water_component_mask(terrain: np.ndarray, component: str) -> np.ndarray:
    water = np.isin(terrain, WATER_IDS)
    labels, count = component_labels(water)
    if not count:
        return np.zeros_like(water)
    edge_values = np.concatenate((labels[0, :], labels[-1, :], labels[:, 0], labels[:, -1]))
    edge_ids = {int(value) for value in np.unique(edge_values) if int(value) != 0}
    if component == 'ocean':
        selected_ids = edge_ids
    elif component == 'inland':
        selected_ids = set(range(1, count + 1)) - edge_ids
    else:
        selected_ids = set()
    return np.isin(labels, tuple(selected_ids)) if selected_ids else np.zeros_like(water)


def _component_mask(terrain: np.ndarray, family: str, component_id) -> np.ndarray:
    families = {
        'mountain': np.isin(terrain, MOUNTAIN_FAMILY_IDS),
        'desert': np.isin(terrain, DESERT_IDS),
        'swamp': np.isin(terrain, SWAMP_IDS),
        'river': np.isin(terrain, RIVER_IDS),
        'water': np.isin(terrain, WATER_IDS),
    }
    source = families.get(str(family))
    if source is None:
        return np.zeros_like(terrain, dtype=bool)
    labels, _count = component_labels(source)
    try:
        return labels == int(component_id)
    except (TypeError, ValueError):
        return np.zeros_like(source)


def _player_local_mask(state, focus: Mapping) -> np.ndarray:
    terrain = np.asarray(state.terrain)
    objects = np.asarray(state.objects)
    resources = np.asarray(state.resources)
    try:
        player = int(focus.get('player'))
        x, y = state.starts[player - 1]
    except (IndexError, TypeError, ValueError):
        return np.zeros_like(terrain, dtype=bool)
    radius = max(0, int(focus.get('radius', 50)))
    distance = _hex_distance_grid(terrain.shape, int(x), int(y))
    inner = bool(focus.get('inner', True))
    if inner:
        in_range = distance <= radius
    else:
        inner_radius = max(0, int(focus.get('inner_radius', 50)))
        in_range = (distance > inner_radius) & (distance <= radius)

    resource = str(focus.get('resource', ''))
    if resource == 'trees':
        content = np.isin(objects, TREE_FOCUS_IDS)
    elif resource in ('stone', 'building_stones'):
        content = np.isin(objects, STONE_FOCUS_IDS)
    elif resource == 'fish':
        content = np.isin(terrain, WATER_IDS) & ((resources & 0xF0) == 0) & ((resources & 0x0F) > 0)
    elif resource == 'minerals':
        family = MINERAL_FAMILIES.get(str(focus.get('family')))
        content = (resources & 0xF0) == family if family is not None else np.isin(resources & 0xF0, tuple(MINERAL_FAMILIES.values()))
        content &= ~np.isin(terrain, SNOW_TERRAIN_IDS)
    else:
        family = MINERAL_FAMILIES.get(resource)
        content = (resources & 0xF0) == family if family is not None else np.zeros_like(terrain, dtype=bool)
    return in_range & content


def focus_mask(state, focus) -> np.ndarray:
    """Resolve a chart semantic payload to exact map cells.

    Unknown or malformed payloads intentionally resolve to an empty mask; a
    tooltip can therefore remain usable even if a future chart adds a payload
    that this renderer does not know yet.
    """
    terrain = np.asarray(state.terrain)
    objects = np.asarray(state.objects)
    resources = np.asarray(state.resources)
    if not isinstance(focus, Mapping):
        return np.zeros_like(terrain, dtype=bool)
    kind = str(focus.get('kind', ''))

    if kind in ('terrain_ids', 'object_ids'):
        source = terrain if kind == 'terrain_ids' else objects
        return np.isin(source, _ids(focus.get('ids')))
    if kind == 'object_family':
        ids = _ids(focus.get('ids')) or _OBJECT_FAMILY_IDS.get(str(focus.get('family')), ())
        return np.isin(objects, ids)
    if kind == 'resource_family':
        family = MINERAL_FAMILIES.get(str(focus.get('family')))
        if family is None:
            return np.zeros_like(terrain, dtype=bool)
        mask = (resources & 0xF0) == family
        snow = np.isin(terrain, SNOW_TERRAIN_IDS)
        scope = str(focus.get('scope', 'all'))
        if scope == 'snow':
            mask &= snow
        elif scope == 'open':
            mask &= ~snow
        return mask
    if kind == 'fish':
        return np.isin(terrain, WATER_IDS) & ((resources & 0xF0) == 0) & ((resources & 0x0F) > 0)
    if kind == 'water_component':
        return _water_component_mask(terrain, str(focus.get('component', '')))
    if kind == 'component':
        return _component_mask(terrain, str(focus.get('family', '')), focus.get('component_id'))
    if kind == 'height_band':
        height = np.asarray(state.height)
        try:
            threshold = float(focus.get('threshold'))
        except (TypeError, ValueError):
            return np.zeros_like(terrain, dtype=bool)
        mode = str(focus.get('mode', 'le'))
        if mode == 'ge':
            selected = height >= threshold
        elif mode == 'eq':
            selected = np.isclose(height.astype(np.float32), threshold)
        elif mode == 'range':
            try:
                selected = (height >= float(focus.get('minimum'))) & (height <= float(focus.get('maximum')))
            except (TypeError, ValueError):
                return np.zeros_like(terrain, dtype=bool)
        else:
            selected = height <= threshold
        return selected & ~np.isin(terrain, WATER_IDS)
    if kind == 'start_player':
        try:
            player = int(focus.get('player'))
            x, y = state.starts[player - 1]
        except (IndexError, TypeError, ValueError):
            return np.zeros_like(terrain, dtype=bool)
        mask = np.zeros_like(terrain, dtype=bool)
        if 0 <= int(y) < terrain.shape[0] and 0 <= int(x) < terrain.shape[1]:
            mask[int(y), int(x)] = True
        return mask
    if kind == 'player_local':
        return _player_local_mask(state, focus)
    return np.zeros_like(terrain, dtype=bool)


def focus_view(focus) -> str:
    """Choose the most useful existing viewer layer for a focus payload."""
    if isinstance(focus, Mapping) and focus.get('view') in {
        'global', 'heightmap', 'resources', 'territories', 'initial_territory', 'paths', 'crops', 'heatmap',
    }:
        return str(focus['view'])
    kind = focus.get('kind') if isinstance(focus, Mapping) else None
    if kind == 'height_band':
        return 'heightmap'
    if kind == 'start_player':
        return 'global'
    if kind == 'resource_family':
        return 'resources'
    if kind == 'player_local':
        return 'global'
    return 'global'


def apply_focus_overlay(base: Image.Image, state, focus, mask=None) -> Image.Image:
    """Dim non-selected cells and brighten the exact selected cells."""
    if not focus:
        return base.copy()
    mask = focus_mask(state, focus) if mask is None else np.asarray(mask, dtype=bool)
    if not mask.any():
        return base.copy()
    image = np.asarray(base.convert('RGB')).copy().astype(np.float32)
    dim = np.asarray((18, 20, 24), dtype=np.float32)
    highlight = np.asarray((255, 211, 54), dtype=np.float32)
    image[~mask] = image[~mask] * 0.28 + dim * 0.72
    image[mask] = image[mask] * 0.18 + highlight * 0.82
    return Image.fromarray(np.rint(image).clip(0, 255).astype(np.uint8), mode='RGB')
