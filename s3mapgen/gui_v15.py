from __future__ import annotations
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from .gui import VIEWS, NATIVE_LIMITS
from .gui_v14 import App as V14App
from .binary import export_with_scaffold
from .preview import render
from .preferences import save_settings
from .app_paths import EDM_SCAFFOLD, MAP_SCAFFOLD
from .session_cache import GenerationCacheKey, SessionGenerationCache

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
    'Copier seed':{'en':'Copy seed'},'Langue':{'en':'Language'},'Aide':{'en':'Help'},
    'Historique session':{'en':'Session history'},'Charger':{'en':'Load'},'Vider cache':{'en':'Clear cache'},
    'Définir A':{'en':'Set A'},'Définir B':{'en':'Set B'},'Basculer A/B':{'en':'Toggle A/B'},
}

MINERAL_NAMES={0x10:'Coal',0x20:'Iron',0x30:'Gold',0x40:'Gemstones',0x50:'Sulfur'}
TERRAIN_NAMES={
    16:'Grass',24:'Yellow Grass',32:'Rocky',34:'Rocky detail',35:'Rock/Snow transition',
    48:'Shore',128:'Snow',129:'Snow transition',22:'Agricultural runtime',28:'Worked/Path runtime',
    96:'River 1',97:'River 2',98:'River 3',99:'River 4',
}


class App(V14App):
    """v1.5 stable runtime + post-release UI analysis improvements."""

    def __init__(self):
        self.session_cache=SessionGenerationCache(max_items=8)
        self._history_lookup={}
        self._compare_slots={'A':None,'B':None}
        self._compare_active=None
        self._display_origin=(0,0)
        self._display_factor=1.0
        super().__init__()
        self.title('Settlers III MapGen v1.5')
        self._bind_shortcuts()
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
        ttk.Button(top,text='Aide',command=self._show_help).grid(row=1,column=16,padx=3)

        self.inspector_var=tk.StringVar(value='Inspecteur : —')
        self.inspector_label=ttk.Label(top,textvariable=self.inspector_var,anchor='w')
        self.inspector_label.grid(row=4,column=0,columnspan=17,sticky='ew',pady=(3,1))

        ttk.Label(top,text='Historique session').grid(row=5,column=0,sticky='w',pady=(4,0))
        self.history_var=tk.StringVar(value='')
        self.history_combo=ttk.Combobox(top,textvariable=self.history_var,state='readonly',width=58)
        self.history_combo.grid(row=5,column=1,columnspan=6,sticky='ew',padx=(3,3),pady=(4,0))
        ttk.Button(top,text='Charger',command=self._load_history).grid(row=5,column=7,padx=3,pady=(4,0))
        ttk.Button(top,text='Vider cache',command=self._clear_history).grid(row=5,column=8,padx=3,pady=(4,0))
        ttk.Button(top,text='Définir A',command=lambda:self._set_compare_slot('A')).grid(row=5,column=9,padx=3,pady=(4,0))
        ttk.Button(top,text='Définir B',command=lambda:self._set_compare_slot('B')).grid(row=5,column=10,padx=3,pady=(4,0))
        ttk.Button(top,text='Basculer A/B',command=self._toggle_compare).grid(row=5,column=11,padx=3,pady=(4,0))
        self.compare_var=tk.StringVar(value='A: —   |   B: —')
        ttk.Label(top,textvariable=self.compare_var,anchor='w').grid(row=6,column=0,columnspan=17,sticky='ew',pady=(1,2))

        self.canvas.bind('<Motion>',self._inspect_motion,add='+')
        self.canvas.bind('<Leave>',lambda e:self._clear_inspector(),add='+')

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
        if self._view_combo:self._view_combo.configure(values=list(VIEW_LABELS[lang].values()))
        self.view.set(VIEW_LABELS[lang][view_key])
        self.heatmap_combo.configure(values=list(HEATMAP_LABELS[lang].values()))
        self.heatmap_var.set(HEATMAP_LABELS[lang][heat_key])
        if self._theme_combo:self._theme_combo.configure(values=list(THEME_LABELS[lang].values()))
        self.theme_var.set(THEME_LABELS[lang][self.prefs['theme']])
        if self._projection_combo:self._projection_combo.configure(values=list(PROJECTION_LABELS[lang].values()))
        self.projection_var.set(PROJECTION_LABELS[lang][self.prefs['projection']])
        self.lang_var.set(LANG_LABELS[lang])
        self._update_view_controls();self._clear_inspector();self._refresh_compare_label()

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

    def _heatmap_changed(self):self._invalidate_preview();self._refresh_preview(True)

    def _reset_view(self):
        self.zoom_var.set(1.0);self.zoom=1.0;self._invalidate_preview();self._refresh_preview(True)

    def _copy_seed(self):
        value=str(self.seed.get());self.clipboard_clear();self.clipboard_append(value)
        self.status.set((f'Seed copied: {value}') if self.prefs.get('language')=='en' else f'Seed copié : {value}')

    # ---------- cell inspector ----------
    def _source_cell_from_canvas(self,event):
        if not self.current or self._display_factor<=0:return None
        cx=self.canvas.canvasx(event.x);cy=self.canvas.canvasy(event.y)
        px=(cx-self._display_origin[0])/self._display_factor
        py=(cy-self._display_origin[1])/self._display_factor
        side=self.current.state.side
        if self.prefs.get('projection')=='parallelogram':
            y=int(py//2)
            if not 0<=y<side:return None
            shift=side-1-y
            x=int((px-shift)//2)
        else:
            x=int(px);y=int(py)
        if 0<=x<side and 0<=y<side:return x,y
        return None

    def _resource_text(self,terrain,raw):
        fam=int(raw)&0xf0;qty=int(raw)&0x0f
        if qty<=0:return '—'
        if int(terrain) in range(8) and fam==0:return f'Fish {qty}'
        if fam in MINERAL_NAMES:return f'{MINERAL_NAMES[fam]} {qty}'
        return f'0x{int(raw):02X} (qty {qty})'

    def _object_text(self,oid):
        oid=int(oid)
        if oid==0:return '—'
        if 68<=oid<=81:return f'{oid} (tree)'
        if oid==84:return '84 (Small Tree)'
        if 115<=oid<=127:return f'{oid} (Building Stone, stock {127-oid})'
        if 85<=oid<=93:return f'{oid} (wheat)'
        if 94<=oid<=102:return f'{oid} (vine)'
        if 103<=oid<=110:return f'{oid} (rice)'
        if 111<=oid<=114:return f'{oid} (reef)'
        return str(oid)

    def _inspect_motion(self,event):
        cell=self._source_cell_from_canvas(event)
        if cell is None:return self._clear_inspector()
        x,y=cell;st=self.current.state
        h=int(st.height[y,x]);t=int(st.terrain[y,x]);o=int(st.objects[y,x]);a=int(st.accessibility[y,x]);c=int(st.claim[y,x]);r=int(st.resources[y,x])
        tname=TERRAIN_NAMES.get(t,'')
        terrain=f'{t}'+(f' ({tname})' if tname else '')
        claim='—' if c==255 else f'P{c+1} / {c}'
        prefix='Inspector' if self.prefs.get('language')=='en' else 'Inspecteur'
        self.inspector_var.set(f'{prefix}  x={x} y={y}  |  Terrain {terrain}  |  Object {self._object_text(o)}  |  Resource {self._resource_text(t,r)}  |  Height {h}  |  Access {a}  |  Claim {claim}')

    def _clear_inspector(self):
        if hasattr(self,'inspector_var'):
            self.inspector_var.set('Inspector: —' if self.prefs.get('language')=='en' else 'Inspecteur : —')

    # ---------- session cache / history ----------
    def _cache_key(self):
        return GenerationCacheKey(
            seed=int(self.seed.get()),side=int(self.size.get()),players=int(self.players.get()),
            mode=self._mode_key(),archetype=self._arch_key(),modifiers=(),engine_revision='v1.5-post-ui',
        )

    def _history_label(self,key):
        return f'{key.seed} · {key.side}² · {key.players}P · {key.mode} · {key.archetype}'

    def _refresh_history_combo(self):
        self._history_lookup={self._history_label(k):(k,v) for k,v in self.session_cache.entries()}
        values=list(self._history_lookup)
        self.history_combo.configure(values=values)
        if values:self.history_var.set(values[0])
        else:self.history_var.set('')

    def _load_history(self):
        pair=self._history_lookup.get(self.history_var.get())
        if not pair:return
        self._activate_cached(pair[0],pair[1],reset_pan=True)
        self.status.set(('Loaded from session cache' if self.prefs.get('language')=='en' else 'Chargé depuis le cache de session')+f' — {self._history_label(pair[0])}')

    def _activate_cached(self,key,result,reset_pan=False):
        self.seed.set(str(key.seed));self.size.set(str(key.side));self.players.set(key.players)
        self.current=result;self.import_source=None
        self._populate_current();self._invalidate_preview();self._refresh_preview(reset_pan)

    def _clear_history(self):
        self.session_cache.clear();self._compare_slots={'A':None,'B':None};self._compare_active=None
        self._refresh_history_combo();self._refresh_compare_label()
        self.status.set('Session cache cleared' if self.prefs.get('language')=='en' else 'Cache de session vidé')

    def generate(self):
        try:
            side=int(self.size.get())
            if side!=768:raise NotImplementedError(f'La génération {side}×{side} est réservée mais pas encore calibrée. Max joueurs={NATIVE_LIMITS[side]}.')
            key=self._cache_key();cached=self.session_cache.get(key)
            if cached is not None:
                self._activate_cached(key,cached,reset_pan=True);self._refresh_history_combo()
                self.status.set(('Cache hit — generation reused' if self.prefs.get('language')=='en' else 'Cache trouvé — génération réutilisée')+f' — {self._history_label(key)}')
                return
            self._task_begin('Generation…' if self.prefs.get('language')=='en' else 'Génération…',2);self.import_source=None
            self.current=self.generator.generate(int(self.players.get()),int(self.seed.get()),mode=self._mode_key(),archetype=self._arch_key())
            self.session_cache.put(key,self.current);self._refresh_history_combo()
            self._task_progress(97,'Finalizing preview…' if self.prefs.get('language')=='en' else 'Finalisation de l’aperçu…')
            self._populate_current();self._invalidate_preview();self._refresh_preview(True);self._task_done(self.status.get())
        except Exception as e:
            self._task_error();messagebox.showerror('MapGen',f'{e}')

    # ---------- lightweight A/B comparison ----------
    def _selected_history_pair(self):
        return self._history_lookup.get(self.history_var.get())

    def _set_compare_slot(self,slot):
        pair=self._selected_history_pair()
        if not pair:
            self.status.set('Select a cached generation first' if self.prefs.get('language')=='en' else 'Sélectionne d’abord une génération du cache')
            return
        self._compare_slots[slot]=pair
        self._refresh_compare_label()
        self.status.set((f'Comparison {slot} set' if self.prefs.get('language')=='en' else f'Comparaison {slot} définie')+f' — {self._history_label(pair[0])}')

    def _short_compare_label(self,pair):
        if not pair:return '—'
        key,_=pair
        return f'{key.seed}/{key.mode}/{key.players}P'

    def _refresh_compare_label(self):
        if not hasattr(self,'compare_var'):return
        marker=self._compare_active or '—'
        self.compare_var.set(f'A: {self._short_compare_label(self._compare_slots["A"])}   |   B: {self._short_compare_label(self._compare_slots["B"])}   |   active: {marker}')

    def _toggle_compare(self):
        a=self._compare_slots['A'];b=self._compare_slots['B']
        if not a or not b:
            self.status.set('Set both A and B first' if self.prefs.get('language')=='en' else 'Définis d’abord A et B')
            return
        target='B' if self._compare_active=='A' else 'A'
        pair=self._compare_slots[target]
        # Keep view/zoom/projection/heatmap and current canvas fractions unchanged.
        self._activate_cached(pair[0],pair[1],reset_pan=False)
        self._compare_active=target;self._refresh_compare_label()
        self.status.set((f'Comparison {target}' if self.prefs.get('language')=='en' else f'Comparaison {target}')+f' — {self._history_label(pair[0])}')

    # ---------- shortcuts / help ----------
    def _bind_shortcuts(self):
        self.bind_all('<Control-g>',lambda e:self.generate())
        self.bind_all('<Control-o>',lambda e:self.import_file())
        self.bind_all('<Control-e>',lambda e:self.export())
        self.bind_all('<Control-r>',lambda e:self._reset_view())
        self.bind_all('<Control-Shift-C>',lambda e:self._copy_seed())
        self.bind_all('<Control-b>',lambda e:self._toggle_compare())
        self.bind_all('<F1>',lambda e:self._show_help())

    def _show_help(self):
        en=self.prefs.get('language')=='en'
        text=(
            'Keyboard shortcuts\n\nCtrl+G  Generate\nCtrl+O  Import\nCtrl+E  Export\nCtrl+R  Reset view\nCtrl+Shift+C  Copy seed\nCtrl+B  Toggle comparison A/B\nF1  Help\n\nMouse\nWheel: zoom\nLeft drag: pan\nHover map: inspect exact cell data\n\nCache\nGenerating the exact same parameters again reuses the in-memory result instantly. Session history and A/B are optional analysis tools on top of that transparent cache.\n\nShortcuts will become rebindable in Settings in a future UI pass.'
            if en else
            'Raccourcis clavier\n\nCtrl+G  Générer\nCtrl+O  Importer\nCtrl+E  Exporter\nCtrl+R  Recentrer\nCtrl+Shift+C  Copier le seed\nCtrl+B  Basculer comparaison A/B\nF1  Aide\n\nSouris\nMolette : zoom\nClic gauche + glisser : déplacer\nSurvol de la map : inspecter les données exactes de la cellule\n\nCache\nRelancer exactement les mêmes paramètres réutilise instantanément le résultat en mémoire. L’historique et A/B sont seulement des outils d’analyse optionnels au-dessus de ce cache transparent.\n\nLes raccourcis deviendront reconfigurables dans Paramètres lors d’une future passe UI.'
        )
        messagebox.showinfo('Help' if en else 'Aide',text)

    def _update_view_controls(self):
        if hasattr(self,'opacity_scale'):self.opacity_scale.configure(state='disabled' if self._view_key()=='global' else 'normal')
        if hasattr(self,'heatmap_combo'):self.heatmap_combo.configure(state='readonly' if self._view_key()=='heatmap' else 'disabled')

    def _render_options(self):
        view=self._view_key()
        return {'view':view,'overlay_alpha':100 if view=='global' else int(self.opacity_var.get()),'projection':self.prefs['projection'],'heatmap_resource':self._heatmap_key()}

    def _refresh_preview(self,reset_pan=False):
        self._zoom_after=None
        if not self.current:return
        self._update_view_controls();view=self._view_key();alpha=100 if view=='global' else int(self.opacity_var.get());proj=self.prefs['projection'];heat=self._heatmap_key()
        key=(id(self.current.state),view,alpha,proj,heat)
        if key!=self._preview_key:
            self._preview_base=render(self.current.state,labels=True,view=view,overlay_alpha=alpha,projection=proj,heatmap_resource=heat);self._preview_key=key
        im=self._preview_base;cw=max(100,self.canvas.winfo_width());ch=max(100,self.canvas.winfo_height());factor=max(.05,min((cw-10)/im.width,(ch-10)/im.height)*self.zoom)
        new=(max(1,int(im.width*factor)),max(1,int(im.height*factor)));oldx=0 if reset_pan else self.canvas.xview()[0];oldy=0 if reset_pan else self.canvas.yview()[0]
        shown=im.resize(new,Image.Resampling.NEAREST);self.photo=ImageTk.PhotoImage(shown);self.canvas.delete('all');sw=max(cw,new[0]);sh=max(ch,new[1]);x=max(0,(cw-new[0])//2);y=max(0,(ch-new[1])//2)
        self.canvas.create_image(x,y,image=self.photo,anchor='nw');self.canvas.configure(scrollregion=(0,0,sw,sh));self.canvas.xview_moveto(oldx);self.canvas.yview_moveto(oldy)
        self._display_origin=(x,y);self._display_factor=factor

    def export(self):
        if not self.current:return
        lang=self.prefs.get('language','fr');folder=filedialog.askdirectory(title='Output folder' if lang=='en' else 'Dossier de sortie')
        if not folder:return
        try:
            folder=Path(folder);st=self.current.state;side=st.side;self._task_begin('Export…',5)
            base=(f"S3_{st.metadata.get('archetype','Imported')}_{st.metadata.get('mode','Map')}_{len(st.starts) or st.metadata.get('players',0)}P_{side}x{side}_seed_{st.metadata.get('seed','import')}_MapGenV1_5").replace(' ','');made=[]
            if side==768:
                edm=folder/(base+'.edm');mp=folder/('1-'+base+'.map');export_with_scaffold(st,EDM_SCAFFOLD,edm);self._task_progress(35,'Export MAP…');export_with_scaffold(st,MAP_SCAFFOLD,mp);made += [edm.name,mp.name]
            else:made.append('EDM/MAP not rewritten: no validated scaffold for this size.' if lang=='en' else 'EDM/MAP non réécrits : aucun scaffold validé pour cette taille.')
            self._task_progress(62,'Export SAV/preview…' if lang=='en' else 'Export SAV/aperçu…')
            if self.import_source and self.import_source.suffix.lower()=='.sav':
                sv=folder/(base+'.sav');shutil.copy2(self.import_source,sv);made.append(sv.name+(' (unchanged SAV copy)' if lang=='en' else ' (copie SAV inchangée)'))
            else:made.append('SAV not exported: SAV writer is intentionally not implemented/validated.' if lang=='en' else 'SAV non exporté : writer SAV volontairement non implémenté/validé.')
            png=folder/(base+'_preview.png');render(st,png,**self._render_options());made.append(png.name);self._task_done('Export complete' if lang=='en' else 'Export terminé');messagebox.showinfo('Export','\n'.join(made))
        except Exception as e:self._task_error('Export error' if lang=='en' else 'Erreur export');messagebox.showerror('Export',f'{e}')


def main():App().mainloop()
