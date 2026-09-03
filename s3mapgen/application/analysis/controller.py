"""Statistics-analysis tabs and chart interaction for the main window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import ImageTk

from .core import analyze_map
from .charts import CHART_KEYS, CHART_LABELS, render_stats_chart
from ..rendering.focus import focus_signature
from ..ui.i18n.common import _lang_text


class AnalysisController:
    """Host contract: current outputs, analysis widgets and export action."""
    def _reorder_analysis_tabs(self):
        """Keep Statistics + Charts together, then Settings + Shortcuts."""
        tabs=list(self.nb.tabs())
        chart=next((t for t in tabs if self.nb.tab(t,'text')=='Graphiques'),None)
        settings=next((t for t in tabs if self.nb.tab(t,'text')=='Paramètres'),None)
        if chart and settings:
            self.nb.insert(self.nb.index(settings),chart)

    def _build_stats_charts_tab(self):
        frame=ttk.Frame(self.nb,padding=10);self.nb.add(frame,text='Graphiques')
        frame.columnconfigure(0,weight=1);frame.rowconfigure(1,weight=1)
        controls=ttk.Frame(frame);controls.grid(row=0,column=0,sticky='ew',pady=(0,8));controls.columnconfigure(1,weight=1)
        ttk.Label(controls,text='Graphiques').grid(row=0,column=0,sticky='w',padx=(0,8))
        self.stats_chart_var=tk.StringVar(value=CHART_LABELS[self.prefs.get('language','fr')]['terrain_families'])
        self.stats_chart_combo=ttk.Combobox(controls,textvariable=self.stats_chart_var,state='readonly',width=40)
        self.stats_chart_combo.grid(row=0,column=1,sticky='ew',padx=(0,8));self.stats_chart_combo.bind('<<ComboboxSelected>>',lambda e:self._stats_chart_selection_changed())
        self.stats_link_var=tk.BooleanVar(value=False)
        self.stats_link_button=ttk.Checkbutton(controls,text='Lier à la vue',variable=self.stats_link_var,command=self._toggle_chart_link)
        self.stats_link_button.grid(row=0,column=2,padx=(0,8))
        self.stats_export_button=ttk.Button(controls,text='Exporter…',command=self._open_stats_export_center);self.stats_export_button.grid(row=0,column=3,padx=3)
        self.stats_chart_canvas=tk.Canvas(frame,highlightthickness=0,bg='#212225');self.stats_chart_canvas.grid(row=1,column=0,sticky='nsew')
        self.stats_chart_canvas.bind('<Configure>',lambda e:self._refresh_stats_chart(),add='+')
        self.stats_chart_canvas.bind('<Motion>',self._chart_tooltip_motion,add='+');self.stats_chart_canvas.bind('<Leave>',self._chart_leave,add='+')
        self._stats_chart_photo=None;self._stats_chart_regions=[];self._chart_tooltip=None;self._chart_tooltip_label=None
        self._chart_hover_region=None;self._chart_link_focus=None
        self._refresh_stats_chart_labels()

    def _stats_chart_selection_changed(self):
        """Change charts without leaving a stale semantic selection active."""
        self._chart_hover_region=None
        self._set_chart_link_focus(None)
        self._refresh_stats_chart()

    def _set_chart_link_focus(self, focus):
        if not getattr(self, 'stats_link_var', None) or not self.stats_link_var.get():
            focus=None
        old=focus_signature(getattr(self, '_chart_link_focus', None))
        new=focus_signature(focus)
        self._chart_link_focus=focus
        if old != new and hasattr(self, '_refresh_preview'):
            self._refresh_preview(False)

    def _toggle_chart_link(self):
        """Enable temporary chart-hover highlighting in the main map."""
        focus=None
        if self.stats_link_var.get():
            focus=(getattr(self, '_chart_hover_region', None) or {}).get('focus')
        self._set_chart_link_focus(focus)

    def _chart_leave(self,event=None):
        self._hide_chart_tooltip()
        self._chart_hover_region=None
        self._set_chart_link_focus(None)

    def _refresh_stats_chart_labels(self):
        if not hasattr(self,'stats_chart_combo'):return
        lang=self.prefs.get('language','fr');labels=CHART_LABELS[lang]
        current_key=self._stats_chart_key() if self.stats_chart_var.get() else 'terrain_families'
        self.stats_chart_combo.configure(values=[labels[k] for k in CHART_KEYS])
        self.stats_chart_var.set(labels.get(current_key,labels['terrain_families']))

    def _stats_chart_key(self):
        if not hasattr(self,'stats_chart_var'):return 'terrain_families'
        value=self.stats_chart_var.get()
        for lang_labels in CHART_LABELS.values():
            for key,label in lang_labels.items():
                if label==value:return key
        return 'terrain_families'

    def _ensure_stats_cache(self):
        if not self.current:return None
        state=self.current.state
        stats=self.session_stats_cache.get(state)
        if stats is None:
            if getattr(self,'_task_overlay',None) is not None:self._task_progress(82,_lang_text(self.prefs.get('language','fr'),'Calcul des statistiques…','Computing statistics…','Statistiken werden berechnet…','Calculando estadísticas…'))
            stats=analyze_map(state)
            self.session_stats_cache.put(state,stats)
        return stats

    def _stats_for_output(self,out):
        if out is None:return None
        state=out.state
        stats=self.session_stats_cache.get(state)
        if stats is None:
            stats=analyze_map(state);self.session_stats_cache.put(state,stats)
        return stats

    def _compare_stats_pair(self):
        return (self._stats_for_output(self._compare_slots.get('A')), self._stats_for_output(self._compare_slots.get('B')))

    def _refresh_stats_chart(self):
        if not hasattr(self,'stats_chart_canvas'):return
        c=self.stats_chart_canvas;c.delete('all')
        stats=self._ensure_stats_cache()
        if not stats:
            c.create_text(20,20,text='—',anchor='nw',fill=getattr(self,'_ui_theme_colors',{}).get('fg','#e8eaed'));return
        try:
            w=max(420,int(c.winfo_width()));h=max(280,int(c.winfo_height()));lang=self.prefs.get('language','fr');dark=self.prefs.get('theme','dark')=='dark'
            im,self._stats_chart_regions=render_stats_chart(stats,self._stats_chart_key(),lang=lang,dark=dark,width=w,height=h,compare_stats=self._compare_stats_pair(),return_regions=True)
            self._stats_chart_photo=ImageTk.PhotoImage(im);c.create_image(0,0,image=self._stats_chart_photo,anchor='nw')
        except Exception as exc:
            c.create_text(20,20,text=f'Chart error: {exc}',anchor='nw',fill=getattr(self,'_ui_theme_colors',{}).get('fg','#e8eaed'))

    def _hide_chart_tooltip(self):
        if getattr(self,'_chart_tooltip',None) is not None:
            try:self._chart_tooltip.destroy()
            except tk.TclError:pass
            self._chart_tooltip=None
            self._chart_tooltip_label=None

    def _chart_tooltip_motion(self,event):
        hit=None
        for region in reversed(getattr(self,'_stats_chart_regions',[])):
            x0,y0,x1,y1=region.get('bbox',(0,0,0,0))
            if x0<=event.x<=x1 and y0<=event.y<=y1:
                hit=region;break
        if hit is None:
            self._chart_leave();return
        self._chart_hover_region=hit
        self._set_chart_link_focus(hit.get('focus'))
        unit=hit.get('unit','');text=f"{hit.get('label','')}\n{hit.get('value','')}"+(f" {unit}" if unit else '')
        details=hit.get('details') or []
        if details:text+='\n'+'\n'.join(str(line) for line in details)
        dark=self.prefs.get('theme','dark')=='dark';bg='#202124' if dark else '#fffdf5';fg='#f1f3f4' if dark else '#202124'
        # Keep one tooltip window alive while the mouse moves across chart regions.
        # Recreating the Toplevel on every <Motion> caused visible flicker/disappearance.
        tip=getattr(self,'_chart_tooltip',None);label=getattr(self,'_chart_tooltip_label',None)
        if tip is None or label is None:
            tip=tk.Toplevel(self);tip.overrideredirect(True);tip.attributes('-topmost',True)
            label=tk.Label(tip,text=text,justify='left',background=bg,foreground=fg,relief='solid',borderwidth=1,padx=7,pady=5,font=('Segoe UI',9));label.pack()
            self._chart_tooltip=tip;self._chart_tooltip_label=label
        else:
            label.configure(text=text,background=bg,foreground=fg)
        tip.geometry(f"+{self.stats_chart_canvas.winfo_rootx()+event.x+14}+{self.stats_chart_canvas.winfo_rooty()+event.y+12}")
