"""Stable v1.5 UI/export shell inherited by the current v1.8 interface."""

from __future__ import annotations
import shutil
from pathlib import Path
from tkinter import filedialog, messagebox

from .gui_v14 import App as V14App
from .binary import export_with_scaffold
from .preview import render
from .app_paths import EDM_SCAFFOLD, MAP_SCAFFOLD


class App(V14App):
    """v1.5 release shell: v1.4 UX with the audited v1.5 generator rules."""

    def __init__(self):
        super().__init__()
        self.title('Settlers III MapGen v1.5')

    def export(self):
        if not self.current:
            return
        folder = filedialog.askdirectory(title='Dossier de sortie')
        if not folder:
            return
        try:
            folder = Path(folder)
            st = self.current.state
            side = st.side
            self._task_begin('Export…', 5)
            base = (
                f"S3_{st.metadata.get('archetype','Imported')}_{st.metadata.get('mode','Map')}_"
                f"{len(st.starts) or st.metadata.get('players',0)}P_{side}x{side}_"
                f"seed_{st.metadata.get('seed','import')}_MapGenV1_5"
            ).replace(' ', '')
            made = []
            if side == 768:
                edm = folder / (base + '.edm')
                mp = folder / ('1-' + base + '.map')
                export_with_scaffold(st, EDM_SCAFFOLD, edm)
                self._task_progress(35, 'Export MAP…')
                export_with_scaffold(st, MAP_SCAFFOLD, mp)
                made += [edm.name, mp.name]
            else:
                made.append('EDM/MAP non réécrits : aucun scaffold validé pour cette taille.')
            self._task_progress(62, 'Export SAV/aperçu…')
            if self.import_source and self.import_source.suffix.lower() == '.sav':
                sv = folder / (base + '.sav')
                shutil.copy2(self.import_source, sv)
                made.append(sv.name + ' (copie SAV inchangée)')
            else:
                made.append('SAV non exporté : writer SAV volontairement non implémenté/validé.')
            png = folder / (base + '_preview.png')
            render(st, png, **self._render_options())
            made.append(png.name)
            self._task_done('Export terminé')
            messagebox.showinfo('Export', '\n'.join(made))
        except Exception as e:
            self._task_error('Erreur export')
            messagebox.showerror('Export', f'{e}')


def main():
    App().mainloop()
