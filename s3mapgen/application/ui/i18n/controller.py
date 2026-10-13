"""Runtime language switching for the composed desktop application."""

from __future__ import annotations

import tkinter as tk

from .starts import START_LABELS
from ....generation.modes import MODE_ORDER
from ...analysis.core import format_stats_report
from ..viewer.options import HEATMAP_ICON_COLORS, VIEW_ICON_COLORS
from .shell import (
    ARCHETYPE_INPUT_LABELS, ARCHETYPE_LABELS, COMMAND_LABELS, LANGUAGE_LABELS, MIRROR_LABELS, MODE_LABELS, NONE_LABELS,
    PREVIEW_START_MARKER_LABELS, PROJECTION_LABELS, TEXTS, THEME_LABELS,
    WINDOW_TITLES,
)
from .shortcuts import SHORTCUT_UI_TEXT
from .viewer import HEATMAP_LABELS, VIEW_LABELS


class LanguageController:
    """Host contract: translatable widgets and subsystem refresh hooks."""
    def _capture_translatable_widgets(self):
        self._i18n_widgets=[]
        for w in self._walk(self):
            try:text=str(w.cget('text'))
            except tk.TclError:continue
            if text in TEXTS:self._i18n_widgets.append((w,text))
        self._i18n_tabs=[]
        for tab in self.nb.tabs():
            text=self.nb.tab(tab,'text')
            if text in TEXTS:self._i18n_tabs.append((tab,text))

    def _apply_language(self):
        if not hasattr(self,'lang_var'):return
        if hasattr(self, '_hide_ui_tooltip'):
            self._hide_ui_tooltip()
        lang=self.prefs.get('language','fr');vk=self._view_key();hk=self._heatmap_key();mk=self._mode_key();ak=self._arch_key()
        self.title(WINDOW_TITLES[lang])
        for w,source in getattr(self,'_i18n_widgets',[]):
            try:w.configure(text=source if lang=='fr' else TEXTS[source].get(lang,TEXTS[source].get('en',source)))
            except tk.TclError:pass
        for tab,source in getattr(self,'_i18n_tabs',[]):self.nb.tab(tab,text=source if lang=='fr' else TEXTS[source].get(lang,TEXTS[source].get('en',source)))
        if self._view_combo:
            self._view_combo.set_items([(k,VIEW_LABELS[lang][k],VIEW_ICON_COLORS[k],k) for k in VIEW_LABELS[lang]])
            self._view_combo.configure(width=max(12,max(len(v) for v in VIEW_LABELS[lang].values())+1))
        self.view.set(VIEW_LABELS[lang][vk]);self._view_combo._sync_icon()
        self.heatmap_combo.set_items([(k,HEATMAP_LABELS[lang][k],HEATMAP_ICON_COLORS[k],('sprite:minerals/'+k) if k in ('coal','iron','gold','gems','sulfur') else ('sprite:heatmap/'+k) if k in ('trees','building_stones','fish') else 'dot') for k in HEATMAP_LABELS[lang]])
        self.heatmap_combo.configure(width=max(14,min(22,max(len(v) for v in HEATMAP_LABELS[lang].values())+1)))
        self.heatmap_var.set(HEATMAP_LABELS[lang][hk]);self.heatmap_combo._sync_icon()
        self.mode_combo.configure(values=[MODE_LABELS[lang][k] for k in MODE_ORDER]);self.mode.set(MODE_LABELS[lang][mk])
        self.arch.set(ARCHETYPE_LABELS[lang][ak])
        if hasattr(self,'_custom_refresh_main_archetype_input'):
            self._custom_refresh_main_archetype_input()
        else:
            self.arch_combo.configure(values=[ARCHETYPE_INPUT_LABELS[lang][k] for k in ('classic','continental','large_islands','team_islands')])
            self.arch_input.set(ARCHETYPE_INPUT_LABELS[lang]['classic'])
        if hasattr(self,'start_menu'):
            self.start_text.set(START_LABELS[lang][self._start_algorithm_key()])
            for index,key in enumerate(('auto','balanced','fair','islands')):
                self.start_menu.entryconfigure(index,label=START_LABELS[lang][key])
            self.start_menu.entryconfigure(5,label=START_LABELS[lang]['classic'])
            self.start_menu.entryconfigure(6,label=START_LABELS[lang]['nations'])
        if hasattr(self,'mirror_combo'):
            mirror=self._mirror_key()
            self.mirror_combo.configure(values=list(MIRROR_LABELS[lang].values()))
            self.mirror_combo.configure(width=max(8,max((len(str(value)) for value in MIRROR_LABELS[lang].values()),default=0)+2))
            self.mirror.set(MIRROR_LABELS[lang][mirror])
        if self._theme_combo:self._theme_combo.configure(values=list(THEME_LABELS[lang].values()))
        self.theme_var.set(THEME_LABELS[lang][self.prefs['theme']])
        if self._projection_combo:self._projection_combo.configure(values=list(PROJECTION_LABELS[lang].values()))
        self.projection_var.set(PROJECTION_LABELS[lang][self.prefs['projection']])
        if hasattr(self,'preview_marker_combo'):
            self.preview_marker_combo.configure(values=list(PREVIEW_START_MARKER_LABELS[lang].values()))
            self.preview_marker_var.set(PREVIEW_START_MARKER_LABELS[lang][self.prefs.get('preview_start_markers','small')])
        self.lang_var.set(LANGUAGE_LABELS[lang]);self.lang_combo._sync_icon()
        self._refresh_stats_chart_labels()
        if getattr(self,'current',None) and getattr(self,'stats',None):
            report=format_stats_report(self._ensure_stats_cache(),lang=lang)
            previous_state=self.stats.cget('state');position=self.stats.yview()
            # Text silently ignores writes while disabled. Keep this report
            # read-only outside the short translation update, as on load.
            try:
                self.stats.configure(state='normal')
                self.stats.delete('1.0','end');self.stats.insert('end',report)
            finally:
                self.stats.configure(state=previous_state)
            if position:self.stats.yview_moveto(position[0])
        self._refresh_stats_chart();self._refresh_compare_buttons()
        if hasattr(self, '_custom_refresh_after_language'):
            self._custom_refresh_after_language()
        for cmd,lbl in getattr(self,'shortcut_labels',{}).items():lbl.configure(text=COMMAND_LABELS[lang][cmd])
        shortcut_text=SHORTCUT_UI_TEXT[lang]
        for btn in getattr(self,'shortcut_reset_buttons',{}).values():btn.configure(text=shortcut_text['reset'])
        for btn in getattr(self,'shortcut_disable_buttons',{}).values():btn.configure(text=shortcut_text['disable'])
        if hasattr(self,'shortcut_apply_button'):self.shortcut_apply_button.configure(text=shortcut_text['apply'])
        if hasattr(self,'shortcut_defaults_button'):self.shortcut_defaults_button.configure(text=shortcut_text['defaults'])
        if hasattr(self,'shortcut_hint_label'):self.shortcut_hint_label.configure(text=shortcut_text['hint'])
        for cmd in getattr(self,'shortcut_vars',{}):self._refresh_shortcut_capture_text(cmd)
        self._refresh_shortcut_validation()
        if hasattr(self,'history_combo'):self._refresh_history()
        self._retranslate_history_center()
        self._retranslate_history_capacity_dialog()
        self._retranslate_help_window()
        self._apply_compact_action_icons()
        if hasattr(self,'_schedule_responsive_layout'):self._schedule_responsive_layout()
        self._update_view_controls();self._clear_inspector();self._retranslate_feedback()

    def _language_changed(self):
        selected=self.lang_var.get();self.prefs['language']=next((key for key,label in LANGUAGE_LABELS.items() if label==selected),'en');self._save_prefs();self._apply_language();self._retranslate_batch_window();self._refresh_preview(False)
