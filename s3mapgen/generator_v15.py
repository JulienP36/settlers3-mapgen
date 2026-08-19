from __future__ import annotations

import numpy as np

from .constants import WATER_IDS
from .generator import MapGenerator as _AuditedMapGenerator
from .hexgrid import neighbor_count


class MapGenerator(_AuditedMapGenerator):
    """v1.5 runtime generator with final cosmetic safety constraints."""

    def _place_decorations(self, state, rng, pr):
        super()._place_decorations(state, rng, pr)

        cfg = self.profile['decor']
        margin = max(0, int(cfg.get('reef_edge_margin', 0)))
        reef_target = int(cfg.get('reef_target', 0))
        if reef_target <= 0 or margin <= 0:
            return

        T, O, A = state.terrain, state.objects, state.accessibility
        reef_mask = (O >= 111) & (O <= 114)
        yy, xx = np.mgrid[0:self.side, 0:self.side]
        edge_safe = (
            (xx >= margin)
            & (yy >= margin)
            & (xx < self.side - margin)
            & (yy < self.side - margin)
        )
        bad = np.argwhere(reef_mask & ~edge_safe)
        if not len(bad):
            return

        water = np.isin(T, WATER_IDS)
        eligible = (
            (T == 7)
            & (neighbor_count(~water) == 0)
            & (O == 0)
            & edge_safe
        )
        destinations = np.argwhere(eligible)
        if len(destinations) < len(bad):
            raise RuntimeError(
                f'Not enough edge-safe deep-water cells to relocate reefs: '
                f'{len(destinations)}/{len(bad)}'
            )

        chosen = rng.choice(len(destinations), len(bad), replace=False)
        moved_ids = []
        for y, x in bad:
            y = int(y); x = int(x)
            moved_ids.append(int(O[y, x]))
            O[y, x] = 0
            A[y, x] = 0

        for oid, idx in zip(moved_ids, chosen):
            y, x = map(int, destinations[int(idx)])
            O[y, x] = oid
            A[y, x] = 1

        self.log(
            'objects.reef_edge_margin',
            f'margin={margin} relocated={len(bad)} target={reef_target}',
        )

    def validate(self, state):
        out = super().validate(state)
        margin = max(0, int(self.profile['decor'].get('reef_edge_margin', 0)))
        if margin <= 0:
            return out

        O = state.objects
        reef = (O >= 111) & (O <= 114)
        yy, xx = np.mgrid[0:self.side, 0:self.side]
        bad = int(np.count_nonzero(
            reef
            & (
                (xx < margin)
                | (yy < margin)
                | (xx >= self.side - margin)
                | (yy >= self.side - margin)
            )
        ))
        from .rules import ValidationResult
        out.append(ValidationResult(
            'REEF_EDGE_MARGIN',
            bad == 0,
            f'bad={bad}, margin={margin}',
        ))
        return out
