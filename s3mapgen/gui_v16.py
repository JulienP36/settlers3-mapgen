from __future__ import annotations
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw

from .gui import VIEWS, NATIVE_LIMITS
from .modes import MODES, MODE_ORDER
from .archetypes import ARCHETYPES, ARCHETYPE_ORDER
from .gui_v15 import App as V15StableApp
from .binary import export_with_scaffold
from .preview import render, HEATMAP_RESOURCES
from .preferences import save_settings, DEFAULT_SHORTCUTS
from .app_paths import EDM_SCAFFOLD, MAP_SCAFFOLD
from .session_cache import GenerationCacheKey, SessionGenerationCache, SessionStatsCache
from .stats_analysis import analyze_map, format_stats_report, stats_json, stats_csv
from .stats_charts import render_stats_chart, CHART_KEYS, CHART_LABELS

VIEWS.update({'Chemins':'paths','Cultures':'crops','Heatmap':'heatmap'})

VIEW_LABELS={
 'fr':{'global':'Global','heightmap':'Élévation','resources':'Ressources','territories':'Territoires','paths':'Chemins','crops':'Cultures','heatmap':'Carte thermique'},
 'en':{'global':'Global','heightmap':'Elevation','resources':'Resources','territories':'Territories','paths':'Paths','crops':'Crops','heatmap':'Heatmap'},
}
LANGUAGE_LABELS={'fr':'Français','en':'English'}

HEATMAP_LABELS={
 'fr':{'trees':'Arbres','building_stones':'Pierres de construction','fish':'Poissons','coal':'Charbon','iron':'Fer','gold':'Or','gems':'Gemmes','sulfur':'Soufre'},
 'en':{'trees':'Trees','building_stones':'Building Stones','fish':'Fish','coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gemstones','sulfur':'Sulfur'},
}

# R5: real raster icons.  Unicode colored-circle emoji were rendered as monochrome
# glyphs by some Windows/Tk combinations, so the selectors now use tiny images
# drawn by Pillow and attached to Tk menu entries.
VIEW_ICON_COLORS={
 'global':'#2698e8','heightmap':'#8f55d6','resources':'#ff9418','territories':'#31a354',
 'paths':'#9a6438','crops':'#e4c83d','heatmap':'#d83737',
}
HEATMAP_ICON_COLORS={
 'trees':'#2b9a4a','building_stones':'#dedede','fish':'#278fd4','coal':'#101010',
 'iron':'#ff9400','gold':'#ffff00','gems':'#ce0000','sulfur':'#c4b25c',
}

MODE_LABELS={
 'fr':{'legacy':'Héritage (Legacy)','upgraded':'Amélioré (Upgraded)','custom':'Personnalisé'},
 'en':{'legacy':'Legacy','upgraded':'Upgraded','custom':'Custom'},
}
ARCHETYPE_LABELS={
 'fr':{'continental':'Continental','large_islands':'Grandes îles','small_islands':'Petites îles'},
 'en':{'continental':'Continental','large_islands':'Large Islands','small_islands':'Small Islands'},
}

COMMAND_LABELS={
 'fr':{'generate':'Générer','import':'Importer','export':'Exporter','reset_view':'Recentrer','copy_seed':'Copier le seed','toggle_ab':'Basculer A/B','toggle_theme':'Basculer thème','help':'Aide'},
 'en':{'generate':'Generate','import':'Import','export':'Export','reset_view':'Reset view','copy_seed':'Copy seed','toggle_ab':'Toggle A/B','toggle_theme':'Toggle theme','help':'Help'},
}

THEME_LABELS={'fr':{'dark':'Sombre','light':'Clair'},'en':{'dark':'Dark','light':'Light'}}
PROJECTION_LABELS={'fr':{'square':'Carrée','parallelogram':'Parallélogramme'},'en':{'square':'Square','parallelogram':'Parallelogram'}}
TEXTS={
 'Mode':{'en':'Mode'},'Archétype':{'en':'Archetype'},'Taille':{'en':'Size'},'Joueurs':{'en':'Players'},'Seed':{'en':'Seed'},'Zoom':{'en':'Zoom'},
 'Générer':{'en':'Generate'},'Importer…':{'en':'Import…'},'Exporter…':{'en':'Export…'},'Aperçu PNG':{'en':'PNG Preview'},'Vue':{'en':'View'},
 'Affichage':{'en':'Display'},'Thème':{'en':'Theme'},'Opacité couche':{'en':'Layer opacity'},'0 % = map globale · 100 % = couche seule':{'en':'0 % = global map · 100 % = overlay only'},
 'Projection':{'en':'Projection'},'Le parallélogramme modifie uniquement le rendu, jamais les données.':{'en':'Parallelogram changes rendering only, never map data.'},
 'Sensibilité molette':{'en':'Mouse-wheel sensitivity'},'Navigation':{'en':'Navigation'},'Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.':{'en':'Mouse wheel: zoom\nLeft click + drag: move map\nZoom refresh is delayed to reduce recalculation.'},
 'Paramètres':{'en':'Settings'},'Validations':{'en':'Validations'},'Pipeline':{'en':'Pipeline'},'Métadonnées':{'en':'Metadata'},'Statistiques':{'en':'Statistics'},'Graphiques':{'en':'Charts'},'Exporter JSON':{'en':'Export JSON'},'Exporter CSV':{'en':'Export CSV'},'Exporter PNG':{'en':'Export PNG'},'Ressource Heatmap':{'en':'Heatmap resource'},'Filtre carte thermique':{'en':'Heatmap filter'},
 'Recentrer':{'en':'Reset view'},'Copier seed':{'en':'Copy seed'},'Langue':{'en':'Language'},'Aide':{'en':'Help'},'Historique session':{'en':'Session history'},
 'Charger':{'en':'Load'},'Vider cache':{'en':'Clear cache'},'Définir A':{'en':'Set A'},'Définir B':{'en':'Set B'},'Basculer A/B':{'en':'Toggle A/B'},
 'Raccourcis':{'en':'Shortcuts'},'Appliquer':{'en':'Apply'},'Valeurs par défaut':{'en':'Defaults'},'Réinitialiser':{'en':'Reset'},
 'Session / Comparaison':{'en':'Session / Comparison'},'Format : Ctrl+G, Ctrl+Shift+C, Alt+1, F1…':{'en':'Format: Ctrl+G, Ctrl+Shift+C, Alt+1, F1…'},
}

MINERAL_NAMES={0x10:'Coal',0x20:'Iron',0x30:'Gold',0x40:'Gemstones',0x50:'Sulfur'}
TERRAIN_NAMES={16:'Grass',22:'Agricultural runtime',24:'Yellow Grass',28:'Worked/Path runtime',32:'Rocky',34:'Rocky detail',35:'Rock/Snow transition',48:'Shore',128:'Snow',129:'Snow transition',96:'River 1',97:'River 2',98:'River 3',99:'River 4'}

OBJECT_NAMES={
    **{i:f'Big Stone {i}' for i in range(1,9)},
    **{i:f'Stone {i-8}' for i in range(9,13)},
    **{i:f'Border Stone {i-12}' for i in range(13,21)},
    **{i:f'Small Stone {i-20}' for i in range(21,29)},
    **{i:f'Wreck {i-28}' for i in range(29,34)},34:'Grave',
    **{i:f'Small Plant {i-34}' for i in range(35,38)},
    **{i:f'Toadstool {i-37}' for i in range(38,41)},
    **{i:f'Tree Stump {i-40}' for i in range(41,43)},
    **{i:f'Dead Tree {i-42}' for i in range(43,45)},
    **{i:f'Cactus {i-44}' for i in range(45,49)},49:'Skeleton',
    **{i:f'Small Flower {i-49}' for i in range(50,53)},
    **{i:f'Small Bush {i-52}' for i in range(53,57)},
    **{i:f'Bush {i-56}' for i in range(57,62)},
    **{i:f'Reed {i-61}' for i in range(62,68)},
    68:'Birch 1',69:'Birch 2',70:'Elm 1',71:'Elm 2',72:'Oak',78:'Palm 1',79:'Palm 2',84:'Small Tree',
    **{i:f'Wheat {i-84}' for i in range(85,94)},
    **{i:f'Vine {i-93}' for i in range(94,103)},
    **{i:f'Rice {i-102}' for i in range(103,111)},
    **{i:f'Reef {i-110}' for i in range(111,115)},
    **{i:f'Building Stone {i-114}' for i in range(115,128)},
}


def _selector_icon(master, color, kind='dot', size=18):
    """Create a small high-contrast raster icon which remains colored in Tk."""
    im=Image.new('RGBA',(size,size),(0,0,0,0));d=ImageDraw.Draw(im)
    c=color
    # A two-tone outline stays visible on both light and dark popup backgrounds.
    if kind=='global':
        d.ellipse((2,2,size-3,size-3),fill=c,outline='#111111',width=1)
        d.arc((5,4,size-6,size-4),80,280,fill='#d7f2ff',width=1);d.line((3,size//2,size-4,size//2),fill='#d7f2ff',width=1)
    elif kind=='heightmap':
        d.polygon([(2,size-3),(size//2,2),(size-3,size-3)],fill=c,outline='#111111');d.line((size//2,4,size//2-3,9),fill='#f2eaff',width=2)
    elif kind=='resources':
        d.polygon([(size//2,2),(size-3,size//2),(size//2,size-3),(2,size//2)],fill=c,outline='#111111');d.ellipse((7,7,10,10),fill='#fff0c7')
    elif kind=='territories':
        d.polygon([(size//2,2),(size-3,5),(size-4,12),(size//2,size-2),(3,12),(2,5)],fill=c,outline='#111111');d.line((5,8,8,11,13,5),fill='#e8ffe8',width=2)
    elif kind=='paths':
        d.line((2,size-4,6,9,9,11,size-3,3),fill='#111111',width=5);d.line((2,size-4,6,9,9,11,size-3,3),fill=c,width=3)
    elif kind=='crops':
        d.line((size//2,size-3,size//2,4),fill='#5a4716',width=2);d.ellipse((3,4,9,8),fill=c,outline='#111111');d.ellipse((9,7,15,11),fill=c,outline='#111111');d.ellipse((4,10,10,14),fill=c,outline='#111111')
    elif kind=='heatmap':
        d.ellipse((2,2,size-3,size-3),fill=c,outline='#111111');d.ellipse((5,5,size-6,size-6),outline='#ffd9d9',width=2);d.ellipse((8,8,10,10),fill='#ffffff')
    elif kind=='flag_fr':
        # French tricolour, drawn as pixels so it stays colored on every Tk build.
        x0,y0,x1,y1=2,4,size-3,size-5;third=max(1,(x1-x0+1)//3)
        d.rectangle((x0,y0,x0+third-1,y1),fill='#0055a4');d.rectangle((x0+third,y0,x0+2*third-1,y1),fill='#ffffff');d.rectangle((x0+2*third,y0,x1,y1),fill='#ef4135');d.rectangle((x0,y0,x1,y1),outline='#111111')
    elif kind=='flag_en':
        # Compact Union Jack for the English-language selector.
        x0,y0,x1,y1=2,4,size-3,size-5;d.rectangle((x0,y0,x1,y1),fill='#21468b',outline='#111111')
        d.line((x0,y0,x1,y1),fill='#ffffff',width=4);d.line((x0,y1,x1,y0),fill='#ffffff',width=4)
        d.line((x0,y0,x1,y1),fill='#cf142b',width=2);d.line((x0,y1,x1,y0),fill='#cf142b',width=2)
        cy=(y0+y1)//2;cx=(x0+x1)//2;d.rectangle((x0,cy-2,x1,cy+2),fill='#ffffff');d.rectangle((cx-2,y0,cx+2,y1),fill='#ffffff');d.rectangle((x0,cy-1,x1,cy+1),fill='#cf142b');d.rectangle((cx-1,y0,cx+1,y1),fill='#cf142b')
    elif kind=='lock_closed':
        d.rounded_rectangle((4,8,size-4,size-3),radius=2,fill=c,outline='#111111');d.arc((5,2,size-5,11),180,360,fill=c,width=3);d.ellipse((8,11,10,13),fill='#ffffff')
    elif kind=='lock_open':
        d.rounded_rectangle((4,8,size-4,size-3),radius=2,fill=c,outline='#111111');d.arc((7,2,size-2,11),180,315,fill=c,width=3);d.ellipse((8,11,10,13),fill='#ffffff')
    else:
        # Generic resource swatch: double outline avoids black/white disappearing.
        d.ellipse((1,1,size-2,size-2),fill='#ffffff',outline='#111111',width=1)
        d.ellipse((3,3,size-4,size-4),fill=c,outline='#444444' if c.lower()!='#101010' else '#eeeeee',width=1)
    return ImageTk.PhotoImage(im,master=master)


class ColorMenuSelect(ttk.Menubutton):
    """Menubutton-backed dropdown supporting a real colored icon per entry."""
    def __init__(self, master, variable, width=20, command=None):
        super().__init__(master,textvariable=variable,width=width,compound='left',style='ImageSelect.TMenubutton')
        self.variable=variable;self.command=command;self.menu=tk.Menu(self,tearoff=False)
        self.configure(menu=self.menu);self._icons={};self._items=[];self._enabled=True
        self.bind('<MouseWheel>',self._on_mousewheel,add='+')
        self.bind('<Button-4>',lambda e:self._wheel_step(-1),add='+')
        self.bind('<Button-5>',lambda e:self._wheel_step(1),add='+')
    def set_items(self, items):
        # items: [(key,label,color,kind), ...]
        current=self.variable.get();self._items=list(items);self.menu.delete(0,'end');self._icons={}
        for key,label,color,kind in self._items:
            icon=_selector_icon(self,color,kind);self._icons[key]=icon
            self.menu.add_command(label=label,image=icon,compound='left',command=lambda k=key,l=label:self._choose(k,l))
        labels=[x[1] for x in self._items]
        if current not in labels and labels:self.variable.set(labels[0])
        self._sync_icon()
    def _choose(self,key,label):
        if not self._enabled:return
        self.variable.set(label);self._sync_icon()
        if self.command:self.command()
    def _sync_icon(self):
        value=self.variable.get()
        for key,label,_,_ in self._items:
            if label==value:
                ttk.Menubutton.configure(self,image=self._icons.get(key,''));break
    def _wheel_step(self,step):
        if not self._enabled or not self._items:return 'break'
        labels=[x[1] for x in self._items]
        try:i=labels.index(self.variable.get())
        except ValueError:i=0
        i=max(0,min(len(labels)-1,i+int(step)))
        key,label,_,_=self._items[i]
        self._choose(key,label)
        return 'break'
    def _on_mousewheel(self,event):
        delta=getattr(event,'delta',0)
        if not delta:return 'break'
        return self._wheel_step(-1 if delta>0 else 1)
    def set_enabled(self,enabled=True):
        self._enabled=bool(enabled);ttk.Menubutton.configure(self,state='normal' if enabled else 'disabled')
    def set_menu_theme(self,bg,fg,active_bg,active_fg):
        try:self.menu.configure(background=bg,foreground=fg,activebackground=active_bg,activeforeground=active_fg)
        except tk.TclError:pass

class App(V15StableApp):
    """v1.6 UI/tooling shell running the unchanged validated v1.5 generator."""
    def __init__(self):
        self.session_cache=SessionGenerationCache(max_entries=8)
        self.session_stats_cache=SessionStatsCache(max_entries=12)
        self._history_lookup={};self._compare_slots={'A':None,'B':None};self._compare_active=None
        self._display_origin=(0,0);self._display_factor=1.0;self._display_base_size=(1,1);self._bound_shortcuts=[];self._task_dialog=None;self._task_overlay=None;self._task_overlay_value=0;self._task_overlay_detail=''
        super().__init__()
        self.title('Settlers III MapGen v1.7 DEV_9 — moteur v1.5')
        self._apply_language();self._bind_shortcuts()

    def _build(self):
        super()._build();top=self.winfo_children()[0]
        # Replace the native view combobox with an image-capable menu selector.
        # Windows/Tk renders colored-circle emoji as monochrome in comboboxes.
        old_view=self._find_combo_for_var(self.view)
        view_grid=dict(old_view.grid_info()) if old_view else {'row':1,'column':5}
        if old_view: old_view.grid_remove()
        for k in ('in','rowspan','columnspan'): view_grid.pop(k,None)
        self._view_combo=ColorMenuSelect(top,self.view,width=20,command=self._view_changed)
        self._view_combo.grid(**view_grid)
        self.heatmap_title=ttk.Label(top,text='Filtre carte thermique',compound='left');self.heatmap_title.grid(row=0,column=12,sticky='w',padx=(8,0))
        self.heatmap_var=tk.StringVar(value='Arbres')
        self.heatmap_combo=ColorMenuSelect(top,self.heatmap_var,width=26,command=self._heatmap_changed)
        self.heatmap_combo.grid(row=1,column=12,padx=(8,3))
        self._lock_closed_icon=_selector_icon(self,'#d84a3a','lock_closed',18)
        self._lock_open_icon=_selector_icon(self,'#2ca85a','lock_open',18)
        # Give translated native comboboxes enough room without abbreviating labels.
        self.mode_combo.configure(width=max(int(self.mode_combo.cget('width')),20))
        self.arch_combo.configure(width=max(int(self.arch_combo.cget('width')),18))
        ttk.Button(top,text='Recentrer',command=self._reset_view).grid(row=1,column=13,padx=3)
        ttk.Button(top,text='Copier seed',command=self._copy_seed).grid(row=1,column=14,padx=3)
        ttk.Label(top,text='Langue').grid(row=0,column=15,sticky='w',padx=(8,0))
        self.lang_var=tk.StringVar(value=LANGUAGE_LABELS[self.prefs.get('language','fr')])
        self.lang_combo=ColorMenuSelect(top,self.lang_var,width=11,command=self._language_changed)
        self.lang_combo.set_items([('fr',LANGUAGE_LABELS['fr'],'#0055a4','flag_fr'),('en',LANGUAGE_LABELS['en'],'#21468b','flag_en')])
        self.lang_combo.grid(row=1,column=15,padx=(8,3))
        ttk.Button(top,text='Aide',command=self._show_help).grid(row=1,column=16,padx=3)
        self._theme_button=ttk.Button(top,command=self._toggle_theme,width=3)
        self._theme_button.grid(row=1,column=17,padx=(5,3))
        self._refresh_theme_button_icon()
        self.inspector_var=tk.StringVar(value='Inspecteur : —')
        ttk.Label(top,textvariable=self.inspector_var,anchor='w').grid(row=4,column=0,columnspan=18,sticky='ew',pady=(3,1))
        self.session_box=ttk.LabelFrame(top,text='Session / Comparaison',padding=(6,4));self.session_box.grid(row=5,column=0,columnspan=18,sticky='ew',pady=(5,2));self.session_box.columnconfigure(1,weight=1)
        ttk.Label(self.session_box,text='Historique session').grid(row=0,column=0,sticky='w')
        self.history_var=tk.StringVar(value='');self.history_combo=ttk.Combobox(self.session_box,textvariable=self.history_var,state='readonly',width=52)
        self.history_combo.grid(row=0,column=1,sticky='ew',padx=(6,3))
        ttk.Button(self.session_box,text='Charger',command=self._load_history).grid(row=0,column=2,padx=3)
        ttk.Button(self.session_box,text='Vider cache',command=self._clear_history).grid(row=0,column=3,padx=3)
        ttk.Button(self.session_box,text='Définir A',command=lambda:self._set_compare_slot('A')).grid(row=0,column=4,padx=3)
        ttk.Button(self.session_box,text='Définir B',command=lambda:self._set_compare_slot('B')).grid(row=0,column=5,padx=3)
        ttk.Button(self.session_box,text='Basculer A/B',command=self._toggle_compare).grid(row=0,column=6,padx=3)
        self.compare_var=tk.StringVar(value='A: —   |   B: —');ttk.Label(self.session_box,textvariable=self.compare_var,anchor='w').grid(row=1,column=0,columnspan=7,sticky='ew',pady=(3,0))
        self.canvas.bind('<Motion>',self._inspect_motion,add='+');self.canvas.bind('<Leave>',lambda e:self._clear_inspector(),add='+')
        self._build_stats_charts_tab()
        self._shortcut_settings_tab()
        self._reorder_analysis_tabs()
        self._theme_combo=self._find_combo_for_var(self.theme_var);self._projection_combo=self._find_combo_for_var(self.projection_var)
        self._capture_translatable_widgets()

    def _reorder_analysis_tabs(self):
        """Keep Statistics + Charts together, then Settings + Shortcuts."""
        tabs=list(self.nb.tabs())
        chart=next((t for t in tabs if self.nb.tab(t,'text')=='Graphiques'),None)
        settings=next((t for t in tabs if self.nb.tab(t,'text')=='Paramètres'),None)
        if chart and settings:
            self.nb.insert(self.nb.index(settings),chart)

    def _refresh_theme_button_icon(self):
        if not hasattr(self,'_theme_button'):return
        # Small deterministic raster icon: show the action (sun in dark mode, moon in light mode).
        dark=self.prefs.get('theme','dark')=='dark'
        im=Image.new('RGBA',(20,20),(0,0,0,0));d=ImageDraw.Draw(im)
        if dark:
            c=(245,195,55,255);d.ellipse((6,6,14,14),fill=c)
            for x1,y1,x2,y2 in ((10,1,10,4),(10,16,10,19),(1,10,4,10),(16,10,19,10),(3,3,5,5),(15,15,17,17),(15,3,17,5),(3,15,5,17)):d.line((x1,y1,x2,y2),fill=c,width=2)
            tip='Passer au thème clair' if self.prefs.get('language','fr')=='fr' else 'Switch to light theme'
        else:
            c=(75,95,145,255);d.ellipse((4,3,16,17),fill=c);d.ellipse((8,1,18,13),fill=(0,0,0,0))
            tip='Passer au thème sombre' if self.prefs.get('language','fr')=='fr' else 'Switch to dark theme'
        self._theme_button_icon=ImageTk.PhotoImage(im);self._theme_button.configure(image=self._theme_button_icon,text='',takefocus=False)
        try:self._theme_button.configure(cursor='hand2')
        except tk.TclError:pass

    def _build_stats_charts_tab(self):
        frame=ttk.Frame(self.nb,padding=10);self.nb.add(frame,text='Graphiques')
        frame.columnconfigure(0,weight=1);frame.rowconfigure(1,weight=1)
        controls=ttk.Frame(frame);controls.grid(row=0,column=0,sticky='ew',pady=(0,8));controls.columnconfigure(1,weight=1)
        ttk.Label(controls,text='Graphiques').grid(row=0,column=0,sticky='w',padx=(0,8))
        self.stats_chart_var=tk.StringVar(value=CHART_LABELS[self.prefs.get('language','fr')]['terrain_families'])
        self.stats_chart_combo=ttk.Combobox(controls,textvariable=self.stats_chart_var,state='readonly',width=40)
        self.stats_chart_combo.grid(row=0,column=1,sticky='ew',padx=(0,8));self.stats_chart_combo.bind('<<ComboboxSelected>>',lambda e:self._refresh_stats_chart())
        ttk.Button(controls,text='Exporter JSON',command=self._export_stats_json).grid(row=0,column=2,padx=3)
        ttk.Button(controls,text='Exporter CSV',command=self._export_stats_csv).grid(row=0,column=3,padx=3)
        ttk.Button(controls,text='Exporter PNG',command=self._export_stats_chart).grid(row=0,column=4,padx=3)
        self.stats_chart_canvas=tk.Canvas(frame,highlightthickness=0,bg='#212225');self.stats_chart_canvas.grid(row=1,column=0,sticky='nsew')
        self.stats_chart_canvas.bind('<Configure>',lambda e:self._refresh_stats_chart(),add='+')
        self._stats_chart_photo=None
        self._refresh_stats_chart_labels()

    def _refresh_stats_chart_labels(self):
        if not hasattr(self,'stats_chart_combo'):return
        lang=self.prefs.get('language','fr');labels=CHART_LABELS[lang]
        current_key=self._stats_chart_key() if self.stats_chart_var.get() else 'terrain_families'
        self.stats_chart_combo.configure(values=[labels[k] for k in CHART_KEYS])
        self.stats_chart_var.set(labels.get(current_key,labels['terrain_families']))

    def _stats_chart_key(self):
        if not hasattr(self,'stats_chart_var'):return 'terrain_families'
        value=self.stats_chart_var.get()
        for lang_labels in CHART_LABELS.values():
            for key,label in lang_labels.items():
                if label==value:return key
        return 'terrain_families'

    def _ensure_stats_cache(self):
        if not self.current:return None
        state=self.current.state
        stats=self.session_stats_cache.get(state)
        if stats is None:
            if getattr(self,'_task_overlay',None) is not None:self._task_progress(82,'Calcul des statistiques…' if self.prefs.get('language','fr')=='fr' else 'Computing statistics…')
            stats=analyze_map(state)
            self.session_stats_cache.put(state,stats)
        return stats

    def _stats_for_output(self,out):
        if out is None:return None
        state=out.state
        stats=self.session_stats_cache.get(state)
        if stats is None:
            stats=analyze_map(state);self.session_stats_cache.put(state,stats)
        return stats

    def _compare_stats_pair(self):
        return (self._stats_for_output(self._compare_slots.get('A')), self._stats_for_output(self._compare_slots.get('B')))

    def _refresh_stats_chart(self):
        if not hasattr(self,'stats_chart_canvas'):return
        c=self.stats_chart_canvas;c.delete('all')
        stats=self._ensure_stats_cache()
        if not stats:
            c.create_text(20,20,text='—',anchor='nw',fill=getattr(self,'_ui_theme_colors',{}).get('fg','#e8eaed'));return
        try:
            w=max(420,int(c.winfo_width()));h=max(280,int(c.winfo_height()));lang=self.prefs.get('language','fr');dark=self.prefs.get('theme','dark')=='dark'
            im=render_stats_chart(stats,self._stats_chart_key(),lang=lang,dark=dark,width=w,height=h,compare_stats=self._compare_stats_pair())
            self._stats_chart_photo=ImageTk.PhotoImage(im);c.create_image(0,0,image=self._stats_chart_photo,anchor='nw')
        except Exception as exc:
            c.create_text(20,20,text=f'Chart error: {exc}',anchor='nw',fill=getattr(self,'_ui_theme_colors',{}).get('fg','#e8eaed'))

    def _export_stats_json(self):
        stats=self._ensure_stats_cache()
        if not stats:return
        path=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')],initialfile='map_stats.json')
        if path:Path(path).write_text(stats_json(stats),encoding='utf-8')

    def _export_stats_csv(self):
        stats=self._ensure_stats_cache()
        if not stats:return
        path=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')],initialfile='map_stats.csv')
        if path:Path(path).write_text(stats_csv(stats),encoding='utf-8-sig')

    def _export_stats_chart(self):
        stats=self._ensure_stats_cache()
        if not stats:return
        path=filedialog.asksaveasfilename(defaultextension='.png',filetypes=[('PNG','*.png')],initialfile=f"stats_{self._stats_chart_key()}.png")
        if not path:return
        w=max(900,int(self.stats_chart_canvas.winfo_width()));h=max(520,int(self.stats_chart_canvas.winfo_height()))
        im=render_stats_chart(stats,self._stats_chart_key(),lang=self.prefs.get('language','fr'),dark=self.prefs.get('theme','dark')=='dark',width=w,height=h,compare_stats=self._compare_stats_pair());im.save(path)

    def _populate_current(self,imported=False):
        # These panels are reports, not editors. Temporarily unlock them only while refreshing.
        report_widgets=[w for w in (getattr(self,'validation',None),getattr(self,'pipeline',None),getattr(self,'meta',None),getattr(self,'stats',None)) if w is not None]
        for w in report_widgets:w.configure(state='normal')
        super()._populate_current(imported=imported)
        stats=self._ensure_stats_cache();lang=self.prefs.get('language','fr')
        if stats and hasattr(self,'stats'):
            self.stats.delete('1.0','end');self.stats.insert('end',format_stats_report(stats,lang=lang))
        for w in report_widgets:w.configure(state='disabled')
        self._refresh_stats_chart()

    def _walk(self,root):
        for child in root.winfo_children():
            yield child;yield from self._walk(child)
    def _find_combo_for_var(self,var):
        target=str(var)
        for w in self._walk(self):
            if isinstance(w,ttk.Combobox):
                try:
                    if str(w.cget('textvariable'))==target:return w
                except tk.TclError:pass
        return None

    def _shortcut_settings_tab(self):
        f=ttk.Frame(self.nb,padding=14);self.nb.add(f,text='Raccourcis');f.columnconfigure(1,weight=1)
        self.shortcut_vars={};self.shortcut_labels={};self.shortcut_reset_buttons={};lang=self.prefs.get('language','fr')
        for row,cmd in enumerate(DEFAULT_SHORTCUTS):
            lbl=ttk.Label(f,text=COMMAND_LABELS[lang][cmd]);lbl.grid(row=row,column=0,sticky='w',pady=4);self.shortcut_labels[cmd]=lbl
            var=tk.StringVar(value=self.prefs.get('shortcuts',{}).get(cmd,DEFAULT_SHORTCUTS[cmd]));self.shortcut_vars[cmd]=var
            ttk.Entry(f,textvariable=var,width=24).grid(row=row,column=1,sticky='ew',padx=(10,8),pady=4)
            btn=ttk.Button(f,text='Réinitialiser',command=lambda c=cmd:self._reset_one_shortcut(c));btn.grid(row=row,column=2,sticky='e',pady=4);self.shortcut_reset_buttons[cmd]=btn
        r=len(DEFAULT_SHORTCUTS)
        ttk.Button(f,text='Appliquer',command=self._apply_shortcut_settings).grid(row=r,column=0,pady=(12,0),sticky='w')
        ttk.Button(f,text='Valeurs par défaut',command=self._reset_shortcut_settings).grid(row=r,column=1,pady=(12,0),sticky='w',padx=(10,0))
        ttk.Label(f,text='Format : Ctrl+G, Ctrl+Shift+C, Alt+1, F1…').grid(row=r+1,column=0,columnspan=3,sticky='w',pady=(8,0))

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
    def _apply_language(self):
        if not hasattr(self,'lang_var'):return
        lang=self.prefs.get('language','fr');vk=self._view_key();hk=self._heatmap_key();mk=self._mode_key();ak=self._arch_key()
        for w,source in getattr(self,'_i18n_widgets',[]):
            try:w.configure(text=source if lang=='fr' else TEXTS[source].get('en',source))
            except tk.TclError:pass
        for tab,source in getattr(self,'_i18n_tabs',[]):self.nb.tab(tab,text=source if lang=='fr' else TEXTS[source].get('en',source))
        if self._view_combo:
            self._view_combo.set_items([(k,VIEW_LABELS[lang][k],VIEW_ICON_COLORS[k],k) for k in VIEW_LABELS[lang]])
        self.view.set(VIEW_LABELS[lang][vk]);self._view_combo._sync_icon()
        self.heatmap_combo.set_items([(k,HEATMAP_LABELS[lang][k],HEATMAP_ICON_COLORS[k],'dot') for k in HEATMAP_LABELS[lang]])
        self.heatmap_var.set(HEATMAP_LABELS[lang][hk]);self.heatmap_combo._sync_icon()
        self.mode_combo.configure(values=[MODE_LABELS[lang][k] for k in MODE_ORDER]);self.mode.set(MODE_LABELS[lang][mk])
        self.arch_combo.configure(values=[ARCHETYPE_LABELS[lang][k] for k in ARCHETYPE_ORDER]);self.arch.set(ARCHETYPE_LABELS[lang][ak])
        if self._theme_combo:self._theme_combo.configure(values=list(THEME_LABELS[lang].values()))
        self.theme_var.set(THEME_LABELS[lang][self.prefs['theme']])
        if self._projection_combo:self._projection_combo.configure(values=list(PROJECTION_LABELS[lang].values()))
        self.projection_var.set(PROJECTION_LABELS[lang][self.prefs['projection']])
        self.lang_var.set(LANGUAGE_LABELS[lang]);self.lang_combo._sync_icon()
        self._refresh_stats_chart_labels()
        if getattr(self,'current',None) and getattr(self,'stats',None):
            st=self._ensure_stats_cache();self.stats.delete('1.0','end');self.stats.insert('end',format_stats_report(st,lang=lang))
        self._refresh_stats_chart()
        for cmd,lbl in getattr(self,'shortcut_labels',{}).items():lbl.configure(text=COMMAND_LABELS[lang][cmd])
        for btn in getattr(self,'shortcut_reset_buttons',{}).values():btn.configure(text='Réinitialiser' if lang=='fr' else 'Reset')
        self._update_view_controls();self._clear_inspector()
    def _language_changed(self):
        self.prefs['language']='en' if self.lang_var.get()=='English' else 'fr';self._save_prefs();self._apply_language();self._invalidate_preview();self._refresh_preview(True)
    def _apply_theme(self):
        super()._apply_theme();dark=self.prefs.get('theme')=='dark';style=ttk.Style(self)
        field='#303134' if dark else '#ffffff';fg='#e8eaed' if dark else '#202124';muted='#7f858d' if dark else '#8a8f98';panel='#292a2d' if dark else '#e5e5e5'
        self._ui_theme_colors={'field':field,'fg':fg,'muted':muted,'panel':panel,'bar_bg':'#3c4043' if dark else '#dddddd','bar_fg':'#35a853','dark':dark}
        style.configure('ImageSelect.TMenubutton',background=field,foreground=fg)
        style.map('ImageSelect.TMenubutton',background=[('active',panel),('pressed',panel)],foreground=[('active',fg),('pressed',fg)])
        style.configure('Locked.TCombobox',fieldbackground=field,background=field,foreground=muted,selectforeground=muted)
        style.map('Locked.TCombobox',fieldbackground=[('disabled',field)],background=[('disabled',field)],foreground=[('disabled',muted)])
        # Option DB helps comboboxes created after the theme switch; direct popdown
        # styling below also fixes listboxes which Tk has already instantiated.
        self.option_add('*TCombobox*Listbox.background',field,'interactive');self.option_add('*TCombobox*Listbox.foreground',fg,'interactive')
        self.option_add('*TCombobox*Listbox.selectBackground',panel,'interactive');self.option_add('*TCombobox*Listbox.selectForeground',fg,'interactive')
        self._style_combobox_popdowns(field,fg,panel)
        for selector in (getattr(self,'_view_combo',None),getattr(self,'heatmap_combo',None),getattr(self,'lang_combo',None)):
            if isinstance(selector,ColorMenuSelect):selector.set_menu_theme(field,fg,panel,fg)
        if self._task_dialog is not None and hasattr(self,'_task_dialog_progress'):
            try:self._task_dialog_progress.configure(bg=self._ui_theme_colors['bar_bg'])
            except tk.TclError:pass
        if self._task_overlay is not None:
            try:
                self._task_overlay.configure(bg=panel)
                self._task_overlay_title.configure(bg=panel,fg=fg)
                self._task_overlay_progress.configure(bg=self._ui_theme_colors['bar_bg'])
                self._draw_task_progress(self._task_overlay_value)
            except tk.TclError:pass
        if hasattr(self,'heatmap_combo'):self._update_view_controls()
        if hasattr(self,'stats_chart_canvas'):
            self.stats_chart_canvas.configure(bg=panel);self._refresh_stats_chart()

    def _style_combobox_popdowns(self,field,fg,panel):
        for combo in self._walk(self):
            if not isinstance(combo,ttk.Combobox):continue
            try:
                pop=self.tk.call('ttk::combobox::PopdownWindow',str(combo))
                lb=pop+'.f.l'
                self.tk.call(lb,'configure','-background',field,'-foreground',fg,'-selectbackground',panel,'-selectforeground',fg)
            except tk.TclError:
                pass

    def _task_overlay_dimensions(self):
        """Responsive overlay dimensions relative to the visible map viewport."""
        try:
            self.canvas.update_idletasks()
            cw=max(1,int(self.canvas.winfo_width()))
        except tk.TclError:
            cw=720
        # Keep comfortable margins on small windows, but do not make the panel
        # absurdly wide on large monitors.
        width=max(300,min(680,int(cw*0.52)))
        width=min(width,max(220,cw-36))
        return width,86

    def _fit_progress_detail(self,text,max_px):
        """Elide a technical status string only when it cannot fit inside the bar."""
        text=str(text or '')
        try:
            import tkinter.font as tkfont
            font=tkfont.nametofont('TkDefaultFont')
            if font.measure(text)<=max_px:return text
            ell='…'; budget=max(20,max_px-font.measure(ell))
            left='';right='';li=0;ri=len(text)-1;turn=True
            while li<=ri:
                if turn:
                    cand=left+text[li]
                    if font.measure(cand)+font.measure(right)>budget:break
                    left=cand;li+=1
                else:
                    cand=text[ri]+right
                    if font.measure(left)+font.measure(cand)>budget:break
                    right=cand;ri-=1
                turn=not turn
            return left+ell+right
        except Exception:
            return text

    def _draw_task_progress(self,value,detail=None):
        if self._task_overlay is None or not hasattr(self,'_task_overlay_progress'):return
        value=max(0,min(100,float(value)));self._task_overlay_value=value
        if detail is not None:self._task_overlay_detail=str(detail)
        c=self._task_overlay_progress
        try:c.update_idletasks()
        except tk.TclError:return
        c.delete('all');w=max(1,int(c.winfo_width()));h=max(1,int(c.winfo_height()))
        colors=getattr(self,'_ui_theme_colors',{})
        bg=colors.get('bar_bg','#3c4043');fg=colors.get('bar_fg','#35a853');text_color=colors.get('fg','#e8eaed')
        c.configure(bg=bg,highlightthickness=0)
        if value>0:c.create_rectangle(0,0,max(1,round(w*value/100.0)),h,fill=fg,outline='')
        shown=self._fit_progress_detail(self._task_overlay_detail,max(40,w-18))
        # Keep the halo only in dark mode. In the light theme the same dark
        # text plus a dark outline makes the glyphs look artificially bold.
        cx,cy=w//2,h//2
        if colors.get('dark',False):
            for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)):
                c.create_text(cx+dx,cy+dy,text=shown,fill='#151719',anchor='center')
        c.create_text(cx,cy,text=shown,fill=text_color,anchor='center')

    def _layout_task_overlay(self,event=None):
        if self._task_overlay is None:return
        try:
            width,height=self._task_overlay_dimensions()
            self._task_overlay.place_configure(relx=.5,rely=.5,anchor='center',width=width,height=height)
            self._task_overlay_title.configure(wraplength=max(180,width-28))
            self._task_overlay.update_idletasks()
            self._draw_task_progress(self._task_overlay_value)
            self._task_overlay.lift()
        except tk.TclError:pass

    def _task_begin(self,label,value=5):
        self.status.set(label)
        try:self.progress.grid_remove()
        except (AttributeError,tk.TclError):pass
        self._close_task_dialog()
        colors=getattr(self,'_ui_theme_colors',{})
        panel=colors.get('panel','#292a2d');fg=colors.get('fg','#e8eaed')
        overlay=tk.Frame(self.canvas,bg=panel,bd=1,relief='solid',highlightthickness=0)
        self._task_overlay=overlay
        title=label.strip() if label else ('Génération…' if self.prefs.get('language','fr')=='fr' else 'Generating…')
        self._task_overlay_title=tk.Label(overlay,text=title,bg=panel,fg=fg,anchor='center',justify='center')
        self._task_overlay_title.pack(fill='x',padx=14,pady=(11,7))
        self._task_overlay_progress=tk.Canvas(overlay,height=24,bg=colors.get('bar_bg','#3c4043'),highlightthickness=0,bd=0)
        self._task_overlay_progress.pack(fill='x',expand=True,padx=14,pady=(0,12))
        self._task_overlay_value=max(0,min(100,float(value)));self._task_overlay_detail='Initialisation…' if self.prefs.get('language','fr')=='fr' else 'Initializing…'
        self.canvas.bind('<Configure>',self._layout_task_overlay,add='+')
        self._layout_task_overlay();self._draw_task_progress(value,self._task_overlay_detail);self.update_idletasks()

    def _task_progress(self,value,label=None):
        if label:self.status.set(label)
        if self._task_overlay is not None:self._draw_task_progress(max(0,min(99,value)),label if label else None)
        self.update_idletasks()

    def _close_task_dialog(self):
        # Kept under the historical method name because generation/export call
        # sites already use it; RC_8 no longer creates a Toplevel dialog.
        if self._task_dialog is not None:
            try:self._task_dialog.grab_release();self._task_dialog.destroy()
            except tk.TclError:pass
            self._task_dialog=None
        if self._task_overlay is not None:
            try:self._task_overlay.destroy()
            except tk.TclError:pass
            self._task_overlay=None

    def _task_done(self,label=None):
        if label:self.status.set(label)
        if self._task_overlay is not None:
            self._draw_task_progress(100,label if label else None);self.update_idletasks()
        self._close_task_dialog()

    def _task_error(self,label='Erreur'):
        self.status.set(label);self._close_task_dialog();self.update_idletasks()

    def _save_prefs(self):
        save_settings({'theme':self.prefs['theme'],'overlay_alpha':int(self.opacity_var.get()),'projection':self.prefs['projection'],'wheel_zoom':float(self.wheel_var.get()),'language':self.prefs.get('language','fr'),'shortcuts':self.prefs.get('shortcuts',dict(DEFAULT_SHORTCUTS))})

    def _theme_changed(self):
        self.prefs['theme']=self._theme_key();self._save_prefs();self._apply_theme()
    def _toggle_theme(self):
        self.prefs['theme']='light' if self.prefs.get('theme')=='dark' else 'dark';self.theme_var.set(THEME_LABELS[self.prefs.get('language','fr')][self.prefs['theme']]);self._save_prefs();self._apply_theme();self._refresh_theme_button_icon();self._invalidate_preview();self._refresh_preview(False);self._refresh_stats_chart()
    def _projection_changed(self):
        self.prefs['projection']=self._projection_key();self._save_prefs();self._invalidate_preview();self._refresh_preview(True)

    def _update_view_controls(self):
        view=self._view_key();lang=self.prefs.get('language','fr')
        if hasattr(self,'opacity_scale'):self.opacity_scale.configure(state='disabled' if view=='global' else 'normal')
        if hasattr(self,'heatmap_combo'):
            locked=view!='heatmap';self.heatmap_combo.set_enabled(not locked)
            if hasattr(self,'heatmap_title'):self.heatmap_title.configure(text=('Filtre carte thermique' if lang=='fr' else 'Heatmap filter'),image=self._lock_closed_icon if locked else self._lock_open_icon)
    def _view_changed(self):self._invalidate_preview();self._update_view_controls();self._refresh_preview(True)
    def _heatmap_changed(self):self._invalidate_preview();self._refresh_preview(True)
    def _reset_view(self):self.zoom_var.set(1.0);self.zoom=1.0;self._invalidate_preview();self._refresh_preview(True)
    def _copy_seed(self):
        value=str(self.seed.get());self.clipboard_clear();self.clipboard_append(value);self.status.set(f'Seed copié : {value}' if self.prefs.get('language')=='fr' else f'Seed copied: {value}')

    def _cache_key(self):
        return GenerationCacheKey(seed=int(self.seed.get()),side=int(self.size.get()),players=int(self.players.get()),mode=self._mode_key(),archetype=self._arch_key(),modifiers=(),engine_revision='v1.5-stable')
    def _history_label(self,key):return f'{key.seed} · {key.side} · {key.players}P · {key.mode} · {key.archetype}'
    def _refresh_history(self):
        self._history_lookup={self._history_label(k):k for k,_ in self.session_cache.entries()};vals=list(self._history_lookup);self.history_combo.configure(values=vals)
        if vals and self.history_var.get() not in vals:self.history_var.set(vals[0])
    def generate(self):
        try:
            side=int(self.size.get())
            if side!=768:raise NotImplementedError(f'La génération {side}×{side} est réservée mais pas encore calibrée. Max joueurs={NATIVE_LIMITS[side]}.')
            key=self._cache_key();cached=self.session_cache.get(key);self.import_source=None
            if cached is not None:
                self.current=cached;self._populate_current();self._invalidate_preview();self._refresh_preview(True);self._refresh_history();self.status.set('Cache hit — résultat réutilisé immédiatement');return
            self._task_begin('Génération…',2);self.current=self.generator.generate(int(self.players.get()),int(self.seed.get()),mode=self._mode_key(),archetype=self._arch_key())
            self.session_cache.put(key,self.current);self._refresh_history();self._task_progress(97,'Finalisation de l’aperçu…');self._populate_current();self._invalidate_preview();self._refresh_preview(True);self._task_done(self.status.get())
        except Exception as e:
            import traceback;self._task_error();messagebox.showerror('MapGen',f'{e}\n\n{traceback.format_exc()}')
    def _load_history(self):
        key=self._history_lookup.get(self.history_var.get());out=self.session_cache.get(key) if key else None
        if out is not None:
            need_stats=self.session_stats_cache.get(out.state) is None
            if need_stats:self._task_begin('Chargement de l’historique…' if self.prefs.get('language','fr')=='fr' else 'Loading history…',10)
            self.current=out;self.import_source=None;self._populate_current();self._invalidate_preview();self._refresh_preview(True)
            if need_stats:self._task_done('Historique chargé' if self.prefs.get('language','fr')=='fr' else 'History loaded')
            else:self.status.set('Historique chargé' if self.prefs.get('language','fr')=='fr' else 'History loaded')
    def _clear_history(self):self.session_cache.clear();self.session_stats_cache.clear();self._history_lookup.clear();self.history_combo.configure(values=[]);self.history_var.set('');self.status.set('Caches de session vidés')
    def _set_compare_slot(self,slot):
        if not self.current:return
        need_stats=self.session_stats_cache.get(self.current.state) is None
        if need_stats:self._task_begin((f'Préparation comparaison {slot}…' if self.prefs.get('language','fr')=='fr' else f'Preparing comparison {slot}…'),10)
        self._compare_slots[slot]=self.current;self._compare_active=slot;self._stats_for_output(self.current);self._refresh_compare_label();self._refresh_stats_chart()
        if need_stats:self._task_done((f'Comparaison {slot} prête' if self.prefs.get('language','fr')=='fr' else f'Comparison {slot} ready'))
    def _output_label(self,out):
        if out is None:return '—'
        m=out.state.metadata;return f"{m.get('seed','import')}/{m.get('mode_key',m.get('mode','?'))}/{len(out.state.starts) or m.get('players',0)}P"
    def _refresh_compare_label(self):self.compare_var.set(f"A: {self._output_label(self._compare_slots['A'])}   |   B: {self._output_label(self._compare_slots['B'])}");self._refresh_stats_chart()
    def _toggle_compare(self):
        a,b=self._compare_slots['A'],self._compare_slots['B']
        if a is None or b is None:self.status.set('Définir A et B avant la bascule');return
        self._compare_active='B' if self._compare_active!='B' else 'A';self.current=self._compare_slots[self._compare_active];imported=bool(self.current.state.metadata.get('source_format'));self._populate_current(imported=imported);self._invalidate_preview();self._refresh_preview(False);self.status.set(f'Comparaison {self._compare_active}')

    def _render_options(self):
        view=self._view_key();return {'view':view,'overlay_alpha':100 if view=='global' else int(self.opacity_var.get()),'projection':self.prefs['projection'],'heatmap_resource':self._heatmap_key()}
    def _refresh_preview(self,reset_pan=False):
        self._zoom_after=None
        if not self.current:return
        self._update_view_controls();opts=self._render_options();key=(id(self.current.state),opts['view'],opts['overlay_alpha'],opts['projection'],opts['heatmap_resource'])
        if key!=self._preview_key:self._preview_base=render(self.current.state,labels=True,**opts);self._preview_key=key
        im=self._preview_base;cw=max(100,self.canvas.winfo_width());ch=max(100,self.canvas.winfo_height());factor=max(.05,min((cw-10)/im.width,(ch-10)/im.height)*self.zoom);new=(max(1,int(im.width*factor)),max(1,int(im.height*factor)))
        oldx=0 if reset_pan else self.canvas.xview()[0];oldy=0 if reset_pan else self.canvas.yview()[0];shown=im.resize(new,Image.Resampling.NEAREST);self.photo=ImageTk.PhotoImage(shown);self.canvas.delete('all');sw=max(cw,new[0]);sh=max(ch,new[1]);x=max(0,(cw-new[0])//2);y=max(0,(ch-new[1])//2);self.canvas.create_image(x,y,image=self.photo,anchor='nw');self.canvas.configure(scrollregion=(0,0,sw,sh));self.canvas.xview_moveto(oldx);self.canvas.yview_moveto(oldy)
        self._display_origin=(x,y);self._display_factor=new[0]/im.width;self._display_base_size=im.size

    def _source_cell_from_canvas(self,event):
        if not self.current or self._display_factor<=0:return None
        cx=self.canvas.canvasx(event.x);cy=self.canvas.canvasy(event.y);px=(cx-self._display_origin[0])/self._display_factor;py=(cy-self._display_origin[1])/self._display_factor;side=self.current.state.side
        if self.prefs.get('projection')=='parallelogram':
            y=int(py//2)
            if not 0<=y<side:return None
            shift=side-1-y;x=int((px-shift)//2)
        else:x=int(px);y=int(py)
        return (x,y) if 0<=x<side and 0<=y<side else None
    def _resource_text(self,terrain,raw):
        fam=int(raw)&0xf0;qty=int(raw)&0x0f
        if qty<=0:return '—'
        if int(terrain) in range(8) and fam==0:return f'Fish {qty}'
        return f'{MINERAL_NAMES.get(fam,hex(fam))} {qty}'
    def _inspect_motion(self,event):
        cell=self._source_cell_from_canvas(event)
        if cell is None:return self._clear_inspector()
        x,y=cell;st=self.current.state;t=int(st.terrain[y,x]);o=int(st.objects[y,x]);r=int(st.resources[y,x]);h=int(st.height[y,x]);a=int(st.accessibility[y,x]);c=int(st.claim[y,x]);claim='—' if c==255 else f'P{c+1}'
        oname=OBJECT_NAMES.get(o,'—' if o==0 else '?');lang=self.prefs.get('language','fr')
        if lang=='fr':self.inspector_var.set(f'x={x}  y={y}  Terrain={t} ({TERRAIN_NAMES.get(t,"?")})  Objet={o} ({oname})  Ressource={self._resource_text(t,r)}  Hauteur={h}  Accès={a}  Territoire={claim}')
        else:self.inspector_var.set(f'x={x}  y={y}  Terrain={t} ({TERRAIN_NAMES.get(t,"?")})  Object={o} ({oname})  Resource={self._resource_text(t,r)}  Height={h}  Access={a}  Claim={claim}')
    def _clear_inspector(self):
        if hasattr(self,'inspector_var'):self.inspector_var.set('Inspecteur : —' if self.prefs.get('language','fr')=='fr' else 'Inspector: —')

    @staticmethod
    def _tk_sequence(shortcut):
        text=shortcut.strip();parts=[p.strip() for p in text.split('+') if p.strip()]
        if not parts:return None
        key=parts[-1];mods=[]
        for p in parts[:-1]:
            q=p.lower();mods.append({'ctrl':'Control','control':'Control','shift':'Shift','alt':'Alt'}.get(q,p))
        if key.upper().startswith('F') and key[1:].isdigit():key=key.upper()
        elif len(key)==1:
            # Tk reports shifted letters as uppercase keysyms on Windows.  Using
            # lowercase here made Ctrl+Shift+T/C unreliable (notably on AZERTY).
            key=key.upper() if 'Shift' in mods else key.lower()
        return '<'+'-'.join(mods+[key])+'>'
    def _bind_shortcuts(self):
        for seq in self._bound_shortcuts:
            try:self.unbind_all(seq)
            except tk.TclError:pass
        self._bound_shortcuts=[]
        actions={'generate':self.generate,'import':self.import_file,'export':self.export,'reset_view':self._reset_view,'copy_seed':self._copy_seed,'toggle_ab':self._toggle_compare,'toggle_theme':self._toggle_theme,'help':self._show_help}
        for cmd,shortcut in self.prefs.get('shortcuts',DEFAULT_SHORTCUTS).items():
            seq=self._tk_sequence(shortcut)
            if seq and cmd in actions:
                self.bind_all(seq,lambda e,fn=actions[cmd]:(fn(),'break')[1]);self._bound_shortcuts.append(seq)
    def _apply_shortcut_settings(self):
        vals={k:v.get().strip() for k,v in self.shortcut_vars.items()};norm=[v.lower().replace(' ','') for v in vals.values()]
        if any(not v for v in vals.values()):messagebox.showerror('Raccourcis','Un raccourci ne peut pas être vide.');return
        dups=sorted({v for v in norm if norm.count(v)>1})
        if dups:messagebox.showerror('Raccourcis','Conflit détecté : '+', '.join(dups));return
        if any(self._tk_sequence(v) is None for v in vals.values()):messagebox.showerror('Raccourcis','Format de raccourci invalide.');return
        self.prefs['shortcuts']=vals;self._save_prefs();self._bind_shortcuts();self.status.set('Raccourcis appliqués')
    def _reset_one_shortcut(self,cmd):
        self.shortcut_vars[cmd].set(DEFAULT_SHORTCUTS[cmd]);self._apply_shortcut_settings()
    def _reset_shortcut_settings(self):
        for k,v in DEFAULT_SHORTCUTS.items():self.shortcut_vars[k].set(v)
        self.prefs['shortcuts']=dict(DEFAULT_SHORTCUTS);self._save_prefs();self._bind_shortcuts();self.status.set('Raccourcis restaurés')
    def _show_help(self):
        sc=self.prefs.get('shortcuts',DEFAULT_SHORTCUTS);lang=self.prefs.get('language','fr');lines=[]
        for cmd in DEFAULT_SHORTCUTS:lines.append(f"{COMMAND_LABELS[lang][cmd]} : {sc.get(cmd,DEFAULT_SHORTCUTS[cmd])}")
        extra='\n\nMolette : zoom\nClic gauche + glisser : déplacer\nCache : 8 générations, mémoire de session uniquement.\nA/B : conserve vue, zoom, projection et overlay.' if lang=='fr' else '\n\nWheel: zoom\nLeft drag: pan\nCache: 8 generations, session memory only.\nA/B preserves view, zoom, projection and overlay.'
        messagebox.showinfo('Aide / Help','\n'.join(lines)+extra)

    def export(self):
        if not self.current:return
        folder=filedialog.askdirectory(title='Dossier de sortie')
        if not folder:return
        try:
            folder=Path(folder);st=self.current.state;side=st.side;self._task_begin('Export…',5)
            base=(f"S3_{st.metadata.get('archetype','Imported')}_{st.metadata.get('mode','Map')}_{len(st.starts) or st.metadata.get('players',0)}P_{side}x{side}_seed_{st.metadata.get('seed','import')}_MapGenV1_6").replace(' ','');made=[]
            if side==768:
                edm=folder/(base+'.edm');mp=folder/('1-'+base+'.map');export_with_scaffold(st,EDM_SCAFFOLD,edm);self._task_progress(35,'Export MAP…');export_with_scaffold(st,MAP_SCAFFOLD,mp);made += [edm.name,mp.name]
            else:made.append('EDM/MAP non réécrits : aucun scaffold validé pour cette taille.')
            self._task_progress(62,'Export SAV/aperçu…')
            if self.import_source and self.import_source.suffix.lower()=='.sav':sv=folder/(base+'.sav');shutil.copy2(self.import_source,sv);made.append(sv.name+' (copie SAV inchangée)')
            else:made.append('SAV non exporté : writer SAV volontairement non implémenté/validé.')
            png=folder/(base+'_preview.png');render(st,png,**self._render_options());made.append(png.name);self._task_done('Export terminé');messagebox.showinfo('Export','\n'.join(made))
        except Exception as e:self._task_error('Erreur export');messagebox.showerror('Export',f'{e}')

def main():App().mainloop()
