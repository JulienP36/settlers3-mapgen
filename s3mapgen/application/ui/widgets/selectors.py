"""Reusable selector widgets with deterministic raster entry icons."""

import tkinter as tk
from tkinter import ttk

from .icons import _selector_icon


class ColorMenuSelect(ttk.Menubutton):
    """Menubutton-backed dropdown supporting a real colored icon per entry."""

    def __init__(self, master, variable, width=20, command=None):
        super().__init__(master, textvariable=variable, width=width, compound="left", style="ImageSelect.TMenubutton")
        self.variable = variable
        self.command = command
        self.menu = tk.Menu(self, tearoff=False)
        self.configure(menu=self.menu)
        self._icons = {}
        self._items = []
        self._enabled = True
        self.bind("<MouseWheel>", self._on_mousewheel, add="+")
        self.bind("<Button-4>", lambda event: self._wheel_step(-1), add="+")
        self.bind("<Button-5>", lambda event: self._wheel_step(1), add="+")

    def set_items(self, items):
        current = self.variable.get()
        self._items = list(items)
        self.menu.delete(0, "end")
        self._icons = {}
        for key, label, color, kind in self._items:
            icon = _selector_icon(self, color, kind)
            self._icons[key] = icon
            self.menu.add_command(label=label, image=icon, compound="left", command=lambda k=key, value=label: self._choose(k, value))
        labels = [item[1] for item in self._items]
        if current not in labels and labels:
            self.variable.set(labels[0])
        self._sync_icon()

    def _choose(self, key, label):
        if not self._enabled:
            return
        self.variable.set(label)
        self._sync_icon()
        if self.command:
            self.command()

    def _sync_icon(self):
        value = self.variable.get()
        for key, label, _, _ in self._items:
            if label == value:
                ttk.Menubutton.configure(self, image=self._icons.get(key, ""))
                break

    def _wheel_step(self, step):
        if not self._enabled or not self._items:
            return "break"
        labels = [item[1] for item in self._items]
        try:
            index = labels.index(self.variable.get())
        except ValueError:
            index = 0
        index = max(0, min(len(labels) - 1, index + int(step)))
        key, label, _, _ = self._items[index]
        self._choose(key, label)
        return "break"

    def _on_mousewheel(self, event):
        delta = getattr(event, "delta", 0)
        if not delta:
            return "break"
        return self._wheel_step(-1 if delta > 0 else 1)

    def set_enabled(self, enabled=True):
        self._enabled = bool(enabled)
        ttk.Menubutton.configure(self, state="normal" if enabled else "disabled")

    def set_menu_theme(self, bg, fg, active_bg, active_fg):
        try:
            self.menu.configure(background=bg, foreground=fg, activebackground=active_bg, activeforeground=active_fg)
        except tk.TclError:
            pass
