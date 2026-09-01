from __future__ import annotations

import heapq
import math
import numpy as np
from scipy import ndimage

from ..map_data.constants import WATER_IDS, ROCKY, ROCK_SNOW_TRANS, SNOW_TRANS, SNOW, HEX6
from .contracts import GenerationOutput
from .continental import UpgradedGenerator as _AuditedMapGenerator
from ..map_data.hexgrid import neighbor_count


_HEX_STRUCTURE = np.array([[1,1,0],[1,1,1],[0,1,1]], dtype=bool)


def _hex_neighbors(x: int, y: int, w: int, h: int):
    for dx, dy in HEX6:
        X, Y = x + dx, y + dy
        if 0 <= X < w and 0 <= Y < h:
            yield X, Y


def _make_blob_sizes(total, n, rng, pr, min_size=18, max_size=105):
    """Canonical v7 elementary-blob size distribution."""
    total = int(total)
    if total <= 0:
        return []
    n = max(1, min(int(n), total // max(1, int(min_size))))
    mean = total / n
    raw = rng.lognormal(mean=math.log(max(5, mean)) - 0.10, sigma=.34, size=n)
    raw = np.clip(raw, min_size, max_size)
    sizes = np.rint(raw / raw.sum() * total).astype(int)
    sizes = np.clip(sizes, min_size, max_size)
    diff = total - int(sizes.sum())
    while diff:
        i = pr.randrange(n)
        if diff > 0 and sizes[i] < max_size:
            sizes[i] += 1; diff -= 1
        elif diff < 0 and sizes[i] > min_size:
            sizes[i] -= 1; diff += 1
    return sorted(map(int, sizes), reverse=True)


def _grow_ovoid_no_gap(region_mask, occupied, target_size, aspect, angle, rng, pr):
    """Canonical v7 solid connected mildly-ovoid blob, with no forced moat."""
    h, w = region_mask.shape
    available = region_mask & ~occupied
    cand = np.argwhere(available)
    if len(cand) == 0:
        return None

    for _ in range(180):
        y0, x0 = map(int, cand[pr.randrange(len(cand))])
        b = math.sqrt(target_size / (math.pi * aspect))
        a = b * aspect
        ca, sa = math.cos(angle), math.sin(angle)

        def priority(x, y):
            dx = x - x0; dy = y - y0
            u = ca * dx + sa * dy
            v = -sa * dx + ca * dy
            return (u / (a + 1e-6)) ** 2 + (v / (b + 1e-6)) ** 2 + 0.045 * math.sin(.52*u + .29*v)

        heap = [(0.0, x0, y0)]
        seen = {(x0, y0)}
        chosen = []
        while heap and len(chosen) < target_size:
            _, x, y = heapq.heappop(heap)
            if not available[y, x]:
                continue
            chosen.append((x, y))
            for nx, ny in _hex_neighbors(x, y, w, h):
                if (nx, ny) in seen:
                    continue
                seen.add((nx, ny))
                if available[ny, nx]:
                    heapq.heappush(heap, (priority(nx, ny), nx, ny))

        if len(chosen) < target_size:
            continue

        xs = [x for x, y in chosen]; ys = [y for x, y in chosen]
        sub = np.zeros((max(ys)-min(ys)+1, max(xs)-min(xs)+1), bool)
        for x, y in chosen:
            sub[y-min(ys), x-min(xs)] = True
        if (ndimage.binary_fill_holes(sub, structure=_HEX_STRUCTURE) & ~sub).any():
            continue
        if target_size / sub.size < 0.32:
            continue
        return chosen
    return None


class MapGenerator(_AuditedMapGenerator):
    """Application facade while the native Legacy engine is rebuilt.

    DEV_2 deliberately exposes only the validated Upgraded path. The previous
    Legacy v2 procedural pipeline and the obsolete v1.5 Legacy path are no
    longer reachable through the application facade.
    """

    def generate(
        self,
        players: int,
        seed: int,
        mode: str = 'upgraded',
        archetype: str = 'continental',
        side: int = 768,
        progress_callback=None,
    ) -> GenerationOutput:
        """Generate through the mode-specific engine with one app contract."""

        if mode != 'upgraded':
            raise NotImplementedError(
                'La génération Legacy est désactivée pendant sa reconstruction native DEV_2; '
                'seul le chemin Upgraded validé est conservé.'
            )

        if int(side) != 768:
            raise ValueError('Le chemin Upgraded historique reste calibré pour 768×768')

        previous_callback = self.progress_callback
        if progress_callback is not None:
            self.progress_callback = progress_callback
        try:
            return super().generate(
                int(players),
                int(seed),
                archetype=archetype,
            )
        finally:
            self.progress_callback = previous_callback

    def _generate_minerals(self, state, rng, pr):
        T, R = state.terrain, state.resources
        R[:] = 0
        cfg = self.profile['minerals']

        # Terrain34 is a valid internal Rocky variant and may carry ore.
        support = np.isin(T, [ROCKY, 34, ROCK_SNOW_TRANS, SNOW_TRANS, SNOW])
        support_cells = int(support.sum())
        occupancy = float(cfg.get('rocky_accessible_occupancy_target', .90))
        target_total = int(round(support_cells * occupancy))
        if target_total > support_cells:
            raise RuntimeError(f'Mineral target exceeds support: {target_total}/{support_cells}')

        families = {int(k): v for k, v in cfg['families'].items()}
        shares = {int(k): float(v) for k, v in cfg.get('shares', {}).items()}
        if not shares:
            original_total = sum(int(v['cells']) for v in families.values())
            shares = {fam: int(v['cells']) / original_total for fam, v in families.items()}
        norm = sum(shares.values())
        order = list(families)
        targets = {}
        used = 0
        for fam in order[:-1]:
            targets[fam] = int(round(target_total * shares[fam] / norm)); used += targets[fam]
        targets[order[-1]] = target_total - used

        occupied = np.zeros_like(support, bool)
        placed_by_family = {}
        blob_counts = {}
        for fam in order:
            fcfg = families[fam]
            original_cells = max(1, int(fcfg['cells']))
            original_blobs = max(1, int(fcfg['blobs']))
            requested_blobs = max(1, round(targets[fam] * original_blobs / original_cells))
            sizes = _make_blob_sizes(
                targets[fam], requested_blobs, rng, pr,
                int(cfg.get('blob_size_min', 18)), int(cfg.get('blob_size_max', 105)),
            )

            family_cells = 0
            family_blobs = 0
            for size in sizes:
                cells = None
                # Caller-side orientation/aspect variation from the validated v7 profile.
                for _ in range(48):
                    aspect = 1.05 + pr.random() * 0.70
                    angle = pr.random() * math.pi
                    cells = _grow_ovoid_no_gap(support, occupied, size, aspect, angle, rng, pr)
                    if cells is not None:
                        break
                if cells is None:
                    raise RuntimeError(
                        f'Canonical v7 blob placement failed for family {fam:#x}, size={size}, '
                        f'occupied={int(occupied.sum())}/{target_total}'
                    )

                q0 = rng.integers(1, 16, len(cells), dtype=np.uint8)
                q1 = np.minimum(
                    int(cfg['quantity_cap']),
                    np.floor(q0.astype(float) * float(cfg['quantity_multiplier']) + 0.5),
                ).astype(np.uint8)
                for (x, y), q in zip(cells, q1):
                    R[y, x] = fam | int(q)
                    occupied[y, x] = True
                family_cells += len(cells)
                family_blobs += 1

            if family_cells != targets[fam]:
                raise RuntimeError(f'v7 family target mismatch {fam:#x}: {family_cells}/{targets[fam]}')
            placed_by_family[fam] = family_cells
            blob_counts[fam] = family_blobs

        state.metadata['upgraded_mineral_target_total'] = target_total
        state.metadata['upgraded_mineral_targets'] = {f'{k:02x}': int(v) for k, v in targets.items()}
        state.metadata['upgraded_mineral_support_cells'] = support_cells
        state.metadata['upgraded_mineral_occupancy_target'] = occupancy
        state.metadata['upgraded_mineral_geometry'] = 'v7_nogap_canonical_ovoid'
        state.metadata['upgraded_mineral_elementary_blobs'] = {f'{k:02x}': int(v) for k, v in blob_counts.items()}
        self.log(
            'resources.minerals_v7_nogap',
            f'canonical_ovoid cells={target_total} support={support_cells} blobs={blob_counts}',
        )

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
            (xx >= margin) & (yy >= margin)
            & (xx < self.side - margin) & (yy < self.side - margin)
        )
        bad = np.argwhere(reef_mask & ~edge_safe)
        if not len(bad):
            return

        water = np.isin(T, WATER_IDS)
        eligible = (T == 7) & (neighbor_count(~water) == 0) & (O == 0) & edge_safe
        destinations = np.argwhere(eligible)
        if len(destinations) < len(bad):
            raise RuntimeError(
                f'Not enough edge-safe deep-water cells to relocate reefs: {len(destinations)}/{len(bad)}'
            )

        chosen = rng.choice(len(destinations), len(bad), replace=False)
        moved_ids = []
        for y, x in bad:
            y = int(y); x = int(x)
            moved_ids.append(int(O[y, x])); O[y, x] = 0; A[y, x] = 0
        for oid, idx in zip(moved_ids, chosen):
            y, x = map(int, destinations[int(idx)]); O[y, x] = oid; A[y, x] = 1
        self.log('objects.reef_edge_margin', f'margin={margin} relocated={len(bad)} target={reef_target}')

    def validate(self, state):
        out = super().validate(state)
        margin = max(0, int(self.profile['decor'].get('reef_edge_margin', 0)))
        if margin <= 0:
            return out

        O = state.objects
        reef = (O >= 111) & (O <= 114)
        yy, xx = np.mgrid[0:self.side, 0:self.side]
        bad = int(np.count_nonzero(
            reef & ((xx < margin) | (yy < margin) | (xx >= self.side-margin) | (yy >= self.side-margin))
        ))
        from .rules import ValidationResult
        out.append(ValidationResult('REEF_EDGE_MARGIN', bad == 0, f'bad={bad}, margin={margin}'))
        return out
