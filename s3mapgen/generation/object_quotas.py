"""Terrain-supported object quotas; never consumes a generation RNG stream.

Reference: median of five R1 Continental 768/12P maps, before global objects,
excluding fixed start reservations and map borders. Native routines keep their
attempt budgets; this module is for semantic object quotas only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import math

import numpy as np

REFERENCE_SIDE = 768
REFERENCE_SEEDS = (42, 2026101010, 2026101011, 984499091, 1241516019)
REFERENCE_TERRAIN_CELLS = {0: 8051, 1: 7438, 2: 6737, 3: 6174, 4: 5720, 5: 5361, 6: 5056, 7: 66023, 16: 305350, 17: 7751, 18: 141, 19: 131, 20: 6334, 21: 1944, 24: 15178, 32: 67654, 33: 6810, 34: 33, 35: 3006, 48: 17408, 64: 12983, 65: 4040, 80: 101, 81: 536, 96: 3384, 97: 574, 98: 80, 99: 22, 112: 18, 128: 8905, 129: 2404}
MODEL = "compatible_terrain_density_v1"


def support_reference(ids) -> int:
    return sum(REFERENCE_TERRAIN_CELLS.get(int(t), 0) for t in set(ids))


def density_target(reference_quota, support_cells, reference_cells, percent=100.0, *, seed=0, channel="") -> int:
    """Seeded fractional rounding keeps rare objects without a forced minimum."""
    if support_cells <= 0 or reference_quota <= 0 or percent <= 0:
        return 0
    if reference_cells <= 0:
        raise ValueError("Aucune référence de support pour ce quota d’objets")
    expected = float(reference_quota) * int(support_cells) / int(reference_cells) * float(percent) / 100.0
    if not math.isfinite(expected):
        raise ValueError("Quota d’objets non fini")
    whole = math.floor(expected)
    fraction = expected - whole
    token = hashlib.sha256(f"mapgen-object-quota-v1:{int(seed)}:{channel}".encode()).digest()
    uniform = int.from_bytes(token[:8], "big") / 2**64
    return whole + int(uniform < fraction)


@dataclass
class ObjectQuotaBasis:
    cells: tuple[int, ...]
    seed: int = 0
    records: dict = field(default_factory=dict)
    side: int = REFERENCE_SIDE
    terrain_scaled: bool = True

    @classmethod
    def capture(cls, state, excluded=None, *, terrain_scaled=True):
        available = np.ones(state.terrain.shape, dtype=bool)
        if excluded is not None:
            available &= ~np.asarray(excluded, dtype=bool)
        available[[0, -1], :] = False
        available[:, [0, -1]] = False
        cells = tuple(map(int, np.bincount(state.terrain[available], minlength=256)))
        seed = int(state.metadata.get("seed", state.metadata.get("native_rng_input", 0)))
        basis = cls(cells, seed, side=state.side, terrain_scaled=bool(terrain_scaled))
        state.metadata["object_quota_basis"] = {
            "model": MODEL, "side": state.side, "seed": seed,
            "support_counts": list(cells), "quotas": basis.records,
            "reference_side": REFERENCE_SIDE, "terrain_scaled": basis.terrain_scaled,
        }
        return basis

    def target(self, quota, ids, percent=100.0, *, channel, reference_ids=None):
        ids = tuple(sorted(set(map(int, ids))))
        reference_ids = ids if reference_ids is None else tuple(sorted(set(map(int, reference_ids))))
        support = sum(self.cells[t] for t in ids)
        reference = support_reference(reference_ids)
        target = (density_target(quota, support, reference, percent, seed=self.seed, channel=channel)
                  if self.terrain_scaled else max(0, round(float(quota) * (self.side / REFERENCE_SIDE)**2 * float(percent) / 100)))
        self.records[channel] = {
            "support_ids": list(ids), "support_cells": support,
            "reference_ids": list(reference_ids), "reference_cells": reference,
            "reference_quota": float(quota), "percent": float(percent),
            "requested": target, "basis": "compatible_terrain" if self.terrain_scaled else "map_area",
        }
        return target


def quota_geometry_signature(config) -> str:
    import json
    from copy import deepcopy
    value = deepcopy(config.to_dict())
    value["sections"] = config.semantic_sections()
    for field in ("profile", "sections"):
        for name in ("trees", "building_stones", "decor", "decorations"):
            value.get(field, {}).pop(name, None)
    value.get("sections", {}).get("objects", {}).pop("terrain_scaled_quotas", None)
    legacy = value.get("profile", {}).get("legacy_content", {})
    for name in ("trees", "building_stones", "native_objects"):
        legacy.pop(name, None)
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def quota_preview_input(players, seed, teams=(), nations=(), start_algorithm="auto", mirror_mode=0, random_team_count=2):
    return {"players": int(players), "seed": int(seed),
            "teams": list(teams or (0,) * int(players)),
            "nations": list(nations or (255,) * int(players)),
            "start_algorithm": str(start_algorithm), "mirror_mode": int(mirror_mode),
            "random_team_count": int(random_team_count) if -1 in teams else 2}


def estimate_stone_quota(config, side, quota, percent, *, state=None, inputs=None, expanded_grass=False):
    """Use matching terrain data, otherwise explicitly return a reference estimate."""
    from ..map_data.constants import GRASS, GRASS_IDS
    if not config.semantic_sections().get("objects", {}).get("terrain_scaled_quotas", True):
        requested = max(0, round(float(quota) * (int(side) / REFERENCE_SIDE)**2 * float(percent) / 100))
        return requested, "area", int(side)**2
    ids = GRASS_IDS if expanded_grass else (GRASS,)
    reference = support_reference((GRASS,))
    basis = (state.metadata.get("object_quota_basis", {}) if state is not None else {})
    matching = (state is not None and state.side == int(side) and basis.get("model") == MODEL
                and state.metadata.get("object_quota_geometry_signature") == quota_geometry_signature(config)
                and inputs is not None and state.metadata.get("object_quota_inputs") == inputs)
    if matching:
        counts = basis["support_counts"]
        support = sum(counts[t] for t in ids)
        requested = density_target(quota, support, reference, percent, seed=basis["seed"], channel="stones.anchors")
        return requested, "current", support
    # Unknown geometry has a declared reference, never a stale map's support.
    support = support_reference(ids) * (int(side) / REFERENCE_SIDE) ** 2
    requested = round(float(quota) * support / reference * float(percent) / 100.0)
    return requested, "reference", round(support)
