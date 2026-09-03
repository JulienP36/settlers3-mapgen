"""Main-window, feedback, mode and settings translation catalogues."""

from ....version import APP_VERSION, ENGINE_VERSION

LANGUAGE_LABELS={'fr':'Français','en':'English','de':'Deutsch','es':'Español'}

_WINDOW_ENGINE_LABELS={
 'fr':'moteur de génération',
 'en':'generation engine',
 'de':'Generierungs-Engine',
 'es':'motor de generación',
}

WINDOW_TITLES={
 lang:f'Settlers III MapGen v{APP_VERSION} — {engine_label} v{ENGINE_VERSION}'
 for lang,engine_label in _WINDOW_ENGINE_LABELS.items()
}

FEEDBACK_TEXT={
 'fr':{
  'ready':'Prêt — {mode} / {archetype} / modificateurs : {modifiers} / {side}×{side} / {players} joueurs.',
  'size_reserved':'{side}×{side} : max {max_players} joueurs. Génération Legacy et Upgraded disponible.',
  'size_viability_warning':'{side}×{side} est autorisé par l’éditeur, mais inférieur à 384×384 : génération native peu viable et sous le minimum du jeu (max {max_players} joueurs).',
  'size_extended_warning':'{side}×{side} est autorisé par l’éditeur Settlers United, mais dépasse la taille native maximale de 768×768 : viabilité en jeu non garantie (max {max_players} joueurs).',
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
  'history_not_retained':'Carte affichée, mais non conservée : toutes les places du cache sont protégées.',
 },
 'en':{
  'ready':'Ready — {mode} / {archetype} / modifiers: {modifiers} / {side}×{side} / {players} players.',
  'size_reserved':'{side}×{side}: max {max_players} players. Legacy and Upgraded generation are available.',
  'size_viability_warning':'{side}×{side} is editor-valid, but below 384×384: native generation may be poorly viable and is below the game minimum (max {max_players} players).',
  'size_extended_warning':'{side}×{side} is supported by the Settlers United editor, but exceeds the native 768×768 maximum: in-game viability is not guaranteed (max {max_players} players).',
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
  'history_not_retained':'Map displayed but not retained: every cache slot is protected.',
 },
}

MODE_LABELS={
 'fr':{'legacy':'Héritage (Legacy)','upgraded':'Amélioré (Upgraded)','custom':'Personnalisé'},
 'en':{'legacy':'Legacy','upgraded':'Upgraded','custom':'Custom'},
}

ARCHETYPE_LABELS={
 'fr':{'continental':'Continental','large_islands':'Grandes îles','small_islands':'Petites îles'},
 'en':{'continental':'Continental','large_islands':'Large Islands','small_islands':'Small Islands'},
}

MIRROR_LABELS={
 'fr':{0:'Aucun',1:'Axe long',2:'Axe court',3:'Les deux'},
 'en':{0:'None',1:'Long axis',2:'Short axis',3:'Both'},
 'de':{0:'Keine',1:'Längsachse',2:'Querachse',3:'Beide'},
 'es':{0:'Ninguno',1:'Eje largo',2:'Eje corto',3:'Ambos'},
}

COMMAND_LABELS={
 'fr':{'generate':'Générer','generate_batch':'Générer un lot','import':'Importer','export':'Exporter','save_preview':'Enregistrer l’aperçu PNG','manage_history':'Gérer l’historique','reset_view':'Recentrer','copy_seed':'Copier le seed','toggle_ab':'Basculer A/B','clear_compare':'Vider A+B','toggle_theme':'Basculer thème','help':'Aide'},
 'en':{'generate':'Generate','generate_batch':'Generate batch','import':'Import','export':'Export','save_preview':'Save PNG preview','manage_history':'Manage history','reset_view':'Reset view','copy_seed':'Copy seed','toggle_ab':'Toggle A/B','clear_compare':'Clear A+B','toggle_theme':'Toggle theme','help':'Help'},
}

THEME_LABELS={'fr':{'dark':'Sombre','light':'Clair'},'en':{'dark':'Dark','light':'Light'}}

PROJECTION_LABELS={'fr':{'square':'Carrée','parallelogram':'Parallélogramme'},'en':{'square':'Square','parallelogram':'Parallelogram'}}

PREVIEW_START_MARKER_LABELS={
 'fr':{'hidden':'Masqués','tiny':'Petits','small':'Normaux','normal':'Grands'},
 'en':{'hidden':'Hidden','tiny':'Tiny','small':'Normal','normal':'Large'},
}

TEXTS={
 'Mode':{'en':'Mode'},'Archétype':{'en':'Archetype'},'Miroir':{'en':'Mirror'},'Modificateurs':{'en':'Modifiers'},'Taille':{'en':'Size'},'Joueurs':{'en':'Players'},'Seed':{'en':'Seed'},'Zoom':{'en':'Zoom'},
 'Générer':{'en':'Generate'},'Générer lot…':{'en':'Generate batch…'},'Importer…':{'en':'Import…'},'Exporter…':{'en':'Export…'},'Aperçu PNG':{'en':'PNG Preview'},'Vue':{'en':'View'},
 'Affichage':{'en':'Display'},'Thème':{'en':'Theme'},'Opacité couche':{'en':'Layer opacity'},'0 % = map globale · 100 % = couche seule':{'en':'0 % = global map · 100 % = overlay only'},
 'Projection':{'en':'Projection'},'Le parallélogramme modifie uniquement le rendu, jamais les données.':{'en':'Parallelogram changes rendering only, never map data.'},
 'Marqueurs de départ':{'en':'Start markers'},'Ce réglage affecte les marqueurs de départ et les aperçus du lot.':{'en':'This setting affects start markers and batch previews.'},
 'Sensibilité molette':{'en':'Mouse-wheel sensitivity'},'Navigation':{'en':'Navigation'},'Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.':{'en':'Mouse wheel: zoom\nLeft click + drag: move map\nZoom refresh is delayed to reduce recalculation.'},
 'Paramètres':{'en':'Settings'},'Validations':{'en':'Validations'},'Pipeline':{'en':'Pipeline'},'Métadonnées':{'en':'Metadata'},'Statistiques':{'en':'Statistics'},'Graphiques':{'en':'Charts'},'Lier à la vue':{'en':'Link to view'},'Exporter JSON':{'en':'Export JSON'},'Exporter CSV':{'en':'Export CSV'},'Exporter PNG':{'en':'Export PNG'},'Ressource Heatmap':{'en':'Heatmap resource'},'Filtre carte thermique':{'en':'Heatmap filter'},
 'Recentrer':{'en':'Reset view'},'Copier seed':{'en':'Copy seed'},'Langue':{'en':'Language'},'Aide':{'en':'Help'},'Historique session':{'en':'Session history'},
 'Charger':{'en':'Load'},'Vider cache':{'en':'Clear cache'},'Gérer…':{'en':'Manage…'},"Capacité de l'historique":{'en':'History capacity'},'Cartes conservées uniquement pendant cette session.':{'en':'Maps are kept for this session only.'},'Définir A':{'en':'Set A'},'Définir B':{'en':'Set B'},'Basculer A/B':{'en':'Toggle A/B'},
 'Vider A':{'en':'Clear A'},'Vider B':{'en':'Clear B'},'Vider A+B':{'en':'Clear A+B'},
 'Raccourcis':{'en':'Shortcuts'},'Appliquer':{'en':'Apply'},'Valeurs par défaut':{'en':'Defaults'},'Réinitialiser':{'en':'Reset'},
 'Session / Comparaison':{'en':'Session / Comparison'},'Format : Ctrl+G, Ctrl+Shift+C, Alt+1, F1…':{'en':'Format: Ctrl+G, Ctrl+Shift+C, Alt+1, F1…'},
}

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
 'de':{'hidden':'Ausgeblendet','tiny':'Sehr klein','small':'Normal','normal':'Groß'},
 'es':{'hidden':'Ocultos','tiny':'Muy pequeños','small':'Normales','normal':'Grandes'},
})

_TEXTS_DE_ES={
 'Mode':('Modus','Modo'),'Archétype':('Archetyp','Arquetipo'),'Miroir':('Spiegel','Espejo'),'Modificateurs':('Modifikatoren','Modificadores'),'Taille':('Größe','Tamaño'),'Joueurs':('Spieler','Jugadores'),'Seed':('Seed','Seed'),'Zoom':('Zoom','Zoom'),
 'Générer':('Generieren','Generar'),'Générer lot…':('Stapel generieren…','Generar lote…'),'Importer…':('Importieren…','Importar…'),'Exporter…':('Exportieren…','Exportar…'),'Aperçu PNG':('PNG-Vorschau','Vista previa PNG'),'Vue':('Ansicht','Vista'),
 'Affichage':('Anzeige','Visualización'),'Thème':('Design','Tema'),'Opacité couche':('Ebenendeckkraft','Opacidad de capa'),'0 % = map globale · 100 % = couche seule':('0 % = globale Karte · 100 % = nur Ebene','0 % = mapa global · 100 % = solo capa'),
 'Projection':('Projektion','Proyección'),'Le parallélogramme modifie uniquement le rendu, jamais les données.':('Das Parallelogramm ändert nur die Darstellung, niemals die Daten.','El paralelogramo solo cambia la visualización, nunca los datos.'),
 'Marqueurs de départ':('Startmarker','Marcadores de inicio'),'Ce réglage affecte les marqueurs de départ et les aperçus du lot.':('Diese Einstellung betrifft Startmarker und Stapelvorschauen.','Este ajuste afecta a los marcadores de inicio y a las vistas previas del lote.'),
 'Sensibilité molette':('Mausrad-Empfindlichkeit','Sensibilidad de la rueda'),'Navigation':('Navigation','Navegación'),'Molette : zoom\nClic gauche + glisser : déplacer la carte\nLe zoom est temporisé pour limiter les recalculs.':('Mausrad: zoomen\nLinksklick + Ziehen: Karte verschieben\nDer Zoom wird verzögert, um Neuberechnungen zu begrenzen.','Rueda: zoom\nClic izquierdo + arrastrar: mover el mapa\nEl zoom se retrasa para limitar los recálculos.'),
 'Paramètres':('Einstellungen','Ajustes'),'Validations':('Prüfungen','Validaciones'),'Pipeline':('Pipeline','Proceso'),'Métadonnées':('Metadaten','Metadatos'),'Statistiques':('Statistiken','Estadísticas'),'Graphiques':('Diagramme','Gráficos'),'Lier à la vue':('Mit der Ansicht verknüpfen','Vincular a la vista'),'Exporter JSON':('JSON exportieren','Exportar JSON'),'Exporter CSV':('CSV exportieren','Exportar CSV'),'Exporter PNG':('PNG exportieren','Exportar PNG'),'Ressource Heatmap':('Heatmap-Ressource','Recurso del mapa de calor'),'Filtre carte thermique':('Heatmap-Filter','Filtro del mapa de calor'),
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
  'ready':'Bereit — {mode} / {archetype} / Modifikatoren: {modifiers} / {side}×{side} / {players} Spieler.','size_reserved':'{side}×{side}: max. {max_players} Spieler. Legacy- und Upgraded-Generierung verfügbar.','size_viability_warning':'{side}×{side}: editorgültig, aber kleiner als 384×384. Die native Generierung kann wenig praktikabel sein und liegt unter dem Spielminimum (max. {max_players} Spieler).','mode_reserved':'Modus „{mode}“ ist reserviert und nicht implementiert.','arch_reserved':'Archetyp „{archetype}“ ist reserviert und nicht implementiert.','generating':'Generiere {archetype} — {mode} — Modifikatoren: {modifiers} — {side}×{side} — {players} Spieler — Seed {seed}…','generated':'Karte generiert — {archetype} / {mode} / Modifikatoren: {modifiers} / {side}×{side} / {players} Spieler / Seed {seed}.','cache_hit':'Ergebnis aus dem Cache wiederverwendet — Seed {seed}.','heatmap_locked':'Der Filter ist in der Ansicht „Heatmap“ verfügbar.','history_loaded':'Karte aus dem Sitzungsverlauf geladen.','history_cleared':'Sitzungs-Caches geleert.','shortcut_applied':'Tastenkürzel übernommen.','shortcut_restored':'Tastenkürzel auf Standardwerte zurückgesetzt.','seed_copied':'Seed kopiert: {seed}','export_done':'Export abgeschlossen.','history_empty':'Keine Karte im Sitzungs-Cache verfügbar.','compare_toggled':'Karte zu {map} gewechselt.','theme_changed':'Design geändert: {theme}.','view_reset':'Ansicht zentriert.','seed_randomized':'Neuer zufälliger Seed: {seed}','graph_exported':'Diagrammexport abgeschlossen: {format} — {file}','opacity_locked':'Die Deckkraft ist in der globalen Ansicht nicht verfügbar.','modifier_none':'Kein Modifikator aktiv.','batch_opened':'Stapelgenerierung bereit — 1 bis 4 Karten konfigurieren.','batch_done':'Stapel abgeschlossen — {success} erfolgreich, {failed} fehlgeschlagen, {cancelled} abgebrochen.','history_not_retained':'Karte angezeigt, aber nicht behalten: Alle Cache-Plätze sind geschützt.',
 },
 'es':{
  'ready':'Listo — {mode} / {archetype} / modificadores: {modifiers} / {side}×{side} / {players} jugadores.','size_reserved':'{side}×{side}: máx. {max_players} jugadores. Generación Legacy y Upgraded disponible.','size_viability_warning':'{side}×{side} es válido para el editor, pero menor que 384×384: la generación nativa puede ser poco viable y queda por debajo del mínimo del juego (máx. {max_players} jugadores).','mode_reserved':'El modo «{mode}» está reservado y no implementado.','arch_reserved':'El arquetipo «{archetype}» está reservado y no implementado.','generating':'Generando {archetype} — {mode} — modificadores: {modifiers} — {side}×{side} — {players} jugadores — seed {seed}…','generated':'Mapa generado — {archetype} / {mode} / modificadores: {modifiers} / {side}×{side} / {players} jugadores / seed {seed}.','cache_hit':'Resultado reutilizado desde la caché — seed {seed}.','heatmap_locked':'El filtro está disponible en la vista «Mapa de calor».','history_loaded':'Mapa cargado desde el historial de sesión.','history_cleared':'Cachés de sesión vaciadas.','shortcut_applied':'Atajos aplicados.','shortcut_restored':'Atajos restablecidos a sus valores predeterminados.','seed_copied':'Seed copiada: {seed}','export_done':'Exportación terminada.','history_empty':'No hay mapas disponibles en la caché de sesión.','compare_toggled':'Mapa cambiado a {map}.','theme_changed':'Tema cambiado: {theme}.','view_reset':'Vista centrada.','seed_randomized':'Nueva seed aleatoria: {seed}','graph_exported':'Exportación del gráfico terminada: {format} — {file}','opacity_locked':'La opacidad no está disponible en la vista Global.','modifier_none':'No hay modificadores activos.','batch_opened':'Generación por lotes lista — configura de 1 a 4 mapas.','batch_done':'Lote terminado — {success} correctos, {failed} fallidos, {cancelled} cancelados.','history_not_retained':'Mapa mostrado pero no conservado: todas las plazas de la caché están protegidas.',
 },
})

FEEDBACK_TEXT['de']['size_reserved']='{side}×{side}: max. {max_players} Spieler. Legacy- und Upgraded-Generierung verfügbar.'
FEEDBACK_TEXT['es']['size_reserved']='{side}×{side}: máx. {max_players} jugadores. Generación Legacy y Upgraded disponible.'
FEEDBACK_TEXT['de']['size_viability_warning']='{side}×{side}: editorgültig, aber kleiner als 384×384. Die native Generierung kann wenig praktikabel sein und liegt unter dem Spielminimum (max. {max_players} Spieler).'
FEEDBACK_TEXT['es']['size_viability_warning']='{side}×{side}: válido para el editor, pero menor que 384×384. La generación nativa puede ser poco viable y queda por debajo del mínimo del juego (máx. {max_players} jugadores).'
FEEDBACK_TEXT['de']['size_extended_warning']='{side}×{side}: vom Settlers-United-Editor unterstützt, aber größer als das native Maximum von 768×768. Die Spieltauglichkeit ist nicht garantiert (max. {max_players} Spieler).'
FEEDBACK_TEXT['es']['size_extended_warning']='{side}×{side}: compatible con el editor Settlers United, pero supera el máximo nativo de 768×768. La viabilidad en el juego no está garantizada (máx. {max_players} jugadores).'

NONE_LABELS={'fr':'Aucun','en':'None','de':'Keine','es':'Ninguno'}

LOWER_NONE_LABELS={'fr':'aucun','en':'none','de':'keine','es':'ninguno'}
