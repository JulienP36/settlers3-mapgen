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
    832: 20,
    896: 20,
    960: 20,
    1024: 20,
}

NATIVE_GAME_MIN_SIDE = 384
NATIVE_GAME_MAX_SIDE = 768
EDITOR_EXTENDED_SIDES = (832, 896, 960, 1024)


def native_size_warning_kind(side: int) -> str | None:
    """Return the neutral viability warning category for a supported size."""

    side = int(side)
    if side < NATIVE_GAME_MIN_SIDE:
        return "small"
    if side > NATIVE_GAME_MAX_SIDE:
        return "extended"
    return None


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
