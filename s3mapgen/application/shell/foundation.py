"""Foundational Tk shell and base information tabs.

The class owns only root-window construction and common selection state. Feature
behavior is supplied explicitly by the application controllers.
"""

from __future__ import annotations

import json
import random
import sys
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from ..paths import APP_ICON_PNG, APP_ICON_ICO
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
        self._application_icon=tk.PhotoImage(master=self,file=str(APP_ICON_PNG))
        self.iconphoto(True,self._application_icon)
        if sys.platform == "win32":
            self.iconbitmap(str(APP_ICON_ICO))
            self.iconbitmap(default=str(APP_ICON_ICO))
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
        self._vertical_split_height = self._initial_vertical_split_height()
        self._vertical_split_dragging = False
        self._vertical_split_initialized = False
        self._vertical_split_apply_after = None
        vertical=ttk.Panedwindow(self,orient='vertical')
        vertical.pack(fill='both',expand=True,padx=8,pady=(0,8))
        self._vertical_paned=vertical
        header_host=ttk.Frame(vertical)
        body_host=ttk.Frame(vertical)
        vertical.add(header_host,weight=0)
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
        self._workspace_default_split_active = False
        self._workspace_split_job = None
        pan.bind('<Configure>', self._workspace_split_configure, add='+')
        pan.bind('<ButtonPress-1>', self._workspace_split_press, add='+')
        left=ttk.Frame(pan);right=ttk.Frame(pan);pan.add(left,weight=3);pan.add(right,weight=2)
        self.canvas=tk.Canvas(left,bg='#181818',highlightthickness=0);self.canvas.pack(fill='both',expand=True);self.canvas.bind('<Configure>',self._preview_canvas_configured,add='+');self.canvas.bind('<MouseWheel>',self._mouse_zoom)
        self.nb=ttk.Notebook(right);self.nb.pack(fill='both',expand=True)
        self.validation=self._text_tab('Validations');self.pipeline=self._text_tab('Pipeline');self.meta=self._text_tab('Métadonnées');self.stats=self._text_tab('Statistiques')
        vertical.bind('<ButtonPress-1>',self._vertical_split_press,add='+')
        vertical.bind('<ButtonRelease-1>',self._vertical_split_release,add='+')
        vertical.bind('<Configure>',self._vertical_split_configure,add='+')

    def _initial_vertical_split_height(self):
        # Old ratios deliberately do not migrate: they create empty space as
        # the window grows. None anchors the sash to the real header content.
        value=getattr(self,'prefs',{}).get('vertical_split_height')
        try:
            return None if value is None else max(0,int(value))
        except (TypeError,ValueError,OverflowError):
            return None

    def _vertical_split_configure(self,event=None):
        if self._vertical_split_dragging or self._vertical_split_apply_after is not None:
            return
        try:
            self._vertical_split_apply_after=self.after_idle(self._apply_vertical_split_layout)
        except tk.TclError:
            self._vertical_split_apply_after=None

    def _apply_vertical_split_layout(self):
        self._vertical_split_apply_after=None
        if self._vertical_split_dragging:
            return
        try:
            total=int(self._vertical_paned.winfo_height())
            if total<=1:return
            target=self._vertical_split_height
            if target is None:target=int(self.header_root.winfo_reqheight())
            target=max(0,min(total-1,target))
            current=int(self._vertical_paned.sashpos(0))
            if not self._vertical_split_initialized or abs(current-target)>1:
                self._vertical_paned.sashpos(0,target)
            self._vertical_split_initialized=True
        except tk.TclError:
            pass

    def _vertical_split_press(self,event=None):
        if event is None:return
        try:
            if str(self._vertical_paned.identify(event.x,event.y))!='0':return
        except tk.TclError:
            return
        self._vertical_split_dragging=True
        if self._vertical_split_apply_after is not None:
            try:self.after_cancel(self._vertical_split_apply_after)
            except tk.TclError:pass
            self._vertical_split_apply_after=None

    def _vertical_split_release(self,event=None):
        if not self._vertical_split_dragging:return
        self._vertical_split_dragging=False
        try:
            position=int(self._vertical_paned.sashpos(0))
            natural=int(self.header_root.winfo_reqheight())
        except tk.TclError:
            return
        # A sash next to the controls follows their natural height through
        # reflow/language changes. Else retain the user's visible height,
        # including partial or complete collapse, without reopening it.
        self._vertical_split_height=None if abs(position-natural)<=4 else max(0,position)
        prefs=getattr(self,'prefs',None)
        if isinstance(prefs,dict):prefs['vertical_split_height']=self._vertical_split_height
        self._vertical_split_configure()
        save=getattr(self,'_schedule_prefs_save',None)
        if save is not None:save()

    def _reset_workspace(self):
        """Maximize and restore the two default sashes, preserving map/navigation state."""
        grab = self.grab_current()
        if grab is not None and grab is not self:
            return
        try:
            if self.state() != 'zoomed':
                self.state('zoomed')
        except tk.TclError:
            # X11 window managers expose maximization as an attribute instead.
            self.attributes('-zoomed', True)
        self._vertical_split_height = None
        self._vertical_split_dragging = False
        self._vertical_split_initialized = False
        self.prefs['vertical_split_height'] = None
        self._workspace_default_split_active = True
        self._vertical_split_configure()
        self._workspace_split_configure()
        self._schedule_prefs_save()

    def _workspace_split_configure(self, event=None):
        if not self._workspace_default_split_active or self._workspace_split_job is not None:
            return
        self._workspace_split_job = self.after_idle(self._apply_workspace_split)

    def _apply_workspace_split(self):
        self._workspace_split_job = None
        if not self._workspace_default_split_active:
            return
        width = self._content_paned.winfo_width()
        if width <= 1:
            return
        target = round(width * .55)  # Workspace reset: map 55%, tabs 45%.
        if abs(self._content_paned.sashpos(0)-target) > 1:
            self._content_paned.sashpos(0, target)

    def _workspace_split_press(self, event):
        if str(self._content_paned.identify(event.x, event.y)) == '0':
            # A manual drag takes ownership immediately, including a collapsed pane.
            self._workspace_default_split_active = False

    def _text_tab(self,name):
        frame=ttk.Frame(self.nb);self.nb.add(frame,text=name);txt=tk.Text(frame,wrap='word',font=('Consolas',10));sb=ttk.Scrollbar(frame,orient='vertical',command=txt.yview);txt.configure(yscrollcommand=sb.set);txt.pack(side='left',fill='both',expand=True);sb.pack(side='right',fill='y');return txt

    def random_seed(self):self.seed.set(str(random.randint(1,2_147_483_647)))

    def _set_generated_status(self):
        """Keep validation information and export availability visible after a task closes."""
        if not self.current:return
        hard_fail=[v for v in self.current.validations if v.hard and not v.passed]
        status=f'Généré — {len(self.current.validations)-len(hard_fail)}/{len(self.current.validations)} checks OK'
        if hard_fail:status+=f' — {len(hard_fail)} contrôles non validés'
        metadata=getattr(getattr(self.current,'state',None),'metadata',{})
        incomplete=metadata.get('start_disabled_slots') or metadata.get('classic_disabled_slots')
        self.status.set(status+(' — DÉPARTS INCOMPLETS — EDM DE TEST DISPONIBLE' if incomplete else ' — EXPORT AUTORISÉ'))
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
        for button in (self.export_btn,self.preview_button):
            button.configure(state='normal' if self.current else 'disabled')
        metadata=self.current.state.metadata if self.current else {}
        if not imported:self._set_generated_status()
