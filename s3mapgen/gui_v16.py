from __future__ import annotations
import random
import shutil
import hashlib
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
from .session_cache import GenerationCacheKey, ImportedHistoryKey, SessionGenerationCache, SessionStatsCache
from .stats_analysis import analyze_map, format_stats_report, stats_json, stats_csv
from .stats_charts import render_stats_chart, CHART_KEYS, CHART_LABELS
from .export_center import safe_export_basename, map_export_capabilities, map_export_paths, stats_export_paths, existing_export_paths
from .native_titlebar import apply_native_titlebar
from .shortcuts import canonicalize_shortcut, shortcut_from_event, shortcut_to_tk

VIEWS.clear()
VIEWS.update({'Global':'global','Départs':'starts','Territoires':'territories','Élévation':'heightmap','Ressources':'resources','Chemins':'paths','Cultures':'crops','Carte thermique':'heatmap'})

VIEW_LABELS={
 'fr':{'global':'Global','starts':'Départs','territories':'Territoires','heightmap':'Élévation','resources':'Ressources','paths':'Chemins','crops':'Cultures','heatmap':'Carte thermique'},
 'en':{'global':'Global','starts':'Starts','territories':'Territories','heightmap':'Elevation','resources':'Resources','paths':'Paths','crops':'Crops','heatmap':'Heatmap'},
}
LANGUAGE_LABELS={'fr':'Français','en':'English','de':'Deutsch','es':'Español'}
WINDOW_TITLES={
 'fr':'Settlers III MapGen v1.8 DEV_8_R4 — moteur de génération v1.5',
 'en':'Settlers III MapGen v1.8 DEV_8_R4 — generation engine v1.5',
 'de':'Settlers III MapGen v1.8 DEV_8_R4 — Generierungs-Engine v1.5',
 'es':'Settlers III MapGen v1.8 DEV_8_R4 — motor de generación v1.5',
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
 'fr':{'generate':'Générer','generate_batch':'Générer un lot','import':'Importer','export':'Exporter','save_preview':'Enregistrer l’aperçu PNG','manage_history':'Gérer l’historique','reset_view':'Recentrer','copy_seed':'Copier le seed','toggle_ab':'Basculer A/B','clear_compare':'Vider A+B','toggle_theme':'Basculer thème','help':'Aide'},
 'en':{'generate':'Generate','generate_batch':'Generate batch','import':'Import','export':'Export','save_preview':'Save PNG preview','manage_history':'Manage history','reset_view':'Reset view','copy_seed':'Copy seed','toggle_ab':'Toggle A/B','clear_compare':'Clear A+B','toggle_theme':'Toggle theme','help':'Help'},
}

SHORTCUT_UI_TEXT={
 'fr':{'capture':'Appuyez sur les touches…','disabled':'Désactivé','disable':'Désactiver','reset':'Réinitialiser','apply':'Appliquer','defaults':'Valeurs par défaut','hint':'Cliquez sur un raccourci puis appuyez sur la combinaison. Échap annule ; Suppr ou Retour arrière désactive.','title':'Raccourcis','pending':'Modifications non appliquées.','conflict_summary':'Conflit à corriger avant application.','pending_tip':'Modification non appliquée.','conflict_tip':'« {shortcut} » est aussi affecté à : {actions}.','invalid_tip':'Combinaison invalide.','help_title':'Aide','action':'Action','shortcut':'Raccourci','navigation':'Navigation','close':'Fermer','wheel':'Molette : zoom','drag':'Clic gauche + glisser : déplacer la carte','cache':'Historique : capacité configurable, mémoire de session uniquement.','compare':'A/B conserve vue, zoom, projection et couche.'},
 'en':{'capture':'Press the keys…','disabled':'Disabled','disable':'Disable','reset':'Reset','apply':'Apply','defaults':'Defaults','hint':'Click a shortcut, then press the combination. Escape cancels; Delete or Backspace disables it.','title':'Shortcuts','pending':'Unapplied changes.','conflict_summary':'Resolve the conflict before applying.','pending_tip':'Unapplied change.','conflict_tip':'“{shortcut}” is also assigned to: {actions}.','invalid_tip':'Invalid combination.','help_title':'Help','action':'Action','shortcut':'Shortcut','navigation':'Navigation','close':'Close','wheel':'Mouse wheel: zoom','drag':'Left click + drag: move the map','cache':'History: configurable capacity, session memory only.','compare':'A/B preserves view, zoom, projection and overlay.'},
 'de':{'capture':'Tasten drücken…','disabled':'Deaktiviert','disable':'Deaktivieren','reset':'Zurücksetzen','apply':'Übernehmen','defaults':'Standardwerte','hint':'Klicken Sie auf ein Tastenkürzel und drücken Sie die Kombination. Escape bricht ab; Entf oder Rücktaste deaktiviert.','title':'Tastenkürzel','pending':'Nicht übernommene Änderungen.','conflict_summary':'Konflikt vor dem Übernehmen beheben.','pending_tip':'Nicht übernommene Änderung.','conflict_tip':'„{shortcut}“ ist auch zugewiesen an: {actions}.','invalid_tip':'Ungültige Kombination.','help_title':'Hilfe','action':'Aktion','shortcut':'Tastenkürzel','navigation':'Navigation','close':'Schließen','wheel':'Mausrad: Zoom','drag':'Linksklick + Ziehen: Karte verschieben','cache':'Verlauf: konfigurierbare Kapazität, nur Sitzungsspeicher.','compare':'A/B behält Ansicht, Zoom, Projektion und Ebene bei.'},
 'es':{'capture':'Pulsa las teclas…','disabled':'Desactivado','disable':'Desactivar','reset':'Restablecer','apply':'Aplicar','defaults':'Valores predeterminados','hint':'Haz clic en un atajo y pulsa la combinación. Escape cancela; Supr o Retroceso lo desactiva.','title':'Atajos','pending':'Cambios sin aplicar.','conflict_summary':'Resuelve el conflicto antes de aplicar.','pending_tip':'Cambio sin aplicar.','conflict_tip':'«{shortcut}» también está asignado a: {actions}.','invalid_tip':'Combinación no válida.','help_title':'Ayuda','action':'Acción','shortcut':'Atajo','navigation':'Navegación','close':'Cerrar','wheel':'Rueda: zoom','drag':'Clic izquierdo + arrastrar: mover el mapa','cache':'Historial: capacidad configurable, solo memoria de sesión.','compare':'A/B conserva vista, zoom, proyección y capa.'},
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
 'Charger':{'en':'Load'},'Vider cache':{'en':'Clear cache'},'Gérer…':{'en':'Manage…'},"Capacité de l'historique":{'en':'History capacity'},'Cartes conservées uniquement pendant cette session.':{'en':'Maps are kept for this session only.'},'Définir A':{'en':'Set A'},'Définir B':{'en':'Set B'},'Basculer A/B':{'en':'Toggle A/B'},
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

# DEV_6: complete four-language catalog.  French remains the source text used
# while constructing widgets; every other language resolves through the same
# stable semantic keys, with English as the explicit safety fallback.
VIEW_LABELS.update({
 'de':{'global':'Global','starts':'Startpositionen','territories':'Territorien','heightmap':'Höhen','resources':'Ressourcen','paths':'Wege','crops':'Anbau','heatmap':'Heatmap'},
 'es':{'global':'Global','starts':'Inicios','territories':'Territorios','heightmap':'Elevación','resources':'Recursos','paths':'Caminos','crops':'Cultivos','heatmap':'Mapa de calor'},
})
HEATMAP_LABELS.update({
 'de':{'trees':'Bäume','building_stones':'Bausteine','fish':'Fische','coal':'Kohle','iron':'Eisen','gold':'Gold','gems':'Edelsteine','sulfur':'Schwefel'},
 'es':{'trees':'Árboles','building_stones':'Piedras de construcción','fish':'Peces','coal':'Carbón','iron':'Hierro','gold':'Oro','gems':'Gemas','sulfur':'Azufre'},
})
MODE_LABELS.update({
 'de':{'legacy':'Klassisch (Legacy)','upgraded':'Verbessert (Upgraded)','custom':'Benutzerdefiniert'},
 'es':{'legacy':'Clásico (Legacy)','upgraded':'Mejorado (Upgraded)','custom':'Personalizado'},
})
ARCHETYPE_LABELS.update({
 'de':{'continental':'Kontinental','large_islands':'Große Inseln','small_islands':'Kleine Inseln'},
 'es':{'continental':'Continental','large_islands':'Islas grandes','small_islands':'Islas pequeñas'},
})
COMMAND_LABELS.update({
 'de':{'generate':'Generieren','generate_batch':'Stapel generieren','import':'Importieren','export':'Exportieren','save_preview':'PNG-Vorschau speichern','manage_history':'Verlauf verwalten','reset_view':'Ansicht zentrieren','copy_seed':'Seed kopieren','toggle_ab':'A/B wechseln','clear_compare':'A+B leeren','toggle_theme':'Design wechseln','help':'Hilfe'},
 'es':{'generate':'Generar','generate_batch':'Generar lote','import':'Importar','export':'Exportar','save_preview':'Guardar vista previa PNG','manage_history':'Gestionar historial','reset_view':'Centrar vista','copy_seed':'Copiar seed','toggle_ab':'Alternar A/B','clear_compare':'Vaciar A+B','toggle_theme':'Cambiar tema','help':'Ayuda'},
})
THEME_LABELS.update({'de':{'dark':'Dunkel','light':'Hell'},'es':{'dark':'Oscuro','light':'Claro'}})
PROJECTION_LABELS.update({'de':{'square':'Quadratisch','parallelogram':'Parallelogramm'},'es':{'square':'Cuadrada','parallelogram':'Paralelogramo'}})
PREVIEW_START_MARKER_LABELS.update({
 'de':{'hidden':'Ausgeblendet','small':'Klein','normal':'Normal'},
 'es':{'hidden':'Ocultos','small':'Pequeños','normal':'Normales'},
})

_TEXTS_DE_ES={
 'Mode':('Modus','Modo'),'Archétype':('Archetyp','Arquetipo'),'Modificateurs':('Modifikatoren','Modificadores'),'Taille':('Größe','Tamaño'),'Joueurs':('Spieler','Jugadores'),'Seed':('Seed','Seed'),'Zoom':('Zoom','Zoom'),
 'Générer':('Generieren','Generar'),'Générer lot…':('Stapel generieren…','Generar lote…'),'Importer…':('Importieren…','Importar…'),'Exporter…':('Exportieren…','Exportar…'),'Aperçu PNG':('PNG-Vorschau','Vista previa PNG'),'Vue':('Ansicht','Vista'),
 'Affichage':('Anzeige','Visualización'),'Thème':('Design','Tema'),'Opacité couche':('Ebenendeckkraft','Opacidad de capa'),'0 % = map globale · 100 % = couche seule':('0 % = globale Karte · 100 % = nur Ebene','0 % = mapa global · 100 % = solo capa'),
 'Projection':('Projektion','Proyección'),'Le parallélogramme modifie uniquement le rendu, jamais les données.':('Das Parallelogramm ändert nur die Darstellung, niemals die Daten.','El paralelogramo solo cambia la visualización, nunca los datos.'),
 'Marqueurs dans les aperçus':('Marker in Vorschauen','Marcadores en vistas previas'),'Ce réglage affecte les miniatures et le grand aperçu du lot.':('Diese Einstellung betrifft Miniaturen und die große Stapelvorschau.','Este ajuste afecta a las miniaturas y a la vista previa grande del lote.'),
 'Sensibilité molette':('Mausrad-Empfindlichkeit','Sensibilidad de la rueda'),'Navigation':('Navigation','Navegación'),'Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.':('Mausrad: zoomen\nLinksklick + Ziehen: Karte verschieben\nDer Zoom wird verzögert, um Neuberechnungen zu begrenzen.','Rueda: zoom\nClic izquierdo + arrastrar: mover el mapa\nEl zoom se retrasa para limitar los recálculos.'),
 'Paramètres':('Einstellungen','Ajustes'),'Validations':('Prüfungen','Validaciones'),'Pipeline':('Pipeline','Proceso'),'Métadonnées':('Metadaten','Metadatos'),'Statistiques':('Statistiken','Estadísticas'),'Graphiques':('Diagramme','Gráficos'),'Exporter JSON':('JSON exportieren','Exportar JSON'),'Exporter CSV':('CSV exportieren','Exportar CSV'),'Exporter PNG':('PNG exportieren','Exportar PNG'),'Ressource Heatmap':('Heatmap-Ressource','Recurso del mapa de calor'),'Filtre carte thermique':('Heatmap-Filter','Filtro del mapa de calor'),
 'Recentrer':('Zentrieren','Centrar'),'Copier seed':('Seed kopieren','Copiar seed'),'Langue':('Sprache','Idioma'),'Aide':('Hilfe','Ayuda'),'Historique session':('Sitzungsverlauf','Historial de sesión'),
 'Charger':('Laden','Cargar'),'Vider cache':('Cache leeren','Vaciar caché'),'Définir A':('A festlegen','Definir A'),'Définir B':('B festlegen','Definir B'),'Basculer A/B':('A/B wechseln','Alternar A/B'),
 'Gérer…':('Verwalten…','Gestionar…'),"Capacité de l'historique":('Verlaufskapazität','Capacidad del historial'),'Cartes conservées uniquement pendant cette session.':('Karten werden nur während dieser Sitzung gespeichert.','Los mapas se conservan solo durante esta sesión.'),
 'Vider A':('A leeren','Vaciar A'),'Vider B':('B leeren','Vaciar B'),'Vider A+B':('A+B leeren','Vaciar A+B'),
 'Raccourcis':('Tastenkürzel','Atajos'),'Appliquer':('Übernehmen','Aplicar'),'Valeurs par défaut':('Standardwerte','Valores predeterminados'),'Réinitialiser':('Zurücksetzen','Restablecer'),
 'Session / Comparaison':('Sitzung / Vergleich','Sesión / Comparación'),'Format : Ctrl+G, Ctrl+Shift+C, Alt+1, F1…':('Format: Strg+G, Strg+Umschalt+C, Alt+1, F1…','Formato: Ctrl+G, Ctrl+Mayús+C, Alt+1, F1…'),
}
for _source,(_de,_es) in _TEXTS_DE_ES.items():
    TEXTS[_source].update({'de':_de,'es':_es})

FEEDBACK_TEXT.update({
 'de':{
  'ready':'Bereit — {mode} / {archetype} / Modifikatoren: {modifiers} / {side}×{side} / {players} Spieler.','size_reserved':'{side}×{side}: max. {max_players} Spieler. Auswahl bereit; Generierung noch nicht kalibriert.','mode_reserved':'Modus „{mode}“ ist reserviert und nicht implementiert.','arch_reserved':'Archetyp „{archetype}“ ist reserviert und nicht implementiert.','generating':'Generiere {archetype} — {mode} — Modifikatoren: {modifiers} — {side}×{side} — {players} Spieler — Seed {seed}…','generated':'Karte generiert — {archetype} / {mode} / Modifikatoren: {modifiers} / {side}×{side} / {players} Spieler / Seed {seed}.','cache_hit':'Ergebnis aus dem Cache wiederverwendet — Seed {seed}.','heatmap_locked':'Der Filter ist in der Ansicht „Heatmap“ verfügbar.','history_loaded':'Karte aus dem Sitzungsverlauf geladen.','history_cleared':'Sitzungs-Caches geleert.','shortcut_applied':'Tastenkürzel übernommen.','shortcut_restored':'Tastenkürzel auf Standardwerte zurückgesetzt.','seed_copied':'Seed kopiert: {seed}','export_done':'Export abgeschlossen.','history_empty':'Keine Karte im Sitzungs-Cache verfügbar.','compare_toggled':'Karte zu {map} gewechselt.','theme_changed':'Design geändert: {theme}.','view_reset':'Ansicht zentriert.','seed_randomized':'Neuer zufälliger Seed: {seed}','graph_exported':'Diagrammexport abgeschlossen: {format} — {file}','opacity_locked':'Die Deckkraft ist in der globalen Ansicht nicht verfügbar.','modifier_none':'Kein Modifikator aktiv.','batch_opened':'Stapelgenerierung bereit — 1 bis 4 Karten konfigurieren.','batch_done':'Stapel abgeschlossen — {success} erfolgreich, {failed} fehlgeschlagen, {cancelled} abgebrochen.',
 },
 'es':{
  'ready':'Listo — {mode} / {archetype} / modificadores: {modifiers} / {side}×{side} / {players} jugadores.','size_reserved':'{side}×{side}: máx. {max_players} jugadores. Selección lista; generación aún no calibrada.','mode_reserved':'El modo «{mode}» está reservado y no implementado.','arch_reserved':'El arquetipo «{archetype}» está reservado y no implementado.','generating':'Generando {archetype} — {mode} — modificadores: {modifiers} — {side}×{side} — {players} jugadores — seed {seed}…','generated':'Mapa generado — {archetype} / {mode} / modificadores: {modifiers} / {side}×{side} / {players} jugadores / seed {seed}.','cache_hit':'Resultado reutilizado desde la caché — seed {seed}.','heatmap_locked':'El filtro está disponible en la vista «Mapa de calor».','history_loaded':'Mapa cargado desde el historial de sesión.','history_cleared':'Cachés de sesión vaciadas.','shortcut_applied':'Atajos aplicados.','shortcut_restored':'Atajos restablecidos a sus valores predeterminados.','seed_copied':'Seed copiada: {seed}','export_done':'Exportación terminada.','history_empty':'No hay mapas disponibles en la caché de sesión.','compare_toggled':'Mapa cambiado a {map}.','theme_changed':'Tema cambiado: {theme}.','view_reset':'Vista centrada.','seed_randomized':'Nueva seed aleatoria: {seed}','graph_exported':'Exportación del gráfico terminada: {format} — {file}','opacity_locked':'La opacidad no está disponible en la vista Global.','modifier_none':'No hay modificadores activos.','batch_opened':'Generación por lotes lista — configura de 1 a 4 mapas.','batch_done':'Lote terminado — {success} correctos, {failed} fallidos, {cancelled} cancelados.',
 },
})

BATCH_TEXT.update({
 'de':{
  'title':'Stapelgenerierung','count':'Anzahl Karten','randomize':'Neue Seeds','apply_seed':'Auf alle anwenden','map':'Karte {index}','mode':'Modus','archetype':'Archetyp','modifiers':'Modifikatoren','size':'Größe','players':'Spieler','seed':'Seed','status':'Status','waiting':'Wartend','generating':'Generierung…','cached':'Aus Cache wiederverwendet','success':'Abgeschlossen','failed':'Fehler: {error}','cancelled':'Abgebrochen','start':'Stapel generieren','cancel':'Wartende Karten abbrechen','close':'Schließen','set_a':'A zuweisen','set_b':'B zuweisen','show':'Anzeigen','none':'Keine','invalid_title':'Ungültige Stapelparameter','invalid_row':'Karte {index}: {error}','unsupported_size':'derzeit kann nur 768×768 generiert werden','unsupported_mode':'Modus ist nicht implementiert','unsupported_archetype':'Archetyp ist nicht implementiert','invalid_players':'ungültige Spielerzahl (2 bis {maximum})','invalid_seed':'ganzzahliger Seed erforderlich','running':'Stapel läuft: Karte {current}/{total}','cancel_pending':'Abbruch nach der aktuellen Karte angefordert.','finished':'Stapel abgeschlossen: {success} erfolgreich, {failed} fehlgeschlagen, {cancelled} abgebrochen.','assigned':'Karte {index} wurde {slot} zugewiesen.','moved':'Karte {index} wurde von {other} nach {slot} verschoben.','already_assigned':'Karte {index} ist bereits {slot} zugewiesen.','preview_hint':'Klicken oder 700 ms verweilen zum Vergrößern.','close_preview':'Vorschau schließen','close_running':'Der Stapel läuft; wartende Karten werden abgebrochen.',
 },
 'es':{
  'title':'Generación por lotes','count':'Número de mapas','randomize':'Nuevas seeds','apply_seed':'Aplicar a todos','map':'Mapa {index}','mode':'Modo','archetype':'Arquetipo','modifiers':'Modificadores','size':'Tamaño','players':'Jugadores','seed':'Seed','status':'Estado','waiting':'En espera','generating':'Generando…','cached':'Reutilizado desde la caché','success':'Terminado','failed':'Error: {error}','cancelled':'Cancelado','start':'Generar lote','cancel':'Cancelar mapas pendientes','close':'Cerrar','set_a':'Asignar a A','set_b':'Asignar a B','show':'Mostrar','none':'Ninguno','invalid_title':'Parámetros del lote no válidos','invalid_row':'Mapa {index}: {error}','unsupported_size':'actualmente solo se puede generar 768×768','unsupported_mode':'el modo no está implementado','unsupported_archetype':'el arquetipo no está implementado','invalid_players':'número de jugadores no válido (2 a {maximum})','invalid_seed':'se requiere una seed entera','running':'Lote en curso: mapa {current}/{total}','cancel_pending':'Cancelación solicitada después del mapa actual.','finished':'Lote terminado: {success} correctos, {failed} fallidos, {cancelled} cancelados.','assigned':'Mapa {index} asignado a {slot}.','moved':'Mapa {index} movido de {other} a {slot}.','already_assigned':'El mapa {index} ya está asignado a {slot}.','preview_hint':'Haz clic o mantén el cursor 700 ms para ampliar.','close_preview':'Cerrar vista previa','close_running':'El lote está en curso; se cancelarán los mapas pendientes.',
 },
})

EXPORT_TEXT.update({
 'de':{
  'map_title':'Karte exportieren','stats_title':'Statistiken und Diagramm exportieren','folder':'Ordner','browse':'Durchsuchen…','basename':'Basisname','formats':'Formate','files':'Geplante Dateien','none':'Mindestens ein Format auswählen.','cancel':'Abbrechen','export':'Exportieren','overwrite_title':'Vorhandene Dateien','overwrite':'Diese Dateien sind bereits vorhanden:\n\n{files}\n\nErsetzen?','invalid_name':'Der Basisname ist leer oder ungültig.','invalid_folder':'Einen gültigen Ausgabeordner auswählen.','done':'Export abgeschlossen:\n\n{files}','edm':'Editor-Karte (.EDM)','map':'Spielbare Karte (.MAP)','sav':'Unveränderte Quell-SAV (.SAV)','png_global':'Globale Karte, aktive Projektion (.PNG)','png_current':'Aktuelle Ansicht mit Ebenen (.PNG)','json':'Vollständige Statistiken (.JSON)','csv':'Vollständige Statistiken (.CSV)','png':'Aktuell angezeigtes Diagramm (.PNG)','binary_unavailable':'EDM/MAP nicht verfügbar: kein validiertes Scaffold für diese Größe.','sav_unavailable':'SAV nicht verfügbar: nur eine unveränderte Kopie einer importierten SAV ist erlaubt.','sav_exact':'Die SAV wird Byte für Byte kopiert; es wird kein SAV-Writer verwendet.','current_unavailable':'Aktuelle Ansicht nicht verfügbar: mit Global wäre sie identisch mit dem globalen PNG.','safe_name':'Mit Windows inkompatible Zeichen werden durch „_“ ersetzt.',
 },
 'es':{
  'map_title':'Exportar mapa','stats_title':'Exportar estadísticas y gráfico','folder':'Carpeta','browse':'Examinar…','basename':'Nombre base','formats':'Formatos','files':'Archivos previstos','none':'Selecciona al menos un formato.','cancel':'Cancelar','export':'Exportar','overwrite_title':'Archivos existentes','overwrite':'Estos archivos ya existen:\n\n{files}\n\n¿Reemplazarlos?','invalid_name':'El nombre base está vacío o no es válido.','invalid_folder':'Selecciona una carpeta de salida válida.','done':'Exportación terminada:\n\n{files}','edm':'Mapa del editor (.EDM)','map':'Mapa jugable (.MAP)','sav':'SAV de origen sin cambios (.SAV)','png_global':'Mapa global, proyección activa (.PNG)','png_current':'Vista actual con sus capas (.PNG)','json':'Estadísticas completas (.JSON)','csv':'Estadísticas completas (.CSV)','png':'Gráfico mostrado actualmente (.PNG)','binary_unavailable':'EDM/MAP no disponibles: no existe un scaffold validado para este tamaño.','sav_unavailable':'SAV no disponible: solo se permite una copia sin cambios de un SAV importado.','sav_exact':'El SAV se copia byte por byte; no se utiliza ningún writer SAV.','current_unavailable':'Vista actual no disponible: con Global sería idéntica al PNG Global.','safe_name':'Los caracteres incompatibles con Windows se sustituyen por «_».',
 },
})

NONE_LABELS={'fr':'Aucun','en':'None','de':'Keine','es':'Ninguno'}
LOWER_NONE_LABELS={'fr':'aucun','en':'none','de':'keine','es':'ninguno'}
BATCH_HINTS={'fr':'1–4 cartes · paramètres indépendants · génération séquentielle','en':'1–4 maps · independent parameters · sequential generation','de':'1–4 Karten · unabhängige Parameter · sequenzielle Generierung','es':'1–4 mapas · parámetros independientes · generación secuencial'}

HISTORY_TEXT={
 'fr':{'title':'Centre d’historique','origin':'Origine','map':'Carte','details':'Détails','preview':'Aperçu sélectionné','generated':'Génération','batch':'Lot','imported':'Import','show':'Afficher','set_a':'Affecter à A','set_b':'Affecter à B','delete':'Supprimer','clear':'Tout vider','close':'Fermer','empty':'Aucune carte dans cette session.','none':'Aucun','current':'Carte actuellement affichée','comparison':'Slot de comparaison : {slots}','mru':'Position MRU : {position}/{total}','source':'Source : {path}','protected':'Protégée : {reasons}','main_view':'vue principale','outside_history':'Carte affichée hors historique','confirm_clear':'Vider entièrement l’historique de session ?','confirm_clear_protected':'Des cartes sont protégées par : {reasons}. Les slots A/B seront libérés et la carte affichée restera visible hors historique. Continuer ?','delete_assigned':'Cette carte est protégée par : {reasons}. Sa suppression libérera ses slots A/B et, si elle est affichée, la laissera visible hors historique. Continuer ?','deleted':'Entrée supprimée de l’historique.','capacity':'{used} / {count} cartes · mémoire de session uniquement','capacity_reduce':'Réduire la capacité de {old} à {new} supprimera {removed} carte(s) ancienne(s) non protégée(s). Continuer ?'},
 'en':{'title':'History Center','origin':'Origin','map':'Map','details':'Details','preview':'Selected preview','generated':'Generated','batch':'Batch','imported':'Import','show':'Show','set_a':'Assign to A','set_b':'Assign to B','delete':'Delete','clear':'Clear all','close':'Close','empty':'No map in this session.','none':'None','current':'Currently displayed map','comparison':'Comparison slot: {slots}','mru':'MRU position: {position}/{total}','source':'Source: {path}','protected':'Protected: {reasons}','main_view':'main viewer','outside_history':'Displayed map outside history','confirm_clear':'Clear the entire session history?','confirm_clear_protected':'Maps are protected by: {reasons}. A/B slots will be cleared and the displayed map will remain visible outside history. Continue?','delete_assigned':'This map is protected by: {reasons}. Deleting it will clear its A/B slots and, if displayed, leave it visible outside history. Continue?','deleted':'History entry deleted.','capacity':'{used} / {count} maps · session memory only','capacity_reduce':'Reducing capacity from {old} to {new} will remove {removed} older unprotected map(s). Continue?'},
 'de':{'title':'Verlaufszentrum','origin':'Quelle','map':'Karte','details':'Details','preview':'Ausgewählte Vorschau','generated':'Generiert','batch':'Stapel','imported':'Import','show':'Anzeigen','set_a':'A zuweisen','set_b':'B zuweisen','delete':'Löschen','clear':'Alles leeren','close':'Schließen','empty':'Keine Karte in dieser Sitzung.','none':'Keine','current':'Aktuell angezeigte Karte','comparison':'Vergleichsplatz: {slots}','mru':'MRU-Position: {position}/{total}','source':'Quelle: {path}','protected':'Geschützt: {reasons}','main_view':'Hauptansicht','outside_history':'Angezeigte Karte außerhalb des Verlaufs','confirm_clear':'Den gesamten Sitzungsverlauf leeren?','confirm_clear_protected':'Karten sind geschützt durch: {reasons}. A/B werden freigegeben; die angezeigte Karte bleibt außerhalb des Verlaufs sichtbar. Fortfahren?','delete_assigned':'Diese Karte ist geschützt durch: {reasons}. Beim Löschen werden A/B freigegeben; eine angezeigte Karte bleibt außerhalb des Verlaufs sichtbar. Fortfahren?','deleted':'Verlaufseintrag gelöscht.','capacity':'{used} / {count} Karten · nur Sitzungsspeicher','capacity_reduce':'Die Verringerung von {old} auf {new} entfernt {removed} ältere ungeschützte Karte(n). Fortfahren?'},
 'es':{'title':'Centro de historial','origin':'Origen','map':'Mapa','details':'Detalles','preview':'Vista previa seleccionada','generated':'Generación','batch':'Lote','imported':'Importación','show':'Mostrar','set_a':'Asignar a A','set_b':'Asignar a B','delete':'Eliminar','clear':'Vaciar todo','close':'Cerrar','empty':'No hay mapas en esta sesión.','none':'Ninguno','current':'Mapa mostrado actualmente','comparison':'Ranura de comparación: {slots}','mru':'Posición MRU: {position}/{total}','source':'Origen: {path}','protected':'Protegido: {reasons}','main_view':'visor principal','outside_history':'Mapa mostrado fuera del historial','confirm_clear':'¿Vaciar todo el historial de sesión?','confirm_clear_protected':'Hay mapas protegidos por: {reasons}. Se vaciarán A/B y el mapa mostrado seguirá visible fuera del historial. ¿Continuar?','delete_assigned':'Este mapa está protegido por: {reasons}. Al eliminarlo se vaciarán sus ranuras A/B y, si está mostrado, seguirá visible fuera del historial. ¿Continuar?','deleted':'Entrada eliminada del historial.','capacity':'{used} / {count} mapas · solo memoria de sesión','capacity_reduce':'Reducir la capacidad de {old} a {new} eliminará {removed} mapa(s) antiguo(s) no protegido(s). ¿Continuar?'},
}

_CONTEXT_TEXT={
 'fr':{'loaded':'Chargée !','shown':'Affichée !','assigned_a':'Affectée à A !','assigned_b':'Affectée à B !','lock_tip':'Protection : {roles}','viewer_role':'V = vue principale','manual_role':'M = verrouillage manuel','outside_tip':'Cette carte reste affichée, mais elle ne se trouve plus dans le cache de session.'},
 'en':{'loaded':'Loaded!','shown':'Shown!','assigned_a':'Assigned to A!','assigned_b':'Assigned to B!','lock_tip':'Protection: {roles}','viewer_role':'V = main viewer','manual_role':'M = manual lock','outside_tip':'This map is still displayed, but is no longer in the session cache.'},
 'de':{'loaded':'Geladen!','shown':'Angezeigt!','assigned_a':'A zugewiesen!','assigned_b':'B zugewiesen!','lock_tip':'Schutz: {roles}','viewer_role':'V = Hauptansicht','manual_role':'M = manuelle Sperre','outside_tip':'Diese Karte wird noch angezeigt, befindet sich aber nicht mehr im Sitzungscache.'},
 'es':{'loaded':'¡Cargado!','shown':'¡Mostrado!','assigned_a':'¡Asignado a A!','assigned_b':'¡Asignado a B!','lock_tip':'Protección: {roles}','viewer_role':'V = visor principal','manual_role':'M = bloqueo manual','outside_tip':'Este mapa sigue mostrándose, pero ya no está en la caché de sesión.'},
}

_BATCH_CAPACITY_TEXT={
 'fr':{'title':'Capacité du cache dépassée','intro':'Si toutes les cartes réussissent, ce lot modifiera le cache de session ({used}/{capacity} actuellement).','existing':'• {count} carte(s) actuellement dans l’historique en sortiront.','batch':'• {count} résultat(s) du lot ne resteront pas dans le cache.','kept':'Tous les résultats resteront consultables dans cette fenêtre jusqu’à sa fermeture.','question':'Continuer la génération ?','continue':'Continuer','cancel':'Annuler'},
 'en':{'title':'Cache capacity exceeded','intro':'If every map succeeds, this batch will modify the session cache (currently {used}/{capacity}).','existing':'• {count} map(s) currently in history will be removed.','batch':'• {count} batch result(s) will not remain in the cache.','kept':'All results remain available in this window until it is closed.','question':'Continue generation?','continue':'Continue','cancel':'Cancel'},
 'de':{'title':'Cache-Kapazität überschritten','intro':'Wenn alle Karten erfolgreich sind, verändert dieser Stapel den Sitzungscache (aktuell {used}/{capacity}).','existing':'• {count} derzeitige Verlaufskarte(n) werden entfernt.','batch':'• {count} Stapelergebnis(se) bleiben nicht im Cache.','kept':'Alle Ergebnisse bleiben bis zum Schließen dieses Fensters verfügbar.','question':'Generierung fortsetzen?','continue':'Fortfahren','cancel':'Abbrechen'},
 'es':{'title':'Capacidad de caché superada','intro':'Si todos los mapas se completan, este lote modificará la caché de sesión (actualmente {used}/{capacity}).','existing':'• {count} mapa(s) del historial actual saldrán de la caché.','batch':'• {count} resultado(s) del lote no permanecerán en la caché.','kept':'Todos los resultados seguirán disponibles en esta ventana hasta cerrarla.','question':'¿Continuar la generación?','continue':'Continuar','cancel':'Cancelar'},
}

_BATCH_RETENTION_TEXT={
 'fr':{'not_cached':'Terminée · non conservée dans le cache','finished_retention':'Lot terminé : {success} réussie(s), {failed} erreur(s), {cancelled} annulée(s) · {lost} résultat(s) hors cache.'},
 'en':{'not_cached':'Complete · not retained in cache','finished_retention':'Batch complete: {success} succeeded, {failed} failed, {cancelled} cancelled · {lost} result(s) outside cache.'},
 'de':{'not_cached':'Fertig · nicht im Cache behalten','finished_retention':'Stapel abgeschlossen: {success} erfolgreich, {failed} Fehler, {cancelled} abgebrochen · {lost} Ergebnis(se) außerhalb des Caches.'},
 'es':{'not_cached':'Completado · no conservado en caché','finished_retention':'Lote terminado: {success} correctos, {failed} errores, {cancelled} cancelados · {lost} resultado(s) fuera de la caché.'},
}
for _lang,_values in _BATCH_RETENTION_TEXT.items():BATCH_TEXT[_lang].update(_values)

_HISTORY_CAPACITY_DIALOG_TEXT={
 'fr':{'title':'Réduire la capacité de l’historique','continue':'Réduire','cancel':'Annuler'},
 'en':{'title':'Reduce history capacity','continue':'Reduce','cancel':'Cancel'},
 'de':{'title':'Verlaufskapazität verringern','continue':'Verringern','cancel':'Abbrechen'},
 'es':{'title':'Reducir la capacidad del historial','continue':'Reducir','cancel':'Cancelar'},
}

# One semantic palette drives both built-in themes.  New UI blocks should use
# these roles (or one of the named ttk styles below) instead of embedding colors.
THEME_PALETTES={
 'dark':{'window':'#202124','panel':'#292a2d','surface':'#303134','surface_alt':'#34363a','field':'#303134','text':'#e8eaed','muted':'#aeb4bc','disabled':'#7f858d','border':'#5f6368','hover':'#3c4043','pressed':'#4a4d51','selection':'#315f86','selection_text':'#ffffff','primary':'#2f7ed8','success':'#34a853','warning':'#f9ab00','danger':'#d93025','info':'#8ab4f8','canvas':'#111214','titlebar':'#15171a','titlebar_text':'#e8eaed','titlebar_border':'#3c4043','titlebar_separator':'#6f7378','titlebar_dark':True},
 'light':{'window':'#f2f2f2','panel':'#e5e5e5','surface':'#ffffff','surface_alt':'#f5f6f7','field':'#ffffff','text':'#202124','muted':'#5f6368','disabled':'#8a8f98','border':'#aeb3b8','hover':'#d8e3f3','pressed':'#c5d7ee','selection':'#3d6f9b','selection_text':'#ffffff','primary':'#2459a9','success':'#238636','warning':'#b26a00','danger':'#c5221f','info':'#2459a9','canvas':'#d6d6d6','titlebar':'#dfe3e8','titlebar_text':'#202124','titlebar_border':'#aeb3b8','titlebar_separator':'#8f969e','titlebar_dark':False},
}

def _lang_text(lang,fr,en,de,es):
    return {'fr':fr,'en':en,'de':de,'es':es}.get(lang,en)

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
    elif kind=='flag_de':
        x0,y0,x1,y1=2,4,size-3,size-5;third=max(1,(y1-y0+1)//3)
        d.rectangle((x0,y0,x1,y0+third-1),fill='#000000');d.rectangle((x0,y0+third,x1,y0+2*third-1),fill='#dd0000');d.rectangle((x0,y0+2*third,x1,y1),fill='#ffce00');d.rectangle((x0,y0,x1,y1),outline='#111111')
    elif kind=='flag_es':
        x0,y0,x1,y1=2,4,size-3,size-5;quarter=max(1,(y1-y0+1)//4)
        d.rectangle((x0,y0,x1,y0+quarter-1),fill='#aa151b');d.rectangle((x0,y0+quarter,x1,y1-quarter),fill='#f1bf00');d.rectangle((x0,y1-quarter+1,x1,y1),fill='#aa151b');d.rectangle((x0,y0,x1,y1),outline='#111111')
    elif kind=='lock_closed':
        d.rounded_rectangle((4,8,size-4,size-3),radius=2,fill=c,outline='#111111');d.arc((5,2,size-5,11),180,360,fill=c,width=3);d.ellipse((8,11,10,13),fill='#ffffff')
    elif kind=='lock_open':
        d.rounded_rectangle((4,8,size-4,size-3),radius=2,fill=c,outline='#111111');d.arc((7,2,size-2,11),180,315,fill=c,width=3);d.ellipse((8,11,10,13),fill='#ffffff')
    elif kind=='status_on':
        d.ellipse((0,0,size-1,size-1),fill=c,outline='#111111',width=1)
        d.line((size*0.23,size*0.52,size*0.43,size*0.71,size*0.77,size*0.29),fill='#ffffff',width=max(2,size//6),joint='curve')
    elif kind=='status_off':
        d.ellipse((2,2,size-3,size-3),fill='#ffffff',outline='#111111',width=1)
        d.ellipse((4,4,size-5,size-5),fill=None,outline=c,width=max(2,size//7))
    elif kind=='warning':
        d.polygon(((size//2,1),(size-2,size-3),(2,size-3)),fill=c,outline='#111111')
        d.line((size//2,5,size//2,size-8),fill='#111111',width=max(2,size//8));d.ellipse((size//2-1,size-6,size//2+1,size-4),fill='#111111')
    elif kind=='conflict':
        d.ellipse((1,1,size-2,size-2),fill=c,outline='#111111',width=1)
        d.line((size//2,4,size//2,size-7),fill='#ffffff',width=max(2,size//7));d.ellipse((size//2-1,size-5,size//2+1,size-3),fill='#ffffff')
    elif kind=='pending':
        d.ellipse((1,1,size-2,size-2),fill=c,outline='#111111',width=1)
        cx=size//2;cy=size//2;d.line((cx,4,cx,cy),fill='#202124',width=max(2,size//9));d.line((cx,cy,size-5,cy+3),fill='#202124',width=max(2,size//9));d.ellipse((cx-1,cy-1,cx+1,cy+1),fill='#202124')
    elif kind=='blank':
        pass
    else:
        # Generic resource swatch: double outline avoids black/white disappearing.
        d.ellipse((1,1,size-2,size-2),fill='#ffffff',outline='#111111',width=1)
        d.ellipse((3,3,size-4,size-4),fill=c,outline='#444444' if c.lower()!='#101010' else '#eeeeee',width=1)
    return ImageTk.PhotoImage(im,master=master)


def _thumbnail_with_magnifier(image,state='idle'):
    """Composite a large translucent magnifier without an opaque backing box."""
    base=image.convert('RGBA');overlay=Image.new('RGBA',base.size,(0,0,0,0));draw=ImageDraw.Draw(overlay)
    short=max(1,min(base.size));radius=max(12,round(short*.17));handle=max(10,round(short*.14));cx=base.width//2-4;cy=base.height//2-4
    alpha={'idle':58,'hover':205,'active':238,'preview_hover':236,'close_hover':245}.get(state,58)
    accent={'idle':(245,248,252,alpha),'hover':(138,190,255,alpha),'active':(72,210,128,alpha),'preview_hover':(178,132,255,alpha),'close_hover':(255,184,92,alpha)}.get(state,(245,248,252,alpha))
    shadow=(0,0,0,min(170,alpha+42));fill=(12,20,28,22 if state=='idle' else 50)
    box=(cx-radius,cy-radius,cx+radius,cy+radius);width=max(3,round(short*.035))
    draw.ellipse((box[0]+2,box[1]+2,box[2]+2,box[3]+2),fill=(0,0,0,28),outline=shadow,width=width+2)
    draw.ellipse(box,fill=fill,outline=accent,width=width)
    start=(cx+round(radius*.68),cy+round(radius*.68));end=(start[0]+handle,start[1]+handle)
    draw.line((start[0]+2,start[1]+2,end[0]+2,end[1]+2),fill=shadow,width=width+3)
    draw.line((*start,*end),fill=accent,width=width, joint='curve')
    if state in ('active','preview_hover'):
        inner=max(4,radius//3);draw.ellipse((cx-inner,cy-inner,cx+inner,cy+inner),outline=(255,255,255,225),width=max(2,width//2))
        if state=='preview_hover':draw.ellipse((cx-2,cy-2,cx+2,cy+2),fill=(255,255,255,225))
    elif state=='close_hover':
        inner=max(5,radius//3);cross=max(3,inner//2);draw.line((cx-cross,cy-cross,cx+cross,cy+cross),fill=(255,255,255,235),width=max(2,width//2));draw.line((cx+cross,cy-cross,cx-cross,cy+cross),fill=(255,255,255,235),width=max(2,width//2))
    return Image.alpha_composite(base,overlay)


def _history_role_icon(master,roles,size=15):
    """Compact, explicit padlocks for Viewer/A/B and the reserved Manual role."""
    roles=tuple(roles);gap=1;width=max(1,len(roles)*(size+gap)-gap)
    im=Image.new('RGBA',(width,size),(0,0,0,0));d=ImageDraw.Draw(im)
    colors={'V':'#2f7ed8','A':'#34a853','B':'#9b59d0','M':'#d59b28'}
    for index,role in enumerate(roles):
        x=index*(size+gap);color=colors.get(role,'#7b8088')
        d.arc((x+4,0,x+size-5,size-6),180,360,fill='#111111',width=4)
        d.arc((x+4,0,x+size-5,size-6),180,360,fill=color,width=2)
        d.rounded_rectangle((x+1,6,x+size-2,size-1),radius=2,fill=color,outline='#111111',width=1)
        d.text((x+size//2,10),role,fill='#ffffff',anchor='mm',stroke_width=1,stroke_fill='#111111')
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
        self._manual_history_locks=[]
        self.session_cache.set_protected_provider(lambda:(getattr(self,'current',None),self._compare_slots.get('A'),self._compare_slots.get('B'),*self._manual_history_locks))
        self._preview_layer_base=None;self._preview_layer_key=None;self._preview_projection_cache={};self._prefs_save_after=None
        self._display_origin=(0,0);self._display_factor=1.0;self._display_base_size=(1,1);self._bound_shortcuts=[];self._task_dialog=None;self._task_overlay=None;self._task_overlay_value=0;self._task_overlay_detail='';self._status_kind='ready';self._feedback_key=None;self._feedback_values={};self._responsive_mode=None;self._layout_after=None
        self._batch_window=None;self._batch_rows=[];self._batch_queue=[];self._batch_running=False;self._batch_cancel_requested=False;self._batch_active_row=None;self._batch_last_success=None;self._batch_active_count=0
        self._batch_preview_window=None;self._batch_preview_label=None;self._batch_preview_photo=None;self._batch_preview_row=None;self._batch_preview_pinned=False;self._batch_preview_projection=None;self._batch_preview_drag_origin=None;self._batch_preview_zoom=1.0;self._batch_hover_after=None;self._batch_i18n={}
        self._map_export_window=None;self._stats_export_window=None
        self._history_window=None;self._history_tree=None;self._history_center_lookup={};self._history_window_widgets={};self._history_preview_photo=None;self._history_preview_key=None
        self._history_large_window=None;self._history_large_label=None;self._history_large_photo=None;self._history_large_image=None;self._history_large_key=None;self._history_large_zoom=.72;self._history_large_drag_origin=None;self._history_large_pinned=False;self._history_hover_after=None;self._history_preview_hover=False
        self._history_role_icons={};self._ui_tooltip_window=None;self._ui_tooltip_key=None
        self._history_capacity_dialog=None;self._history_capacity_dialog_widgets={}
        self._help_window=None;self._help_widgets={};self._shortcut_capture_command=None;self._shortcut_capture_modifiers=set();self._shortcut_row_states={};self._scroll_tab_surfaces=[]
        self._magnifier_hover_kind=None;self._magnifier_hover_ref=None;self._magnifier_active_kind=None;self._magnifier_active_ref=None
        self._native_titlebar_after=None
        super().__init__()
        self.session_cache.resize(self.prefs.get('history_capacity',8))
        self.bind_class('Toplevel','<Map>',self._native_titlebar_mapped,add='+')
        self._apply_initial_window_geometry();self._apply_language();self._bind_shortcuts();self.bind('<Configure>',self._schedule_responsive_layout,add='+');self.bind('<Escape>',self._close_large_preview_escape,add='+');self.after_idle(self._apply_responsive_layout);self._schedule_native_titlebar_refresh()

    def _native_titlebar_mapped(self,event):
        self._schedule_native_titlebar_refresh()

    def _schedule_native_titlebar_refresh(self):
        if self._native_titlebar_after is not None:
            try:self.after_cancel(self._native_titlebar_after)
            except tk.TclError:pass
        self._native_titlebar_after=self.after_idle(self._refresh_native_titlebars)

    def _refresh_native_titlebars(self):
        self._native_titlebar_after=None
        palette=getattr(self,'_ui_theme_colors',None)
        if not palette:return
        targets=[self,*[w for w in self._walk(self) if isinstance(w,tk.Toplevel)]]
        seen=set()
        for target in targets:
            if target is None or id(target) in seen:continue
            seen.add(id(target))
            apply_native_titlebar(target,palette)

    def _close_large_preview_escape(self,event=None):
        closed=False
        if self._batch_preview_window is not None:self._batch_hide_preview_tooltip();closed=True
        if self._history_large_window is not None:self._history_hide_large_preview();closed=True
        return 'break' if closed else None

    def _scroll_notebook_tab(self,title):
        """Create a tab whose content remains reachable at compact dimensions."""
        host=ttk.Frame(self.nb);self.nb.add(host,text=title);host.rowconfigure(0,weight=1);host.columnconfigure(0,weight=1)
        canvas=tk.Canvas(host,highlightthickness=0,borderwidth=0)
        hbar=ttk.Scrollbar(host,orient='horizontal',command=canvas.xview);vbar=ttk.Scrollbar(host,orient='vertical',command=canvas.yview);canvas.configure(xscrollcommand=hbar.set,yscrollcommand=vbar.set)
        canvas.grid(row=0,column=0,sticky='nsew')
        inner=ttk.Frame(canvas,padding=14);item=canvas.create_window((0,0),window=inner,anchor='nw')
        def refresh(_event=None):
            try:
                required_w=max(1,inner.winfo_reqwidth());required_h=max(1,inner.winfo_reqheight());available_w=max(1,canvas.winfo_width());available_h=max(1,canvas.winfo_height())
                canvas.itemconfigure(item,width=max(required_w,available_w));canvas.configure(scrollregion=canvas.bbox('all'))
                if required_w>available_w+1:
                    if not hbar.winfo_ismapped():hbar.grid(row=1,column=0,sticky='ew')
                elif hbar.winfo_ismapped():hbar.grid_remove();canvas.xview_moveto(0)
                if required_h>available_h+1:
                    if not vbar.winfo_ismapped():vbar.grid(row=0,column=1,sticky='ns')
                elif vbar.winfo_ismapped():vbar.grid_remove();canvas.yview_moveto(0)
            except tk.TclError:pass
        inner.bind('<Configure>',refresh,add='+');canvas.bind('<Configure>',refresh,add='+')
        self._scroll_tab_surfaces.append(canvas);return inner

    def _settings_tab(self):
        """Build v1.8 display settings, including preview-only start markers."""
        f=self._scroll_notebook_tab('Paramètres');f.columnconfigure(1,weight=1)
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
        ttk.Label(f,text="Capacité de l'historique").grid(row=8,column=0,sticky='w',pady=(14,6))
        self.history_capacity_var=tk.StringVar(value=str(self.prefs.get('history_capacity',8)))
        self.history_capacity_combo=ttk.Combobox(f,textvariable=self.history_capacity_var,values=('4','8','12','16'),state='readonly',width=8)
        self.history_capacity_combo.grid(row=8,column=1,sticky='w');self.history_capacity_combo.bind('<<ComboboxSelected>>',lambda e:self._history_capacity_changed())
        ttk.Label(f,text='Cartes conservées uniquement pendant cette session.',style='Hint.TLabel',wraplength=360).grid(row=9,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Sensibilité molette').grid(row=10,column=0,sticky='w',pady=(14,6))
        self.wheel_var=tk.DoubleVar(value=float(self.prefs['wheel_zoom']))
        self.wheel_scale=ttk.Scale(f,from_=1.04,to=1.20,variable=self.wheel_var,command=lambda v:self._wheel_changed());self.wheel_scale.grid(row=10,column=1,sticky='ew')
        self.wheel_label=ttk.Label(f,text=f"×{self.wheel_var.get():.2f}",width=7);self.wheel_label.grid(row=10,column=2,padx=(8,0))
        ttk.Separator(f).grid(row=11,column=0,columnspan=3,sticky='ew',pady=16)
        ttk.Label(f,text='Navigation',style='Section.TLabel').grid(row=12,column=0,columnspan=3,sticky='w')
        ttk.Label(f,text='Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.',style='Hint.TLabel',justify='left').grid(row=13,column=0,columnspan=3,sticky='w',pady=(6,0))

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
        self.lang_combo.set_items([
            ('fr',LANGUAGE_LABELS['fr'],'#0055a4','flag_fr'),('en',LANGUAGE_LABELS['en'],'#21468b','flag_en'),
            ('de',LANGUAGE_LABELS['de'],'#000000','flag_de'),('es',LANGUAGE_LABELS['es'],'#aa151b','flag_es'),
        ])
        self.help_button=ttk.Button(self.global_panel,text='Aide',command=self._show_help)
        self._theme_button=ttk.Button(self.global_panel,command=self._toggle_theme,width=3)
        self._refresh_theme_button_icon()

        # Session/Comparison is the middle region in wide mode and becomes one
        # coherent full-width block below the header only in compact mode.
        self.session_box=ttk.LabelFrame(self._header_shell,text='Session / Comparaison',padding=(6,4))
        self.session_history_label=ttk.Label(self.session_box,text='Historique session');self.session_history_label.grid(row=0,column=0,sticky='w')
        self.history_var=tk.StringVar(value='');self.history_combo=ttk.Combobox(self.session_box,textvariable=self.history_var,state='readonly',width=27)
        self.history_combo.bind('<<ComboboxSelected>>',lambda e:self._refresh_state_indicators())
        self.history_load_button=ttk.Button(self.session_box,text='Charger',command=self._load_history)
        self.history_clear_button=ttk.Button(self.session_box,text='Vider cache',command=self._clear_history)
        self.history_manage_button=ttk.Button(self.session_box,text='Gérer…',command=self._open_history_center)
        self._compare_led_off=_selector_icon(self,'#7b8088','status_off',18);self._compare_led_on=_selector_icon(self,'#34a853','status_on',18)
        self._history_blank_icon=_selector_icon(self,'#7b8088','blank',16)
        self._history_outside_icon=_selector_icon(self,'#f2b84b','warning',18)
        self.history_residency_label=ttk.Label(self.session_box,image='',cursor='hand2')
        self.history_residency_label.bind('<Button-1>',lambda e:self._history_residency_hint())
        self.history_residency_label.bind('<Enter>',lambda e:self._history_residency_tooltip())
        self.history_residency_label.bind('<Leave>',lambda e:self._hide_ui_tooltip())
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
        widgets=(self.history_combo,self.history_load_button,self.history_clear_button,self.history_manage_button,self.history_residency_label,self.compare_a_button,self.compare_b_button,self.compare_toggle_button,self.clear_a_button,self.clear_b_button,self.clear_ab_button)
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
        self.history_manage_button.grid(row=1,column=3,padx=2,pady=(4,0),sticky='w')
        self.history_residency_label.grid(row=1,column=0,padx=(2,0),pady=(4,0))
        self.compare_toggle_button.grid(row=1,column=4,padx=2,pady=(4,0),sticky='w')
        self.clear_ab_button.grid(row=1,column=5,columnspan=2,padx=(3,2),pady=(4,0),sticky='w')

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
            tip=_lang_text(self.prefs.get('language','fr'),'Passer au thème clair','Switch to light theme','Zum hellen Design wechseln','Cambiar al tema claro')
        else:
            c=(75,95,145,255);d.ellipse((4,3,16,17),fill=c);d.ellipse((8,1,18,13),fill=(0,0,0,0))
            tip=_lang_text(self.prefs.get('language','fr'),'Passer au thème sombre','Switch to dark theme','Zum dunklen Design wechseln','Cambiar al tema oscuro')
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
            if getattr(self,'_task_overlay',None) is not None:self._task_progress(82,_lang_text(self.prefs.get('language','fr'),'Calcul des statistiques…','Computing statistics…','Statistiken werden berechnet…','Calculando estadísticas…'))
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
        self._refresh_stats_chart();self._refresh_state_indicators();self._refresh_history_preview()

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
        f=self._scroll_notebook_tab('Raccourcis');f.columnconfigure(1,weight=1)
        self.shortcut_vars={};self.shortcut_display_vars={};self.shortcut_labels={};self.shortcut_capture_buttons={};self.shortcut_disable_buttons={};self.shortcut_reset_buttons={};self.shortcut_status_labels={};lang=self.prefs.get('language','fr');text=SHORTCUT_UI_TEXT[lang]
        self._shortcut_pending_icon=_selector_icon(f,'#f2b84b','pending',22);self._shortcut_conflict_icon=_selector_icon(f,'#e04444','conflict',22);self._shortcut_blank_icon=_selector_icon(f,'#7b8088','blank',22)
        for row,cmd in enumerate(DEFAULT_SHORTCUTS):
            lbl=ttk.Label(f,text=COMMAND_LABELS[lang][cmd]);lbl.grid(row=row,column=0,sticky='w',pady=4);self.shortcut_labels[cmd]=lbl
            var=tk.StringVar(value=self.prefs.get('shortcuts',{}).get(cmd,DEFAULT_SHORTCUTS[cmd]));self.shortcut_vars[cmd]=var
            display=tk.StringVar();self.shortcut_display_vars[cmd]=display
            capture=ttk.Button(f,textvariable=display,command=lambda c=cmd:self._start_shortcut_capture(c));capture.grid(row=row,column=1,sticky='ew',padx=(10,8),pady=4);capture.bind('<KeyPress>',lambda e,c=cmd:self._capture_shortcut_key(c,e));capture.bind('<KeyRelease>',lambda e,c=cmd:self._release_shortcut_key(c,e));self.shortcut_capture_buttons[cmd]=capture
            disable=ttk.Button(f,text=text['disable'],command=lambda c=cmd:self._disable_shortcut(c));disable.grid(row=row,column=2,sticky='e',padx=(0,6),pady=4);self.shortcut_disable_buttons[cmd]=disable
            btn=ttk.Button(f,text=text['reset'],command=lambda c=cmd:self._reset_one_shortcut(c));btn.grid(row=row,column=3,sticky='e',pady=4);self.shortcut_reset_buttons[cmd]=btn
            status=ttk.Label(f,image=self._shortcut_blank_icon,cursor='hand2');status.grid(row=row,column=4,padx=(7,0));status.bind('<Enter>',lambda e,c=cmd:self._shortcut_status_tooltip(c));status.bind('<Leave>',lambda e:self._hide_ui_tooltip());self.shortcut_status_labels[cmd]=status
            var.trace_add('write',lambda *_args,c=cmd:self._shortcut_values_changed(c))
            self._refresh_shortcut_capture_text(cmd)
        r=len(DEFAULT_SHORTCUTS)
        self.shortcut_apply_button=ttk.Button(f,text=text['apply'],command=self._apply_shortcut_settings);self.shortcut_apply_button.grid(row=r,column=0,pady=(12,0),sticky='w')
        self.shortcut_defaults_button=ttk.Button(f,text=text['defaults'],command=self._reset_shortcut_settings);self.shortcut_defaults_button.grid(row=r,column=1,pady=(12,0),sticky='w',padx=(10,0))
        self.shortcut_hint_label=ttk.Label(f,text=text['hint'],wraplength=720);self.shortcut_hint_label.grid(row=r+1,column=0,columnspan=4,sticky='w',pady=(8,0))
        self.shortcut_pending_label=ttk.Label(f,text='',style='ShortcutPending.TLabel',compound='left');self.shortcut_pending_label.grid(row=r+2,column=0,columnspan=5,sticky='w',pady=(7,0))
        self._refresh_shortcut_validation()

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
        return NONE_LABELS.get(self.prefs.get('language','fr'),NONE_LABELS['en'])
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
            try:w.configure(text=source if lang=='fr' else TEXTS[source].get(lang,TEXTS[source].get('en',source)))
            except tk.TclError:pass
        for tab,source in getattr(self,'_i18n_tabs',[]):self.nb.tab(tab,text=source if lang=='fr' else TEXTS[source].get(lang,TEXTS[source].get('en',source)))
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
            try:self.modifier_menu.entryconfigure(0,label=NONE_LABELS.get(lang,NONE_LABELS['en']))
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
        shortcut_text=SHORTCUT_UI_TEXT[lang]
        for btn in getattr(self,'shortcut_reset_buttons',{}).values():btn.configure(text=shortcut_text['reset'])
        for btn in getattr(self,'shortcut_disable_buttons',{}).values():btn.configure(text=shortcut_text['disable'])
        if hasattr(self,'shortcut_apply_button'):self.shortcut_apply_button.configure(text=shortcut_text['apply'])
        if hasattr(self,'shortcut_defaults_button'):self.shortcut_defaults_button.configure(text=shortcut_text['defaults'])
        if hasattr(self,'shortcut_hint_label'):self.shortcut_hint_label.configure(text=shortcut_text['hint'])
        for cmd in getattr(self,'shortcut_vars',{}):self._refresh_shortcut_capture_text(cmd)
        self._refresh_shortcut_validation()
        if hasattr(self,'history_combo'):self._refresh_history()
        self._retranslate_history_center()
        self._retranslate_history_capacity_dialog()
        self._retranslate_help_window()
        self._update_view_controls();self._clear_inspector();self._retranslate_feedback()
    def _language_changed(self):
        selected=self.lang_var.get();self.prefs['language']=next((key for key,label in LANGUAGE_LABELS.items() if label==selected),'en');self._save_prefs();self._apply_language();self._retranslate_batch_window();self._refresh_preview(True)
    def _apply_theme(self):
        super()._apply_theme();dark=self.prefs.get('theme')=='dark';style=ttk.Style(self);palette=dict(THEME_PALETTES['dark' if dark else 'light'])
        field=palette['field'];fg=palette['text'];muted=palette['disabled'];panel=palette['panel']
        self._ui_theme_colors={**palette,'field':field,'fg':fg,'muted':muted,'panel':panel,'bar_bg':'#3c4043' if dark else '#dddddd','bar_fg':palette['success'],'dark':dark}
        # Global state maps prevent Windows native hover/focus colors from leaking
        # through newly created widgets. Named semantic styles remain available
        # for intentionally colored primary/status actions.
        style.configure('TFrame',background=palette['window']);style.configure('Card.TFrame',background=palette['panel'],relief='solid',borderwidth=1)
        style.configure('TLabel',background=palette['window'],foreground=fg);style.configure('Panel.TLabel',background=palette['panel'],foreground=fg);style.configure('PanelHint.TLabel',background=palette['panel'],foreground=palette['muted'])
        style.configure('ShortcutPending.TLabel',background=palette['window'],foreground=palette['warning'],font=('TkDefaultFont',9,'bold'))
        style.configure('ShortcutConflict.TLabel',background=palette['window'],foreground=palette['danger'],font=('TkDefaultFont',9,'bold'))
        style.configure('TLabelframe',background=palette['window'],bordercolor=palette['border']);style.configure('TLabelframe.Label',background=palette['window'],foreground=fg)
        style.configure('History.TLabelframe',background=palette['panel'],bordercolor=palette['border']);style.configure('History.TLabelframe.Label',background=palette['panel'],foreground=fg)
        style.configure('TButton',background=palette['surface'],foreground=fg,bordercolor=palette['border'],lightcolor=palette['border'],darkcolor=palette['border'])
        style.map('TButton',background=[('disabled',palette['panel']),('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('disabled',muted),('pressed',fg),('active',fg)])
        style.configure('TMenubutton',background=palette['surface'],foreground=fg,bordercolor=palette['border']);style.map('TMenubutton',background=[('disabled',palette['panel']),('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('disabled',muted),('active',fg)])
        for name,color in (('Primary',palette['primary']),('Success',palette['success']),('Warning',palette['warning']),('Danger',palette['danger'])):
            style.configure(f'{name}.TButton',background=color,foreground='#ffffff')
            style.map(f'{name}.TButton',background=[('disabled',palette['panel']),('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('disabled',muted),('pressed','#ffffff'),('active','#ffffff')])
        style.configure('TCheckbutton',background=palette['window'],foreground=fg);style.map('TCheckbutton',background=[('disabled',palette['window']),('pressed',palette['window']),('active',palette['window'])],foreground=[('disabled',muted),('active',fg)])
        style.configure('TRadiobutton',background=palette['window'],foreground=fg);style.map('TRadiobutton',background=[('disabled',palette['window']),('pressed',palette['window']),('active',palette['window'])],foreground=[('disabled',muted),('active',fg)])
        for widget_style in ('TEntry','TSpinbox','TCombobox'):
            style.configure(widget_style,fieldbackground=field,background=field,foreground=fg,selectbackground=palette['selection'],selectforeground=palette['selection_text'],bordercolor=palette['border'])
            style.map(widget_style,fieldbackground=[('disabled',palette['panel']),('readonly',field),('focus',field)],background=[('disabled',palette['panel']),('readonly',field),('active',palette['hover'])],foreground=[('disabled',muted),('readonly',fg)],selectbackground=[('readonly',palette['selection'])],selectforeground=[('readonly',palette['selection_text'])])
        style.configure('TNotebook.Tab',background=panel,foreground=fg);style.map('TNotebook.Tab',background=[('selected',field),('active',palette['hover']),('pressed',palette['pressed'])],foreground=[('disabled',muted),('selected',fg),('active',fg)])
        style.configure('Horizontal.TScale',background=palette['window'],troughcolor=palette['panel']);style.map('Horizontal.TScale',background=[('active',palette['primary']),('disabled',palette['disabled'])])
        style.configure('Vertical.TScrollbar',background=palette['surface'],troughcolor=palette['panel'],arrowcolor=fg,bordercolor=palette['border']);style.map('Vertical.TScrollbar',background=[('pressed',palette['pressed']),('active',palette['hover'])],arrowcolor=[('disabled',muted)])
        style.configure('Horizontal.TScrollbar',background=palette['surface'],troughcolor=palette['panel'],arrowcolor=fg,bordercolor=palette['border']);style.map('Horizontal.TScrollbar',background=[('pressed',palette['pressed']),('active',palette['hover'])],arrowcolor=[('disabled',muted)])
        style.configure('Treeview',background=palette['surface'],fieldbackground=palette['surface'],foreground=fg,bordercolor=palette['border'],rowheight=23)
        style.map('Treeview',background=[('selected',palette['selection'])],foreground=[('selected',palette['selection_text'])])
        style.configure('Treeview.Heading',background=panel,foreground=fg,bordercolor=palette['border'],relief='raised')
        style.map('Treeview.Heading',background=[('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('pressed',fg),('active',fg)])
        style.configure('History.Treeview',background=palette['surface'],fieldbackground=palette['surface'],foreground=fg,bordercolor=palette['border'],rowheight=24)
        style.map('History.Treeview',background=[('selected',palette['selection'])],foreground=[('selected',palette['selection_text'])])
        style.configure('History.Treeview.Heading',background=panel,foreground=fg,bordercolor=palette['border'],relief='raised')
        style.map('History.Treeview.Heading',background=[('pressed',palette['pressed']),('active',palette['hover'])],foreground=[('pressed',fg),('active',fg)])
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
        self._apply_history_window_theme()
        self._apply_history_capacity_dialog_theme()
        self._apply_help_window_theme()
        for surface in getattr(self,'_scroll_tab_surfaces',[]):
            try:surface.configure(background=palette['window'])
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
        self._schedule_native_titlebar_refresh()

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
        title=label.strip() if label else _lang_text(self.prefs.get('language','fr'),'Génération…','Generating…','Generierung…','Generando…')
        self._task_overlay_title=tk.Label(overlay,text=title,bg=panel,fg=fg,anchor='center',justify='center')
        self._task_overlay_title.pack(fill='x',padx=14,pady=(11,7))
        self._task_overlay_progress=tk.Canvas(overlay,height=24,bg=colors.get('bar_bg','#3c4043'),highlightthickness=0,bd=0)
        self._task_overlay_progress.pack(fill='x',expand=True,padx=14,pady=(0,12))
        self._task_overlay_value=max(0,min(100,float(value)));self._task_overlay_detail=_lang_text(self.prefs.get('language','fr'),'Initialisation…','Initializing…','Initialisierung…','Inicializando…')
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
        save_settings({'theme':self.prefs['theme'],'overlay_alpha':int(self.opacity_var.get()),'projection':self.prefs['projection'],'preview_start_markers':self.prefs.get('preview_start_markers','small'),'history_capacity':int(self.prefs.get('history_capacity',8)),'wheel_zoom':float(self.wheel_var.get()),'language':self.prefs.get('language','fr'),'shortcuts':self.prefs.get('shortcuts',dict(DEFAULT_SHORTCUTS))})

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
        self.prefs['projection']=self._projection_key();self._save_prefs();self._refresh_preview(True);self._refresh_batch_previews();self._refresh_history_preview()
    def _preview_marker_changed(self):
        self.prefs['preview_start_markers']=self._preview_marker_key();self._save_prefs();self._refresh_batch_previews();self._refresh_history_preview()

    def _history_capacity_changed(self):
        if self._history_capacity_dialog is not None:return
        old=int(self.prefs.get('history_capacity',8))
        try:value=int(self.history_capacity_var.get())
        except (TypeError,ValueError):value=old
        if value not in (4,8,12,16):value=old
        removed=max(0,len(self.session_cache)-value)
        if value<old and removed:
            if not self._show_history_capacity_warning(old,value,removed):
                self.history_capacity_var.set(str(old));return
        self.prefs['history_capacity']=value;self.session_cache.resize(value);self._save_prefs();self._refresh_history()

    def _show_history_capacity_warning(self,old,new,removed):
        if self._history_capacity_dialog is not None:return False
        lang=self.prefs.get('language','fr');dialog_text=_HISTORY_CAPACITY_DIALOG_TEXT[lang];history_text=HISTORY_TEXT[lang];result={'continue':False}
        parent=self._history_window or self;win=tk.Toplevel(parent);self._history_capacity_dialog=win;win.withdraw();win.title(dialog_text['title']);win.transient(parent);win.resizable(False,False)
        shell=ttk.Frame(win,padding=16);shell.pack(fill='both',expand=True)
        title=ttk.Label(shell,text=dialog_text['title'],style='Section.TLabel');title.pack(anchor='w',fill='x',pady=(0,10))
        message=ttk.Label(shell,text=history_text['capacity_reduce'].format(old=old,new=new,removed=removed),justify='left',wraplength=480);message.pack(anchor='w',fill='x')
        buttons=ttk.Frame(shell);buttons.pack(fill='x',pady=(16,0))
        def close(accepted=False):
            result['continue']=bool(accepted)
            try:win.grab_release()
            except tk.TclError:pass
            self._history_capacity_dialog=None;self._history_capacity_dialog_widgets={}
            try:self.history_capacity_combo.configure(state='readonly')
            except tk.TclError:pass
            win.destroy()
        cancel=ttk.Button(buttons,text=dialog_text['cancel'],command=lambda:close(False));cancel.pack(side='right')
        confirm=ttk.Button(buttons,text=dialog_text['continue'],command=lambda:close(True));confirm.pack(side='right',padx=(0,8))
        self._history_capacity_dialog_widgets={'title':title,'message':message,'cancel':cancel,'confirm':confirm,'old':old,'new':new,'removed':removed}
        win.protocol('WM_DELETE_WINDOW',lambda:close(False));win.bind('<Escape>',lambda e:close(False),add='+');win.bind('<Return>',lambda e:close(True),add='+')
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
            win.title(dialog_text['title']);widgets['title'].configure(text=dialog_text['title']);widgets['message'].configure(text=history_text['capacity_reduce'].format(old=widgets['old'],new=widgets['new'],removed=widgets['removed']))
            widgets['cancel'].configure(text=dialog_text['cancel']);widgets['confirm'].configure(text=dialog_text['continue'])
        except tk.TclError:pass

    def _apply_history_capacity_dialog_theme(self):
        win=self._history_capacity_dialog
        if win is None:return
        try:win.configure(background=getattr(self,'_ui_theme_colors',THEME_PALETTES['dark']).get('window','#202124'))
        except tk.TclError:pass

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
            if hasattr(self,'heatmap_title'):self.heatmap_title.configure(text='Filtre carte thermique' if lang=='fr' else TEXTS['Filtre carte thermique'].get(lang,TEXTS['Filtre carte thermique']['en']),image=self._lock_closed_icon if locked else self._lock_open_icon)
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
    def _refresh_history(self,preferred_index=None):
        self._history_lookup={}
        for key,_ in self.session_cache.entries():
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
        self.session_cache.put(key,out,{'origin':'imported','source_format':fmt,'source_name':path.name,'source_path':str(path),'side':state.side,'players':len(state.starts) or state.metadata.get('players',0)})
        self._refresh_history()

    def import_file(self):
        before=getattr(self,'current',None);super().import_file()
        if self.current is not None and self.current is not before and self.import_source:
            self._register_import_history(self.current,self.import_source)

    def _display_history_key(self,key):
        # UI navigation is observational: only an actual generation cache hit
        # promotes an LRU entry. Displaying/assigning must keep list order stable.
        out=self.session_cache.peek(key) if key else None
        if out is None:self._feedback('history_empty','warning');return
        need_stats=self.session_stats_cache.get(out.state) is None
        if need_stats:self._task_begin(_lang_text(self.prefs.get('language','fr'),'Chargement de l’historique…','Loading history…','Verlauf wird geladen…','Cargando historial…'),10)
        self.current=out;source=self.session_cache.metadata(key).get('source_path');self.import_source=Path(source) if source else None
        self._populate_current(imported=isinstance(key,ImportedHistoryKey));self._invalidate_preview();self._refresh_preview(True);self._refresh_history()
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
        columns=('origin','map','details');tree=ttk.Treeview(table_host,columns=columns,show='tree headings',selectmode='browse',style='History.Treeview');self._history_tree=tree
        tree.heading('#0',text='#',anchor='center');tree.heading('origin',text=text['origin']);tree.heading('map',text=text['map']);tree.heading('details',text=text['details'])
        tree.column('#0',width=68,minwidth=68,stretch=False,anchor='center')
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
        actions=ttk.Frame(shell);actions.grid(row=2,column=0,columnspan=2,sticky='ew');actions.columnconfigure(4,weight=1)
        buttons={}
        for col,(name,label,command) in enumerate((('show',text['show'],self._history_center_show),('a',text['set_a'],lambda:self._history_center_assign('A')),('b',text['set_b'],lambda:self._history_center_assign('B')),('delete',text['delete'],self._history_center_delete))):
            image=self._compare_led_off if name in ('show','a','b') else ''
            buttons[name]=ttk.Button(actions,text=label,image=image,compound='left',command=command,state='disabled');buttons[name].grid(row=0,column=col,padx=(0,6))
        buttons['clear']=ttk.Button(actions,text=text['clear'],command=self._history_center_clear);buttons['clear'].grid(row=0,column=5,padx=(6,6))
        buttons['close']=ttk.Button(actions,text=text['close'],command=self._close_history_center);buttons['close'].grid(row=0,column=6)
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
        for name in ('show','a','b','delete'):
            button=self._history_window_widgets.get('buttons',{}).get(name)
            if button is not None:button.configure(state=state)
        self._refresh_history_preview();self._refresh_state_indicators()

    def _refresh_history_center(self,preferred_index=None):
        tree=self._history_tree
        if tree is None:return
        selected=self._history_selected_key();old_y=tree.yview()[0] if tree.get_children() else 0.0;tree.delete(*tree.get_children());self._history_center_lookup={};lang=self.prefs.get('language','fr');text=HISTORY_TEXT[lang]
        for index,(key,out) in enumerate(self.session_cache.entries()):
            meta=self.session_cache.metadata(key);origin=self._history_origin(key);origin_label=text.get(origin,origin)
            if isinstance(key,ImportedHistoryKey):map_label=meta.get('source_name',key.source_format);details=f'(.{key.source_format.lower()}) · {meta.get("side",out.state.side)}×{meta.get("side",out.state.side)} · {meta.get("players",len(out.state.starts))}P'
            else:map_label=f'Seed {key.seed}';details=f'{key.side}×{key.side} · {key.players}P · {MODE_LABELS[lang].get(key.mode,key.mode)} · {ARCHETYPE_LABELS[lang].get(key.archetype,key.archetype)}'
            roles=self._history_roles_for_output(out)
            iid=f'h{index}';tree.insert('', 'end',iid=iid,text=str(index+1),image=self._history_role_image(roles),values=(origin_label,map_label,details),tags=('even' if index%2==0 else 'odd',));self._history_center_lookup[iid]=key
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
            image=render(out.state,labels=False,view='global',projection=self.prefs.get('projection','square'),start_markers=marker_mode!='hidden',start_marker_scale=2 if marker_mode=='normal' else 1)
            image.thumbnail((300,210),Image.Resampling.NEAREST);self._history_preview_base_image=image;self._history_preview_key=preview_key
        self._history_refresh_thumbnail_photo()
        slots=[slot for slot,value in self._compare_slots.items() if value is out];parts=[text['comparison'].format(slots='/'.join(slots) if slots else text['none'])]
        if getattr(self,'current',None) is out:parts.append(text['current'])
        reasons=[]
        if getattr(self,'current',None) is out:reasons.append(text['main_view'])
        reasons.extend(f'Slot {slot}' for slot in slots)
        if reasons:parts.append(text['protected'].format(reasons=', '.join(reasons)))
        entries=self.session_cache.entries();position=next((index+1 for index,(entry_key,_) in enumerate(entries) if entry_key==key),1);parts.append(text['mru'].format(position=position,total=len(entries)))
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
            self._history_large_image=render(out.state,labels=False,view='global',projection=projection,start_markers=marker_mode!='hidden',start_marker_scale=2 if marker_mode=='normal' else 1)
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
    def _history_center_delete(self):
        key=self._history_selected_key()
        if key is None:return
        children=list(self._history_tree.get_children());selection=self._history_tree.selection();index=children.index(selection[0]) if selection and selection[0] in children else 0
        out=self.session_cache.peek(key);slots=[slot for slot,value in self._compare_slots.items() if value is out];text=HISTORY_TEXT[self.prefs.get('language','fr')]
        reasons=[]
        if out is getattr(self,'current',None):reasons.append(text['main_view'])
        reasons.extend(f'Slot {slot}' for slot in slots)
        if reasons and not messagebox.askyesno(text['title'],text['delete_assigned'].format(reasons=', '.join(reasons)),parent=self._history_window):return
        for slot in slots:
            self._compare_slots[slot]=None
            if self._compare_active==slot:self._compare_active=None
        self.session_cache.remove(key);self._refresh_compare_label();self._refresh_history(preferred_index=index);self._feedback_key=None;self._status_kind='info';self.status.set(text['deleted']);self._sync_status_display();self._refresh_state_indicators()
    def _history_center_clear(self):
        self._clear_history(confirm=True,parent=self._history_window)

    def _retranslate_history_center(self):
        if self._history_window is None:return
        text=HISTORY_TEXT[self.prefs.get('language','fr')];self._history_window.title(text['title']);tree=self._history_tree
        tree.heading('#0',text='#');
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
        self._batch_i18n['hint_label']=ttk.Label(header,text=BATCH_HINTS.get(lang,BATCH_HINTS['en']));self._batch_i18n['hint_label'].pack(side='right')

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
            row['thumbnail'].bind('<Button-1>',lambda e,r=row:self._batch_toggle_large_preview(r));row['thumbnail'].bind('<Enter>',lambda e,r=row:self._batch_schedule_hover_preview(r));row['thumbnail'].bind('<Leave>',lambda e,r=row:self._batch_thumbnail_leave(r))
            row['thumbnail_host'].bind('<Enter>',lambda e,r=row:self._batch_schedule_hover_preview(r),add='+');row['thumbnail_host'].bind('<Leave>',lambda e,r=row:self._batch_thumbnail_leave(r),add='+')
            result_line=ttk.Frame(frame);result_line.grid(row=1,column=0,sticky='ew',padx=(7,8),pady=(7,3));result_line.columnconfigure(3,weight=1)
            row['status_var']=tk.StringVar(value=bt['waiting'])
            row['show']=ttk.Button(result_line,text=bt['show'],image=self._compare_led_off,compound='left',state='disabled',command=lambda r=row:self._batch_show_result(r));row['show'].grid(row=0,column=0,padx=(0,4))
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
            fill={'running':colors.get('bar_fg','#35a853'),'success':'#35a853','cached':'#2879d0','not_cached':colors.get('warning','#f9ab00'),'failed':'#d84a3a','cancelled':'#7f858d'}.get(state,colors.get('muted','#7f858d'))
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
        row['thumbnail_base_image']=thumb;self._batch_refresh_thumbnail_photo(row)

    def _batch_refresh_thumbnail_photo(self,row):
        base=row.get('thumbnail_base_image');label=row.get('thumbnail')
        if base is None or label is None:return
        shown=_thumbnail_with_magnifier(base,self._magnifier_state_for('batch',row));row['thumbnail_photo']=ImageTk.PhotoImage(shown,master=label);label.configure(image=row['thumbnail_photo'],text='')

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
        if row.get('result') is None:return
        self._set_magnifier_hover('batch',row)
        if not self._batch_preview_pinned:self._batch_hover_after=self.after(700,lambda r=row:self._batch_hover_preview_ready(r))

    def _batch_hover_preview_ready(self,row):
        self._batch_hover_after=None
        if self._magnifier_hover_kind=='batch' and self._magnifier_hover_ref is row:self._batch_show_preview_tooltip(row,False)

    def _batch_cancel_hover_preview(self,event=None):
        if self._batch_hover_after is not None:
            try:self.after_cancel(self._batch_hover_after)
            except tk.TclError:pass
            self._batch_hover_after=None

    def _batch_thumbnail_leave(self,row=None):
        self._batch_cancel_hover_preview()
        try:self.after_idle(lambda r=row:self._batch_finish_thumbnail_leave(r))
        except tk.TclError:pass

    def _batch_finish_thumbnail_leave(self,row):
        if row is not None:
            host=row.get('thumbnail_host')
            try:
                x,y=host.winfo_pointerxy();inside=host.winfo_rootx()<=x<host.winfo_rootx()+host.winfo_width() and host.winfo_rooty()<=y<host.winfo_rooty()+host.winfo_height()
                if inside:return
            except (tk.TclError,AttributeError):pass
        if self._magnifier_hover_kind=='batch' and self._magnifier_hover_ref is row:self._set_magnifier_hover()
        if not self._batch_preview_pinned:self._batch_hide_preview_tooltip()
        else:self._restore_magnifier_visual()

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
        if pinned:shown,size,x,y=self._batch_preview_geometry(row,image)
        else:shown,size,x,y=self._temporary_preview_geometry(image,self._batch_preview_zoom,row['thumbnail_host'])
        if preserved is not None:x,y=self._batch_clamp_preview_position(preserved[0],preserved[1],size)
        win,label,photo=self._batch_build_preview_surface(shown,size,x,y,pinned)
        self._batch_preview_window=win;self._batch_preview_label=label;self._batch_preview_photo=photo;self._batch_preview_row=row;self._batch_preview_pinned=bool(pinned);self._batch_preview_projection=self.prefs.get('projection','square');self._activate_magnifier('batch',row)
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
        label.bind('<MouseWheel>',self._batch_preview_wheel);label.bind('<Button-4>',lambda e:self._batch_preview_wheel(e,1));label.bind('<Button-5>',lambda e:self._batch_preview_wheel(e,-1))
        win.bind('<Escape>',lambda e:self._batch_hide_preview_tooltip(),add='+')
        win.update_idletasks();return win,label,photo

    def _batch_preview_geometry(self,row,image):
        screen_w=self.winfo_screenwidth();screen_h=self.winfo_screenheight();anchor=row['thumbnail_host'];anchor.update_idletasks()
        ax=anchor.winfo_rootx();ay=anchor.winfo_rooty();aw=anchor.winfo_width();ah=anchor.winfo_height();margin=14
        left_space=max(0,ax-margin-8);right_space=max(0,screen_w-(ax+aw)-margin-8);place_left=left_space>=right_space
        side_space=left_space if place_left else right_space
        if side_space<360:place_left=not place_left
        # Match History preview: zoom is constrained by the visible screen, not
        # by the narrow strip beside the Batch window. Overlap is preferable to
        # silently flattening most of the requested zoom range.
        max_w=max(320,screen_w-80);max_h=max(280,screen_h-120)
        factor=min(max_w/image.width,max_h/image.height,float(self._batch_preview_zoom));size=(max(1,int(image.width*factor)),max(1,int(image.height*factor)));shown=image.resize(size,Image.Resampling.NEAREST)
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

    def _batch_preview_wheel(self,event,direction=None):
        if direction is None:direction=1 if getattr(event,'delta',0)>0 else -1
        self._batch_preview_zoom=max(.35,min(1.25,self._batch_preview_zoom+(.1 if direction>0 else -.1)));self._batch_refresh_preview_tooltip(self._batch_preview_row);return 'break'

    def _batch_refresh_preview_tooltip(self,row):
        win=self._batch_preview_window;label=self._batch_preview_label
        if win is None or label is None or self._batch_preview_row is not row:return
        try:
            current=(win.winfo_x(),win.winfo_y());image=self._batch_compose_preview(row)
            if self._batch_preview_pinned:
                shown,size,_,_=self._batch_preview_geometry(row,image);x,y=self._batch_clamp_preview_position(current[0],current[1],size)
            else:shown,size,x,y=self._temporary_preview_geometry(image,self._batch_preview_zoom,row['thumbnail_host'])
            projection=self.prefs.get('projection','square')
            if projection!=self._batch_preview_projection:
                new_win,new_label,new_photo=self._batch_build_preview_surface(shown,size,x,y,self._batch_preview_pinned)
                self._batch_preview_window=new_win;self._batch_preview_label=new_label;self._batch_preview_photo=new_photo;self._batch_preview_projection=projection
                new_win.deiconify();new_win.lift();new_win.update_idletasks();win.destroy();return
            photo=ImageTk.PhotoImage(shown);label.configure(image=photo);self._batch_preview_photo=photo
            win.geometry(f'{size[0]}x{size[1]}+{x}+{y}')
        except tk.TclError:pass

    def _batch_hide_preview_tooltip(self):
        closing_row=self._batch_preview_row
        if self._batch_preview_window is not None:
            try:self._batch_preview_window.destroy()
            except tk.TclError:pass
        self._batch_preview_window=None;self._batch_preview_label=None;self._batch_preview_photo=None;self._batch_preview_row=None;self._batch_preview_pinned=False;self._batch_preview_projection=None;self._batch_preview_drag_origin=None
        if self._magnifier_active_kind=='batch' and self._magnifier_active_ref is closing_row:self._set_magnifier_active()
        self._restore_magnifier_visual()

    def _retranslate_batch_window(self):
        win=getattr(self,'_batch_window',None)
        if win is None:return
        try:
            lang=self.prefs.get('language','fr');bt=BATCH_TEXT[lang];win.title(bt['title'])
            self._batch_i18n['count_label'].configure(text=bt['count']);self._batch_randomize_button.configure(text=bt['randomize']);self._batch_apply_seed_button.configure(text=bt['apply_seed'])
            self._batch_i18n['hint_label'].configure(text=BATCH_HINTS.get(lang,BATCH_HINTS['en']))
            for row in self._batch_rows:
                mode=self._batch_label_key(row['mode_var'].get(),MODE_LABELS,'legacy');arch=self._batch_label_key(row['arch_var'].get(),ARCHETYPE_LABELS,'continental')
                row['frame'].configure(text=bt['map'].format(index=row['index']))
                for key,label in row['group_labels'].items():label.configure(text=bt[key])
                row['mode'].configure(values=[MODE_LABELS[lang][key] for key in MODE_ORDER]);row['mode_var'].set(MODE_LABELS[lang][mode])
                row['arch'].configure(values=[ARCHETYPE_LABELS[lang][key] for key in ARCHETYPE_ORDER]);row['arch_var'].set(ARCHETYPE_LABELS[lang][arch])
                row['modifier'].configure(values=[bt['none']]);row['modifier_var'].set(bt['none']);row['show'].configure(text=bt['show']);row['set_a'].configure(text=bt['set_a']);row['set_b'].configure(text=bt['set_b'])
                state=row.get('state','waiting');key='not_cached' if state=='not_cached' else ('cached' if row.get('cached') else ('success' if state=='success' else state))
                if key=='failed':text=bt['failed'].format(error=row.get('error',''))
                elif key in bt:text=bt[key]
                else:text=bt['waiting']
                row['status_var'].set(text);self._batch_draw_progress(row)
            self._batch_start_button.configure(text=bt['start']);self._batch_cancel_button.configure(text=bt['cancel']);self._batch_close_button.configure(text=bt['close'])
            self._refresh_batch_assignment_buttons()
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
        if not self._confirm_batch_cache_capacity(requests):return
        self._batch_queue=list(requests);self._batch_active_count=len(requests);self._batch_running=True;self._batch_cancel_requested=False;self._batch_active_row=None;self._batch_last_success=None
        for request in requests:
            row=request['row'];row['result']=None;row['cached']=False;row['error']='';row.pop('history_key',None);row.pop('preview_image',None);row.pop('thumbnail_photo',None);row.pop('thumbnail_base_image',None);row['thumbnail'].configure(image='',text=str(row['index']))
            self._batch_update_progress(row,0,self._batch_text('waiting'),'waiting')
            row['show'].configure(state='disabled');row['set_a'].configure(state='disabled');row['set_b'].configure(state='disabled')
        self._batch_set_running_controls(True);self._batch_summary_var.set(self._batch_text('running',current=1,total=len(requests)))
        self.after(20,self._batch_run_next)

    def _confirm_batch_cache_capacity(self,requests):
        forecast=self._batch_cache_capacity_forecast(requests)
        if forecast['existing_evicted']==0 and forecast['batch_dropped']==0:return True
        return self._show_batch_cache_warning(forecast)

    def _batch_cache_capacity_forecast(self,requests):
        """Simulate generation plus final re-touch without mutating the real LRU."""
        entries=self.session_cache.entries();original_keys=[key for key,_ in entries]
        simulated={key:value for key,value in reversed(entries)};capacity=self.session_cache.max_entries
        protected_ids={id(value) for value in (getattr(self,'current',None),self._compare_slots.get('A'),self._compare_slots.get('B'),*self._manual_history_locks) if value is not None and any(cached is value for cached in simulated.values())}
        requested_keys=[request['key'] for request in requests];requested_values={};last_value=None
        def trim():
            while len(simulated)>capacity:
                victim=next((key for key,value in simulated.items() if id(value) not in protected_ids),None)
                if victim is None:break
                simulated.pop(victim,None)
        for key in requested_keys:
            if key in simulated:value=simulated.pop(key)
            elif key in requested_values:value=requested_values[key]
            else:value=object()
            requested_values.setdefault(key,value);simulated[key]=value;last_value=value;trim()
        if getattr(self,'current',None) is None and last_value is not None:protected_ids.add(id(last_value))
        for key in requested_keys:
            value=requested_values[key];simulated.pop(key,None);simulated[key]=value;trim()
        final_keys=set(simulated);unique_requested=list(dict.fromkeys(requested_keys))
        existing_evicted=sum(key not in final_keys for key in original_keys)
        batch_dropped=sum(key not in final_keys for key in unique_requested)
        return {'used':len(entries),'capacity':capacity,'requested':len(unique_requested),'retained':len(unique_requested)-batch_dropped,'protected':len(protected_ids),'existing_evicted':existing_evicted,'batch_dropped':batch_dropped}

    def _show_batch_cache_warning(self,forecast):
        lang=self.prefs.get('language','fr');text=_BATCH_CAPACITY_TEXT[lang];result={'continue':False}
        parent=self._batch_window or self;win=tk.Toplevel(parent);win.withdraw();win.title(text['title']);win.transient(parent);win.resizable(False,False)
        colors=getattr(self,'_ui_theme_colors',THEME_PALETTES.get(self.prefs.get('theme','dark'),THEME_PALETTES['dark']));win.configure(background=colors.get('window','#202124'))
        shell=ttk.Frame(win,padding=16);shell.pack(fill='both',expand=True)
        ttk.Label(shell,text=text['title'],style='Section.TLabel').pack(anchor='w',fill='x',pady=(0,10))
        lines=[text['intro'].format(**forecast)]
        if forecast['existing_evicted']:lines.append(text['existing'].format(count=forecast['existing_evicted']))
        if forecast['batch_dropped']:lines.append(text['batch'].format(count=forecast['batch_dropped']))
        lines.extend((text['kept'],text['question']))
        ttk.Label(shell,text='\n\n'.join((lines[0],'\n'.join(lines[1:-2]),lines[-2],lines[-1])),justify='left',wraplength=520).pack(anchor='w',fill='x')
        buttons=ttk.Frame(shell);buttons.pack(fill='x',pady=(16,0))
        def close(accepted=False):
            result['continue']=bool(accepted)
            try:win.grab_release()
            except tk.TclError:pass
            win.destroy()
        ttk.Button(buttons,text=text['cancel'],command=lambda:close(False)).pack(side='right')
        ttk.Button(buttons,text=text['continue'],command=lambda:close(True)).pack(side='right',padx=(0,8))
        win.protocol('WM_DELETE_WINDOW',lambda:close(False));win.bind('<Escape>',lambda e:close(False),add='+');win.bind('<Return>',lambda e:close(True),add='+')
        win.update_idletasks();width=max(480,win.winfo_reqwidth());height=win.winfo_reqheight();screen_w=win.winfo_screenwidth();screen_h=win.winfo_screenheight()
        x=parent.winfo_rootx()+(parent.winfo_width()-width)//2;y=parent.winfo_rooty()+(parent.winfo_height()-height)//2;x=max(8,min(x,screen_w-width-8));y=max(8,min(y,screen_h-height-48));win.geometry(f'{width}x{height}+{x}+{y}')
        win.deiconify();win.lift();win.focus_force();win.grab_set();win.wait_window();return result['continue']

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
            self.session_cache.put(key,out);self.session_cache.set_metadata(key,{'origin':'batch'});row['history_key']=key;row['result']=out;row['cached']=cached;self._batch_last_success=out
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
            # Batch is a producer, not an implicit navigation command. It fills an
            # empty viewer for convenience, but never replaces an existing map.
            if self._batch_should_autodisplay():
                self.current=self._batch_last_success;self.import_source=None;self._populate_current();self._invalidate_preview();self._refresh_preview(True)
            # Re-touch successful rows under the final protection set so the
            # preflight forecast and the actual retained set follow the same rule.
            for row in active:
                key=row.get('history_key');out=row.get('result')
                if key is not None and out is not None:self.session_cache.put(key,out);self.session_cache.set_metadata(key,{'origin':'batch'})
            self._refresh_history()
        lost_ids=set()
        for row in active:
            out=row.get('result')
            if out is not None and row.get('state') in ('success','cached') and not self._output_in_history(out):
                lost_ids.add(id(out));self._batch_update_progress(row,100,self._batch_text('not_cached'),'not_cached')
        if lost_ids:self._batch_summary_var.set(self._batch_text('finished_retention',success=success,failed=failed,cancelled=cancelled,lost=len(lost_ids)))
        self._feedback('batch_done','success' if failed==0 and not lost_ids else 'warning',success=success,failed=failed,cancelled=cancelled)

    def _batch_should_autodisplay(self):
        return getattr(self,'current',None) is None

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
            if side!=768:raise NotImplementedError(_lang_text(self.prefs.get('language','fr'),f'La génération {side}×{side} est réservée mais pas encore calibrée. Max joueurs={NATIVE_LIMITS[side]}.',f'{side}×{side} generation is reserved but not calibrated yet. Max players={NATIVE_LIMITS[side]}.',f'Die Generierung in {side}×{side} ist reserviert, aber noch nicht kalibriert. Max. Spieler={NATIVE_LIMITS[side]}.',f'La generación {side}×{side} está reservada, pero aún no está calibrada. Máx. jugadores={NATIVE_LIMITS[side]}.'))
            key=self._cache_key();cached=self.session_cache.get(key);self.import_source=None;lang=self.prefs.get('language','fr')
            mode=MODE_LABELS[lang][key.mode];arch=ARCHETYPE_LABELS[lang][key.archetype];modifiers=self._modifier_summary()
            if cached is not None:
                self.current=cached;self.session_cache.set_metadata(key,{'origin':'generated'});self._populate_current();self._invalidate_preview();self._refresh_preview(True);self._refresh_history();self._feedback('cache_hit','success',seed=key.seed);return
            msg=FEEDBACK_TEXT[lang]['generating'].format(archetype=arch,mode=mode,modifiers=modifiers,side=side,players=int(self.players.get()),seed=int(self.seed.get()))
            self._task_begin(msg,2);self.current=self.generator.generate(int(self.players.get()),int(self.seed.get()),mode=self._mode_key(),archetype=self._arch_key())
            self.session_cache.put(key,self.current);self.session_cache.set_metadata(key,{'origin':'generated'});self._refresh_history();self._task_progress(97,_lang_text(lang,'Finalisation de l’aperçu…','Finalizing preview…','Vorschau wird fertiggestellt…','Finalizando vista previa…'));self._populate_current();self._invalidate_preview();self._refresh_preview(True)
            done=FEEDBACK_TEXT[lang]['generated'].format(archetype=arch,mode=mode,modifiers=modifiers,side=side,players=int(self.players.get()),seed=int(self.seed.get()));self._task_done(done)
        except Exception as e:
            import traceback;self._task_error(_lang_text(self.prefs.get('language','fr'),'Erreur de génération','Generation error','Generierungsfehler','Error de generación'));messagebox.showerror('MapGen',f'{e}\n\n{traceback.format_exc()}')
    def _load_history(self):
        self._display_history_key(self._history_lookup.get(self.history_var.get()))
    def _clear_history(self,confirm=True,parent=None):
        text=HISTORY_TEXT[self.prefs.get('language','fr')];slots=[slot for slot,value in self._compare_slots.items() if value is not None];reasons=[]
        if self._output_in_history(getattr(self,'current',None)):reasons.append(text['main_view'])
        reasons.extend(f'Slot {slot}' for slot in slots)
        prompt=text['confirm_clear_protected'].format(reasons=', '.join(reasons)) if reasons else text['confirm_clear']
        if confirm and not messagebox.askyesno(text['title'],prompt,parent=parent or self):return
        self.session_cache.clear();self.session_stats_cache.clear();self._history_lookup.clear();self.history_combo.configure(values=[]);self.history_var.set('')
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

    def _refresh_batch_assignment_buttons(self):
        lang=self.prefs.get('language','fr');bt=BATCH_TEXT[lang];ctx=_CONTEXT_TEXT[lang]
        for row in getattr(self,'_batch_rows',[]):
            out=row.get('result')
            show=row.get('show')
            if show is not None:
                active=out is not None and out is getattr(self,'current',None)
                try:show.configure(text=ctx['shown'] if active else bt['show'],image=self._compare_led_on if active else self._compare_led_off)
                except tk.TclError:pass
            for slot,key in (('A','set_a'),('B','set_b')):
                button=row.get(key)
                if button is not None:
                    active=out is not None and self._compare_slots.get(slot) is out
                    try:button.configure(text=ctx['assigned_a' if slot=='A' else 'assigned_b'] if active else bt['set_a' if slot=='A' else 'set_b'],image=self._compare_led_on if active else self._compare_led_off)
                    except tk.TclError:pass
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
        labels={'fr':('Terrain','Objet','Ressource','Hauteur','Accès','Territoire'),'en':('Terrain','Object','Resource','Height','Access','Claim'),'de':('Gelände','Objekt','Ressource','Höhe','Zugang','Territorium'),'es':('Terreno','Objeto','Recurso','Altura','Acceso','Territorio')}.get(lang,('Terrain','Object','Resource','Height','Access','Claim'))
        self.inspector_var.set(f'x={x}  y={y}  {labels[0]}={t} ({TERRAIN_NAMES.get(t,"?")})  {labels[1]}={o} ({oname})  {labels[2]}={self._resource_text(t,r)}  {labels[3]}={h}  {labels[4]}={a}  {labels[5]}={claim}')
    def _clear_inspector(self):
        if hasattr(self,'inspector_var'):self.inspector_var.set(_lang_text(self.prefs.get('language','fr'),'Inspecteur : —','Inspector: —','Inspektor: —','Inspector: —'))

    @staticmethod
    def _tk_sequence(shortcut):
        try:return shortcut_to_tk(shortcut)
        except (TypeError,ValueError):return None
    def _refresh_shortcut_capture_text(self,cmd):
        display=getattr(self,'shortcut_display_vars',{}).get(cmd)
        if display is None:return
        lang=self.prefs.get('language','fr');text=SHORTCUT_UI_TEXT[lang]
        if self._shortcut_capture_command==cmd:display.set(text['capture'])
        else:display.set(self.shortcut_vars[cmd].get() or text['disabled'])
    def _shortcut_values_changed(self,cmd):
        self._refresh_shortcut_capture_text(cmd);self._refresh_shortcut_validation()
    def _refresh_shortcut_validation(self):
        variables=getattr(self,'shortcut_vars',{})
        if not variables:return
        lang=self.prefs.get('language','fr');text=SHORTCUT_UI_TEXT[lang];values={};invalid=set()
        for cmd,var in variables.items():
            try:values[cmd]=canonicalize_shortcut(var.get())
            except (TypeError,ValueError):values[cmd]=var.get();invalid.add(cmd)
        groups={}
        for cmd,value in values.items():
            if cmd not in invalid and value:groups.setdefault(value.casefold(),[]).append(cmd)
        conflicts={cmd for commands in groups.values() if len(commands)>1 for cmd in commands}
        applied=self.prefs.get('shortcuts',DEFAULT_SHORTCUTS);states={}
        for cmd,value in values.items():
            if cmd in invalid:
                states[cmd]=('invalid',text['invalid_tip'])
            elif cmd in conflicts:
                peers=[COMMAND_LABELS[lang][other] for other in groups[value.casefold()] if other!=cmd]
                states[cmd]=('conflict',text['conflict_tip'].format(shortcut=value,actions=', '.join(peers)))
            elif value!=applied.get(cmd,DEFAULT_SHORTCUTS[cmd]):
                states[cmd]=('pending',text['pending_tip'])
            else:states[cmd]=('clean','')
        self._shortcut_row_states=states
        for cmd,label in getattr(self,'shortcut_status_labels',{}).items():
            state=states.get(cmd,('clean',''))[0]
            image=self._shortcut_conflict_icon if state in ('invalid','conflict') else self._shortcut_pending_icon if state=='pending' else self._shortcut_blank_icon
            label.configure(image=image)
        blocked=bool(invalid or conflicts);pending=any(state=='pending' for state,_ in states.values())
        if hasattr(self,'shortcut_apply_button'):self.shortcut_apply_button.configure(state='disabled' if blocked else 'normal')
        if hasattr(self,'shortcut_pending_label'):
            self.shortcut_pending_label.configure(text=text['conflict_summary'] if blocked else text['pending'] if pending else '',image=self._shortcut_conflict_icon if blocked else self._shortcut_pending_icon if pending else '',style='ShortcutConflict.TLabel' if blocked else 'ShortcutPending.TLabel')
    def _shortcut_status_tooltip(self,cmd):
        label=getattr(self,'shortcut_status_labels',{}).get(cmd);state,tip=self._shortcut_row_states.get(cmd,('clean',''))
        if label is not None and tip:self._show_ui_tooltip(label,tip,key=('shortcut-status',cmd,state,tip))
        else:self._hide_ui_tooltip()
    def _start_shortcut_capture(self,cmd):
        previous=self._shortcut_capture_command;self._shortcut_capture_command=cmd;self._shortcut_capture_modifiers=set()
        if previous and previous!=cmd:self._refresh_shortcut_capture_text(previous)
        self._refresh_shortcut_capture_text(cmd)
        button=self.shortcut_capture_buttons.get(cmd)
        if button is not None:button.focus_set()
    def _finish_shortcut_capture(self,cmd):
        if self._shortcut_capture_command==cmd:self._shortcut_capture_command=None;self._shortcut_capture_modifiers=set()
        self._refresh_shortcut_capture_text(cmd)
    @staticmethod
    def _shortcut_modifier_key(keysym):
        if keysym in ('Control_L','Control_R'):return 'Ctrl'
        if keysym in ('Shift_L','Shift_R'):return 'Shift'
        if keysym in ('Alt_L','Alt_R','ISO_Level3_Shift'):return 'Alt'
        return None
    def _capture_shortcut_key(self,cmd,event):
        if self._shortcut_capture_command!=cmd:return None
        keysym=str(getattr(event,'keysym',''))
        if keysym=='Escape':self._finish_shortcut_capture(cmd);return 'break'
        if keysym in ('Delete','BackSpace'):
            self.shortcut_vars[cmd].set('');self._finish_shortcut_capture(cmd);return 'break'
        modifier=self._shortcut_modifier_key(keysym)
        if modifier:self._shortcut_capture_modifiers.add(modifier);return 'break'
        state=int(getattr(event,'state',0));modifiers=set(self._shortcut_capture_modifiers)
        try:value=shortcut_from_event(keysym,state,pressed_modifiers=modifiers)
        except (TypeError,ValueError):return 'break'
        if value is None:return 'break'
        self.shortcut_vars[cmd].set(value);self._finish_shortcut_capture(cmd);return 'break'
    def _release_shortcut_key(self,cmd,event):
        if self._shortcut_capture_command!=cmd:return None
        modifier=self._shortcut_modifier_key(str(getattr(event,'keysym','')))
        if modifier:self._shortcut_capture_modifiers.discard(modifier)
        return 'break'
    def _disable_shortcut(self,cmd):
        self.shortcut_vars[cmd].set('');self._finish_shortcut_capture(cmd)
    def _bind_shortcuts(self):
        for seq in self._bound_shortcuts:
            try:self.unbind_all(seq)
            except tk.TclError:pass
        self._bound_shortcuts=[]
        actions={'generate':self.generate,'generate_batch':self._open_batch_window,'import':self.import_file,'export':self.export,'save_preview':self.save_preview,'manage_history':self._open_history_center,'reset_view':self._reset_view,'copy_seed':self._copy_seed,'toggle_ab':self._toggle_compare,'clear_compare':self._clear_compare_slots,'toggle_theme':self._toggle_theme,'help':self._show_help}
        for cmd,shortcut in self.prefs.get('shortcuts',DEFAULT_SHORTCUTS).items():
            seq=self._tk_sequence(shortcut)
            if seq and cmd in actions:
                self.bind_all(seq,lambda e,fn=actions[cmd]:(fn(),'break')[1]);self._bound_shortcuts.append(seq)
    def _apply_shortcut_settings(self):
        active=self._shortcut_capture_command
        if active:self._finish_shortcut_capture(active)
        vals={}
        for cmd,var in self.shortcut_vars.items():
            try:vals[cmd]=canonicalize_shortcut(var.get())
            except (TypeError,ValueError):self._refresh_shortcut_validation();return
        enabled=[value.casefold() for value in vals.values() if value]
        duplicate=next((value for value in vals.values() if value and enabled.count(value.casefold())>1),None)
        if duplicate:self._refresh_shortcut_validation();return
        self.prefs['shortcuts']=vals;self._save_prefs();self._bind_shortcuts();self._feedback('shortcut_applied','success')
        self._refresh_shortcut_validation();self._retranslate_help_window()
    def _reset_one_shortcut(self,cmd):
        self.shortcut_vars[cmd].set(DEFAULT_SHORTCUTS[cmd]);self._finish_shortcut_capture(cmd)
    def _reset_shortcut_settings(self):
        active=self._shortcut_capture_command
        if active:self._finish_shortcut_capture(active)
        for k,v in DEFAULT_SHORTCUTS.items():self.shortcut_vars[k].set(v);self._refresh_shortcut_capture_text(k)
        self._refresh_shortcut_validation()
    def _show_help(self):
        existing=self._help_window
        if existing is not None:
            try:existing.deiconify();existing.lift();existing.focus_force();return
            except tk.TclError:self._help_window=None
        w=tk.Toplevel(self);self._help_window=w;w.transient(self);w.resizable(True,True);w.minsize(480,380);w.protocol('WM_DELETE_WINDOW',self._close_help_window)
        body=ttk.Frame(w,padding=14);body.pack(fill='both',expand=True)
        shortcuts=ttk.LabelFrame(body,padding=10);shortcuts.pack(fill='both',expand=True);shortcuts.columnconfigure(0,weight=1);shortcuts.columnconfigure(1,weight=1)
        action_header=ttk.Label(shortcuts,anchor='w');action_header.grid(row=0,column=0,sticky='ew',padx=(0,12),pady=(0,5))
        shortcut_header=ttk.Label(shortcuts,anchor='w');shortcut_header.grid(row=0,column=1,sticky='ew',pady=(0,5))
        action_labels={};shortcut_labels={}
        for row,cmd in enumerate(DEFAULT_SHORTCUTS,start=1):
            action=ttk.Label(shortcuts,anchor='w');action.grid(row=row,column=0,sticky='ew',padx=(0,12),pady=2);action_labels[cmd]=action
            value=ttk.Label(shortcuts,anchor='w');value.grid(row=row,column=1,sticky='ew',pady=2);shortcut_labels[cmd]=value
        navigation=ttk.LabelFrame(body,padding=10);navigation.pack(fill='x',pady=(10,0))
        navigation_labels=[]
        for row in range(4):
            label=ttk.Label(navigation,anchor='w');label.grid(row=row,column=0,sticky='w',pady=1);navigation_labels.append(label)
        close=ttk.Button(body,command=self._close_help_window);close.pack(anchor='e',pady=(10,0))
        self._help_widgets={'shortcuts':shortcuts,'action_header':action_header,'shortcut_header':shortcut_header,'actions':action_labels,'values':shortcut_labels,'navigation':navigation,'navigation_labels':navigation_labels,'close':close}
        self._retranslate_help_window();self._apply_help_window_theme();w.update_idletasks()
        width=max(520,min(w.winfo_reqwidth(),w.winfo_screenwidth()-80));height=max(430,min(w.winfo_reqheight(),w.winfo_screenheight()-100));x=max(20,(w.winfo_screenwidth()-width)//2);y=max(20,(w.winfo_screenheight()-height)//2);w.geometry(f'{width}x{height}+{x}+{y}')
    def _close_help_window(self):
        w=self._help_window;self._help_window=None;self._help_widgets={}
        if w is not None:
            try:w.destroy()
            except tk.TclError:pass
    def _retranslate_help_window(self):
        w=self._help_window
        if w is None:return
        try:
            if not w.winfo_exists():self._help_window=None;self._help_widgets={};return
        except tk.TclError:self._help_window=None;self._help_widgets={};return
        lang=self.prefs.get('language','fr');text=SHORTCUT_UI_TEXT[lang];widgets=self._help_widgets;sc=self.prefs.get('shortcuts',DEFAULT_SHORTCUTS)
        w.title(text['help_title']);widgets['shortcuts'].configure(text=text['title']);widgets['action_header'].configure(text=text['action']);widgets['shortcut_header'].configure(text=text['shortcut']);widgets['navigation'].configure(text=text['navigation']);widgets['close'].configure(text=text['close'])
        for cmd,label in widgets['actions'].items():label.configure(text=COMMAND_LABELS[lang][cmd])
        for cmd,label in widgets['values'].items():label.configure(text=sc.get(cmd,DEFAULT_SHORTCUTS[cmd]) or text['disabled'])
        for label,value in zip(widgets['navigation_labels'],(text['wheel'],text['drag'],text['cache'],text['compare'])):label.configure(text=value)
    def _apply_help_window_theme(self):
        if self._help_window is None:return
        try:self._help_window.configure(background=self._ui_theme_colors.get('window','#202124'))
        except tk.TclError:pass

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
            except Exception as error:self._task_error(_lang_text(lang,'Erreur export','Export error','Exportfehler','Error de exportación'));messagebox.showerror(text['map_title'],str(error),parent=self)
        export_button.configure(command=perform)
        for var in (folder,basename,*formats.values()):var.trace_add('write',refresh)
        refresh();self._place_export_center(w);self._activate_export_modal(w)

def main():App().mainloop()
