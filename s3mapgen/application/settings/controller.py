"""Settings/theme foundation and zoom-navigation behavior.

The controller expects the composed shell to provide Tk widgets and preference
state; it does not create a window or participate in constructor inheritance.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont

from .preferences import DEFAULT_SHORTCUTS, save_settings
from ..ui.i18n.shell import PREVIEW_START_MARKER_LABELS, PROJECTION_LABELS, THEME_LABELS


class SettingsController:
    """Behavior shared by the settings tab, theme and viewer navigation."""

    def _configure_settings_and_navigation(self):
        self.canvas.configure(cursor='fleur')
        self.canvas.bind('<ButtonPress-1>',self._pan_start)
        self.canvas.bind('<B1-Motion>',self._pan_move)
        self.canvas.bind('<Button-4>',lambda e:self._linux_zoom(1))
        self.canvas.bind('<Button-5>',lambda e:self._linux_zoom(-1))
        self._settings_tab()
        self._bind_scale_jump(self.opacity_scale,self.opacity_var,0,100,self._opacity_changed)
        self._bind_scale_jump(self.wheel_scale,self.wheel_var,1.04,1.20,self._wheel_changed)

    def _bind_scale_jump(self,scale,var,lo,hi,changed):
        def jump(e):
            if 'disabled' in scale.state():return 'break'
            try:element=str(scale.identify(e.x,e.y))
            except Exception:element=''
            if 'slider' in element:return None
            w=max(1,scale.winfo_width());pad=min(9,max(0,w//4))
            usable=max(1,w-2*pad);fraction=max(0.0,min(1.0,(e.x-pad)/usable))
            var.set(lo+(hi-lo)*fraction);changed();return 'break'
        scale.bind('<Button-1>',jump,add='+')

    def _apply_base_theme(self):
        dark=self.prefs['theme']=='dark';s=ttk.Style(self)
        try:s.theme_use('clam')
        except tk.TclError:pass
        if dark:
            bg='#202124';panel='#292a2d';fg='#e8eaed';muted='#aeb4bc';field='#303134';accent='#8ab4f8';textbg='#17181a';canvas='#111214'
        else:
            bg='#f2f2f2';panel='#e5e5e5';fg='#202124';muted='#5f6368';field='#ffffff';accent='#2459a9';textbg='#ffffff';canvas='#d6d6d6'
        self.configure(bg=bg)
        s.configure('.',background=bg,foreground=fg,fieldbackground=field,selectforeground=fg)
        s.configure('TFrame',background=bg);s.configure('TLabel',background=bg,foreground=fg)
        s.configure('Section.TLabel',background=bg,foreground=accent,font=('TkDefaultFont',10,'bold'));s.configure('Hint.TLabel',background=bg,foreground=muted)
        s.configure('TNotebook',background=bg,borderwidth=0);s.configure('TNotebook.Tab',background=panel,foreground=fg,padding=(10,6));s.map('TNotebook.Tab',background=[('selected',field)])
        s.configure('TButton',background=field,foreground=fg);s.map('TButton',background=[('active',panel)])
        s.configure('TCheckbutton',background=bg,foreground=fg)
        s.map('TCheckbutton',background=[('disabled',bg),('active',bg),('pressed',bg)],foreground=[('disabled',muted),('active',fg),('pressed',fg)])
        unavailable='#747980' if dark else '#8a8d91'
        if not hasattr(self,'_unavailable_font'):
            self._unavailable_font=tkfont.nametofont('TkDefaultFont').copy()
        self._unavailable_font.configure(overstrike=True)
        s.configure('Unavailable.TCheckbutton',background=bg,foreground=unavailable,font=self._unavailable_font,indicatorcolor=panel)
        s.map('Unavailable.TCheckbutton',background=[('disabled',bg)],foreground=[('disabled',unavailable)],indicatorcolor=[('disabled',panel)])
        s.configure('TCombobox',fieldbackground=field,background=field,foreground=fg,selectbackground=field,selectforeground=fg)
        s.map('TCombobox',fieldbackground=[('readonly',field),('disabled',field)],background=[('readonly',field),('disabled',field)],foreground=[('readonly',fg)],selectbackground=[('readonly',field)],selectforeground=[('readonly',fg)])
        self.option_add('*TCombobox*Listbox.background',field)
        self.option_add('*TCombobox*Listbox.foreground',fg)
        self.option_add('*TCombobox*Listbox.selectBackground',panel)
        self.option_add('*TCombobox*Listbox.selectForeground',fg)
        s.configure('TSpinbox',fieldbackground=field,foreground=fg);s.configure('TEntry',fieldbackground=field,foreground=fg)
        trough='#3c4043' if dark else '#dddddd';s.configure('Running.Horizontal.TProgressbar',troughcolor=trough,background='#35a853');s.configure('Done.Horizontal.TProgressbar',troughcolor=trough,background='#4285f4');s.configure('Error.Horizontal.TProgressbar',troughcolor=trough,background='#d93025')
        for w in (self.validation,self.pipeline,self.meta,self.stats):w.configure(bg=textbg,fg=fg,insertbackground=fg,selectbackground='#4f6480' if dark else '#b8d2ff')
        self.canvas.configure(bg=canvas)

    def _schedule_preview(self):
        if self._zoom_after:
            try:self.after_cancel(self._zoom_after)
            except Exception:pass
        self._zoom_after=self.after(35,self._refresh_preview)

    def _zoom_changed(self):self.zoom=float(self.zoom_var.get());self._schedule_preview()

    def _mouse_zoom(self,e):self._queue_zoom(1 if e.delta>0 else -1);return 'break'

    def _linux_zoom(self,d):self._queue_zoom(d);return 'break'

    def _queue_zoom(self,d):
        step=float(self.wheel_var.get());v=float(self.zoom_var.get())*(step if d>0 else 1/step);self.zoom_var.set(max(.5,min(4.,v)));self.zoom=float(self.zoom_var.get());self._schedule_preview()

    def _pan_start(self,e):self.canvas.scan_mark(e.x,e.y)

    def _pan_move(self,e):self.canvas.scan_dragto(e.x,e.y,gain=1)

    def _scroll_notebook_tab(self,title):
        """Create a tab whose content remains reachable at compact dimensions."""
        host=ttk.Frame(self.nb);self.nb.add(host,text=title);host.rowconfigure(0,weight=1);host.columnconfigure(0,weight=1)
        canvas=tk.Canvas(host,highlightthickness=0,borderwidth=0)
        hbar=ttk.Scrollbar(host,orient='horizontal',command=canvas.xview);vbar=ttk.Scrollbar(host,orient='vertical',command=canvas.yview);canvas.configure(xscrollcommand=hbar.set,yscrollcommand=vbar.set)
        canvas.grid(row=0,column=0,sticky='nsew')
        inner=ttk.Frame(canvas,padding=14);item=canvas.create_window((0,0),window=inner,anchor='nw')
        def refresh(_event=None):
            try:
                required_w=max(1,inner.winfo_reqwidth());required_h=max(1,inner.winfo_reqheight());available_w=max(1,canvas.winfo_width());available_h=max(1,canvas.winfo_height())
                canvas.itemconfigure(item,width=max(required_w,available_w));canvas.configure(scrollregion=canvas.bbox('all'))
                if required_w>available_w+1:
                    if not hbar.winfo_ismapped():hbar.grid(row=1,column=0,sticky='ew')
                elif hbar.winfo_ismapped():hbar.grid_remove();canvas.xview_moveto(0)
                if required_h>available_h+1:
                    if not vbar.winfo_ismapped():vbar.grid(row=0,column=1,sticky='ns')
                elif vbar.winfo_ismapped():vbar.grid_remove();canvas.yview_moveto(0)
            except tk.TclError:pass
        inner.bind('<Configure>',refresh,add='+');canvas.bind('<Configure>',refresh,add='+')
        self._scroll_tab_surfaces.append(canvas);return inner

    def _settings_tab(self):
        """Build display settings, including preview-only start markers."""
        f=self._scroll_notebook_tab('Paramètres');f.columnconfigure(1,weight=1)
        ttk.Label(f,text='Affichage',style='Section.TLabel').grid(row=0,column=0,columnspan=3,sticky='w',pady=(0,10))
        ttk.Label(f,text='Thème').grid(row=1,column=0,sticky='w',pady=6)
        lang=self.prefs.get('language','fr')
        self.theme_var=tk.StringVar(value=THEME_LABELS[lang][self.prefs['theme']])
        c=ttk.Combobox(f,textvariable=self.theme_var,values=list(THEME_LABELS[lang].values()),state='readonly');c.grid(row=1,column=1,sticky='ew');c.bind('<<ComboboxSelected>>',lambda e:self._theme_changed())
        ttk.Label(f,text='Opacité couche').grid(row=2,column=0,sticky='w',pady=(14,6))
        self.opacity_var=tk.DoubleVar(value=float(self.prefs['overlay_alpha']))
        self.opacity_scale=ttk.Scale(f,from_=0,to=100,variable=self.opacity_var,command=lambda v:self._opacity_changed());self.opacity_scale.grid(row=2,column=1,sticky='ew')
        self.opacity_label=ttk.Label(f,text=f"{int(self.opacity_var.get())} %",width=7);self.opacity_label.grid(row=2,column=2,padx=(8,0))
        ttk.Label(f,text='0 % = map globale · 100 % = couche seule',style='Hint.TLabel').grid(row=3,column=1,columnspan=2,sticky='w')
        ttk.Label(f,text='Projection').grid(row=4,column=0,sticky='w',pady=(14,6))
        self.projection_var=tk.StringVar(value=PROJECTION_LABELS[lang][self.prefs['projection']])
        c=ttk.Combobox(f,textvariable=self.projection_var,values=list(PROJECTION_LABELS[lang].values()),state='readonly');c.grid(row=4,column=1,sticky='ew');c.bind('<<ComboboxSelected>>',lambda e:self._projection_changed())
        ttk.Label(f,text='Le parallélogramme modifie uniquement le rendu, jamais les données.',style='Hint.TLabel',wraplength=360).grid(row=5,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Marqueurs dans les aperçus').grid(row=6,column=0,sticky='w',pady=(14,6))
        marker_key=self.prefs.get('preview_start_markers','small')
        self.preview_marker_var=tk.StringVar(value=PREVIEW_START_MARKER_LABELS[lang][marker_key])
        self.preview_marker_combo=ttk.Combobox(f,textvariable=self.preview_marker_var,values=list(PREVIEW_START_MARKER_LABELS[lang].values()),state='readonly')
        self.preview_marker_combo.grid(row=6,column=1,sticky='ew');self.preview_marker_combo.bind('<<ComboboxSelected>>',lambda e:self._preview_marker_changed())
        ttk.Label(f,text='Ce réglage affecte les miniatures et le grand aperçu du lot.',style='Hint.TLabel',wraplength=360).grid(row=7,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text="Capacité de l'historique").grid(row=8,column=0,sticky='w',pady=(14,6))
        self.history_capacity_var=tk.StringVar(value=str(self.prefs.get('history_capacity',8)))
        self.history_capacity_combo=ttk.Combobox(f,textvariable=self.history_capacity_var,values=('4','8','12','16'),state='readonly',width=8)
        self.history_capacity_combo.grid(row=8,column=1,sticky='w');self.history_capacity_combo.bind('<<ComboboxSelected>>',lambda e:self._history_capacity_changed())
        ttk.Label(f,text='Cartes conservées uniquement pendant cette session.',style='Hint.TLabel',wraplength=360).grid(row=9,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Sensibilité molette').grid(row=10,column=0,sticky='w',pady=(14,6))
        self.wheel_var=tk.DoubleVar(value=float(self.prefs['wheel_zoom']))
        self.wheel_scale=ttk.Scale(f,from_=1.04,to=1.20,variable=self.wheel_var,command=lambda v:self._wheel_changed());self.wheel_scale.grid(row=10,column=1,sticky='ew')
        self.wheel_label=ttk.Label(f,text=f"×{self.wheel_var.get():.2f}",width=7);self.wheel_label.grid(row=10,column=2,padx=(8,0))
        ttk.Separator(f).grid(row=11,column=0,columnspan=3,sticky='ew',pady=16)
        ttk.Label(f,text='Navigation',style='Section.TLabel').grid(row=12,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.',style='Hint.TLabel',justify='left').grid(row=13,column=0,columnspan=3,sticky='w',pady=(6,0))

    def _find_combo_for_var(self,var):
        target=str(var)
        for w in self._walk(self):
            if isinstance(w,ttk.Combobox):
                try:
                    if str(w.cget('textvariable'))==target:return w
                except tk.TclError:pass
        return None

    def _theme_key(self):
        value=self.theme_var.get()
        for labels in THEME_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return self.prefs.get('theme','dark')

    def _save_prefs(self):
        save_settings({'theme':self.prefs['theme'],'overlay_alpha':int(self.opacity_var.get()),'projection':self.prefs['projection'],'preview_start_markers':self.prefs.get('preview_start_markers','small'),'history_capacity':int(self.prefs.get('history_capacity',8)),'wheel_zoom':float(self.wheel_var.get()),'language':self.prefs.get('language','fr'),'shortcuts':self.prefs.get('shortcuts',dict(DEFAULT_SHORTCUTS))})

    def _schedule_prefs_save(self):
        if self._prefs_save_after is not None:
            try:self.after_cancel(self._prefs_save_after)
            except tk.TclError:pass
        self._prefs_save_after=self.after(200,self._flush_scheduled_prefs)

    def _flush_scheduled_prefs(self):
        self._prefs_save_after=None;self._save_prefs()

    def destroy(self):
        if self._prefs_save_after is not None:
            try:self.after_cancel(self._prefs_save_after)
            except tk.TclError:pass
            self._prefs_save_after=None;self._save_prefs()
        super().destroy()

    def _theme_changed(self):
        self.prefs['theme']=self._theme_key();self._save_prefs();self._apply_theme()

    def _toggle_theme(self):
        self.prefs['theme']='light' if self.prefs.get('theme')=='dark' else 'dark';lang=self.prefs.get('language','fr');self.theme_var.set(THEME_LABELS[lang][self.prefs['theme']]);self._save_prefs();self._apply_theme();self._refresh_theme_button_icon();self._refresh_preview(False);self._refresh_stats_chart();self._feedback('theme_changed','info',theme=THEME_LABELS[lang][self.prefs['theme']])
