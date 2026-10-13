"""General preview placement: layout and cached rendering, never generation."""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk


def choose_placement(width, height, previous=None):
    """Hysteresis prevents auto mode oscillating during an internal sash drag."""
    threshold = 1000 if previous == 'right' else 1120
    height_threshold = 620 if previous == 'right' else 650
    return 'right' if width >= threshold and height >= height_threshold else 'top'


class PreviewDockController:
    def _custom_preview_placement_options(self, language):
        labels = {
            'free': ('Vues libres', 'Free previews', 'Freie Vorschauen', 'Vistas libres'),
            'top': ('Vues fixées en haut', 'Previews pinned above', 'Vorschauen oben fixiert', 'Vistas fijadas arriba'),
            'right': ('Vues fixées à droite', 'Previews pinned right', 'Vorschauen rechts fixiert', 'Vistas fijadas a la derecha'),
            'auto': ('Placement automatique', 'Automatic placement', 'Automatische Platzierung', 'Ubicación automática'),
        }
        index = {'fr': 0, 'en': 1, 'de': 2, 'es': 3}.get(language, 0)
        return {key: value[index] for key, value in labels.items()}

    def _custom_destroy_preview_panel(self):
        panel = getattr(self, '_custom_preview_panel', None)
        if panel is not None:
            try: panel.destroy()
            except tk.TclError: pass
        self._custom_preview_panel = None

    def _custom_requested_preview_placement(self):
        inner = self._custom_archetype_tab
        if not hasattr(inner, '_preview_viewport'):
            return 'free'
        requested = self.prefs.get('archetype_preview_placement', 'free')
        if requested == 'auto':
            host = inner._scroll_host
            return choose_placement(host.winfo_width(), host.winfo_height(),
                                    getattr(self, '_custom_preview_effective_placement', None))
        return requested

    def _custom_fixed_preview_size(self, preferred):
        placement = getattr(self, '_custom_preview_effective_placement', 'free')
        inner = getattr(self, '_custom_archetype_tab', None)
        if placement == 'free' or not hasattr(inner, '_preview_viewport'):
            return preferred
        host = inner._scroll_host
        width = host.winfo_width() if host.winfo_width() > 1 else 760
        height = host.winfo_height() if host.winfo_height() > 1 else 550
        if placement == 'right':
            return max(48, min(preferred, 280, (height - 190) // 3 - 30))
        return max(48, min(preferred, (width - 80) // 3, int(height * .48) - 155))

    def _custom_rebuild_preview_panel(self):
        """Rebuild only the three-view surface when changing its Tk parent."""
        self._custom_destroy_preview_panel()
        inner = self._custom_archetype_tab
        placement = self._custom_requested_preview_placement()
        self._custom_preview_effective_placement = placement
        viewport = getattr(inner, '_preview_viewport', None)
        host = inner._scroll_host if viewport is not None else None
        if viewport is not None:
            viewport.grid_forget()
            host.rowconfigure(0, weight=1 if placement != 'top' else 0)
            host.rowconfigure(1, weight=1 if placement == 'top' else 0)
            host.columnconfigure(1, weight=0)
            viewport.grid(row=1 if placement == 'top' else 0, column=0, sticky='nsew')
        panel = self._custom_build_archetype_preview_panel(inner if placement == 'free' else host, placement)
        panel.grid(row=4 if placement == 'free' else 0,
                   column=1 if placement == 'right' else 0, sticky='nw')
        snapshot = getattr(self, '_custom_archetype_preview_last_snapshot', None)
        if snapshot is not None:
            noise, macro, side, seed = snapshot
            self._custom_render_archetype_preview_rasters(noise, macro, side, seed,
                noise_lab=getattr(self, '_custom_archetype_preview_last_lab', None),
                include_neutral_contribution=True)

    def _custom_preview_placement_changed(self, *_args):
        options = self._custom_preview_placement_options(self._custom_language())
        requested = next(k for k, v in options.items() if v == self._custom_preview_placement_var.get())
        self.prefs['archetype_preview_placement'] = requested
        self._custom_rebuild_preview_panel()
        self._schedule_prefs_save()

    def _custom_update_auto_preview_placement(self):
        if self.prefs.get('archetype_preview_placement') == 'auto':
            if self._custom_requested_preview_placement() != self._custom_preview_effective_placement:
                self._custom_rebuild_preview_panel()
                return True
        return False

    def _custom_enlarge_preview(self, key):
        """Enlarge the latest actual field, respecting its display projection."""
        snapshot = getattr(self, '_custom_archetype_preview_last_snapshot', None)
        if snapshot is None:
            return
        import numpy as np
        from ...generation.archetypes import noise_rgb, macro_rgb, noise_delta_rgb, project_preview_rgb
        from ..ui.theme.windows import ThemedWindow
        noise, macro, side, seed = snapshot
        lab = getattr(self, '_custom_archetype_preview_last_lab', None)
        raster = noise_rgb(noise) if key == 'noise' else (macro_rgb(macro) if key == 'macro'
            else noise_delta_rgb(lab.layer_delta if lab is not None else np.zeros_like(noise)))
        raster = project_preview_rgb(raster, self._custom_archetype_preview_projection_key)
        window = ThemedWindow(self)
        from .i18n import custom_section_text
        title_key = {"noise": "archetype_preview_noise", "macro": "archetype_preview_macro", "contribution": "archetype_noise_contribution_short"}[key]
        window.title(f"{custom_section_text(title_key, self._custom_language())} · {side} · seed {seed}")
        ttk.Label(window, text=self._custom_archetype_preview_stats_var.get(), wraplength=620, style='Hint.TLabel').pack(fill='x', padx=10, pady=6)
        if key == 'macro':
            from ...generation.archetypes import MACRO_PALETTE
            legend = ttk.Frame(window)
            legend.pack(fill='x', padx=10)
            for index, name in enumerate(('water', 'beach', 'grass', 'mountain', 'snow')):
                tk.Canvas(legend, width=12, height=12, highlightthickness=0,
                    background='#%02x%02x%02x' % MACRO_PALETTE[index]).grid(row=0, column=index * 2)
                ttk.Label(legend, text=custom_section_text(f'archetype_preview_{name}', self._custom_language())).grid(row=0, column=index * 2 + 1, padx=(3, 10))
        canvas = tk.Canvas(window, highlightthickness=0)
        window.theme_widget(canvas, background='window')
        canvas.pack(fill='both', expand=True)
        image = Image.fromarray(raster)
        item = canvas.create_image(0, 0, anchor='center')
        pending = [None]
        def draw():
            pending[0] = None
            width, height = max(1, canvas.winfo_width()), max(1, canvas.winfo_height())
            ratio = min(width / image.width, height / image.height)
            photo = ImageTk.PhotoImage(image.resize((max(1, round(image.width * ratio)), max(1, round(image.height * ratio))), Image.Resampling.NEAREST), master=window)
            canvas.photo = photo
            canvas.itemconfigure(item, image=photo)
            canvas.coords(item, width // 2, height // 2)
        def schedule(_event):
            if pending[0] is None: pending[0] = canvas.after_idle(draw)
        canvas.bind('<Configure>', schedule)
        window.geometry('650x650')
        window.bind('<Escape>', lambda _event: window.destroy())
