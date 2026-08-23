from __future__ import annotations
import random
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
from .preview import render, render_square_base, compose_rendered_map, compose_start_markers, project_parallelogram, HEATMAP_RESOURCES
from .preferences import save_settings, DEFAULT_SHORTCUTS
from .app_paths import EDM_SCAFFOLD, MAP_SCAFFOLD, OUTPUT
from .session_cache import GenerationCacheKey, SessionGenerationCache, SessionStatsCache
from .stats_analysis import analyze_map, format_stats_report, stats_json, stats_csv
from .stats_charts import render_stats_chart, CHART_KEYS, CHART_LABELS
from .export_center import safe_export_basename, map_export_capabilities, map_export_paths, stats_export_paths, existing_export_paths

VIEWS.clear()
VIEWS.update({'Global':'global','Départs':'starts','Territoires':'territories','Élévation':'heightmap','Ressources':'resources','Chemins':'paths','Cultures':'crops','Carte thermique':'heatmap'})

VIEW_LABELS={
 'fr':{'global':'Global','starts':'Départs','territories':'Territoires','heightmap':'Élévation','resources':'Ressources','paths':'Chemins','crops':'Cultures','heatmap':'Carte thermique'},
 'en':{'global':'Global','starts':'Starts','territories':'Territories','heightmap':'Elevation','resources':'Resources','paths':'Paths','crops':'Crops','heatmap':'Heatmap'},
}
LANGUAGE_LABELS={'fr':'Français','en':'English'}
WINDOW_TITLES={
 'fr':'Settlers III MapGen v1.8 DEV_5_R3 — moteur de génération v1.5',
 'en':'Settlers III MapGen v1.8 DEV_5_R3 — generation engine v1.5',
}

FEEDBACK_TEXT={
 'fr':{
  'ready':'Prêt — {mode} / {archetype} / modificateurs : {modifiers} / {side}×{side} / {players} joueurs.',
  'size_reserved':'{side}×{side} : max {max_players} joueurs. Sélection prête, génération pas encore calibrée.',
  'mode_reserved':'Mode « {mode} » réservé, non implémenté.',
  'arch_reserved':'Archétype « {archetype} » réservé, non implémenté.',
  'generating':'Génération de {archetype} — {mode} — modificateurs : {modifiers} — {side}×{side} — {players} joueurs — seed {seed}…',
  'generated':'Carte générée — {archetype} / {mode} / modificateurs : {modifiers} / {side}×{side} / {players} joueurs / seed {seed}.',
  'cache_hit':'Résultat réutilisé depuis le cache — seed {seed}.',
  'heatmap_locked':'Le filtre est disponible lorsque la vue « Carte thermique » est sélectionnée.',
  'history_loaded':'Carte chargée depuis l’historique.',
  'history_cleared':'Caches de session vidés.',
  'shortcut_applied':'Raccourcis appliqués.',
  'shortcut_restored':'Raccourcis restaurés aux valeurs par défaut.',
  'seed_copied':'Seed copié : {seed}',
  'export_done':'Export terminé.',
  'history_empty':'Aucune carte disponible dans le cache de session.',
  'compare_toggled':'Carte basculée vers {map}.',
  'theme_changed':'Thème changé : {theme}.',
  'view_reset':'Vue recentrée.',
  'seed_randomized':'Nouveau seed aléatoire : {seed}',
  'graph_exported':'Export graphique terminé : {format} — {file}',
  'opacity_locked':'L’opacité n’est pas disponible dans la vue Global.',
  'modifier_none':'Aucun modificateur actif.',
  'batch_opened':'Génération par lot prête — configurez de 1 à 4 cartes.',
  'batch_done':'Lot terminé — {success} réussie(s), {failed} erreur(s), {cancelled} annulée(s).',
 },
 'en':{
  'ready':'Ready — {mode} / {archetype} / modifiers: {modifiers} / {side}×{side} / {players} players.',
  'size_reserved':'{side}×{side}: max {max_players} players. Selection ready; generation is not calibrated yet.',
  'mode_reserved':'Mode “{mode}” is reserved and not implemented.',
  'arch_reserved':'Archetype “{archetype}” is reserved and not implemented.',
  'generating':'Generating {archetype} — {mode} — modifiers: {modifiers} — {side}×{side} — {players} players — seed {seed}…',
  'generated':'Map generated — {archetype} / {mode} / modifiers: {modifiers} / {side}×{side} / {players} players / seed {seed}.',
  'cache_hit':'Result reused from cache — seed {seed}.',
  'heatmap_locked':'The filter is available when the “Heatmap” view is selected.',
  'history_loaded':'Map loaded from session history.',
  'history_cleared':'Session caches cleared.',
  'shortcut_applied':'Shortcuts applied.',
  'shortcut_restored':'Shortcuts restored to defaults.',
  'seed_copied':'Seed copied: {seed}',
  'export_done':'Export complete.',
  'history_empty':'No map is available in the session cache.',
  'compare_toggled':'Map switched to {map}.',
  'theme_changed':'Theme changed: {theme}.',
  'view_reset':'View recentered.',
  'seed_randomized':'New random seed: {seed}',
  'graph_exported':'Chart export complete: {format} — {file}',
  'opacity_locked':'Opacity is not available in the Global view.',
  'modifier_none':'No modifier is active.',
  'batch_opened':'Batch generation ready — configure 1 to 4 maps.',
  'batch_done':'Batch complete — {success} succeeded, {failed} failed, {cancelled} cancelled.',
 },
}

BATCH_TEXT={
 'fr':{
  'title':'Génération par lot','count':'Nombre de cartes','randomize':'Nouvelles seeds','apply_seed':'Appliquer à toutes',
  'map':'Carte {index}','mode':'Mode','archetype':'Archétype','modifiers':'Modificateurs','size':'Taille',
  'players':'Joueurs','seed':'Seed','status':'État','waiting':'En attente','generating':'Génération…',
  'cached':'Réutilisée depuis le cache','success':'Terminée','failed':'Erreur : {error}','cancelled':'Annulée',
  'start':'Générer le lot','cancel':'Annuler les cartes en attente','close':'Fermer','set_a':'Affecter à A',
  'set_b':'Affecter à B','show':'Afficher','none':'Aucun','invalid_title':'Paramètres du lot invalides',
  'invalid_row':'Carte {index} : {error}','unsupported_size':'seule la taille 768×768 est actuellement générable',
  'unsupported_mode':'mode non implémenté','unsupported_archetype':'archétype non implémenté',
  'invalid_players':'nombre de joueurs invalide (2 à {maximum})','invalid_seed':'seed entière requise',
  'running':'Lot en cours : carte {current}/{total}','cancel_pending':'Annulation demandée après la carte en cours.',
  'finished':'Lot terminé : {success} réussie(s), {failed} erreur(s), {cancelled} annulée(s).',
  'assigned':'Carte {index} affectée à {slot}.','moved':'Carte {index} déplacée de {other} vers {slot}.','already_assigned':'Carte {index} déjà affectée à {slot}.',
  'preview_hint':'Cliquez ou laissez la souris 700 ms pour agrandir.','close_preview':'Fermer l’aperçu','close_running':'Le lot est en cours ; les cartes en attente seront annulées.',
 },
 'en':{
  'title':'Batch generation','count':'Number of maps','randomize':'New seeds','apply_seed':'Apply to all',
  'map':'Map {index}','mode':'Mode','archetype':'Archetype','modifiers':'Modifiers','size':'Size',
  'players':'Players','seed':'Seed','status':'Status','waiting':'Waiting','generating':'Generating…',
  'cached':'Reused from cache','success':'Complete','failed':'Error: {error}','cancelled':'Cancelled',
  'start':'Generate batch','cancel':'Cancel pending maps','close':'Close','set_a':'Assign to A',
  'set_b':'Assign to B','show':'Show','none':'None','invalid_title':'Invalid batch parameters',
  'invalid_row':'Map {index}: {error}','unsupported_size':'only 768×768 generation is currently available',
  'unsupported_mode':'mode is not implemented','unsupported_archetype':'archetype is not implemented',
  'invalid_players':'invalid player count (2 to {maximum})','invalid_seed':'an integer seed is required',
  'running':'Batch running: map {current}/{total}','cancel_pending':'Cancellation requested after the current map.',
  'finished':'Batch complete: {success} succeeded, {failed} failed, {cancelled} cancelled.',
  'assigned':'Map {index} assigned to {slot}.','moved':'Map {index} moved from {other} to {slot}.','already_assigned':'Map {index} is already assigned to {slot}.',
  'preview_hint':'Click or hover for 700 ms to enlarge.','close_preview':'Close preview','close_running':'The batch is running; pending maps will be cancelled.',
 },
}

HEATMAP_LABELS={
 'fr':{'trees':'Arbres','building_stones':'Pierres de construction','fish':'Poissons','coal':'Charbon','iron':'Fer','gold':'Or','gems':'Gemmes','sulfur':'Soufre'},
 'en':{'trees':'Trees','building_stones':'Building Stones','fish':'Fish','coal':'Coal','iron':'Iron','gold':'Gold','gems':'Gemstones','sulfur':'Sulfur'},
}

# R5: real raster icons.  Unicode colored-circle emoji were rendered as monochrome
# glyphs by some Windows/Tk combinations, so the selectors now use tiny images
# drawn by Pillow and attached to Tk menu entries.
VIEW_ICON_COLORS={
 'global':'#2698e8','starts':'#cd1e10','heightmap':'#8f55d6','resources':'#ff9418','territories':'#31a354',
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
PREVIEW_START_MARKER_LABELS={
 'fr':{'hidden':'Masqués','small':'Petits','normal':'Normaux'},
 'en':{'hidden':'Hidden','small':'Small','normal':'Normal'},
}
TEXTS={
 'Mode':{'en':'Mode'},'Archétype':{'en':'Archetype'},'Modificateurs':{'en':'Modifiers'},'Taille':{'en':'Size'},'Joueurs':{'en':'Players'},'Seed':{'en':'Seed'},'Zoom':{'en':'Zoom'},
 'Générer':{'en':'Generate'},'Générer lot…':{'en':'Generate batch…'},'Importer…':{'en':'Import…'},'Exporter…':{'en':'Export…'},'Aperçu PNG':{'en':'PNG Preview'},'Vue':{'en':'View'},
 'Affichage':{'en':'Display'},'Thème':{'en':'Theme'},'Opacité couche':{'en':'Layer opacity'},'0 % = map globale · 100 % = couche seule':{'en':'0 % = global map · 100 % = overlay only'},
 'Projection':{'en':'Projection'},'Le parallélogramme modifie uniquement le rendu, jamais les données.':{'en':'Parallelogram changes rendering only, never map data.'},
 'Marqueurs dans les aperçus':{'en':'Markers in previews'},'Ce réglage affecte les miniatures et le grand aperçu du lot.':{'en':'This setting affects batch thumbnails and the large preview.'},
 'Sensibilité molette':{'en':'Mouse-wheel sensitivity'},'Navigation':{'en':'Navigation'},'Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.':{'en':'Mouse wheel: zoom\nLeft click + drag: move map\nZoom refresh is delayed to reduce recalculation.'},
 'Paramètres':{'en':'Settings'},'Validations':{'en':'Validations'},'Pipeline':{'en':'Pipeline'},'Métadonnées':{'en':'Metadata'},'Statistiques':{'en':'Statistics'},'Graphiques':{'en':'Charts'},'Exporter JSON':{'en':'Export JSON'},'Exporter CSV':{'en':'Export CSV'},'Exporter PNG':{'en':'Export PNG'},'Ressource Heatmap':{'en':'Heatmap resource'},'Filtre carte thermique':{'en':'Heatmap filter'},
 'Recentrer':{'en':'Reset view'},'Copier seed':{'en':'Copy seed'},'Langue':{'en':'Language'},'Aide':{'en':'Help'},'Historique session':{'en':'Session history'},
 'Charger':{'en':'Load'},'Vider cache':{'en':'Clear cache'},'Définir A':{'en':'Set A'},'Définir B':{'en':'Set B'},'Basculer A/B':{'en':'Toggle A/B'},
 'Vider A':{'en':'Clear A'},'Vider B':{'en':'Clear B'},'Vider A+B':{'en':'Clear A+B'},
 'Raccourcis':{'en':'Shortcuts'},'Appliquer':{'en':'Apply'},'Valeurs par défaut':{'en':'Defaults'},'Réinitialiser':{'en':'Reset'},
 'Session / Comparaison':{'en':'Session / Comparison'},'Format : Ctrl+G, Ctrl+Shift+C, Alt+1, F1…':{'en':'Format: Ctrl+G, Ctrl+Shift+C, Alt+1, F1…'},
}

EXPORT_TEXT={
 'fr':{
  'map_title':'Exporter la carte','stats_title':'Exporter les statistiques et le graphique','folder':'Dossier','browse':'Parcourir…','basename':'Nom de base','formats':'Formats','files':'Fichiers prévus','none':'Sélectionnez au moins un format.','cancel':'Annuler','export':'Exporter','overwrite_title':'Fichiers existants','overwrite':'Ces fichiers existent déjà :\n\n{files}\n\nLes remplacer ?','invalid_name':'Le nom de base est vide ou invalide.','invalid_folder':'Sélectionnez un dossier de sortie valide.','done':'Export terminé :\n\n{files}',
  'edm':'Carte éditeur (.EDM)','map':'Carte jouable (.MAP)','sav':'SAV source inchangé (.SAV)','png_global':'Carte globale, projection active (.PNG)','png_current':'Vue actuelle avec ses couches (.PNG)','json':'Statistiques complètes (.JSON)','csv':'Statistiques complètes (.CSV)','png':'Graphique actuellement affiché (.PNG)',
  'binary_unavailable':'EDM/MAP indisponibles : aucun scaffold validé pour cette taille.','sav_unavailable':'SAV indisponible : seule la copie inchangée d’un SAV importé est autorisée.','sav_exact':'Le SAV sera copié octet pour octet ; aucun writer SAV n’est utilisé.','current_unavailable':'Vue actuelle indisponible : avec Global, elle serait identique au PNG Global.','safe_name':'Les caractères incompatibles avec Windows sont remplacés par « _ ».',
 },
 'en':{
  'map_title':'Export map','stats_title':'Export statistics and chart','folder':'Folder','browse':'Browse…','basename':'Base name','formats':'Formats','files':'Planned files','none':'Select at least one format.','cancel':'Cancel','export':'Export','overwrite_title':'Existing files','overwrite':'These files already exist:\n\n{files}\n\nReplace them?','invalid_name':'The base name is empty or invalid.','invalid_folder':'Select a valid output folder.','done':'Export complete:\n\n{files}',
  'edm':'Editor map (.EDM)','map':'Playable map (.MAP)','sav':'Unchanged source SAV (.SAV)','png_global':'Global map, active projection (.PNG)','png_current':'Current view with its layers (.PNG)','json':'Complete statistics (.JSON)','csv':'Complete statistics (.CSV)','png':'Currently displayed chart (.PNG)',
  'binary_unavailable':'EDM/MAP unavailable: no validated scaffold exists for this size.','sav_unavailable':'SAV unavailable: only an unchanged copy of an imported SAV is allowed.','sav_exact':'The SAV is copied byte for byte; no SAV writer is used.','current_unavailable':'Current View unavailable: with Global selected, it would be identical to the Global PNG.','safe_name':'Characters incompatible with Windows are replaced with “_”.',
 },
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
    elif kind=='starts':
        d.ellipse((3,2,size-4,size-5),fill=c,outline='#111111',width=1);d.ellipse((7,6,size-8,size-9),fill='#fff2df')
        d.polygon(((size//2,size-2),(size//2-3,size-7),(size//2+3,size-7)),fill=c,outline='#111111')
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
    elif kind=='cross':
        # Deterministic delete mark with a dark outline for both application themes.
        d.line((3,3,size-4,size-4),fill='#111111',width=5);d.line((size-4,3,3,size-4),fill='#111111',width=5)
        d.line((3,3,size-4,size-4),fill=c,width=3);d.line((size-4,3,3,size-4),fill=c,width=3)
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
    """v1.8 UI/tooling shell running the unchanged validated v1.5 generator."""
    def __init__(self):
        self.session_cache=SessionGenerationCache(max_entries=8)
        self.session_stats_cache=SessionStatsCache(max_entries=12)
        self._history_lookup={};self._compare_slots={'A':None,'B':None};self._compare_active=None
        self._preview_layer_base=None;self._preview_layer_key=None;self._preview_projection_cache={};self._prefs_save_after=None
        self._display_origin=(0,0);self._display_factor=1.0;self._display_base_size=(1,1);self._bound_shortcuts=[];self._task_dialog=None;self._task_overlay=None;self._task_overlay_value=0;self._task_overlay_detail='';self._status_kind='ready';self._feedback_key=None;self._feedback_values={};self._responsive_mode=None;self._layout_after=None
        self._batch_window=None;self._batch_rows=[];self._batch_queue=[];self._batch_running=False;self._batch_cancel_requested=False;self._batch_active_row=None;self._batch_last_success=None;self._batch_active_count=0
        self._batch_preview_window=None;self._batch_preview_label=None;self._batch_preview_photo=None;self._batch_preview_row=None;self._batch_preview_pinned=False;self._batch_preview_projection=None;self._batch_preview_drag_origin=None;self._batch_hover_after=None;self._batch_i18n={}
        self._map_export_window=None;self._stats_export_window=None
        super().__init__()
        self._apply_initial_window_geometry();self._apply_language();self._bind_shortcuts();self.bind('<Configure>',self._schedule_responsive_layout,add='+');self.after_idle(self._apply_responsive_layout)

    def _settings_tab(self):
        """Build v1.8 display settings, including preview-only start markers."""
        f=ttk.Frame(self.nb,padding=14);self.nb.add(f,text='Paramètres');f.columnconfigure(1,weight=1)
        ttk.Label(f,text='Affichage',style='Section.TLabel').grid(row=0,column=0,columnspan=3,sticky='w',pady=(0,10))
        ttk.Label(f,text='Thème').grid(row=1,column=0,sticky='w',pady=6)
        lang=self.prefs.get('language','fr')
        self.theme_var=tk.StringVar(value=THEME_LABELS[lang][self.prefs['theme']])
        c=ttk.Combobox(f,textvariable=self.theme_var,values=list(THEME_LABELS[lang].values()),state='readonly');c.grid(row=1,column=1,sticky='ew');c.bind('<<ComboboxSelected>>',lambda e:self._theme_changed())
        ttk.Label(f,text='Opacité couche').grid(row=2,column=0,sticky='w',pady=(14,6))
        self.opacity_var=tk.DoubleVar(value=float(self.prefs['overlay_alpha']))
        self.opacity_scale=ttk.Scale(f,from_=0,to=100,variable=self.opacity_var,command=lambda v:self._opacity_changed());self.opacity_scale.grid(row=2,column=1,sticky='ew')
        self.opacity_label=ttk.Label(f,text=f"{int(self.opacity_var.get())} %",width=7);self.opacity_label.grid(row=2,column=2,padx=(8,0))
        ttk.Label(f,text='0 % = map globale · 100 % = couche seule',style='Hint.TLabel').grid(row=3,column=1,columnspan=2,sticky='w')
        ttk.Label(f,text='Projection').grid(row=4,column=0,sticky='w',pady=(14,6))
        self.projection_var=tk.StringVar(value=PROJECTION_LABELS[lang][self.prefs['projection']])
        c=ttk.Combobox(f,textvariable=self.projection_var,values=list(PROJECTION_LABELS[lang].values()),state='readonly');c.grid(row=4,column=1,sticky='ew');c.bind('<<ComboboxSelected>>',lambda e:self._projection_changed())
        ttk.Label(f,text='Le parallélogramme modifie uniquement le rendu, jamais les données.',style='Hint.TLabel',wraplength=360).grid(row=5,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Marqueurs dans les aperçus').grid(row=6,column=0,sticky='w',pady=(14,6))
        marker_key=self.prefs.get('preview_start_markers','small')
        self.preview_marker_var=tk.StringVar(value=PREVIEW_START_MARKER_LABELS[lang][marker_key])
        self.preview_marker_combo=ttk.Combobox(f,textvariable=self.preview_marker_var,values=list(PREVIEW_START_MARKER_LABELS[lang].values()),state='readonly')
        self.preview_marker_combo.grid(row=6,column=1,sticky='ew');self.preview_marker_combo.bind('<<ComboboxSelected>>',lambda e:self._preview_marker_changed())
        ttk.Label(f,text='Ce réglage affecte les miniatures et le grand aperçu du lot.',style='Hint.TLabel',wraplength=360).grid(row=7,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Sensibilité molette').grid(row=8,column=0,sticky='w',pady=(14,6))
        self.wheel_var=tk.DoubleVar(value=float(self.prefs['wheel_zoom']))
        self.wheel_scale=ttk.Scale(f,from_=1.04,to=1.20,variable=self.wheel_var,command=lambda v:self._wheel_changed());self.wheel_scale.grid(row=8,column=1,sticky='ew')
        self.wheel_label=ttk.Label(f,text=f"×{self.wheel_var.get():.2f}",width=7);self.wheel_label.grid(row=8,column=2,padx=(8,0))
        ttk.Separator(f).grid(row=9,column=0,columnspan=3,sticky='ew',pady=16)
        ttk.Label(f,text='Navigation',style='Section.TLabel').grid(row=10,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.',style='Hint.TLabel',justify='left').grid(row=11,column=0,columnspan=3,sticky='w',pady=(6,0))

    def _build(self):
        super()._build();top=self.winfo_children()[0]

        # R6 rebuilds the header as three independent functional regions.  Keep the
        # validated generation variables and hidden progress/status plumbing, but
        # discard the historical widget-by-widget grid inherited from v1.3.
        self._legacy_status_label=None
        for w in list(top.winfo_children()):
            if w is self.progress:
                w.grid_remove();continue
            try:
                if str(w.cget('textvariable'))==str(self.status):
                    self._legacy_status_label=w;w.grid_remove();continue
            except tk.TclError:pass
            w.destroy()

        # The inherited v1.3 header gave column 11 an elastic weight.  Once its
        # widgets are removed, that stale column would still absorb half the free
        # width and prevent the global region from reaching the right edge.
        for c in range(18):top.columnconfigure(c,weight=0,minsize=0)

        self._header_shell=ttk.Frame(top)
        self._header_shell.grid(row=0,column=0,sticky='ew')
        top.columnconfigure(0,weight=1)
        self.generation_panel=ttk.Frame(self._header_shell)
        self.global_panel=ttk.Frame(self._header_shell)

        def selector_group(parent,label):
            group=ttk.Frame(parent)
            ttk.Label(group,text=label).pack(anchor='w',pady=(0,2))
            return group

        # Generation row 1: selectors and their own independent action bar.
        primary_row=ttk.Frame(self.generation_panel);primary_row.pack(anchor='w',fill='x')
        mode_group=selector_group(primary_row,'Mode');mode_group.pack(side='left',padx=(0,5))
        self.mode_combo=ttk.Combobox(mode_group,textvariable=self.mode,values=[MODES[k].label for k in MODE_ORDER],state='readonly',width=20)
        self.mode_combo.pack();self.mode_combo.bind('<<ComboboxSelected>>',lambda e:self._selection_changed())
        arch_group=selector_group(primary_row,'Archétype');arch_group.pack(side='left',padx=(0,5))
        self.arch_combo=ttk.Combobox(arch_group,textvariable=self.arch,values=[ARCHETYPES[k].label for k in ARCHETYPE_ORDER],state='readonly',width=18)
        self.arch_combo.pack();self.arch_combo.bind('<<ComboboxSelected>>',lambda e:self._selection_changed())
        modifier_group=selector_group(primary_row,'Modificateurs');modifier_group.pack(side='left',padx=(0,7))
        self.modifier_label=modifier_group.winfo_children()[0]
        self.modifier_none=tk.BooleanVar(value=True);self.modifier_text=tk.StringVar(value='Aucun')
        self.modifier_button=ttk.Menubutton(modifier_group,textvariable=self.modifier_text,width=14,style='ImageSelect.TMenubutton')
        self.modifier_menu=tk.Menu(self.modifier_button,tearoff=False);self.modifier_button.configure(menu=self.modifier_menu)
        self.modifier_menu.add_checkbutton(label='Aucun',variable=self.modifier_none,command=self._modifier_none_selected)
        self.modifier_button.pack()
        primary_actions=ttk.Frame(primary_row);primary_actions.pack(side='left',fill='y')
        self.generate_button=ttk.Button(primary_actions,text='Générer',command=self.generate)
        self.generate_button.pack(side='left',anchor='s',padx=(0,4),pady=(19,0))
        self.batch_generate_button=ttk.Button(primary_actions,text='Générer lot…',command=self._open_batch_window)
        self.batch_generate_button.pack(side='left',anchor='s',padx=(0,0),pady=(19,0))

        # Generation row 2: dependent parameters followed by two local button bars.
        # Their spacing no longer depends on the selector columns above.
        secondary_row=ttk.Frame(self.generation_panel);secondary_row.pack(anchor='w',fill='x',pady=(5,0))
        size_group=selector_group(secondary_row,'Taille');size_group.pack(side='left',padx=(0,5))
        self.size_combo=ttk.Combobox(size_group,textvariable=self.size,values=[str(x) for x in NATIVE_LIMITS],state='readonly',width=8)
        self.size_combo.pack();self.size_combo.bind('<<ComboboxSelected>>',lambda e:self._size_changed())
        players_group=selector_group(secondary_row,'Joueurs');players_group.pack(side='left',padx=(0,5))
        self.players_spin=ttk.Spinbox(players_group,from_=2,to=20,textvariable=self.players,width=8);self.players_spin.pack()
        seed_group=selector_group(secondary_row,'Seed');seed_group.pack(side='left',padx=(0,7))
        self.seed_entry=ttk.Entry(seed_group,textvariable=self.seed,width=14);self.seed_entry.pack()
        seed_actions=ttk.Frame(secondary_row);seed_actions.pack(side='left',fill='y',padx=(0,7))
        self.random_seed_button=ttk.Button(seed_actions,text='🎲',width=3,command=self.random_seed)
        self.random_seed_button.pack(side='left',anchor='s',padx=(0,4),pady=(19,0))
        self.copy_seed_button=ttk.Button(seed_actions,text='Copier seed',command=self._copy_seed)
        self.copy_seed_button.pack(side='left',anchor='s',pady=(19,0))
        self.file_actions=ttk.Frame(secondary_row);self.file_actions.pack(side='left',fill='y')
        self.import_button=ttk.Button(self.file_actions,text='Importer…',command=self.import_file)
        self.import_button.pack(side='left',anchor='s',padx=(0,4),pady=(19,0))
        self.export_btn=ttk.Button(self.file_actions,text='Exporter…',command=self.export,state='disabled')
        self.export_btn.pack(side='left',anchor='s',padx=(0,4),pady=(19,0))
        self.preview_button=ttk.Button(self.file_actions,text='Aperçu PNG',command=self.save_preview)
        self.preview_button.pack(side='left',anchor='s',pady=(19,0))

        # Global controls have their own layout and never occupy generation columns.
        self.language_label=ttk.Label(self.global_panel,text='Langue')
        self.lang_var=tk.StringVar(value=LANGUAGE_LABELS[self.prefs.get('language','fr')])
        self.lang_combo=ColorMenuSelect(self.global_panel,self.lang_var,width=11,command=self._language_changed)
        self.lang_combo.set_items([('fr',LANGUAGE_LABELS['fr'],'#0055a4','flag_fr'),('en',LANGUAGE_LABELS['en'],'#21468b','flag_en')])
        self.help_button=ttk.Button(self.global_panel,text='Aide',command=self._show_help)
        self._theme_button=ttk.Button(self.global_panel,command=self._toggle_theme,width=3)
        self._refresh_theme_button_icon()

        # Session/Comparison is the middle region in wide mode and becomes one
        # coherent full-width block below the header only in compact mode.
        self.session_box=ttk.LabelFrame(self._header_shell,text='Session / Comparaison',padding=(6,4))
        self.session_history_label=ttk.Label(self.session_box,text='Historique session');self.session_history_label.grid(row=0,column=0,sticky='w')
        self.history_var=tk.StringVar(value='');self.history_combo=ttk.Combobox(self.session_box,textvariable=self.history_var,state='readonly',width=27)
        self.history_load_button=ttk.Button(self.session_box,text='Charger',command=self._load_history)
        self.history_clear_button=ttk.Button(self.session_box,text='Vider cache',command=self._clear_history)
        self._compare_led_off=_selector_icon(self,'#7b8088','dot',14);self._compare_led_on=_selector_icon(self,'#34a853','dot',14)
        self._delete_icon_off=_selector_icon(self.session_box,'#7b8088','cross',14)
        self._delete_icon_on=_selector_icon(self.session_box,'#e04444','cross',14)
        self.compare_a_button=ttk.Button(self.session_box,text='Définir A',image=self._compare_led_off,compound='left',command=lambda:self._set_compare_slot('A'))
        self.compare_b_button=ttk.Button(self.session_box,text='Définir B',image=self._compare_led_off,compound='left',command=lambda:self._set_compare_slot('B'))
        self.compare_toggle_button=ttk.Button(self.session_box,text='Basculer A/B',command=self._toggle_compare)
        self.clear_a_button=ttk.Button(self.session_box,text='',image=self._delete_icon_off,command=lambda:self._clear_compare_slot('A'))
        self.clear_b_button=ttk.Button(self.session_box,text='',image=self._delete_icon_off,command=lambda:self._clear_compare_slot('B'))
        self.clear_ab_button=ttk.Button(self.session_box,text='Vider A+B',command=self._clear_compare_slots)
        self.session_box.bind('<Configure>',self._apply_session_layout,add='+')
        self._apply_session_layout()

        self.inspector_var=tk.StringVar(value='Inspecteur : —')
        self._inspector_label=ttk.Label(top,textvariable=self.inspector_var,anchor='w')
        self._inspector_label.grid(row=1,column=0,sticky='ew',pady=(3,1))

        # Raster selector resources used by the independent viewer toolbar.
        self.heatmap_var=tk.StringVar(value='Arbres')
        self._lock_closed_icon=_selector_icon(self,'#d84a3a','lock_closed',18)
        self._lock_open_icon=_selector_icon(self,'#2ca85a','lock_open',18)
        self.canvas.bind('<Motion>',self._inspect_motion,add='+');self.canvas.bind('<Leave>',lambda e:self._clear_inspector(),add='+')
        self._build_stats_charts_tab()
        self._shortcut_settings_tab()
        self._reorder_analysis_tabs()
        self._theme_combo=self._find_combo_for_var(self.theme_var);self._projection_combo=self._find_combo_for_var(self.projection_var)
        self._build_viewer_toolbar(top)
        self._capture_translatable_widgets();self._install_status_feedback(top)
        # Keep the ready message synchronized when the player spinbox changes.
        self.players.trace_add('write',lambda *_:self.after_idle(self._selection_changed))
        if hasattr(self,'opacity_scale'):
            self.opacity_scale.bind('<Button-1>',self._opacity_locked_hint,add='+')

    def _build_viewer_toolbar(self,top):
        """Build map-specific controls independently from the application header."""
        left=self.canvas.master
        self.viewer_toolbar=ttk.Frame(left,padding=(4,3))
        self.viewer_toolbar.pack(fill='x',before=self.canvas,pady=(0,3))
        self.viewer_toolbar.columnconfigure(1,weight=1)
        self._viewer_migrated_widgets=set()

        self.viewer_view_label=ttk.Label(self.viewer_toolbar,text='Vue')
        self.viewer_view_label.grid(row=0,column=0,sticky='w',padx=(0,4))
        self._view_combo=ColorMenuSelect(self.viewer_toolbar,self.view,width=16,command=self._view_changed)
        self._view_combo.grid(row=0,column=1,sticky='ew',padx=(0,6))

        self.heatmap_title=ttk.Label(self.viewer_toolbar,text='Filtre carte thermique',compound='left')
        self.heatmap_title.grid(row=0,column=2,sticky='w',padx=(2,4))
        self.heatmap_combo=ColorMenuSelect(self.viewer_toolbar,self.heatmap_var,width=21,command=self._heatmap_changed)
        self.heatmap_combo.grid(row=0,column=3,padx=(0,6))

        self.viewer_recenter_button=ttk.Button(self.viewer_toolbar,text='Recentrer',command=self._reset_view)
        self.viewer_recenter_button.grid(row=0,column=4,padx=(0,8))
        self.viewer_zoom_label=ttk.Label(self.viewer_toolbar,text='Zoom')
        self.viewer_zoom_label.grid(row=0,column=5,sticky='w',padx=(0,4))
        self.zoom_scale=ttk.Scale(self.viewer_toolbar,from_=0.5,to=4.0,variable=self.zoom_var,command=lambda v:self._zoom_changed())
        self.zoom_scale.grid(row=0,column=6,sticky='ew');self.viewer_toolbar.columnconfigure(6,weight=1,minsize=90)
        self._bind_scale_jump(self.zoom_scale,self.zoom_var,.5,4.0,self._zoom_changed)
        self.viewer_toolbar.bind('<Configure>',self._apply_viewer_toolbar_layout,add='+')

    def _apply_viewer_toolbar_layout(self,event=None):
        """Reflow viewer-specific tools independently from the global header."""
        if not hasattr(self,'viewer_toolbar'):return
        try:width=int(self.viewer_toolbar.winfo_width())
        except tk.TclError:return
        compact=width<720
        mode='compact' if compact else 'wide'
        if getattr(self,'_viewer_toolbar_mode',None)==mode:return
        self._viewer_toolbar_mode=mode
        widgets=(self.viewer_view_label,self._view_combo,self.heatmap_title,self.heatmap_combo,self.viewer_recenter_button,self.viewer_zoom_label,self.zoom_scale)
        for w in widgets:
            try:w.grid_forget()
            except tk.TclError:pass
        for c in range(7):self.viewer_toolbar.columnconfigure(c,weight=0,minsize=0)
        if compact:
            self.viewer_view_label.grid(row=0,column=0,sticky='w',padx=(0,4))
            self._view_combo.grid(row=0,column=1,sticky='ew',padx=(0,6))
            self.viewer_recenter_button.grid(row=0,column=2,padx=(0,4))
            self.heatmap_title.grid(row=1,column=0,sticky='w',padx=(0,4),pady=(3,0))
            self.heatmap_combo.grid(row=1,column=1,sticky='ew',padx=(0,6),pady=(3,0))
            self.viewer_zoom_label.grid(row=1,column=2,sticky='w',padx=(0,4),pady=(3,0))
            self.zoom_scale.grid(row=1,column=3,sticky='ew',pady=(3,0))
            self.viewer_toolbar.columnconfigure(1,weight=0);self.viewer_toolbar.columnconfigure(3,weight=1,minsize=80)
        else:
            self.viewer_view_label.grid(row=0,column=0,sticky='w',padx=(0,4))
            self._view_combo.grid(row=0,column=1,sticky='ew',padx=(0,6))
            self.heatmap_title.grid(row=0,column=2,sticky='w',padx=(2,4))
            self.heatmap_combo.grid(row=0,column=3,padx=(0,6))
            self.viewer_recenter_button.grid(row=0,column=4,padx=(0,8))
            self.viewer_zoom_label.grid(row=0,column=5,sticky='w',padx=(0,4))
            self.zoom_scale.grid(row=0,column=6,sticky='ew')
            self.viewer_toolbar.columnconfigure(1,weight=0);self.viewer_toolbar.columnconfigure(6,weight=1,minsize=90)

    def _apply_initial_window_geometry(self):
        """Choose a useful initial size from the actual screen without assuming 1440p."""
        try:
            sw=max(900,int(self.winfo_screenwidth()));sh=max(700,int(self.winfo_screenheight()))
            w=min(1740,max(980,int(sw*0.90)));h=min(980,max(680,int(sh*0.86)))
            self.geometry(f'{w}x{h}');self.minsize(900,650)
        except tk.TclError:pass

    def _install_status_feedback(self,top):
        """Turn the historical status label into a small user-feedback strip."""
        self.status_display=tk.StringVar(value='')
        self.status_strip=ttk.Frame(top,padding=(4,2))
        self.status_strip.grid(row=2,column=0,sticky='ew',pady=(2,2))
        self.status_icon=ttk.Label(self.status_strip,text='●',width=2,anchor='center')
        self.status_icon.pack(side='left')
        self.status_label=ttk.Label(self.status_strip,textvariable=self.status_display,anchor='w')
        self.status_label.pack(side='left',fill='x',expand=True)
        self.status.trace_add('write',lambda *_:self._sync_status_display())
        # The historical header Progressbar is obsolete: progress now lives in the map overlay.
        # Never remap it during responsive reflow (it caused the persistent pale strip seen on Windows).
        try:self.progress.grid_remove()
        except tk.TclError:pass
        if hasattr(self,'heatmap_title'):
            self.heatmap_title.bind('<Enter>',lambda e:self._heatmap_locked_hint(),add='+')
        self._sync_status_display();self._apply_responsive_layout()

    def _status_symbol(self):
        return {'ready':'●','info':'ℹ','busy':'◉','success':'✓','warning':'⚠','error':'✕'}.get(self._status_kind,'●')

    def _sync_status_display(self):
        if not hasattr(self,'status_display'):return
        self.status_display.set(str(self.status.get() or ''))
        if hasattr(self,'status_icon'):self.status_icon.configure(text=self._status_symbol())

    def _feedback(self,key,kind='info',**values):
        lang=self.prefs.get('language','fr');template=FEEDBACK_TEXT.get(lang,FEEDBACK_TEXT['fr']).get(key,key)
        self._feedback_key=key;self._feedback_values=dict(values);self._status_kind=kind;self.status.set(template.format(**values));getattr(self,'_sync_status_display',lambda:None)()

    def _retranslate_feedback(self):
        if self._feedback_key in FEEDBACK_TEXT.get(self.prefs.get('language','fr'),{}):
            kind=self._status_kind;self._feedback(self._feedback_key,kind,**self._feedback_values)
        else:self._sync_status_display()

    def _schedule_responsive_layout(self,event=None):
        if event is not None and event.widget is not self:return
        if self._layout_after:
            try:self.after_cancel(self._layout_after)
            except tk.TclError:pass
        self._layout_after=self.after(80,self._apply_responsive_layout)

    def _apply_responsive_layout(self):
        """Reflow whole functional regions without mixing their internal controls."""
        if not hasattr(self,'_header_shell'):return
        self._layout_after=None
        try:width=int(self.winfo_width())
        except tk.TclError:return
        # R6 showed that 1600 px left the rightmost theme action clipped for a few
        # frames before reflow.  Keep the 1920 target wide, but switch earlier.
        compact=width<1750
        mode='compact' if compact else 'wide'
        if mode==self._responsive_mode:return
        self._responsive_mode=mode;shell=self._header_shell

        # Only selector widths adapt.  Text buttons retain their natural requested
        # width so translations are never clipped.
        try:
            self.mode_combo.configure(width=15 if compact else 20)
            self.arch_combo.configure(width=13 if compact else 18)
            self.modifier_button.configure(width=9 if compact else 14)
            self.lang_combo.configure(width=9 if compact else 11)
        except tk.TclError:pass

        for w in (self.generation_panel,self.session_box,self.global_panel):w.grid_forget()
        for c in range(5):shell.columnconfigure(c,weight=0,minsize=0)
        for r in range(2):shell.rowconfigure(r,weight=0,minsize=0)

        if compact:
            # Generation and global controls remain visibly separate at the 900 px
            # minimum; Session moves as a complete block below them.
            self.generation_panel.grid(row=0,column=0,sticky='nw')
            self.global_panel.grid(row=0,column=1,sticky='ne',padx=(10,0))
            self.session_box.grid(row=1,column=0,columnspan=2,sticky='ew',pady=(5,0))
            shell.columnconfigure(0,weight=1)
        else:
            # Fixed functional regions with elastic gutters keep Session genuinely
            # central instead of stretching it into a full-width second band.
            self.generation_panel.grid(row=0,column=0,sticky='nw')
            self.session_box.grid(row=0,column=2,sticky='n',padx=(10,10))
            self.global_panel.grid(row=0,column=4,sticky='ne')
            shell.columnconfigure(1,weight=1);shell.columnconfigure(3,weight=1)

        self._layout_global_controls(compact)
        shell.update_idletasks()
        self._session_layout_mode=None;self._apply_session_layout()

    def _layout_global_controls(self,compact):
        """Lay out the global region locally, never inside generation columns."""
        for w in (self.language_label,self.lang_combo,self.help_button,self._theme_button):w.grid_forget()
        for c in range(3):self.global_panel.columnconfigure(c,weight=0,minsize=0)
        self.language_label.grid(row=0,column=0,columnspan=3,sticky='w',pady=(0,2))
        self.lang_combo.grid(row=1,column=0,columnspan=3 if compact else 1,sticky='ew',padx=(0,4))
        if compact:
            self.help_button.grid(row=2,column=0,columnspan=2,sticky='ew',pady=(5,0),padx=(0,4))
            self._theme_button.grid(row=2,column=2,pady=(5,0))
        else:
            self.help_button.grid(row=1,column=1,padx=(0,4))
            self._theme_button.grid(row=1,column=2)

    def _apply_session_layout(self,event=None):
        """Keep full A/B identities when space allows and compact only near minimum."""
        if not hasattr(self,'session_box'):return
        try:width=int(event.width) if event is not None else int(self.session_box.winfo_width())
        except (AttributeError,tk.TclError,TypeError,ValueError):width=1
        compact=self._responsive_mode=='compact' and width<900
        mode='compact_ab' if compact else 'natural_ab'
        if getattr(self,'_session_layout_mode',None)==mode:return
        self._session_layout_mode=mode
        widgets=(self.history_combo,self.history_load_button,self.history_clear_button,self.compare_a_button,self.compare_b_button,self.compare_toggle_button,self.clear_a_button,self.clear_b_button,self.clear_ab_button)
        for w in widgets:
            try:w.grid_forget()
            except tk.TclError:pass
        for c in range(8):self.session_box.columnconfigure(c,weight=0,minsize=0)
        self.history_combo.configure(width=27)
        self.history_combo.grid(row=0,column=1,columnspan=3,sticky='ew',padx=(6,6))
        self.session_box.columnconfigure(1,weight=1,minsize=210)

        # Full identity in roomy layouts; a bounded width only at the real minimum.
        self.compare_a_button.configure(width=8 if compact else 0)
        self.compare_a_button.grid(row=0,column=4,padx=(3,1))
        self.clear_a_button.configure(width=3)
        self.clear_a_button.grid(row=0,column=5,padx=(1,4))
        self.compare_b_button.configure(width=8 if compact else 0)
        self.compare_b_button.grid(row=0,column=6,padx=(3,1))
        self.clear_b_button.configure(width=3)
        self.clear_b_button.grid(row=0,column=7,padx=(1,0))

        # History/cache and global A/B actions remain grouped on row 2.
        self.history_clear_button.configure(width=10 if compact else 0)
        self.history_load_button.configure(width=9 if compact else 0)
        self.compare_toggle_button.configure(width=12 if compact else 0)
        self.clear_ab_button.configure(width=10 if compact else 0)
        self.history_clear_button.grid(row=1,column=1,padx=(6,2),pady=(4,0),sticky='w')
        self.history_load_button.grid(row=1,column=2,padx=2,pady=(4,0),sticky='w')
        self.compare_toggle_button.grid(row=1,column=3,padx=2,pady=(4,0),sticky='w')
        self.clear_ab_button.grid(row=1,column=4,columnspan=2,padx=(3,2),pady=(4,0),sticky='w')

    def _heatmap_locked_hint(self):
        if self._view_key()!='heatmap':self._feedback('heatmap_locked','info')

    def _opacity_locked_hint(self,event=None):
        if self._view_key()=='global':self._feedback('opacity_locked','info');return 'break'

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
        self.stats_export_button=ttk.Button(controls,text='Exporter…',command=self._open_stats_export_center);self.stats_export_button.grid(row=0,column=2,padx=3)
        self.stats_chart_canvas=tk.Canvas(frame,highlightthickness=0,bg='#212225');self.stats_chart_canvas.grid(row=1,column=0,sticky='nsew')
        self.stats_chart_canvas.bind('<Configure>',lambda e:self._refresh_stats_chart(),add='+')
        self.stats_chart_canvas.bind('<Motion>',self._chart_tooltip_motion,add='+');self.stats_chart_canvas.bind('<Leave>',lambda e:self._hide_chart_tooltip(),add='+')
        self._stats_chart_photo=None;self._stats_chart_regions=[];self._chart_tooltip=None;self._chart_tooltip_label=None
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
            im,self._stats_chart_regions=render_stats_chart(stats,self._stats_chart_key(),lang=lang,dark=dark,width=w,height=h,compare_stats=self._compare_stats_pair(),return_regions=True)
            self._stats_chart_photo=ImageTk.PhotoImage(im);c.create_image(0,0,image=self._stats_chart_photo,anchor='nw')
        except Exception as exc:
            c.create_text(20,20,text=f'Chart error: {exc}',anchor='nw',fill=getattr(self,'_ui_theme_colors',{}).get('fg','#e8eaed'))

    def _hide_chart_tooltip(self):
        if getattr(self,'_chart_tooltip',None) is not None:
            try:self._chart_tooltip.destroy()
            except tk.TclError:pass
            self._chart_tooltip=None
            self._chart_tooltip_label=None

    def _chart_tooltip_motion(self,event):
        hit=None
        for region in reversed(getattr(self,'_stats_chart_regions',[])):
            x0,y0,x1,y1=region.get('bbox',(0,0,0,0))
            if x0<=event.x<=x1 and y0<=event.y<=y1:
                hit=region;break
        if hit is None:
            self._hide_chart_tooltip();return
        unit=hit.get('unit','');text=f"{hit.get('label','')}\n{hit.get('value','')}"+(f" {unit}" if unit else '')
        details=hit.get('details') or []
        if details:text+='\n'+'\n'.join(str(line) for line in details)
        dark=self.prefs.get('theme','dark')=='dark';bg='#202124' if dark else '#fffdf5';fg='#f1f3f4' if dark else '#202124'
        # Keep one tooltip window alive while the mouse moves across chart regions.
        # Recreating the Toplevel on every <Motion> caused visible flicker/disappearance.
        tip=getattr(self,'_chart_tooltip',None);label=getattr(self,'_chart_tooltip_label',None)
        if tip is None or label is None:
            tip=tk.Toplevel(self);tip.overrideredirect(True);tip.attributes('-topmost',True)
            label=tk.Label(tip,text=text,justify='left',background=bg,foreground=fg,relief='solid',borderwidth=1,padx=7,pady=5,font=('Segoe UI',9));label.pack()
            self._chart_tooltip=tip;self._chart_tooltip_label=label
        else:
            label.configure(text=text,background=bg,foreground=fg)
        tip.geometry(f"+{self.stats_chart_canvas.winfo_rootx()+event.x+14}+{self.stats_chart_canvas.winfo_rooty()+event.y+12}")

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
    def _preview_marker_key(self):
        value=self.preview_marker_var.get() if hasattr(self,'preview_marker_var') else ''
        for labels in PREVIEW_START_MARKER_LABELS.values():
            for key,label in labels.items():
                if label==value:return key
        return self.prefs.get('preview_start_markers','small')

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

    def _modifier_keys(self):
        # v1.8 DEV_2_R4 reserves the future multi-select architecture.  The only
        # currently valid state is no modifier, represented by an empty tuple.
        return ()
    def _modifier_summary(self):
        return 'Aucun' if self.prefs.get('language','fr')=='fr' else 'None'
    def _modifier_none_selected(self):
        # “None” is exclusive by definition and cannot be unchecked while it is
        # the sole available entry.
        self.modifier_none.set(True);self.modifier_text.set(self._modifier_summary())
        self._selection_changed();self._feedback('modifier_none','info')

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
        self.title(WINDOW_TITLES[lang])
        for w,source in getattr(self,'_i18n_widgets',[]):
            try:w.configure(text=source if lang=='fr' else TEXTS[source].get('en',source))
            except tk.TclError:pass
        for tab,source in getattr(self,'_i18n_tabs',[]):self.nb.tab(tab,text=source if lang=='fr' else TEXTS[source].get('en',source))
        if self._view_combo:
            self._view_combo.set_items([(k,VIEW_LABELS[lang][k],VIEW_ICON_COLORS[k],k) for k in VIEW_LABELS[lang]])
            self._view_combo.configure(width=max(12,max(len(v) for v in VIEW_LABELS[lang].values())+1))
        self.view.set(VIEW_LABELS[lang][vk]);self._view_combo._sync_icon()
        self.heatmap_combo.set_items([(k,HEATMAP_LABELS[lang][k],HEATMAP_ICON_COLORS[k],'dot') for k in HEATMAP_LABELS[lang]])
        self.heatmap_combo.configure(width=max(14,min(22,max(len(v) for v in HEATMAP_LABELS[lang].values())+1)))
        self.heatmap_var.set(HEATMAP_LABELS[lang][hk]);self.heatmap_combo._sync_icon()
        self.mode_combo.configure(values=[MODE_LABELS[lang][k] for k in MODE_ORDER]);self.mode.set(MODE_LABELS[lang][mk])
        self.arch_combo.configure(values=[ARCHETYPE_LABELS[lang][k] for k in ARCHETYPE_ORDER]);self.arch.set(ARCHETYPE_LABELS[lang][ak])
        if hasattr(self,'modifier_text'):
            self.modifier_text.set(self._modifier_summary())
            try:self.modifier_menu.entryconfigure(0,label='Aucun' if lang=='fr' else 'None')
            except tk.TclError:pass
        if self._theme_combo:self._theme_combo.configure(values=list(THEME_LABELS[lang].values()))
        self.theme_var.set(THEME_LABELS[lang][self.prefs['theme']])
        if self._projection_combo:self._projection_combo.configure(values=list(PROJECTION_LABELS[lang].values()))
        self.projection_var.set(PROJECTION_LABELS[lang][self.prefs['projection']])
        if hasattr(self,'preview_marker_combo'):
            self.preview_marker_combo.configure(values=list(PREVIEW_START_MARKER_LABELS[lang].values()))
            self.preview_marker_var.set(PREVIEW_START_MARKER_LABELS[lang][self.prefs.get('preview_start_markers','small')])
        self.lang_var.set(LANGUAGE_LABELS[lang]);self.lang_combo._sync_icon()
        self._refresh_stats_chart_labels()
        if getattr(self,'current',None) and getattr(self,'stats',None):
            st=self._ensure_stats_cache();self.stats.delete('1.0','end');self.stats.insert('end',format_stats_report(st,lang=lang))
        self._refresh_stats_chart();self._refresh_compare_buttons()
        for cmd,lbl in getattr(self,'shortcut_labels',{}).items():lbl.configure(text=COMMAND_LABELS[lang][cmd])
        for btn in getattr(self,'shortcut_reset_buttons',{}).values():btn.configure(text='Réinitialiser' if lang=='fr' else 'Reset')
        if hasattr(self,'history_combo'):self._refresh_history()
        self._update_view_controls();self._clear_inspector();self._retranslate_feedback()
    def _language_changed(self):
        self.prefs['language']='en' if self.lang_var.get()=='English' else 'fr';self._save_prefs();self._apply_language();self._retranslate_batch_window();self._refresh_preview(True)
    def _apply_theme(self):
        super()._apply_theme();dark=self.prefs.get('theme')=='dark';style=ttk.Style(self)
        field='#303134' if dark else '#ffffff';fg='#e8eaed' if dark else '#202124';muted='#7f858d' if dark else '#8a8f98';panel='#292a2d' if dark else '#e5e5e5'
        self._ui_theme_colors={'field':field,'fg':fg,'muted':muted,'panel':panel,'bar_bg':'#3c4043' if dark else '#dddddd','bar_fg':'#35a853','dark':dark}
        style.configure('ImageSelect.TMenubutton',background=field,foreground=fg,relief='raised')
        style.map('ImageSelect.TMenubutton',background=[('active',panel),('pressed',panel),('disabled',field)],foreground=[('active',fg),('pressed',fg),('disabled',muted)])
        style.configure('Locked.TCombobox',fieldbackground=field,background=field,foreground=muted,selectforeground=muted)
        style.map('Locked.TCombobox',fieldbackground=[('disabled',field)],background=[('disabled',field)],foreground=[('disabled',muted)])
        # Option DB helps comboboxes created after the theme switch; direct popdown
        # styling below also fixes listboxes which Tk has already instantiated.
        self.option_add('*TCombobox*Listbox.background',field,'interactive');self.option_add('*TCombobox*Listbox.foreground',fg,'interactive')
        self.option_add('*TCombobox*Listbox.selectBackground',panel,'interactive');self.option_add('*TCombobox*Listbox.selectForeground',fg,'interactive')
        self._style_combobox_popdowns(field,fg,panel)
        for selector in (getattr(self,'_view_combo',None),getattr(self,'heatmap_combo',None),getattr(self,'lang_combo',None)):
            if isinstance(selector,ColorMenuSelect):selector.set_menu_theme(field,fg,panel,fg)
        if hasattr(self,'modifier_menu'):
            try:self.modifier_menu.configure(background=field,foreground=fg,activebackground=panel,activeforeground=fg)
            except tk.TclError:pass
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
        for row in getattr(self,'_batch_rows',[]):
            try:row['thumbnail_host'].configure(bg=panel);row['thumbnail'].configure(bg=panel)
            except (KeyError,tk.TclError):pass
            self._batch_draw_progress(row)

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
        self._status_kind='busy';self.status.set(label);getattr(self,'_sync_status_display',lambda:None)()
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
        # Fast-changing stage detail belongs in the progress bar/overlay, not in the human status strip.
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
        self._status_kind='success'
        if label:self.status.set(label)
        self._sync_status_display()
        if self._task_overlay is not None:
            self._draw_task_progress(100,label if label else None);self.update_idletasks()
        self._close_task_dialog()

    def _task_error(self,label='Erreur'):
        self._status_kind='error';self.status.set(label);getattr(self,'_sync_status_display',lambda:None)();self._close_task_dialog();self.update_idletasks()

    def _save_prefs(self):
        save_settings({'theme':self.prefs['theme'],'overlay_alpha':int(self.opacity_var.get()),'projection':self.prefs['projection'],'preview_start_markers':self.prefs.get('preview_start_markers','small'),'wheel_zoom':float(self.wheel_var.get()),'language':self.prefs.get('language','fr'),'shortcuts':self.prefs.get('shortcuts',dict(DEFAULT_SHORTCUTS))})

    def _schedule_prefs_save(self):
        if self._prefs_save_after is not None:
            try:self.after_cancel(self._prefs_save_after)
            except tk.TclError:pass
        self._prefs_save_after=self.after(200,self._flush_scheduled_prefs)

    def _flush_scheduled_prefs(self):
        self._prefs_save_after=None;self._save_prefs()

    def destroy(self):
        if self._prefs_save_after is not None:
            try:self.after_cancel(self._prefs_save_after)
            except tk.TclError:pass
            self._prefs_save_after=None;self._save_prefs()
        super().destroy()

    def _theme_changed(self):
        self.prefs['theme']=self._theme_key();self._save_prefs();self._apply_theme()
    def _toggle_theme(self):
        self.prefs['theme']='light' if self.prefs.get('theme')=='dark' else 'dark';lang=self.prefs.get('language','fr');self.theme_var.set(THEME_LABELS[lang][self.prefs['theme']]);self._save_prefs();self._apply_theme();self._refresh_theme_button_icon();self._refresh_preview(False);self._refresh_stats_chart();self._feedback('theme_changed','info',theme=THEME_LABELS[lang][self.prefs['theme']])
    def _projection_changed(self):
        self.prefs['projection']=self._projection_key();self._save_prefs();self._refresh_preview(True);self._refresh_batch_previews()
    def _preview_marker_changed(self):
        self.prefs['preview_start_markers']=self._preview_marker_key();self._save_prefs();self._refresh_batch_previews()

    def _opacity_changed(self):
        self.opacity_label.configure(text=f'{int(self.opacity_var.get())} %');self.prefs['overlay_alpha']=int(self.opacity_var.get());self._schedule_prefs_save()
        if self._view_key()=='starts':self._invalidate_preview_composite()
        else:self._invalidate_preview()
        self._schedule_preview()

    def _wheel_changed(self):
        self.wheel_label.configure(text=f'×{self.wheel_var.get():.2f}');self.prefs['wheel_zoom']=float(self.wheel_var.get());self._schedule_prefs_save()

    def _update_view_controls(self):
        view=self._view_key();lang=self.prefs.get('language','fr')
        if hasattr(self,'opacity_scale'):self.opacity_scale.configure(state='disabled' if view=='global' else 'normal')
        if hasattr(self,'heatmap_combo'):
            locked=view!='heatmap';self.heatmap_combo.set_enabled(not locked)
            if hasattr(self,'heatmap_title'):self.heatmap_title.configure(text=('Filtre carte thermique' if lang=='fr' else 'Heatmap filter'),image=self._lock_closed_icon if locked else self._lock_open_icon)
    def _view_changed(self):self._update_view_controls();self._refresh_preview(True)
    def _heatmap_changed(self):self._refresh_preview(True)
    def _reset_view(self):self.zoom_var.set(1.0);self.zoom=1.0;self._refresh_preview(True);self._feedback('view_reset','info')
    def random_seed(self):
        super().random_seed();self._feedback('seed_randomized','info',seed=str(self.seed.get()))
    def _copy_seed(self):
        value=str(self.seed.get());self.clipboard_clear();self.clipboard_append(value);self._feedback('seed_copied','success',seed=value)

    def _selection_changed(self):
        s=int(self.size.get());mkey=self._mode_key();akey=self._arch_key();m=MODES[mkey];a=ARCHETYPES[akey];lang=self.prefs.get('language','fr')
        mode=MODE_LABELS[lang][mkey];arch=ARCHETYPE_LABELS[lang][akey];modifiers=self._modifier_summary()
        if s!=768:self._feedback('size_reserved','warning',side=s,max_players=NATIVE_LIMITS[s])
        elif not m.implemented:self._feedback('mode_reserved','warning',mode=mode)
        elif not a.implemented:self._feedback('arch_reserved','warning',archetype=arch)
        else:self._feedback('ready','ready',mode=mode,archetype=arch,modifiers=modifiers,side=s,players=int(self.players.get()))

    def _progress_stage(self,stage,detail,index):
        # Detailed generator stages can change too quickly to be readable as status messages.
        value=min(95,5+index*4);text=f'{stage} {detail}'.strip()
        if self._batch_running and self._batch_active_row is not None:
            row=self._batch_active_row
            try:
                self._batch_update_progress(row,value,text)
                # Process the Batch cancel button while the current synchronous
                # generator call is running.  Cancellation deliberately affects
                # only queued maps; the protected engine is never interrupted.
                self.update()
            except tk.TclError:pass
        elif self._task_overlay is not None:self._draw_task_progress(value,text)
        else:
            self.progress['value']=value
        self.update_idletasks()

    def _cache_key(self):
        return GenerationCacheKey(seed=int(self.seed.get()),side=int(self.size.get()),players=int(self.players.get()),mode=self._mode_key(),archetype=self._arch_key(),modifiers=self._modifier_keys(),engine_revision='v1.5-stable')
    def _history_label(self,key):
        mods=('aucun' if self.prefs.get('language','fr')=='fr' else 'none') if not key.modifiers else '+'.join(key.modifiers)
        return f'{key.seed} · {key.side} · {key.players}P · {key.mode} · {key.archetype} · {mods}'
    def _refresh_history(self):
        self._history_lookup={self._history_label(k):k for k,_ in self.session_cache.entries()};vals=list(self._history_lookup);self.history_combo.configure(values=vals)
        if vals and self.history_var.get() not in vals:self.history_var.set(vals[0])

    # ---------- v1.8 DEV_3: Batch Generation v1 ----------
    def _batch_text(self,key,**values):
        text=BATCH_TEXT[self.prefs.get('language','fr')][key]
        return text.format(**values) if values else text

    @staticmethod
    def _batch_label_key(value,label_tables,fallback):
        for labels in label_tables.values():
            for key,label in labels.items():
                if label==value:return key
        return fallback

    def _open_batch_window(self):
        if self._batch_window is not None:
            try:self._batch_window.deiconify();self._batch_window.lift();self._batch_window.focus_force();return
            except tk.TclError:self._batch_window=None
        lang=self.prefs.get('language','fr');bt=BATCH_TEXT[lang]
        win=tk.Toplevel(self);self._batch_window=win
        win.title(bt['title']);win.transient(self);win.geometry('1120x650');win.minsize(900,560)
        win.protocol('WM_DELETE_WINDOW',self._close_batch_window)
        shell=ttk.Frame(win,padding=12);shell.pack(fill='both',expand=True)

        header=ttk.Frame(shell);header.pack(fill='x',pady=(0,6))
        self._batch_i18n={'shell':shell}
        self._batch_i18n['count_label']=ttk.Label(header,text=bt['count']);self._batch_i18n['count_label'].pack(side='left')
        self._batch_count_var=tk.StringVar(value='4')
        self._batch_count_spin=ttk.Spinbox(header,from_=1,to=4,textvariable=self._batch_count_var,width=4,command=self._batch_update_row_visibility)
        self._batch_count_spin.pack(side='left',padx=(7,8));self._batch_count_spin.bind('<KeyRelease>',self._batch_count_typed);self._batch_count_spin.bind('<Return>',self._batch_commit_count);self._batch_count_spin.bind('<FocusOut>',self._batch_commit_count)
        self._batch_randomize_button=ttk.Button(header,text=bt['randomize'],command=self._batch_randomize_seeds)
        self._batch_randomize_button.pack(side='left',padx=(0,12))
        self._batch_common_seed_var=tk.StringVar(value=str(self._default_batch_seed()))
        self._batch_common_seed_entry=ttk.Entry(header,textvariable=self._batch_common_seed_var,width=13);self._batch_common_seed_entry.pack(side='left')
        self._batch_common_seed_random=ttk.Button(header,text='🎲',width=3,command=self._batch_randomize_common_seed);self._batch_common_seed_random.pack(side='left',padx=(4,0))
        self._batch_apply_seed_button=ttk.Button(header,text=bt['apply_seed'],command=self._batch_apply_seed_all);self._batch_apply_seed_button.pack(side='left',padx=(4,0))
        self._batch_i18n['hint_label']=ttk.Label(header,text=('1–4 cartes · paramètres indépendants · génération séquentielle' if lang=='fr' else '1–4 maps · independent parameters · sequential generation'));self._batch_i18n['hint_label'].pack(side='right')

        rows_host=ttk.Frame(shell);rows_host.pack(fill='both',expand=True)
        rows_host.columnconfigure(0,weight=1)
        self._batch_rows=[]
        current_mode=self._mode_key();current_arch=self._arch_key();current_size=str(self.size.get());current_players=str(self.players.get())
        first_seed=self._default_batch_seed();self._batch_common_seed_var.set(str(first_seed))
        for index in range(1,5):
            frame=ttk.Labelframe(rows_host,text=bt['map'].format(index=index),padding=(1,1))
            frame.grid(row=index-1,column=0,sticky='ew',pady=(0,4));frame.columnconfigure(0,weight=1)
            controls=ttk.Frame(frame);controls.grid(row=0,column=0,sticky='ew',padx=(7,0),pady=(3,0))
            row={'index':index,'frame':frame,'result':None,'state':'waiting','cached':False,'error':'','progress_value':0};input_widgets=[];row['group_labels']={}

            def group(key):
                box=ttk.Frame(controls);box.pack(side='left',padx=(0,7));label=ttk.Label(box,text=bt[key]);label.pack(anchor='w',pady=(0,2));row['group_labels'][key]=label;return box

            box=group('mode');row['mode_var']=tk.StringVar(value=MODE_LABELS[lang][current_mode])
            row['mode']=ttk.Combobox(box,textvariable=row['mode_var'],values=[MODE_LABELS[lang][k] for k in MODE_ORDER],state='readonly',width=19);row['mode'].pack();input_widgets.append((row['mode'],'readonly'))
            box=group('archetype');row['arch_var']=tk.StringVar(value=ARCHETYPE_LABELS[lang][current_arch])
            row['arch']=ttk.Combobox(box,textvariable=row['arch_var'],values=[ARCHETYPE_LABELS[lang][k] for k in ARCHETYPE_ORDER],state='readonly',width=17);row['arch'].pack();input_widgets.append((row['arch'],'readonly'))
            box=group('modifiers');row['modifier_var']=tk.StringVar(value=bt['none'])
            row['modifier']=ttk.Combobox(box,textvariable=row['modifier_var'],values=[bt['none']],state='readonly',width=13);row['modifier'].pack();input_widgets.append((row['modifier'],'readonly'))
            box=group('size');row['size_var']=tk.StringVar(value=current_size)
            row['size']=ttk.Combobox(box,textvariable=row['size_var'],values=[str(x) for x in NATIVE_LIMITS],state='readonly',width=7);row['size'].pack();input_widgets.append((row['size'],'readonly'))
            box=group('players');row['players_var']=tk.StringVar(value=current_players)
            row['players']=ttk.Spinbox(box,from_=2,to=NATIVE_LIMITS.get(int(current_size),20),textvariable=row['players_var'],width=7);row['players'].pack();input_widgets.append((row['players'],'normal'))
            box=group('seed');row['seed_var']=tk.StringVar(value=str(first_seed))
            seed_line=ttk.Frame(box);seed_line.pack(fill='x');row['seed']=ttk.Entry(seed_line,textvariable=row['seed_var'],width=14);row['seed'].pack(side='left');input_widgets.append((row['seed'],'normal'))
            row['random']=ttk.Button(seed_line,text='🎲',width=3,command=lambda r=row:self._batch_randomize_row(r));row['random'].pack(side='left',padx=(4,0));input_widgets.append((row['random'],'normal'))
            row['size'].bind('<<ComboboxSelected>>',lambda e,r=row:self._batch_row_size_changed(r))

            mini_bg=getattr(self,'_ui_theme_colors',{}).get('panel','#292a2d')
            row['thumbnail_host']=tk.Frame(frame,width=182,height=122,bg=mini_bg,bd=0,highlightthickness=0);row['thumbnail_host'].grid(row=0,column=1,rowspan=2,sticky='e');row['thumbnail_host'].grid_propagate(False)
            row['thumbnail']=tk.Label(row['thumbnail_host'],text=str(index),bg=mini_bg,bd=0,highlightthickness=0,cursor='hand2');row['thumbnail'].place(relx=.5,rely=.5,anchor='center')
            row['thumbnail'].bind('<Button-1>',lambda e,r=row:self._batch_toggle_large_preview(r));row['thumbnail'].bind('<Enter>',lambda e,r=row:self._batch_schedule_hover_preview(r));row['thumbnail'].bind('<Leave>',self._batch_thumbnail_leave)
            result_line=ttk.Frame(frame);result_line.grid(row=1,column=0,sticky='ew',padx=(7,8),pady=(7,3));result_line.columnconfigure(3,weight=1)
            row['status_var']=tk.StringVar(value=bt['waiting'])
            row['show']=ttk.Button(result_line,text=bt['show'],state='disabled',command=lambda r=row:self._batch_show_result(r));row['show'].grid(row=0,column=0,padx=(0,4))
            row['set_a']=ttk.Button(result_line,text=bt['set_a'],image=self._compare_led_off,compound='left',state='disabled',command=lambda r=row:self._batch_assign_result(r,'A'));row['set_a'].grid(row=0,column=1,padx=2)
            row['set_b']=ttk.Button(result_line,text=bt['set_b'],image=self._compare_led_off,compound='left',state='disabled',command=lambda r=row:self._batch_assign_result(r,'B'));row['set_b'].grid(row=0,column=2,padx=(2,7))
            row['progress']=tk.Canvas(result_line,height=26,highlightthickness=0,bd=0);row['progress'].grid(row=0,column=3,sticky='ew');row['progress'].bind('<Configure>',lambda e,r=row:self._batch_draw_progress(r))
            row['input_widgets']=input_widgets;self._batch_rows.append(row)
            self._batch_draw_progress(row)

        footer=ttk.Frame(shell);footer.pack(fill='x',pady=(2,0))
        self._batch_summary_var=tk.StringVar(value=bt['waiting']);self._batch_i18n['summary_label']=ttk.Label(footer,textvariable=self._batch_summary_var,anchor='w');self._batch_i18n['summary_label'].pack(side='left',fill='x',expand=True)
        self._batch_start_button=ttk.Button(footer,text=bt['start'],command=self._start_batch);self._batch_start_button.pack(side='right',padx=(5,0))
        self._batch_cancel_button=ttk.Button(footer,text=bt['cancel'],command=self._cancel_batch,state='disabled');self._batch_cancel_button.pack(side='right',padx=(5,0))
        self._batch_close_button=ttk.Button(footer,text=bt['close'],command=self._close_batch_window);self._batch_close_button.pack(side='right')
        self._batch_update_row_visibility();self._fit_batch_window_initial();self._feedback('batch_opened','info')

    def _fit_batch_window_initial(self):
        win=self._batch_window
        if win is None:return
        try:
            win.update_idletasks();screen_w=win.winfo_screenwidth();screen_h=win.winfo_screenheight();max_w=max(900,screen_w-64);max_h=max(560,screen_h-96)
            wanted_w=max(1120,win.winfo_reqwidth());wanted_h=max(650,win.winfo_reqheight());width=min(wanted_w,max_w);height=min(wanted_h,max_h)
            self.update_idletasks();x=self.winfo_rootx()+(self.winfo_width()-width)//2;y=self.winfo_rooty()+(self.winfo_height()-height)//2
            x=max(8,min(x,screen_w-width-8));y=max(8,min(y,screen_h-height-48));win.minsize(min(900,width),min(560,height));win.geometry(f'{width}x{height}+{x}+{y}')
        except tk.TclError:pass

    def _default_batch_seed(self):
        try:return int(self.seed.get())
        except (TypeError,ValueError):return random.randint(1,2_147_483_647)

    def _batch_apply_seed_all(self):
        value=self._batch_common_seed_var.get().strip()
        try:int(value)
        except (TypeError,ValueError):
            messagebox.showerror(self._batch_text('invalid_title'),self._batch_text('invalid_seed'),parent=self._batch_window);return
        for row in self._batch_rows:row['seed_var'].set(value)

    def _batch_randomize_common_seed(self):
        self._batch_common_seed_var.set(str(random.randint(1,2_147_483_647)))

    def _batch_update_progress(self,row,value,text=None,state=None):
        row['progress_value']=max(0,min(100,float(value)))
        if text is not None:row['status_var'].set(str(text))
        if state is not None:row['state']=state
        self._batch_draw_progress(row)

    def _batch_draw_progress(self,row):
        canvas=row.get('progress')
        if canvas is None:return
        try:
            canvas.update_idletasks();w=max(1,canvas.winfo_width());h=max(1,canvas.winfo_height());canvas.delete('all')
            colors=getattr(self,'_ui_theme_colors',{});bg=colors.get('bar_bg','#3c4043');state=row.get('state','waiting')
            fill={'running':colors.get('bar_fg','#35a853'),'success':'#35a853','cached':'#2879d0','failed':'#d84a3a','cancelled':'#7f858d'}.get(state,colors.get('muted','#7f858d'))
            value=float(row.get('progress_value',0));canvas.configure(bg=bg)
            if value>0:canvas.create_rectangle(0,0,max(1,round(w*value/100)),h,fill=fill,outline='')
            shown=self._fit_progress_detail(row.get('status_var').get() if row.get('status_var') else '',max(40,w-18))
            canvas.create_text(w//2,h//2,text=shown,fill=colors.get('fg','#e8eaed'),anchor='center')
        except tk.TclError:pass

    def _batch_render_thumbnail(self,row):
        out=row.get('result')
        if out is None:return
        state_key=id(out.state);projection=self.prefs.get('projection','square')
        if row.get('preview_square_base_key')!=state_key:
            row['preview_square_base_image']=render_square_base(out.state,view='global',overlay_alpha=100,heatmap_resource='trees')
            row['preview_square_base_key']=state_key;row['preview_projected_base_image']=None;row['preview_projected_base_key']=None
        if projection=='parallelogram':
            if row.get('preview_projected_base_key')!=state_key:
                row['preview_projected_base_image']=project_parallelogram(row['preview_square_base_image']);row['preview_projected_base_key']=state_key
            row['preview_base_image']=row['preview_projected_base_image']
        else:row['preview_base_image']=row['preview_square_base_image']
        row['preview_base_key']=(state_key,projection)
        image=self._batch_compose_preview(row)
        thumb=image.copy();thumb.thumbnail((180,120),Image.Resampling.NEAREST)
        row['thumbnail_photo']=ImageTk.PhotoImage(thumb);row['thumbnail'].configure(image=row['thumbnail_photo'],text='')

    def _batch_compose_preview(self,row):
        base=row.get('preview_base_image');out=row.get('result')
        if base is None or out is None:return None
        marker_mode=self.prefs.get('preview_start_markers','small')
        if marker_mode=='hidden':return base
        return compose_start_markers(base,out.state,projection=self.prefs.get('projection','square'),scale=2 if marker_mode=='normal' else 1)

    def _refresh_batch_previews(self):
        if not getattr(self,'_batch_rows',None):return
        visible_row=self._batch_preview_row;visible=self._batch_preview_window is not None
        for row in self._batch_rows:
            if row.get('result') is not None:self._batch_render_thumbnail(row)
        if visible and visible_row is not None and visible_row.get('result') is not None:self._batch_refresh_preview_tooltip(visible_row)

    def _batch_schedule_hover_preview(self,row):
        self._batch_cancel_hover_preview()
        if row.get('result') is not None and not self._batch_preview_pinned:self._batch_hover_after=self.after(700,lambda:self._batch_show_preview_tooltip(row,False))

    def _batch_cancel_hover_preview(self,event=None):
        if self._batch_hover_after is not None:
            try:self.after_cancel(self._batch_hover_after)
            except tk.TclError:pass
            self._batch_hover_after=None

    def _batch_thumbnail_leave(self,event=None):
        self._batch_cancel_hover_preview()
        if not self._batch_preview_pinned:self._batch_hide_preview_tooltip()

    def _batch_toggle_large_preview(self,row):
        if self._batch_preview_pinned and self._batch_preview_row is row:
            self._batch_hide_preview_tooltip();return
        self._batch_show_preview_tooltip(row,True)

    def _batch_show_preview_tooltip(self,row,pinned=False):
        self._batch_cancel_hover_preview()
        if row.get('result') is None:return
        if row.get('preview_base_image') is None:self._batch_render_thumbnail(row)
        image=self._batch_compose_preview(row)
        old_win=self._batch_preview_window;preserved=None
        if old_win is not None and self._batch_preview_pinned:
            try:preserved=(old_win.winfo_x(),old_win.winfo_y())
            except tk.TclError:pass
        shown,size,x,y=self._batch_preview_geometry(row,image)
        if preserved is not None:x,y=self._batch_clamp_preview_position(preserved[0],preserved[1],size)
        win,label,photo=self._batch_build_preview_surface(shown,size,x,y,pinned)
        self._batch_preview_window=win;self._batch_preview_label=label;self._batch_preview_photo=photo;self._batch_preview_row=row;self._batch_preview_pinned=bool(pinned);self._batch_preview_projection=self.prefs.get('projection','square')
        win.deiconify();win.lift();win.update_idletasks()
        if old_win is not None and old_win is not win:
            try:old_win.destroy()
            except tk.TclError:pass

    def _batch_build_preview_surface(self,shown,size,x,y,pinned):
        chroma='#ff00ff';win=tk.Toplevel(self._batch_window or self);win.withdraw()
        win.overrideredirect(True);win.configure(bg=chroma);win.attributes('-topmost',True)
        try:win.wm_attributes('-transparentcolor',chroma)
        except tk.TclError:pass
        photo=ImageTk.PhotoImage(shown,master=win);label=tk.Label(win,image=photo,bg=chroma,bd=0,highlightthickness=0,cursor='fleur' if pinned else 'arrow');label.pack()
        win.geometry(f'{size[0]}x{size[1]}+{x}+{y}')
        if pinned:
            label.bind('<ButtonPress-1>',self._batch_preview_drag_start);label.bind('<B1-Motion>',self._batch_preview_drag_move);label.bind('<ButtonRelease-1>',self._batch_preview_drag_end)
        win.bind('<Escape>',lambda e:self._batch_hide_preview_tooltip(),add='+')
        win.update_idletasks();return win,label,photo

    def _batch_preview_geometry(self,row,image):
        screen_w=self.winfo_screenwidth();screen_h=self.winfo_screenheight();anchor=row['thumbnail_host'];anchor.update_idletasks()
        ax=anchor.winfo_rootx();ay=anchor.winfo_rooty();aw=anchor.winfo_width();ah=anchor.winfo_height();margin=14
        left_space=max(0,ax-margin-8);right_space=max(0,screen_w-(ax+aw)-margin-8);place_left=left_space>=right_space
        side_space=left_space if place_left else right_space
        if side_space<360:place_left=not place_left;side_space=left_space if place_left else right_space
        max_w=max(280,min(900,side_space));max_h=min(700,max(280,screen_h-96))
        factor=min(max_w/image.width,max_h/image.height,1.0);size=(max(1,int(image.width*factor)),max(1,int(image.height*factor)));shown=image.resize(size,Image.Resampling.NEAREST)
        x=(ax-size[0]-margin) if place_left else (ax+aw+margin);x=max(8,min(x,screen_w-size[0]-8))
        y=ay+(ah-size[1])//2;y=max(8,min(y,screen_h-size[1]-48))
        return shown,size,x,y

    def _batch_clamp_preview_position(self,x,y,size):
        screen_w=self.winfo_screenwidth();screen_h=self.winfo_screenheight()
        return max(8,min(int(x),screen_w-size[0]-8)),max(8,min(int(y),screen_h-size[1]-48))

    def _batch_preview_drag_start(self,event):
        win=self._batch_preview_window
        if win is None or not self._batch_preview_pinned:return 'break'
        try:self._batch_preview_drag_origin=(event.x_root,event.y_root,win.winfo_x(),win.winfo_y())
        except tk.TclError:self._batch_preview_drag_origin=None
        return 'break'

    def _batch_preview_drag_move(self,event):
        win=self._batch_preview_window;origin=self._batch_preview_drag_origin
        if win is None or origin is None or not self._batch_preview_pinned:return 'break'
        try:
            size=(win.winfo_width(),win.winfo_height());x,y=self._batch_clamp_preview_position(origin[2]+event.x_root-origin[0],origin[3]+event.y_root-origin[1],size)
            win.geometry(f'+{x}+{y}')
        except tk.TclError:pass
        return 'break'

    def _batch_preview_drag_end(self,event=None):
        self._batch_preview_drag_origin=None;return 'break'

    def _batch_refresh_preview_tooltip(self,row):
        win=self._batch_preview_window;label=self._batch_preview_label
        if win is None or label is None or self._batch_preview_row is not row:return
        try:
            current=(win.winfo_x(),win.winfo_y());image=self._batch_compose_preview(row);shown,size,_,_=self._batch_preview_geometry(row,image);x,y=self._batch_clamp_preview_position(current[0],current[1],size)
            projection=self.prefs.get('projection','square')
            if projection!=self._batch_preview_projection:
                new_win,new_label,new_photo=self._batch_build_preview_surface(shown,size,x,y,self._batch_preview_pinned)
                self._batch_preview_window=new_win;self._batch_preview_label=new_label;self._batch_preview_photo=new_photo;self._batch_preview_projection=projection
                new_win.deiconify();new_win.lift();new_win.update_idletasks();win.destroy();return
            photo=ImageTk.PhotoImage(shown);label.configure(image=photo);self._batch_preview_photo=photo
            win.geometry(f'{size[0]}x{size[1]}+{x}+{y}')
        except tk.TclError:pass

    def _batch_hide_preview_tooltip(self):
        if self._batch_preview_window is not None:
            try:self._batch_preview_window.destroy()
            except tk.TclError:pass
        self._batch_preview_window=None;self._batch_preview_label=None;self._batch_preview_photo=None;self._batch_preview_row=None;self._batch_preview_pinned=False;self._batch_preview_projection=None;self._batch_preview_drag_origin=None

    def _retranslate_batch_window(self):
        win=getattr(self,'_batch_window',None)
        if win is None:return
        try:
            lang=self.prefs.get('language','fr');bt=BATCH_TEXT[lang];win.title(bt['title'])
            self._batch_i18n['count_label'].configure(text=bt['count']);self._batch_randomize_button.configure(text=bt['randomize']);self._batch_apply_seed_button.configure(text=bt['apply_seed'])
            self._batch_i18n['hint_label'].configure(text='1–4 cartes · paramètres indépendants · génération séquentielle' if lang=='fr' else '1–4 maps · independent parameters · sequential generation')
            for row in self._batch_rows:
                mode=self._batch_label_key(row['mode_var'].get(),MODE_LABELS,'legacy');arch=self._batch_label_key(row['arch_var'].get(),ARCHETYPE_LABELS,'continental')
                row['frame'].configure(text=bt['map'].format(index=row['index']))
                for key,label in row['group_labels'].items():label.configure(text=bt[key])
                row['mode'].configure(values=[MODE_LABELS[lang][key] for key in MODE_ORDER]);row['mode_var'].set(MODE_LABELS[lang][mode])
                row['arch'].configure(values=[ARCHETYPE_LABELS[lang][key] for key in ARCHETYPE_ORDER]);row['arch_var'].set(ARCHETYPE_LABELS[lang][arch])
                row['modifier'].configure(values=[bt['none']]);row['modifier_var'].set(bt['none']);row['show'].configure(text=bt['show']);row['set_a'].configure(text=bt['set_a']);row['set_b'].configure(text=bt['set_b'])
                state=row.get('state','waiting');key='cached' if row.get('cached') else ('success' if state=='success' else state)
                if key=='failed':text=bt['failed'].format(error=row.get('error',''))
                elif key in bt:text=bt[key]
                else:text=bt['waiting']
                row['status_var'].set(text);self._batch_draw_progress(row)
            self._batch_start_button.configure(text=bt['start']);self._batch_cancel_button.configure(text=bt['cancel']);self._batch_close_button.configure(text=bt['close'])
        except tk.TclError:pass

    def _batch_update_row_visibility(self):
        if self._batch_running:return
        try:count=max(1,min(4,int(self._batch_count_var.get())))
        except (TypeError,ValueError,tk.TclError):return
        for i,row in enumerate(self._batch_rows):
            if i<count:row['frame'].grid()
            else:row['frame'].grid_remove()

    def _batch_count_typed(self,event=None):
        try:count=int(self._batch_count_var.get())
        except (TypeError,ValueError,tk.TclError):return
        if 1<=count<=4:self._batch_update_row_visibility()

    def _batch_commit_count(self,event=None):
        try:count=int(self._batch_count_var.get())
        except (TypeError,ValueError,tk.TclError):count=1
        self._batch_count_var.set(str(max(1,min(4,count))));self._batch_update_row_visibility()

    def _batch_row_size_changed(self,row):
        try:side=int(row['size_var'].get());maximum=NATIVE_LIMITS[side];row['players'].configure(to=maximum)
        except (TypeError,ValueError,KeyError):return
        try:
            if int(row['players_var'].get())>maximum:row['players_var'].set(str(maximum))
        except (TypeError,ValueError):pass

    def _batch_randomize_row(self,row):row['seed_var'].set(str(random.randint(1,2_147_483_647)))
    def _batch_randomize_seeds(self):
        try:count=max(1,min(4,int(self._batch_count_var.get())))
        except (TypeError,ValueError):count=1
        for row in self._batch_rows[:count]:self._batch_randomize_row(row)

    def _batch_collect_requests(self):
        lang=self.prefs.get('language','fr');errors=[];requests=[]
        try:count=max(1,min(4,int(self._batch_count_var.get())))
        except (TypeError,ValueError):count=1
        for row in self._batch_rows[:count]:
            error=None
            try:side=int(row['size_var'].get())
            except (TypeError,ValueError):side=0
            mode=self._batch_label_key(row['mode_var'].get(),MODE_LABELS,'legacy')
            archetype=self._batch_label_key(row['arch_var'].get(),ARCHETYPE_LABELS,'continental')
            try:players=int(row['players_var'].get())
            except (TypeError,ValueError):players=0
            try:seed=int(row['seed_var'].get())
            except (TypeError,ValueError):seed=None
            if side!=768:error=BATCH_TEXT[lang]['unsupported_size']
            elif not MODES[mode].implemented:error=BATCH_TEXT[lang]['unsupported_mode']
            elif not ARCHETYPES[archetype].implemented:error=BATCH_TEXT[lang]['unsupported_archetype']
            elif not 2<=players<=NATIVE_LIMITS[side]:error=BATCH_TEXT[lang]['invalid_players'].format(maximum=NATIVE_LIMITS[side])
            elif seed is None:error=BATCH_TEXT[lang]['invalid_seed']
            if error:
                errors.append(BATCH_TEXT[lang]['invalid_row'].format(index=row['index'],error=error));continue
            key=GenerationCacheKey(seed=seed,side=side,players=players,mode=mode,archetype=archetype,modifiers=(),engine_revision='v1.5-stable')
            requests.append({'row':row,'key':key})
        if errors:raise ValueError('\n'.join(errors))
        return requests

    def _batch_set_running_controls(self,running):
        state='disabled' if running else 'normal';self.batch_generate_button.configure(state=state)
        self._batch_count_spin.configure(state=state);self._batch_randomize_button.configure(state=state)
        self._batch_common_seed_entry.configure(state=state);self._batch_common_seed_random.configure(state=state);self._batch_apply_seed_button.configure(state=state)
        self._batch_start_button.configure(state=state);self._batch_cancel_button.configure(state='normal' if running else 'disabled')
        for row in self._batch_rows:
            for widget,normal_state in row['input_widgets']:widget.configure(state='disabled' if running else normal_state)

    def _start_batch(self):
        if self._batch_running:return
        try:requests=self._batch_collect_requests()
        except ValueError as exc:
            messagebox.showerror(self._batch_text('invalid_title'),str(exc),parent=self._batch_window);return
        self._batch_queue=list(requests);self._batch_active_count=len(requests);self._batch_running=True;self._batch_cancel_requested=False;self._batch_active_row=None;self._batch_last_success=None
        for request in requests:
            row=request['row'];row['result']=None;row['cached']=False;row['error']='';row.pop('preview_image',None);row.pop('thumbnail_photo',None);row['thumbnail'].configure(image='',text=str(row['index']))
            self._batch_update_progress(row,0,self._batch_text('waiting'),'waiting')
            row['show'].configure(state='disabled');row['set_a'].configure(state='disabled');row['set_b'].configure(state='disabled')
        self._batch_set_running_controls(True);self._batch_summary_var.set(self._batch_text('running',current=1,total=len(requests)))
        self.after(20,self._batch_run_next)

    def _batch_run_next(self):
        if not self._batch_running:return
        if self._batch_cancel_requested:
            while self._batch_queue:
                request=self._batch_queue.pop(0);row=request['row'];self._batch_update_progress(row,100,self._batch_text('cancelled'),'cancelled')
            self._finish_batch();return
        if not self._batch_queue:self._finish_batch();return
        request=self._batch_queue.pop(0);row=request['row'];key=request['key'];self._batch_active_row=row
        total=self._batch_active_count
        done=sum(1 for r in self._batch_rows[:total] if r['state'] in ('success','cached','failed','cancelled'))
        self._batch_summary_var.set(self._batch_text('running',current=min(total,done+1),total=total))
        self._batch_update_progress(row,2,self._batch_text('generating'),'running')
        try:
            out=self.session_cache.get(key);cached=out is not None
            if out is None:out=self.generator.generate(key.players,key.seed,mode=key.mode,archetype=key.archetype)
            self.session_cache.put(key,out);row['result']=out;row['cached']=cached;self._batch_last_success=out
            self._batch_update_progress(row,100,self._batch_text('cached' if cached else 'success'),'cached' if cached else 'success');self._batch_render_thumbnail(row)
        except Exception as exc:
            row['error']=str(exc);self._batch_update_progress(row,100,self._batch_text('failed',error=str(exc)),'failed')
        finally:
            self._batch_active_row=None;self._refresh_history();self.after(30,self._batch_run_next)

    def _cancel_batch(self):
        if not self._batch_running:return
        self._batch_cancel_requested=True;self._batch_cancel_button.configure(state='disabled');self._batch_summary_var.set(self._batch_text('cancel_pending'))

    def _finish_batch(self):
        active=self._batch_rows[:self._batch_active_count]
        success=sum(row['state'] in ('success','cached') for row in active);failed=sum(row['state']=='failed' for row in active);cancelled=sum(row['state']=='cancelled' for row in active)
        self._batch_running=False;self._batch_active_row=None;self._batch_set_running_controls(False);self._batch_summary_var.set(self._batch_text('finished',success=success,failed=failed,cancelled=cancelled))
        for row in active:
            enabled='normal' if row['state'] in ('success','cached') and row.get('result') is not None else 'disabled'
            row['show'].configure(state=enabled);row['set_a'].configure(state=enabled);row['set_b'].configure(state=enabled)
        self._refresh_history();self._refresh_batch_assignment_buttons()
        if self._batch_last_success is not None:
            self.current=self._batch_last_success;self.import_source=None;self._populate_current();self._invalidate_preview();self._refresh_preview(True)
        self._feedback('batch_done','success' if failed==0 else 'warning',success=success,failed=failed,cancelled=cancelled)

    def _batch_show_result(self,row):
        out=row.get('result')
        if out is None:return
        self.current=out;self.import_source=None;self._populate_current();self._invalidate_preview();self._refresh_preview(True)

    def _batch_assign_result(self,row,slot):
        out=row.get('result')
        if out is None:return
        action,other=self._set_compare_output(slot,out)
        key='moved' if action=='moved' else ('already_assigned' if action=='already' else 'assigned')
        values={'index':row['index'],'slot':slot}
        if other:values['other']=other
        self._batch_summary_var.set(self._batch_text(key,**values))

    def _close_batch_window(self):
        if self._batch_running:
            self._cancel_batch();self._batch_summary_var.set(self._batch_text('close_running'));return
        if self._batch_window is not None:
            try:self._batch_window.destroy()
            except tk.TclError:pass
        self._batch_cancel_hover_preview();self._batch_hide_preview_tooltip()
        self._batch_window=None;self._batch_rows=[];self.batch_generate_button.configure(state='normal')

    def generate(self):
        try:
            side=int(self.size.get())
            if side!=768:raise NotImplementedError(f'La génération {side}×{side} est réservée mais pas encore calibrée. Max joueurs={NATIVE_LIMITS[side]}.')
            key=self._cache_key();cached=self.session_cache.get(key);self.import_source=None;lang=self.prefs.get('language','fr')
            mode=MODE_LABELS[lang][key.mode];arch=ARCHETYPE_LABELS[lang][key.archetype];modifiers=self._modifier_summary()
            if cached is not None:
                self.current=cached;self._populate_current();self._invalidate_preview();self._refresh_preview(True);self._refresh_history();self._feedback('cache_hit','success',seed=key.seed);return
            msg=FEEDBACK_TEXT[lang]['generating'].format(archetype=arch,mode=mode,modifiers=modifiers,side=side,players=int(self.players.get()),seed=int(self.seed.get()))
            self._task_begin(msg,2);self.current=self.generator.generate(int(self.players.get()),int(self.seed.get()),mode=self._mode_key(),archetype=self._arch_key())
            self.session_cache.put(key,self.current);self._refresh_history();self._task_progress(97,'Finalisation de l’aperçu…' if lang=='fr' else 'Finalizing preview…');self._populate_current();self._invalidate_preview();self._refresh_preview(True)
            done=FEEDBACK_TEXT[lang]['generated'].format(archetype=arch,mode=mode,modifiers=modifiers,side=side,players=int(self.players.get()),seed=int(self.seed.get()));self._task_done(done)
        except Exception as e:
            import traceback;self._task_error('Erreur de génération' if self.prefs.get('language','fr')=='fr' else 'Generation error');messagebox.showerror('MapGen',f'{e}\n\n{traceback.format_exc()}')
    def _load_history(self):
        key=self._history_lookup.get(self.history_var.get());out=self.session_cache.get(key) if key else None
        if out is not None:
            need_stats=self.session_stats_cache.get(out.state) is None
            if need_stats:self._task_begin('Chargement de l’historique…' if self.prefs.get('language','fr')=='fr' else 'Loading history…',10)
            self.current=out;self.import_source=None;self._populate_current();self._invalidate_preview();self._refresh_preview(True)
            if need_stats:self._task_done(FEEDBACK_TEXT[self.prefs.get('language','fr')]['history_loaded'])
            else:self._feedback('history_loaded','success')
        else:self._feedback('history_empty','warning')
    def _clear_history(self):self.session_cache.clear();self.session_stats_cache.clear();self._history_lookup.clear();self.history_combo.configure(values=[]);self.history_var.set('');self._feedback('history_cleared','success')
    def _set_compare_slot(self,slot):
        if not self.current:return
        self._set_compare_output(slot,self.current)
    def _set_compare_output(self,slot,out):
        if out is None:return 'ignored',None
        if self._compare_slots.get(slot) is out:
            self._compare_active=slot;self._refresh_compare_label();lang=self.prefs.get('language','fr')
            self._feedback_key=None;self._status_kind='info';self.status.set((f'Cette carte est déjà affectée à {slot}.' if lang=='fr' else f'This map is already assigned to {slot}.'));getattr(self,'_sync_status_display',lambda:None)();return 'already',None
        other='B' if slot=='A' else 'A';moved=self._compare_slots.get(other) is out
        if moved:self._compare_slots[other]=None
        need_stats=self.session_stats_cache.get(out.state) is None
        if need_stats:self._task_begin((f'Préparation comparaison {slot}…' if self.prefs.get('language','fr')=='fr' else f'Preparing comparison {slot}…'),10)
        self._compare_slots[slot]=out;self._compare_active=slot;self._stats_for_output(out);self._refresh_compare_label();self._refresh_stats_chart()
        lang=self.prefs.get('language','fr');message=((f'Carte déplacée de {other} vers {slot}.' if lang=='fr' else f'Map moved from {other} to {slot}.') if moved else (f'Comparaison {slot} prête.' if lang=='fr' else f'Comparison {slot} ready.'))
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
                button.configure(text=(f'Définir {slot}' if lang=='fr' else f'Set {slot}'),image=self._compare_led_off)
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

    def _refresh_batch_assignment_buttons(self):
        for row in getattr(self,'_batch_rows',[]):
            out=row.get('result')
            for slot,key in (('A','set_a'),('B','set_b')):
                button=row.get(key)
                if button is not None:
                    try:button.configure(image=self._compare_led_on if out is not None and self._compare_slots.get(slot) is out else self._compare_led_off)
                    except tk.TclError:pass
    def _refresh_compare_label(self):
        # Compatibility helper kept for existing callers; identity is now shown only on the LED buttons.
        self._refresh_compare_buttons();self._refresh_stats_chart()
    def _clear_compare_slot(self,slot):
        if slot not in self._compare_slots:return
        self._compare_slots[slot]=None
        if self._compare_active==slot:self._compare_active=None
        self._refresh_compare_label()
        lang=self.prefs.get('language','fr')
        self._feedback_key=None;self._status_kind='success';self.status.set((f'Comparaison {slot} vidée' if lang=='fr' else f'Comparison {slot} cleared'));getattr(self,'_sync_status_display',lambda:None)()
    def _clear_compare_slots(self):
        self._compare_slots={'A':None,'B':None};self._compare_active=None
        self._refresh_compare_label()
        self._feedback_key=None;self._status_kind='success';self.status.set('Comparaisons A/B vidées' if self.prefs.get('language','fr')=='fr' else 'A/B comparisons cleared');getattr(self,'_sync_status_display',lambda:None)()
    def _toggle_compare(self):
        a,b=self._compare_slots['A'],self._compare_slots['B']
        if a is None or b is None:
            self._feedback_key=None;self._status_kind='warning';self.status.set('Définissez A et B avant la bascule.' if self.prefs.get('language','fr')=='fr' else 'Set both A and B before toggling.');getattr(self,'_sync_status_display',lambda:None)();return
        self._compare_active='B' if self._compare_active!='B' else 'A';self.current=self._compare_slots[self._compare_active];imported=bool(self.current.state.metadata.get('source_format'));self._populate_current(imported=imported);self._invalidate_preview();self._refresh_preview(False);self._feedback('compare_toggled','info',map=f'{self._compare_active} · {self._output_label(self.current)}')

    def _render_options(self):
        view=self._view_key();return {'view':view,'overlay_alpha':100 if view=='global' else int(self.opacity_var.get()),'projection':self.prefs['projection'],'heatmap_resource':self._heatmap_key()}
    def _invalidate_preview(self):
        """Discard both the colorized square layer and its projected composites."""
        self._preview_base=None;self._preview_key=None;self._preview_layer_base=None;self._preview_layer_key=None;self._preview_projection_cache={}
    def _invalidate_preview_composite(self):
        """Keep the costly colorized layer and discard only cheap decorations."""
        self._preview_base=None;self._preview_key=None;self._preview_projection_cache={}
    def _refresh_preview(self,reset_pan=False):
        self._zoom_after=None
        if not self.current:return
        self._update_view_controls();opts=self._render_options();state=self.current.state
        # Global and Starts share the same marker-free terrain raster.  Starts
        # opacity affects only its sprite layer, so changing it never recolors
        # the map.  Other overlays bake their opacity into the square layer.
        layer_view='global' if opts['view'] in ('global','starts') else opts['view']
        layer_alpha=100 if layer_view=='global' else opts['overlay_alpha']
        layer_key=(id(state),layer_view,layer_alpha,opts['heatmap_resource'])
        if layer_key!=self._preview_layer_key:
            self._preview_layer_base=render_square_base(state,layer_view,layer_alpha,opts['heatmap_resource']);self._preview_layer_key=layer_key;self._preview_projection_cache={}
        composite_key=(opts['projection'],opts['view'],opts['overlay_alpha'])
        if composite_key not in self._preview_projection_cache:
            self._preview_projection_cache[composite_key]=compose_rendered_map(self._preview_layer_base,state,labels=True,view=opts['view'],overlay_alpha=opts['overlay_alpha'],projection=opts['projection'])
        self._preview_base=self._preview_projection_cache[composite_key];self._preview_key=(layer_key,composite_key)
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
        self.prefs['shortcuts']=vals;self._save_prefs();self._bind_shortcuts();self._feedback('shortcut_applied','success')
    def _reset_one_shortcut(self,cmd):
        self.shortcut_vars[cmd].set(DEFAULT_SHORTCUTS[cmd]);self._apply_shortcut_settings()
    def _reset_shortcut_settings(self):
        for k,v in DEFAULT_SHORTCUTS.items():self.shortcut_vars[k].set(v)
        self.prefs['shortcuts']=dict(DEFAULT_SHORTCUTS);self._save_prefs();self._bind_shortcuts();self._feedback('shortcut_restored','success')
    def _show_help(self):
        sc=self.prefs.get('shortcuts',DEFAULT_SHORTCUTS);lang=self.prefs.get('language','fr');lines=[]
        for cmd in DEFAULT_SHORTCUTS:lines.append(f"{COMMAND_LABELS[lang][cmd]} : {sc.get(cmd,DEFAULT_SHORTCUTS[cmd])}")
        extra='\n\nMolette : zoom\nClic gauche + glisser : déplacer\nCache : 8 générations, mémoire de session uniquement.\nA/B : conserve vue, zoom, projection et overlay.' if lang=='fr' else '\n\nWheel: zoom\nLeft drag: pan\nCache: 8 generations, session memory only.\nA/B preserves view, zoom, projection and overlay.'
        messagebox.showinfo('Aide / Help','\n'.join(lines)+extra)

    def export(self):
        self._open_map_export_center()

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
            except Exception as error:self._task_error('Erreur export' if lang=='fr' else 'Export error');messagebox.showerror(text['map_title'],str(error),parent=self)
        export_button.configure(command=perform)
        for var in (folder,basename,*formats.values()):var.trace_add('write',refresh)
        refresh();self._place_export_center(w);self._activate_export_modal(w)

def main():App().mainloop()
