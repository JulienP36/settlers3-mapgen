"""Shortcut settings, Tk bindings and the application Help window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ..ui.i18n.shell import COMMAND_LABELS
from ..ui.i18n.shortcuts import SHORTCUT_UI_TEXT
from ..ui.widgets import _selector_icon
from .bindings import (
    DEFAULT_SHORTCUTS,
    canonicalize_shortcut,
    shortcut_from_event,
    shortcut_to_tk,
)


class ShortcutController:
    """Host contract: settings state, application commands and UI tooltips."""
    def _shortcut_settings_tab(self):
        f=self._scroll_notebook_tab('Raccourcis');f.columnconfigure(1,weight=1)
        self.shortcut_vars={};self.shortcut_display_vars={};self.shortcut_labels={};self.shortcut_capture_buttons={};self.shortcut_disable_buttons={};self.shortcut_reset_buttons={};self.shortcut_status_labels={};lang=self.prefs.get('language','fr');text=SHORTCUT_UI_TEXT[lang]
        self._shortcut_pending_icon=_selector_icon(f,'#f2b84b','pending',22);self._shortcut_conflict_icon=_selector_icon(f,'#e04444','conflict',22);self._shortcut_blank_icon=_selector_icon(f,'#7b8088','blank',22)
        for row,cmd in enumerate(DEFAULT_SHORTCUTS):
            lbl=ttk.Label(f,text=COMMAND_LABELS[lang][cmd]);lbl.grid(row=row,column=0,sticky='w',pady=4);self.shortcut_labels[cmd]=lbl
            var=tk.StringVar(value=self.prefs.get('shortcuts',{}).get(cmd,DEFAULT_SHORTCUTS[cmd]));self.shortcut_vars[cmd]=var
            display=tk.StringVar();self.shortcut_display_vars[cmd]=display
            capture=ttk.Button(f,textvariable=display,command=lambda c=cmd:self._start_shortcut_capture(c));capture.grid(row=row,column=1,sticky='ew',padx=(10,8),pady=4);capture.bind('<KeyPress>',lambda e,c=cmd:self._capture_shortcut_key(c,e));capture.bind('<KeyRelease>',lambda e,c=cmd:self._release_shortcut_key(c,e));self.shortcut_capture_buttons[cmd]=capture
            disable=ttk.Button(f,text=text['disable'],command=lambda c=cmd:self._disable_shortcut(c));disable.grid(row=row,column=2,sticky='e',padx=(0,6),pady=4);self.shortcut_disable_buttons[cmd]=disable
            btn=ttk.Button(f,text=text['reset'],command=lambda c=cmd:self._reset_one_shortcut(c));btn.grid(row=row,column=3,sticky='e',pady=4);self.shortcut_reset_buttons[cmd]=btn
            status=ttk.Label(f,image=self._shortcut_blank_icon,cursor='hand2');status.grid(row=row,column=4,padx=(7,0));status.bind('<Enter>',lambda e,c=cmd:self._shortcut_status_tooltip(c));status.bind('<Leave>',lambda e:self._hide_ui_tooltip());self.shortcut_status_labels[cmd]=status
            var.trace_add('write',lambda *_args,c=cmd:self._shortcut_values_changed(c))
            self._refresh_shortcut_capture_text(cmd)
        r=len(DEFAULT_SHORTCUTS)
        self.shortcut_apply_button=ttk.Button(f,text=text['apply'],command=self._apply_shortcut_settings);self.shortcut_apply_button.grid(row=r,column=0,pady=(12,0),sticky='w')
        self.shortcut_defaults_button=ttk.Button(f,text=text['defaults'],command=self._reset_shortcut_settings);self.shortcut_defaults_button.grid(row=r,column=1,pady=(12,0),sticky='w',padx=(10,0))
        self.shortcut_hint_label=ttk.Label(f,text=text['hint'],wraplength=720);self.shortcut_hint_label.grid(row=r+1,column=0,columnspan=4,sticky='w',pady=(8,0))
        self.shortcut_pending_label=ttk.Label(f,text='',style='ShortcutPending.TLabel',compound='left');self.shortcut_pending_label.grid(row=r+2,column=0,columnspan=5,sticky='w',pady=(7,0))
        self._refresh_shortcut_validation()

    @staticmethod
    def _tk_sequence(shortcut):
        try:return shortcut_to_tk(shortcut)
        except (TypeError,ValueError):return None

    def _refresh_shortcut_capture_text(self,cmd):
        display=getattr(self,'shortcut_display_vars',{}).get(cmd)
        if display is None:return
        lang=self.prefs.get('language','fr');text=SHORTCUT_UI_TEXT[lang]
        if self._shortcut_capture_command==cmd:display.set(text['capture'])
        else:display.set(self.shortcut_vars[cmd].get() or text['disabled'])

    def _shortcut_values_changed(self,cmd):
        self._refresh_shortcut_capture_text(cmd);self._refresh_shortcut_validation()

    def _refresh_shortcut_validation(self):
        variables=getattr(self,'shortcut_vars',{})
        if not variables:return
        lang=self.prefs.get('language','fr');text=SHORTCUT_UI_TEXT[lang];values={};invalid=set()
        for cmd,var in variables.items():
            try:values[cmd]=canonicalize_shortcut(var.get())
            except (TypeError,ValueError):values[cmd]=var.get();invalid.add(cmd)
        groups={}
        for cmd,value in values.items():
            if cmd not in invalid and value:groups.setdefault(value.casefold(),[]).append(cmd)
        conflicts={cmd for commands in groups.values() if len(commands)>1 for cmd in commands}
        applied=self.prefs.get('shortcuts',DEFAULT_SHORTCUTS);states={}
        for cmd,value in values.items():
            if cmd in invalid:
                states[cmd]=('invalid',text['invalid_tip'])
            elif cmd in conflicts:
                peers=[COMMAND_LABELS[lang][other] for other in groups[value.casefold()] if other!=cmd]
                states[cmd]=('conflict',text['conflict_tip'].format(shortcut=value,actions=', '.join(peers)))
            elif value!=applied.get(cmd,DEFAULT_SHORTCUTS[cmd]):
                states[cmd]=('pending',text['pending_tip'])
            else:states[cmd]=('clean','')
        self._shortcut_row_states=states
        for cmd,label in getattr(self,'shortcut_status_labels',{}).items():
            state=states.get(cmd,('clean',''))[0]
            image=self._shortcut_conflict_icon if state in ('invalid','conflict') else self._shortcut_pending_icon if state=='pending' else self._shortcut_blank_icon
            label.configure(image=image)
        blocked=bool(invalid or conflicts);pending=any(state=='pending' for state,_ in states.values())
        if hasattr(self,'shortcut_apply_button'):self.shortcut_apply_button.configure(state='disabled' if blocked else 'normal')
        if hasattr(self,'shortcut_pending_label'):
            self.shortcut_pending_label.configure(text=text['conflict_summary'] if blocked else text['pending'] if pending else '',image=self._shortcut_conflict_icon if blocked else self._shortcut_pending_icon if pending else '',style='ShortcutConflict.TLabel' if blocked else 'ShortcutPending.TLabel')

    def _shortcut_status_tooltip(self,cmd):
        label=getattr(self,'shortcut_status_labels',{}).get(cmd);state,tip=self._shortcut_row_states.get(cmd,('clean',''))
        if label is not None and tip:self._show_ui_tooltip(label,tip,key=('shortcut-status',cmd,state,tip))
        else:self._hide_ui_tooltip()

    def _start_shortcut_capture(self,cmd):
        previous=self._shortcut_capture_command;self._shortcut_capture_command=cmd;self._shortcut_capture_modifiers=set()
        if previous and previous!=cmd:self._refresh_shortcut_capture_text(previous)
        self._refresh_shortcut_capture_text(cmd)
        button=self.shortcut_capture_buttons.get(cmd)
        if button is not None:button.focus_set()

    def _finish_shortcut_capture(self,cmd):
        if self._shortcut_capture_command==cmd:self._shortcut_capture_command=None;self._shortcut_capture_modifiers=set()
        self._refresh_shortcut_capture_text(cmd)

    @staticmethod
    def _shortcut_modifier_key(keysym):
        if keysym in ('Control_L','Control_R'):return 'Ctrl'
        if keysym in ('Shift_L','Shift_R'):return 'Shift'
        if keysym in ('Alt_L','Alt_R','ISO_Level3_Shift'):return 'Alt'
        return None

    def _capture_shortcut_key(self,cmd,event):
        if self._shortcut_capture_command!=cmd:return None
        keysym=str(getattr(event,'keysym',''))
        if keysym=='Escape':self._finish_shortcut_capture(cmd);return 'break'
        if keysym in ('Delete','BackSpace'):
            self.shortcut_vars[cmd].set('');self._finish_shortcut_capture(cmd);return 'break'
        modifier=self._shortcut_modifier_key(keysym)
        if modifier:self._shortcut_capture_modifiers.add(modifier);return 'break'
        state=int(getattr(event,'state',0));modifiers=set(self._shortcut_capture_modifiers)
        try:value=shortcut_from_event(keysym,state,pressed_modifiers=modifiers)
        except (TypeError,ValueError):return 'break'
        if value is None:return 'break'
        self.shortcut_vars[cmd].set(value);self._finish_shortcut_capture(cmd);return 'break'

    def _release_shortcut_key(self,cmd,event):
        if self._shortcut_capture_command!=cmd:return None
        modifier=self._shortcut_modifier_key(str(getattr(event,'keysym','')))
        if modifier:self._shortcut_capture_modifiers.discard(modifier)
        return 'break'

    def _disable_shortcut(self,cmd):
        self.shortcut_vars[cmd].set('');self._finish_shortcut_capture(cmd)

    def _bind_shortcuts(self):
        for seq in self._bound_shortcuts:
            try:self.unbind_all(seq)
            except tk.TclError:pass
        self._bound_shortcuts=[]
        actions={'generate':self.generate,'generate_batch':self._open_batch_window,'import':self.import_file,'export':self.export,'save_preview':self.save_preview,'manage_history':self._open_history_center,'reset_view':self._reset_view,'copy_seed':self._copy_seed,'toggle_ab':self._toggle_compare,'clear_compare':self._clear_compare_slots,'toggle_theme':self._toggle_theme,'help':self._show_help}
        for cmd,shortcut in self.prefs.get('shortcuts',DEFAULT_SHORTCUTS).items():
            seq=self._tk_sequence(shortcut)
            if seq and cmd in actions:
                self.bind_all(seq,lambda e,fn=actions[cmd]:(fn(),'break')[1]);self._bound_shortcuts.append(seq)

    def _apply_shortcut_settings(self):
        active=self._shortcut_capture_command
        if active:self._finish_shortcut_capture(active)
        vals={}
        for cmd,var in self.shortcut_vars.items():
            try:vals[cmd]=canonicalize_shortcut(var.get())
            except (TypeError,ValueError):self._refresh_shortcut_validation();return
        enabled=[value.casefold() for value in vals.values() if value]
        duplicate=next((value for value in vals.values() if value and enabled.count(value.casefold())>1),None)
        if duplicate:self._refresh_shortcut_validation();return
        self.prefs['shortcuts']=vals;self._save_prefs();self._bind_shortcuts();self._feedback('shortcut_applied','success')
        self._refresh_shortcut_validation();self._retranslate_help_window()

    def _reset_one_shortcut(self,cmd):
        self.shortcut_vars[cmd].set(DEFAULT_SHORTCUTS[cmd]);self._finish_shortcut_capture(cmd)

    def _reset_shortcut_settings(self):
        active=self._shortcut_capture_command
        if active:self._finish_shortcut_capture(active)
        for k,v in DEFAULT_SHORTCUTS.items():self.shortcut_vars[k].set(v);self._refresh_shortcut_capture_text(k)
        self._refresh_shortcut_validation()

    def _show_help(self):
        existing=self._help_window
        if existing is not None:
            try:existing.deiconify();existing.lift();existing.focus_force();return
            except tk.TclError:self._help_window=None
        w=tk.Toplevel(self);self._help_window=w;w.transient(self);w.resizable(True,True);w.minsize(480,380);w.protocol('WM_DELETE_WINDOW',self._close_help_window)
        body=ttk.Frame(w,padding=14);body.pack(fill='both',expand=True)
        shortcuts=ttk.LabelFrame(body,padding=10);shortcuts.pack(fill='both',expand=True);shortcuts.columnconfigure(0,weight=1);shortcuts.columnconfigure(1,weight=1)
        action_header=ttk.Label(shortcuts,anchor='w');action_header.grid(row=0,column=0,sticky='ew',padx=(0,12),pady=(0,5))
        shortcut_header=ttk.Label(shortcuts,anchor='w');shortcut_header.grid(row=0,column=1,sticky='ew',pady=(0,5))
        action_labels={};shortcut_labels={}
        for row,cmd in enumerate(DEFAULT_SHORTCUTS,start=1):
            action=ttk.Label(shortcuts,anchor='w');action.grid(row=row,column=0,sticky='ew',padx=(0,12),pady=2);action_labels[cmd]=action
            value=ttk.Label(shortcuts,anchor='w');value.grid(row=row,column=1,sticky='ew',pady=2);shortcut_labels[cmd]=value
        navigation=ttk.LabelFrame(body,padding=10);navigation.pack(fill='x',pady=(10,0))
        navigation_labels=[]
        for row in range(5):
            label=ttk.Label(navigation,anchor='w');label.grid(row=row,column=0,sticky='w',pady=1);navigation_labels.append(label)
        close=ttk.Button(body,command=self._close_help_window);close.pack(anchor='e',pady=(10,0))
        self._help_widgets={'shortcuts':shortcuts,'action_header':action_header,'shortcut_header':shortcut_header,'actions':action_labels,'values':shortcut_labels,'navigation':navigation,'navigation_labels':navigation_labels,'close':close}
        self._retranslate_help_window();self._apply_help_window_theme();w.update_idletasks()
        width=max(520,min(w.winfo_reqwidth(),w.winfo_screenwidth()-80));height=max(430,min(w.winfo_reqheight(),w.winfo_screenheight()-100));x=max(20,(w.winfo_screenwidth()-width)//2);y=max(20,(w.winfo_screenheight()-height)//2);w.geometry(f'{width}x{height}+{x}+{y}')

    def _close_help_window(self):
        w=self._help_window;self._help_window=None;self._help_widgets={}
        if w is not None:
            try:w.destroy()
            except tk.TclError:pass

    def _retranslate_help_window(self):
        w=self._help_window
        if w is None:return
        try:
            if not w.winfo_exists():self._help_window=None;self._help_widgets={};return
        except tk.TclError:self._help_window=None;self._help_widgets={};return
        lang=self.prefs.get('language','fr');text=SHORTCUT_UI_TEXT[lang];widgets=self._help_widgets;sc=self.prefs.get('shortcuts',DEFAULT_SHORTCUTS)
        w.title(text['help_title']);widgets['shortcuts'].configure(text=text['title']);widgets['action_header'].configure(text=text['action']);widgets['shortcut_header'].configure(text=text['shortcut']);widgets['navigation'].configure(text=text['navigation']);widgets['close'].configure(text=text['close'])
        for cmd,label in widgets['actions'].items():label.configure(text=COMMAND_LABELS[lang][cmd])
        for cmd,label in widgets['values'].items():label.configure(text=sc.get(cmd,DEFAULT_SHORTCUTS[cmd]) or text['disabled'])
        for label,value in zip(widgets['navigation_labels'],(text['wheel'],text['drag'],text['cache'],text['viewer_protection'],text['compare'])):label.configure(text=value)

    def _apply_help_window_theme(self):
        if self._help_window is None:return
        try:self._help_window.configure(background=self._ui_theme_colors.get('window','#202124'))
        except tk.TclError:pass
