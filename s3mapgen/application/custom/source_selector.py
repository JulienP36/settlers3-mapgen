"""Source menus using bundled reference PNGs, with no generation at runtime."""
from functools import lru_cache
from weakref import WeakSet
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from ..paths import BASE


@lru_cache(maxsize=32)
def reference_thumbnail(key):
    """Load a trusted bundled thumbnail once; absent assets never trigger generation."""
    if not isinstance(key, str) or not key or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_' for c in key):
        return None
    try:
        with Image.open(BASE / 'data' / 'source_thumbnails' / f'{key}.png') as image:
            if image.size != (64, 64):
                return None
            return image.convert('L').resize((24, 24), Image.Resampling.BILINEAR)
    except (OSError, ValueError):
        return None


class SourceSelect(ttk.Menubutton):
    """Read-only selector retaining the existing selected-event contract."""
    def __init__(self, parent, *, textvariable, options, width=22, state='readonly', photo_provider=None):
        super().__init__(parent, textvariable=textvariable, width=width,
                         state='disabled' if state == 'disabled' else 'normal', compound='left',
                         style='ImageSelect.TMenubutton')
        self.variable = textvariable
        self.options = dict(options)
        self.menu = tk.Menu(self, tearoff=False)
        self.configure(menu=self.menu)
        self.theme_owner = parent
        while getattr(self.theme_owner, 'master', None) is not None:
            self.theme_owner = self.theme_owner.master
        if not hasattr(self.theme_owner, '_themed_windows'):
            self.theme_owner._themed_windows = WeakSet()
        self.theme_owner._themed_windows.add(self)
        # One small PhotoImage per key and Tk interpreter, shared by all selectors.
        if not hasattr(self.theme_owner, '_source_thumbnail_photos'):
            self.theme_owner._source_thumbnail_photos = {}
        self.photos = self.theme_owner._source_thumbnail_photos
        for key, label in self.options.items():
            if key not in self.photos:
                if photo_provider is not None:
                    self.photos[key] = photo_provider(self.theme_owner, key)
                else:
                    image = reference_thumbnail(key)
                    self.photos[key] = ImageTk.PhotoImage(image, master=self.theme_owner) if image is not None else ''
            self.menu.add_command(label=label, image=self.photos[key], compound='left',
                                  command=lambda k=key: self.choose(k))
        self.trace = self.variable.trace_add('write', self._sync_thumbnail)
        self.bind('<Up>', lambda _event: self._step(-1))
        self.bind('<Down>', lambda _event: self._step(1))
        self.apply_palette(getattr(self.theme_owner, '_ui_theme_colors', {}))
        self._sync_thumbnail()

    def configure(self, cnf=None, **kwargs):
        if kwargs.get('state') == 'readonly':
            kwargs['state'] = 'normal'
        return super().configure(cnf, **kwargs)

    def _sync_thumbnail(self, *_args):
        key = next((k for k, v in self.options.items() if v == self.variable.get()), None)
        self.configure(image=self.photos.get(key, ''))

    def choose(self, key):
        if self.instate(['disabled']) or key not in self.options:
            return
        label = self.options[key]
        if label != self.variable.get():
            self.variable.set(label)
            self.event_generate('<<ComboboxSelected>>')

    def _step(self, amount):
        keys = list(self.options)
        current = next((k for k in keys if self.options[k] == self.variable.get()), None)
        if current is not None:
            self.choose(keys[max(0, min(len(keys) - 1, keys.index(current) + amount))])
        return 'break'

    def apply_palette(self, palette):
        roles = {'background': 'field', 'foreground': 'text',
                 'activebackground': 'selection', 'activeforeground': 'selection_text',
                 'disabledforeground': 'disabled'}
        self.menu.configure(**{option: palette[role] for option, role in roles.items() if role in palette})

    def destroy(self):
        self.variable.trace_remove('write', self.trace)
        self.theme_owner._themed_windows.discard(self)
        super().destroy()
