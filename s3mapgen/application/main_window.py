"""Current desktop application window above the validated generation runtime.

The module is the explicit composition of feature controllers and owns only the
remaining shell layout/state glue. Generation is injected by
:mod:`s3mapgen.application.runtime` so UI maintenance does not silently replace
the validated engine implementation.
"""

from __future__ import annotations
import tkinter as tk
from tkinter import ttk

from .shell import NATIVE_LIMITS, ShellWindow
from ..generation.modes import MODES, MODE_ORDER
from ..generation.archetypes import ARCHETYPES, ARCHETYPE_ORDER
from .batch import BatchController
from .history import HistoryController
from .analysis.controller import AnalysisController
from .exports.controller import ExportController
from .shortcuts.controller import ShortcutController
from .viewer.controller import ViewerController
from .imports import ImportController
from .settings import SettingsController
from .ui.i18n.controller import LanguageController
from .ui.theme.controller import ThemeController
from .tasks import TaskController
from .workflows import GenerationWorkflowController
from .settings.preferences import load_settings
from .session.cache import SessionGenerationCache, SessionStatsCache
from .analysis.core import format_stats_report
from .platform.titlebar import apply_native_titlebar
from .ui.i18n.shell import (
    FEEDBACK_TEXT,
    LANGUAGE_LABELS,
)
from .ui.widgets import (
    ColorMenuSelect,
    _history_heading_lock_icon,
    _selector_icon,
)

class MainWindow(ViewerController, AnalysisController, ExportController, ShortcutController, BatchController, HistoryController, ImportController, TaskController, GenerationWorkflowController, LanguageController, ThemeController, SettingsController, ShellWindow):
    """Composed desktop shell running the validated generation facade."""
    def __init__(self):
        self.prefs=load_settings();self._preview_base=None;self._preview_key=None
        self._zoom_after=None
        self.session_cache=SessionGenerationCache(max_entries=8)
        self.session_stats_cache=SessionStatsCache(max_entries=12)
        self._history_lookup={};self._compare_slots={'A':None,'B':None};self._compare_active=None
        # History remains session-only.  Manual locks protect cached outputs;
        # visual order is deliberately independent from the real LRU order.
        self._manual_history_locks=[];self._history_visual_order=[]
        self.session_cache.set_protected_provider(lambda:(getattr(self,'current',None),self._compare_slots.get('A'),self._compare_slots.get('B'),*self._manual_history_locks))
        self._preview_layer_base=None;self._preview_layer_key=None;self._preview_projection_cache={};self._prefs_save_after=None
        self._display_origin=(0,0);self._display_factor=1.0;self._display_base_size=(1,1);self._bound_shortcuts=[];self._task_overlay=None;self._task_overlay_value=0;self._task_overlay_detail='';self._status_kind='ready';self._feedback_key=None;self._feedback_values={};self._responsive_mode=None;self._layout_after=None
        self._batch_window=None;self._batch_rows=[];self._batch_queue=[];self._batch_running=False;self._batch_cancel_requested=False;self._batch_active_row=None;self._batch_last_success=None;self._batch_active_count=0
        self._batch_preview_window=None;self._batch_preview_label=None;self._batch_preview_photo=None;self._batch_preview_row=None;self._batch_preview_pinned=False;self._batch_preview_projection=None;self._batch_preview_drag_origin=None;self._batch_preview_zoom=1.0;self._batch_hover_after=None;self._batch_i18n={}
        self._map_export_window=None;self._stats_export_window=None
        self._history_window=None;self._history_tree=None;self._history_center_lookup={};self._history_window_widgets={};self._history_preview_photo=None;self._history_preview_key=None
        self._history_large_window=None;self._history_large_label=None;self._history_large_photo=None;self._history_large_image=None;self._history_large_key=None;self._history_large_zoom=.72;self._history_large_drag_origin=None;self._history_large_pinned=False;self._history_hover_after=None;self._history_preview_hover=False
        self._history_role_icons={};self._ui_tooltip_window=None;self._ui_tooltip_key=None
        self._history_capacity_dialog=None;self._history_capacity_dialog_widgets={}
        self._help_window=None;self._help_widgets={};self._shortcut_capture_command=None;self._shortcut_capture_modifiers=set();self._shortcut_row_states={};self._scroll_tab_surfaces=[]
        self._magnifier_hover_kind=None;self._magnifier_hover_ref=None;self._magnifier_active_kind=None;self._magnifier_active_ref=None
        self._native_titlebar_after=None
        super().__init__()
        self._apply_theme();self._update_view_controls()
        self.session_cache.resize(self.prefs.get('history_capacity',8))
        self.bind_class('Toplevel','<Map>',self._native_titlebar_mapped,add='+')
        self._apply_initial_window_geometry();self._apply_language();self._bind_shortcuts();self.bind('<Configure>',self._schedule_responsive_layout,add='+');self.bind('<Escape>',self._close_large_preview_escape,add='+');self.after_idle(self._apply_responsive_layout);self._schedule_native_titlebar_refresh()

    def _native_titlebar_mapped(self,event):
        self._schedule_native_titlebar_refresh()

    def _schedule_native_titlebar_refresh(self):
        if self._native_titlebar_after is not None:
            try:self.after_cancel(self._native_titlebar_after)
            except tk.TclError:pass
        self._native_titlebar_after=self.after_idle(self._refresh_native_titlebars)

    def _refresh_native_titlebars(self):
        self._native_titlebar_after=None
        palette=getattr(self,'_ui_theme_colors',None)
        if not palette:return
        targets=[self,*[w for w in self._walk(self) if isinstance(w,tk.Toplevel)]]
        seen=set()
        for target in targets:
            if target is None or id(target) in seen:continue
            seen.add(id(target))
            apply_native_titlebar(target,palette)

    def _close_large_preview_escape(self,event=None):
        closed=False
        if self._batch_preview_window is not None:self._batch_hide_preview_tooltip();closed=True
        if self._history_large_window is not None:self._history_hide_large_preview();closed=True
        return 'break' if closed else None


    def _build(self):
        self._build_foundation();self._configure_settings_and_navigation();top=self.header_root

        self._header_shell=ttk.Frame(top)
        self._header_shell.grid(row=0,column=0,sticky='ew')
        top.columnconfigure(0,weight=1)
        self.generation_panel=ttk.Frame(self._header_shell)
        self.global_panel=ttk.Frame(self._header_shell)

        def selector_group(parent,label):
            group=ttk.Frame(parent)
            ttk.Label(group,text=label).pack(anchor='w',pady=(0,2))
            return group

        # Generation row 1: selectors and their own independent action bar.
        primary_row=ttk.Frame(self.generation_panel);primary_row.pack(anchor='w',fill='x')
        mode_group=selector_group(primary_row,'Mode');mode_group.pack(side='left',padx=(0,5))
        self.mode_combo=ttk.Combobox(mode_group,textvariable=self.mode,values=[MODES[k].label for k in MODE_ORDER],state='readonly',width=20)
        self.mode_combo.pack();self.mode_combo.bind('<<ComboboxSelected>>',lambda e:self._selection_changed())
        arch_group=selector_group(primary_row,'Archétype');arch_group.pack(side='left',padx=(0,5))
        self.arch_combo=ttk.Combobox(arch_group,textvariable=self.arch,values=[ARCHETYPES[k].label for k in ARCHETYPE_ORDER],state='readonly',width=18)
        self.arch_combo.pack();self.arch_combo.bind('<<ComboboxSelected>>',lambda e:self._selection_changed())
        modifier_group=selector_group(primary_row,'Modificateurs');modifier_group.pack(side='left',padx=(0,7))
        self.modifier_label=modifier_group.winfo_children()[0]
        self.modifier_none=tk.BooleanVar(value=True);self.modifier_text=tk.StringVar(value='Aucun')
        self.modifier_button=ttk.Menubutton(modifier_group,textvariable=self.modifier_text,width=14,style='ImageSelect.TMenubutton')
        self.modifier_menu=tk.Menu(self.modifier_button,tearoff=False);self.modifier_button.configure(menu=self.modifier_menu)
        self.modifier_menu.add_checkbutton(label='Aucun',variable=self.modifier_none,command=self._modifier_none_selected)
        self.modifier_button.pack()
        primary_actions=ttk.Frame(primary_row);primary_actions.pack(side='left',fill='y')
        self.generate_button=ttk.Button(primary_actions,text='Générer',command=self.generate)
        self.generate_button.pack(side='left',anchor='s',padx=(0,4),pady=(19,0))
        self.batch_generate_button=ttk.Button(primary_actions,text='Générer lot…',command=self._open_batch_window)
        self.batch_generate_button.pack(side='left',anchor='s',padx=(0,0),pady=(19,0))

        # Generation row 2: dependent parameters followed by two local button bars.
        # Their spacing no longer depends on the selector columns above.
        secondary_row=ttk.Frame(self.generation_panel);secondary_row.pack(anchor='w',fill='x',pady=(5,0))
        size_group=selector_group(secondary_row,'Taille');size_group.pack(side='left',padx=(0,5))
        self.size_combo=ttk.Combobox(size_group,textvariable=self.size,values=[str(x) for x in NATIVE_LIMITS],state='readonly',width=8)
        self.size_combo.pack();self.size_combo.bind('<<ComboboxSelected>>',lambda e:self._size_changed())
        players_group=selector_group(secondary_row,'Joueurs');players_group.pack(side='left',padx=(0,5))
        self.players_spin=ttk.Spinbox(players_group,from_=2,to=20,textvariable=self.players,width=8);self.players_spin.pack()
        seed_group=selector_group(secondary_row,'Seed');seed_group.pack(side='left',padx=(0,7))
        self.seed_entry=ttk.Entry(seed_group,textvariable=self.seed,width=14);self.seed_entry.pack()
        seed_actions=ttk.Frame(secondary_row);seed_actions.pack(side='left',fill='y',padx=(0,7))
        self.random_seed_button=ttk.Button(seed_actions,text='🎲',width=3,command=self.random_seed)
        self.random_seed_button.pack(side='left',anchor='s',padx=(0,4),pady=(19,0))
        self.copy_seed_button=ttk.Button(seed_actions,text='Copier seed',command=self._copy_seed)
        self.copy_seed_button.pack(side='left',anchor='s',pady=(19,0))
        self.file_actions=ttk.Frame(secondary_row);self.file_actions.pack(side='left',fill='y')
        self.import_button=ttk.Button(self.file_actions,text='Importer…',command=self.import_file)
        self.import_button.pack(side='left',anchor='s',padx=(0,4),pady=(19,0))
        self.export_btn=ttk.Button(self.file_actions,text='Exporter…',command=self.export,state='disabled')
        self.export_btn.pack(side='left',anchor='s',padx=(0,4),pady=(19,0))
        self.preview_button=ttk.Button(self.file_actions,text='Aperçu PNG',command=self.save_preview)
        self.preview_button.pack(side='left',anchor='s',pady=(19,0))

        # Global controls have their own layout and never occupy generation columns.
        self.language_label=ttk.Label(self.global_panel,text='Langue')
        self.lang_var=tk.StringVar(value=LANGUAGE_LABELS[self.prefs.get('language','fr')])
        self.lang_combo=ColorMenuSelect(self.global_panel,self.lang_var,width=11,command=self._language_changed)
        self.lang_combo.set_items([
            ('fr',LANGUAGE_LABELS['fr'],'#0055a4','flag_fr'),('en',LANGUAGE_LABELS['en'],'#21468b','flag_en'),
            ('de',LANGUAGE_LABELS['de'],'#000000','flag_de'),('es',LANGUAGE_LABELS['es'],'#aa151b','flag_es'),
        ])
        self.help_button=ttk.Button(self.global_panel,text='Aide',command=self._show_help)
        self._theme_button=ttk.Button(self.global_panel,command=self._toggle_theme,width=3)
        self._refresh_theme_button_icon()

        # Session/Comparison is the middle region in wide mode and becomes one
        # coherent full-width block below the header only in compact mode.
        self.session_box=ttk.LabelFrame(self._header_shell,text='Session / Comparaison',padding=(6,4))
        self.session_history_label=ttk.Label(self.session_box,text='Historique session');self.session_history_label.grid(row=0,column=0,sticky='w')
        self.history_var=tk.StringVar(value='');self.history_combo=ttk.Combobox(self.session_box,textvariable=self.history_var,state='readonly',width=27)
        self.history_combo.bind('<<ComboboxSelected>>',lambda e:self._refresh_state_indicators())
        self.history_load_button=ttk.Button(self.session_box,text='Charger',command=self._load_history)
        self.history_clear_button=ttk.Button(self.session_box,text='Vider cache',command=self._clear_history)
        self.history_manage_button=ttk.Button(self.session_box,text='Gérer…',command=self._open_history_center)
        self._compare_led_off=_selector_icon(self,'#7b8088','status_off',18);self._compare_led_on=_selector_icon(self,'#34a853','status_on',18)
        self._history_blank_icon=_selector_icon(self,'#7b8088','blank',16)
        self._delete_icon_off=_selector_icon(self.session_box,'#7b8088','cross',14)
        self._delete_icon_on=_selector_icon(self.session_box,'#e04444','cross',14)
        self.compare_a_button=ttk.Button(self.session_box,text='Définir A',image=self._compare_led_off,compound='left',command=lambda:self._set_compare_slot('A'))
        self.compare_b_button=ttk.Button(self.session_box,text='Définir B',image=self._compare_led_off,compound='left',command=lambda:self._set_compare_slot('B'))
        self.compare_toggle_button=ttk.Button(self.session_box,text='Basculer A/B',command=self._toggle_compare)
        self.clear_a_button=ttk.Button(self.session_box,text='',image=self._delete_icon_off,command=lambda:self._clear_compare_slot('A'))
        self.clear_b_button=ttk.Button(self.session_box,text='',image=self._delete_icon_off,command=lambda:self._clear_compare_slot('B'))
        self.clear_ab_button=ttk.Button(self.session_box,text='Vider A+B',command=self._clear_compare_slots)
        self.session_box.bind('<Configure>',self._apply_session_layout,add='+')
        self._apply_session_layout()

        self.inspector_var=tk.StringVar(value='Inspecteur : —')
        self._inspector_label=ttk.Label(top,textvariable=self.inspector_var,anchor='w')
        self._inspector_label.grid(row=1,column=0,sticky='ew',pady=(3,1))

        # Raster selector resources used by the independent viewer toolbar.
        self.heatmap_var=tk.StringVar(value='Arbres')
        self._lock_closed_icon=_selector_icon(self,'#d84a3a','lock_closed',18)
        self._lock_open_icon=_selector_icon(self,'#2ca85a','lock_open',18)
        self._history_heading_lock_icon=_history_heading_lock_icon(self)
        self.canvas.bind('<Motion>',self._inspect_motion,add='+');self.canvas.bind('<Leave>',lambda e:self._clear_inspector(),add='+')
        self._build_stats_charts_tab()
        self._shortcut_settings_tab()
        self._reorder_analysis_tabs()
        self._theme_combo=self._find_combo_for_var(self.theme_var);self._projection_combo=self._find_combo_for_var(self.projection_var)
        self._build_viewer_toolbar(top)
        self._capture_translatable_widgets();self._install_status_feedback(top)
        # Keep the ready message synchronized when the player spinbox changes.
        self.players.trace_add('write',lambda *_:self.after_idle(self._selection_changed))
        if hasattr(self,'opacity_scale'):
            self.opacity_scale.bind('<Button-1>',self._opacity_locked_hint,add='+')


    def _apply_initial_window_geometry(self):
        """Choose a useful initial size from the actual screen without assuming 1440p."""
        try:
            sw=max(900,int(self.winfo_screenwidth()));sh=max(700,int(self.winfo_screenheight()))
            w=min(1740,max(980,int(sw*0.90)));h=min(980,max(680,int(sh*0.86)))
            self.geometry(f'{w}x{h}');self.minsize(900,650)
        except tk.TclError:pass

    def _install_status_feedback(self,top):
        """Build the user-feedback strip below the active header."""
        self.status_display=tk.StringVar(value='')
        self.status_strip=ttk.Frame(top,padding=(4,2))
        self.status_strip.grid(row=2,column=0,sticky='ew',pady=(2,2))
        self.status_icon=ttk.Label(self.status_strip,text='●',width=2,anchor='center')
        self.status_icon.pack(side='left')
        self.status_label=ttk.Label(self.status_strip,textvariable=self.status_display,anchor='w')
        self.status_label.pack(side='left',fill='x',expand=True)
        self.status.trace_add('write',lambda *_:self._sync_status_display())
        if hasattr(self,'heatmap_title'):
            self.heatmap_title.bind('<Enter>',lambda e:self._heatmap_locked_hint(),add='+')
        self._sync_status_display();self._apply_responsive_layout()

    def _status_symbol(self):
        return {'ready':'●','info':'ℹ','busy':'◉','success':'✓','warning':'⚠','error':'✕'}.get(self._status_kind,'●')

    def _sync_status_display(self):
        if not hasattr(self,'status_display'):return
        self.status_display.set(str(self.status.get() or ''))
        if hasattr(self,'status_icon'):self.status_icon.configure(text=self._status_symbol())

    def _feedback(self,key,kind='info',**values):
        lang=self.prefs.get('language','fr');template=FEEDBACK_TEXT.get(lang,FEEDBACK_TEXT['fr']).get(key,key)
        self._feedback_key=key;self._feedback_values=dict(values);self._status_kind=kind;self.status.set(template.format(**values));getattr(self,'_sync_status_display',lambda:None)()

    def _retranslate_feedback(self):
        if self._feedback_key in FEEDBACK_TEXT.get(self.prefs.get('language','fr'),{}):
            kind=self._status_kind;self._feedback(self._feedback_key,kind,**self._feedback_values)
        else:self._sync_status_display()

    def _schedule_responsive_layout(self,event=None):
        if event is not None and event.widget is not self:return
        if self._layout_after:
            try:self.after_cancel(self._layout_after)
            except tk.TclError:pass
        self._layout_after=self.after(80,self._apply_responsive_layout)

    def _apply_responsive_layout(self):
        """Reflow whole functional regions without mixing their internal controls."""
        if not hasattr(self,'_header_shell'):return
        self._layout_after=None
        try:width=int(self.winfo_width())
        except tk.TclError:return
        # At 1600 px the rightmost theme action can clip for a few frames before
        # reflow. Keep the 1920 target wide, but switch earlier.
        compact=width<1750
        mode='compact' if compact else 'wide'
        if mode==self._responsive_mode:return
        self._responsive_mode=mode;shell=self._header_shell

        # Only selector widths adapt.  Text buttons retain their natural requested
        # width so translations are never clipped.
        try:
            self.mode_combo.configure(width=15 if compact else 20)
            self.arch_combo.configure(width=13 if compact else 18)
            self.modifier_button.configure(width=9 if compact else 14)
            self.lang_combo.configure(width=9 if compact else 11)
        except tk.TclError:pass

        for w in (self.generation_panel,self.session_box,self.global_panel):w.grid_forget()
        for c in range(5):shell.columnconfigure(c,weight=0,minsize=0)
        for r in range(2):shell.rowconfigure(r,weight=0,minsize=0)

        if compact:
            # Generation and global controls remain visibly separate at the 900 px
            # minimum; Session moves as a complete block below them.
            self.generation_panel.grid(row=0,column=0,sticky='nw')
            self.global_panel.grid(row=0,column=1,sticky='ne',padx=(10,0))
            self.session_box.grid(row=1,column=0,columnspan=2,sticky='ew',pady=(5,0))
            shell.columnconfigure(0,weight=1)
        else:
            # Fixed functional regions with elastic gutters keep Session genuinely
            # central instead of stretching it into a full-width second band.
            self.generation_panel.grid(row=0,column=0,sticky='nw')
            self.session_box.grid(row=0,column=2,sticky='n',padx=(10,10))
            self.global_panel.grid(row=0,column=4,sticky='ne')
            shell.columnconfigure(1,weight=1);shell.columnconfigure(3,weight=1)

        self._layout_global_controls(compact)
        shell.update_idletasks()
        self._session_layout_mode=None;self._apply_session_layout()

    def _layout_global_controls(self,compact):
        """Lay out the global region locally, never inside generation columns."""
        for w in (self.language_label,self.lang_combo,self.help_button,self._theme_button):w.grid_forget()
        for c in range(3):self.global_panel.columnconfigure(c,weight=0,minsize=0)
        self.language_label.grid(row=0,column=0,columnspan=3,sticky='w',pady=(0,2))
        self.lang_combo.grid(row=1,column=0,columnspan=3 if compact else 1,sticky='ew',padx=(0,4))
        if compact:
            self.help_button.grid(row=2,column=0,columnspan=2,sticky='ew',pady=(5,0),padx=(0,4))
            self._theme_button.grid(row=2,column=2,pady=(5,0))
        else:
            self.help_button.grid(row=1,column=1,padx=(0,4))
            self._theme_button.grid(row=1,column=2)

    def _apply_session_layout(self,event=None):
        """Keep full A/B identities when space allows and compact only near minimum."""
        if not hasattr(self,'session_box'):return
        try:width=int(event.width) if event is not None else int(self.session_box.winfo_width())
        except (AttributeError,tk.TclError,TypeError,ValueError):width=1
        compact=self._responsive_mode=='compact' and width<900
        mode='compact_ab' if compact else 'natural_ab'
        if getattr(self,'_session_layout_mode',None)==mode:return
        self._session_layout_mode=mode
        widgets=(self.history_combo,self.history_load_button,self.history_clear_button,self.history_manage_button,self.compare_a_button,self.compare_b_button,self.compare_toggle_button,self.clear_a_button,self.clear_b_button,self.clear_ab_button)
        for w in widgets:
            try:w.grid_forget()
            except tk.TclError:pass
        for c in range(8):self.session_box.columnconfigure(c,weight=0,minsize=0)
        self.history_combo.configure(width=27)
        self.history_combo.grid(row=0,column=1,columnspan=3,sticky='ew',padx=(6,6))
        self.session_box.columnconfigure(1,weight=1,minsize=210)

        # Full identity in roomy layouts; a bounded width only at the real minimum.
        self.compare_a_button.configure(width=8 if compact else 0)
        self.compare_a_button.grid(row=0,column=4,padx=(3,1))
        self.clear_a_button.configure(width=3)
        self.clear_a_button.grid(row=0,column=5,padx=(1,4))
        self.compare_b_button.configure(width=8 if compact else 0)
        self.compare_b_button.grid(row=0,column=6,padx=(3,1))
        self.clear_b_button.configure(width=3)
        self.clear_b_button.grid(row=0,column=7,padx=(1,0))

        # History/cache and global A/B actions remain grouped on row 2.
        self.history_clear_button.configure(width=10 if compact else 0)
        self.history_load_button.configure(width=9 if compact else 0)
        self.compare_toggle_button.configure(width=12 if compact else 0)
        self.clear_ab_button.configure(width=10 if compact else 0)
        self.history_clear_button.grid(row=1,column=1,padx=(6,2),pady=(4,0),sticky='w')
        self.history_load_button.grid(row=1,column=2,padx=2,pady=(4,0),sticky='w')
        self.history_manage_button.grid(row=1,column=3,padx=2,pady=(4,0),sticky='w')
        self.compare_toggle_button.grid(row=1,column=4,padx=2,pady=(4,0),sticky='w')
        self.clear_ab_button.grid(row=1,column=5,columnspan=2,padx=(3,2),pady=(4,0),sticky='w')


    def _populate_current(self,imported=False):
        # These panels are reports, not editors. Temporarily unlock them only while refreshing.
        report_widgets=[w for w in (getattr(self,'validation',None),getattr(self,'pipeline',None),getattr(self,'meta',None),getattr(self,'stats',None)) if w is not None]
        for w in report_widgets:w.configure(state='normal')
        self._populate_current_base(imported=imported)
        stats=self._ensure_stats_cache();lang=self.prefs.get('language','fr')
        if stats and hasattr(self,'stats'):
            self.stats.delete('1.0','end');self.stats.insert('end',format_stats_report(stats,lang=lang))
        for w in report_widgets:w.configure(state='disabled')
        self._refresh_stats_chart();self._refresh_state_indicators();self._refresh_history_preview()

    def _walk(self,root):
        for child in root.winfo_children():
            yield child;yield from self._walk(child)

def main():MainWindow().mainloop()
