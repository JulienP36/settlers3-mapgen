from __future__ import annotations
from pathlib import Path
import numpy as np

from .engine import MapGenerator as _BaseMapGenerator
from .model import MapState
from .morphology import ArchetypeMorphologyLibrary
from .constants import *
from .hexgrid import hex_distance, neighbor_count
from .rules import ValidationResult


# Native 768 mean targets for cosmetic families shared by Legacy and Upgraded.
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
_MUD_FAMILY = (23, 145, 144)
_YELLOW_GRASS = 24


class MapGenerator(_BaseMapGenerator):
    """App-facing generator implementing the audited Legacy/Upgraded split.

    Macro geography stays shared. Legacy preserves native generator behaviour
    except for required stability/format/start fixes. Upgraded starts from the
    same base and applies only the explicitly validated improvements.
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

    # ---------- shared macro morphology ----------
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

        # Audit: Legacy keeps native Mud and Terrain24. Upgraded deliberately
        # removes both for now; Terrain24 will be reintroduced later in isolation.
        mud_removed = yellow_removed = 0
        if self.current_mode == 'upgraded':
            mud = np.isin(t, _MUD_FAMILY)
            yellow = (t == _YELLOW_GRASS)
            mud_removed = int(mud.sum())
            yellow_removed = int(yellow.sum())
            t[mud | yellow] = GRASS

        terrain34_count = int(np.count_nonzero(t == 34))
        state = MapState.empty(self.side)
        state.terrain[:] = t
        state.height[:] = h
        state.objects[:] = 0
        state.resources[:] = 0
        state.accessibility[:] = 0
        state.claim[:] = 255
        state.metadata.update(
            archetype_morphology_index=int(idx),
            archetype_morphology_source=base.source,
            archetype_transform=transform,
            terrain34_preserved=terrain34_count,
            upgraded_mud_removed=mud_removed,
            upgraded_yellow_grass_deferred=yellow_removed,
        )
        self.log(
            'morphology.archetype_library',
            f'continental template={idx} transform={transform} terrain34={terrain34_count} '
            f'mud_removed={mud_removed} yellow24_deferred={yellow_removed}'
        )
        return state

    def _morphology_from_native(self, rng, pr) -> MapState:
        return self._continental_morphology(pr)

    def _morphology_from_upgraded_reference(self, rng, pr) -> MapState:
        return self._continental_morphology(pr)

    # ---------- hydrology ----------
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
        cfg['practical_max_cells'] = int(round(
            float(cfg.get('p99_scale_slope', 0.0245)) * self.side
            + float(cfg.get('p99_scale_intercept', 34.7))
        ))
        try:
            return super()._cleanup_rivers(state)
        finally:
            cfg['practical_max_cells'] = old_cap

    # ---------- biomes ----------
    def _expand_upgraded_swamps(self, state, rng):
        if self.current_mode != 'upgraded':
            return 0
        T = state.terrain
        family = np.isin(T, SWAMP_IDS)
        initial = int(family.sum())
        target = int(round(initial * 1.30))
        need = max(0, target - initial)
        if not need:
            return 0

        # Keep global swamps separate from the Upgraded start mini-swamp bonus.
        protected = self._core_mask(state, 30)
        grown = 0
        while grown < need:
            frontier = (neighbor_count(family) > 0) & (T == GRASS) & ~protected
            pts = np.argwhere(frontier)
            if not len(pts):
                break
            take = min(need - grown, max(1, min(len(pts), 32)))
            chosen = rng.choice(len(pts), take, replace=False)
            p = pts[chosen]
            T[p[:, 0], p[:, 1]] = GRASS_SWAMP_TRANS
            family[p[:, 0], p[:, 1]] = True
            grown += take
        state.metadata['upgraded_global_swamp_native_cells'] = initial
        state.metadata['upgraded_global_swamp_added_cells'] = grown
        return grown

    def _place_start_swamps(self, state, rng, pr):
        if self.current_mode == 'legacy':
            self.log('biomes.start_mini_swamps', 'legacy=disabled')
            return
        grown = self._expand_upgraded_swamps(state, rng)
        self.log('biomes.global_swamp_upgrade', f'added={grown}')
        return super()._place_start_swamps(state, rng, pr)

    # ---------- Snow / Terrain34 ----------
    def _rebuild_snow(self, state, rng):
        T = state.terrain
        old34 = (T == 34)
        # Treat 34 as Rocky for massif-depth calculations, then restore only
        # legitimate Rocky-internal 34 singletons after the common Snow rebuild.
        T[old34] = ROCKY
        super()._rebuild_snow(state, rng)
        for y, x in np.argwhere(old34):
            y = int(y); x = int(x)
            if T[y, x] != ROCKY:
                continue
            if all(
                0 <= x + dx < self.side and 0 <= y + dy < self.side
                and T[y + dy, x + dx] == ROCKY
                for dx, dy in HEX6
            ):
                T[y, x] = 34

    # ---------- minerals ----------
    def _generate_minerals(self, state, rng, pr):
        if self.current_mode != 'upgraded':
            # Legacy mineral implementation is deliberately left unchanged.
            return super()._generate_minerals(state, rng, pr)

        T = state.terrain
        cfg = self.profile['minerals']
        old34 = (T == 34)
        T[old34] = ROCKY
        support = np.isin(T, [ROCKY, ROCK_SNOW_TRANS, SNOW_TRANS, SNOW])
        occupancy = float(cfg.get('rocky_accessible_occupancy_target', 0.90))
        target_total = int(round(int(support.sum()) * occupancy))

        families = {int(k): v for k, v in cfg['families'].items()}
        shares = {int(k): float(v) for k, v in cfg.get('shares', {}).items()}
        if not shares:
            old_total = sum(int(v['cells']) for v in families.values())
            shares = {k: int(v['cells']) / old_total for k, v in families.items()}
        norm = sum(shares.values())
        order = list(families)
        targets = {}
        used = 0
        for fam in order[:-1]:
            targets[fam] = int(round(target_total * shares[fam] / norm))
            used += targets[fam]
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

    # ---------- decorations ----------
    def _place_decorations(self, state, rng, pr):
        T, O, A = state.terrain, state.objects, state.accessibility
        cfg = self.profile['decor']
        core = self._core_mask(
            state,
            max(self.profile['starts']['technical_clear_hex'],
                self.profile['starts'].get('editor_object_clear_hex', 14))
        )

        def place_on_mask(oid, target, mask, blocking=False, spacing=0):
            pts = np.argwhere(mask & ~core & (O == 0))
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

        common_grass = sum(
            place_on_mask(oid, target, T == GRASS)
            for oid, target in _NATIVE_GRASS_DECOR_TARGETS.items()
        )
        wrecks = sum(
            place_on_mask(oid, target, T == SHORE, True, 1)
            for oid, target in _NATIVE_WRECK_TARGETS.items()
        )

        de = np.argwhere(np.isin(T, DESERT_IDS) & ~core & (O == 0))
        desert_target = min(int(cfg.get('desert_target', 30)), len(de))
        if desert_target:
            for i in rng.choice(len(de), desert_target, replace=False):
                y, x = map(int, de[i]); O[y, x] = pr.choice(cfg['desert_ids'])

        sw = np.argwhere(np.isin(T, SWAMP_IDS) & ~core & (O == 0))
        swamp_target = min(int(cfg.get('swamp_target', 60)), len(sw))
        if swamp_target:
            for i in rng.choice(len(sw), swamp_target, replace=False):
                y, x = map(int, sw[i]); O[y, x] = pr.choice(cfg['swamp_reed_ids'])

        # IDs1..28 are the deliberate Legacy/Upgraded cosmetic-density split.
        stone_target = int(cfg.get('decorative_stone_target', 0))
        stones = 0
        gp = np.argwhere((T == GRASS) & ~core & (O == 0))
        for j in rng.permutation(len(gp)):
            if stones >= stone_target:
                break
            y, x = map(int, gp[j])
            if self._obj_clear(state, x, y, 2):
                O[y, x] = pr.randint(1, 28); A[y, x] = 1; stones += 1

        water = np.isin(T, WATER_IDS)
        deep = np.argwhere((T == 7) & (neighbor_count(~water) == 0) & (O == 0))
        reefs = min(int(cfg.get('reef_target', 0)), len(deep))
        if reefs:
            for i in rng.choice(len(deep), reefs, replace=False):
                y, x = map(int, deep[i]); O[y, x] = pr.randint(111, 114); A[y, x] = 1

        self.log(
            'objects.decorations',
            f'common_grass={common_grass} wrecks={wrecks} desert={desert_target} '
            f'swamp={swamp_target} decor_stones={stones} reefs={reefs}'
        )

    # ---------- wood ----------
    def _weighted_adult(self, cfg, pr):
        ids = cfg['adult_ids']; weights = cfg.get('adult_weights')
        return pr.choices(ids, weights=weights, k=1)[0] if weights else pr.choice(ids)

    def _place_trees(self, state, rng, pr):
        T, O, A = state.terrain, state.objects, state.accessibility
        cfg = self.profile['trees']
        core = self._core_mask(
            state,
            max(self.profile['starts']['technical_clear_hex'],
                self.profile['starts'].get('editor_object_clear_hex', 14))
        )
        bonus_per_player = int(cfg.get('adult_start_bonus_per_player', 0))
        bonus_total = 0

        # Legacy profile uses zero; Upgraded keeps the current bonus until the
        # dedicated post-audit start-bonus recalibration.
        if bonus_per_player:
            for sx, sy in state.starts:
                cand = [
                    (x, y)
                    for y in range(max(2, sy - 28), min(self.side - 2, sy + 29))
                    for x in range(max(2, sx - 28), min(self.side - 2, sx + 29))
                    if self.profile['starts'].get('editor_object_clear_hex', 14) + 2
                    <= hex_distance(sx, sy, x, y) <= 30
                    and T[y, x] == GRASS and O[y, x] == 0
                ]
                pr.shuffle(cand); k = 0
                for x, y in cand:
                    if k >= bonus_per_player:
                        break
                    if self._obj_clear(state, x, y, 2):
                        O[y, x] = self._weighted_adult(cfg, pr); A[y, x] = 1
                        k += 1; bonus_total += 1
                if k < bonus_per_player:
                    raise RuntimeError(f'Insufficient start forest near {(sx, sy)}: {k}/{bonus_per_player}')

        target = int(cfg['adult_global_target'])
        cluster_target = round(target * float(cfg.get('adult_cluster_share', 0.0)))
        global_adult = 0; centers = []
        if cluster_target:
            cp = np.argwhere((T == GRASS) & (O == 0) & ~core)
            if len(cp):
                for i in rng.choice(len(cp), min(int(cfg.get('forest_centers', 38)), len(cp)), replace=False):
                    y, x = map(int, cp[i]); centers.append((x, y))
            attempts = 0
            while global_adult < cluster_target and centers and attempts < cluster_target * 80:
                attempts += 1
                cx, cy = centers[int(rng.integers(len(centers)))]; rad = int(rng.integers(5, 13))
                x = int(np.clip(cx + rng.integers(-rad, rad + 1), 2, self.side - 3))
                y = int(np.clip(cy + rng.integers(-rad, rad + 1), 2, self.side - 3))
                if (hex_distance(cx, cy, x, y) <= rad and T[y, x] == GRASS and O[y, x] == 0
                        and not core[y, x] and self._obj_clear(state, x, y, 2)):
                    O[y, x] = self._weighted_adult(cfg, pr); A[y, x] = 1; global_adult += 1

        pts = np.argwhere((T == GRASS) & (O == 0) & ~core)
        for i in rng.permutation(len(pts)):
            if global_adult >= target:
                break
            y, x = map(int, pts[i])
            if self._obj_clear(state, x, y, 2):
                O[y, x] = self._weighted_adult(cfg, pr); A[y, x] = 1; global_adult += 1
        if global_adult < target:
            raise RuntimeError(f'Adult tree quota not reached: {global_adult}/{target}')

        # Palms are harvestable and now explicitly part of the wood accounting.
        palms = 0; palm_target = int(cfg.get('palm_target', 0)); palm_ids = cfg.get('palm_ids', [78, 79])
        de = np.argwhere(np.isin(T, DESERT_IDS) & (O == 0) & ~core)
        for i in rng.permutation(len(de)):
            if palms >= palm_target:
                break
            y, x = map(int, de[i])
            if self._obj_clear(state, x, y, 2):
                O[y, x] = pr.choice(palm_ids); A[y, x] = 1; palms += 1
        if palms < palm_target:
            raise RuntimeError(f'Palm quota not reached: {palms}/{palm_target}')

        small = 0; small_target = int(cfg.get('small_tree_target', 0))
        small_cluster = round(small_target * float(cfg.get('small_tree_cluster_share', 0.0)))
        attempts = 0
        while small < small_cluster and centers and attempts < max(1, small_target) * 100:
            attempts += 1
            cx, cy = centers[int(rng.integers(len(centers)))]; rad = int(rng.integers(5, 13))
            x = int(np.clip(cx + rng.integers(-rad, rad + 1), 2, self.side - 3))
            y = int(np.clip(cy + rng.integers(-rad, rad + 1), 2, self.side - 3))
            if (hex_distance(cx, cy, x, y) <= rad and T[y, x] == GRASS and O[y, x] == 0
                    and not core[y, x] and self._obj_clear(state, x, y, 2)):
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

        state.metadata.update(
            adult_cluster_target=cluster_target,
            small84_cluster_target=small_cluster,
            palm_target=palm_target,
        )
        self.log('objects.adult_trees', f'global={global_adult} bonus={bonus_total} palms={palms} cluster_target={cluster_target}')
        self.log('objects.smalltree84', f'count={small} cluster_target={small_cluster}')

    def _final_accessibility(self, state):
        super()._final_accessibility(state)
        O, A = state.objects, state.accessibility
        tree_pool = self.profile['trees']['adult_ids'] + self.profile['trees'].get('palm_ids', [78, 79]) + [84]
        A[np.isin(O, tree_pool)] = 1

    # ---------- validators ----------
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
        adults = int(np.isin(O, cfg['adult_ids']).sum())
        expected = int(cfg['adult_global_target']) + int(cfg.get('adult_start_bonus_per_player', 0)) * len(state.starts)
        if 'ADULT_TREE_QUOTA' in by_id:
            by_id['ADULT_TREE_QUOTA'].passed = adults == expected
            by_id['ADULT_TREE_QUOTA'].message = f'{adults}/{expected}'
        small = int((O == cfg.get('small_tree_id', 84)).sum())
        if 'SMALLTREE84' in by_id:
            target = int(cfg.get('small_tree_target', 0))
            by_id['SMALLTREE84'].passed = small == target
            by_id['SMALLTREE84'].message = f'{small}/{target}'

        palms = int(np.isin(O, cfg.get('palm_ids', [78, 79])).sum())
        palm_target = int(cfg.get('palm_target', 0))
        out.append(ValidationResult('PALM_QUOTA', palms == palm_target, f'{palms}/{palm_target}'))
        palm_bad = np.count_nonzero(np.isin(O, cfg.get('palm_ids', [78, 79])) & ~np.isin(T, DESERT_IDS))
        out.append(ValidationResult('PALMS_ON_DESERT', palm_bad == 0, f'bad={palm_bad}'))

        if self.current_mode == 'legacy':
            # These four validators encode Upgraded cleanup policy, not native legality.
            for rule in ('MICRO_WATER_1_4', 'RIVER_ORPHANS', 'RIVER_STOPS_AT_WATER', 'RIVER_LENGTH_CAP'):
                if rule in by_id:
                    by_id[rule].passed = True
                    by_id[rule].message = 'Legacy native behaviour preserved by audit'
        return out
