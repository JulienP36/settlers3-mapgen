from __future__ import annotations
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from .gui import VIEWS
from .gui_v14 import App as V14App
from .binary import export_with_scaffold
from .preview import render, HEATMAP_RESOURCES
from .app_paths import EDM_SCAFFOLD, MAP_SCAFFOLD

# Extend the stable v1.4/v1.5 view registry without changing generation semantics.
VIEWS.update({
    'Chemins':'paths',
    'Cultures':'crops',
    'Heatmap':'heatmap',
})

HEATMAP_LABELS={
    'Arbres':'trees',
    'Building Stones':'building_stones',
    'Poissons':'fish',
    'Coal':'coal',
    'Iron':'iron',
    'Gold':'gold',
    'Gemstones':'gems',
    'Sulfur':'sulfur',
}


class App(V14App):
    """v1.5 stable runtime + post-release UI analysis improvements."""

    def __init__(self):
        super().__init__()
        self.title('Settlers III MapGen v1.5')

    def _build(self):
        super()._build()
        # The first root child is the top control bar created by the base GUI.
        top=self.winfo_children()[0]
        ttk.Label(top,text='Ressource Heatmap').grid(row=0,column=12,sticky='w',padx=(8,0))
        self.heatmap_var=tk.StringVar(value='Arbres')
        self.heatmap_combo=ttk.Combobox(
            top,textvariable=self.heatmap_var,values=list(HEATMAP_LABELS),
            state='readonly',width=16,
        )
        self.heatmap_combo.grid(row=1,column=12,padx=(8,3))
        self.heatmap_combo.bind('<<ComboboxSelected>>',lambda e:self._heatmap_changed())
        ttk.Button(top,text='Recentrer',command=self._reset_view).grid(row=1,column=13,padx=3)
        ttk.Button(top,text='Copier seed',command=self._copy_seed).grid(row=1,column=14,padx=3)
        self._update_view_controls()

    def _heatmap_changed(self):
        self._invalidate_preview()
        self._refresh_preview(True)

    def _reset_view(self):
        self.zoom_var.set(1.0);self.zoom=1.0
        self._invalidate_preview();self._refresh_preview(True)

    def _copy_seed(self):
        value=str(self.seed.get())
        self.clipboard_clear();self.clipboard_append(value)
        self.status.set(f'Seed copié : {value}')

    def _update_view_controls(self):
        super()._update_view_controls()
        if not hasattr(self,'heatmap_combo'):
            return
        is_heatmap=VIEWS[self.view.get()]=='heatmap'
        self.heatmap_combo.configure(state='readonly' if is_heatmap else 'disabled')

    def _render_options(self):
        opts=super()._render_options()
        opts['heatmap_resource']=HEATMAP_LABELS.get(self.heatmap_var.get(),'trees') if hasattr(self,'heatmap_var') else 'trees'
        return opts

    def _refresh_preview(self,reset_pan=False):
        self._zoom_after=None
        if not self.current:return
        self._update_view_controls()
        view=VIEWS[self.view.get()]
        alpha=100 if view=='global' else int(self.opacity_var.get())
        proj=self.prefs['projection']
        heat=HEATMAP_LABELS.get(self.heatmap_var.get(),'trees') if hasattr(self,'heatmap_var') else 'trees'
        key=(id(self.current.state),view,alpha,proj,heat)
        if key!=self._preview_key:
            self._preview_base=render(
                self.current.state,labels=True,view=view,overlay_alpha=alpha,
                projection=proj,heatmap_resource=heat,
            )
            self._preview_key=key
        im=self._preview_base
        cw=max(100,self.canvas.winfo_width());ch=max(100,self.canvas.winfo_height())
        factor=max(.05,min((cw-10)/im.width,(ch-10)/im.height)*self.zoom)
        new=(max(1,int(im.width*factor)),max(1,int(im.height*factor)))
        oldx=0 if reset_pan else self.canvas.xview()[0];oldy=0 if reset_pan else self.canvas.yview()[0]
        shown=im.resize(new,Image.Resampling.NEAREST);self.photo=ImageTk.PhotoImage(shown)
        self.canvas.delete('all');sw=max(cw,new[0]);sh=max(ch,new[1])
        x=max(0,(cw-new[0])//2);y=max(0,(ch-new[1])//2)
        self.canvas.create_image(x,y,image=self.photo,anchor='nw')
        self.canvas.configure(scrollregion=(0,0,sw,sh));self.canvas.xview_moveto(oldx);self.canvas.yview_moveto(oldy)

    def export(self):
        if not self.current:
            return
        folder = filedialog.askdirectory(title='Dossier de sortie')
        if not folder:
            return
        try:
            folder = Path(folder)
            st = self.current.state
            side = st.side
            self._task_begin('Export…', 5)
            base = (
                f"S3_{st.metadata.get('archetype','Imported')}_{st.metadata.get('mode','Map')}_"
                f"{len(st.starts) or st.metadata.get('players',0)}P_{side}x{side}_"
                f"seed_{st.metadata.get('seed','import')}_MapGenV1_5"
            ).replace(' ', '')
            made = []
            if side == 768:
                edm = folder / (base + '.edm')
                mp = folder / ('1-' + base + '.map')
                export_with_scaffold(st, EDM_SCAFFOLD, edm)
                self._task_progress(35, 'Export MAP…')
                export_with_scaffold(st, MAP_SCAFFOLD, mp)
                made += [edm.name, mp.name]
            else:
                made.append('EDM/MAP non réécrits : aucun scaffold validé pour cette taille.')
            self._task_progress(62, 'Export SAV/aperçu…')
            if self.import_source and self.import_source.suffix.lower() == '.sav':
                sv = folder / (base + '.sav')
                shutil.copy2(self.import_source, sv)
                made.append(sv.name + ' (copie SAV inchangée)')
            else:
                made.append('SAV non exporté : writer SAV volontairement non implémenté/validé.')
            png = folder / (base + '_preview.png')
            render(st, png, **self._render_options())
            made.append(png.name)
            self._task_done('Export terminé')
            messagebox.showinfo('Export', '\n'.join(made))
        except Exception as e:
            self._task_error('Erreur export')
            messagebox.showerror('Export', f'{e}')


def main():
    App().mainloop()
