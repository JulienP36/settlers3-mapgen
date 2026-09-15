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


SCROLLBAR_DRAG_FRAME_MS = 16
SCROLLABLE_TAB_LAYOUT_SETTLE_MS = 24
SCROLLABLE_INPUT_WIDGET_CLASSES = frozenset(
    {"Spinbox", "TSpinbox", "Combobox", "TCombobox", "Listbox", "TListbox"}
)


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

    def _ensure_scrollable_tab_wheel_bindings(self):
        """Install one app-wide wheel route for the currently hovered tab."""

        if getattr(self, "_scroll_tab_wheel_bound", False):
            return
        self._scroll_tab_wheel_bound = True
        self._scroll_tab_active_surface = None
        self.bind_all("<MouseWheel>", self._scrollable_tab_wheel, add="+")
        # Linux exposes the wheel as buttons instead of a delta event.
        self.bind_all("<Button-4>", self._scrollable_tab_wheel, add="+")
        self.bind_all("<Button-5>", self._scrollable_tab_wheel, add="+")

    def _activate_scrollable_tab(self, host, canvas, _event=None):
        self._scroll_tab_active_surface = (host, canvas)

    def _deactivate_scrollable_tab(self, host, canvas, _event=None):
        if getattr(self, "_scroll_tab_active_surface", None) == (host, canvas):
            self._scroll_tab_active_surface = None

    def _scrollable_tab_surface_at(self, x_root, y_root):
        for canvas in reversed(getattr(self, "_scroll_tab_surfaces", ())):
            host = getattr(canvas, "_scroll_host", None)
            if host is None:
                continue
            try:
                if (
                    host.winfo_ismapped()
                    and host.winfo_rootx() <= x_root < host.winfo_rootx() + host.winfo_width()
                    and host.winfo_rooty() <= y_root < host.winfo_rooty() + host.winfo_height()
                ):
                    return host, canvas
            except tk.TclError:
                continue
        return None

    def _scrollable_tab_wheel_is_over_input(self, event):
        """Leave wheel events to controls that natively consume them."""

        try:
            widget = self.winfo_containing(int(event.x_root), int(event.y_root))
            if widget is None:
                widget = getattr(event, "widget", None)
        except (AttributeError, TypeError, tk.TclError):
            widget = getattr(event, "widget", None)
        while widget is not None:
            try:
                if widget.winfo_class() in SCROLLABLE_INPUT_WIDGET_CLASSES:
                    return True
                parent_name = widget.winfo_parent()
                if not parent_name or parent_name == str(widget):
                    break
                widget = self.nametowidget(parent_name)
            except (AttributeError, KeyError, tk.TclError):
                break
        return False

    def _scrollable_tab_wheel(self, event):
        """Scroll a tab unless the pointer is over a wheel-aware input."""

        try:
            # Spinboxes, comboboxes and listboxes must keep their native wheel
            # behavior.  Returning without consuming the event lets Tk's
            # widget/class bindings handle the value or list selection.
            if self._scrollable_tab_wheel_is_over_input(event):
                return None
            # A stale Leave event must not make a later wheel event affect a
            # hidden tab or a different part of the application.
            x_root, y_root = int(event.x_root), int(event.y_root)
            surface = getattr(self, "_scroll_tab_active_surface", None)
            if surface is None:
                surface = self._scrollable_tab_surface_at(x_root, y_root)
                self._scroll_tab_active_surface = surface
            if surface is None:
                return None
            host, canvas = surface
            inside = (
                host.winfo_ismapped()
                and host.winfo_rootx() <= x_root < host.winfo_rootx() + host.winfo_width()
                and host.winfo_rooty() <= y_root < host.winfo_rooty() + host.winfo_height()
            )
            if not inside:
                surface = self._scrollable_tab_surface_at(x_root, y_root)
                if surface is None:
                    self._scroll_tab_active_surface = None
                    return None
                self._scroll_tab_active_surface = surface
                host, canvas = surface

            event_num = getattr(event, "num", None)
            delta = getattr(event, "delta", 0)
            if event_num == 4:
                amount = -1
            elif event_num == 5:
                amount = 1
            elif delta:
                amount = (-1 if delta > 0 else 1) * max(1, int(round(abs(delta) / 120.0)))
            else:
                return "break"

            horizontal = bool(getattr(event, "state", 0) & 0x0001)
            view = canvas.xview() if horizontal else canvas.yview()
            if view[1] - view[0] < 0.999999:
                if horizontal:
                    canvas.xview_scroll(amount, "units")
                else:
                    canvas.yview_scroll(amount, "units")
            # Keep the event consumed for ordinary tab content, including at
            # the edge; wheel-aware inputs returned above before this point.
            return "break"
        except tk.TclError:
            self._scroll_tab_active_surface = None
            return None

    def _scroll_notebook_tab(self,title):
        """Create a tab whose content remains reachable at compact dimensions."""
        self._ensure_scrollable_tab_wheel_bindings()
        host=ttk.Frame(self.nb);self.nb.add(host,text=title);host.rowconfigure(0,weight=1);host.columnconfigure(0,weight=1)
        canvas=tk.Canvas(host,highlightthickness=0,borderwidth=0)
        scroll_state={'after':None,'pending':None}

        def apply_pending_view():
            scroll_state['after']=None
            pending=scroll_state['pending'];scroll_state['pending']=None
            if pending is None:return
            axis,args=pending
            try:getattr(canvas,f'{axis}view')(*args)
            except tk.TclError:pass

        def schedule_view(axis,*args):
            # A scrollbar drag can emit far more motion events than Tk can
            # repaint when the canvas contains many child widgets.  Keep the
            # latest position and cap the embedded-frame redraw to 60 Hz.
            scroll_state['pending']=(axis,args)
            if scroll_state['after'] is not None:return
            try:scroll_state['after']=canvas.after(SCROLLBAR_DRAG_FRAME_MS,apply_pending_view)
            except tk.TclError:scroll_state['after']=None

        def flush_view(_event=None):
            pending=scroll_state['pending']
            if pending is None:return
            after_id=scroll_state['after']
            if after_id is not None:
                try:canvas.after_cancel(after_id)
                except tk.TclError:pass
                scroll_state['after']=None
            apply_pending_view()

        hbar=ttk.Scrollbar(host,orient='horizontal',command=lambda *args:schedule_view('x',*args));vbar=ttk.Scrollbar(host,orient='vertical',command=lambda *args:schedule_view('y',*args));canvas.configure(xscrollcommand=hbar.set,yscrollcommand=vbar.set)
        hbar.bind('<ButtonRelease-1>',flush_view,add='+');vbar.bind('<ButtonRelease-1>',flush_view,add='+')
        canvas.grid(row=0,column=0,sticky='nsew')
        inner=ttk.Frame(canvas,padding=14);item=canvas.create_window((0,0),window=inner,anchor='nw')
        # The editor can restore a generator scroll position without knowing
        # about the notebook implementation details.
        canvas._scroll_host = host
        inner._scroll_canvas = canvas
        inner._scroll_host = host

        host.bind(
            "<Enter>",
            lambda event, h=host, c=canvas: self._activate_scrollable_tab(h, c, event),
            add="+",
        )
        host.bind(
            "<Leave>",
            lambda event, h=host, c=canvas: self._deactivate_scrollable_tab(h, c, event),
            add="+",
        )

        layout_state={'after':None,'item_width':None,'scrollregion':None}

        def refresh():
            layout_state['after']=None
            try:
                required_w=max(1,inner.winfo_reqwidth());required_h=max(1,inner.winfo_reqheight());available_w=max(1,canvas.winfo_width());available_h=max(1,canvas.winfo_height())
                target_width=max(required_w,available_w)
                if layout_state['item_width']!=target_width:
                    canvas.itemconfigure(item,width=target_width);layout_state['item_width']=target_width
                scrollregion=canvas.bbox('all')
                if scrollregion and tuple(scrollregion)!=layout_state['scrollregion']:
                    canvas.configure(scrollregion=scrollregion);layout_state['scrollregion']=tuple(scrollregion)
                show_hbar=required_w>available_w+1;show_vbar=required_h>available_h+1
                hbar_visible=bool(hbar.winfo_ismapped());vbar_visible=bool(vbar.winfo_ismapped());changed=False
                if show_hbar!=hbar_visible:
                    changed=True
                    if show_hbar:hbar.grid(row=1,column=0,sticky='ew')
                    else:hbar.grid_remove();canvas.xview_moveto(0)
                if show_vbar!=vbar_visible:
                    changed=True
                    if show_vbar:vbar.grid(row=0,column=1,sticky='ns')
                    else:vbar.grid_remove();canvas.yview_moveto(0)
                if changed:schedule_refresh()
            except tk.TclError:pass

        def schedule_refresh(_event=None):
            if layout_state['after'] is not None:return
            try:layout_state['after']=canvas.after(SCROLLABLE_TAB_LAYOUT_SETTLE_MS,refresh)
            except tk.TclError:layout_state['after']=None

        inner.bind('<Configure>',schedule_refresh,add='+');canvas.bind('<Configure>',schedule_refresh,add='+')
        self._scroll_tab_surfaces.append(canvas);schedule_refresh();return inner

    def _settings_tab(self):
        """Build display settings shared by the viewer and every preview."""
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
        ttk.Label(f,text='Marqueurs de départ').grid(row=6,column=0,sticky='w',pady=(14,6))
        marker_key=self.prefs.get('preview_start_markers','small')
        self.preview_marker_var=tk.StringVar(value=PREVIEW_START_MARKER_LABELS[lang][marker_key])
        self.preview_marker_combo=ttk.Combobox(f,textvariable=self.preview_marker_var,values=list(PREVIEW_START_MARKER_LABELS[lang].values()),state='readonly')
        self.preview_marker_combo.grid(row=6,column=1,sticky='ew');self.preview_marker_combo.bind('<<ComboboxSelected>>',lambda e:self._preview_marker_changed())
        ttk.Label(f,text='Ce réglage affecte les marqueurs de départ dans toutes les vues et previews.',style='Hint.TLabel',wraplength=360).grid(row=7,column=0,columnspan=3,sticky='w')
        self.preview_start_circles_var=tk.BooleanVar(value=bool(self.prefs.get('preview_start_circles',False)))
        self.preview_start_circles_check=ttk.Checkbutton(f,text='Cercles de départ',variable=self.preview_start_circles_var,command=self._preview_start_circles_changed)
        self.preview_start_circles_check.grid(row=8,column=0,columnspan=2,sticky='w',pady=(10,0))
        ttk.Label(f,text='Afficher le contour du territoire initial dans toutes les vues et previews.',style='Hint.TLabel',wraplength=360).grid(row=9,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text="Capacité de l'historique").grid(row=10,column=0,sticky='w',pady=(14,6))
        self.history_capacity_var=tk.StringVar(value=str(self.prefs.get('history_capacity',8)))
        self.history_capacity_combo=ttk.Combobox(f,textvariable=self.history_capacity_var,values=('4','8','12','16'),state='readonly',width=8)
        self.history_capacity_combo.grid(row=10,column=1,sticky='w');self.history_capacity_combo.bind('<<ComboboxSelected>>',lambda e:self._history_capacity_changed())
        ttk.Label(f,text='Cartes conservées uniquement pendant cette session.',style='Hint.TLabel',wraplength=360).grid(row=11,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Sensibilité molette').grid(row=12,column=0,sticky='w',pady=(14,6))
        self.wheel_var=tk.DoubleVar(value=float(self.prefs['wheel_zoom']))
        self.wheel_scale=ttk.Scale(f,from_=1.04,to=1.20,variable=self.wheel_var,command=lambda v:self._wheel_changed());self.wheel_scale.grid(row=12,column=1,sticky='ew')
        self.wheel_label=ttk.Label(f,text=f"×{self.wheel_var.get():.2f}",width=7);self.wheel_label.grid(row=12,column=2,padx=(8,0))
        ttk.Separator(f).grid(row=13,column=0,columnspan=3,sticky='ew',pady=16)
        ttk.Label(f,text='Navigation',style='Section.TLabel').grid(row=14,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.',style='Hint.TLabel',justify='left').grid(row=15,column=0,columnspan=3,sticky='w',pady=(6,0))

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
        save_settings({'theme':self.prefs['theme'],'overlay_alpha':int(self.opacity_var.get()),'projection':self.prefs['projection'],'preview_start_markers':self.prefs.get('preview_start_markers','small'),'preview_start_circles':bool(self.prefs.get('preview_start_circles',False)),'history_capacity':int(self.prefs.get('history_capacity',8)),'wheel_zoom':float(self.wheel_var.get()),'language':self.prefs.get('language','fr'),'shortcuts':self.prefs.get('shortcuts',dict(DEFAULT_SHORTCUTS))})

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
