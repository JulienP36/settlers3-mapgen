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


class ArchetypeMorphologyLibrary:
    """Terrain+height templates grouped by map archetype.

    Existing native NPZ libraries are accepted directly. EDM input remains
    supported only as a migration/extraction source for reverse-engineering.
    """

    def __init__(self, path: Path | str, archetype: str = 'continental'):
        self.path = Path(path)
        if self.path.suffix.lower() == '.npz':
            data = np.load(self.path, allow_pickle=True)
            self.terrain = np.asarray(data['terrain'], dtype=np.uint8)
            self.height = np.asarray(data['height'], dtype=np.uint8)
            n = len(self.terrain)
            if 'source' in data.files:
                self.sources = np.asarray(data['source']).astype(str)
            elif 'filenames' in data.files:
                self.sources = np.asarray(data['filenames']).astype(str)
            else:
                self.sources = np.asarray([self.path.name] * n)
            if 'archetype' in data.files:
                self.archetypes = np.asarray(data['archetype']).astype(str)
            else:
                self.archetypes = np.asarray([archetype] * n)
        else:
            state = read_area(self.path)
            self.terrain = state.terrain[None, ...].astype(np.uint8, copy=True)
            self.height = state.height[None, ...].astype(np.uint8, copy=True)
            self.sources = np.asarray([self.path.name])
            self.archetypes = np.asarray([archetype])

        if self.terrain.ndim != 3 or self.height.shape != self.terrain.shape:
            raise ValueError('Invalid morphology library array shapes')
        n, h, w = self.terrain.shape
        if h != w:
            raise ValueError('Morphology templates must be square')
        if len(self.sources) != n or len(self.archetypes) != n:
            raise ValueError('Morphology metadata length mismatch')
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


# Compatibility name used by the migration tool/tests created during v1.4 work.
UpgradedMorphologyLibrary = ArchetypeMorphologyLibrary
