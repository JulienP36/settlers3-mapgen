"""Mask selector with provided shapes and directly selectable user PNGs."""
import tkinter as tk
from tkinter import ttk
from weakref import WeakSet
from collections import OrderedDict
from functools import lru_cache
import numpy as np
import hashlib
from PIL import Image, ImageTk


@lru_cache(maxsize=16)
def provided_thumbnail_grid(kind):
    from ...generation.archetypes.morphology import mask_template_grid
    return np.zeros((64, 64), dtype=np.uint8) if kind == "manual" else mask_template_grid(kind, 64)

from .mask_library import MaskCatalogue


class MaskSelect(ttk.Menubutton):
    def __init__(self, parent, *, variable, options, users_label, select_type,
                 select_file, enabled=True, catalogue=None, preview=None):
        super().__init__(parent, textvariable=variable, width=22,
                         state='normal' if enabled else 'disabled')
        self.preview = preview
        self._photos = OrderedDict()
        self._menu_photos = []
        self._preview_trace = variable.trace_add("write", self._update_thumbnail)
        self._variable = variable
        self.options = options
        self.users_label = users_label
        self.select_type = select_type
        self.select_file = select_file
        self.catalogue = catalogue or MaskCatalogue()
        self._scan_job = None
        self.menu = tk.Menu(self, tearoff=False, postcommand=self.refresh)
        self.users = tk.Menu(self.menu, tearoff=False)
        self.configure(menu=self.menu)
        self.theme_owner = parent
        while getattr(self.theme_owner, 'master', None) is not None:
            self.theme_owner = self.theme_owner.master
        if not hasattr(self.theme_owner, '_themed_windows'):
            self.theme_owner._themed_windows = WeakSet()
        self.theme_owner._themed_windows.add(self)
        self.apply_palette(getattr(self.theme_owner, '_ui_theme_colors', {}))
        self._update_thumbnail()

    def _photo(self, grid, key):
        if key in self._photos:
            self._photos.move_to_end(key)
            return self._photos[key]
        photo = ImageTk.PhotoImage(Image.fromarray(np.asarray(grid, dtype=np.uint8)).resize((24, 24), Image.Resampling.BILINEAR), master=self)
        self._photos[key] = photo
        while len(self._photos) > 128:
            self._photos.popitem(last=False)
        return photo

    def _update_thumbnail(self, *_args):
        if self.preview is None:
            return
        try:
            layer = self.preview()
            kind = layer['type']
            provider = layer.get('provider_settings', {})
            if kind == 'manual':
                side = int(provider.get('grid_side', 64))
                raw = provider.get('grid')
                grid = np.asarray(raw, dtype=np.uint8).reshape(side, side) if raw is not None else np.zeros((side, side), dtype=np.uint8)
                # The selected embedded copy is independent from its original PNG.
                key = ('selected', grid.shape, hashlib.blake2b(grid.tobytes(), digest_size=16).digest(), bool(layer.get('inverted', False)))
            else:
                grid = provided_thumbnail_grid(kind)
                key = ('provided', kind, bool(layer.get('inverted', False)))
            if layer.get('inverted', False):
                grid = 255 - grid
            self._selected_photo = self._photo(grid, key)
            self.configure(image=self._selected_photo, compound='left')
        except (AttributeError, KeyError, TypeError, ValueError, tk.TclError):
            return

    def apply_palette(self, palette):
        roles = {'background': 'field', 'foreground': 'text',
                 'activebackground': 'selection', 'activeforeground': 'selection_text',
                 'disabledforeground': 'disabled'}
        for menu in (self.menu, self.users):
            menu.configure(**{option: palette[role] for option, role in roles.items() if role in palette})

    def refresh(self):
        self.menu.delete(0, 'end')
        self._menu_photos.clear()
        self.users.delete(0, 'end')
        for key, label in self.options.items():
            photo = self._photo(provided_thumbnail_grid(key), ("provided", key, False))
            self._menu_photos.append(photo)
            self.menu.add_command(label=label, image=photo, compound="left", command=lambda k=key: self.choose_type(k))
        if self._scan_job is not None:
            self.after_cancel(self._scan_job)
            self._scan_job = None
        self.menu.add_separator()
        self.menu.add_cascade(label=self.users_label, menu=self.users, state='disabled')
        try:
            paths = iter(self.catalogue.paths())
        except OSError:
            return  # Folder diagnostics remain available in the catalogue.
        def add_next():
            self._scan_job = None
            try:
                path = next(paths)
            except StopIteration:
                return
            entry = self.catalogue.entry(path)
            if entry.grid is not None:
                photo = self._photo(entry.grid, ("file", path, hashlib.blake2b(entry.grid.tobytes(), digest_size=16).digest()))
                self._menu_photos.append(photo)
                self.users.add_command(label=path.stem, image=photo, compound="left", command=lambda p=path: self.choose_file(p))
                self.menu.entryconfigure('end', state='normal')
            self._scan_job = self.after_idle(add_next)
        self._scan_job = self.after_idle(add_next)

    def choose_type(self, key):
        if not self.instate(['disabled']):
            self.select_type(key)

    def choose_file(self, path):
        if not self.instate(['disabled']):
            self.select_file(path)

    def destroy(self):
        if self._scan_job is not None:
            self.after_cancel(self._scan_job)
            self._scan_job = None
        self._variable.trace_remove("write", self._preview_trace)
        self._photos.clear()
        self.theme_owner._themed_windows.discard(self)
        super().destroy()
