"""Versioned value objects and atomic storage, independent of Tk and generation."""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from uuid import uuid4

from ...generation.archetypes import ARCHETYPES
from ...generation.custom.config import CustomGenerationConfig
from ...generation.core import NATIVE_PLAYER_LIMITS

FORMAT = 'settlers3-mapgen-configurations'
VERSION = 1
MAX_BYTES = 64 * 1024 * 1024


def collection_path():
    return Path(os.environ.get('APPDATA') or Path.home()) / 'Settlers3MapGen' / 'configurations.json'


def integer(value, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f'Integer required: {low}–{high}')
    return value


def validate_snapshot(value):
    """Validate completely before changing disk or application state.

    Masks are already embedded grayscale grids in CustomGenerationConfig;
    the full composition is retained rather than referencing catalogue paths.
    """
    if not isinstance(value, dict):
        raise ValueError('Configuration must be an object')
    required = {'mode', 'archetype', 'size', 'players', 'mirror', 'starts',
                'nations', 'teams', 'random_team_count', 'custom'}
    if set(value) not in (required, required | {'seed'}):
        raise ValueError('Incomplete or unknown configuration fields')
    result = deepcopy(value)
    if result['mode'] not in ('legacy', 'upgraded', 'custom'):
        raise ValueError('Unknown generator')
    if result['archetype'] not in ARCHETYPES:
        raise ValueError('Unknown archetype')
    if type(result['size']) is not int or result['size'] not in NATIVE_PLAYER_LIMITS:
        raise ValueError('Unsupported map size')
    integer(result['players'], 2, 20)
    if result['players'] > NATIVE_PLAYER_LIMITS[result['size']]:
        raise ValueError('Too many players for this map size')
    integer(result['mirror'], 0, 3)
    integer(result['random_team_count'], 2, 20)
    if result['starts'] not in ('auto', 'classic', 'balanced', 'fair', 'islands', 'teams'):
        raise ValueError('Unknown start algorithm')
    for key, low, high in (('nations', 0, 255), ('teams', -1, 20)):
        items = result[key]
        if not isinstance(items, list) or len(items) != 20:
            raise ValueError('Twenty player slots required')
        for item in items:
            integer(item, low, high)
            if key == 'nations' and item not in (0, 1, 2, 3, 255):
                raise ValueError('Unknown civilization')
    if 'seed' in result:
        if type(result['seed']) is not int:
            raise ValueError('Integer seed required')
    custom = result['custom']
    if not isinstance(custom, dict) or custom.get('schema_version') != 2:
        raise ValueError('Unsupported custom configuration version')
    config = CustomGenerationConfig.from_dict(custom)
    if config.base_archetype != result['archetype'] or (
        result['mode'] != 'custom' and config.base_mode != result['mode']
    ):
        raise ValueError('Inconsistent configuration sources')
    result['custom'] = config.to_dict()
    # Reject NaN/infinity, even in optional profile metadata.
    json.dumps(result, allow_nan=False)
    return result


def preset(name, snapshot, *, identity=None):
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 100:
        raise ValueError('Name required (1–100 characters)')
    if any(ord(char) < 32 for char in name):
        raise ValueError('Invalid name')
    return {'id': identity or uuid4().hex, 'name': name.strip(),
            'configuration': validate_snapshot(snapshot)}


def document(entries):
    return {'format': FORMAT, 'version': VERSION, 'configurations': deepcopy(entries)}


def parse_document(value):
    if not isinstance(value, dict) or value.get('format') != FORMAT or type(value.get('version')) is not int or value['version'] != VERSION:
        raise ValueError('Unsupported configurations collection')
    entries = value.get('configurations')
    if not isinstance(entries, list):
        raise ValueError('Configurations list required')
    result, ids, names = [], set(), set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'id', 'name', 'configuration'}:
            raise ValueError('Invalid collection entry')
        identity = entry['id']
        if not isinstance(identity, str) or not identity or len(identity) > 100 or identity in ids:
            raise ValueError('Invalid or duplicate configuration identifier')
        item = preset(entry['name'], entry['configuration'], identity=identity)
        if item['name'].casefold() in names:
            raise ValueError('Duplicate configuration name')
        ids.add(identity)
        names.add(item['name'].casefold())
        result.append(item)
    return result


def read_collection(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('Configurations collection exceeds 64 MiB')
    return parse_document(json.loads(path.read_text(encoding='utf-8')))


def write_collection(path, entries):
    """Validate first, replace atomically, leave the previous collection on failure."""
    payload = json.dumps(document(parse_document(document(entries))), ensure_ascii=False,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    if len(payload) > MAX_BYTES:
        raise ValueError('Configurations collection exceeds 64 MiB')
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.configurations-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def merge_collections(existing, incoming):
    merged = parse_document(document(existing))
    names = {item['name'].casefold() for item in merged}
    for item in parse_document(document(incoming)):
        base, number = item['name'], 2
        name = base
        while name.casefold() in names:
            suffix = f' ({number})'
            name = base[:100-len(suffix)] + suffix
            number += 1
        merged.append(preset(name, item['configuration']))
        names.add(name.casefold())
    return merged
