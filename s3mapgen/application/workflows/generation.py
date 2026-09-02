"""Application-level generation selection, cache and execution workflow.

The validated map-building implementation remains exclusively under the strict
s3mapgen.generation package; this controller only translates UI state into one
engine invocation and session-cache updates.
"""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import messagebox

from ...generation.archetypes import ARCHETYPES
from ...generation.core import (
    NATIVE_PLAYER_LIMITS as NATIVE_LIMITS,
    native_size_warning_kind,
)
from ...generation.modes import MODES, cache_engine_revision
from ..session.cache import GenerationCacheKey
from ..ui.i18n.common import _lang_text
from ..ui.i18n.shell import ARCHETYPE_LABELS, FEEDBACK_TEXT, MIRROR_LABELS, MODE_LABELS, NONE_LABELS


class GenerationWorkflowController:
    """Host contract: generation widgets, protected engine and session cache."""

    @staticmethod
    def _legacy_size_warning_key(mode, archetype, side):
        """Translate core size semantics into an application feedback key."""

        if mode != 'legacy' or archetype != 'continental':
            return None
        kind = native_size_warning_kind(side)
        return {
            'small': 'size_viability_warning',
            'extended': 'size_extended_warning',
        }.get(kind)

    def _mode_key(self):
        value=self.mode.get()
        for labels in MODE_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return next((k for k,v in MODES.items() if v.label==value),'legacy')

    def _arch_key(self):
        value=self.arch.get()
        for labels in ARCHETYPE_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return next((k for k,v in ARCHETYPES.items() if v.label==value),'continental')

    def _mirror_key(self):
        value=self.mirror.get()
        for labels in MIRROR_LABELS.values():
            for key,label in labels.items():
                if label==value:return int(key)
        return 0

    def _modifier_keys(self):
        # The future multi-select architecture is reserved. The only currently
        # valid state is no modifier, represented by an empty tuple.
        return ()

    def _modifier_summary(self):
        return NONE_LABELS.get(self.prefs.get('language','fr'),NONE_LABELS['en'])

    def _modifier_none_selected(self):
        # “None” is exclusive by definition and cannot be unchecked while it is
        # the sole available entry.
        self.modifier_none.set(True);self.modifier_text.set(self._modifier_summary())
        self._selection_changed();self._feedback('modifier_none','info')

    def random_seed(self):
        self.seed.set(str(random.randint(1,2_147_483_647)));self._feedback('seed_randomized','info',seed=str(self.seed.get()))

    def _copy_seed(self):
        value=str(self.seed.get());self.clipboard_clear();self.clipboard_append(value);self._feedback('seed_copied','success',seed=value)

    def _selection_changed(self):
        s=int(self.size.get());mkey=self._mode_key();akey=self._arch_key();m=MODES[mkey];a=ARCHETYPES[akey];lang=self.prefs.get('language','fr');warning_key=self._legacy_size_warning_key(mkey,akey,s)
        mode=MODE_LABELS[lang][mkey];arch=ARCHETYPE_LABELS[lang][akey];modifiers=self._modifier_summary()
        if not m.implemented:self._feedback('mode_reserved','warning',mode=mode)
        elif not a.implemented:self._feedback('arch_reserved','warning',archetype=arch)
        elif self._mirror_key() and not (mkey=='legacy' and akey=='continental'):self._feedback('mirror_reserved','warning')
        elif mkey!='legacy' and s!=768:self._feedback('size_reserved','warning',side=s,max_players=NATIVE_LIMITS[s])
        elif warning_key:self._feedback(warning_key,'warning',side=s,max_players=NATIVE_LIMITS[s])
        else:self._feedback('ready','ready',mode=mode,archetype=arch,modifiers=modifiers,side=s,players=int(self.players.get()))

    def _progress_stage(self,stage,detail,index):
        # Detailed generator stages can change too quickly to be readable as status messages.
        value=min(95,5+index*4);text=f'{stage} {detail}'.strip()
        if self._batch_running and self._batch_active_row is not None:
            row=self._batch_active_row
            try:
                self._batch_update_progress(row,value,text)
                # Process the Batch cancel button while the current synchronous
                # generator call is running.  Cancellation deliberately affects
                # only queued maps; the protected engine is never interrupted.
                self.update()
            except tk.TclError:pass
        elif self._task_overlay is not None:self._draw_task_progress(value,text)
        self.update_idletasks()

    def _cache_key(self):
        mode = self._mode_key()
        archetype = self._arch_key()
        return GenerationCacheKey(seed=int(self.seed.get()),side=int(self.size.get()),players=int(self.players.get()),mode=mode,archetype=archetype,modifiers=self._modifier_keys(),engine_revision=cache_engine_revision(mode, archetype),mirror_mode=self._mirror_key())

    def generate(self):
        try:
            side=int(self.size.get())
            key=self._cache_key();cached=self.session_cache.get(key);self.import_source=None;lang=self.prefs.get('language','fr')
            mode=MODE_LABELS[lang][key.mode];arch=ARCHETYPE_LABELS[lang][key.archetype];modifiers=self._modifier_summary()
            warning_key=self._legacy_size_warning_key(key.mode,key.archetype,key.side)
            if cached is not None:
                self.current=cached;self.session_cache.set_metadata(key,{'origin':'generated'});self._populate_current();self._invalidate_preview();self._refresh_preview(True);self._refresh_history()
                if warning_key:self._feedback(warning_key,'warning',side=key.side,max_players=NATIVE_LIMITS[key.side])
                else:self._feedback('cache_hit','success',seed=key.seed)
                return
            msg=FEEDBACK_TEXT[lang]['generating'].format(archetype=arch,mode=mode,modifiers=modifiers,side=side,players=int(self.players.get()),seed=int(self.seed.get()))
            self._task_begin(msg,2);self.current=self.generator.generate(int(self.players.get()),int(self.seed.get()),mode=self._mode_key(),archetype=self._arch_key(),side=side,mirror_mode=self._mirror_key())
            retained=self.session_cache.put(key,self.current);self.session_cache.set_metadata(key,{'origin':'generated'});self._refresh_history();self._task_progress(97,_lang_text(lang,'Finalisation de l’aperçu…','Finalizing preview…','Vorschau wird fertiggestellt…','Finalizando vista previa…'));self._populate_current();self._invalidate_preview();self._refresh_preview(True)
            done=FEEDBACK_TEXT[lang]['generated'].format(archetype=arch,mode=mode,modifiers=modifiers,side=side,players=int(self.players.get()),seed=int(self.seed.get()));self._task_done(done)
            if warning_key:
                self._feedback(warning_key,'warning',side=key.side,max_players=NATIVE_LIMITS[key.side])
            elif not retained:self._feedback('history_not_retained','warning')
        except Exception as e:
            import traceback;self._task_error(_lang_text(self.prefs.get('language','fr'),'Erreur de génération','Generation error','Generierungsfehler','Error de generación'));messagebox.showerror('MapGen',f'{e}\n\n{traceback.format_exc()}')
