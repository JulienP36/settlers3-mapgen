import numpy as np
import pytest

from s3mapgen.generation.start_algorithms import resolve_start_algorithm
from s3mapgen.generation.start_placement import place_starts
from s3mapgen.map_data.model import MapState
from s3mapgen.application.session.cache import GenerationCacheKey, SessionGenerationCache


def test_classic_is_explicit_and_islands_require_geography():
    assert resolve_start_algorithm('classic') == 'classic'
    assert resolve_start_algorithm('classic',np.ones((32,32))) == 'classic'
    with pytest.raises(ValueError):
        resolve_start_algorithm('islands')
    assert resolve_start_algorithm('auto') == 'balanced'


def test_island_contract_survives_explicit_balanced_selection():
    state = MapState.empty(192)
    state.terrain[:] = 16
    labels = np.zeros((192, 192), dtype=np.uint8)
    labels[20:80, 20:80] = 1
    labels[112:172, 112:172] = 2
    place_starts(state, 2, np.random.default_rng(42), island_labels=labels,
                 start_algorithm='balanced')
    assert [int(labels[y, x]) for x, y in state.starts] == [1, 2]
    assert state.metadata['start_algorithm_requested'] == 'balanced'
    assert state.metadata['start_algorithm_effective'] == 'islands'


def test_cache_never_reuses_a_different_start_strategy():
    cache = SessionGenerationCache(4)
    balanced = GenerationCacheKey(42, 512, 4, 'legacy', 'continental', start_algorithm='balanced')
    automatic = GenerationCacheKey(42, 512, 4, 'legacy', 'continental', start_algorithm='auto')
    cache.put(balanced, 'balanced map')
    assert cache.get(automatic) is None
