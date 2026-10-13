"""Convert current SAV surface into a new map, never a resumed game."""
from __future__ import annotations
import numpy as np
from .model import MapState
from .object_context import is_runtime, reef_mask, construction_mask, felling_mask
from .constants import WATER_IDS


def _players(state, metadata, include_players):
    if not include_players:
        return []
    records = [r for r in state.metadata.get('sav_player_records', ())
               if r.get('active') and r.get('start_x') is not None and r.get('start_y') is not None]
    if not records or any(r.get('layout') != 'native_v11' for r in records):
        return list(state.starts)
    if len(records) != len(state.starts):
        raise ValueError('SAV : départs et fiches joueurs incohérents pour la conversion')
    nations, teams, slots = [], [], []
    for record in records:
        nation, team = record.get('tribe_code_candidate'), record.get('team_code')
        if nation not in (0, 1, 2, 3, 255):
            raise ValueError(f"SAV : civilisation non prise en charge pour J{record['player']} ({nation})")
        if type(team) is not int or not 0 <= team < 20:
            raise ValueError(f"SAV : équipe non prise en charge pour J{record['player']} ({team})")
        nations.append(nation)
        # Native zero is an alliance; UI zero means an independent player.
        teams.append(team + 1)
        slots.append(record['player'])
    metadata.update(classic_start_nations=tuple(nations), player_teams=tuple(teams),
                    start_slot_indices=list(range(len(records))), players=len(records),
                    sav_export_player_slots=slots)
    return list(state.starts)


def sav_to_map_state(state: MapState, *, include_players=True) -> MapState:
    """Return an independent derived copy; ordinary maps are unchanged."""
    if not is_runtime(state):
        return state
    flags = state.runtime_flags
    if flags is None or flags.shape != state.objects.shape or flags.dtype != np.uint8:
        raise ValueError('SAV : flags runtime absents ou invalides ; réimportez le fichier SAV')
    raw = state.objects
    reefs, markers, felling = reef_mask(state), construction_mask(state), felling_mask(state)
    animations = (raw >= 128) & (raw <= 207)
    unsupported = ((animations & ~felling) | np.isin(raw, (111, 114, 215, 223, 231))
                   | (np.isin(raw, (112, 113)) & ~markers))
    if unsupported.any():
        ids = ', '.join(map(str, np.unique(raw[unsupported]).tolist()))
        raise ValueError('SAV : objets runtime non convertibles sans interprétation incertaine : ' + ids)
    area = state.area.copy()
    area[:, :, 3] = 255
    area[:, :, 4] = flags & np.uint8(1)
    obj = area[:, :, 2]
    obj[reefs] = raw[reefs] + np.uint8(98)
    obj[markers] = 0
    # No woodcutter in a new map: settle observed variants to confirmed stumps.
    obj[felling] = np.uint8(208) + (raw[felling] - np.uint8(128)) % np.uint8(8)
    area[:, :, 4][markers | felling] = 0
    blocked = np.isin(state.terrain, (*WATER_IDS, 128, 129, 0x70))
    area[:, :, 4][blocked] |= np.uint8(1)
    metadata = dict(state.metadata)
    metadata.update(source_format='SAV_TERRAIN_EXPORT', sav_terrain_export=True)
    starts = _players(state, metadata, include_players)
    metadata['sav_export_conversion'] = {
        'reefs_recoded': int(reefs.sum()), 'construction_markers_removed': int(markers.sum()),
        'felling_settled_to_stumps': int(felling.sum()),
        'claims_neutralized': int((state.claim != 255).sum()),
        'changed_object_cells': int((obj != raw).sum()), 'starts': len(starts),
        'source_player_slots': metadata.get('sav_export_player_slots', []),
        'runtime_buildings_units_inventories_retained': False,
        'terrain_before_editor_preparation_unchanged': True,
        'remaining_ground_resources_unchanged': True, 'static_access_source': 'sav_byte10_bit0',
    }
    return MapState(state.side, area, starts, metadata=metadata)
