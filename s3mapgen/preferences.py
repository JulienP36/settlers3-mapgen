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
    'help': 'F1',
}

DEFAULTS = {
    'theme': 'dark',
    'overlay_alpha': 68,
    'projection': 'square',
    'wheel_zoom': 1.10,
    'language': 'fr',
    'shortcuts': DEFAULT_SHORTCUTS,
}


def settings_path() -> Path:
    base = Path(os.environ.get('APPDATA') or Path.home())
    return base / 'Settlers3MapGen' / 'settings.json'


def load_settings() -> dict:
    cfg = dict(DEFAULTS)
    cfg['shortcuts'] = dict(DEFAULT_SHORTCUTS)
    path = settings_path()
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(raw, dict):
            for k in DEFAULTS:
                if k == 'shortcuts':
                    continue
                if k in raw:
                    cfg[k] = raw[k]
            if isinstance(raw.get('shortcuts'), dict):
                for command, default in DEFAULT_SHORTCUTS.items():
                    value = raw['shortcuts'].get(command, default)
                    if isinstance(value, str) and value.strip():
                        cfg['shortcuts'][command] = value.strip()
    except (OSError, ValueError, TypeError):
        pass
    cfg['theme'] = 'dark' if cfg.get('theme') == 'dark' else 'light'
    cfg['projection'] = 'parallelogram' if cfg.get('projection') == 'parallelogram' else 'square'
    cfg['overlay_alpha'] = max(0, min(100, int(cfg.get('overlay_alpha', 68))))
    cfg['wheel_zoom'] = max(1.02, min(1.30, float(cfg.get('wheel_zoom', 1.10))))
    cfg['language'] = 'en' if cfg.get('language') == 'en' else 'fr'
    return cfg


def save_settings(settings: dict) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = dict(DEFAULTS)
    clean['shortcuts'] = dict(DEFAULT_SHORTCUTS)
    for k in DEFAULTS:
        if k == 'shortcuts':
            continue
        if k in settings:
            clean[k] = settings[k]
    if isinstance(settings.get('shortcuts'), dict):
        for command, default in DEFAULT_SHORTCUTS.items():
            value = settings['shortcuts'].get(command, default)
            if isinstance(value, str) and value.strip():
                clean['shortcuts'][command] = value.strip()
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(path)
