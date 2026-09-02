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
        'legacy', 'Legacy', True,
        'Reconstruction native Legacy v1.'
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

# Cache revisions are part of the application contract: changing the active
# implementation must never make a result produced by an older engine look
# like a hit for the new one.
LEGACY_CACHE_ENGINE_REVISION = 'continental_legacy_native_content'
UPGRADED_CACHE_ENGINE_REVISION = 'continental_upgraded-native-v1'
FALLBACK_CACHE_ENGINE_REVISION = 'v1.5-stable'


def cache_engine_revision(mode: str, archetype: str) -> str:
    """Return the cache namespace for the selected implementation."""

    if mode == 'legacy' and archetype == 'continental':
        return LEGACY_CACHE_ENGINE_REVISION
    if mode == 'upgraded' and archetype == 'continental':
        return UPGRADED_CACHE_ENGINE_REVISION
    return FALLBACK_CACHE_ENGINE_REVISION

def get_mode(key: str) -> GenerationMode:
    try:
        return MODES[key]
    except KeyError as exc:
        raise ValueError(f'Mode inconnu: {key}') from exc
