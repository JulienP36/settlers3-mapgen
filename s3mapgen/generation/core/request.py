"""Contrat d'entrée commun aux nouveaux générateurs.

Les limites joueurs sont natives et restent indépendantes de toute interface.
"""

from __future__ import annotations

from dataclasses import dataclass


NATIVE_PLAYER_LIMITS: dict[int, int] = {
    256: 4,
    320: 6,
    384: 8,
    448: 11,
    512: 15,
    576: 19,
    640: 20,
    704: 20,
    768: 20,
}

NATIVE_GAME_MIN_SIDE = 384
NATIVE_GAME_MAX_SIDE = 768


def native_size_warning_kind(side: int) -> str | None:
    """Return the neutral viability warning category for a supported size."""

    side = int(side)
    if side < NATIVE_GAME_MIN_SIDE:
        return "small"
    return None


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Demande immuable adressée à un générateur concret.

    Le champ ``modifiers`` est réservé ; aucun générateur ne les interprète
    encore et les valeurs non vides sont refusées.
    """

    side: int
    players: int
    seed: int
    modifiers: tuple[str, ...] = ()
    start_algorithm: str = "auto"
    start_nations: tuple[int, ...] = ()
    start_slot_types: tuple[int, ...] = ()
    player_teams: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.side not in NATIVE_PLAYER_LIMITS:
            supported = ", ".join(map(str, NATIVE_PLAYER_LIMITS))
            raise ValueError(f"Taille non prise en charge : {self.side} (tailles natives : {supported})")
        maximum = NATIVE_PLAYER_LIMITS[self.side]
        if not 2 <= self.players <= maximum:
            raise ValueError(
                f"Nombre de joueurs invalide pour {self.side}×{self.side} : "
                f"{self.players} (2 à {maximum})"
            )
        if not isinstance(self.seed, int):
            raise TypeError("La seed doit être un entier")
        from ..start_algorithms import check_start_algorithm
        check_start_algorithm(self.start_algorithm)
        if self.start_algorithm == 'classic':
            if self.start_slot_types and (len(self.start_slot_types)!=self.players or any(t not in (1,2) for t in self.start_slot_types)):
                raise ValueError('Classique : types de slots natifs 1 ou 2 requis')
        if (self.start_nations or self.start_algorithm == 'classic') and (
            len(self.start_nations) != self.players
            or any(type(n) is not int or n not in (0,1,2,3,255) for n in self.start_nations)
        ):
            raise ValueError('Départs : choisir une nation (0..3) ou Choisir (255) pour chaque joueur')
        if self.player_teams and (len(self.player_teams) != self.players or any(type(t) is not int or not 0 <= t <= 20 for t in self.player_teams)):
            raise ValueError("Équipes : une valeur entière de 0 à 20 par joueur requise")
        if self.modifiers:
            raise ValueError("Les modificateurs ne sont pas encore disponibles")
