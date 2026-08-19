from __future__ import annotations
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from .gui import VIEWS
from .gui_v14 import App as V14App
from .binary import export_with_scaffold
from .preview import render
from .preferences import save_settings
from .app_paths import EDM_SCAFFOLD, MAP_SCAFFOLD

VIEWS.update({'Chemins':'paths','Cultures':'crops','Heatmap':'heatmap'})

VIEW_LABELS={
    'fr':{'global':'Global','heightmap':'Heightmap','resources':'Ressources','territories':'Territoires','paths':'Chemins','crops':'Cultures','heatmap':'Heatmap'},
    'en':{'global':'Global','heightmap':'Heightmap','resources':'Resources','territories':'Territories','paths':'Paths','crops':'Crops','heatmap':'Heatmap'},
}
HEATMAP_LABELS={
    'fr':{'trees':'Arbres','building_stones':'Building Stones','fish':'Poissons','coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gemstones','sulfur':'Sulfur'},
    'en':{'trees':'Trees','building_stones':'Building Stones','fish':'Fish','coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gemstones','sulfur':'Sulfur'},
}
THEME_LABELS={'fr':{'dark':'Sombre','light':'Clair'},'en':{'dark':'Dark','light':'Light'}}
PROJECTION_LABELS={'fr':{'square':'Carrée','parallelogram':'Parallélogramme'},'en':{'square':'Square','parallelogram':'Parallelogram'}}
LANG_LABELS={'fr':'Français','en':'English'}

TEXTS={
    'Archétype':{'en':'Archetype'},'Taille':{'en':'Size'},'Joueurs':{'en':'Players'},
    'Générer':{'en':'Generate'},'Importer…':{'en':'Import…'},'Exporter…':{'en':'Export…'},
    'Aperçu PNG':{'en':'PNG Preview'},'Vue':{'en':'View'},'Affichage':{'en':'Display'},
    'Thème':{'en':'Theme'},'Opacité couche':{'en':'Layer opacity'},
    '0 % = map globale · 100 % = couche seule':{'en':'0 % = global map · 100 % = overlay only'},
    'Projection':{'en':'Projection'},
    'Le parallélogramme modifie uniquement le rendu, jamais les données.':{'en':'Parallelogram changes rendering only, never map data.'},
    'Sensibilité molette':{'en':'Mouse-wheel sensitivity'},'Navigation':{'en':'Navigation'},
    'Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.':{'en':'Mouse wheel: zoom\nLeft click + drag: move map\nZoom refresh is delayed to reduce recalculation.'},
    'Paramètres':{'en':'Settings'},'Métadonnées':{'en':'Metadata'},'Statistiques':{'en':'Statistics'},
    'Ressource Heatmap':{'en':'Heatmap resource'},'Recentrer':{'en':'Reset view'},
    'Copier seed':{'en':'Copy seed'},'Langue':{'en':'Language'},
}


class App(V14App):
    """v1.5 stable runtime + post-release UI analysis improvements."""

    def __init__(self):
        super().__init__()
        self.title('Settlers III MapGen v1.5')
        self._apply_language()

    def _build(self):
        super()._build()
        top=self.winfo_children()[0]
        ttk.Label(top,text='Ressource Heatmap').grid(row=0,column=12,sticky='w',padx=(8,0))
        self.heatmap_var=tk.StringVar(value='Arbres')
        self.heatmap_combo=ttk.Combobox(top,textvariable=self.heatmap_var,state='readonly',width=16)
        self.heatmap_combo.grid(row=1,column=12,padx=(8,3))
        self.heatmap_combo.bind('<<ComboboxSelected>>',lambda e:self._heatmap_changed())
        ttk.Button(top,text='Recentrer',command=self._reset_view).grid(row=1,column=13,padx=3)
        ttk.Button(top,text='Copier seed',command=self._copy_seed).grid(row=1,column=14,padx=3)
        ttk.Label(top,text='Langue').grid(row=0,column=15,sticky='w',padx=(8,0))
        self.lang_var=tk.StringVar(value=LANG_LABELS.get(self.prefs.get('language','fr'),'Français'))
        self.lang_combo=ttk.Combobox(top,textvariable=self.lang_var,values=list(LANG_LABELS.values()),state='readonly',width=9)
        self.lang_combo.grid(row=1,column=15,padx=(8,3))
        self.lang_combo.bind('<<ComboboxSelected>>',lambda e:self._language_changed())

        self._view_combo=self._find_combo_for_var(self.view)
        self._theme_combo=self._find_combo_for_var(self.theme_var)
        self._projection_combo=self._find_combo_for_var(self.projection_var)
        self._capture_translatable_widgets()
        self._update_view_controls()

    def _walk(self,root):
        for child in root.winfo_children():
            yield child
            yield from self._walk(child)

    def _find_combo_for_var(self,var):
        target=str(var)
        for w in self._walk(self):
            if isinstance(w,ttk.Combobox):
                try:
                    if str(w.cget('textvariable'))==target:return w
                except tk.TclError:
                    pass
        return None

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

    def _view_key(self):
        value=self.view.get()
        for labels in VIEW_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return VIEWS.get(value,'global')

    def _heatmap_key(self):
        value=self.heatmap_var.get() if hasattr(self,'heatmap_var') else 'Arbres'
        for labels in HEATMAP_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return 'trees'

    def _theme_key(self):
        value=self.theme_var.get()
        for labels in THEME_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return self.prefs.get('theme','dark')

    def _projection_key(self):
        value=self.projection_var.get()
        for labels in PROJECTION_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return self.prefs.get('projection','square')

    def _apply_language(self):
        if not hasattr(self,'lang_var'):return
        lang=self.prefs.get('language','fr')
        view_key=self._view_key();heat_key=self._heatmap_key()
        for w,source in getattr(self,'_i18n_widgets',[]):
            try:w.configure(text=TEXTS[source].get(lang,source) if lang!='fr' else source)
            except tk.TclError:pass
        for tab,source in getattr(self,'_i18n_tabs',[]):
            self.nb.tab(tab,text=TEXTS[source].get(lang,source) if lang!='fr' else source)
        if self._view_combo:
            self._view_combo.configure(values=list(VIEW_LABELS[lang].values()))
        self.view.set(VIEW_LABELS[lang][view_key])
        self.heatmap_combo.configure(values=list(HEATMAP_LABELS[lang].values()))
        self.heatmap_var.set(HEATMAP_LABELS[lang][heat_key])
        if self._theme_combo:self._theme_combo.configure(values=list(THEME_LABELS[lang].values()))
        self.theme_var.set(THEME_LABELS[lang][self.prefs['theme']])
        if self._projection_combo:self._projection_combo.configure(values=list(PROJECTION_LABELS[lang].values()))
        self.projection_var.set(PROJECTION_LABELS[lang][self.prefs['projection']])
        self.lang_var.set(LANG_LABELS[lang])
        self._update_view_controls()

    def _language_changed(self):
        self.prefs['language']='en' if self.lang_var.get()=='English' else 'fr'
        self._save_prefs();self._apply_language();self._invalidate_preview();self._refresh_preview(True)

    def _save_prefs(self):
        save_settings({
            'theme':self.prefs['theme'],'overlay_alpha':int(self.opacity_var.get()),
            'projection':self.prefs['projection'],'wheel_zoom':float(self.wheel_var.get()),
            'language':self.prefs.get('language','fr'),
        })

    def _theme_changed(self):
        self.prefs['theme']=self._theme_key();self._save_prefs();self._apply_theme()

    def _projection_changed(self):
        self.prefs['projection']=self._projection_key();self._save_prefs();self._invalidate_preview();self._refresh_preview(True)

    def _heatmap_changed(self):
        self._invalidate_preview();self._refresh_preview(True)

    def _reset_view(self):
        self.zoom_var.set(1.0);self.zoom=1.0;self._invalidate_preview();self._refresh_preview(True)

    def _copy_seed(self):
        value=str(self.seed.get());self.clipboard_clear();self.clipboard_append(value)
        self.status.set((f'Seed copied: {value}') if self.prefs.get('language')=='en' else f'Seed copié : {value}')

    def _update_view_controls(self):
        if hasattr(self,'opacity_scale'):
            self.opacity_scale.configure(state='disabled' if self._view_key()=='global' else 'normal')
        if hasattr(self,'heatmap_combo'):
            self.heatmap_combo.configure(state='readonly' if self._view_key()=='heatmap' else 'disabled')

    def _render_options(self):
        view=self._view_key()
        return {
            'view':view,'overlay_alpha':100 if view=='global' else int(self.opacity_var.get()),
            'projection':self.prefs['projection'],'heatmap_resource':self._heatmap_key(),
        }

    def _refresh_preview(self,reset_pan=False):
        self._zoom_after=None
        if not self.current:return
        self._update_view_controls();view=self._view_key()
        alpha=100 if view=='global' else int(self.opacity_var.get())
        proj=self.prefs['projection'];heat=self._heatmap_key()
        key=(id(self.current.state),view,alpha,proj,heat)
        if key!=self._preview_key:
            self._preview_base=render(self.current.state,labels=True,view=view,overlay_alpha=alpha,projection=proj,heatmap_resource=heat)
            self._preview_key=key
        im=self._preview_base
        cw=max(100,self.canvas.winfo_width());ch=max(100,self.canvas.winfo_height())
        factor=max(.05,min((cw-10)/im.width,(ch-10)/im.height)*self.zoom)
        new=(max(1,int(im.width*factor)),max(1,int(im.height*factor)))
        oldx=0 if reset_pan else self.canvas.xview()[0];oldy=0 if reset_pan else self.canvas.yview()[0]
        shown=im.resize(new,Image.Resampling.NEAREST);self.photo=ImageTk.PhotoImage(shown)
        self.canvas.delete('all');sw=max(cw,new[0]);sh=max(ch,new[1]);x=max(0,(cw-new[0])//2);y=max(0,(ch-new[1])//2)
        self.canvas.create_image(x,y,image=self.photo,anchor='nw');self.canvas.configure(scrollregion=(0,0,sw,sh));self.canvas.xview_moveto(oldx);self.canvas.yview_moveto(oldy)

    def export(self):
        if not self.current:return
        lang=self.prefs.get('language','fr')
        folder=filedialog.askdirectory(title='Output folder' if lang=='en' else 'Dossier de sortie')
        if not folder:return
        try:
            folder=Path(folder);st=self.current.state;side=st.side
            self._task_begin('Export…',5)
            base=(f"S3_{st.metadata.get('archetype','Imported')}_{st.metadata.get('mode','Map')}_{len(st.starts) or st.metadata.get('players',0)}P_{side}x{side}_seed_{st.metadata.get('seed','import')}_MapGenV1_5").replace(' ','')
            made=[]
            if side==768:
                edm=folder/(base+'.edm');mp=folder/('1-'+base+'.map');export_with_scaffold(st,EDM_SCAFFOLD,edm);self._task_progress(35,'Export MAP…');export_with_scaffold(st,MAP_SCAFFOLD,mp);made += [edm.name,mp.name]
            else:
                made.append('EDM/MAP not rewritten: no validated scaffold for this size.' if lang=='en' else 'EDM/MAP non réécrits : aucun scaffold validé pour cette taille.')
            self._task_progress(62,'Export SAV/preview…' if lang=='en' else 'Export SAV/aperçu…')
            if self.import_source and self.import_source.suffix.lower()=='.sav':
                sv=folder/(base+'.sav');shutil.copy2(self.import_source,sv);made.append(sv.name+(' (unchanged SAV copy)' if lang=='en' else ' (copie SAV inchangée)'))
            else:
                made.append('SAV not exported: SAV writer is intentionally not implemented/validated.' if lang=='en' else 'SAV non exporté : writer SAV volontairement non implémenté/validé.')
            png=folder/(base+'_preview.png');render(st,png,**self._render_options());made.append(png.name)
            self._task_done('Export complete' if lang=='en' else 'Export terminé');messagebox.showinfo('Export','\n'.join(made))
        except Exception as e:
            self._task_error('Export error' if lang=='en' else 'Erreur export');messagebox.showerror('Export',f'{e}')


def main():App().mainloop()
