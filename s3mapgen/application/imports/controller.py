"""EDM/MAP/SAV import workflow for the desktop application."""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog
from ..ui.messages import show_message

from ...generation.contracts import GenerationOutput
from ...generation.core import NATIVE_GAME_MAX_SIDE
from ...map_data.binary import read_area, read_sav_state, read_starts, read_start_context


class ImportController:
    """Import supported map files and register successful session history."""

    def import_file(self):
        path=filedialog.askopenfilename(title='Importer une map',filetypes=[('Settlers III','*.edm *.map *.sav'),('EDM','*.edm'),('MAP','*.map'),('SAV','*.sav'),('Tous','*.*')])
        if not path:return
        try:
            p=Path(path);ext=p.suffix.lower();self._task_begin(f'Import {p.name}…',8)
            if ext=='.sav':
                state=read_sav_state(p);state.metadata.update({'source_format':'SAV','source_path':str(p),'territories_available':True})
            elif ext in ('.edm','.map'):
                state=read_area(p);state.starts=read_starts(p);state.metadata.update(read_start_context(p));state.metadata.update({'source_format':ext[1:].upper(),'source_path':str(p),'territories_available':False})
            else:raise ValueError('Extension non supportée')
            if state.side > NATIVE_GAME_MAX_SIDE:
                raise ValueError("Taille non prise en charge : maximum 768×768")
            self._task_progress(80,'Calcul des statistiques…');self.import_source=p;self.current=GenerationOutput(state,[],[f'import.{ext[1:]} — {p.name}']);self._populate_current(True);self._invalidate_preview();self._task_progress(92,'Construction de l’aperçu…');self._refresh_preview(False);self._task_done(f'Importé — {p.name} — {state.side}×{state.side}');self._register_import_history(self.current,self.import_source)
        except Exception as e:
            self._task_error('Erreur import')
            show_message(self, 'import', exception=e, context={'Fichier / File': path})
