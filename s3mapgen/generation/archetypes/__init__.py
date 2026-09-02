"""Catalogue des archétypes de carte, indépendant des moteurs d'exécution."""

from __future__ import annotations
from dataclasses import dataclass

from .continental import ContinentalContext, ContinentalV1

@dataclass(frozen=True)
class Archetype:
    key: str
    label: str
    implemented: bool
    description: str

ARCHETYPES = {
    'continental': Archetype(
        'continental', 'Continental', True,
        'Macro-topologie : une masse terrestre principale avec océan périphérique.'
    ),
    'large_islands': Archetype(
        'large_islands', 'Large Islands', False,
        'Macro-topologie : plusieurs grandes masses insulaires.'
    ),
    'small_islands': Archetype(
        'small_islands', 'Small Islands', False,
        'Macro-topologie : nombreuses petites masses insulaires.'
    ),
}

ARCHETYPE_ORDER = ('continental', 'large_islands', 'small_islands')

def get_archetype(key: str) -> Archetype:
    try:
        return ARCHETYPES[key]
    except KeyError as exc:
        raise ValueError(f'Archétype inconnu: {key}') from exc


__all__ = [
    "Archetype",
    "ARCHETYPES",
    "ARCHETYPE_ORDER",
    "get_archetype",
    "ContinentalContext",
    "ContinentalV1",
]
