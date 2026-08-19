from __future__ import annotations
from pathlib import Path
import numpy as np

from .engine import MapGenerator as _BaseMapGenerator
from .model import MapState
from .morphology import ArchetypeMorphologyLibrary


class MapGenerator(_BaseMapGenerator):
    """App-facing generator with mode-independent archetype morphology.

    The validated gameplay pipeline remains in engine.MapGenerator. Macro
    geography comes from the archetype library; Legacy/Upgraded only affect
    downstream rules, content and balance.
    """

    def __init__(
        self,
        profile_path: Path | str,
        native_library_path: Path | str,
        upgraded_profile_path: Path | str | None = None,
        upgraded_morphology_source_path: Path | str | None = None,
        progress_callback=None,
    ):
        # Keep the validated base engine's native library/profile setup, but
        # never load the historical Upgraded checkpoint.
        super().__init__(
            profile_path,
            native_library_path,
            upgraded_profile_path,
            None,
            progress_callback=progress_callback,
        )
        self.archetype_morphology = ArchetypeMorphologyLibrary(
            native_library_path, archetype='continental'
        )

    def _continental_morphology(self, pr) -> MapState:
        indices = self.archetype_morphology.indices_for('continental')
        if not indices:
            raise RuntimeError('No Continental morphology templates available')
        idx = indices[pr.randrange(len(indices))]
        base = self.archetype_morphology.get(idx)
        t = base.terrain
        h = base.height
        transform = pr.randrange(4)

        if transform == 1:
            t = np.rot90(t, 2).copy(); h = np.rot90(h, 2).copy()
        elif transform == 2:
            t = t.T.copy(); h = h.T.copy()
        elif transform == 3:
            t = np.rot90(t.T, 2).copy(); h = np.rot90(h.T, 2).copy()

        # Terrain34 is a rare technical Rocky/Snow transition state observed in
        # native runtime/static sources. When imported as a raw morphology
        # template it can survive as isolated visual speckles after our
        # relief-driven Snow rebuild. Normalize it to Rocky before downstream
        # biome reconstruction; the final legal Snow chain is rebuilt later as
        # Rocky32 -> 35 -> 129 -> Snow128.
        residual34 = int(np.count_nonzero(t == 34))
        if residual34:
            t = t.copy()
            t[t == 34] = 32

        state = MapState.empty(self.side)
        state.terrain[:] = t
        state.height[:] = h
        state.objects[:] = 0
        state.resources[:] = 0
        state.accessibility[:] = 0
        state.claim[:] = 255
        state.metadata['archetype_morphology_index'] = int(idx)
        state.metadata['archetype_morphology_source'] = base.source
        state.metadata['archetype_transform'] = transform
        state.metadata['terrain34_normalized'] = residual34
        self.log('morphology.archetype_library', f'continental template={idx} transform={transform} terrain34_normalized={residual34}')
        return state

    def _morphology_from_native(self, rng, pr) -> MapState:
        return self._continental_morphology(pr)

    def _morphology_from_upgraded_reference(self, rng, pr) -> MapState:
        # Base engine still calls this historical hook for Upgraded. Route it
        # to the same Continental archetype source as Legacy.
        return self._continental_morphology(pr)
