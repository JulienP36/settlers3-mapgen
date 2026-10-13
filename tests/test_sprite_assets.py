"""Preserve supplied pixel art and prevent cache consumers from altering it."""
import hashlib
import json
from PIL import Image
from s3mapgen.application.ui import sprites


def test_sprite_registry_and_manifest_preserve_all_supplied_pngs():
    manifest=json.loads((sprites.SPRITES_ROOT/'manifest.json').read_text())
    assert set(manifest)==set(sprites.SPRITE_FILES.values())
    for key,relative in sprites.SPRITE_FILES.items():
        path=sprites.sprite_path(key);entry=manifest[relative]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']
        with Image.open(path) as image:
            assert list(image.size)==entry['size']
            loaded=sprites.sprite_image(key)
            assert loaded.tobytes()==image.convert('RGBA').tobytes()
        if key.startswith('mask/'):
            assert loaded.size==(24,24)
            assert loaded.getchannel('A').getextrema()==(0,255)


def test_cached_images_are_isolated_from_caller_mutations():
    sprites._loaded_sprite.cache_clear()
    original=sprites.sprite_image('mask/brush')
    altered=sprites.sprite_image('mask/brush')
    altered.putpixel((0,0),(255,0,255,255))
    assert sprites.sprite_image('mask/brush').tobytes()==original.tobytes()
    assert sprites._loaded_sprite.cache_info().misses==1
