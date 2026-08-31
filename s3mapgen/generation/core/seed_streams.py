"""Sous-flux pseudo-aléatoires stables et indépendants par étape."""

from __future__ import annotations

import hashlib

import numpy as np


class SeedStreams:
    """Dérive un générateur NumPy déterministe pour chaque nom d'étape.

    L'ajout ou la modification d'une étape ne décale jamais les tirages des
    autres étapes, contrairement à une unique suite de nombres aléatoires.
    """

    def __init__(self, seed: int) -> None:
        self.seed = seed

    def value(self, stage: str) -> int:
        if not stage or not isinstance(stage, str):
            raise ValueError("Chaque sous-flux doit avoir un nom non vide")
        payload = f"settlers3-mapgen/v2/{self.seed}/{stage}".encode("utf-8")
        return int.from_bytes(hashlib.blake2b(payload, digest_size=16).digest(), "little")

    def rng(self, stage: str) -> np.random.Generator:
        return np.random.default_rng(self.value(stage))
