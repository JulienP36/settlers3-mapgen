from __future__ import annotations
import json, os
from pathlib import Path

DEFAULT_SHORTCUTS = {
    'generate': 'Ctrl+G',
    'import': 'Ctrl+O',
    'export': 'Ctrl+E',
    'reset_view': 'Ctrl+R',
    'copy_seed': 'Ctrl+Shift+C',
    'toggle_ab': 'Ctrl+B',
    'toggle_theme': 'Ctrl+Shift+T',
    'help': 'F1',
}

DEFAULTS = {
    'theme': 'dark',
    'overlay_alpha': 75,
    'projection': 'square',
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
            v = value.get(key)
            if isinstance(v, str) and v.strip():
                out[key] = v.strip()
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
    cfg['overlay_alpha'] = max(0, min(100, int(cfg.get('overlay_alpha', 75))))
    cfg['wheel_zoom'] = max(1.02, min(1.30, float(cfg.get('wheel_zoom', 1.10))))
    cfg['language'] = cfg.get('language') if cfg.get('language') in ('fr', 'en') else 'fr'
    cfg['shortcuts'] = _clean_shortcuts(cfg.get('shortcuts'))
    return cfg

def save_settings(settings: dict) -> None:
    path = settings_path(); path.parent.mkdir(parents=True, exist_ok=True)
    clean = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
    for key in DEFAULTS:
        if key in settings:
            clean[key] = settings[key]
    clean['shortcuts'] = _clean_shortcuts(clean.get('shortcuts'))
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(path)
