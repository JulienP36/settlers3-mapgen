from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np

from .binary import read_area


@dataclass(frozen=True)
class MorphologyTemplate:
    terrain: np.ndarray
    height: np.ndarray
    source: str
    archetype: str


class UpgradedMorphologyLibrary:
    """Runtime abstraction for Upgraded macro morphology.

    NPZ is the target reusable format. During migration, an EDM checkpoint may
    still be supplied; only its terrain and height are extracted here so the
    generation engine itself no longer depends on EDM semantics.
    """

    def __init__(self, path: Path | str, archetype: str = 'continental'):
        self.path = Path(path)
        if self.path.suffix.lower() == '.npz':
            data = np.load(self.path, allow_pickle=False)
            self.terrain = np.asarray(data['terrain'], dtype=np.uint8)
            self.height = np.asarray(data['height'], dtype=np.uint8)
            self.sources = np.asarray(data['source']).astype(str)
            self.archetypes = np.asarray(data['archetype']).astype(str)
        else:
            state = read_area(self.path)
            self.terrain = state.terrain[None, ...].astype(np.uint8, copy=True)
            self.height = state.height[None, ...].astype(np.uint8, copy=True)
            self.sources = np.asarray([self.path.name])
            self.archetypes = np.asarray([archetype])

        if self.terrain.ndim != 3 or self.height.shape != self.terrain.shape:
            raise ValueError('Invalid Upgraded morphology library array shapes')
        n, h, w = self.terrain.shape
        if h != w:
            raise ValueError('Upgraded morphology templates must be square')
        if len(self.sources) != n or len(self.archetypes) != n:
            raise ValueError('Upgraded morphology metadata length mismatch')
        self.side = int(w)

    def indices_for(self, archetype: str) -> list[int]:
        key = str(archetype).strip().lower()
        return [i for i, value in enumerate(self.archetypes)
                if value.strip().lower() == key]

    def get(self, index: int) -> MorphologyTemplate:
        return MorphologyTemplate(
            terrain=self.terrain[index].copy(),
            height=self.height[index].copy(),
            source=str(self.sources[index]),
            archetype=str(self.archetypes[index]),
        )

    def save_npz(self, output: Path | str) -> Path:
        output = Path(output)
        np.savez_compressed(
            output,
            terrain=self.terrain,
            height=self.height,
            source=self.sources,
            archetype=self.archetypes,
            side=np.asarray([self.side], dtype=np.int32),
        )
        return output
