from pathlib import Path

import numpy as np
import pytest

from s3mapgen.generation.archetypes.island_detail import add_plain_detail
from s3mapgen.generation.archetypes.large_islands import generate_independent_islands
from s3mapgen.generation.generators.legacy import native_terrain as nt
from s3mapgen.map_data.constants import HEX6

FIXTURE = Path(__file__).parent / 'fixtures/islands_r10/384_8_42_baseline.npz'


def test_island_detail_preserves_validated_geometry_and_mountains(monkeypatch):
    from s3mapgen.generation.archetypes import large_islands
    captured = {}
    original = large_islands.add_plain_detail
    def observe(height, labels, **kwargs):
        captured['baseline'] = height.copy()
        captured['labels'] = labels.copy()
        return original(height, labels, **kwargs)
    monkeypatch.setattr(large_islands, 'add_plain_detail', observe)
    height, actual_labels, report = generate_independent_islands(
        np.zeros((384, 384), np.uint8), players=8, seed=42,
        water_threshold=0, mountain_threshold=140, snow_threshold=190,
        native_relaxation=nt.relax_large_island_height,
    )
    # The source geometry may evolve; the detail pass must preserve the
    # actual relaxed macro field rather than freezing an older preset.
    baseline, labels = captured['baseline'], captured['labels']
    assert np.array_equal(actual_labels, labels)
    assert np.array_equal(height > 0, labels > 0)
    assert np.array_equal(height[baseline >= 130], baseline[baseline >= 130])
    assert report['plain_detail']['changed_cells'] > 0
    # The detail must leave the game's relaxation stable; a different noise
    # realization may not silently move the protected macro relief later.
    relaxed, passes = nt.relax_large_island_height(height)
    relaxed[labels == 0] = 0
    assert passes == 1
    assert np.array_equal(relaxed, height)
    for dr, dc in HEX6:
        a = (slice(max(0, dr), 384 + min(0, dr)), slice(max(0, dc), 384 + min(0, dc)))
        b = (slice(max(0, -dr), 384 + min(0, -dr)), slice(max(0, -dc), 384 + min(0, -dc)))
        old = baseline[a].astype(int) - baseline[b].astype(int)
        new = height[a].astype(int) - height[b].astype(int)
        assert np.all(new <= np.maximum(5, old))
        assert np.all(new >= np.minimum(-5, old))


@pytest.mark.parametrize('shift', [0, 10])
def test_plain_detail_respects_custom_water_and_mountain_thresholds(shift):
    with np.load(FIXTURE) as fixture:
        labels = fixture['labels']
        baseline = fixture['height'].copy()
    baseline[labels > 0] += shift
    height, _ = add_plain_detail(
        baseline, labels, seed=42, water_threshold=shift,
        mountain_threshold=140 + shift,
    )
    assert np.array_equal(height > shift, labels > 0)
    assert np.array_equal(height[baseline >= 130 + shift], baseline[baseline >= 130 + shift])
    repeated, _ = add_plain_detail(
        baseline, labels, seed=42, water_threshold=shift,
        mountain_threshold=140 + shift,
    )
    assert np.array_equal(height, repeated)


def test_detail_reduces_river_footprint_with_unchanged_native_tracer():
    with np.load(FIXTURE) as fixture:
        baseline, labels = fixture['height'], fixture['labels']
    height, _ = add_plain_detail(
        baseline, labels, seed=42, water_threshold=0, mountain_threshold=140,
    )
    counts = []
    for field in (baseline, height):
        grid = nt.NativeTerrainGrid.empty(384)
        nt._initialize_cells(grid)
        grid.height[:] = field
        nt._classify_relief(grid)
        nt._clear_pre_river_fields(grid)
        nt._generate_rivers(grid, nt.NativeRng16(42))
        counts.append(int(np.count_nonzero(np.isin(grid.terrain, (96, 97, 98, 99)))))
    assert counts[1] < counts[0]


@pytest.mark.parametrize("side,players,seed", [(384,8,42), (768,4,2026093006)])
def test_coastal_detail_reduces_coast_occupation_without_large_low_river_components(side,players,seed):
    from s3mapgen.map_data.hexgrid import distance_from,component_labels
    fixture = Path(__file__).parent / f"fixtures/islands_r13/{side}_{players}_{seed}.npz"
    with np.load(fixture) as z:
        base, labels, prior = z["height"], z["labels"], z["r12_height"]
    height, _ = add_plain_detail(base, labels, seed=seed, water_threshold=0, mountain_threshold=140)
    coast = distance_from(labels == 0) == 1
    occupied = []
    for field in (prior, height):
        grid = nt.NativeTerrainGrid.empty(side)
        nt._initialize_cells(grid)
        grid.height[:] = field
        nt._classify_relief(grid)
        nt._clear_pre_river_fields(grid)
        nt._generate_rivers(grid,nt.NativeRng16(seed))
        rivers = np.isin(grid.terrain,(96,97,98,99))
        occupied.append(int((rivers & coast).sum()))
        components,_ = component_labels(rivers & (field <= 2))
        assert max(np.bincount(components.ravel())[1:],default=0) < 64
    assert occupied[1] < occupied[0]
    assert np.array_equal(height[base >= 130],base[base >= 130])
