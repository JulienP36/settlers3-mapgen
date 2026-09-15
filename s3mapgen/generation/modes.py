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
        'Générateur Legacy natif v1.'
    ),
    'upgraded': GenerationMode(
        'upgraded', 'Upgraded', True,
        'Preset amélioré accumulant toutes les règles custom validées du projet.'
    ),
    'custom': GenerationMode(
        'custom', 'Custom', True,
        'Profil déclaratif dérivé d’un moteur intégré ; paramètres et diagnostics explicites.'
    ),
}

MODE_ORDER = ('legacy', 'upgraded', 'custom')

# Cache revisions are part of the application contract: changing the active
# implementation must never make a result produced by an older engine look
# like a hit for the new one.
LEGACY_CACHE_ENGINE_REVISION = 'continental_legacy_native_content'
UPGRADED_CACHE_ENGINE_REVISION = 'continental_upgraded-native-v1'
FALLBACK_CACHE_ENGINE_REVISION = 'unsupported-generation-v1'


def cache_engine_revision(
    mode: str,
    archetype: str,
    configuration_digest: str | None = None,
) -> str:
    """Return the cache namespace for the selected implementation."""

    if mode == 'legacy' and archetype == 'continental':
        return LEGACY_CACHE_ENGINE_REVISION
    if mode == 'upgraded' and archetype == 'continental':
        return UPGRADED_CACHE_ENGINE_REVISION
    if mode == 'custom':
        digest = str(configuration_digest or '').strip()
        return f'custom-v1:{digest}' if digest else 'custom-v1'
    return FALLBACK_CACHE_ENGINE_REVISION

def get_mode(key: str) -> GenerationMode:
    try:
        return MODES[key]
    except KeyError as exc:
        raise ValueError(f'Mode inconnu: {key}') from exc
