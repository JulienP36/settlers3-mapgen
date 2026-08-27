"""Runtime language switching for the composed desktop application."""

from __future__ import annotations

import tkinter as tk

from ....generation.archetypes import ARCHETYPE_ORDER
from ....generation.modes import MODE_ORDER
from ...analysis.core import format_stats_report
from ..viewer.options import HEATMAP_ICON_COLORS, VIEW_ICON_COLORS
from .shell import (
    ARCHETYPE_LABELS, COMMAND_LABELS, LANGUAGE_LABELS, MODE_LABELS, NONE_LABELS,
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
        self.heatmap_combo.set_items([(k,HEATMAP_LABELS[lang][k],HEATMAP_ICON_COLORS[k],'dot') for k in HEATMAP_LABELS[lang]])
        self.heatmap_combo.configure(width=max(14,min(22,max(len(v) for v in HEATMAP_LABELS[lang].values())+1)))
        self.heatmap_var.set(HEATMAP_LABELS[lang][hk]);self.heatmap_combo._sync_icon()
        self.mode_combo.configure(values=[MODE_LABELS[lang][k] for k in MODE_ORDER]);self.mode.set(MODE_LABELS[lang][mk])
        self.arch_combo.configure(values=[ARCHETYPE_LABELS[lang][k] for k in ARCHETYPE_ORDER]);self.arch.set(ARCHETYPE_LABELS[lang][ak])
        if hasattr(self,'modifier_text'):
            self.modifier_text.set(self._modifier_summary())
            try:self.modifier_menu.entryconfigure(0,label=NONE_LABELS.get(lang,NONE_LABELS['en']))
            except tk.TclError:pass
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
            st=self._ensure_stats_cache();self.stats.delete('1.0','end');self.stats.insert('end',format_stats_report(st,lang=lang))
        self._refresh_stats_chart();self._refresh_compare_buttons()
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
        self._update_view_controls();self._clear_inspector();self._retranslate_feedback()

    def _language_changed(self):
        selected=self.lang_var.get();self.prefs['language']=next((key for key,label in LANGUAGE_LABELS.items() if label==selected),'en');self._save_prefs();self._apply_language();self._retranslate_batch_window();self._refresh_preview(True)
