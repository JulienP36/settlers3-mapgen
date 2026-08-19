from __future__ import annotations
from pathlib import Path
import numpy as np

from .engine import MapGenerator as _BaseMapGenerator
from .model import MapState
from .morphology import UpgradedMorphologyLibrary


class MapGenerator(_BaseMapGenerator):
    """App-facing generator with pluggable Upgraded morphology.

    The validated generation pipeline remains in engine.MapGenerator. This
    facade changes only how the Upgraded macro terrain+height template is
    supplied, isolating the historical EDM checkpoint behind a reusable
    morphology-library interface.
    """

    def __init__(
        self,
        profile_path: Path | str,
        native_library_path: Path | str,
        upgraded_profile_path: Path | str | None = None,
        upgraded_morphology_source_path: Path | str | None = None,
        progress_callback=None,
    ):
        # Do not let the validated base engine parse/load the old Upgraded EDM.
        super().__init__(
            profile_path,
            native_library_path,
            upgraded_profile_path,
            None,
            progress_callback=progress_callback,
        )
        self.upgraded_morphology = (
            UpgradedMorphologyLibrary(upgraded_morphology_source_path)
            if upgraded_morphology_source_path else None
        )

    def _morphology_from_upgraded_reference(self, rng, pr) -> MapState:
        if self.upgraded_morphology is None:
            raise RuntimeError('Upgraded morphology source is unavailable')

        indices = self.upgraded_morphology.indices_for('continental')
        if not indices:
            raise RuntimeError('No Upgraded Continental morphology template')

        # With the current single validated template this consumes exactly the
        # same PRNG call sequence as v1.4: only transform uses pr.randrange(4).
        idx = indices[0] if len(indices) == 1 else indices[pr.randrange(len(indices))]
        base = self.upgraded_morphology.get(idx)
        state = MapState.empty(self.side)
        t = base.terrain
        h = base.height
        transform = pr.randrange(4)

        if transform == 1:
            t = np.rot90(t, 2).copy(); h = np.rot90(h, 2).copy()
        elif transform == 2:
            t = t.T.copy(); h = h.T.copy()
        elif transform == 3:
            t = np.rot90(t.T, 2).copy(); h = np.rot90(h.T, 2).copy()

        state.terrain[:] = t
        state.height[:] = h
        state.objects[:] = 0
        state.resources[:] = 0
        state.accessibility[:] = 0
        state.claim[:] = 255
        state.metadata['upgraded_morphology_index'] = int(idx)
        state.metadata['upgraded_morphology_source'] = base.source
        state.metadata['upgraded_transform'] = transform
        self.log('morphology.upgraded_library', f'template={idx} transform={transform}')
        return state
