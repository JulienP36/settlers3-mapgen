"""Session history, History Center, previews and A/B comparison.

``HistoryController`` is a behavior-preserving mixin. Its host supplies the
main viewer, cache, feedback, theme and export coordination APIs.
"""

from __future__ import annotations
import hashlib
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
from .order import cached_protected_outputs, move_visual_key, reconcile_visual_order
from ..rendering.preview import START_MARKER_SCALES, render
from ..session.cache import ImportedHistoryKey
from ..ui.i18n.common import _lang_text
from ..ui.i18n.history import HISTORY_TEXT, _CONTEXT_TEXT, _HISTORY_CAPACITY_DIALOG_TEXT
from ..ui.i18n.shell import ARCHETYPE_LABELS, FEEDBACK_TEXT, LOWER_NONE_LABELS, MODE_LABELS, TEXTS
from ..ui.theme import THEME_PALETTES
from ..ui.widgets import _history_heading_lock_icon, _history_role_icon, _thumbnail_with_magnifier

class HistoryController:
    def _history_capacity_changed(self):
        if self._history_capacity_dialog is not None:return
        old=int(self.prefs.get('history_capacity',8))
        try:value=int(self.history_capacity_var.get())
        except (TypeError,ValueError):value=old
        if value not in (4,8,12,16):value=old
        protected=len(self._cached_protected_outputs())
        if value<protected:
            self._show_history_capacity_warning(old,value,0,blocked=True,protected=protected);self.history_capacity_var.set(str(old));return
        removed=max(0,len(self.session_cache)-value)
        if value<old and removed:
            if not self._show_history_capacity_warning(old,value,removed):
                self.history_capacity_var.set(str(old));return
        self.prefs['history_capacity']=value;self.session_cache.resize(value);self._save_prefs();self._refresh_history()

    def _show_history_capacity_warning(self,old,new,removed,blocked=False,protected=0):
        if self._history_capacity_dialog is not None:return False
        lang=self.prefs.get('language','fr');dialog_text=_HISTORY_CAPACITY_DIALOG_TEXT[lang];history_text=HISTORY_TEXT[lang];result={'continue':False}
        parent=self._history_window or self;win=tk.Toplevel(parent);self._history_capacity_dialog=win;win.withdraw();win.title(dialog_text['title']);win.transient(parent);win.resizable(False,False)
        shell=ttk.Frame(win,padding=16);shell.pack(fill='both',expand=True)
        title=ttk.Label(shell,text=dialog_text['title'],style='Section.TLabel');title.pack(anchor='w',fill='x',pady=(0,10))
        body=history_text['capacity_protected'].format(new=new,protected=protected) if blocked else history_text['capacity_reduce'].format(old=old,new=new,removed=removed)
        message=ttk.Label(shell,text=body,justify='left',wraplength=480);message.pack(anchor='w',fill='x')
        buttons=ttk.Frame(shell);buttons.pack(fill='x',pady=(16,0))
        def close(accepted=False):
            result['continue']=bool(accepted)
            try:win.grab_release()
            except tk.TclError:pass
            self._history_capacity_dialog=None;self._history_capacity_dialog_widgets={}
            try:self.history_capacity_combo.configure(state='readonly')
            except tk.TclError:pass
            win.destroy()
        cancel_label=_lang_text(lang,'OK','OK','OK','OK') if blocked else dialog_text['cancel']
        cancel=ttk.Button(buttons,text=cancel_label,command=lambda:close(False));cancel.pack(side='right')
        confirm=None
        if not blocked:
            confirm=ttk.Button(buttons,text=dialog_text['continue'],command=lambda:close(True));confirm.pack(side='right',padx=(0,8))
        self._history_capacity_dialog_widgets={'title':title,'message':message,'cancel':cancel,'confirm':confirm,'old':old,'new':new,'removed':removed,'blocked':blocked,'protected':protected}
        win.protocol('WM_DELETE_WINDOW',lambda:close(False));win.bind('<Escape>',lambda e:close(False),add='+');win.bind('<Return>',lambda e:close(False if blocked else True),add='+')
        self._apply_history_capacity_dialog_theme();win.update_idletasks();width=max(460,win.winfo_reqwidth());height=win.winfo_reqheight();screen_w=win.winfo_screenwidth();screen_h=win.winfo_screenheight()
        x=parent.winfo_rootx()+(parent.winfo_width()-width)//2;y=parent.winfo_rooty()+(parent.winfo_height()-height)//2;x=max(8,min(x,screen_w-width-8));y=max(8,min(y,screen_h-height-48));win.geometry(f'{width}x{height}+{x}+{y}')
        try:self.history_capacity_combo.configure(state='disabled')
        except tk.TclError:pass
        win.deiconify();win.lift();win.focus_force();win.grab_set();win.wait_window();return result['continue']

    def _retranslate_history_capacity_dialog(self):
        win=self._history_capacity_dialog;widgets=self._history_capacity_dialog_widgets
        if win is None or not widgets:return
        try:
            lang=self.prefs.get('language','fr');dialog_text=_HISTORY_CAPACITY_DIALOG_TEXT[lang];history_text=HISTORY_TEXT[lang]
            win.title(dialog_text['title']);widgets['title'].configure(text=dialog_text['title'])
            if widgets.get('blocked'):
                widgets['message'].configure(text=history_text['capacity_protected'].format(new=widgets['new'],protected=widgets['protected']));widgets['cancel'].configure(text='OK')
            else:
                widgets['message'].configure(text=history_text['capacity_reduce'].format(old=widgets['old'],new=widgets['new'],removed=widgets['removed']));widgets['cancel'].configure(text=dialog_text['cancel']);widgets['confirm'].configure(text=dialog_text['continue'])
        except tk.TclError:pass

    def _apply_history_capacity_dialog_theme(self):
        win=self._history_capacity_dialog
        if win is None:return
        try:win.configure(background=getattr(self,'_ui_theme_colors',THEME_PALETTES['dark']).get('window','#202124'))
        except tk.TclError:pass

    def _history_label(self,key):
        meta=self.session_cache.metadata(key)
        origin=self._history_origin(key);prefix=HISTORY_TEXT[self.prefs.get('language','fr')].get(origin,origin)
        if isinstance(key,ImportedHistoryKey):
            name=meta.get('source_name') or f'{key.source_format} import'
            return f'{prefix} · {name} · {key.source_format} · {meta.get("side","?")} · {meta.get("players",0)}P'
        lang=self.prefs.get('language','fr');mods=LOWER_NONE_LABELS.get(lang,LOWER_NONE_LABELS['en']) if not key.modifiers else '+'.join(key.modifiers)
        mode=MODE_LABELS[lang].get(key.mode,key.mode);archetype=ARCHETYPE_LABELS[lang].get(key.archetype,key.archetype)
        return f'{prefix} · {key.seed} · {key.side} · {key.players}P · {mode} · {archetype} · {mods}'

    def _history_origin(self,key):
        return self.session_cache.metadata(key).get('origin','generated')

    def _ordered_history_entries(self):
        """Return the stable visual order without touching cache recency."""
        self._history_visual_order, ordered = reconcile_visual_order(
            self.session_cache.entries(),
            self._history_visual_order,
        )
        return ordered

    def _history_move_key(self,key,step):
        entries = self._ordered_history_entries()
        keys = [entry_key for entry_key, _ in entries]
        self._history_visual_order, moved = move_visual_key(keys, key, step)
        return moved

    def _cached_protected_outputs(self):
        candidates = (
            getattr(self, 'current', None),
            self._compare_slots.get('A'),
            self._compare_slots.get('B'),
            *self._manual_history_locks,
        )
        return cached_protected_outputs(self.session_cache.entries(), candidates)

    def _refresh_history(self,preferred_index=None):
        self._history_lookup={}
        for key,_ in self._ordered_history_entries():
            label=self._history_label(key);candidate=label;suffix=2
            while candidate in self._history_lookup:candidate=f'{label} · {suffix}';suffix+=1
            self._history_lookup[candidate]=key
        vals=list(self._history_lookup);self.history_combo.configure(values=vals)
        if vals and self.history_var.get() not in vals:self.history_var.set(vals[0])
        if not vals:self.history_var.set('')
        self._refresh_history_center(preferred_index=preferred_index);self._refresh_state_indicators()

    def _register_import_history(self,out,path):
        path=Path(path);digest=hashlib.sha256(path.read_bytes()).hexdigest();fmt=path.suffix[1:].upper()
        key=ImportedHistoryKey(digest=digest,source_format=fmt);state=out.state
        retained=self.session_cache.put(key,out,{'origin':'imported','source_format':fmt,'source_name':path.name,'source_path':str(path),'side':state.side,'players':len(state.starts) or state.metadata.get('players',0)})
        self._refresh_history()
        if not retained:self._feedback('history_not_retained','warning')

    def _display_history_key(self,key):
        # UI navigation is observational: only an actual generation cache hit
        # promotes an LRU entry. Displaying/assigning must keep list order stable.
        out=self.session_cache.peek(key) if key else None
        if out is None:self._feedback('history_empty','warning');return
        need_stats=self.session_stats_cache.get(out.state) is None
        if need_stats:self._task_begin(_lang_text(self.prefs.get('language','fr'),'Chargement de l’historique…','Loading history…','Verlauf wird geladen…','Cargando historial…'),10)
        self.current=out;source=self.session_cache.metadata(key).get('source_path');self.import_source=Path(source) if source else None
        self._populate_current(imported=isinstance(key,ImportedHistoryKey));self._invalidate_preview();self._refresh_preview(False);self._refresh_history()
        if need_stats:self._task_done(FEEDBACK_TEXT[self.prefs.get('language','fr')]['history_loaded'])
        else:self._feedback('history_loaded','success')

    def _history_roles_for_output(self,out):
        if out is None:return ()
        roles=[]
        if out is getattr(self,'current',None):roles.append('V')
        if self._compare_slots.get('A') is out:roles.append('A')
        if self._compare_slots.get('B') is out:roles.append('B')
        if any(value is out for value in self._manual_history_locks):roles.append('M')
        return tuple(roles)

    def _history_role_image(self,roles):
        roles=tuple(roles)
        if not roles:return self._history_blank_icon
        if roles not in self._history_role_icons:self._history_role_icons[roles]=_history_role_icon(self,roles)
        return self._history_role_icons[roles]

    def _history_role_tooltip_text(self,roles):
        lang=self.prefs.get('language','fr');ctx=_CONTEXT_TEXT[lang];parts=[]
        for role in roles:
            if role=='V':parts.append(ctx['viewer_role'])
            elif role in ('A','B'):parts.append(f'{role} = Slot {role}')
            elif role=='M':parts.append(ctx['manual_role'])
        return ctx['lock_tip'].format(roles=' · '.join(parts)) if parts else ''

    def _show_ui_tooltip(self,widget,text,key=None,x=None,y=None):
        if not text:return
        marker=key if key is not None else (id(widget),text)
        if self._ui_tooltip_window is not None and self._ui_tooltip_key==marker:return
        self._hide_ui_tooltip();colors=getattr(self,'_ui_theme_colors',THEME_PALETTES['dark'])
        win=tk.Toplevel(widget);win.withdraw();win.overrideredirect(True);win.attributes('-topmost',True)
        label=tk.Label(win,text=text,justify='left',wraplength=360,padx=7,pady=5,bg=colors.get('surface','#303134'),fg=colors.get('text','#e8eaed'),bd=1,relief='solid',highlightthickness=0);label.pack()
        win.update_idletasks()
        if x is None:x=widget.winfo_rootx()+12
        if y is None:y=widget.winfo_rooty()+widget.winfo_height()+6
        x=max(6,min(int(x),widget.winfo_screenwidth()-win.winfo_reqwidth()-6));y=max(6,min(int(y),widget.winfo_screenheight()-win.winfo_reqheight()-42))
        win.geometry(f'+{x}+{y}');win.deiconify();win.lift();self._ui_tooltip_window=win;self._ui_tooltip_key=marker

    def _hide_ui_tooltip(self):
        if self._ui_tooltip_window is not None:
            try:self._ui_tooltip_window.destroy()
            except tk.TclError:pass
        self._ui_tooltip_window=None;self._ui_tooltip_key=None

    def _history_tree_motion(self,event):
        tree=self._history_tree
        if tree is None:return
        iid=tree.identify_row(event.y);key=self._history_center_lookup.get(iid);out=self.session_cache.peek(key) if key else None;roles=self._history_roles_for_output(out)
        if roles:self._show_ui_tooltip(tree,self._history_role_tooltip_text(roles),key=('history-role',iid,roles),x=event.x_root+14,y=event.y_root+16)
        else:self._hide_ui_tooltip()

    @staticmethod
    def _magnifier_refs_match(left,right):
        if left is right:return True
        if isinstance(left,dict) or isinstance(right,dict):return False
        return left==right

    def _magnifier_state_for(self,kind,ref):
        hovered=self._magnifier_hover_kind==kind and self._magnifier_refs_match(self._magnifier_hover_ref,ref)
        active=self._magnifier_active_kind==kind and self._magnifier_refs_match(self._magnifier_active_ref,ref) and self._magnifier_preview_exists(kind,ref)
        if active and hovered:return 'close_hover' if self._magnifier_preview_pinned(kind,ref) else 'preview_hover'
        if active:return 'active'
        if hovered:return 'hover'
        return 'idle'

    def _refresh_magnifier_target(self,kind,ref):
        if kind=='batch' and isinstance(ref,dict):self._batch_refresh_thumbnail_photo(ref)
        elif kind=='history' and self._magnifier_refs_match(self._history_selected_key(),ref):self._history_refresh_thumbnail_photo()

    def _set_magnifier_hover(self,kind=None,ref=None):
        old_kind,old_ref=self._magnifier_hover_kind,self._magnifier_hover_ref
        self._magnifier_hover_kind=kind;self._magnifier_hover_ref=ref
        if old_kind is not None:self._refresh_magnifier_target(old_kind,old_ref)
        if kind is not None and not (old_kind==kind and self._magnifier_refs_match(old_ref,ref)):self._refresh_magnifier_target(kind,ref)

    def _set_magnifier_active(self,kind=None,ref=None):
        old_kind,old_ref=self._magnifier_active_kind,self._magnifier_active_ref
        self._magnifier_active_kind=kind;self._magnifier_active_ref=ref
        if old_kind is not None:self._refresh_magnifier_target(old_kind,old_ref)
        if kind is not None and not (old_kind==kind and self._magnifier_refs_match(old_ref,ref)):self._refresh_magnifier_target(kind,ref)

    def _activate_magnifier(self,kind,ref):self._set_magnifier_active(kind,ref)

    def _magnifier_preview_exists(self,kind,ref):
        if kind=='batch':return self._batch_preview_window is not None and self._batch_preview_row is ref
        if kind=='history':return self._history_large_window is not None and self._magnifier_refs_match(self._history_large_key[0] if self._history_large_key else None,ref)
        return False

    def _magnifier_preview_pinned(self,kind,ref):
        if kind=='batch':return self._batch_preview_pinned and self._batch_preview_row is ref
        if kind=='history':return self._history_large_pinned and self._magnifier_refs_match(self._history_large_key[0] if self._history_large_key else None,ref)
        return False

    def _restore_magnifier_visual(self):
        kind,ref=self._magnifier_active_kind,self._magnifier_active_ref
        if kind is not None and self._magnifier_preview_exists(kind,ref):self._refresh_magnifier_target(kind,ref);return
        if self._batch_preview_pinned and self._batch_preview_window is not None:
            self._set_magnifier_active('batch',self._batch_preview_row);return
        if self._history_large_pinned and self._history_large_window is not None and self._history_large_key:
            self._set_magnifier_active('history',self._history_large_key[0]);return
        self._set_magnifier_active()

    def _open_history_center(self):
        if self._history_window is not None:
            try:self._history_window.deiconify();self._history_window.lift();self._history_window.focus_force();return
            except tk.TclError:self._history_window=None
        lang=self.prefs.get('language','fr');text=HISTORY_TEXT[lang];w=tk.Toplevel(self);self._history_window=w
        w.title(text['title']);w.transient(self);w.resizable(True,True);w.minsize(620,300);w.geometry('860x420');w.protocol('WM_DELETE_WINDOW',self._close_history_center)
        shell=ttk.Frame(w,padding=12);shell.pack(fill='both',expand=True);shell.rowconfigure(0,weight=1);shell.columnconfigure(0,weight=1)
        content=ttk.Panedwindow(shell,orient='horizontal');content.grid(row=0,column=0,columnspan=2,sticky='nsew')
        table_host=ttk.Frame(content);preview_host=ttk.LabelFrame(content,text=text['preview'],padding=8,style='History.TLabelframe');content.add(table_host,weight=4);content.add(preview_host,weight=2)
        table_host.rowconfigure(0,weight=1);table_host.columnconfigure(0,weight=1)
        columns=('rank','origin','map','details');tree=ttk.Treeview(table_host,columns=columns,show='tree headings',selectmode='browse',style='History.Treeview');self._history_tree=tree
        tree.heading('#0',text='',image=self._history_heading_lock_icon,anchor='center');tree.heading('rank',text='#',anchor='center');tree.heading('origin',text=text['origin']);tree.heading('map',text=text['map']);tree.heading('details',text=text['details'])
        tree.column('#0',width=68,minwidth=68,stretch=False,anchor='center');tree.column('rank',width=34,minwidth=34,stretch=False,anchor='center')
        tree.column('origin',width=100,stretch=False);tree.column('map',width=220,stretch=True);tree.column('details',width=330,stretch=True)
        scroll=ttk.Scrollbar(table_host,orient='vertical',command=tree.yview);tree.configure(yscrollcommand=scroll.set);tree.grid(row=0,column=0,sticky='nsew');scroll.grid(row=0,column=1,sticky='ns')
        tree.bind('<<TreeviewSelect>>',lambda e:self._history_selection_changed());tree.bind('<Double-1>',lambda e:self._history_center_show());tree.bind('<Motion>',self._history_tree_motion);tree.bind('<Leave>',lambda e:self._hide_ui_tooltip())
        preview_image_host=tk.Frame(preview_host,height=230,bd=0,highlightthickness=0);preview_image_host.pack(fill='x');preview_image_host.pack_propagate(False)
        self._history_preview_label=tk.Label(preview_image_host,text='—',anchor='center',bd=0,highlightthickness=0,cursor='hand2');self._history_preview_label.pack(fill='both',expand=True)
        self._history_preview_label.bind('<Button-1>',lambda e:self._history_toggle_large_preview());self._history_preview_label.bind('<Enter>',lambda e:self._history_schedule_hover_preview());self._history_preview_label.bind('<Leave>',lambda e:self._history_thumbnail_leave())
        preview_image_host.bind('<Enter>',lambda e:self._history_schedule_hover_preview(),add='+');preview_image_host.bind('<Leave>',lambda e:self._history_thumbnail_leave(),add='+')
        self._history_preview_status=tk.StringVar(value='');self._history_preview_source=tk.StringVar(value='')
        ttk.Label(preview_host,textvariable=self._history_preview_status,style='Panel.TLabel',justify='left',wraplength=260).pack(fill='x',pady=(8,2))
        ttk.Label(preview_host,textvariable=self._history_preview_source,style='PanelHint.TLabel',justify='left',wraplength=260).pack(fill='x')
        info=ttk.Label(shell,text=text['capacity'].format(used=len(self.session_cache),count=self.session_cache.max_entries),style='Hint.TLabel');info.grid(row=1,column=0,columnspan=2,sticky='w',pady=(8,4))
        actions=ttk.Frame(shell);actions.grid(row=2,column=0,columnspan=2,sticky='ew');actions.columnconfigure(7,weight=1)
        buttons={}
        for col,(name,label,command) in enumerate((('show',text['show'],self._history_center_show),('a',text['set_a'],lambda:self._history_center_assign('A')),('b',text['set_b'],lambda:self._history_center_assign('B')))):
            image=self._compare_led_off if name in ('show','a','b') else ''
            buttons[name]=ttk.Button(actions,text=label,image=image,compound='left',command=command,state='disabled');buttons[name].grid(row=0,column=col,padx=(0,6))
        buttons['lock']=ttk.Button(actions,text=text['lock'],image=self._lock_closed_icon,compound='left',command=self._history_center_toggle_manual_lock,state='disabled');buttons['lock'].grid(row=0,column=3,padx=(0,6))
        buttons['up']=ttk.Button(actions,text='↑',width=3,command=lambda:self._history_center_move(-1),state='disabled');buttons['up'].grid(row=0,column=4,padx=(0,3))
        buttons['down']=ttk.Button(actions,text='↓',width=3,command=lambda:self._history_center_move(1),state='disabled');buttons['down'].grid(row=0,column=5,padx=(0,6))
        buttons['delete']=ttk.Button(actions,text=text['delete'],command=self._history_center_delete,state='disabled');buttons['delete'].grid(row=0,column=6,padx=(0,6))
        buttons['clear']=ttk.Button(actions,text=text['clear'],command=self._history_center_clear);buttons['clear'].grid(row=0,column=8,padx=(6,6))
        buttons['close']=ttk.Button(actions,text=text['close'],command=self._close_history_center);buttons['close'].grid(row=0,column=9)
        buttons['up'].bind('<Enter>',lambda e:self._show_ui_tooltip(buttons['up'],HISTORY_TEXT[self.prefs.get('language','fr')]['move_up'],key='history-up'));buttons['up'].bind('<Leave>',lambda e:self._hide_ui_tooltip())
        buttons['down'].bind('<Enter>',lambda e:self._show_ui_tooltip(buttons['down'],HISTORY_TEXT[self.prefs.get('language','fr')]['move_down'],key='history-down'));buttons['down'].bind('<Leave>',lambda e:self._hide_ui_tooltip())
        self._history_window_widgets={'tree':tree,'info':info,'buttons':buttons,'preview_host':preview_host,'preview_image_host':preview_image_host};self._apply_history_window_theme();self._refresh_history_center()
        w.update_idletasks();screen_w=w.winfo_screenwidth();screen_h=w.winfo_screenheight();width=min(1120,max(760,screen_w-40));height=min(500,max(340,screen_h-80));x=max(0,min(self.winfo_rootx()+60,screen_w-width));y=max(0,min(self.winfo_rooty()+60,screen_h-height));w.geometry(f'{width}x{height}+{x}+{y}')

    def _close_history_center(self):
        win=self._history_window
        self._history_cancel_hover_preview();self._history_preview_hover=False
        if self._magnifier_hover_kind=='history':self._set_magnifier_hover()
        self._history_hide_large_preview();self._hide_ui_tooltip()
        self._history_window=None;self._history_tree=None;self._history_center_lookup={};self._history_window_widgets={}
        self._history_preview_label=None;self._history_preview_status=None;self._history_preview_source=None;self._history_preview_photo=None;self._history_preview_base_image=None;self._history_preview_key=None
        if win is not None:
            try:win.destroy()
            except tk.TclError:pass

    def _history_selected_key(self):
        if self._history_tree is None:return None
        try:
            if not self._history_tree.winfo_exists():return None
            selection=self._history_tree.selection();return self._history_center_lookup.get(selection[0]) if selection else None
        except tk.TclError:return None

    def _history_selection_changed(self):
        state='normal' if self._history_selected_key() is not None else 'disabled'
        for name in ('show','a','b','lock','delete'):
            button=self._history_window_widgets.get('buttons',{}).get(name)
            if button is not None:button.configure(state=state)
        key=self._history_selected_key();keys=[entry_key for entry_key,_ in self._ordered_history_entries()]
        index=keys.index(key) if key in keys else -1;buttons=self._history_window_widgets.get('buttons',{})
        if buttons.get('up') is not None:buttons['up'].configure(state='normal' if index>0 else 'disabled')
        if buttons.get('down') is not None:buttons['down'].configure(state='normal' if 0<=index<len(keys)-1 else 'disabled')
        self._refresh_history_preview();self._refresh_state_indicators()

    def _refresh_history_center(self,preferred_index=None):
        tree=self._history_tree
        if tree is None:return
        selected=self._history_selected_key();old_y=tree.yview()[0] if tree.get_children() else 0.0;tree.delete(*tree.get_children());self._history_center_lookup={};lang=self.prefs.get('language','fr');text=HISTORY_TEXT[lang]
        for index,(key,out) in enumerate(self._ordered_history_entries()):
            meta=self.session_cache.metadata(key);origin=self._history_origin(key);origin_label=text.get(origin,origin)
            if isinstance(key,ImportedHistoryKey):map_label=meta.get('source_name',key.source_format);details=f'(.{key.source_format.lower()}) · {meta.get("side",out.state.side)}×{meta.get("side",out.state.side)} · {meta.get("players",len(out.state.starts))}P'
            else:map_label=f'Seed {key.seed}';details=f'{key.side}×{key.side} · {key.players}P · {MODE_LABELS[lang].get(key.mode,key.mode)} · {ARCHETYPE_LABELS[lang].get(key.archetype,key.archetype)}'
            roles=self._history_roles_for_output(out)
            iid=f'h{index}';tree.insert('', 'end',iid=iid,text='',image=self._history_role_image(roles),values=(index+1,origin_label,map_label,details),tags=('even' if index%2==0 else 'odd',));self._history_center_lookup[iid]=key
            if key==selected:tree.selection_set(iid)
        children=tree.get_children()
        if not tree.selection() and children and preferred_index is not None:
            iid=children[max(0,min(int(preferred_index),len(children)-1))];tree.selection_set(iid);tree.focus(iid);tree.see(iid)
        elif tree.selection():tree.focus(tree.selection()[0])
        if children and preferred_index is None:tree.yview_moveto(old_y)
        info=self._history_window_widgets.get('info')
        if info is not None:info.configure(text=text['capacity'].format(used=len(self.session_cache),count=self.session_cache.max_entries))
        self._history_selection_changed()

    def _refresh_history_preview(self):
        label=getattr(self,'_history_preview_label',None)
        if self._history_window is None or label is None:return
        try:
            if not label.winfo_exists():return
        except tk.TclError:return
        key=self._history_selected_key();out=self.session_cache.peek(key) if key else None;lang=self.prefs.get('language','fr');text=HISTORY_TEXT[lang]
        if out is None:
            self._history_preview_photo=None;self._history_preview_base_image=None;self._history_preview_key=None;label.configure(image='',text='—');self._history_preview_status.set(text['empty']);self._history_preview_source.set('');self._history_hide_large_preview();return
        marker_mode=self.prefs.get('preview_start_markers','small')
        preview_key=(id(out.state),self.prefs.get('projection','square'),marker_mode)
        if preview_key!=self._history_preview_key or getattr(self,'_history_preview_base_image',None) is None:
            image=render(out.state,labels=False,view='global',projection=self.prefs.get('projection','square'),start_markers=marker_mode!='hidden',start_marker_scale=START_MARKER_SCALES.get(marker_mode,START_MARKER_SCALES['small']))
            image.thumbnail((300,210),Image.Resampling.NEAREST);self._history_preview_base_image=image;self._history_preview_key=preview_key
        self._history_refresh_thumbnail_photo()
        slots=[slot for slot,value in self._compare_slots.items() if value is out];parts=[text['comparison'].format(slots='/'.join(slots) if slots else text['none'])]
        if getattr(self,'current',None) is out:parts.append(text['current'])
        reasons=[]
        if getattr(self,'current',None) is out:reasons.append(text['main_view'])
        reasons.extend(f'Slot {slot}' for slot in slots)
        if reasons:parts.append(text['protected'].format(reasons=', '.join(reasons)))
        if any(value is out for value in self._manual_history_locks):reasons.append(text['manual_lock'])
        entries=self._ordered_history_entries();position=next((index+1 for index,(entry_key,_) in enumerate(entries) if entry_key==key),1);parts.append(text['display_position'].format(position=position,total=len(entries)))
        self._history_preview_status.set('\n'.join(parts));source=self.session_cache.metadata(key).get('source_path');self._history_preview_source.set(text['source'].format(path=source) if source else '')
        if self._history_large_window is not None:self._history_refresh_large_preview()

    def _history_refresh_thumbnail_photo(self):
        label=getattr(self,'_history_preview_label',None);base=getattr(self,'_history_preview_base_image',None);key=self._history_selected_key()
        if self._history_window is None or label is None or base is None or key is None:return
        try:
            if not label.winfo_exists():return
            shown=_thumbnail_with_magnifier(base,self._magnifier_state_for('history',key));self._history_preview_photo=ImageTk.PhotoImage(shown,master=label);label.configure(image=self._history_preview_photo,text='')
        except tk.TclError:return

    def _history_schedule_hover_preview(self):
        self._history_cancel_hover_preview();self._history_preview_hover=True
        key=self._history_selected_key()
        if key is None:return
        self._set_magnifier_hover('history',key)
        if not self._history_large_pinned:self._history_hover_after=self.after(700,lambda k=key:self._history_hover_preview_ready(k))

    def _history_hover_preview_ready(self,key):
        self._history_hover_after=None
        if self._history_preview_hover and self._magnifier_refs_match(self._history_selected_key(),key):self._history_show_large_preview(False)

    def _history_cancel_hover_preview(self):
        if self._history_hover_after is not None:
            try:self.after_cancel(self._history_hover_after)
            except tk.TclError:pass
            self._history_hover_after=None

    def _history_thumbnail_leave(self):
        self._history_cancel_hover_preview()
        try:self.after_idle(self._history_finish_thumbnail_leave)
        except tk.TclError:pass

    def _history_finish_thumbnail_leave(self):
        host=self._history_window_widgets.get('preview_image_host')
        if host is not None:
            try:
                x,y=host.winfo_pointerxy();inside=host.winfo_rootx()<=x<host.winfo_rootx()+host.winfo_width() and host.winfo_rooty()<=y<host.winfo_rooty()+host.winfo_height()
                if inside:return
            except tk.TclError:pass
        self._history_preview_hover=False
        self._set_magnifier_hover()
        if not self._history_large_pinned:self._history_hide_large_preview()
        else:self._restore_magnifier_visual()

    def _history_toggle_large_preview(self):
        key=self._history_selected_key()
        if key is None:return
        if self._history_large_pinned and self._history_large_window is not None and self._history_large_key and self._history_large_key[0]==key:
            self._history_hide_large_preview();return
        self._history_show_large_preview(True)

    def _history_show_large_preview(self,pinned=False):
        self._history_cancel_hover_preview()
        key=self._history_selected_key();out=self.session_cache.peek(key) if key else None
        if out is None:return
        old=self._history_large_window;preserved=None
        if old is not None:
            try:preserved=(old.winfo_x(),old.winfo_y())
            except tk.TclError:pass
        marker_mode=self.prefs.get('preview_start_markers','small');projection=self.prefs.get('projection','square')
        render_key=(key,id(out.state),projection,marker_mode)
        if render_key!=self._history_large_key or self._history_large_image is None:
            self._history_large_image=render(out.state,labels=False,view='global',projection=projection,start_markers=marker_mode!='hidden',start_marker_scale=START_MARKER_SCALES.get(marker_mode,START_MARKER_SCALES['small']))
            self._history_large_key=render_key
        if pinned:
            shown,size=self._history_large_scaled_image(self._history_large_image)
            if preserved is None:preserved=self._history_large_initial_position(size)
            x,y=self._history_large_clamp(*preserved,size)
        else:
            shown,size,x,y=self._temporary_preview_geometry(self._history_large_image,self._history_large_zoom,self._history_preview_label)
        old_projection=getattr(self,'_history_large_projection',None)
        if old is not None and self._history_large_label is not None and old_projection==projection:
            try:
                photo=ImageTk.PhotoImage(shown,master=old);self._history_large_label.configure(image=photo,cursor='fleur' if pinned else 'arrow');self._history_large_photo=photo;old.geometry(f'{size[0]}x{size[1]}+{x}+{y}');self._history_large_pinned=bool(pinned);self._history_bind_large_surface(self._history_large_label,pinned);self._activate_magnifier('history',key);old.lift();return
            except tk.TclError:pass
        win,label,photo=self._history_build_large_surface(shown,size,x,y,pinned)
        self._history_large_window=win;self._history_large_label=label;self._history_large_photo=photo;self._history_large_projection=projection;self._history_large_pinned=bool(pinned);self._activate_magnifier('history',key)
        win.deiconify();win.lift();win.update_idletasks()
        if old is not None and old is not win:
            try:old.destroy()
            except tk.TclError:pass

    def _history_large_scaled_image(self,image):
        screen_w=self.winfo_screenwidth();screen_h=self.winfo_screenheight();max_w=max(320,screen_w-80);max_h=max(280,screen_h-120)
        factor=min(float(self._history_large_zoom),max_w/image.width,max_h/image.height)
        size=(max(1,round(image.width*factor)),max(1,round(image.height*factor)))
        return image.resize(size,Image.Resampling.NEAREST),size

    def _history_large_initial_position(self,size):
        anchor=self._history_preview_label;anchor.update_idletasks();screen_w=self.winfo_screenwidth();margin=14
        ax=anchor.winfo_rootx();ay=anchor.winfo_rooty();aw=anchor.winfo_width()
        x=ax-size[0]-margin if ax>=screen_w-(ax+aw) else ax+aw+margin
        return x,ay

    def _history_large_clamp(self,x,y,size):
        screen_w=self.winfo_screenwidth();screen_h=self.winfo_screenheight()
        return max(8,min(int(x),screen_w-size[0]-8)),max(8,min(int(y),screen_h-size[1]-48))

    def _temporary_preview_geometry(self,image,zoom,anchor):
        """Fit an unpinned preview beside its source without changing stored zoom."""
        screen_w=self.winfo_screenwidth();screen_h=self.winfo_screenheight();gap=18
        anchor.update_idletasks();ax=anchor.winfo_rootx();ay=anchor.winfo_rooty();aw=anchor.winfo_width();ah=anchor.winfo_height()
        left,top,right,bottom=8,8,screen_w-8,screen_h-48
        regions=(
            ('left',left,top,max(left,ax-gap),bottom),
            ('right',min(right,ax+aw+gap),top,right,bottom),
            ('top',left,top,right,max(top,ay-gap)),
            ('bottom',left,min(bottom,ay+ah+gap),right,bottom),
        )
        choices=[]
        for priority,(side,x0,y0,x1,y1) in enumerate(regions):
            available_w=max(0,x1-x0);available_h=max(0,y1-y0)
            if available_w<1 or available_h<1:continue
            factor=min(float(zoom),available_w/image.width,available_h/image.height)
            if factor<=0:continue
            width=max(1,round(image.width*factor));height=max(1,round(image.height*factor))
            if side=='left':x=x1-width;y=max(y0,min(ay+(ah-height)//2,y1-height))
            elif side=='right':x=x0;y=max(y0,min(ay+(ah-height)//2,y1-height))
            elif side=='top':x=max(x0,min(ax+(aw-width)//2,x1-width));y=y1-height
            else:x=max(x0,min(ax+(aw-width)//2,x1-width));y=y0
            choices.append((factor,-priority,(width,height),int(x),int(y)))
        if not choices:
            shown,size=self._history_large_scaled_image(image);x,y=self._history_large_clamp(8,8,size);return shown,size,x,y
        _,_,size,x,y=max(choices,key=lambda item:(item[0],item[1]))
        return image.resize(size,Image.Resampling.NEAREST),size,x,y

    def _history_build_large_surface(self,shown,size,x,y,pinned):
        chroma='#ff00ff';win=tk.Toplevel(self._history_window or self);win.withdraw();win.overrideredirect(True);win.configure(bg=chroma);win.attributes('-topmost',True)
        try:win.wm_attributes('-transparentcolor',chroma)
        except tk.TclError:pass
        photo=ImageTk.PhotoImage(shown,master=win);label=tk.Label(win,image=photo,bg=chroma,bd=0,highlightthickness=0,cursor='fleur' if pinned else 'arrow');label.pack()
        win.geometry(f'{size[0]}x{size[1]}+{x}+{y}')
        self._history_bind_large_surface(label,pinned)
        win.bind('<Escape>',lambda e:self._history_hide_large_preview(),add='+');win.update_idletasks();return win,label,photo

    def _history_bind_large_surface(self,label,pinned):
        for sequence in ('<ButtonPress-1>','<B1-Motion>','<ButtonRelease-1>','<MouseWheel>','<Button-4>','<Button-5>'):label.unbind(sequence)
        if pinned:
            label.bind('<ButtonPress-1>',self._history_large_drag_start);label.bind('<B1-Motion>',self._history_large_drag_move);label.bind('<ButtonRelease-1>',self._history_large_drag_end)
        label.bind('<MouseWheel>',self._history_large_wheel);label.bind('<Button-4>',lambda e:self._history_large_wheel(e,1));label.bind('<Button-5>',lambda e:self._history_large_wheel(e,-1))

    def _history_large_drag_start(self,event):
        win=self._history_large_window
        if win is None:return 'break'
        try:self._history_large_drag_origin=(event.x_root,event.y_root,win.winfo_x(),win.winfo_y())
        except tk.TclError:self._history_large_drag_origin=None
        return 'break'

    def _history_large_drag_move(self,event):
        win=self._history_large_window;origin=self._history_large_drag_origin
        if win is None or origin is None:return 'break'
        try:
            size=(win.winfo_width(),win.winfo_height());x,y=self._history_large_clamp(origin[2]+event.x_root-origin[0],origin[3]+event.y_root-origin[1],size);win.geometry(f'+{x}+{y}')
        except tk.TclError:pass
        return 'break'

    def _history_large_drag_end(self,event=None):self._history_large_drag_origin=None;return 'break'

    def _history_large_wheel(self,event,direction=None):
        if direction is None:direction=1 if getattr(event,'delta',0)>0 else -1
        self._history_large_zoom=max(.35,min(1.25,self._history_large_zoom+(.1 if direction>0 else -.1)));self._history_refresh_large_preview();return 'break'

    def _history_refresh_large_preview(self):
        if self._history_large_window is not None:self._history_show_large_preview(self._history_large_pinned)

    def _history_hide_large_preview(self):
        closing_key=self._history_large_key[0] if self._history_large_key else None
        if self._history_large_window is not None:
            try:self._history_large_window.destroy()
            except tk.TclError:pass
        self._history_large_window=None;self._history_large_label=None;self._history_large_photo=None;self._history_large_image=None;self._history_large_key=None;self._history_large_drag_origin=None;self._history_large_pinned=False;self._history_large_projection=None
        if self._magnifier_active_kind=='history' and self._magnifier_refs_match(self._magnifier_active_ref,closing_key):self._set_magnifier_active()
        self._restore_magnifier_visual()

    def _history_center_show(self):
        key=self._history_selected_key()
        if key is not None:self._display_history_key(key)

    def _history_center_assign(self,slot):
        key=self._history_selected_key();out=self.session_cache.peek(key) if key else None
        if out is not None:self._set_compare_output(slot,out);self._refresh_history()

    def _history_center_toggle_manual_lock(self):
        key=self._history_selected_key();out=self.session_cache.peek(key) if key else None
        if out is None:return
        locked=any(value is out for value in self._manual_history_locks);text=HISTORY_TEXT[self.prefs.get('language','fr')]
        if locked:self._manual_history_locks=[value for value in self._manual_history_locks if value is not out];message=text['unlocked']
        else:self._manual_history_locks.append(out);message=text['locked']
        self._feedback_key=None;self._status_kind='info';self.status.set(message);self._sync_status_display();self._refresh_history()

    def _history_center_move(self,step):
        key=self._history_selected_key()
        if key is None or not self._history_move_key(key,step):return
        self._refresh_history();self._refresh_state_indicators()

    def _history_center_delete(self):
        key=self._history_selected_key()
        if key is None:return
        children=list(self._history_tree.get_children());selection=self._history_tree.selection();index=children.index(selection[0]) if selection and selection[0] in children else 0
        out=self.session_cache.peek(key);slots=[slot for slot,value in self._compare_slots.items() if value is out];text=HISTORY_TEXT[self.prefs.get('language','fr')]
        reasons=[]
        if out is getattr(self,'current',None):reasons.append(text['main_view'])
        reasons.extend(f'Slot {slot}' for slot in slots)
        if any(value is out for value in self._manual_history_locks):reasons.append(text['manual_lock'])
        if reasons and not messagebox.askyesno(text['title'],text['delete_assigned'].format(reasons=', '.join(reasons)),parent=self._history_window):return
        for slot in slots:
            self._compare_slots[slot]=None
            if self._compare_active==slot:self._compare_active=None
        self._manual_history_locks=[value for value in self._manual_history_locks if value is not out];self.session_cache.remove(key);self._refresh_compare_label();self._refresh_history(preferred_index=index);self._feedback_key=None;self._status_kind='info';self.status.set(text['deleted']);self._sync_status_display();self._refresh_state_indicators()

    def _history_center_clear(self):
        self._clear_history(confirm=True,parent=self._history_window)

    def _retranslate_history_center(self):
        if self._history_window is None:return
        text=HISTORY_TEXT[self.prefs.get('language','fr')];self._history_window.title(text['title']);tree=self._history_tree
        tree.heading('#0',text='',image=self._history_heading_lock_icon,anchor='center');tree.heading('rank',text='#');
        for key in ('origin','map','details'):tree.heading(key,text=text[key])
        self._history_window_widgets['preview_host'].configure(text=text['preview'])
        for key,label in (('show','show'),('a','set_a'),('b','set_b'),('delete','delete'),('clear','clear'),('close','close')):self._history_window_widgets['buttons'][key].configure(text=text[label])
        self._refresh_history_center()

    def _apply_history_window_theme(self):
        if self._history_window is None:return
        try:
            colors=self._ui_theme_colors;self._history_window.configure(background=colors.get('window','#202124'))
            self._history_tree.tag_configure('even',background=colors.get('surface','#303134'),foreground=colors.get('text','#e8eaed'))
            self._history_tree.tag_configure('odd',background=colors.get('surface_alt','#34363a'),foreground=colors.get('text','#e8eaed'))
            self._history_preview_label.configure(background=colors.get('panel','#292a2d'),foreground=colors.get('text','#e8eaed'))
            host=self._history_window_widgets.get('preview_image_host')
            if host is not None:host.configure(background=colors.get('panel','#292a2d'))
        except tk.TclError:pass

    def _load_history(self):
        self._display_history_key(self._history_lookup.get(self.history_var.get()))

    def _clear_history(self,confirm=True,parent=None):
        text=HISTORY_TEXT[self.prefs.get('language','fr')];slots=[slot for slot,value in self._compare_slots.items() if value is not None];reasons=[]
        if self._output_in_history(getattr(self,'current',None)):reasons.append(text['main_view'])
        reasons.extend(f'Slot {slot}' for slot in slots)
        if self._manual_history_locks:reasons.append(text['manual_lock'])
        prompt=text['confirm_clear_protected'].format(reasons=', '.join(reasons)) if reasons else text['confirm_clear']
        if confirm and not messagebox.askyesno(text['title'],prompt,parent=parent or self):return
        self.session_cache.clear();self.session_stats_cache.clear();self._manual_history_locks=[];self._history_visual_order=[];self._history_lookup.clear();self.history_combo.configure(values=[]);self.history_var.set('')
        if slots:self._compare_slots={'A':None,'B':None};self._compare_active=None;self._refresh_compare_label()
        self._refresh_history_center();self._refresh_state_indicators();self._feedback('history_cleared','success')

    def _set_compare_slot(self,slot):
        if not self.current:return
        self._set_compare_output(slot,self.current)

    def _set_compare_output(self,slot,out):
        if out is None:return 'ignored',None
        if self._compare_slots.get(slot) is out:
            self._compare_active=slot;self._refresh_compare_label();getattr(self,'_refresh_history_preview',lambda:None)();lang=self.prefs.get('language','fr')
            self._feedback_key=None;self._status_kind='info';self.status.set(_lang_text(lang,f'Cette carte est déjà affectée à {slot}.',f'This map is already assigned to {slot}.',f'Diese Karte ist bereits {slot} zugewiesen.',f'Este mapa ya está asignado a {slot}.'));getattr(self,'_sync_status_display',lambda:None)();return 'already',None
        other='B' if slot=='A' else 'A';moved=self._compare_slots.get(other) is out
        if moved:self._compare_slots[other]=None
        need_stats=self.session_stats_cache.get(out.state) is None
        if need_stats:self._task_begin(_lang_text(self.prefs.get('language','fr'),f'Préparation comparaison {slot}…',f'Preparing comparison {slot}…',f'Vergleich {slot} wird vorbereitet…',f'Preparando comparación {slot}…'),10)
        self._compare_slots[slot]=out;self._compare_active=slot;self._stats_for_output(out);self._refresh_compare_label();self._refresh_stats_chart()
        lang=self.prefs.get('language','fr');message=(_lang_text(lang,f'Carte déplacée de {other} vers {slot}.',f'Map moved from {other} to {slot}.',f'Karte von {other} nach {slot} verschoben.',f'Mapa movido de {other} a {slot}.') if moved else _lang_text(lang,f'Comparaison {slot} prête.',f'Comparison {slot} ready.',f'Vergleich {slot} ist bereit.',f'Comparación {slot} lista.'))
        getattr(self,'_refresh_history_preview',lambda:None)()
        if need_stats:self._task_done(message)
        else:self._feedback_key=None;self._status_kind='success';self.status.set(message);getattr(self,'_sync_status_display',lambda:None)()
        return ('moved' if moved else 'assigned'),(other if moved else None)

    def _output_label(self,out):
        if out is None:return '—'
        m=out.state.metadata;return f"{m.get('seed','import')}/{m.get('mode_key',m.get('mode','?'))}/{len(out.state.starts) or m.get('players',0)}P"

    def _refresh_compare_buttons(self):
        lang=self.prefs.get('language','fr')
        for slot,button in (('A',getattr(self,'compare_a_button',None)),('B',getattr(self,'compare_b_button',None))):
            if button is None:continue
            out=self._compare_slots.get(slot)
            if out is None:
                button.configure(text=_lang_text(lang,f'Définir {slot}',f'Set {slot}',f'{slot} festlegen',f'Definir {slot}'),image=self._compare_led_off)
            else:
                button.configure(text=f"{slot} · {self._output_label(out)}",image=self._compare_led_on)
        for slot,button in (('A',getattr(self,'clear_a_button',None)),('B',getattr(self,'clear_b_button',None))):
            if button is not None:
                active=self._compare_slots.get(slot) is not None
                button.configure(state='normal' if active else 'disabled',image=self._delete_icon_on if active else self._delete_icon_off)
        both=getattr(self,'clear_ab_button',None)
        if both is not None:both.configure(state='normal' if any(self._compare_slots.values()) else 'disabled')
        # Slot identity text changes the natural button width.  Re-evaluate the
        # local Session layout after Tk has recomputed the requested dimensions.
        self._session_layout_mode=None
        try:self.after_idle(self._apply_session_layout)
        except tk.TclError:pass
        self._refresh_batch_assignment_buttons()

    def _output_in_history(self,out):
        return out is not None and any(value is out for _,value in self.session_cache.entries())

    def _history_residency_hint(self):
        current=getattr(self,'current',None)
        if current is None or self._output_in_history(current):return
        text=HISTORY_TEXT[self.prefs.get('language','fr')]['outside_history'];self._feedback_key=None;self._status_kind='warning';self.status.set(text);self._sync_status_display()

    def _history_residency_tooltip(self):
        current=getattr(self,'current',None)
        if current is None or self._output_in_history(current):return
        self._show_ui_tooltip(self.history_residency_label,_CONTEXT_TEXT[self.prefs.get('language','fr')]['outside_tip'],key='outside-history')

    def _localized_source(self,source):
        lang=self.prefs.get('language','fr')
        return source if lang=='fr' else TEXTS.get(source,{}).get(lang,TEXTS.get(source,{}).get('en',source))

    def _refresh_state_indicators(self):
        current=getattr(self,'current',None)
        selected_key=self._history_lookup.get(self.history_var.get()) if hasattr(self,'history_var') else None
        selected_out=self.session_cache.peek(selected_key) if selected_key is not None else None
        load=getattr(self,'history_load_button',None)
        if load is not None:
            active=selected_out is not None and selected_out is current
            try:load.configure(text=_CONTEXT_TEXT[self.prefs.get('language','fr')]['loaded'] if active else self._localized_source('Charger'),image=self._compare_led_on if active else self._compare_led_off,compound='left')
            except tk.TclError:pass
        residency=getattr(self,'history_residency_label',None)
        if residency is not None:
            try:residency.configure(image=self._history_outside_icon if current is not None and not self._output_in_history(current) else '')
            except tk.TclError:pass
        key=self._history_selected_key();out=self.session_cache.peek(key) if key is not None else None
        buttons=self._history_window_widgets.get('buttons',{})
        states={'show':out is not None and out is current,'a':out is not None and self._compare_slots.get('A') is out,'b':out is not None and self._compare_slots.get('B') is out}
        for name,active in states.items():
            button=buttons.get(name)
            if button is not None:
                text=HISTORY_TEXT[self.prefs.get('language','fr')];label=(_CONTEXT_TEXT[self.prefs.get('language','fr')][{'show':'shown','a':'assigned_a','b':'assigned_b'}[name]] if active else text[{'show':'show','a':'set_a','b':'set_b'}[name]])
                try:button.configure(text=label,image=self._compare_led_on if active else self._compare_led_off,compound='left')
                except tk.TclError:pass
        lock_button=buttons.get('lock');manually_locked=out is not None and any(value is out for value in self._manual_history_locks)
        if lock_button is not None:
            text=HISTORY_TEXT[self.prefs.get('language','fr')]
            try:lock_button.configure(text=text['unlock' if manually_locked else 'lock'],image=self._lock_open_icon if manually_locked else self._lock_closed_icon,compound='left')
            except tk.TclError:pass
        for iid,entry_key in self._history_center_lookup.items():
            entry=self.session_cache.peek(entry_key);roles=self._history_roles_for_output(entry)
            try:self._history_tree.item(iid,image=self._history_role_image(roles))
            except (tk.TclError,AttributeError):pass
        self._refresh_batch_assignment_buttons()

    def _refresh_compare_label(self):
        # Compatibility helper kept for existing callers; identity is now shown only on the LED buttons.
        self._refresh_compare_buttons();self._refresh_stats_chart();self._refresh_state_indicators()

    def _clear_compare_slot(self,slot):
        if slot not in self._compare_slots:return
        self._compare_slots[slot]=None
        if self._compare_active==slot:self._compare_active=None
        self._refresh_compare_label();getattr(self,'_refresh_history_preview',lambda:None)()
        lang=self.prefs.get('language','fr')
        self._feedback_key=None;self._status_kind='success';self.status.set(_lang_text(lang,f'Comparaison {slot} vidée',f'Comparison {slot} cleared',f'Vergleich {slot} geleert',f'Comparación {slot} vaciada'));getattr(self,'_sync_status_display',lambda:None)()

    def _clear_compare_slots(self):
        self._compare_slots={'A':None,'B':None};self._compare_active=None
        self._refresh_compare_label();getattr(self,'_refresh_history_preview',lambda:None)()
        self._feedback_key=None;self._status_kind='success';self.status.set(_lang_text(self.prefs.get('language','fr'),'Comparaisons A/B vidées','A/B comparisons cleared','A/B-Vergleiche geleert','Comparaciones A/B vaciadas'));getattr(self,'_sync_status_display',lambda:None)()

    def _toggle_compare(self):
        a,b=self._compare_slots['A'],self._compare_slots['B']
        if a is None or b is None:
            self._feedback_key=None;self._status_kind='warning';self.status.set(_lang_text(self.prefs.get('language','fr'),'Définissez A et B avant la bascule.','Set both A and B before toggling.','Legen Sie vor dem Wechsel A und B fest.','Define A y B antes de alternar.'));getattr(self,'_sync_status_display',lambda:None)();return
        self._compare_active='B' if self._compare_active!='B' else 'A';self.current=self._compare_slots[self._compare_active];imported=bool(self.current.state.metadata.get('source_format'));self._populate_current(imported=imported);self._invalidate_preview();self._refresh_preview(False);self._feedback('compare_toggled','info',map=f'{self._compare_active} · {self._output_label(self.current)}')
