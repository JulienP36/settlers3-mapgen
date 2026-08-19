from __future__ import annotations
import json, os
from pathlib import Path

DEFAULTS = {
    'theme': 'dark',
    'overlay_alpha': 68,
    'projection': 'square',
    'wheel_zoom': 1.10,
}


def settings_path() -> Path:
    base = Path(os.environ.get('APPDATA') or Path.home())
    return base / 'Settlers3MapGen' / 'settings.json'


def load_settings() -> dict:
    cfg = dict(DEFAULTS)
    path = settings_path()
    try:
        raw = json.loads(path.read_text(encoding='utf-8'))
        if isinstance(raw, dict):
            cfg.update({k: raw[k] for k in DEFAULTS if k in raw})
    except (OSError, ValueError, TypeError):
        pass
    cfg['theme'] = 'dark' if cfg.get('theme') == 'dark' else 'light'
    cfg['projection'] = 'parallelogram' if cfg.get('projection') == 'parallelogram' else 'square'
    cfg['overlay_alpha'] = max(0, min(100, int(cfg.get('overlay_alpha', 68))))
    cfg['wheel_zoom'] = max(1.02, min(1.30, float(cfg.get('wheel_zoom', 1.10))))
    return cfg


def save_settings(settings: dict) -> None:
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = dict(DEFAULTS)
    clean.update({k: settings[k] for k in DEFAULTS if k in settings})
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding='utf-8')
    tmp.replace(path)
