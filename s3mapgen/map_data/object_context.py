"""Read-only interpretation of map objects versus current SAV runtime objects.

Raw IDs remain in MapState. The decoration projection below is for existing
chart categories only; it must never be serialized as an export conversion.
"""
from __future__ import annotations

import numpy as np
from .constants import WATER_IDS, REEF_IDS


def is_runtime(state) -> bool:
    return str(state.metadata.get('source_format', '')).upper() == 'SAV'


def reef_mask(state) -> np.ndarray:
    if is_runtime(state):
        return np.isin(state.objects, (13, 14, 15, 16)) & np.isin(state.terrain, WATER_IDS)
    return np.isin(state.objects, REEF_IDS)


def construction_mask(state) -> np.ndarray:
    return (np.isin(state.objects, (112, 113)) & ~np.isin(state.terrain, WATER_IDS)
            if is_runtime(state) else np.zeros(state.objects.shape, bool))


def felling_mask(state) -> np.ndarray:
    # Variants 0..4 and 6 observed; palm variant5 and holes7 remain unconfirmed.
    obj = state.objects.astype(np.int16)
    return (((obj >= 128) & (obj <= 207) & np.isin((obj - 128) % 8, (0, 1, 2, 3, 4, 6)))
            if is_runtime(state) else np.zeros(obj.shape, bool))


def decoration_objects(state) -> np.ndarray:
    """Project only confirmed runtime reefs into the static chart catalogue."""
    if not is_runtime(state):
        return state.objects
    obj = state.objects.copy()
    # These runtime values are not static border stones or static reefs.
    obj[np.isin(obj, (13, 14, 15, 16, 111, 112, 113, 114))] = 0
    reefs = reef_mask(state)
    obj[reefs] = state.objects[reefs] + np.uint8(98)
    return obj


def object_family_mask(state, ids, family=None) -> np.ndarray:
    if family == 'reefs':
        return reef_mask(state)
    return np.isin(decoration_objects(state), tuple(ids))


def runtime_object_name(state, oid: int):
    """Known context-dependent names; None leaves the existing catalogue intact."""
    if not is_runtime(state):
        return None
    if oid in (13, 14, 15, 16):
        cells = state.objects == oid
        if np.all(np.isin(state.terrain[cells], WATER_IDS)):
            return (f'Récif {oid - 12}', f'Reef {oid - 12}')
        return (f'Objet runtime {oid} — récif sur eau, autre contexte inconnu',
                f'Runtime object {oid} — reef on water, other context unknown')
    if oid in (112, 113):
        cells = state.objects == oid
        if np.all(~np.isin(state.terrain[cells], WATER_IDS)):
            return (('Panneau de chantier', 'Construction sign') if oid == 112
                    else ('Piquet de chantier', 'Construction stake'))
        return (f'Objet runtime {oid} — chantier sur terre, autre contexte inconnu',
                f'Runtime object {oid} — construction on land, other context unknown')
    if oid in (111, 114):
        return (f'Objet runtime {oid} — inconnu', f'Runtime object {oid} — unknown')
    if 128 <= oid <= 207:
        variant = (oid - 128) % 8
        if variant in (0, 1, 2, 3, 4, 6):
            return (f'Arbre en cours d’abattage — phase {(oid - 128) // 8 + 1}',
                    f'Tree being felled — phase {(oid - 128) // 8 + 1}')
        return (f'Objet runtime {oid} — non confirmé', f'Runtime object {oid} — unconfirmed')
    return None
