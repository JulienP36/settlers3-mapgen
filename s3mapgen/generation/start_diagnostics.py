"""Read-only departure diagnostics on final geography and selection-time objects."""
import numpy as np
from hashlib import blake2b
from ..map_data.constants import WATER_IDS, GRASS
from ..map_data.hexgrid import component_labels
from ..map_data.model import MapState
from .start_safety import candidate_centers, _centers_matching, START_TERRAIN_OFFSETS


def capture_departure_source(state, phase):
    """Keep an immutable session snapshot; never serialize it into MAP/EDM."""
    state.departure_area = state.area.copy()
    state.departure_area.flags.writeable = False
    state.departure_phase = phase


def departure_source(state, context='selection'):
    """Final terrain/height; preserve only the selection-time object context.

    Early starts precede some biome passes. Their immutable snapshot is useful
    for ignoring later objects, but its geography must never color the final map.
    Imported maps and the after-content Classic route use the complete current
    Area. No generation data or captured snapshot is modified.
    """
    if context not in ('selection', 'before_objects', 'current'):
        raise ValueError('Unknown departure context')
    if context != 'selection':
        from ..map_data.editor_height import prepare_editor_export
        from .editor_starts import editor_occupation
        area = state.area.copy()
        metadata = dict(state.metadata)
        # Claims describe ownership established by starts or later play. They
        # are outside both placement questions: a fresh start uses terrain only,
        # while the current-map check adds the objects already in the Area.
        # Neutralize them on this analysis copy for every imported format.
        if context in ('before_objects', 'current'):
            area[:, :, 3] = 255
            # Old versions used this metadata flag for private start records or
            # occupied claims. Neither makes terrain/object admission unknown.
            metadata['native_start_context_unavailable'] = False
        source_format = metadata.get('source_format')
        if str(source_format).upper() == 'SAV':
            from ..map_data.object_context import construction_mask
            # A sign/stake belongs to a building setup, explicitly ignored by
            # these terrain(+objects) questions. Do not restore byte14 here.
            area[:, :, 2][construction_mask(state)] = 0
        eligible = (64 <= state.side <= 768 and source_format != 'SAV'
                    and np.all(area[:, :, 3] == 255)
                    and not metadata.get('native_start_context_unavailable'))
        key = (blake2b(state.area.tobytes(), digest_size=16).digest(), bool(eligible), context)
        cache = getattr(state, '_departure_export_cache', {})
        if key in cache:
            return MapState(state.side, cache[key], list(state.starts), metadata=metadata), 'export_' + context
        # Exactly the writer's preparation, on a copy. Never normalize a SAV
        # or a map outside the fresh-map/native diagnostic domain.
        if eligible:
            prepare_editor_export(area)
        if context == 'before_objects':
            occupied, _ = editor_occupation(area[:, :, 2])
            area[:, :, 4][occupied | (area[:, :, 2] != 0)] &= np.uint8(254)
            area[:, :, 2] = 0
            blocked = np.isin(area[:, :, 1], (*WATER_IDS, 128, 129, 0x70, 80, 81))
            area[:, :, 4][blocked] |= np.uint8(1)
        area.flags.writeable = False
        # At most the two contexts for the current bytes; mutation invalidates
        # by content, including in-place edits. Start records are never cached.
        cache = {k:v for k,v in cache.items() if k[:2] == key[:2]}
        cache[key] = area
        state._departure_export_cache = cache
        return MapState(state.side, area, list(state.starts), metadata=metadata), 'export_' + context
    saved = state.departure_area
    if saved is None:
        return state, 'current'
    if state.departure_phase == 'after_objects':
        return state, 'final_after_objects'
    area = state.area.copy()
    area[:, :, 2] = saved[:, :, 2]
    area[:, :, 4] = saved[:, :, 4]
    # Update terrain-derived blocking without importing later object flags.
    blocked_ids = (*WATER_IDS, 128, 129, 0x70)
    old_blocked = np.isin(saved[:, :, 1], blocked_ids)
    blocked = np.isin(state.terrain, blocked_ids)
    clear_old = old_blocked & ~blocked & (saved[:, :, 2] == 0)
    area[:, :, 4][clear_old] &= np.uint8(254)
    area[:, :, 4][blocked] |= np.uint8(1)
    source = MapState(state.side, area, metadata=state.metadata)
    return source, 'final_' + state.departure_phase


def departure_diagnostics(state, policy='valid_conservative', *, context='selection'):
    if ':' in policy:
        policy, context = policy.split(':', 1)
    source, phase = departure_source(state, context)
    terrain = _centers_matching(source.terrain == GRASS, START_TERRAIN_OFFSETS)
    clearance = candidate_centers(source, include_levelling=False)
    unavailable = False
    if policy == 'valid_conservative':
        valid = candidate_centers(source)
    else:
        from .classic_starts import ClassicRuntime, _LEVEL, _OUTER
        unavailable = (not 64 <= source.side <= 768 or not np.all(source.claim == 255)
                       or bool(source.metadata.get('native_start_context_unavailable')))
        if unavailable:
            terrain = clearance = valid = np.zeros(source.height.shape, bool)
        else:
            players = int(source.metadata.get('players', 1))
            native_source = MapState(source.side, source.area, metadata={**source.metadata, 'players': players})
            runtime = ClassicRuntime(native_source, (0,)*players, 2, 0, 0)
            nations = tuple(range(4)) if policy == 'valid_all' else (int(policy.rsplit('_', 1)[1]),)
            terrain_masks, clearance_masks = [], []
            for nation in nations:
                family = source.terrain & 240
                allowed = family == 16
                if nation == 1:
                    allowed |= family == 64
                elif nation == 2:
                    allowed |= family == 144
                offsets = (*_LEVEL[nation], *_OUTER[nation])
                terrain_masks.append(_centers_matching(allowed, offsets))
                clear = allowed & (source.claim == 255) & ((source.accessibility & 13) == 0)
                clearance_masks.append(_centers_matching(clear, offsets))
            terrain = np.logical_and.reduce(terrain_masks)
            clearance = np.logical_and.reduce(clearance_masks)
            valid = np.logical_and.reduce([runtime.valid_centers(n) for n in nations])
    # The native leveller needs its complete 31x31 domain. A missing domain
    # is a border/footprint refusal, not evidence of an excessive slope.
    domain = np.zeros(source.height.shape, bool)
    if source.side >= 31:
        domain[15:source.side-15, 15:source.side-15] = True
    terrain &= domain
    clearance &= domain
    if policy == 'valid_conservative' and not np.all(source.claim == 255):
        from scipy.ndimage import minimum_filter
        clearance &= minimum_filter(source.claim == 255, size=31, mode='constant', cval=0)
    labels, count = component_labels(~np.isin(source.terrain, WATER_IDS))
    masks = (terrain, clearance, valid)
    stages = [int(mask.sum()) for mask in masks]
    island_stages = [[int(np.count_nonzero(mask & (labels == i))) for mask in masks]
                     for i in range(1, count+1)]
    from .editor_starts import editor_start_checks
    nations = tuple(range(4)) if policy in ('valid_all','valid_conservative') else (int(policy.rsplit('_',1)[1]),)
    editor = editor_start_checks(source,nations)
    green = editor['valid'].copy() if editor['available'] and not unavailable else np.zeros_like(valid)
    yellow = valid & ~editor['valid'] if editor['available'] else np.zeros_like(valid)
    relocation = green & ~valid
    visible = green | yellow
    return dict(valid=valid, terrain=terrain, clearance=clearance, total=int(visible.sum()),
                labels=labels, counts=[int(np.count_nonzero(visible & (labels == i))) for i in range(1,count+1)],
                stages=stages, island_stages=island_stages, phase=phase,
                unavailable=unavailable, editor=editor, green=green,yellow=yellow,
                game_exact=valid, relocation=relocation, visible=green | yellow,
                relocation_count=int(relocation.sum()),
                green_count=int(green.sum()),yellow_count=int(yellow.sum()),
                island_colors=[[int(np.count_nonzero(green & (labels == i))),
                                int(np.count_nonzero(yellow & (labels == i)))] for i in range(1,count+1)])
