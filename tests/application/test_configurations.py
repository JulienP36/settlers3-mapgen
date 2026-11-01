"""Portable presets retain complete settings and never partially overwrite collections."""
from copy import deepcopy
import json

import pytest

from s3mapgen.application.configurations import model
from s3mapgen.generation.custom import build_custom_config


@pytest.fixture
def snapshot():
    config = build_custom_config('upgraded', 'team_islands')
    profile = deepcopy(config.archetype_profile)
    profile['morphology']['mask_layer_count'] = 1
    profile['morphology']['mask_layers'][0].update(
        enabled=True, type='manual',
        provider_settings={'grid_side': 64, 'grid': [n % 256 for n in range(64*64)]},
    )
    config = config.with_archetype_profile(profile)
    return dict(mode='custom', archetype='team_islands', size=768, players=12,
                mirror=2, starts='teams', nations=[0, 1, 2, 3, 255] * 4,
                teams=[-1, 0, 1, 2, 20] * 4, random_team_count=4, custom=config.to_dict())


def test_collection_roundtrip_is_self_contained_and_preserves_raw_choices(snapshot, tmp_path):
    entries = [model.preset('Îles à jouer', snapshot), model.preset('Seed fixe', dict(snapshot, seed=2026101010))]
    path = tmp_path / 'collection.json'
    model.write_collection(path, entries)
    assert model.read_collection(path) == entries
    assert list(tmp_path.iterdir()) == [path]
    loaded = model.read_collection(path)[0]['configuration']
    assert loaded['teams'] == snapshot['teams']
    assert loaded['nations'] == snapshot['nations']
    grid = loaded['custom']['archetype_profile']['morphology']['mask_layers'][0]['provider_settings']['grid']
    assert grid == snapshot['custom']['archetype_profile']['morphology']['mask_layers'][0]['provider_settings']['grid']
    assert 'seed' not in loaded


def test_merge_keeps_every_preset_and_suffixes_names_case_insensitively(snapshot):
    original = [model.preset('Îles', snapshot), model.preset('Îles (2)', snapshot)]
    incoming = [model.preset('ÎLES', snapshot), model.preset('Neuf', snapshot)]
    saved = deepcopy(original)
    merged = model.merge_collections(original, incoming)
    assert [item['name'] for item in merged] == ['Îles', 'Îles (2)', 'ÎLES (3)', 'Neuf']
    assert len({item['id'] for item in merged}) == 4
    assert original == saved
    assert merged[2]['configuration'] == snapshot


@pytest.mark.parametrize('field,value', [
    ('size', 1024), ('players', 21), ('players', True), ('mode', 'invalid'),
    ('archetype', 'unknown'), ('mirror', 4), ('starts', 'unknown'),
    ('random_team_count', 1), ('teams', [21]*20), ('teams', [-2]*20),
    ('nations', [4]*20), ('nations', [True]*20), ('nations', [0]),
    ('seed', '123'), ('custom', {}),
])
def test_invalid_snapshot_rejected(snapshot, field, value):
    snapshot[field] = value
    with pytest.raises((ValueError, TypeError)):
        model.validate_snapshot(snapshot)


def test_rejects_player_size_and_source_mismatches(snapshot):
    with pytest.raises(ValueError):
        model.validate_snapshot(dict(snapshot, size=256))
    with pytest.raises(ValueError):
        model.validate_snapshot(dict(snapshot, archetype='continental'))
    with pytest.raises(ValueError):
        model.validate_snapshot(dict(snapshot, mode='legacy'))


def test_failed_atomic_replace_preserves_previous_file_and_cleans_temporary(snapshot, tmp_path, monkeypatch):
    path = tmp_path / 'collection.json'
    entries = [model.preset('Première', snapshot)]
    model.write_collection(path, entries)
    previous = path.read_bytes()
    def fail(*args):
        raise OSError('Disk failure')
    monkeypatch.setattr(model.os, 'replace', fail)
    with pytest.raises(OSError):
        model.write_collection(path, entries + [model.preset('Seconde', snapshot)])
    assert path.read_bytes() == previous
    assert list(tmp_path.iterdir()) == [path]


def test_whole_import_is_validated_before_merge(snapshot):
    original = [model.preset('Original', snapshot)]
    saved = deepcopy(original)
    incoming = [model.preset('Good', snapshot), model.preset('Bad', snapshot)]
    incoming[1]['configuration']['nations'] = []
    with pytest.raises(ValueError):
        model.merge_collections(original, incoming)
    assert original == saved


@pytest.mark.parametrize('change', ['format', 'version', 'ids', 'names', 'malformed', 'nan'])
def test_corrupt_or_future_collections_rejected(snapshot, tmp_path, change):
    doc = model.document([model.preset('A', snapshot), model.preset('B', snapshot)])
    if change == 'format': doc['format'] = 'other'
    if change == 'version': doc['version'] = 2
    if change == 'ids': doc['configurations'][1]['id'] = doc['configurations'][0]['id']
    if change == 'names': doc['configurations'][1]['name'] = 'a'
    if change == 'nan': doc['configurations'][0]['configuration']['custom']['profile']['bad'] = float('nan')
    path = tmp_path / 'collection.json'
    path.write_text('{' if change == 'malformed' else json.dumps(doc), encoding='utf-8')
    with pytest.raises((ValueError, TypeError)):
        model.read_collection(path)


def test_all_integer_seeds_remain_supported(snapshot):
    for seed in (-10, 0, 2026101010, 2**48):
        assert model.validate_snapshot(dict(snapshot, seed=seed))['seed'] == seed


def test_language_catalogues_cover_same_actions():
    from s3mapgen.application.configurations.text import TEXT
    assert all(set(value) == set(TEXT['fr']) for value in TEXT.values())
