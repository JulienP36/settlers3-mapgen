"""Foundational Tk shell and base information tabs.

The class owns only root-window construction and common selection state. Feature
behavior is supplied explicitly by the application controllers.
"""

from __future__ import annotations

import json
import random
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from ..analysis.core import analyze_map, format_stats_report
from ...generation.core import NATIVE_PLAYER_LIMITS


NATIVE_LIMITS = dict(NATIVE_PLAYER_LIMITS)


def default_seed_value(now=None) -> str:
    """Return the familiar date-and-hour seed used when the app opens."""

    return (now or datetime.now()).strftime("%Y%m%d%H")


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
        self.mode=tk.StringVar(value='Classique')
        self.arch=tk.StringVar(value='Continental')
        self.arch_input=tk.StringVar(value='Classique')
        self.mirror=tk.StringVar(value='Aucun')
        self.size=tk.StringVar(value='512')
        self.players=tk.IntVar(value=4)
        self.seed=tk.StringVar(value=default_seed_value())
        self.view=tk.StringVar(value='Global')
        self.zoom_var=tk.DoubleVar(value=1.0)
        self.status=tk.StringVar(value='Prêt')

        # The existing horizontal map/tabs sash remains inside the lower pane.
        # This outer vertical sash lets the user give the Archétype editor more
        # room without pushing the three main previews below the fold.
        self._vertical_split_ratio = self._initial_vertical_split_ratio()
        self._vertical_split_dragging = False
        self._vertical_split_initialized = False
        self._vertical_split_apply_after = None
        vertical=ttk.Panedwindow(self,orient='vertical')
        vertical.pack(fill='both',expand=True,padx=8,pady=(0,8))
        self._vertical_paned=vertical
        header_host=ttk.Frame(vertical)
        body_host=ttk.Frame(vertical)
        vertical.add(header_host,weight=1)
        vertical.add(body_host,weight=1)
        self.header_root=ttk.Frame(header_host,padding=8)
        self.header_root.pack(fill='both',expand=True)
        self.header_root.columnconfigure(0,weight=1)
        # The upper pane may be made taller with the sash, but its controls
        # must remain attached to the top edge instead of being vertically
        # centred in the newly available space.
        self.header_root.rowconfigure(0,weight=0)

        pan=ttk.Panedwindow(body_host,orient='horizontal');pan.pack(fill='both',expand=True)
        self._content_paned=pan
        left=ttk.Frame(pan);right=ttk.Frame(pan);pan.add(left,weight=3);pan.add(right,weight=2)
        self.canvas=tk.Canvas(left,bg='#181818',highlightthickness=0);self.canvas.pack(fill='both',expand=True);self.canvas.bind('<Configure>',self._preview_canvas_configured,add='+');self.canvas.bind('<MouseWheel>',self._mouse_zoom)
        self.nb=ttk.Notebook(right);self.nb.pack(fill='both',expand=True)
        self.validation=self._text_tab('Validations');self.pipeline=self._text_tab('Pipeline');self.meta=self._text_tab('Métadonnées');self.stats=self._text_tab('Statistiques')
        vertical.bind('<ButtonPress-1>',self._vertical_split_press,add='+')
        vertical.bind('<ButtonRelease-1>',self._vertical_split_release,add='+')
        vertical.bind('<Configure>',self._vertical_split_configure,add='+')

    def _initial_vertical_split_ratio(self):
        try:
            value=float(getattr(self,'prefs',{}).get('vertical_split_ratio',0.32))
        except (AttributeError,TypeError,ValueError):
            value=0.32
        return max(0.20,min(0.65,value))

    def _vertical_split_bounds(self):
        try:
            total=int(self._vertical_paned.winfo_height())
        except tk.TclError:
            return 0,0,0
        if total<=1:
            return total,0,0
        minimum_top=160
        minimum_bottom=280
        if total<minimum_top+minimum_bottom:
            minimum_top=max(110,total//3)
            minimum_bottom=max(150,total-minimum_top)
        return total,minimum_top,max(minimum_top,total-minimum_bottom)

    def _vertical_split_configure(self,event=None):
        if self._vertical_split_dragging:
            return
        total,minimum_top,maximum_top=self._vertical_split_bounds()
        if total<=1:
            return
        target=max(minimum_top,min(maximum_top,round(total*self._vertical_split_ratio)))
        try:
            current=int(self._vertical_paned.sashpos(0))
            if not self._vertical_split_initialized or abs(current-target)>2:
                self._vertical_paned.sashpos(0,target)
            self._vertical_split_initialized=True
        except tk.TclError:
            pass

    def _vertical_split_press(self,event=None):
        self._vertical_split_dragging=True

    def _vertical_split_release(self,event=None):
        self._vertical_split_dragging=False
        total,minimum_top,maximum_top=self._vertical_split_bounds()
        if total<=1:
            return
        try:
            position=int(self._vertical_paned.sashpos(0))
        except tk.TclError:
            return
        position=max(minimum_top,min(maximum_top,position))
        self._vertical_split_ratio=max(0.20,min(0.65,position/float(total)))
        try:
            self._vertical_paned.sashpos(0,position)
        except tk.TclError:
            pass
        prefs=getattr(self,'prefs',None)
        if isinstance(prefs,dict):
            prefs['vertical_split_ratio']=self._vertical_split_ratio
        save=getattr(self,'_save_prefs',None)
        if save is not None:
            save()

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
