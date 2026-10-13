"""Application-owned windows using the current semantic palette.

New dialogs should use ThemedWindow instead of bare Tk Toplevel/simpledialog.
Native file pickers remain owned and styled by the operating system.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from weakref import WeakSet


class ThemedWindow(tk.Toplevel):
    def __init__(self, parent, *, colors=None):
        super().__init__(parent)
        self.theme_owner = parent
        while getattr(self.theme_owner, 'master', None) is not None:
            self.theme_owner = self.theme_owner.master
        self.colors = dict(colors or getattr(self.theme_owner, '_ui_theme_colors', {}))
        self._theme_widgets = []
        if not hasattr(self.theme_owner, '_themed_windows'):
            self.theme_owner._themed_windows = WeakSet()
        self.theme_owner._themed_windows.add(self)
        self.transient(parent.winfo_toplevel())
        self.apply_palette(getattr(self.theme_owner, '_ui_theme_colors', self.colors))

    def theme_widget(self, widget, **roles):
        """Register classic Tk options by semantic role, never by theme name."""
        self._theme_widgets.append((widget, roles))
        widget.configure(**{option: self.colors[role] for option, role in roles.items()
                            if role in self.colors})
        return widget

    def apply_palette(self, palette):
        self.colors = dict(palette)
        if 'window' in palette:
            self.configure(background=palette['window'])
        alive = []
        for widget, roles in self._theme_widgets:
            if widget.winfo_exists():
                widget.configure(**{option: palette[role] for option, role in roles.items()
                                    if role in palette})
                alive.append((widget, roles))
        self._theme_widgets = alive

    def destroy(self):
        self.theme_owner._themed_windows.discard(self)
        super().destroy()


def themed_prompt(parent, title, message, *, accept, cancel, initial=None, accept_image=None, cancel_image=None):
    """Modal text/confirmation dialog with keyboard focus and grab restoration."""
    dialog = ThemedWindow(parent, colors=getattr(parent, 'colors', None))
    dialog.withdraw()
    dialog.title(title)
    dialog.resizable(False, False)
    result = [None if initial is not None else False]
    previous_grab = parent.grab_current()
    ttk.Label(dialog, text=message, wraplength=440).grid(
        row=0, column=0, columnspan=2, sticky='w', padx=16, pady=12)
    value = tk.StringVar(dialog, value=initial or '')
    entry = None
    if initial is not None:
        entry = ttk.Entry(dialog, textvariable=value, width=40)
        entry.grid(row=1, column=0, columnspan=2, sticky='ew', padx=16, pady=(0, 10))

    def finish(confirmed=False):
        result[0] = value.get() if confirmed and initial is not None else (True if confirmed else result[0])
        dialog.destroy()
        if previous_grab is not None and previous_grab.winfo_exists():
            previous_grab.grab_set()
            previous_grab.focus_set()

    image_options = lambda image: {'image': image, 'compound': 'left', 'padding': (5,0,5,1)} if image is not None else {}
    ttk.Button(dialog, text=cancel, command=finish, **image_options(cancel_image)).grid(row=2, column=0, padx=16, pady=12)
    primary = ttk.Button(dialog, text=accept, style='Primary.TButton', command=lambda: finish(True), **image_options(accept_image))
    primary.grid(row=2, column=1, padx=16, pady=12)
    dialog.bind('<Escape>', lambda event: finish())
    dialog.bind('<Return>', lambda event: finish(True))
    dialog.protocol('WM_DELETE_WINDOW', finish)
    dialog.update_idletasks()
    owner = parent.winfo_toplevel()
    width, height = dialog.winfo_reqwidth(), dialog.winfo_reqheight()
    left = owner.winfo_rootx() + (owner.winfo_width() - width) // 2
    top = owner.winfo_rooty() + (owner.winfo_height() - height) // 2
    left = max(0, min(left, dialog.winfo_screenwidth() - width))
    top = max(0, min(top, dialog.winfo_screenheight() - height))
    dialog.geometry(f'+{left}+{top}')
    dialog.deiconify()
    dialog.wait_visibility()
    dialog.grab_set()
    if entry is not None:
        entry.focus_set()
        entry.selection_range(0, 'end')
    else:
        primary.focus_set()
    parent.wait_window(dialog)
    return result[0]
