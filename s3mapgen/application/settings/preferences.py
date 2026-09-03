"""Versioned user-settings loading, migration, validation and persistence."""

from __future__ import annotations
import json, os
from pathlib import Path
from ..shortcuts.bindings import DEFAULT_SHORTCUTS, canonicalize_shortcut

SETTINGS_SCHEMA_VERSION = 2

DEFAULTS = {
    'settings_version': SETTINGS_SCHEMA_VERSION,
    'theme': 'dark',
    'overlay_alpha': 75,
    'projection': 'square',
    'preview_start_markers': 'small',
    'preview_start_circles': False,
    'history_capacity': 8,
    'wheel_zoom': 1.10,
    'language': 'fr',
    'shortcuts': DEFAULT_SHORTCUTS,
}

def settings_path() -> Path:
    base = Path(os.environ.get('APPDATA') or Path.home())
    return base / 'Settlers3MapGen' / 'settings.json'

def _clean_shortcuts(value) -> dict:
    out = dict(DEFAULT_SHORTCUTS)
    if isinstance(value, dict):
        for key in DEFAULT_SHORTCUTS:
            if key not in value:
                continue
            try:
                out[key] = canonicalize_shortcut(value.get(key))
            except (TypeError, ValueError):
                # One malformed user entry never invalidates the full file.
                out[key] = DEFAULT_SHORTCUTS[key]
    return out

def load_settings() -> dict:
    cfg = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
    path = settings_path()
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(raw, dict):
            for key in DEFAULTS:
                if key in raw:
                    cfg[key] = raw[key]
    except (OSError, ValueError, TypeError):
        pass
    cfg['theme'] = 'dark' if cfg.get('theme') == 'dark' else 'light'
    cfg['projection'] = 'parallelogram' if cfg.get('projection') == 'parallelogram' else 'square'
    cfg['preview_start_markers'] = cfg.get('preview_start_markers') if cfg.get('preview_start_markers') in ('hidden', 'tiny', 'small', 'normal') else 'small'
    cfg['preview_start_circles'] = cfg.get('preview_start_circles') is True
    cfg['history_capacity'] = int(cfg.get('history_capacity', 8)) if str(cfg.get('history_capacity', 8)) in ('4','8','12','16') else 8
    cfg['overlay_alpha'] = max(0, min(100, int(cfg.get('overlay_alpha', 75))))
    cfg['wheel_zoom'] = max(1.02, min(1.30, float(cfg.get('wheel_zoom', 1.10))))
    cfg['language'] = cfg.get('language') if cfg.get('language') in ('fr', 'en', 'de', 'es') else 'fr'
    cfg['shortcuts'] = _clean_shortcuts(cfg.get('shortcuts'))
    cfg['settings_version'] = SETTINGS_SCHEMA_VERSION
    return cfg

def save_settings(settings: dict) -> None:
    path = settings_path(); path.parent.mkdir(parents=True, exist_ok=True)
    clean = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
    for key in DEFAULTS:
        if key in settings:
            clean[key] = settings[key]
    clean['shortcuts'] = _clean_shortcuts(clean.get('shortcuts'))
    clean['settings_version'] = SETTINGS_SCHEMA_VERSION
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(path)
