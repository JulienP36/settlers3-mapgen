"""Map and statistics export-center coordination for the main window."""

from __future__ import annotations

import shutil
import traceback
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from ...map_data.binary import export_with_scaffold
from ..analysis.charts import render_stats_chart
from ..analysis.core import stats_csv, stats_json
from ..paths import EDM_SCAFFOLD, MAP_SCAFFOLD, OUTPUT
from ..rendering.preview import render
from ..ui.i18n.common import _lang_text
from ..ui.i18n.exports import EXPORT_TEXT
from ..ui.i18n.shell import FEEDBACK_TEXT
from .planning import (
    existing_export_paths,
    map_export_capabilities,
    map_export_paths,
    safe_export_basename,
    stats_export_paths,
)


class ExportController:
    """Host contract: current map, render/analysis helpers and task feedback."""
    def _default_export_basename(self,stats=False):
        source=self._current_source_path()
        if source:return safe_export_basename(source.stem+('_stats' if stats else ''))
        st=self.current.state;m=st.metadata
        base=f"S3_{m.get('archetype','Imported')}_{m.get('mode','Map')}_{len(st.starts) or m.get('players',0)}P_{st.side}x{st.side}_seed_{m.get('seed','import')}_MapGenV1_8"
        return safe_export_basename(base+('_stats' if stats else ''))

    def _current_source_path(self):
        if not self.current:return None
        metadata=self.current.state.metadata;value=metadata.get('source_path')
        if value:
            path=Path(value)
            if path.is_file():return path
        source=getattr(self,'import_source',None)
        return Path(source) if source and Path(source).is_file() and metadata.get('source_format') else None

    def _choose_export_folder(self,var,parent):
        chosen=filedialog.askdirectory(parent=parent,title=EXPORT_TEXT[self.prefs.get('language','fr')]['folder'],initialdir=var.get() or str(OUTPUT))
        if chosen:var.set(chosen)

    def _confirm_export_conflicts(self,paths,parent,text):
        conflicts=existing_export_paths(paths)
        if not conflicts:return True
        names='\n'.join(f'• {p.name}' for p in conflicts)
        return messagebox.askyesno(text['overwrite_title'],text['overwrite'].format(files=names),parent=parent)

    def _close_export_center(self,attribute):
        window=getattr(self,attribute,None)
        if window is not None:
            try:window.grab_release();window.destroy()
            except tk.TclError:pass
        setattr(self,attribute,None)
        try:
            if self.tk.call('tk','windowingsystem')=='win32':self.attributes('-disabled',False)
            self.focus_force()
        except tk.TclError:pass

    def _activate_export_modal(self,window):
        window.grab_set()
        try:
            if self.tk.call('tk','windowingsystem')=='win32':self.attributes('-disabled',True)
        except tk.TclError:pass
        window.focus_force()

    def _place_export_center(self,window):
        window.update_idletasks();width=window.winfo_reqwidth();height=window.winfo_reqheight()+16;screen_w=window.winfo_screenwidth();screen_h=window.winfo_screenheight()
        x=max(0,min(self.winfo_rootx()+80,screen_w-width));y=max(0,min(self.winfo_rooty()+80,screen_h-height));window.geometry(f'{width}x{height}+{x}+{y}')

    def _open_stats_export_center(self):
        if not self.current:return
        existing=self._stats_export_window
        if existing is not None:
            try:existing.deiconify();existing.lift();existing.focus_force();return
            except tk.TclError:self._stats_export_window=None
        lang=self.prefs.get('language','fr');text=EXPORT_TEXT[lang];w=tk.Toplevel(self);self._stats_export_window=w;w.title(text['stats_title']);w.transient(self);w.resizable(True,False);w.protocol('WM_DELETE_WINDOW',lambda:self._close_export_center('_stats_export_window'))
        w.configure(background=self._ui_theme_colors.get('panel','#292a2d'));w.rowconfigure(0,weight=1)
        body=ttk.Frame(w,padding=14);body.grid(sticky='nsew');body.columnconfigure(1,weight=1);w.columnconfigure(0,weight=1)
        folder=tk.StringVar(value=str(OUTPUT));basename=tk.StringVar(value=self._default_export_basename(True));formats={key:tk.BooleanVar(value=True) for key in ('json','csv','png')}
        ttk.Label(body,text=text['folder']).grid(row=0,column=0,sticky='w',pady=4);ttk.Entry(body,textvariable=folder,width=54).grid(row=0,column=1,sticky='ew',padx=8);ttk.Button(body,text=text['browse'],command=lambda:self._choose_export_folder(folder,w)).grid(row=0,column=2)
        ttk.Label(body,text=text['basename']).grid(row=1,column=0,sticky='w',pady=4);ttk.Entry(body,textvariable=basename).grid(row=1,column=1,columnspan=2,sticky='ew',padx=(8,0));ttk.Label(body,text=text['safe_name'],style='Hint.TLabel').grid(row=2,column=1,columnspan=2,sticky='w',padx=(8,0))
        box=ttk.LabelFrame(body,text=text['formats'],padding=8);box.grid(row=3,column=0,columnspan=3,sticky='ew',pady=(12,8))
        for col,key in enumerate(('json','csv','png')):ttk.Checkbutton(box,text=text[key],variable=formats[key]).grid(row=0,column=col,sticky='w',padx=(0 if col==0 else 14,0))
        summary=tk.StringVar();ttk.Label(body,text=text['files']).grid(row=4,column=0,sticky='nw');ttk.Label(body,textvariable=summary,justify='left',wraplength=520).grid(row=4,column=1,columnspan=2,sticky='w',padx=(8,0))
        actions=ttk.Frame(body);actions.grid(row=5,column=0,columnspan=3,sticky='e',pady=(14,0));ttk.Button(actions,text=text['cancel'],command=lambda:self._close_export_center('_stats_export_window')).pack(side='left',padx=(0,6));export_button=ttk.Button(actions,text=text['export']);export_button.pack(side='left')
        def planned():
            try:return stats_export_paths(Path(folder.get()),basename.get(),[key for key,var in formats.items() if var.get()])
            except ValueError:return {}
        def refresh(*_):
            paths=planned();summary.set('\n'.join(path.name for path in paths.values()) if paths else text['none']);export_button.configure(state='normal' if paths else 'disabled')
        def perform():
            paths=planned()
            if not paths:return messagebox.showwarning(text['stats_title'],text['none'],parent=w)
            target=Path(folder.get())
            if not str(folder.get()).strip():return messagebox.showerror(text['stats_title'],text['invalid_folder'],parent=w)
            if not self._confirm_export_conflicts(paths,w,text):return
            try:
                target.mkdir(parents=True,exist_ok=True);stats=self._ensure_stats_cache()
                if 'json' in paths:paths['json'].write_text(stats_json(stats),encoding='utf-8')
                if 'csv' in paths:paths['csv'].write_text(stats_csv(stats),encoding='utf-8-sig')
                if 'png' in paths:
                    width=max(900,int(self.stats_chart_canvas.winfo_width()));height=max(520,int(self.stats_chart_canvas.winfo_height()))
                    render_stats_chart(stats,self._stats_chart_key(),lang=lang,dark=self.prefs.get('theme','dark')=='dark',width=width,height=height,compare_stats=self._compare_stats_pair()).save(paths['png'])
                names='\n'.join(path.name for path in paths.values());self._close_export_center('_stats_export_window');self._feedback('graph_exported','success',format='/'.join(key.upper() for key in paths),file=target.name);messagebox.showinfo(text['stats_title'],text['done'].format(files=names),parent=self)
            except Exception as error:messagebox.showerror(text['stats_title'],str(error),parent=w)
        export_button.configure(command=perform)
        for var in (folder,basename,*formats.values()):var.trace_add('write',refresh)
        refresh();self._place_export_center(w);self._activate_export_modal(w)

    def export(self):
        self._open_map_export_center()

    def save_preview(self):
        if not self.current:return
        path=filedialog.asksaveasfilename(defaultextension='.png',filetypes=[('PNG','*.png')])
        if not path:return
        try:self._task_begin('Export de l’aperçu…',20);render(self.current.state,path,**self._render_options());self._task_done('Aperçu PNG enregistré')
        except Exception as e:self._task_error('Erreur aperçu');messagebox.showerror('Aperçu PNG',f'{e}\n\n{traceback.format_exc()}')

    def _open_map_export_center(self):
        if not self.current:return
        existing=self._map_export_window
        if existing is not None:
            try:existing.deiconify();existing.lift();existing.focus_force();return
            except tk.TclError:self._map_export_window=None
        lang=self.prefs.get('language','fr');text=EXPORT_TEXT[lang];state=self.current.state;source_path=self._current_source_path();capabilities=map_export_capabilities(state.side,source_path);capabilities['png_current']=self._view_key()!='global'
        w=tk.Toplevel(self);self._map_export_window=w;w.title(text['map_title']);w.transient(self);w.resizable(True,False);w.protocol('WM_DELETE_WINDOW',lambda:self._close_export_center('_map_export_window'))
        w.configure(background=self._ui_theme_colors.get('panel','#292a2d'));w.rowconfigure(0,weight=1)
        body=ttk.Frame(w,padding=14);body.grid(sticky='nsew');body.columnconfigure(1,weight=1);w.columnconfigure(0,weight=1)
        folder=tk.StringVar(value=str(OUTPUT));basename=tk.StringVar(value=self._default_export_basename(False))
        preferred_png='png_global' if self._view_key()=='global' else 'png_current'
        formats={key:tk.BooleanVar(value=(capabilities[key] and (key in ('edm','map','sav') or key==preferred_png))) for key in capabilities}
        ttk.Label(body,text=text['folder']).grid(row=0,column=0,sticky='w',pady=4);ttk.Entry(body,textvariable=folder,width=58).grid(row=0,column=1,sticky='ew',padx=8);ttk.Button(body,text=text['browse'],command=lambda:self._choose_export_folder(folder,w)).grid(row=0,column=2)
        ttk.Label(body,text=text['basename']).grid(row=1,column=0,sticky='w',pady=4);ttk.Entry(body,textvariable=basename).grid(row=1,column=1,columnspan=2,sticky='ew',padx=(8,0));ttk.Label(body,text=text['safe_name'],style='Hint.TLabel').grid(row=2,column=1,columnspan=2,sticky='w',padx=(8,0))
        box=ttk.LabelFrame(body,text=text['formats'],padding=8);box.grid(row=3,column=0,columnspan=3,sticky='ew',pady=(12,6));box.columnconfigure(0,weight=1);box.columnconfigure(1,weight=1)
        order=('edm','map','sav','png_global','png_current')
        for index,key in enumerate(order):
            check=ttk.Checkbutton(box,text=text[key],variable=formats[key]);check.grid(row=index//2,column=index%2,sticky='w',padx=(0 if index%2==0 else 14,0),pady=2)
            if not capabilities[key]:check.configure(state='disabled',style='Unavailable.TCheckbutton')
        hints=[]
        if not capabilities['edm']:hints.append(text['binary_unavailable'])
        if not capabilities['sav']:hints.append(text['sav_unavailable'])
        else:hints.append(text['sav_exact'])
        if not capabilities['png_current']:hints.append(text['current_unavailable'])
        ttk.Label(body,text='\n'.join(hints),style='Hint.TLabel',justify='left',wraplength=620).grid(row=4,column=0,columnspan=3,sticky='w',pady=(2,8))
        summary=tk.StringVar();ttk.Label(body,text=text['files']).grid(row=5,column=0,sticky='nw');ttk.Label(body,textvariable=summary,justify='left',wraplength=540).grid(row=5,column=1,columnspan=2,sticky='w',padx=(8,0))
        actions=ttk.Frame(body);actions.grid(row=6,column=0,columnspan=3,sticky='e',pady=(14,0));ttk.Button(actions,text=text['cancel'],command=lambda:self._close_export_center('_map_export_window')).pack(side='left',padx=(0,6));export_button=ttk.Button(actions,text=text['export']);export_button.pack(side='left')
        def planned():
            try:return map_export_paths(Path(folder.get()),basename.get(),[key for key,var in formats.items() if var.get() and capabilities[key]])
            except ValueError:return {}
        def refresh(*_):
            paths=planned();summary.set('\n'.join(path.name for path in paths.values()) if paths else text['none']);export_button.configure(state='normal' if paths else 'disabled')
        def perform():
            paths=planned()
            if not paths:return messagebox.showwarning(text['map_title'],text['none'],parent=w)
            target=Path(folder.get())
            if not str(folder.get()).strip():return messagebox.showerror(text['map_title'],text['invalid_folder'],parent=w)
            if not self._confirm_export_conflicts(paths,w,text):return
            self._close_export_center('_map_export_window')
            try:
                target.mkdir(parents=True,exist_ok=True);self._task_begin(text['map_title']+'…',5);total=len(paths);done=0
                if 'edm' in paths:export_with_scaffold(state,EDM_SCAFFOLD,paths['edm']);done+=1;self._task_progress(5+85*done/total,paths['edm'].name)
                if 'map' in paths:export_with_scaffold(state,MAP_SCAFFOLD,paths['map']);done+=1;self._task_progress(5+85*done/total,paths['map'].name)
                if 'sav' in paths:
                    if source_path.resolve()!=paths['sav'].resolve():shutil.copy2(source_path,paths['sav'])
                    done+=1;self._task_progress(5+85*done/total,paths['sav'].name)
                projection=self.prefs.get('projection','square')
                if 'png_global' in paths:render(state,paths['png_global'],labels=False,view='global',overlay_alpha=100,projection=projection);done+=1;self._task_progress(5+85*done/total,paths['png_global'].name)
                if 'png_current' in paths:render(state,paths['png_current'],labels=True,**self._render_options());done+=1;self._task_progress(5+85*done/total,paths['png_current'].name)
                names='\n'.join(path.name for path in paths.values());self._task_done(FEEDBACK_TEXT[lang]['export_done']);messagebox.showinfo(text['map_title'],text['done'].format(files=names),parent=self)
            except Exception as error:self._task_error(_lang_text(lang,'Erreur export','Export error','Exportfehler','Error de exportación'));messagebox.showerror(text['map_title'],str(error),parent=self)
        export_button.configure(command=perform)
        for var in (folder,basename,*formats.values()):var.trace_add('write',refresh)
        refresh();self._place_export_center(w);self._activate_export_modal(w)
