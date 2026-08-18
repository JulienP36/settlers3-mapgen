from __future__ import annotations
import json, traceback
from pathlib import Path
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from PIL import ImageTk
from .app_paths import PROFILE,LIBRARY,EDM_SCAFFOLD,MAP_SCAFFOLD,OUTPUT
from .engine import MapGenerator
from .preview import render
from .binary import export_with_scaffold
from .modes import MODES, MODE_ORDER
from .archetypes import ARCHETYPES, ARCHETYPE_ORDER

class App(tk.Tk):
    def __init__(self):
        super().__init__();self.title('Settlers III MapGen v1.1');self.geometry('1280x820');self.minsize(1050,700)
        self.generator=MapGenerator(PROFILE,LIBRARY);self.current=None;self.photo=None
        self._build()

    def _build(self):
        top=ttk.Frame(self,padding=8);top.pack(fill='x')
        ttk.Label(top,text='Mode de génération').grid(row=0,column=0,sticky='w')
        self.mode=tk.StringVar(value='Legacy')
        self.mode_combo=ttk.Combobox(top,textvariable=self.mode,values=[MODES[k].label for k in MODE_ORDER],state='readonly',width=14)
        self.mode_combo.grid(row=1,column=0,padx=(0,8));self.mode_combo.bind('<<ComboboxSelected>>',lambda e:self._selection_changed())
        ttk.Label(top,text='Archétype').grid(row=0,column=1,sticky='w')
        self.arch=tk.StringVar(value='Continental')
        self.arch_combo=ttk.Combobox(top,textvariable=self.arch,values=[ARCHETYPES[k].label for k in ARCHETYPE_ORDER],state='readonly',width=15)
        self.arch_combo.grid(row=1,column=1,padx=(0,8));self.arch_combo.bind('<<ComboboxSelected>>',lambda e:self._selection_changed())
        ttk.Label(top,text='Taille').grid(row=0,column=2,sticky='w');self.size=tk.StringVar(value='768');ttk.Combobox(top,textvariable=self.size,values=['768'],state='readonly',width=8).grid(row=1,column=2,padx=(0,8))
        ttk.Label(top,text='Joueurs').grid(row=0,column=3,sticky='w');self.players=tk.IntVar(value=4);ttk.Spinbox(top,from_=2,to=20,textvariable=self.players,width=7).grid(row=1,column=3,padx=(0,8))
        ttk.Label(top,text='Seed').grid(row=0,column=4,sticky='w');self.seed=tk.StringVar(value='2026081901');ttk.Entry(top,textvariable=self.seed,width=16).grid(row=1,column=4,padx=(0,8))
        ttk.Button(top,text='Générer',command=self.generate).grid(row=1,column=5,padx=4)
        self.export_btn=ttk.Button(top,text='Exporter EDM + MAP',command=self.export,state='disabled');self.export_btn.grid(row=1,column=6,padx=4)
        ttk.Button(top,text='Sauver aperçu PNG',command=self.save_preview).grid(row=1,column=7,padx=4)
        self.status=tk.StringVar(value='Prêt — Legacy / Continental disponible. Upgraded et Custom sont réservés pour les prochaines passes.')
        ttk.Label(top,textvariable=self.status).grid(row=2,column=0,columnspan=8,sticky='w',pady=(8,0))

        pan=ttk.Panedwindow(self,orient='horizontal');pan.pack(fill='both',expand=True,padx=8,pady=(0,8))
        left=ttk.Frame(pan);right=ttk.Frame(pan);pan.add(left,weight=3);pan.add(right,weight=2)
        self.canvas=tk.Canvas(left,bg='#181818',highlightthickness=0);self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Configure>',lambda e:self._refresh_preview())
        nb=ttk.Notebook(right);nb.pack(fill='both',expand=True)
        f1=ttk.Frame(nb);f2=ttk.Frame(nb);f3=ttk.Frame(nb);nb.add(f1,text='Validations');nb.add(f2,text='Pipeline');nb.add(f3,text='Métadonnées')
        self.validation=tk.Text(f1,wrap='word',font=('Consolas',10));self.validation.pack(fill='both',expand=True)
        self.pipeline=tk.Text(f2,wrap='word',font=('Consolas',10));self.pipeline.pack(fill='both',expand=True)
        self.meta=tk.Text(f3,wrap='word',font=('Consolas',10));self.meta.pack(fill='both',expand=True)

    def _mode_key(self):
        label=self.mode.get()
        return next(k for k,v in MODES.items() if v.label==label)

    def _arch_key(self):
        label=self.arch.get()
        return next(k for k,v in ARCHETYPES.items() if v.label==label)

    def _selection_changed(self):
        m=MODES[self._mode_key()];a=ARCHETYPES[self._arch_key()]
        if not m.implemented:
            self.status.set(f'{m.label} est réservé dans la v1.1 ; son profil sera récupéré depuis les références/checkpoints avant activation.')
        elif not a.implemented:
            self.status.set(f'{a.label} est réservé comme macro-archétype mais pas encore implémenté.')
        else:
            self.status.set(f'Prêt — {m.label} / {a.label}. Les starts seront placés immédiatement après le macro-layout.')

    def generate(self):
        try:
            seed=int(self.seed.get());players=int(self.players.get());self.status.set('Génération…');self.update_idletasks()
            self.current=self.generator.generate(players,seed,mode=self._mode_key(),archetype=self._arch_key())
            hard_fail=[v for v in self.current.validations if v.hard and not v.passed]
            self.validation.delete('1.0','end')
            for v in self.current.validations:self.validation.insert('end',v.label()+'\n')
            self.pipeline.delete('1.0','end');self.pipeline.insert('end','\n'.join(self.current.stage_log))
            self.meta.delete('1.0','end');self.meta.insert('end',json.dumps(self.current.state.metadata,indent=2,ensure_ascii=False,default=str))
            self.export_btn.configure(state='disabled' if hard_fail else 'normal')
            self.status.set(f'Généré — {len(self.current.validations)-len(hard_fail)}/{len(self.current.validations)} checks OK' + (f' — {len(hard_fail)} HARD FAIL' if hard_fail else ' — EXPORT AUTORISÉ'))
            self._refresh_preview()
        except Exception as e:
            self.status.set('Erreur de génération');messagebox.showerror('MapGen',f'{e}\n\n{traceback.format_exc()}')

    def _refresh_preview(self):
        if not self.current:return
        im=render(self.current.state,labels=True)
        w=max(100,self.canvas.winfo_width()-10);h=max(100,self.canvas.winfo_height()-10);im.thumbnail((w,h))
        self.photo=ImageTk.PhotoImage(im);self.canvas.delete('all');self.canvas.create_image(w//2,h//2,image=self.photo,anchor='center')

    def export(self):
        if not self.current:return
        hard_fail=[v for v in self.current.validations if v.hard and not v.passed]
        if hard_fail:messagebox.showerror('Export refusé','Un ou plusieurs HARD checks échouent.');return
        folder=Path(filedialog.askdirectory(title='Dossier de sortie') or '')
        if not folder:return
        seed=self.current.state.metadata['seed'];p=self.current.state.metadata['players'];mode=self.current.state.metadata.get('mode','Legacy').replace(' ','');arch=self.current.state.metadata.get('archetype','Continental').replace(' ','');base=f'S3_{arch}_{mode}_{p}P_768x768_seed_{seed}_MapGenV1_1'
        edm=folder/(base+'.edm');mp=folder/('1-'+base+'.map');png=folder/(base+'_preview.png')
        export_with_scaffold(self.current.state,EDM_SCAFFOLD,edm);export_with_scaffold(self.current.state,MAP_SCAFFOLD,mp);render(self.current.state,png)
        messagebox.showinfo('Export terminé',f'{edm.name}\n{mp.name}\n{png.name}')

    def save_preview(self):
        if not self.current:return
        path=filedialog.asksaveasfilename(defaultextension='.png',filetypes=[('PNG','*.png')])
        if path:render(self.current.state,path)

def main():
    App().mainloop()
