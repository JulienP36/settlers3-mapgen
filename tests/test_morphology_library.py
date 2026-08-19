import numpy as np

from s3mapgen.app_paths import LIBRARY, UPGRADED_REFERENCE, LEGACY_PROFILE, UPGRADED_PROFILE
from s3mapgen.morphology import ArchetypeMorphologyLibrary
from s3mapgen.generator import MapGenerator


def test_native_library_is_a_continental_archetype_library():
    lib = ArchetypeMorphologyLibrary(LIBRARY)
    ids = lib.indices_for('continental')
    assert len(ids) == 3
    item = lib.get(ids[0])
    assert item.terrain.shape == (768, 768)
    assert item.height.shape == (768, 768)


def test_edm_is_supported_only_as_migration_source(tmp_path):
    source = ArchetypeMorphologyLibrary(UPGRADED_REFERENCE)
    path = source.save_npz(tmp_path / 'morphology.npz')
    loaded = ArchetypeMorphologyLibrary(path)
    assert np.array_equal(loaded.get(0).terrain, source.get(0).terrain)
    assert np.array_equal(loaded.get(0).height, source.get(0).height)


def test_upgraded_runtime_no_longer_requires_checkpoint_path():
    missing = UPGRADED_REFERENCE.with_name('this_checkpoint_does_not_exist.edm')
    gen = MapGenerator(LEGACY_PROFILE, LIBRARY, UPGRADED_PROFILE, missing)
    result = gen.generate(4, 2026082001, mode='upgraded', archetype='continental')
    assert len(result.state.starts) == 4
    assert 'archetype_morphology_index' in result.state.metadata
