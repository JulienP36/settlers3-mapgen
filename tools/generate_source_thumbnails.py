"""Rebuild fixed selector PNGs offline; never imported by the GUI.

Every icon comes from the real deterministic provider with reference settings.
These are identification samples, not the current user's composition preview.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from s3mapgen.generation.archetypes import default_archetype_profile, generate_archetype_preview, noise_rgb
from s3mapgen.generation.archetypes.profiles import RELIEF_SOURCE_OPTIONS, RELIEF_SOURCE_CONTINENTAL, continental_landmass_profile
from s3mapgen.generation.archetypes.noise_sources import NOISE_SOURCE_OPTIONS
from s3mapgen.generation.archetypes.morphology import generate_noise_component_previews

SEED = 20261005
REFERENCE_SIDE = 384
IMAGE_SIDE = 64


def build(destination=None):
    destination = Path(destination or ROOT / 'data' / 'source_thumbnails')
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {'seed': SEED, 'reference_side': REFERENCE_SIDE, 'players': 4,
                'image_side': IMAGE_SIDE, 'settings': 'Default archetype source settings; no fusions or masks',
                'generator': 'tools/generate_source_thumbnails.py', 'images': {}}
    for key in RELIEF_SOURCE_OPTIONS:
        profile = default_archetype_profile('large_islands' if key.startswith('large_islands') else 'continental')
        if key == RELIEF_SOURCE_CONTINENTAL:
            profile = continental_landmass_profile()
        elif key == 'team_islands':
            profile = default_archetype_profile('team_islands')
        profile['morphology'].update(relief_source=key, noise_layer_count=0, mask_layer_count=0)
        if key in NOISE_SOURCE_OPTIONS:
            grid, _ = generate_noise_component_previews(profile, IMAGE_SIDE, SEED, domain_side=REFERENCE_SIDE)
        else:
            preview = generate_archetype_preview(profile, REFERENCE_SIDE, SEED, players=4, player_teams=(1,1,2,2) if key == "team_islands" else ())
            grid = noise_rgb(preview.source_noise)[:, :, 0]
        image = Image.fromarray(np.asarray(grid, dtype=np.uint8)).resize((IMAGE_SIDE, IMAGE_SIDE), Image.Resampling.BILINEAR)
        path = destination / f'{key}.png'
        image.save(path, optimize=True)
        manifest['images'][key] = {'file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), **({'player_teams':[1,1,2,2]} if key == 'team_islands' else {})}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


if __name__ == '__main__':
    report = build()
    print(f"Built {len(report['images'])} deterministic reference thumbnails")
