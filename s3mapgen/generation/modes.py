from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GenerationMode:
    key: str
    label: str
    implemented: bool
    description: str

MODES = {
    'legacy': GenerationMode(
        'legacy', 'Legacy', False,
        'Reconstruction native en cours ; le générateur DEV_1 a été retiré.'
    ),
    'upgraded': GenerationMode(
        'upgraded', 'Upgraded', True,
        'Preset amélioré accumulant toutes les règles custom validées du projet.'
    ),
    'custom': GenerationMode(
        'custom', 'Custom', False,
        'Paramètres utilisateur exposés manuellement ; validations conservées, risque explicite.'
    ),
}

MODE_ORDER = ('legacy', 'upgraded', 'custom')

def get_mode(key: str) -> GenerationMode:
    try:
        return MODES[key]
    except KeyError as exc:
        raise ValueError(f'Mode inconnu: {key}') from exc
