import numpy as np

from s3mapgen.app_paths import UPGRADED_REFERENCE
from s3mapgen.morphology import UpgradedMorphologyLibrary


def test_edm_migration_source_exposes_continental_template():
    lib = UpgradedMorphologyLibrary(UPGRADED_REFERENCE)
    assert lib.indices_for('continental') == [0]
    item = lib.get(0)
    assert item.terrain.shape == (768, 768)
    assert item.height.shape == (768, 768)
    assert item.source == 'upgraded_reference_768.edm'


def test_npz_roundtrip_preserves_morphology(tmp_path):
    source = UpgradedMorphologyLibrary(UPGRADED_REFERENCE)
    path = source.save_npz(tmp_path / 'morphology.npz')
    loaded = UpgradedMorphologyLibrary(path)
    assert loaded.indices_for('continental') == [0]
    assert np.array_equal(loaded.get(0).terrain, source.get(0).terrain)
    assert np.array_equal(loaded.get(0).height, source.get(0).height)
