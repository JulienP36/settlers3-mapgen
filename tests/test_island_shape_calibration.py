"""Island geometry, source shape and bounded work independent of map content."""
import numpy as np
import pytest
from s3mapgen.generation.archetypes import large_islands
from s3mapgen.generation.archetypes.profiles import default_archetype_profile, normalize_archetype_profile

def test_island_snow_default_is_visible_and_saved_thresholds_are_preserved():
    preset = default_archetype_profile('large_islands')
    assert preset['relief']['snow_threshold'] == 200
    preset['relief']['snow_threshold'] = 190
    assert normalize_archetype_profile(preset, archetype_key='large_islands')['relief']['snow_threshold'] == 190
    assert default_archetype_profile('continental')['relief']['snow_threshold'] == 190

def test_mask_noise_work_is_bounded_by_local_territories(monkeypatch):
    from s3mapgen.generation.archetypes import island_simplex
    layout_cells, local_cells = [], []
    layout_noise = large_islands._smooth_noise
    octave_noise = island_simplex._simplex_noise
    def observe_layout(x, y, *args):
        layout_cells.append(x.size)
        return layout_noise(x, y, *args)
    def observe_octave(x, y, *args):
        local_cells.append(x.size)
        return octave_noise(x, y, *args)
    monkeypatch.setattr(large_islands, '_smooth_noise', observe_layout)
    monkeypatch.setattr(island_simplex, '_simplex_noise', observe_octave)
    labels, centers, mask, channel, attempts = large_islands.build_island_masks(768, 20, 2026093008)
    assert 0 <= attempts < 8
    assert .56 < np.count_nonzero(labels) / labels.size < .57
    assert sum(layout_cells) == 2 * labels.size * (attempts + 1)
    # Only local bounding boxes, never one full-map field per island/octave.
    assert len(local_cells) <= 6 * len(centers) * (attempts + 1)
    assert max(local_cells) < labels.size / 2
    assert sum(local_cells) < 18 * labels.size * (attempts + 1)

def test_soft_summits_have_no_clipped_altitude_plateau():
    signal = np.linspace(-2, 2, 1000, dtype=np.float32)
    depth = np.full(signal.shape, 60, dtype=np.float32)
    raw, relief = large_islands._local_island_relief(signal, depth, 60, 0)
    assert np.all(np.diff(raw) > 0)
    assert raw.max() < 215
    assert np.all(np.diff(relief) > 0)


def test_local_source_is_deterministic_and_independent_of_global_coordinates():
    from s3mapgen.generation.archetypes.island_simplex import simplex_signal
    yy, xx = np.indices((83, 117), dtype=np.float32)
    first = simplex_signal(xx, yy, 48, 1234)
    assert np.array_equal(first, simplex_signal(xx + 500, yy + 300, 48, 1234))
    assert np.array_equal(first, simplex_signal(xx, yy, 48, 1234))
    assert not np.array_equal(first, simplex_signal(xx, yy, 48, 1235))
    assert np.isfinite(first).all() and first.std() > .1


def test_surface_completion_stays_connected_and_respects_the_safe_gap():
    from s3mapgen.map_data.hexgrid import component_labels
    safe = np.zeros((12, 15), bool)
    safe[2:10, 2:13] = True
    retained = np.zeros_like(safe)
    retained[5:7, 6:8] = True
    yy, xx = np.indices(safe.shape)
    score = np.sin(xx * 2) + np.cos(yy * 3)
    result = large_islands._finish_connected_mask(retained, safe, score, 53)
    assert result.sum() == 53
    assert component_labels(result)[1] == 1
    assert result[retained].all() and not result[~safe].any()


def test_setback_detail_is_local_and_bounded_without_changing_safe_domain():
    from scipy.ndimage import distance_transform_edt
    yy, xx = np.indices((100, 100), dtype=np.float32)
    safe = np.zeros(xx.shape, bool)
    safe[2:98, 2:98] = True
    original = safe.copy()
    depth = distance_transform_edt(safe).astype(np.float32)
    coast = np.sin(xx * .8) * np.cos(yy * .7)
    adjusted = large_islands._coast_guard_depth(depth, coast, safe, 15.)
    assert np.array_equal(safe, original)
    assert np.max(np.abs(adjusted[safe] - depth[safe])) <= 2.5
    assert np.mean(np.abs(adjusted[safe & (depth < 5)] - depth[safe & (depth < 5)])) > .25
    assert np.mean(np.abs(adjusted[depth > 30] - depth[depth > 30])) < .25


@pytest.mark.parametrize('water_inside', [False, True])
def test_fine_contours_keep_their_texture_on_steep_coasts_and_lake_rims(water_inside):
    from s3mapgen.generation.archetypes.island_simplex import simplex_signal
    from s3mapgen.map_data.hexgrid import neighbor_count
    yy, xx = np.indices((101, 101), dtype=np.float32)
    radius = np.hypot(xx - 50, yy - 50)
    score = (radius - 27) * (-1 if water_inside else 1)
    detail = large_islands._coast_detail(
        simplex_signal(xx, yy, 32, 1234), np.ones(xx.shape, bool),
    )
    original_water = score > 0
    adjusted_water = large_islands._detail_contour_score(score, detail) > 0
    # Scaling the score gradient must not flatten the same physical rim.
    for steepness in (5, 20):
        assert np.array_equal(
            adjusted_water,
            large_islands._detail_contour_score(score * steepness, detail) > 0,
        )
    original_rim = int((6 - neighbor_count(original_water))[original_water].sum())
    adjusted_rim = int((6 - neighbor_count(adjusted_water))[adjusted_water].sum())
    assert adjusted_rim > original_rim
    changed_radius = radius[original_water != adjusted_water]
    assert np.all(np.abs(changed_radius - 27) < 2)
    # This helper only perturbs scores. Connected land is selected afterwards,
    # covered by the mask-completion and actual island topology tests.


def test_constant_coast_detail_does_not_change_the_shape():
    yy, xx = np.indices((40, 50), dtype=np.float32)
    score = np.hypot(xx - 25, yy - 20)
    detail = large_islands._coast_detail(np.ones_like(score), np.ones(score.shape, bool))
    assert np.array_equal(large_islands._detail_contour_score(score, detail), score)


@pytest.mark.parametrize('rounded_relief', [False, True])
def test_multiscale_source_uses_bounded_affine_coordinates_without_warp(monkeypatch, rounded_relief):
    from s3mapgen.generation.archetypes import island_simplex
    sample = island_simplex._simplex_noise
    coordinates = []
    def observe(x, y, seed, **kwargs):
        coordinates.append((x.copy(), y.copy(), seed))
        return sample(x, y, seed, **kwargs)
    monkeypatch.setattr(island_simplex, '_simplex_noise', observe)
    yy, xx = np.indices((83, 117), dtype=np.float32)
    signal = island_simplex.simplex_signal(xx, yy, 48, 1234, rounded_relief=rounded_relief)
    assert 1 <= len(coordinates) <= 6
    assert len({seed for x, y, seed in coordinates}) == len(coordinates)
    for x, y, seed in coordinates:
        assert x.shape == xx.shape and y.shape == yy.shape
        for values in (x, y):
            # A noise-dependent displacement would introduce varying slopes.
            assert np.max(np.abs(np.diff(values, n=2, axis=0))) < 5e-5
            assert np.max(np.abs(np.diff(values, n=2, axis=1))) < 5e-5
    assert signal.shape == xx.shape and signal.dtype == np.float32
    assert np.isfinite(signal).all() and signal.std() > .1


@pytest.mark.parametrize('side,players,seed,expected', [
    (256, 2, 42, 'db901b0c3107af1901ff999a205bc322bbf7a5e2e63505a30b1a96e9cacefff0'),
    (384, 4, 2026093004, '9793e46cb636a5ccacf16ddc1c626b71e786552088975f438805f43f59b24238'),
    (384, 8, 42, '5e2c93c7630949524c25c46d1b8d264b54e23356554241f7bc8a0f5ec234c6fc'),
    (512, 15, 1, 'e88ebdd6b33b58227b2cbba6c83161104888925e579aecb2b7a1610549862c66'),
    (768, 4, 2026093006, '9d5ce23a970c91d07dd828cfd6c6cb015ecb1e6b9769646c0f83ba36aec0b87e'),
    (768, 20, 2026093008, '4f55568753d89fde45d94d40cba135be8e42df58a210994e1ada0c79dacc3871'),
])
def test_mountain_refinement_preserves_reference_coastlines(side, players, seed, expected):
    import hashlib
    labels, *_ = large_islands.build_island_masks(side, players, seed)
    assert hashlib.sha256(labels.tobytes()).hexdigest() == expected


def test_rounded_relief_is_reproducible_without_diagonal_energy_bias():
    from s3mapgen.generation.archetypes.island_simplex import simplex_signal, _RELIEF_GRADIENTS
    lengths = np.linalg.norm(_RELIEF_GRADIENTS, axis=1)
    assert np.allclose(lengths, np.sqrt(1.5), atol=1e-6)
    directions = np.sort(np.arctan2(_RELIEF_GRADIENTS[:, 1], _RELIEF_GRADIENTS[:, 0]))
    gaps = np.diff(np.r_[directions, directions[0] + 2 * np.pi])
    assert np.allclose(gaps, 2 * np.pi / 32, atol=1e-6)
    yy, xx = np.indices((83, 117), dtype=np.float32)
    first = simplex_signal(xx, yy, 48, 1234, rounded_relief=True)
    assert np.array_equal(first, simplex_signal(xx + 500, yy + 300, 48, 1234, rounded_relief=True))
    assert not np.array_equal(first, simplex_signal(xx, yy, 48, 1235, rounded_relief=True))
    assert np.isfinite(first).all() and .1 < first.std() < .5
