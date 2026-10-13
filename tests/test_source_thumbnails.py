"""Bundled source icons stay complete and never regenerate during UI loading."""
import hashlib
import json
from pathlib import Path
from PIL import Image
from s3mapgen.generation.archetypes.profiles import RELIEF_SOURCE_OPTIONS
from s3mapgen.application.custom import source_selector

ROOT = Path(__file__).resolve().parent.parent


def test_bundled_icons_cover_sources_with_provenance_and_valid_images():
    folder = ROOT / 'data' / 'source_thumbnails'
    manifest = json.loads((folder / 'manifest.json').read_text())
    assert set(manifest['images']) == set(RELIEF_SOURCE_OPTIONS)
    assert manifest['seed'] == 20261005
    for key, record in manifest['images'].items():
        path = folder / record['file']
        assert path.name == key + '.png'
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256']
        with Image.open(path) as image:
            assert image.mode == 'L' and image.size == (64, 64)
            low, high = image.getextrema()
            assert high > low


def test_loading_reuses_images_and_never_generates_missing_thumbnails(monkeypatch, tmp_path):
    source_selector.reference_thumbnail.cache_clear()
    image = source_selector.reference_thumbnail('perlin')
    assert image is not None and image.size == (24, 24)
    assert source_selector.reference_thumbnail('perlin') is image
    monkeypatch.setattr(source_selector, 'BASE', tmp_path)
    assert source_selector.reference_thumbnail('perlin') is image
    assert source_selector.reference_thumbnail('missing') is None
    assert source_selector.reference_thumbnail('../perlin') is None
    source_selector.reference_thumbnail.cache_clear()
