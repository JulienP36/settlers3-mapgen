"""Application-wide theme rendering and deterministic theme-toggle icon."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageDraw, ImageTk

from .palettes import THEME_PALETTES
from ..i18n.common import _lang_text
from ..widgets import ColorMenuSelect


class ThemeController:
    """Host contract: composed widgets and subsystem theme hooks."""
    def _refresh_theme_button_icon(self):
        if not hasattr(self,'_theme_button'):return
        # Small deterministic raster icon: show the action (sun in dark mode, moon in light mode).
        dark=self.prefs.get('theme','dark')=='dark'
        im=Image.new('RGBA',(20,20),(0,0,0,0));d=ImageDraw.Draw(im)
        if dark:
            c=(245,195,55,255);d.ellipse((6,6,14,14),fill=c)
            for x1,y1,x2,y2 in ((10,1,10,4),(10,16,10,19),(1,10,4,10),(16,10,19,10),(3,3,5,5),(15,15,17,17),(15,3,17,5),(3,15,5,17)):d.line((x1,y1,x2,y2),fill=c,width=2)
            tip=_lang_text(self.prefs.get('language','fr'),'Passer au thème clair','Switch to light theme','Zum hellen Design wechseln','Cambiar al tema claro')
        else:
            c=(75,95,145,255);d.ellipse((4,3,16,17),fill=c);d.ellipse((8,1,18,13),fill=(0,0,0,0))
            tip=_lang_text(self.prefs.get('language','fr'),'Passer au thème sombre','Switch to dark theme','Zum dunklen Design wechseln','Cambiar al tema oscuro')
        self._theme_button_icon=ImageTk.PhotoImage(im);self._theme_button.configure(image=self._theme_button_icon,text='',takefocus=False)
        try:self._theme_button.configure(cursor='hand2')
        except tk.TclError:pass

    def _apply_theme(self):
        self._apply_base_theme();dark=self.prefs.get('theme')=='dark';style=ttk.Style(self);palette=dict(THEME_PALETTES['dark' if dark else 'light'])
        field=palette['field'];fg=palette['text'];muted=palette['disabled'];panel=palette['panel']
        self._ui_theme_colors={**palette,'field':field,'fg':fg,'muted':muted,'panel':panel,'bar_bg':'#3c4043' if dark else '#dddddd','bar_fg':palette['success'],'dark':dark}
        # Global state maps prevent Windows native hover/focus colors from leaking
        # through newly created widgets. Named semantic styles remain available
        # for intentionally colored primary/status actions.
        style.configure('TFrame',background=palette['window']);style.configure('Card.TFrame',background=palette['panel'],relief='solid',borderwidth=1)
        style.configure('TLabel',background=palette['window'],foreground=fg);style.configure('Panel.TLabel',background=palette['panel'],foreground=fg);style.configure('PanelHint.TLabel',background=palette['panel'],foreground=palette['muted'])
        style.configure('ShortcutPending.TLabel',background=palette['window'],foreground=palette['warning'],font=('TkDefaultFont',9,'bold'))
        style.configure('ShortcutConflict.TLabel',background=palette['window'],foreground=palette['danger'],font=('TkDefaultFont',9,'bold'))
        style.configure('TLabelframe',background=palette['window'],bordercolor=palette['border']);style.configure('TLabelframe.Label',background=palette['window'],foreground=fg)
        style.configure('History.TLabelframe',background=palette['panel'],bordercolor=palette['border']);style.configure('History.TLabelframe.Label',background=palette['panel'],foreground=fg)
        style.configure('TButton',background=palette['surface'],foreground=fg,bordercolor=palette['border'],lightcolor=palette['border'],darkcolor=palette['border'])
        style.map('TButton',background=[('disabled',palette['panel']),('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('disabled',muted),('pressed',fg),('active',fg)])
        style.configure('TMenubutton',background=palette['surface'],foreground=fg,bordercolor=palette['border']);style.map('TMenubutton',background=[('disabled',palette['panel']),('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('disabled',muted),('active',fg)])
        for name,color in (('Primary',palette['primary']),('Success',palette['success']),('Warning',palette['warning']),('Danger',palette['danger'])):
            style.configure(f'{name}.TButton',background=color,foreground='#ffffff')
            style.map(f'{name}.TButton',background=[('disabled',palette['panel']),('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('disabled',muted),('pressed','#ffffff'),('active','#ffffff')])
        style.configure('TCheckbutton',background=palette['window'],foreground=fg);style.map('TCheckbutton',background=[('disabled',palette['window']),('pressed',palette['window']),('active',palette['window'])],foreground=[('disabled',muted),('active',fg)])
        style.configure('TRadiobutton',background=palette['window'],foreground=fg);style.map('TRadiobutton',background=[('disabled',palette['window']),('pressed',palette['window']),('active',palette['window'])],foreground=[('disabled',muted),('active',fg)])
        for widget_style in ('TEntry','TSpinbox','TCombobox'):
            style.configure(widget_style,fieldbackground=field,background=field,foreground=fg,selectbackground=palette['selection'],selectforeground=palette['selection_text'],bordercolor=palette['border'])
            style.map(widget_style,fieldbackground=[('disabled',palette['panel']),('readonly',field),('focus',field)],background=[('disabled',palette['panel']),('readonly',field),('active',palette['hover'])],foreground=[('disabled',muted),('readonly',fg)],selectbackground=[('readonly',palette['selection'])],selectforeground=[('readonly',palette['selection_text'])])
        style.configure('TNotebook.Tab',background=panel,foreground=fg);style.map('TNotebook.Tab',background=[('selected',field),('active',palette['hover']),('pressed',palette['pressed'])],foreground=[('disabled',muted),('selected',fg),('active',fg)])
        style.configure('Horizontal.TScale',background=palette['window'],troughcolor=palette['panel']);style.map('Horizontal.TScale',background=[('active',palette['primary']),('disabled',palette['disabled'])])
        style.configure('Vertical.TScrollbar',background=palette['surface'],troughcolor=palette['panel'],arrowcolor=fg,bordercolor=palette['border']);style.map('Vertical.TScrollbar',background=[('pressed',palette['pressed']),('active',palette['hover'])],arrowcolor=[('disabled',muted)])
        style.configure('Horizontal.TScrollbar',background=palette['surface'],troughcolor=palette['panel'],arrowcolor=fg,bordercolor=palette['border']);style.map('Horizontal.TScrollbar',background=[('pressed',palette['pressed']),('active',palette['hover'])],arrowcolor=[('disabled',muted)])
        style.configure('Treeview',background=palette['surface'],fieldbackground=palette['surface'],foreground=fg,bordercolor=palette['border'],rowheight=23)
        style.map('Treeview',background=[('selected',palette['selection'])],foreground=[('selected',palette['selection_text'])])
        style.configure('Treeview.Heading',background=panel,foreground=fg,bordercolor=palette['border'],relief='raised')
        style.map('Treeview.Heading',background=[('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('pressed',fg),('active',fg)])
        style.configure('History.Treeview',background=palette['surface'],fieldbackground=palette['surface'],foreground=fg,bordercolor=palette['border'],rowheight=24)
        style.map('History.Treeview',background=[('selected',palette['selection'])],foreground=[('selected',palette['selection_text'])])
        style.configure('History.Treeview.Heading',background=panel,foreground=fg,bordercolor=palette['border'],relief='raised')
        style.map('History.Treeview.Heading',background=[('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('pressed',fg),('active',fg)])
        style.configure('ImageSelect.TMenubutton',background=field,foreground=fg,relief='raised')
        style.map('ImageSelect.TMenubutton',background=[('active',panel),('pressed',panel),('disabled',field)],foreground=[('active',fg),('pressed',fg),('disabled',muted)])
        style.configure('Locked.TCombobox',fieldbackground=field,background=field,foreground=muted,selectforeground=muted)
        style.map('Locked.TCombobox',fieldbackground=[('disabled',field)],background=[('disabled',field)],foreground=[('disabled',muted)])
        # Option DB helps comboboxes created after the theme switch; direct popdown
        # styling below also fixes listboxes which Tk has already instantiated.
        self.option_add('*TCombobox*Listbox.background',field,'interactive');self.option_add('*TCombobox*Listbox.foreground',fg,'interactive')
        self.option_add('*TCombobox*Listbox.selectBackground',panel,'interactive');self.option_add('*TCombobox*Listbox.selectForeground',fg,'interactive')
        self._style_combobox_popdowns(field,fg,panel)
        for selector in (getattr(self,'_view_combo',None),getattr(self,'heatmap_combo',None),getattr(self,'lang_combo',None)):
            if isinstance(selector,ColorMenuSelect):selector.set_menu_theme(field,fg,panel,fg)
        if hasattr(self,'modifier_menu'):
            try:self.modifier_menu.configure(background=field,foreground=fg,activebackground=panel,activeforeground=fg)
            except tk.TclError:pass
        self._apply_history_window_theme()
        self._apply_history_capacity_dialog_theme()
        self._apply_help_window_theme()
        for surface in getattr(self,'_scroll_tab_surfaces',[]):
            try:surface.configure(background=palette['window'])
            except tk.TclError:pass
        if self._task_overlay is not None:
            try:
                self._task_overlay.configure(bg=panel)
                self._task_overlay_title.configure(bg=panel,fg=fg)
                self._task_overlay_progress.configure(bg=self._ui_theme_colors['bar_bg'])
                self._draw_task_progress(self._task_overlay_value)
            except tk.TclError:pass
        if hasattr(self,'heatmap_combo'):self._update_view_controls()
        if hasattr(self,'stats_chart_canvas'):
            self.stats_chart_canvas.configure(bg=panel);self._refresh_stats_chart()
        for row in getattr(self,'_batch_rows',[]):
            try:row['thumbnail_host'].configure(bg=panel);row['thumbnail'].configure(bg=panel)
            except (KeyError,tk.TclError):pass
            self._batch_draw_progress(row)
        self._schedule_native_titlebar_refresh()

    def _style_combobox_popdowns(self,field,fg,panel):
        for combo in self._walk(self):
            if not isinstance(combo,ttk.Combobox):continue
            try:
                pop=self.tk.call('ttk::combobox::PopdownWindow',str(combo))
                lb=pop+'.f.l'
                self.tk.call(lb,'configure','-background',field,'-foreground',fg,'-selectbackground',panel,'-selectforeground',fg)
            except tk.TclError:
                pass
