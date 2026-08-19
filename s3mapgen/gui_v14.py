from __future__ import annotations
import json, traceback, shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from .gui import App as BaseApp, VIEWS, NATIVE_LIMITS
from .preview import render
from .preferences import load_settings, save_settings
from .binary import export_with_scaffold, read_area, read_starts, read_sav_state
from .engine import GenerationOutput
from .app_paths import EDM_SCAFFOLD, MAP_SCAFFOLD

PROJECTIONS={'Carrée':'square','Parallélogramme':'parallelogram'}
THEMES={'Sombre':'dark','Clair':'light'}


class App(BaseApp):
    def __init__(self):
        self.prefs=load_settings();self._preview_base=None;self._preview_key=None
        self._zoom_after=None;self._progress_after=None
        super().__init__()
        self.title('Settlers III MapGen v1.4 candidate')
        self._apply_theme();self._update_view_controls()

    def _build(self):
        super()._build()
        self.progress.grid_remove()
        self.canvas.configure(cursor='fleur')
        self.canvas.bind('<ButtonPress-1>',self._pan_start)
        self.canvas.bind('<B1-Motion>',self._pan_move)
        self.canvas.bind('<Button-4>',lambda e:self._linux_zoom(1))
        self.canvas.bind('<Button-5>',lambda e:self._linux_zoom(-1))
        self._settings_tab()
        self._bind_scale_jump(self.zoom_scale,self.zoom_var,.5,4.0,self._zoom_changed)
        self._bind_scale_jump(self.opacity_scale,self.opacity_var,0,100,self._opacity_changed)
        self._bind_scale_jump(self.wheel_scale,self.wheel_var,1.04,1.20,self._wheel_changed)

    def _settings_tab(self):
        f=ttk.Frame(self.nb,padding=14);self.nb.add(f,text='Paramètres');f.columnconfigure(1,weight=1)
        ttk.Label(f,text='Affichage',style='Section.TLabel').grid(row=0,column=0,columnspan=3,sticky='w',pady=(0,10))
        ttk.Label(f,text='Thème').grid(row=1,column=0,sticky='w',pady=6)
        self.theme_var=tk.StringVar(value=next(k for k,v in THEMES.items() if v==self.prefs['theme']))
        c=ttk.Combobox(f,textvariable=self.theme_var,values=list(THEMES),state='readonly');c.grid(row=1,column=1,sticky='ew');c.bind('<<ComboboxSelected>>',lambda e:self._theme_changed())
        ttk.Label(f,text='Opacité couche').grid(row=2,column=0,sticky='w',pady=(14,6))
        self.opacity_var=tk.DoubleVar(value=float(self.prefs['overlay_alpha']))
        self.opacity_scale=ttk.Scale(f,from_=0,to=100,variable=self.opacity_var,command=lambda v:self._opacity_changed());self.opacity_scale.grid(row=2,column=1,sticky='ew')
        self.opacity_label=ttk.Label(f,text=f"{int(self.opacity_var.get())} %",width=7);self.opacity_label.grid(row=2,column=2,padx=(8,0))
        ttk.Label(f,text='0 % = map globale · 100 % = couche seule',style='Hint.TLabel').grid(row=3,column=1,columnspan=2,sticky='w')
        ttk.Label(f,text='Projection').grid(row=4,column=0,sticky='w',pady=(14,6))
        self.projection_var=tk.StringVar(value=next(k for k,v in PROJECTIONS.items() if v==self.prefs['projection']))
        c=ttk.Combobox(f,textvariable=self.projection_var,values=list(PROJECTIONS),state='readonly');c.grid(row=4,column=1,sticky='ew');c.bind('<<ComboboxSelected>>',lambda e:self._projection_changed())
        ttk.Label(f,text='Le parallélogramme modifie uniquement le rendu, jamais les données.',style='Hint.TLabel',wraplength=360).grid(row=5,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Sensibilité molette').grid(row=6,column=0,sticky='w',pady=(14,6))
        self.wheel_var=tk.DoubleVar(value=float(self.prefs['wheel_zoom']))
        self.wheel_scale=ttk.Scale(f,from_=1.04,to=1.20,variable=self.wheel_var,command=lambda v:self._wheel_changed());self.wheel_scale.grid(row=6,column=1,sticky='ew')
        self.wheel_label=ttk.Label(f,text=f"×{self.wheel_var.get():.2f}",width=7);self.wheel_label.grid(row=6,column=2,padx=(8,0))
        ttk.Separator(f).grid(row=7,column=0,columnspan=3,sticky='ew',pady=16)
        ttk.Label(f,text='Navigation',style='Section.TLabel').grid(row=8,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.',style='Hint.TLabel',justify='left').grid(row=9,column=0,columnspan=3,sticky='w',pady=(6,0))

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

    def _apply_theme(self):
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
        s.configure('TCombobox',fieldbackground=field,background=field,foreground=fg,selectbackground=field,selectforeground=fg)
        self.option_add('*TCombobox*Listbox.background',field)
        self.option_add('*TCombobox*Listbox.foreground',fg)
        self.option_add('*TCombobox*Listbox.selectBackground',panel)
        self.option_add('*TCombobox*Listbox.selectForeground',fg)
        s.configure('TSpinbox',fieldbackground=field,foreground=fg);s.configure('TEntry',fieldbackground=field,foreground=fg)
        trough='#3c4043' if dark else '#dddddd';s.configure('Running.Horizontal.TProgressbar',troughcolor=trough,background='#35a853');s.configure('Done.Horizontal.TProgressbar',troughcolor=trough,background='#4285f4');s.configure('Error.Horizontal.TProgressbar',troughcolor=trough,background='#d93025')
        for w in (self.validation,self.pipeline,self.meta,self.stats):w.configure(bg=textbg,fg=fg,insertbackground=fg,selectbackground='#4f6480' if dark else '#b8d2ff')
        self.canvas.configure(bg=canvas)

    def _save_prefs(self):
        save_settings({'theme':self.prefs['theme'],'overlay_alpha':int(self.opacity_var.get()),'projection':self.prefs['projection'],'wheel_zoom':float(self.wheel_var.get())})
    def _theme_changed(self):self.prefs['theme']=THEMES[self.theme_var.get()];self._save_prefs();self._apply_theme()
    def _opacity_changed(self):self.opacity_label.configure(text=f'{int(self.opacity_var.get())} %');self.prefs['overlay_alpha']=int(self.opacity_var.get());self._save_prefs();self._invalidate_preview();self._schedule_preview()
    def _projection_changed(self):self.prefs['projection']=PROJECTIONS[self.projection_var.get()];self._save_prefs();self._invalidate_preview();self._refresh_preview(True)
    def _wheel_changed(self):self.wheel_label.configure(text=f'×{self.wheel_var.get():.2f}');self.prefs['wheel_zoom']=float(self.wheel_var.get());self._save_prefs()
    def _update_view_controls(self):
        if hasattr(self,'opacity_scale'):self.opacity_scale.configure(state='disabled' if VIEWS[self.view.get()]=='global' else 'normal')

    def _task_begin(self,label,value=5):
        if self._progress_after:
            try:self.after_cancel(self._progress_after)
            except Exception:pass
        self.progress.configure(style='Running.Horizontal.TProgressbar',maximum=100);self.progress['value']=value;self.progress.grid();self.status.set(label);self.update_idletasks()
    def _task_progress(self,value,label=None):
        self.progress.configure(style='Running.Horizontal.TProgressbar');self.progress['value']=max(0,min(99,value))
        if label:self.status.set(label)
        self.update_idletasks()
    def _task_done(self,label=None):
        self.progress.configure(style='Done.Horizontal.TProgressbar');self.progress['value']=100
        if label:self.status.set(label)
        self.update_idletasks();self._progress_after=self.after(1400,self.progress.grid_remove)
    def _task_error(self,label='Erreur'):
        self.progress.configure(style='Error.Horizontal.TProgressbar');self.progress['value']=100;self.status.set(label);self.update_idletasks();self._progress_after=self.after(2500,self.progress.grid_remove)
    def _progress_stage(self,stage,detail,index):self._task_progress(min(95,5+index*4),f'{stage} {detail}')

    def generate(self):
        try:
            side=int(self.size.get())
            if side!=768:raise NotImplementedError(f'La génération {side}×{side} est réservée mais pas encore calibrée. Max joueurs={NATIVE_LIMITS[side]}.')
            self._task_begin('Génération…',2);self.import_source=None
            self.current=self.generator.generate(int(self.players.get()),int(self.seed.get()),mode=self._mode_key(),archetype=self._arch_key())
            self._task_progress(97,'Finalisation de l’aperçu…');self._populate_current();self._invalidate_preview();self._refresh_preview(True);self._task_done(self.status.get())
        except Exception as e:self._task_error();messagebox.showerror('MapGen',f'{e}\n\n{traceback.format_exc()}')

    def import_file(self):
        path=filedialog.askopenfilename(title='Importer une map',filetypes=[('Settlers III','*.edm *.map *.sav'),('EDM','*.edm'),('MAP','*.map'),('SAV','*.sav'),('Tous','*.*')])
        if not path:return
        try:
            p=Path(path);ext=p.suffix.lower();self._task_begin(f'Import {p.name}…',8)
            if ext=='.sav':state=read_sav_state(p)
            elif ext in ('.edm','.map'):
                state=read_area(p);state.starts=read_starts(p);state.metadata.update({'source_format':ext[1:].upper(),'source_path':str(p),'territories_available':False})
            else:raise ValueError('Extension non supportée')
            self._task_progress(80,'Calcul des statistiques…');self.import_source=p;self.current=GenerationOutput(state,[],[f'import.{ext[1:]} — {p.name}']);self._populate_current(True);self._invalidate_preview();self._task_progress(92,'Construction de l’aperçu…');self._refresh_preview(True);self._task_done(f'Importé — {p.name} — {state.side}×{state.side}')
        except Exception as e:self._task_error('Erreur import');messagebox.showerror('Import',f'{e}\n\n{traceback.format_exc()}')

    def _invalidate_preview(self):self._preview_base=None;self._preview_key=None
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

    def _refresh_preview(self,reset_pan=False):
        self._zoom_after=None
        if not self.current:return
        self._update_view_controls();view=VIEWS[self.view.get()];alpha=100 if view=='global' else int(self.opacity_var.get());proj=self.prefs['projection']
        key=(id(self.current.state),view,alpha,proj)
        if key!=self._preview_key:self._preview_base=render(self.current.state,labels=True,view=view,overlay_alpha=alpha,projection=proj);self._preview_key=key
        im=self._preview_base;cw=max(100,self.canvas.winfo_width());ch=max(100,self.canvas.winfo_height());factor=max(.05,min((cw-10)/im.width,(ch-10)/im.height)*self.zoom);new=(max(1,int(im.width*factor)),max(1,int(im.height*factor)))
        oldx=0 if reset_pan else self.canvas.xview()[0];oldy=0 if reset_pan else self.canvas.yview()[0]
        shown=im.resize(new,Image.Resampling.NEAREST);self.photo=ImageTk.PhotoImage(shown);self.canvas.delete('all');sw=max(cw,new[0]);sh=max(ch,new[1]);x=max(0,(cw-new[0])//2);y=max(0,(ch-new[1])//2);self.canvas.create_image(x,y,image=self.photo,anchor='nw');self.canvas.configure(scrollregion=(0,0,sw,sh));self.canvas.xview_moveto(oldx);self.canvas.yview_moveto(oldy)

    def _render_options(self):
        view=VIEWS[self.view.get()];return {'view':view,'overlay_alpha':100 if view=='global' else int(self.opacity_var.get()),'projection':self.prefs['projection']}

    def export(self):
        if not self.current:return
        folder=filedialog.askdirectory(title='Dossier de sortie')
        if not folder:return
        try:
            folder=Path(folder);st=self.current.state;side=st.side;self._task_begin('Export…',5);base=f"S3_{st.metadata.get('archetype','Imported')}_{st.metadata.get('mode','Map')}_{len(st.starts) or st.metadata.get('players',0)}P_{side}x{side}_seed_{st.metadata.get('seed','import')}_MapGenV1_4".replace(' ','');made=[]
            if side==768:
                edm=folder/(base+'.edm');mp=folder/('1-'+base+'.map');export_with_scaffold(st,EDM_SCAFFOLD,edm);self._task_progress(35,'Export MAP…');export_with_scaffold(st,MAP_SCAFFOLD,mp);made += [edm.name,mp.name]
            else:made.append('EDM/MAP non réécrits : aucun scaffold validé pour cette taille.')
            self._task_progress(62,'Export SAV/aperçu…')
            if self.import_source and self.import_source.suffix.lower()=='.sav':sv=folder/(base+'.sav');shutil.copy2(self.import_source,sv);made.append(sv.name+' (copie SAV inchangée)')
            else:made.append('SAV non exporté : writer SAV volontairement non implémenté/validé.')
            png=folder/(base+'_preview.png');render(st,png,**self._render_options());made.append(png.name);self._task_done('Export terminé');messagebox.showinfo('Export','\n'.join(made))
        except Exception as e:self._task_error('Erreur export');messagebox.showerror('Export',f'{e}\n\n{traceback.format_exc()}')

    def save_preview(self):
        if not self.current:return
        path=filedialog.asksaveasfilename(defaultextension='.png',filetypes=[('PNG','*.png')])
        if not path:return
        try:self._task_begin('Export de l’aperçu…',20);render(self.current.state,path,**self._render_options());self._task_done('Aperçu PNG enregistré')
        except Exception as e:self._task_error('Erreur aperçu');messagebox.showerror('Aperçu PNG',f'{e}\n\n{traceback.format_exc()}')


def main():App().mainloop()