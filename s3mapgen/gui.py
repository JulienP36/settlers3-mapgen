from __future__ import annotations
import json, traceback, random, shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from PIL import Image, ImageTk
from .app_paths import LEGACY_PROFILE,UPGRADED_PROFILE,UPGRADED_REFERENCE,LIBRARY,EDM_SCAFFOLD,MAP_SCAFFOLD
from .engine import MapGenerator, GenerationOutput
from .preview import render
from .binary import export_with_scaffold, read_area, read_starts, read_sav_state
from .modes import MODES, MODE_ORDER
from .archetypes import ARCHETYPES, ARCHETYPE_ORDER
from .stats import format_stats

NATIVE_LIMITS={384:8,448:11,512:15,576:19,640:20,704:20,768:20}
VIEWS={'Global':'global','Heightmap':'heightmap','Ressources':'resources','Territoires':'territories'}

class App(tk.Tk):
    def __init__(self):
        super().__init__();self.title('Settlers III MapGen v1.3.1');self.geometry('1380x860');self.minsize(1080,720)
        self.generator=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_PROFILE,UPGRADED_REFERENCE,progress_callback=self._progress_stage)
        self.current=None;self.photo=None;self.import_source=None;self.zoom=1.0
        self._build();self._size_changed()

    def _build(self):
        top=ttk.Frame(self,padding=8);top.pack(fill='x')
        ttk.Label(top,text='Mode').grid(row=0,column=0,sticky='w');self.mode=tk.StringVar(value='Legacy');self.mode_combo=ttk.Combobox(top,textvariable=self.mode,values=[MODES[k].label for k in MODE_ORDER],state='readonly',width=12);self.mode_combo.grid(row=1,column=0,padx=(0,6));self.mode_combo.bind('<<ComboboxSelected>>',lambda e:self._selection_changed())
        ttk.Label(top,text='Archétype').grid(row=0,column=1,sticky='w');self.arch=tk.StringVar(value='Continental');self.arch_combo=ttk.Combobox(top,textvariable=self.arch,values=[ARCHETYPES[k].label for k in ARCHETYPE_ORDER],state='readonly',width=14);self.arch_combo.grid(row=1,column=1,padx=(0,6));self.arch_combo.bind('<<ComboboxSelected>>',lambda e:self._selection_changed())
        ttk.Label(top,text='Taille').grid(row=0,column=2,sticky='w');self.size=tk.StringVar(value='768');self.size_combo=ttk.Combobox(top,textvariable=self.size,values=[str(x) for x in NATIVE_LIMITS],state='readonly',width=7);self.size_combo.grid(row=1,column=2,padx=(0,6));self.size_combo.bind('<<ComboboxSelected>>',lambda e:self._size_changed())
        ttk.Label(top,text='Joueurs').grid(row=0,column=3,sticky='w');self.players=tk.IntVar(value=4);self.players_spin=ttk.Spinbox(top,from_=2,to=20,textvariable=self.players,width=6);self.players_spin.grid(row=1,column=3,padx=(0,6))
        ttk.Label(top,text='Seed').grid(row=0,column=4,sticky='w');self.seed=tk.StringVar(value='2026081901');ttk.Entry(top,textvariable=self.seed,width=14).grid(row=1,column=4,padx=(0,3));ttk.Button(top,text='🎲',width=3,command=self.random_seed).grid(row=1,column=5,padx=(0,6))
        ttk.Button(top,text='Générer',command=self.generate).grid(row=1,column=6,padx=3);ttk.Button(top,text='Importer…',command=self.import_file).grid(row=1,column=7,padx=3)
        self.export_btn=ttk.Button(top,text='Exporter…',command=self.export,state='disabled');self.export_btn.grid(row=1,column=8,padx=3)
        ttk.Button(top,text='Aperçu PNG',command=self.save_preview).grid(row=1,column=9,padx=3)

        ttk.Label(top,text='Vue').grid(row=0,column=10,sticky='w');self.view=tk.StringVar(value='Global');vc=ttk.Combobox(top,textvariable=self.view,values=list(VIEWS),state='readonly',width=12);vc.grid(row=1,column=10,padx=(8,3));vc.bind('<<ComboboxSelected>>',lambda e:self._refresh_preview())
        ttk.Label(top,text='Zoom').grid(row=0,column=11,sticky='w');self.zoom_var=tk.DoubleVar(value=1.0);zs=ttk.Scale(top,from_=0.5,to=4.0,variable=self.zoom_var,command=lambda v:self._zoom_changed());zs.grid(row=1,column=11,sticky='ew',padx=3);top.columnconfigure(11,weight=1)

        self.progress=ttk.Progressbar(top,mode='determinate',maximum=100);self.progress.grid(row=2,column=0,columnspan=12,sticky='ew',pady=(8,2))
        self.status=tk.StringVar(value='Prêt');ttk.Label(top,textvariable=self.status).grid(row=3,column=0,columnspan=12,sticky='w')

        pan=ttk.Panedwindow(self,orient='horizontal');pan.pack(fill='both',expand=True,padx=8,pady=(0,8))
        left=ttk.Frame(pan);right=ttk.Frame(pan);pan.add(left,weight=3);pan.add(right,weight=2)
        self.canvas=tk.Canvas(left,bg='#181818',highlightthickness=0);self.canvas.pack(fill='both',expand=True);self.canvas.bind('<Configure>',lambda e:self._refresh_preview());self.canvas.bind('<MouseWheel>',self._mouse_zoom)
        self.nb=ttk.Notebook(right);self.nb.pack(fill='both',expand=True)
        self.validation=self._text_tab('Validations');self.pipeline=self._text_tab('Pipeline');self.meta=self._text_tab('Métadonnées');self.stats=self._text_tab('Statistiques')

    def _text_tab(self,name):
        frame=ttk.Frame(self.nb);self.nb.add(frame,text=name);txt=tk.Text(frame,wrap='word',font=('Consolas',10));sb=ttk.Scrollbar(frame,orient='vertical',command=txt.yview);txt.configure(yscrollcommand=sb.set);txt.pack(side='left',fill='both',expand=True);sb.pack(side='right',fill='y');return txt

    def _mode_key(self):return next(k for k,v in MODES.items() if v.label==self.mode.get())
    def _arch_key(self):return next(k for k,v in ARCHETYPES.items() if v.label==self.arch.get())
    def random_seed(self):self.seed.set(str(random.randint(1,2_147_483_647)))
    def _size_changed(self):
        s=int(self.size.get());mx=NATIVE_LIMITS[s];self.players_spin.configure(to=mx)
        if self.players.get()>mx:self.players.set(mx)
        self._selection_changed()
    def _selection_changed(self):
        s=int(self.size.get());m=MODES[self._mode_key()];a=ARCHETYPES[self._arch_key()]
        if s!=768:self.status.set(f'{s}×{s}: max {NATIVE_LIMITS[s]} joueurs. Sélection prête, génération pas encore calibrée dans v1.3.')
        elif not m.implemented:self.status.set(f'{m.label} réservé, non implémenté.')
        elif not a.implemented:self.status.set(f'{a.label} réservé, non implémenté.')
        else:self.status.set(f'Prêt — {m.label} / {a.label} / {s}×{s}.')

    def _progress_stage(self,stage,detail,index):
        self.progress['value']=min(95,5+index*4);self.status.set(f'{stage} {detail}');self.update_idletasks()

    def generate(self):
        try:
            s=int(self.size.get())
            if s!=768:raise NotImplementedError(f'La génération {s}×{s} est réservée mais pas encore calibrée. Max joueurs={NATIVE_LIMITS[s]}.')
            seed=int(self.seed.get());players=int(self.players.get());self.progress['value']=2;self.status.set('Génération…');self.update_idletasks();self.import_source=None
            self.current=self.generator.generate(players,seed,mode=self._mode_key(),archetype=self._arch_key());self.progress['value']=100;self._populate_current();self._refresh_preview()
        except Exception as e:self.progress['value']=0;self.status.set('Erreur');messagebox.showerror('MapGen',f'{e}\n\n{traceback.format_exc()}')

    def import_file(self):
        path=filedialog.askopenfilename(title='Importer une map',filetypes=[('Settlers III','*.edm *.map *.sav'),('EDM','*.edm'),('MAP','*.map'),('SAV','*.sav'),('Tous','*.*')])
        if not path:return
        try:
            p=Path(path);ext=p.suffix.lower();self.progress['value']=10
            if ext=='.sav':state=read_sav_state(p)
            elif ext in ('.edm','.map'):
                state=read_area(p);state.starts=read_starts(p);state.metadata.update({'source_format':ext[1:].upper(),'source_path':str(p),'territories_available':False})
            else:raise ValueError('Extension non supportée')
            self.import_source=p;self.current=GenerationOutput(state,[],[f'import.{ext[1:]} — {p.name}']);self.progress['value']=100;self._populate_current(imported=True);self._refresh_preview();self.status.set(f'Importé — {p.name} — {state.side}×{state.side}')
        except Exception as e:self.progress['value']=0;messagebox.showerror('Import',f'{e}\n\n{traceback.format_exc()}')

    def _populate_current(self,imported=False):
        hard_fail=[v for v in self.current.validations if v.hard and not v.passed]
        self.validation.delete('1.0','end');self.validation.insert('end','Fichier importé : validations de génération non exécutées.\n' if imported else ''.join(v.label()+'\n' for v in self.current.validations))
        self.pipeline.delete('1.0','end');self.pipeline.insert('end','\n'.join(self.current.stage_log))
        self.meta.delete('1.0','end');self.meta.insert('end',json.dumps(self.current.state.metadata,indent=2,ensure_ascii=False,default=str))
        self.stats.delete('1.0','end');self.stats.insert('end',format_stats(self.current.state))
        self.export_btn.configure(state='normal' if imported or not hard_fail else 'disabled')
        if not imported:self.status.set(f'Généré — {len(self.current.validations)-len(hard_fail)}/{len(self.current.validations)} checks OK'+(' — EXPORT AUTORISÉ' if not hard_fail else f' — {len(hard_fail)} HARD FAIL'))

    def _zoom_changed(self):self.zoom=float(self.zoom_var.get());self._refresh_preview()
    def _mouse_zoom(self,e):self.zoom_var.set(max(.5,min(4.0,self.zoom_var.get()*(1.15 if e.delta>0 else .87))));self._zoom_changed()
    def _refresh_preview(self):
        if not self.current:return
        view=VIEWS[self.view.get()]
        if view=='territories' and not self.current.state.metadata.get('territories_available') and not (self.current.state.claim!=255).any():self.status.set('Vue Territoires : surtout utile avec un SAV importé.')
        im=render(self.current.state,labels=True,view=view);cw=max(100,self.canvas.winfo_width()-10);ch=max(100,self.canvas.winfo_height()-10);base=min(cw/im.width,ch/im.height);factor=max(.05,base*self.zoom);new=(max(1,int(im.width*factor)),max(1,int(im.height*factor)));im=im.resize(new,Image.Resampling.NEAREST)
        self.photo=ImageTk.PhotoImage(im);self.canvas.delete('all');self.canvas.create_image(cw//2,ch//2,image=self.photo,anchor='center')

    def export(self):
        if not self.current:return
        folder=Path(filedialog.askdirectory(title='Dossier de sortie') or '')
        if not folder:return
        st=self.current.state;srcfmt=st.metadata.get('source_format');side=st.side
        base=f"S3_{st.metadata.get('archetype','Imported')}_{st.metadata.get('mode','Map')}_{len(st.starts) or st.metadata.get('players',0)}P_{side}x{side}_seed_{st.metadata.get('seed','import')}_MapGenV1_3_1".replace(' ','')
        made=[]
        if side==768:
            edm=folder/(base+'.edm');mp=folder/('1-'+base+'.map');export_with_scaffold(st,EDM_SCAFFOLD,edm);export_with_scaffold(st,MAP_SCAFFOLD,mp);made += [edm.name,mp.name]
        else:
            made.append('EDM/MAP non réécrits : aucun scaffold validé pour cette taille.')
        if self.import_source and self.import_source.suffix.lower()=='.sav':
            sv=folder/(base+'.sav');shutil.copy2(self.import_source,sv);made.append(sv.name+' (copie SAV inchangée)')
        else:made.append('SAV non exporté : writer SAV volontairement non implémenté/validé.')
        png=folder/(base+'_preview.png');render(st,png,view=VIEWS[self.view.get()]);made.append(png.name)
        messagebox.showinfo('Export', '\n'.join(made))

    def save_preview(self):
        if not self.current:return
        path=filedialog.asksaveasfilename(defaultextension='.png',filetypes=[('PNG','*.png')])
        if path:render(self.current.state,path,view=VIEWS[self.view.get()])

def main():App().mainloop()
