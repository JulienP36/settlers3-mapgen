"""Batch-window translation catalogues."""

BATCH_TEXT={
 'fr':{
  'title':'Génération par lot','count':'Nombre de cartes','randomize':'Nouvelles seeds','apply_seed':'Appliquer à toutes',
  'map':'Carte {index}','mode':'Mode','archetype':'Archétype','mirror':'Miroir','modifiers':'Modificateurs','size':'Taille',
  'players':'Joueurs','seed':'Seed','status':'État','waiting':'En attente','generating':'Génération…',
  'cached':'Réutilisée depuis le cache','success':'Terminée','failed':'Erreur : {error}','cancelled':'Annulée',
  'start':'Générer le lot','cancel':'Annuler les cartes en attente','close':'Fermer','set_a':'Affecter à A',
  'set_b':'Affecter à B','show':'Afficher','none':'Aucun','invalid_title':'Paramètres du lot invalides',
  'invalid_row':'Carte {index} : {error}','unsupported_size':'taille native non prise en charge','unsupported_mode':'mode non implémenté','unsupported_archetype':'archétype non implémenté','unsupported_mode_size':'ce mode reste limité à 768×768','unsupported_mirror':'le miroir est disponible uniquement pour Legacy / Continental',
  'invalid_players':'nombre de joueurs invalide (2 à {maximum})','invalid_seed':'seed entière requise',
  'running':'Lot en cours : carte {current}/{total}','cancel_pending':'Annulation demandée après la carte en cours.',
  'finished':'Lot terminé : {success} réussie(s), {failed} erreur(s), {cancelled} annulée(s).',
  'assigned':'Carte {index} affectée à {slot}.','moved':'Carte {index} déplacée de {other} vers {slot}.','already_assigned':'Carte {index} déjà affectée à {slot}.',
  'preview_hint':'Cliquez ou laissez la souris 700 ms pour agrandir.','close_preview':'Fermer l’aperçu','close_running':'Le lot est en cours ; les cartes en attente seront annulées.',
 },
 'en':{
  'title':'Batch generation','count':'Number of maps','randomize':'New seeds','apply_seed':'Apply to all',
  'map':'Map {index}','mode':'Mode','archetype':'Archetype','mirror':'Mirror','modifiers':'Modifiers','size':'Size',
  'players':'Players','seed':'Seed','status':'Status','waiting':'Waiting','generating':'Generating…',
  'cached':'Reused from cache','success':'Complete','failed':'Error: {error}','cancelled':'Cancelled',
  'start':'Generate batch','cancel':'Cancel pending maps','close':'Close','set_a':'Assign to A',
  'set_b':'Assign to B','show':'Show','none':'None','invalid_title':'Invalid batch parameters',
  'invalid_row':'Map {index}: {error}','unsupported_size':'native size is not supported','unsupported_mode':'mode is not implemented','unsupported_archetype':'archetype is not implemented','unsupported_mode_size':'this mode remains limited to 768×768','unsupported_mirror':'mirror is available only for Legacy / Continental',
  'invalid_players':'invalid player count (2 to {maximum})','invalid_seed':'an integer seed is required',
  'running':'Batch running: map {current}/{total}','cancel_pending':'Cancellation requested after the current map.',
  'finished':'Batch complete: {success} succeeded, {failed} failed, {cancelled} cancelled.',
  'assigned':'Map {index} assigned to {slot}.','moved':'Map {index} moved from {other} to {slot}.','already_assigned':'Map {index} is already assigned to {slot}.',
  'preview_hint':'Click or hover for 700 ms to enlarge.','close_preview':'Close preview','close_running':'The batch is running; pending maps will be cancelled.',
 },
}

BATCH_TEXT.update({
 'de':{
  'title':'Stapelgenerierung','count':'Anzahl Karten','randomize':'Neue Seeds','apply_seed':'Auf alle anwenden','map':'Karte {index}','mode':'Modus','archetype':'Archetyp','mirror':'Spiegel','modifiers':'Modifikatoren','size':'Größe','players':'Spieler','seed':'Seed','status':'Status','waiting':'Wartend','generating':'Generierung…','cached':'Aus Cache wiederverwendet','success':'Abgeschlossen','failed':'Fehler: {error}','cancelled':'Abgebrochen','start':'Stapel generieren','cancel':'Wartende Karten abbrechen','close':'Schließen','set_a':'A zuweisen','set_b':'B zuweisen','show':'Anzeigen','none':'Keine','invalid_title':'Ungültige Stapelparameter','invalid_row':'Karte {index}: {error}','unsupported_size':'nicht unterstützte native Größe','unsupported_mode':'Modus ist nicht implementiert','unsupported_archetype':'Archetyp ist nicht implementiert','unsupported_mode_size':'dieser Modus bleibt auf 768×768 beschränkt','unsupported_mirror':'Spiegel nur für Legacy / Continental verfügbar','invalid_players':'ungültige Spielerzahl (2 bis {maximum})','invalid_seed':'ganzzahliger Seed erforderlich','running':'Stapel läuft: Karte {current}/{total}','cancel_pending':'Abbruch nach der aktuellen Karte angefordert.','finished':'Stapel abgeschlossen: {success} erfolgreich, {failed} fehlgeschlagen, {cancelled} abgebrochen.','assigned':'Karte {index} wurde {slot} zugewiesen.','moved':'Karte {index} wurde von {other} nach {slot} verschoben.','already_assigned':'Karte {index} ist bereits {slot} zugewiesen.','preview_hint':'Klicken oder 700 ms verweilen zum Vergrößern.','close_preview':'Vorschau schließen','close_running':'Der Stapel läuft; wartende Karten werden abgebrochen.',
 },
 'es':{
  'title':'Generación por lotes','count':'Número de mapas','randomize':'Nuevas seeds','apply_seed':'Aplicar a todos','map':'Mapa {index}','mode':'Modo','archetype':'Arquetipo','mirror':'Espejo','modifiers':'Modificadores','size':'Tamaño','players':'Jugadores','seed':'Seed','status':'Estado','waiting':'En espera','generating':'Generando…','cached':'Reutilizado desde la caché','success':'Terminado','failed':'Error: {error}','cancelled':'Cancelado','start':'Generar lote','cancel':'Cancelar mapas pendientes','close':'Cerrar','set_a':'Asignar a A','set_b':'Asignar a B','show':'Mostrar','none':'Ninguno','invalid_title':'Parámetros del lote no válidos','invalid_row':'Mapa {index}: {error}','unsupported_size':'tamaño nativo no compatible','unsupported_mode':'el modo no está implementado','unsupported_archetype':'el arquetipo no está implementado','unsupported_mode_size':'este modo sigue limitado a 768×768','unsupported_mirror':'el espejo solo está disponible para Legacy / Continental','invalid_players':'número de jugadores no válido (2 a {maximum})','invalid_seed':'se requiere una seed entera','running':'Lote en curso: mapa {current}/{total}','cancel_pending':'Cancelación solicitada después del mapa actual.','finished':'Lote terminado: {success} correctos, {failed} fallidos, {cancelled} cancelados.','assigned':'Mapa {index} asignado a {slot}.','moved':'Mapa {index} movido de {other} a {slot}.','already_assigned':'El mapa {index} ya está asignado a {slot}.','preview_hint':'Haz clic o mantén el cursor 700 ms para ampliar.','close_preview':'Cerrar vista previa','close_running':'El lote está en curso; se cancelarán los mapas pendientes.',
 },
})

BATCH_HINTS={'fr':'1–4 cartes · paramètres indépendants · génération séquentielle','en':'1–4 maps · independent parameters · sequential generation','de':'1–4 Karten · unabhängige Parameter · sequenzielle Generierung','es':'1–4 mapas · parámetros independientes · generación secuencial'}

BATCH_SMALL_SIZE_WARNING={
 'fr':'⚠ {side}×{side} est autorisé par l’éditeur mais inférieur à 384×384 : génération peu viable (max {max_players} joueurs).',
 'en':'⚠ {side}×{side} is editor-valid but below 384×384: generation may be poorly viable (max {max_players} players).',
 'de':'⚠ {side}×{side} ist editorgültig, aber kleiner als 384×384: Die Generierung kann wenig praktikabel sein (max. {max_players} Spieler).',
 'es':'⚠ {side}×{side} es válido para el editor, pero menor que 384×384: la generación puede ser poco viable (máx. {max_players} jugadores).',
}
for _lang,_warning in BATCH_SMALL_SIZE_WARNING.items():
    BATCH_TEXT[_lang]['small_size_warning']=_warning

BATCH_EXTENDED_SIZE_WARNING={
 'fr':'⚠ {side}×{side} est autorisé par l’éditeur Settlers United mais dépasse 768×768 : viabilité en jeu non garantie (max {max_players} joueurs).',
 'en':'⚠ {side}×{side} is supported by the Settlers United editor but exceeds 768×768: in-game viability is not guaranteed (max {max_players} players).',
 'de':'⚠ {side}×{side} wird vom Settlers-United-Editor unterstützt, überschreitet aber 768×768: Die Spieltauglichkeit ist nicht garantiert (max. {max_players} Spieler).',
 'es':'⚠ {side}×{side} es compatible con el editor Settlers United, pero supera 768×768: la viabilidad en el juego no está garantizada (máx. {max_players} jugadores).',
}
for _lang,_warning in BATCH_EXTENDED_SIZE_WARNING.items():
    BATCH_TEXT[_lang]['extended_size_warning']=_warning

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
