"""Contrat d'entrée commun aux nouveaux générateurs.

Les limites joueurs sont natives et restent indépendantes de toute interface.
"""

from __future__ import annotations

from dataclasses import dataclass


NATIVE_PLAYER_LIMITS: dict[int, int] = {
    384: 8,
    448: 11,
    512: 15,
    576: 19,
    640: 20,
    704: 20,
    768: 20,
}


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Demande immuable adressée à un générateur concret.

    Les modificateurs ne sont pas encore interprétés : leur emplacement est
    réservé dans le contrat afin d'éviter une future rupture d'API.
    """

    side: int
    players: int
    seed: int
    modifiers: tuple[str, ...] = ()

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
        if self.modifiers:
            raise ValueError("Les modificateurs ne sont pas encore disponibles")
