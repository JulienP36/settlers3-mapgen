"""Central registry and cached loader for supplied pixel art.

Procedural source thumbnails remain separate generation reference data.
Returned Pillow images are copies, so callers cannot modify the shared cache.
"""
from functools import lru_cache
from PIL import Image, ImageTk
from ..paths import SPRITES_ROOT

NATION_SPRITES = {0: 'civilizations/roman', 1: 'civilizations/egyptian',
                  2: 'civilizations/chinese', 3: 'civilizations/amazon'}

SPRITE_FILES = {
    **{key: key + '.png' for key in NATION_SPRITES.values()},
    **{f'views/{key}': f'views/{key}.png' for key in ('global','territories','initial_territory','heightmap','resources','paths','crops','heatmap','valid_starts')},
    **{f'heatmap/{key}': f'heatmap/{key}.png' for key in ('trees','building_stones','fish')},
    'variants/grapes': 'variants/grapes.png',
    'ui/lock_closed': 'ui/lock_closed.png',
    'ui/lock_open': 'ui/lock_open.png',
    'ui/seed_dice': 'ui/seed_dice.png',
    'ui/info': 'ui/info.png',
    'ui/recenter': 'ui/recenter.png',
    'players/start_markers': 'players/start_markers.png',
    **{f'minerals/{key}': f'minerals/{key}.png' for key in ('coal','iron','gold','gems','sulfur')},
    **{f'mask/{key}': f'mask_editor/{key}.png' for key in ('brush','eraser','picker','round','square','fill','undo','redo','invert','flip_x','flip_y','rotate_left','rotate_right','new','delete','export','import','refresh','folder','cancel','apply','save','catalogue','clear')},
}


def sprite_path(key):
    return SPRITES_ROOT / SPRITE_FILES[key]


@lru_cache(maxsize=64)
def _loaded_sprite(key):
    with Image.open(sprite_path(key)) as source:
        return source.convert('RGBA')


def sprite_image(key):
    return _loaded_sprite(key).copy()


def sprite_photo(master, key):
    owner = master._root()
    if not hasattr(owner, '_sprite_photos'):
        owner._sprite_photos = {}
    if key not in owner._sprite_photos:
        owner._sprite_photos[key] = ImageTk.PhotoImage(sprite_image(key), master=owner)
    return owner._sprite_photos[key]
