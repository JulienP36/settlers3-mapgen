"""Reusable grayscale editor and lazily populated user-mask catalogue."""
from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, font

import numpy as np
from PIL import Image, ImageTk

from ...generation.archetypes.morphology import mask_template_grid
from ..ui.theme.windows import ThemedWindow, themed_prompt
from .source_selector import SourceSelect
from ..ui.sprites import sprite_photo
from ..ui.layout import flow_rows
from .mask_library import (
    MASK_SIDES, MaskCatalogue, MaskDrawing, MaskImageError,
    fit_mask, read_mask_image, square_resolution,
)

TEXT = {
    'new': ('Nouveau masque', 'New mask', 'Neue Maske', 'Nueva máscara'),
    'shape': ('Forme du pinceau', 'Brush shape', 'Pinselform', 'Forma del pincel'),
    'round': ('Rond', 'Round', 'Rund', 'Redondo'),
    'square': ('Carré', 'Square', 'Quadratisch', 'Cuadrado'),
    'new_hint': ('Nouveau dessin : choisir une résolution, dessiner puis enregistrer sous un nom.', 'New drawing: choose a resolution, draw, then save with a name.', 'Neue Zeichnung: Auflösung wählen, zeichnen und unter einem Namen speichern.', 'Nuevo dibujo: elegir resolución, dibujar y guardar con un nombre.'),
    'title': ('Éditeur de masque', 'Mask editor', 'Maskeneditor', 'Editor de máscaras'),
    'catalogue': ('Catalogue', 'Catalogue', 'Katalog', 'Catálogo'),
    'provided': ('Fournis — protégés', 'Provided — protected', 'Mitgeliefert — geschützt', 'Incluidos — protegidos'),
    'variable': ('Variable', 'Variable', 'Variabel', 'Variable'),
    'users': ('Utilisateur — modifiables', 'User — editable', 'Benutzer — bearbeitbar', 'Usuario — editables'),
    'folder': ('Ouvrir le dossier', 'Open folder', 'Ordner öffnen', 'Abrir carpeta'),
    'refresh': ('Actualiser', 'Refresh', 'Aktualisieren', 'Actualizar'),
    'load': ('Charger une copie', 'Load a copy', 'Kopie laden', 'Cargar una copia'),
    'delete': ('Supprimer le fichier', 'Delete file', 'Datei löschen', 'Eliminar archivo'),
    'resolution': ('Résolution', 'Resolution', 'Auflösung', 'Resolución'),
    'gray': ('Gris (0–255)', 'Gray (0–255)', 'Grau (0–255)', 'Gris (0–255)'),
    'size': ('Rayon du pinceau (pixels)', 'Brush radius (pixels)', 'Pinselradius (Pixel)', 'Radio del pincel (píxeles)'),
    'softness': ('Bord doux (%)', 'Soft edge (%)', 'Weicher Rand (%)', 'Borde suave (%)'),
    'brush': ('Pinceau', 'Brush', 'Pinsel', 'Pincel'),
    'eraser': ('Gomme', 'Eraser', 'Radierer', 'Goma'),
    'picker': ('Pipette', 'Eyedropper', 'Pipette', 'Cuentagotas'),
    'fill': ('Remplissage', 'Fill', 'Füllen', 'Relleno'),
    'rotate_left': ('90° à gauche', '90° left', '90° links', '90° izquierda'),
    'rotate_right': ('90° à droite', '90° right', '90° rechts', '90° derecha'),
    'undo': ('Annuler l’action', 'Undo', 'Rückgängig', 'Deshacer'),
    'redo': ('Rétablir', 'Redo', 'Wiederholen', 'Rehacer'),
    'clear': ('Effacer tout', 'Clear all', 'Alles löschen', 'Borrar todo'),
    'invert': ('Inverser les gris', 'Invert grays', 'Grau invertieren', 'Invertir grises'),
    'flip_x': ('Miroir horizontal', 'Horizontal flip', 'Horizontal spiegeln', 'Reflejo horizontal'),
    'flip_y': ('Miroir vertical', 'Vertical flip', 'Vertikal spiegeln', 'Reflejo vertical'),
    'rotate': ('Tourner de 90°', 'Rotate 90°', 'Um 90° drehen', 'Girar 90°'),
    'import': ('Importer une image', 'Import image', 'Bild importieren', 'Importar imagen'),
    'export': ('Exporter en PNG', 'Export PNG', 'PNG exportieren', 'Exportar PNG'),
    'save': ('Enregistrer dans mes masques', 'Save to my masks', 'In eigenen Masken speichern', 'Guardar en mis máscaras'),
    'apply': ('Appliquer au profil', 'Apply to profile', 'Auf Profil anwenden', 'Aplicar al perfil'),
    'cancel': ('Fermer', 'Close', 'Schließen', 'Cerrar'),
    'abort': ('Annuler', 'Cancel', 'Abbrechen', 'Cancelar'),
    'confirm': ('Confirmer', 'Confirm', 'Bestätigen', 'Confirmar'),
    'unnamed': ('Sans nom', 'Untitled', 'Unbenannt', 'Sin nombre'),
    'file_dirty': ('PNG : non enregistré', 'PNG: unsaved', 'PNG: nicht gespeichert', 'PNG: sin guardar'),
    'file_saved': ('PNG : enregistré', 'PNG: saved', 'PNG: gespeichert', 'PNG: guardado'),
    'profile_dirty': ('Profil : modifications non appliquées', 'Profile: unapplied changes', 'Profil: Änderungen nicht angewendet', 'Perfil: cambios sin aplicar'),
    'profile_same': ('Profil : dessin identique', 'Profile: same drawing', 'Profil: gleiche Zeichnung', 'Perfil: dibujo idéntico'),
    'replace_drawing': ('Remplacer le dessin actuel ? Les modifications non enregistrées seront perdues.', 'Replace the current drawing? Unsaved changes will be lost.', 'Aktuelle Zeichnung ersetzen? Ungespeicherte Änderungen gehen verloren.', '¿Reemplazar el dibujo actual? Se perderán los cambios sin guardar.'),
    'hint': ('Noir = 0 · blanc = 255 · gris = influence intermédiaire\nClic droit : gomme · Ctrl+Z/Y : annuler/rétablir',
             'Black = 0 · white = 255 · gray = intermediate influence\nRight click: eraser · Ctrl+Z/Y: undo/redo',
             'Schwarz = 0 · Weiß = 255 · Grau = mittlerer Einfluss\nRechtsklick: Radierer · Strg+Z/Y: rückgängig/wiederholen',
             'Negro = 0 · blanco = 255 · gris = influencia intermedia\nClic derecho: goma · Ctrl+Z/Y: deshacer/rehacer'),
    'name_prompt': ('Nom du masque', 'Mask name', 'Maskenname', 'Nombre de máscara'),
    'overwrite': ('Remplacer le masque existant ?', 'Replace the existing mask?', 'Vorhandene Maske ersetzen?', '¿Reemplazar la máscara existente?'),
    'delete_prompt': ('Supprimer ce fichier ? Les copies déjà appliquées aux profils sont conservées.', 'Delete this file? Copies already applied to profiles are kept.', 'Datei löschen? Bereits auf Profile angewendete Kopien bleiben erhalten.', '¿Eliminar este archivo? Se conservan las copias aplicadas a perfiles.'),
    'discard': ('Fermer sans appliquer les modifications au profil ?', 'Close without applying changes to the profile?', 'Ohne Anwendung der Änderungen auf das Profil schließen?', '¿Cerrar sin aplicar los cambios al perfil?'),
    'saved': ('Masque enregistré.', 'Mask saved.', 'Maske gespeichert.', 'Máscara guardada.'),
    'framing': ('Image rectangulaire : choisir le cadrage', 'Rectangular image: choose framing', 'Rechteckiges Bild: Zuschnitt wählen', 'Imagen rectangular: elegir encuadre'),
    'pad': ('Conserver avec marges noires', 'Keep with black margins', 'Mit schwarzen Rändern behalten', 'Conservar con márgenes negros'),
    'crop': ('Recadrer au centre', 'Crop at center', 'Mittig zuschneiden', 'Recortar al centro'),
    'stretch': ('Étirer en carré', 'Stretch to square', 'Zum Quadrat strecken', 'Estirar a cuadrado'),
    'too_large': ('Image trop grande (2048 px / 32 Mio maximum).', 'Image too large (2048 px / 32 MiB maximum).', 'Bild zu groß (max. 2048 px / 32 MiB).', 'Imagen demasiado grande (máx. 2048 px / 32 MiB).'),
    'not_png': ('Le contenu de ce fichier n’est pas un PNG.', 'The file content is not PNG.', 'Der Dateiinhalt ist kein PNG.', 'El contenido no es PNG.'),
    'animated': ('Les images animées ne sont pas acceptées.', 'Animated images are not accepted.', 'Animierte Bilder werden nicht akzeptiert.', 'No se aceptan imágenes animadas.'),
    'unreadable': ('Image illisible ou incomplète.', 'Unreadable or incomplete image.', 'Unlesbares oder unvollständiges Bild.', 'Imagen ilegible o incompleta.'),
    'rectangular': ('Rectangulaire : choisir un cadrage à l’import.', 'Rectangular: choose framing on import.', 'Rechteckig: Zuschnitt beim Import wählen.', 'Rectangular: elegir encuadre al importar.'),
    'uniform': ('Masque uniforme — utilisable.', 'Uniform mask — usable.', 'Einheitliche Maske — verwendbar.', 'Máscara uniforme — utilizable.'),
    'name': ('Nom invalide ou réservé.', 'Invalid or reserved name.', 'Ungültiger oder reservierter Name.', 'Nombre inválido o reservado.'),
    'protected': ('Ce fichier est protégé.', 'This file is protected.', 'Diese Datei ist geschützt.', 'Este archivo está protegido.'),
    'resolution_error': ('Résolution : 64, 128, 256 ou 512.', 'Resolution: 64, 128, 256 or 512.', 'Auflösung: 64, 128, 256 oder 512.', 'Resolución: 64, 128, 256 o 512.'),
    'snapshot': ('Copie indépendante : modifier le fichier ne modifie pas ce profil.', 'Independent copy: changing the file does not change this profile.', 'Unabhängige Kopie: Dateiänderungen ändern dieses Profil nicht.', 'Copia independiente: cambiar el archivo no cambia este perfil.'),
}
LANG_INDEX = {'fr': 0, 'en': 1, 'de': 2, 'es': 3}


class MaskEditor(ThemedWindow):
    def __init__(self, parent, grid, *, language, colors, templates, apply, name=""):
        super().__init__(parent, colors=colors)
        # Normal owned themed editor: allow native maximize controls.
        self.transient('')
        self.language = language
        self.templates = templates
        self.apply_callback = apply
        self.catalogue = MaskCatalogue()
        self.drawing = MaskDrawing(grid)
        self.initial_grid = self.drawing.grid.copy()
        self.document_grid = self.drawing.grid.copy()
        self.mask_name = name if isinstance(name, str) else ''
        self.saved_grid = None
        self.pointer = None
        self.cursor_items = []
        self.last_point = None
        self.render_job = None
        self.title(self.text('title'))
        self.resizable(True, True)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.side = tk.StringVar(value=str(grid.shape[0]))
        self.gray = tk.StringVar(value='255')
        self.radius = tk.StringVar(value='4')
        self.softness = tk.StringVar(value='0')
        self.tool = tk.StringVar(value=self.text('brush'))
        self.shape = tk.StringVar(value=self.text('round'))
        self.numeric_vars = {'gray': self.gray, 'size': self.radius, 'softness': self.softness}
        self.numeric_limits = {'gray': (0, 255, 255), 'size': (1, 128, 4), 'softness': (0, 100, 0)}
        self.slider_vars = {}
        self.numeric_traces = []
        self.status = tk.StringVar(value=self.text('snapshot'))
        self.canvas_side = max(256, min(420, self.winfo_screenheight()-240))
        self.canvas = tk.Canvas(self, width=self.canvas_side, height=self.canvas_side,
                                highlightthickness=1, highlightbackground=colors.get('border', '#777'))
        self.canvas.grid(row=0, column=0, rowspan=16, sticky='nsew', padx=8, pady=8)
        self.theme_widget(self.canvas, background='canvas', highlightbackground='border', highlightcolor='border')
        self.canvas.bind('<Configure>', self.resize_view)
        self.canvas.bind('<Motion>', self.cursor_motion)
        self.canvas.bind('<Leave>', lambda event: self.hide_cursor())
        controls = ttk.Frame(self)
        controls.grid(row=0, column=1, rowspan=16, sticky='n', padx=(0, 8), pady=8)
        row = 0
        for key, var, values in [('resolution', self.side, tuple(map(str, MASK_SIDES))),
                                 ('brush', self.tool, tuple(self.text(t) for t in ('brush', 'eraser', 'picker', 'fill'))),
                                 ('shape', self.shape, tuple(self.text(t) for t in ('round', 'square')))]:
            ttk.Label(controls, text=self.text(key)).grid(row=row, column=0, sticky='w')
            if key == 'resolution':
                box = ttk.Combobox(controls, textvariable=var, values=values, state='readonly', width=12)
            else:
                tools = ('brush', 'eraser', 'picker', 'fill') if key == 'brush' else ('round', 'square')
                box = SourceSelect(controls, textvariable=var,
                                   options={f'mask/{tool}': self.text(tool) for tool in tools},
                                   width=12, photo_provider=sprite_photo)
                setattr(self, 'tool_selector' if key == 'brush' else 'shape_selector', box)
            box.grid(row=row, column=1, sticky='e', pady=2)
            if key == 'resolution':
                box.bind('<<ComboboxSelected>>', self.resize_grid)
            if key in ('shape', 'brush'):
                box.bind('<<ComboboxSelected>>', lambda event: self.update_cursor())
            row += 1
        for key, var, maximum in [('gray', self.gray, 255), ('size', self.radius, 128), ('softness', self.softness, 100)]:
            low, high, default = self.numeric_limits[key]
            ttk.Label(controls, text=self.text(key)).grid(row=row, column=0, sticky='w')
            spin = ttk.Spinbox(controls, from_=low, to=maximum, textvariable=var, width=7)
            spin.grid(row=row, column=1, sticky='e', pady=2)
            spin.bind('<FocusOut>', lambda event, k=key: self.finish_numeric(k))
            row += 1
            slider_line = ttk.Frame(controls)
            slider_line.grid(row=row, column=0, columnspan=2, sticky='ew')
            slider_line.columnconfigure(0, weight=1)
            slider_var = tk.DoubleVar(value=default)
            self.slider_vars[key] = slider_var
            ttk.Scale(slider_line, from_=low, to=high, variable=slider_var,
                      command=lambda value, k=key: self.slider_changed(k, value)).grid(row=0, column=0, sticky='ew')
            if key == 'gray':
                self.gray_preview = tk.Canvas(slider_line, width=28, height=18, highlightthickness=1,
                                              highlightbackground=colors.get('border', '#777'))
                self.gray_preview.grid(row=0, column=1, padx=(6, 0))
                self.theme_widget(self.gray_preview, highlightbackground='border', highlightcolor='border')
            row += 1
            if key == 'gray':
                gradient = tk.Canvas(controls, width=250, height=10, highlightthickness=0)
                gradient.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0, 3))
                for value in range(256):
                    shade = f'#{value:02x}{value:02x}{value:02x}'
                    gradient.create_rectangle(value*250/256, 0, (value+1)*250/256, 10,
                                              fill=shade, outline=shade)
                gradient.bind('<Button-1>', lambda event: self.gray.set(str(round(max(0, min(255, event.x/max(1, gradient.winfo_width()-1)*255))))))
                gradient.bind('<B1-Motion>', lambda event: self.gray.set(str(round(max(0, min(255, event.x/max(1, gradient.winfo_width()-1)*255))))))
                row += 1
            token = var.trace_add('write', lambda *args, k=key: self.sync_numeric(k))
            self.numeric_traces.append((var, token))
            self.sync_numeric(key)
        self.undo_button = ttk.Button(controls, text=self.text('undo'), image=sprite_photo(self, 'mask/undo'), compound='left', padding=(5,0,5,1), command=lambda: self.history('undo'))
        self.redo_button = ttk.Button(controls, text=self.text('redo'), image=sprite_photo(self, 'mask/redo'), compound='left', padding=(5,0,5,1), command=lambda: self.history('redo'))
        self.undo_button.grid(row=row, column=0, sticky='ew', padx=2, pady=1)
        self.redo_button.grid(row=row, column=1, sticky='ew', padx=2, pady=1)
        row += 1
        operations = [('clear', lambda g: np.zeros_like(g)), ('invert', lambda g: 255-g),
                      ('flip_x', np.flipud), ('flip_y', np.fliplr),
                      ('rotate_left', np.rot90), ('rotate_right', lambda g: np.rot90(g, -1))]
        self.operation_buttons = {}
        for position, (key, operation) in enumerate(operations):
            button = ttk.Button(controls, text=self.text(key), command=lambda op=operation: self.transform(op))
            button.configure(image=sprite_photo(self, f'mask/{key}'), compound='left', padding=(5,0,5,1))
            self.operation_buttons[key] = button
            button.grid(
                row=row+position//2, column=position%2,
                columnspan=1, sticky='ew', padx=2, pady=1)
        row += 3
        actions = [('import', self.import_image), ('export', self.export_image),
                   ('catalogue', self.open_catalogue)]
        for position, (key, command) in enumerate(actions):
            self.sprite_button(controls, key, command=command).grid(
                row=row+position//2, column=position%2, columnspan=2 if key == 'catalogue' else 1,
                sticky='ew', padx=2, pady=1)
        self.document_status = tk.StringVar(self)
        document_label = ttk.Label(self, textvariable=self.document_status, wraplength=700)
        document_label.grid(row=16, column=0, columnspan=2, sticky='w', padx=8)
        ttk.Label(self, text=self.text('hint'), style='Hint.TLabel').grid(row=17, column=0, columnspan=2, sticky='w', padx=8)
        status_label = ttk.Label(self, textvariable=self.status, wraplength=700)
        status_label.grid(row=18, column=0, columnspan=2, sticky='w', padx=8, pady=4)
        footer = ttk.Frame(self)
        footer.grid(row=19, column=0, columnspan=2, sticky='e', padx=8, pady=8)
        self.sprite_button(footer, 'cancel', command=self.close).grid(row=0, column=0, padx=4, pady=2)
        self.sprite_button(footer, 'save', command=self.save_mask).grid(row=0, column=1, padx=4, pady=2)
        self.sprite_button(footer, 'apply', style='Primary.TButton', command=self.apply_profile).grid(row=0, column=2, padx=4, pady=2)
        for button in (1, 3):
            self.canvas.bind(f'<Button-{button}>', lambda event, b=button: self.start_stroke(event, b))
            self.canvas.bind(f'<B{button}-Motion>', lambda event, b=button: self.move_stroke(event, b))
            self.canvas.bind(f'<ButtonRelease-{button}>', lambda event: self.end_stroke())
        self.bind('<Control-z>', lambda event: self.history('undo'))
        self.bind('<Control-y>', lambda event: self.history('redo'))
        self.protocol('WM_DELETE_WINDOW', self.close)
        if self.mask_name:
            try:
                path = next((p for p in self.catalogue.paths() if p.stem == self.mask_name), None)
                entry = self.catalogue.entry(path) if path is not None else None
                if entry is not None and entry.grid is not None:
                    self.saved_grid = entry.grid.copy()
            except OSError:
                pass
        self.redraw()
        self.update_idletasks()
        self.geometry(f'{self.winfo_reqwidth()}x{self.winfo_reqheight()}')
        self.minsize(self.winfo_reqwidth() - self.canvas_side + 256, self.winfo_reqheight())
        def wrap_status(event):
            if event.widget is self:
                for label in (document_label, status_label):
                    label.configure(wraplength=max(1, event.width - 16))
        self.bind('<Configure>', wrap_status, add='+')
        self.grab_set()
        self.focus_set()

    def sprite_button(self, parent, key, **options):
        sprite_key = 'import' if key == 'load' else key
        return ttk.Button(parent, text=self.text(key), image=sprite_photo(self, f'mask/{sprite_key}'),
                          compound='left', padding=(5,0,5,1), **options)

    def bind_tip(self, widget, text):
        """Keep catalogue tooltips owned by their widget and theme-aware."""
        popup = [None]
        def hide(event=None):
            if popup[0] is not None:
                tip, popup[0] = popup[0], None
                if tip.winfo_exists():
                    tip.destroy()
        def show(event=None):
            hide()
            tip = popup[0] = ThemedWindow(widget, colors=self.colors)
            tip.withdraw()
            tip.overrideredirect(True)
            tip.attributes('-topmost', True)
            label = tk.Label(tip, text=text, justify='left', wraplength=360,
                             padx=7, pady=5, bd=1, relief='solid')
            tip.theme_widget(label, background='surface', foreground='text')
            label.pack()
            tip.update_idletasks()
            x = min(widget.winfo_rootx()+8, tip.winfo_screenwidth()-tip.winfo_reqwidth()-6)
            y = min(widget.winfo_rooty()+widget.winfo_height()+6,
                    tip.winfo_screenheight()-tip.winfo_reqheight()-42)
            tip.geometry(f'+{max(6,x)}+{max(6,y)}')
            tip.deiconify()
            tip.lift()
        for event in ('<Enter>', '<FocusIn>'):
            widget.bind(event, show, add='+')
        for event in ('<Leave>', '<FocusOut>', '<ButtonPress>', '<Destroy>'):
            widget.bind(event, hide, add='+')

    def text(self, key):
        return TEXT.get(key, (key,)*4)[LANG_INDEX.get(self.language, 0)]

    def error(self, exc):
        key = str(exc)
        self.status.set(self.text('resolution_error' if key == 'resolution' else key))

    @staticmethod
    def number(var, low, high, default):
        try:
            return max(low, min(high, int(round(float(var.get())))))
        except (ValueError, TypeError, OverflowError):
            return default

    def slider_changed(self, key, value):
        low, high, default = self.numeric_limits[key]
        try:
            numeric = max(low, min(high, int(round(float(value)))))
        except (ValueError, TypeError, OverflowError):
            return
        self.numeric_vars[key].set(str(numeric))

    def sync_numeric(self, key):
        var = self.numeric_vars[key]
        low, high, default = self.numeric_limits[key]
        try:
            numeric = max(low, min(high, int(round(float(var.get())))))
        except (ValueError, TypeError, OverflowError):
            # Keep the last visual value while the user edits a numeric field.
            return
        if self.slider_vars[key].get() != numeric:
            self.slider_vars[key].set(numeric)
        if key == 'gray':
            shade = f'#{numeric:02x}{numeric:02x}{numeric:02x}'
            self.gray_preview.configure(background=shade)
        if key == 'size' and hasattr(self, 'pointer'):
            self.update_cursor()

    def finish_numeric(self, key):
        low, high, default = self.numeric_limits[key]
        self.numeric_vars[key].set(str(self.number(self.numeric_vars[key], low, high, default)))

    def confirm(self, message, *, parent=None, title=None):
        return themed_prompt(parent or self, title or self.text('title'), message,
                             accept=self.text('confirm'), cancel=self.text('abort'),
                                  accept_image=sprite_photo(self, 'mask/apply'), cancel_image=sprite_photo(self, 'mask/cancel'))

    def may_replace(self):
        baseline = self.saved_grid if self.saved_grid is not None else self.document_grid
        return self.same_grid(self.drawing.grid, baseline) or self.confirm(self.text('replace_drawing'))

    @staticmethod
    def same_grid(first, second):
        return second is not None and first.shape == second.shape and np.array_equal(first, second)

    def update_document_status(self):
        file_state = 'file_saved' if self.same_grid(self.drawing.grid, self.saved_grid) else 'file_dirty'
        profile_state = 'profile_same' if self.same_grid(self.drawing.grid, self.initial_grid) else 'profile_dirty'
        self.document_status.set(f"{self.mask_name or self.text('unnamed')} · {self.text(file_state)} · {self.text(profile_state)}")

    def new_mask(self):
        if not self.may_replace():
            return False
        self.end_stroke()
        self.drawing = MaskDrawing(np.zeros_like(self.drawing.grid))
        self.document_grid = self.drawing.grid.copy()
        self.mask_name = ''
        self.saved_grid = None
        self.status.set(self.text('new_hint'))
        self.queue_redraw()
        return True

    def resize_view(self, event):
        self.canvas_side = max(1, min(event.width - 2, event.height - 2))
        self.queue_redraw()

    def view_origin(self):
        return ((self.canvas.winfo_width() - self.canvas_side) // 2,
                (self.canvas.winfo_height() - self.canvas_side) // 2)

    def hide_cursor(self):
        self.pointer = None
        for item in self.cursor_items:
            self.canvas.itemconfigure(item, state='hidden')

    def cursor_motion(self, event):
        self.pointer = (event.x, event.y)
        self.update_cursor()

    def update_cursor(self):
        for item in self.cursor_items:
            self.canvas.delete(item)
        self.cursor_items.clear()
        if self.pointer is None or self.tool.get() in (self.text('picker'), self.text('fill')):
            return
        x, y = self.pointer
        ox, oy = self.view_origin()
        if not (ox <= x < ox + self.canvas_side and oy <= y < oy + self.canvas_side):
            return
        radius = self.number(self.radius, 1, 128, 4) * (self.canvas_side - 1) / max(1, self.drawing.grid.shape[0] - 1)
        draw = self.canvas.create_rectangle if self.shape.get() == self.text('square') else self.canvas.create_oval
        for color, width in (('#000000', 3), ('#ffffff', 1)):
            self.cursor_items.append(draw(x-radius, y-radius, x+radius, y+radius, outline=color, width=width))

    def redraw(self):
        self.render_job = None
        image = Image.fromarray(self.drawing.grid).resize((self.canvas_side,)*2, Image.Resampling.NEAREST)
        photo = ImageTk.PhotoImage(image, master=self)
        if hasattr(self, 'image_item'):
            self.canvas.itemconfigure(self.image_item, image=photo)
        else:
            self.image_item = self.canvas.create_image(0, 0, anchor='nw', image=photo)
        self.photo = photo
        self.canvas.coords(self.image_item, *self.view_origin())
        self.update_cursor()
        self.update_document_status()
        self.side.set(str(self.drawing.grid.shape[0]))
        self.undo_button.configure(state='normal' if self.drawing.undo_stack else 'disabled')
        self.redo_button.configure(state='normal' if self.drawing.redo_stack else 'disabled')

    def queue_redraw(self):
        if self.render_job is None:
            self.render_job = self.after_idle(self.redraw)

    def point(self, event):
        ox, oy = self.view_origin()
        x, y = event.x - ox, event.y - oy
        if not (0 <= x < self.canvas_side and 0 <= y < self.canvas_side):
            return None
        scale = (self.drawing.grid.shape[0]-1) / max(1, self.canvas_side-1)
        return (x*scale, y*scale)

    def start_stroke(self, event, button):
        point = self.point(event)
        if point is None:
            return
        self.cursor_motion(event)
        if button == 1 and self.tool.get() == self.text('picker'):
            self.gray.set(str(int(self.drawing.grid[int(round(point[1])), int(round(point[0]))])))
            self.last_point = None
            return
        if button == 1 and self.tool.get() == self.text('fill'):
            self.end_stroke()
            if self.drawing.fill(int(round(point[0])), int(round(point[1])), self.number(self.gray, 0, 255, 255)):
                self.queue_redraw()
            return
        self.drawing.checkpoint()
        self.last_point = point
        self.move_stroke(event, button)

    def move_stroke(self, event, button):
        if self.last_point is None:
            return
        point = self.point(event)
        self.cursor_motion(event)
        if point is None:
            self.end_stroke()
            return
        value = 0 if button == 3 or self.tool.get() == self.text('eraser') else self.number(self.gray, 0, 255, 255)
        self.drawing.stroke(self.last_point, point, self.number(self.radius, 1, 128, 4), value,
                            self.number(self.softness, 0, 100, 0)/100,
                            'square' if self.shape.get() == self.text('square') else 'round')
        self.last_point = point
        self.queue_redraw()

    def end_stroke(self):
        self.last_point = None

    def transform(self, operation):
        self.end_stroke()
        self.drawing.replace(operation(self.drawing.grid))
        self.queue_redraw()

    def history(self, action):
        self.end_stroke()
        getattr(self.drawing, action)()
        self.queue_redraw()
        return 'break'

    def resize_grid(self, event=None):
        side = self.number(self.side, 64, 512, 64)
        if side in MASK_SIDES and side != self.drawing.grid.shape[0]:
            self.drawing.replace(fit_mask(Image.fromarray(self.drawing.grid), side))
            self.queue_redraw()

    def load_image(self, image, *, name=''):
        side = square_resolution(image)
        def commit(framing):
            if not self.may_replace():
                return
            self.end_stroke()
            self.drawing = MaskDrawing(fit_mask(image, side, framing))
            self.document_grid = self.drawing.grid.copy()
            self.saved_grid = None
            self.mask_name = name
            self.status.set(f'{image.width} × {image.height} → {side} × {side}. '+self.text('snapshot'))
            self.queue_redraw()
        if image.width == image.height:
            commit('pad')
            return
        dialog = ThemedWindow(self, colors=self.colors)
        dialog.transient(self)
        dialog.title(self.text('framing'))
        dialog.configure(background=self.colors.get('window', '#202124'))
        photos = []
        def select(kind):
            commit(kind)
            dialog.destroy()
            self.grab_set()
        for column, kind in enumerate(('pad', 'crop', 'stretch')):
            preview = Image.fromarray(fit_mask(image, 128, kind))
            photo = ImageTk.PhotoImage(preview, master=dialog)
            photos.append(photo)
            ttk.Label(dialog, image=photo).grid(row=0, column=column, padx=6, pady=6)
            ttk.Button(dialog, text=self.text(kind), command=lambda k=kind: select(k)).grid(row=1, column=column, padx=6, pady=6)
        dialog.photos = photos
        def cancel():
            dialog.destroy()
            self.grab_set()
        dialog.protocol('WM_DELETE_WINDOW', cancel)
        dialog.grab_set()

    def import_image(self):
        path = filedialog.askopenfilename(parent=self, title=self.text('import'),
                    filetypes=[('Images', '*.png *.jpg *.jpeg *.bmp')])
        if path:
            try:
                self.load_image(read_mask_image(path), name='')
            except (OSError, MaskImageError) as exc:
                self.error(exc)

    def save_mask(self):
        self.end_stroke()
        name = themed_prompt(self, self.text('save'), self.text('name_prompt'),
                             initial=self.mask_name, accept=self.text('save'), cancel=self.text('abort'),
                             accept_image=sprite_photo(self, 'mask/save'), cancel_image=sprite_photo(self, 'mask/cancel'))
        if name is None:
            return
        try:
            try:
                path = self.catalogue.save(name, self.drawing.grid)
            except FileExistsError:
                if not self.confirm(self.text('overwrite'), title=self.text('save')):
                    return
                path = self.catalogue.save(name, self.drawing.grid, overwrite=True)
            self.mask_name = path.stem
            self.saved_grid = self.drawing.grid.copy()
            self.update_document_status()
            self.status.set(self.text('saved')+' '+path.name)
        except (OSError, MaskImageError) as exc:
            self.error(exc)

    def export_image(self):
        path = filedialog.asksaveasfilename(parent=self, title=self.text('export'),
                                           defaultextension='.png', filetypes=[('PNG', '*.png')])
        if path:
            try:
                Image.fromarray(self.drawing.grid).save(path, format='PNG')
                self.status.set(self.text('saved'))
            except (OSError, ValueError) as exc:
                self.error(exc)

    def open_folder(self):
        try:
            directory = self.catalogue.directory
            directory.mkdir(parents=True, exist_ok=True)
            if sys.platform == 'win32':
                os.startfile(str(directory))
            else:
                subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', str(directory)])
        except OSError as exc:
            self.error(exc)

    def open_catalogue(self):
        window = ThemedWindow(self, colors=self.colors)
        window.title(self.text('catalogue'))
        window.transient('')
        window.resizable(True, True)
        window.configure(background=self.colors.get('window', '#202124'))
        window.geometry('660x540')
        window.rowconfigure(0, weight=1)
        window.columnconfigure(0, weight=1)
        canvas = tk.Canvas(window, background=self.colors.get('canvas', '#202124'), highlightthickness=0)
        canvas.grid(row=0, column=0, sticky='nsew')
        window.theme_widget(canvas, background='canvas')
        scrollbar = ttk.Scrollbar(window, orient='vertical', command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        canvas.configure(yscrollcommand=scrollbar.set)
        content = ttk.Frame(canvas)
        groups = {key: {'header': None, 'cards': []} for key in ('provided', 'users')}
        current_group = ['provided']
        layout = {'job': None, 'columns': 0}
        window._mask_cards = []
        def reflow():
            layout['job'] = None
            width = max(1, canvas.winfo_width())
            card_width = max((frame.winfo_reqwidth()+16 for frame in window._mask_cards), default=1)
            columns = max(1, min(max((len(group['cards']) for group in groups.values()), default=1), width // max(1, card_width)))
            window._catalogue_card_width = card_width
            for column in range(max(columns, layout['columns'])):
                content.columnconfigure(column, weight=1 if column < columns else 0,
                                        uniform='cards' if column < columns else '')
            layout['columns'] = columns
            window._catalogue_columns = columns
            index = 0
            for group in groups.values():
                if group['header'] is not None:
                    group['header'].grid(row=index, column=0, columnspan=columns, sticky='w', padx=8, pady=8)
                    index += 1
                for position, frame in enumerate(group['cards']):
                    frame.grid(row=index+position//columns, column=position%columns, sticky='nsew', padx=8, pady=6)
                index += (len(group['cards'])+columns-1)//columns
            for row_index, row in enumerate(flow_rows(buttons.winfo_children(), width-16, gap=6)):
                for column, button in enumerate(row):
                    button.grid(row=row_index, column=column, sticky='w', padx=(0,6), pady=2)
            info_label.configure(wraplength=max(80,width-16))
        def queue_reflow():
            if layout['job'] is None:
                layout['job'] = window.after_idle(reflow)
        item = canvas.create_window(0, 0, anchor='nw', window=content)
        canvas.bind('<Configure>', lambda e: (canvas.itemconfigure(item, width=e.width), queue_reflow()))
        content.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        def wheel(e):
            canvas.yview_scroll(-1 if getattr(e, 'delta', 0)>0 or getattr(e, 'num', 0)==4 else 1, 'units')
            return 'break'
        window.bind('<MouseWheel>', wheel)
        window.bind('<Button-4>', wheel)
        window.bind('<Button-5>', wheel)
        info = tk.StringVar()
        info_label = ttk.Label(window, textvariable=info, wraplength=630)
        info_label.grid(row=1, column=0, columnspan=2, sticky='w', padx=8)
        buttons = ttk.Frame(window)
        buttons.grid(row=2, column=0, columnspan=2, sticky='w', padx=8, pady=8)
        self.sprite_button(buttons, 'folder', command=self.open_folder).grid(sticky='w')
        pending = {'job': None, 'generation': 0}
        photos = []
        def load(grid, name):
            if not self.may_replace():
                return
            self.end_stroke()
            self.drawing = MaskDrawing(grid)
            self.document_grid = self.drawing.grid.copy()
            self.mask_name = name
            self.saved_grid = grid.copy() if name else None
            self.status.set(self.text('snapshot'))
            self.queue_redraw()
            close()
        def delete(path):
            if self.confirm(self.text('delete_prompt'), parent=window, title=self.text('delete')):
                try:
                    self.catalogue.delete(path)
                    refresh()
                except (OSError, MaskImageError) as exc:
                    info.set(self.text(str(exc)))
        def row(grid, name, index, path=None, issue=None, original=None):
            frame = ttk.Frame(content)
            frame.columnconfigure(2, weight=1)
            groups[current_group[0]]['cards'].append(frame)
            window._mask_cards.append(frame)
            if grid is not None:
                image = Image.fromarray(grid).resize((64, 64), Image.Resampling.BILINEAR)
                photo = ImageTk.PhotoImage(image, master=window)
                photos.append(photo)
                ttk.Label(frame, image=photo).grid(row=0, column=0, rowspan=3, sticky='n', padx=(0, 8))
            description = self.text(issue) if issue else (f'{original[0]} × {original[1]}' if original else self.text('variable'))
            face = font.Font(frame, font=ttk.Style(frame).lookup('TLabel', 'font') or 'TkDefaultFont')
            suffix = '' if issue else f' · {description}'
            budget = max(40, 210-face.measure(suffix))
            short_name = name
            if face.measure(name) > budget:
                low, high = 0, len(name)
                while low < high:
                    middle = (low+high+1)//2
                    if face.measure(name[:middle]+'…') <= budget:
                        low = middle
                    else:
                        high = middle-1
                short_name = name[:low]+'…'
            name_label = ttk.Label(frame, text=short_name+suffix)
            name_label.grid(row=0, column=1, sticky='nw')
            if short_name != name:
                self.bind_tip(name_label, name)
            frame._mask_labels = (name_label,)
            if issue:
                description_label = ttk.Label(frame, text=description, wraplength=210)
                description_label.grid(row=1, column=1, sticky='nw', pady=(4,0))
                frame._mask_labels += (description_label,)
            actions = ttk.Frame(frame)
            actions.grid(row=2 if issue else 1, column=1, sticky='nw', pady=(4,0))
            if grid is not None:
                self.sprite_button(actions, 'load', command=lambda g=grid, n=name: load(g, n if path else '')).grid(row=0, column=0, sticky='ew')
            elif issue == 'rectangular':
                def import_rect():
                    try:
                        image = read_mask_image(path, png_only=True)
                        close()
                        self.load_image(image, name=path.stem)
                    except (OSError, MaskImageError) as exc:
                        info.set(self.text(str(exc)))
                self.sprite_button(actions, 'import', command=import_rect).grid(row=0, column=0, sticky='ew')
            if path is not None:
                delete_button = ttk.Button(actions, image=sprite_photo(self, 'mask/delete'),
                                          width=0, padding=(0,0,0,1), command=lambda p=path: delete(p))
                delete_button.grid(row=0, column=1, sticky='w', padx=(4,0))
                self.bind_tip(delete_button, self.text('delete'))
            queue_reflow()
        def refresh():
            pending['generation'] += 1
            generation = pending['generation']
            if pending['job'] is not None:
                window.after_cancel(pending['job'])
                pending['job'] = None
            for widget in content.winfo_children():
                widget.destroy()
            photos.clear()
            window._mask_cards.clear()
            for key, group in groups.items():
                group['cards'].clear()
                group['header'] = ttk.Label(content, text=self.text(key))
            current_group[0] = 'provided'
            index = 1
            for kind, name in self.templates.items():
                row(mask_template_grid(kind, 64), name, index)
                index += 1
            current_group[0] = 'users'
            queue_reflow()
            index += 1
            try:
                paths = iter(self.catalogue.paths())
                info.set(str(self.catalogue.directory))
            except OSError as exc:
                info.set(str(exc))
                return
            def add_next(position):
                pending['job'] = None
                if generation != pending['generation']:
                    return
                try:
                    path = next(paths)
                except StopIteration:
                    return
                entry = self.catalogue.entry(path)
                row(entry.grid, path.stem, position, path=path, issue=entry.issue, original=entry.original_size)
                pending['job'] = window.after_idle(lambda: add_next(position+1))
            pending['job'] = window.after_idle(lambda: add_next(index))
        self.sprite_button(buttons, 'refresh', command=refresh).grid(sticky='w')
        def create_new():
            if self.new_mask():
                close()
        self.sprite_button(buttons, 'new', command=create_new).grid(sticky='w')
        def close():
            if layout['job'] is not None:
                window.after_cancel(layout['job'])
            if pending['job'] is not None:
                window.after_cancel(pending['job'])
            window.destroy()
            self.grab_set()
        self.sprite_button(buttons, 'cancel', command=close).grid(sticky='w')
        window.protocol('WM_DELETE_WINDOW', close)
        refresh()
        window.grab_set()

    def apply_profile(self):
        try:
            self.apply_callback(self.drawing.grid.copy(), self.mask_name)
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            self.error(exc)
            return
        self.destroy()

    def close(self):
        grid = self.drawing.grid
        if grid.shape != self.initial_grid.shape or not np.array_equal(grid, self.initial_grid):
            if not self.confirm(self.text('discard')):
                return
        self.destroy()

    def destroy(self):
        for var, token in self.numeric_traces:
            var.trace_remove('write', token)
        self.numeric_traces.clear()
        if self.render_job is not None:
            self.after_cancel(self.render_job)
            self.render_job = None
        super().destroy()
