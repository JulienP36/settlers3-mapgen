"""Foundational Tk shell and base information tabs.

The class owns only root-window construction and common selection state. Feature
behavior is supplied explicitly by the application controllers.
"""

from __future__ import annotations

import json
import random
import tkinter as tk
from tkinter import ttk

from ..analysis.core import analyze_map, format_stats_report
from ...generation.core import NATIVE_PLAYER_LIMITS


NATIVE_LIMITS = dict(NATIVE_PLAYER_LIMITS)


class ShellWindow(tk.Tk):
    """Tk root with the stable widgets required by the composed application."""

    def __init__(self):
        super().__init__()
        self.title("Settlers III MapGen")
        self.geometry("1380x860")
        self.minsize(1080,720)
        self.current=None;self.photo=None;self.import_source=None;self.zoom=1.0
        self._build();self._size_changed()

    def _build_foundation(self):
        self.mode=tk.StringVar(value='Legacy')
        self.arch=tk.StringVar(value='Continental')
        self.mirror=tk.StringVar(value='Aucun')
        self.size=tk.StringVar(value='768')
        self.players=tk.IntVar(value=4)
        self.seed=tk.StringVar(value='2026081901')
        self.view=tk.StringVar(value='Global')
        self.zoom_var=tk.DoubleVar(value=1.0)
        self.status=tk.StringVar(value='Prêt')

        self.header_root=ttk.Frame(self,padding=8);self.header_root.pack(fill='x')

        pan=ttk.Panedwindow(self,orient='horizontal');pan.pack(fill='both',expand=True,padx=8,pady=(0,8))
        left=ttk.Frame(pan);right=ttk.Frame(pan);pan.add(left,weight=3);pan.add(right,weight=2)
        self.canvas=tk.Canvas(left,bg='#181818',highlightthickness=0);self.canvas.pack(fill='both',expand=True);self.canvas.bind('<Configure>',lambda e:self._refresh_preview());self.canvas.bind('<MouseWheel>',self._mouse_zoom)
        self.nb=ttk.Notebook(right);self.nb.pack(fill='both',expand=True)
        self.validation=self._text_tab('Validations');self.pipeline=self._text_tab('Pipeline');self.meta=self._text_tab('Métadonnées');self.stats=self._text_tab('Statistiques')

    def _text_tab(self,name):
        frame=ttk.Frame(self.nb);self.nb.add(frame,text=name);txt=tk.Text(frame,wrap='word',font=('Consolas',10));sb=ttk.Scrollbar(frame,orient='vertical',command=txt.yview);txt.configure(yscrollcommand=sb.set);txt.pack(side='left',fill='both',expand=True);sb.pack(side='right',fill='y');return txt

    def random_seed(self):self.seed.set(str(random.randint(1,2_147_483_647)))

    def _set_generated_status(self):
        """Keep validation information and export availability visible after a task closes."""
        if not self.current:return
        hard_fail=[v for v in self.current.validations if v.hard and not v.passed]
        status=f'Généré — {len(self.current.validations)-len(hard_fail)}/{len(self.current.validations)} checks OK'
        if hard_fail:status+=f' — {len(hard_fail)} contrôles non validés'
        self.status.set(status+' — EXPORT AUTORISÉ')
        getattr(self,'_sync_status_display',lambda:None)()

    def _size_changed(self):
        s=int(self.size.get());mx=NATIVE_LIMITS[s];self.players_spin.configure(to=mx)
        if self.players.get()>mx:self.players.set(mx)
        self._selection_changed()

    def _populate_current_base(self,imported=False):
        self.validation.delete('1.0','end');self.validation.insert('end','Fichier importé : validations de génération non exécutées.\n' if imported else ''.join(v.label()+'\n' for v in self.current.validations))
        self.pipeline.delete('1.0','end');self.pipeline.insert('end','\n'.join(self.current.stage_log))
        self.meta.delete('1.0','end');self.meta.insert('end',json.dumps(self.current.state.metadata,indent=2,ensure_ascii=False,default=str))
        self.stats.delete('1.0','end');self.stats.insert('end',format_stats_report(analyze_map(self.current.state)))
        self.export_btn.configure(state='normal' if self.current else 'disabled')
        if not imported:self._set_generated_status()
