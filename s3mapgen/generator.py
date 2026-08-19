from __future__ import annotations
from collections import deque
from pathlib import Path
import numpy as np

from .engine import MapGenerator as _BaseMapGenerator
from .model import MapState
from .morphology import ArchetypeMorphologyLibrary
from .constants import *
from .hexgrid import hex_distance, neighbor_count, component_labels


# Native 768 mean targets for non-resource cosmetic families shared by both modes.
# IDs 1..28 are handled separately because Upgraded deliberately reduces them.
_NATIVE_GRASS_DECOR_TARGETS = {
    34: 32,
    35: 28, 36: 28, 37: 31,
    38: 30, 39: 30, 40: 29,
    41: 28, 42: 35,
    50: 31, 51: 31, 52: 26,
    53: 30, 54: 33, 55: 27, 56: 27,
    57: 29, 58: 28, 59: 28, 60: 30, 61: 26,
}
_NATIVE_WRECK_TARGETS = {29: 1, 30: 2, 31: 1, 32: 1, 33: 2}


class MapGenerator(_BaseMapGenerator):
    """App-facing generator with mode-independent morphology and audited rules.

    Macro geography is shared by Legacy and Upgraded. Legacy preserves native
    generator behaviour except for stability/format/start fixes; Upgraded starts
    from that base and applies the explicitly validated gameplay improvements.
    """

    def __init__(
        self,
        profile_path: Path | str,
        native_library_path: Path | str,
        upgraded_profile_path: Path | str | None = None,
        upgraded_morphology_source_path: Path | str | None = None,
        progress_callback=None,
    ):
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

    # ---------- common morphology ----------
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

        terrain34_count = int(np.count_nonzero(t == 34))
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
        state.metadata['terrain34_preserved'] = terrain34_count
        self.log(
            'morphology.archetype_library',
            f'continental template={idx} transform={transform} terrain34_preserved={terrain34_count}'
        )
        return state

    def _morphology_from_native(self, rng, pr) -> MapState:
        return self._continental_morphology(pr)

    def _morphology_from_upgraded_reference(self, rng, pr) -> MapState:
        return self._continental_morphology(pr)

    # ---------- audited hydrology split ----------
    def _cleanup_micro_water(self, state, rng):
        if self.current_mode == 'legacy':
            self.log('hydrology.micro_water_cleanup', 'legacy=native components preserved')
            return
        return super()._cleanup_micro_water(state, rng)

    def _cleanup_rivers(self, state):
        if self.current_mode == 'legacy':
            self.log('hydrology.river_cleanup', 'legacy=native paths preserved')
            return

        cfg = self.profile['river']
        old_cap = cfg['practical_max_cells']
        cap = int(round(
            float(cfg.get('p99_scale_slope', 0.0245)) * self.side
            + float(cfg.get('p99_scale_intercept', 34.7))
        ))
        cfg['practical_max_cells'] = cap
        try:
            return super()._cleanup_rivers(state)
        finally:
            cfg['practical_max_cells'] = old_cap

    # ---------- audited biome split ----------
    def _place_start_swamps(self, state, rng, pr):
        if self.current_mode == 'legacy':
            self.log('biomes.start_mini_swamps', 'legacy=disabled')
            return
        return super()._place_start_swamps(state, rng, pr)

    def _rebuild_snow(self, state, rng):
        # Terrain34 is a rare Rocky variant, not a Snow transition. Temporarily
        # treat valid 34 cells as Rocky while computing massif depth, then restore
        # only those that remain true Rocky-internal singletons after Snow rebuild.
        T = state.terrain
        old34 = (T == 34)
        T[old34] = ROCKY
        super()._rebuild_snow(state, rng)

        for y, x in np.argwhere(old34):
            y = int(y); x = int(x)
            if T[y, x] != ROCKY:
                continue
            valid = True
            for dx, dy in HEX6:
                X, Y = x + dx, y + dy
                if not (0 <= X < self.side and 0 <= Y < self.side and T[Y, X] == ROCKY):
                    valid = False
                    break
            if valid:
                T[y, x] = 34

    # ---------- audited mineral split ----------
    def _generate_minerals(self, state, rng, pr):
        if self.current_mode != 'upgraded':
            return super()._generate_minerals(state, rng, pr)

        T = state.terrain
        cfg = self.profile['minerals']
        old34 = (T == 34)
        # Base v7 implementation already has the desired no-gap blob geometry;
        # map 34 to Rocky only during placement so it becomes minable too.
        T[old34] = ROCKY
        support = np.isin(T, [ROCKY, ROCK_SNOW_TRANS, SNOW_TRANS, SNOW])
        occupancy = float(cfg.get('rocky_accessible_occupancy_target', 0.90))
        target_total = int(round(int(support.sum()) * occupancy))

        families = {int(k): v for k, v in cfg['families'].items()}
        shares = {int(k): float(v) for k, v in cfg.get('shares', {}).items()}
        if not shares:
            total_old = sum(int(v['cells']) for v in families.values())
            shares = {k: int(v['cells']) / total_old for k, v in families.items()}
        norm = sum(shares.values())
        order = list(families)
        targets = {}
        used = 0
        for fam in order[:-1]:
            value = int(round(target_total * shares[fam] / norm))
            targets[fam] = value
            used += value
        targets[order[-1]] = target_total - used

        old_values = {}
        for fam, fcfg in families.items():
            old_values[fam] = (fcfg['cells'], fcfg['blobs'])
            old_cells = max(1, int(fcfg['cells']))
            old_blobs = max(1, int(fcfg['blobs']))
            fcfg['cells'] = targets[fam]
            fcfg['blobs'] = max(1, round(targets[fam] * old_blobs / old_cells))

        try:
            super()._generate_minerals(state, rng, pr)
        finally:
            T[old34] = 34
            for fam, fcfg in families.items():
                fcfg['cells'], fcfg['blobs'] = old_values[fam]

        state.metadata['upgraded_mineral_target_total'] = target_total
        state.metadata['upgraded_mineral_targets'] = {f'{k:02x}': int(v) for k, v in targets.items()}
        state.metadata['upgraded_mineral_support_cells'] = int(support.sum())
        state.metadata['upgraded_mineral_occupancy_target'] = occupancy

    # ---------- audited decoration rules ----------
    def _place_decorations(self, state, rng, pr):
        T, O, A = state.terrain, state.objects, state.accessibility
        cfg = self.profile['decor']
        core = self._core_mask(
            state,
            max(self.profile['starts']['technical_clear_hex'],
                self.profile['starts'].get('editor_object_clear_hex', 14))
        )

        def place_exact_on_mask(oid, target, mask, blocking=False, spacing=0):
            if target <= 0:
                return 0
            pts = np.argwhere(mask & ~core & (O == 0))
            if not len(pts):
                return 0
            placed = 0
            for j in rng.permutation(len(pts)):
                if placed >= target:
                    break
                y, x = map(int, pts[j])
                if spacing and not self._obj_clear(state, x, y, spacing):
                    continue
                O[y, x] = oid
                if blocking:
                    A[y, x] = 1
                placed += 1
            return placed

        # Native/common non-blocking Grass decoration.
        common_grass = 0
        for oid, target in _NATIVE_GRASS_DECOR_TARGETS.items():
            common_grass += place_exact_on_mask(oid, target, T == GRASS, False, 0)

        # Native/common sparse Shore wrecks.
        wrecks = 0
        for oid, target in _NATIVE_WRECK_TARGETS.items():
            wrecks += place_exact_on_mask(oid, target, T == SHORE, True, 1)

        # Desert native family, palms are generated in the wood pass.
        desert_pts = np.argwhere(np.isin(T, DESERT_IDS) & ~core & (O == 0))
        desert_target = min(int(cfg.get('desert_target', 30)), len(desert_pts))
        if desert_target:
            for i in rng.choice(len(desert_pts), desert_target, replace=False):
                y, x = map(int, desert_pts[i])
                O[y, x] = pr.choice(cfg['desert_ids'])

        # Swamp content is identical in both modes: Reeds only.
        swamp_pts = np.argwhere(np.isin(T, SWAMP_IDS) & ~core & (O == 0))
        swamp_target = min(int(cfg.get('swamp_target', 60)), len(swamp_pts))
        if swamp_target:
            for i in rng.choice(len(swamp_pts), swamp_target, replace=False):
                y, x = map(int, swamp_pts[i])
                O[y, x] = pr.choice(cfg['swamp_reed_ids'])

        # Decorative stones differ: native quantity in Legacy, /10 in Upgraded.
        stone_target = int(cfg.get('decorative_stone_target', 0))
        stones = place_exact_on_mask(1, 0, T == GRASS)  # initialize for clarity
        stones = 0
        gp = np.argwhere((T == GRASS) & ~core & (O == 0))
        for j in rng.permutation(len(gp)):
            if stones >= stone_target:
                break
            y, x = map(int, gp[j])
            if self._obj_clear(state, x, y, 2):
                O[y, x] = pr.randint(1, 28)
                A[y, x] = 1
                stones += 1

        # Reefs are Upgraded-only; Legacy profile target is exactly zero.
        water = np.isin(T, WATER_IDS)
        deep = np.argwhere((T == 7) & (neighbor_count(~water) == 0) & (O == 0))
        reef_target = min(int(cfg.get('reef_target', 0)), len(deep))
        if reef_target:
            for i in rng.choice(len(deep), reef_target, replace=False):
                y, x = map(int, deep[i])
                O[y, x] = pr.randint(111, 114)
                A[y, x] = 1

        self.log(
            'objects.decorations',
            f'common_grass={common_grass} wrecks={wrecks} desert={desert_target} '
            f'swamp={swamp_target} decor_stones={stones} reefs={reef_target}'
        )

    # ---------- audited wood rules ----------
    def _weighted_adult(self, cfg, pr):
        ids = cfg['adult_ids']
        weights = cfg.get('adult_weights')
        if weights and len(weights) == len(ids):
            return pr.choices(ids, weights=weights, k=1)[0]
        return pr.choice(ids)

    def _place_trees(self, state, rng, pr):
        T, O, A = state.terrain, state.objects, state.accessibility
        cfg = self.profile['trees']
        core = self._core_mask(
            state,
            max(self.profile['starts']['technical_clear_hex'],
                self.profile['starts'].get('editor_object_clear_hex', 14))
        )
        adult_ids = cfg['adult_ids']
        bonus_per_player = int(cfg.get('adult_start_bonus_per_player', 0))
        bonus_total = 0

        # Upgraded-only when bonus_per_player > 0; Legacy profile uses zero.
        for sx, sy in state.starts:
            if bonus_per_player <= 0:
                break
            cand = [
                (x, y)
                for y in range(max(2, sy - 28), min(self.side - 2, sy + 29))
                for x in range(max(2, sx - 28), min(self.side - 2, sx + 29))
                if self.profile['starts'].get('editor_object_clear_hex', 14) + 2
                <= hex_distance(sx, sy, x, y) <= 30
                and T[y, x] == GRASS and O[y, x] == 0
            ]
            pr.shuffle(cand)
            k = 0
            for x, y in cand:
                if k >= bonus_per_player:
                    break
                if self._obj_clear(state, x, y, 2):
                    O[y, x] = self._weighted_adult(cfg, pr)
                    A[y, x] = 1
                    k += 1
                    bonus_total += 1
            if k < bonus_per_player:
                raise RuntimeError(f'Insufficient start forest near {(sx, sy)}: {k}/{bonus_per_player}')

        target = int(cfg['adult_global_target'])
        cluster_target = round(target * float(cfg.get('adult_cluster_share', 0.0)))
        global_adult = 0
        centers = []

        if cluster_target:
            cp = np.argwhere((T == GRASS) & (O == 0) & ~core)
            if len(cp):
                for i in rng.choice(len(cp), min(int(cfg.get('forest_centers', 38)), len(cp)), replace=False):
                    y, x = map(int, cp[i]); centers.append((x, y))
            attempts = 0
            while global_adult < cluster_target and centers and attempts < cluster_target * 80:
                attempts += 1
                cx, cy = centers[int(rng.integers(len(centers)))]
                rad = int(rng.integers(5, 13))
                x = int(np.clip(cx + rng.integers(-rad, rad + 1), 2, self.side - 3))
                y = int(np.clip(cy + rng.integers(-rad, rad + 1), 2, self.side - 3))
                if (hex_distance(cx, cy, x, y) <= rad and T[y, x] == GRASS
                        and O[y, x] == 0 and not core[y, x]
                        and self._obj_clear(state, x, y, 2)):
                    O[y, x] = self._weighted_adult(cfg, pr)
                    A[y, x] = 1
                    global_adult += 1

        pts = np.argwhere((T == GRASS) & (O == 0) & ~core)
        for i in rng.permutation(len(pts)):
            if global_adult >= target:
                break
            y, x = map(int, pts[i])
            if self._obj_clear(state, x, y, 2):
                O[y, x] = self._weighted_adult(cfg, pr)
                A[y, x] = 1
                global_adult += 1
        if global_adult < target:
            raise RuntimeError(f'Adult tree quota not reached: {global_adult}/{target}')

        # Palms are harvestable wood and therefore explicitly quota-controlled.
        palms = 0
        palm_target = int(cfg.get('palm_target', 0))
        palm_ids = cfg.get('palm_ids', [78, 79])
        desert_pts = np.argwhere(np.isin(T, DESERT_IDS) & (O == 0) & ~core)
        for i in rng.permutation(len(desert_pts)):
            if palms >= palm_target:
                break
            y, x = map(int, desert_pts[i])
            if self._obj_clear(state, x, y, 2):
                O[y, x] = pr.choice(palm_ids)
                A[y, x] = 1
                palms += 1
        if palms < palm_target:
            raise RuntimeError(f'Palm quota not reached: {palms}/{palm_target}')

        # SmallTree84 exists only in Upgraded because Legacy target is zero.
        small = 0
        small_target = int(cfg.get('small_tree_target', 0))
        small_cluster = round(small_target * float(cfg.get('small_tree_cluster_share', 0.0)))
        attempts = 0
        while small < small_cluster and centers and attempts < max(1, small_target) * 100:
            attempts += 1
            cx, cy = centers[int(rng.integers(len(centers)))]
            rad = int(rng.integers(5, 13))
            x = int(np.clip(cx + rng.integers(-rad, rad + 1), 2, self.side - 3))
            y = int(np.clip(cy + rng.integers(-rad, rad + 1), 2, self.side - 3))
            if (hex_distance(cx, cy, x, y) <= rad and T[y, x] == GRASS
                    and O[y, x] == 0 and not core[y, x]
                    and self._obj_clear(state, x, y, 2)):
                O[y, x] = cfg['small_tree_id']; A[y, x] = 1; small += 1
        if small_target:
            pts = np.argwhere((T == GRASS) & (O == 0) & ~core)
            for i in rng.permutation(len(pts)):
                if small >= small_target:
                    break
                y, x = map(int, pts[i])
                if self._obj_clear(state, x, y, 2):
                    O[y, x] = cfg['small_tree_id']; A[y, x] = 1; small += 1
            if small < small_target:
                raise RuntimeError(f'SmallTree84 quota not reached: {small}/{small_target}')

        state.metadata['adult_cluster_target'] = cluster_target
        state.metadata['small84_cluster_target'] = small_cluster
        state.metadata['palm_target'] = palm_target
        self.log('objects.adult_trees', f'global={global_adult} bonus={bonus_total} palms={palms} cluster_target={cluster_target}')
        self.log('objects.smalltree84', f'count={small} cluster_target={small_cluster}')

    def _final_accessibility(self, state):
        super()._final_accessibility(state)
        O, A = state.objects, state.accessibility
        full_tree_pool = self.profile['trees']['adult_ids'] + self.profile['trees'].get('palm_ids', [78, 79])
        A[np.isin(O, full_tree_pool + [84])] = 1

    # ---------- validator compatibility with audited mode rules ----------
    def validate(self, state):
        dynamic_targets = state.metadata.get('upgraded_mineral_targets')
        families = {int(k): v for k, v in self.profile['minerals']['families'].items()}
        old_cells = None
        if dynamic_targets:
            old_cells = {fam: fcfg['cells'] for fam, fcfg in families.items()}
            for fam, fcfg in families.items():
                fcfg['cells'] = int(dynamic_targets[f'{fam:02x}'])
        try:
            out = super().validate(state)
        finally:
            if old_cells is not None:
                for fam, fcfg in families.items():
                    fcfg['cells'] = old_cells[fam]

        by_id = {v.rule_id: v for v in out}
        O, T = state.objects, state.terrain
        cfg = self.profile['trees']
        adult_count = int(np.isin(O, cfg['adult_ids']).sum())
        expected_adult = int(cfg['adult_global_target']) + int(cfg.get('adult_start_bonus_per_player', 0)) * len(state.starts)
        if 'ADULT_TREE_QUOTA' in by_id:
            by_id['ADULT_TREE_QUOTA'].passed = (adult_count == expected_adult)
            by_id['ADULT_TREE_QUOTA'].message = f'{adult_count}/{expected_adult}'

        small = int((O == cfg.get('small_tree_id', 84)).sum())
        if 'SMALLTREE84' in by_id:
            by_id['SMALLTREE84'].passed = (small == int(cfg.get('small_tree_target', 0)))
            by_id['SMALLTREE84'].message = f'{small}/{int(cfg.get("small_tree_target", 0))}'

        palms = int(np.isin(O, cfg.get('palm_ids', [78, 79])).sum())
        from .rules import ValidationResult
        out.append(ValidationResult('PALM_QUOTA', palms == int(cfg.get('palm_target', 0)), f'{palms}/{int(cfg.get("palm_target", 0))}'))
        out.append(ValidationResult('PALMS_ON_DESERT', np.count_nonzero(np.isin(O, cfg.get('palm_ids', [78,79])) & ~np.isin(T, DESERT_IDS)) == 0, 'harvestable palms remain on Desert family'))

        if self.current_mode == 'legacy':
            # These validators encode Upgraded cleanup policy, not native legality.
            for rule in ('MICRO_WATER_1_4', 'RIVER_ORPHANS', 'RIVER_STOPS_AT_WATER', 'RIVER_LENGTH_CAP'):
                if rule in by_id:
                    by_id[rule].passed = True
                    by_id[rule].message = 'Legacy native behaviour preserved by audit'

        return out
