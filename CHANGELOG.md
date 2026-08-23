## v1.8 DEV_4 PERF+ R1 — 2026-08-23
- Builds a separate, reversible performance candidate from the Windows-validated DEV_4_R6 checkpoint.
- Splits deterministic map rendering into a reusable marker-free square raster followed by lightweight projection and start-marker composition.
- Reuses the same Global square raster when switching between Global and Starts; Starts opacity now invalidates only its sprite composite.
- Keeps at most the current main-view square layer and its projection composites, plus one square and one parallelogram base per completed Batch result.
- Stops invalidating deterministic map pixels for language, theme and projection changes; the visible result still refreshes immediately.
- Debounces rapid opacity and wheel-zoom preference writes by 200 ms and flushes the latest values on application close.
- Preserves exact rendering: split and direct render paths are pixel-identical for Global, Starts and Territories in Square and Parallelogram.
- Reference 768 benchmark: cached projection about 7.6× faster and cached Starts-opacity composition about 24× faster than full rerendering on this environment.
- No threads, engine changes, rendering approximation or interaction changes.
- Windows validation completed: no regression or performance loss observed, with a possible responsiveness improvement; PERF+ R1 is accepted and retained.

## v1.8 DEV_4_R6 — 2026-08-23
- Makes pinned Batch previews draggable directly from the rendered map while keeping temporary hover previews non-interactive.
- Removes click-to-close from the large preview itself; clicking the same source mini-map again remains the primary close action, with Escape as fallback.
- Replaces an already pinned preview with another mini-map at the exact same top-left position instead of re-anchoring it.
- Preserves the current tooltip position during live marker/projection refreshes and clamps all manual movement inside the visible screen.
- Double-buffers projection changes and pinned row replacements: the complete new transparent surface is shown above the old one before the old surface is destroyed.
- Keeps same-projection marker changes on the lighter in-place image swap path.
- Keeps the validated R5 marker-layer cache and atomic image replacement unchanged.
- Generation engine, protected profiles and native library unchanged.
- Windows validation completed: dragging, closing, same-position replacement, screen clamping and projection double-buffering accepted by the user.

## v1.8 DEV_4_R5 — 2026-08-23
- Adds a persistent `Hidden / Small / Normal` display setting for start markers in Batch thumbnails and their enlarged previews.
- Defaults to Small; Normal preserves the R4 compact-marker scale and Hidden removes only preview markers.
- Keeps one marker-free base raster per completed Batch result/projection and composes only the lightweight start layer when the setting changes.
- Refreshes every completed Batch thumbnail immediately and swaps the image of an already visible hover/click preview without destroying its tooltip.
- Confirms pixel-for-pixel equivalence between direct and layered marker rendering in Square and Parallelogram.
- Keeps the validated Starts view, its central marker, 210-marker boundary, opacity behavior and Territories rendering unchanged.
- Layer composition benchmark on the 768 reference: about 0.08–0.09 ms Square and 0.57–0.64 ms Parallelogram, excluding Tk display resizing; generation engine, protected profiles and native library unchanged.
- Windows validation completed: all three marker modes, immediate thumbnails and non-blinking pinned preview accepted by the user.

## v1.8 DEV_4_R4 — 2026-08-23
- Adds a dedicated localized Starts view and removes all start labels/initial-territory overlays from the Global view.
- Keeps the exact native 3500-cell initial-territory mask and 210-cell HEX6 boundary in the Starts view only.
- Extracts J1–J20 start sprites deterministically from the user-provided editor reference, removes only its flat grass background and preserves nearest-neighbour pixel rendering.
- Refines the exact 210-marker Starts outline to the smallest non-overlapping raster sizes: 1×1 in Square and 2×2 in Parallelogram; R3 remains the visual fallback.
- Anchors central, boundary and compact Batch markers on their geometric center instead of their lower edge.
- Enables the opacity slider in Starts and applies it only to its central/boundary sprite layer, from fully visible at 100% to absent at 0%; the terrain remains unchanged.
- Uses compact center sprites in Batch mini-maps and their enlarged previews without adding the initial-territory boundary there.
- Makes Territories claims use the centralized validated J1–J20 palette with strict claim IDs 0..19; unknown values no longer wrap to another player color.
- Moves Territories immediately after Starts in the localized View list.
- Keeps SAV Territories tied to real runtime claims, while EDM/MAP and claim-less generated states reconstruct display-only initial territories from the exact confirmed 3500-cell native mask around each real start.
- Resolves synthetic initial-territory overlaps by nearest HEX6 distance, then lower player slot on ties; source map data remains untouched.
- Records the later label-design pass and the broader composable Views / chart-driven View Control interaction as separate UX work.
- Records a later Batch setting study for smaller, adjustable or disabled compact start markers.
- Postpones any manual modernization of the marker sprites to the future hand-made Pixel Art redesign.
- Windows validation completed: non-overlapping Starts borders, View ordering, opacity and EDM/MAP/SAV Territories behavior accepted by the user.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R7 — 2026-08-22
- Removes the redundant Batch map-count Apply button.
- Applies valid 1–4 map counts immediately from spin arrows or keyboard input; focus/Enter clamps invalid committed values back into range.
- Adds an 8-pixel gap between each progress-feedback bar and its mini-map region.
- Narrows the mini-map container from 224×122 to 182×122 and the render constraint from 222×120 to 180×120, matching the validated parallelogram aspect without reducing the displayed parallelogram.
- Square projection remains naturally centered and less width-constrained.
- Windows validation completed: DEV_3 Batch Generation and all R1–R7 polish accepted by the user, then promoted to `dev`.
- Archives a user-provided four-seed Batch screenshot as evidence for the v1.10 seed/RNG and morphological-diversity audit; no root-cause analysis or generator change is performed here.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R6 — 2026-08-22
- Enlarges the real Batch mini-map from 202×108 to 222×120 and its frameless container from 204×110 to 224×122.
- Preserves the validated one-pixel internal gap between map and container.
- Reduces the Batch row frame padding to one pixel around the mini-map container, letting the preview use the space up to the outer row border.
- Keeps independent left padding on parameter controls and result actions so only the preview region reaches the edge.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R5 — 2026-08-22
- Tightens Batch mini-map containers from 210×116 to 204×110 while preserving the 202×108 rendered map maximum.
- Reduces header, row, frame and footer spacing so the four result blocks remain compact without shrinking their readable controls.
- Measures the completed Batch window's requested width and height before final placement instead of relying only on the historical 1120×650 default.
- Opens at the full requested content size whenever the current screen permits, centers relative to the main application and clamps the window inside visible screen bounds.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R4 — 2026-08-22
- Enlarges each Batch mini-map area from 152×88 to 210×116 pixels and its rendered map from 144×80 to 202×108.
- Removes the relief/highlight frame around mini-maps; transparent projected corners now reveal the current panel color directly.
- Makes existing Batch mini-maps react immediately to Square/Parallelogram projection changes in the main Settings tab.
- Rebuilds an already visible hover/click preview immediately when projection changes.
- Replaces cursor-relative preview placement with deterministic mini-map anchoring: preferred adjacent side with screen-aware fallback and vertical clamping.
- Records a future deterministic start-marker pass using validated native game sprites; no sprite is guessed or bundled in this candidate.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R3 — 2026-08-22
- Fixes Batch thumbnails that collapsed to 12×4 pixels when Tk switched Label dimensions from text units to image pixels; each result now has a fixed 152×88 preview area with a map up to 144×80.
- Adds a dedicated common-seed dice button between the shared seed field and “Apply to all”; global and per-row dice actions remain unchanged.
- Replaces the decorated large-preview window with a borderless map-only tooltip.
- Click toggles a pinned tooltip; deliberate 700 ms hover shows a temporary tooltip.
- Parallelogram preview alpha is preserved through a Windows transparent-color surface so only the projected map remains visible around its transparent corners.
- Generation engine, protected profiles and native library unchanged.

## v1.8 DEV_3_R2 — 2026-08-22
- Polishes the Windows-validated Batch v1 workflow without changing the protected generation engine.
- Every row now opens with the same current/default seed; global and per-row dice actions are both preserved, with an additional common-seed “Apply to all” action.
- Adds deterministic mini previews rendered from each real generated map; click opens the large preview immediately and a 700 ms deliberate hover opens it without reacting to quick passes.
- Reorders each result line to Show / Assign A / Assign B / colored progress-feedback bar.
- Adds semantic Batch bar colors for running/success, cache, error and cancellation states.
- Shows A/B occupancy LEDs on result actions and centrally prevents the same output from occupying both slots; reassignment moves the map and reports it explicitly.
- The open Batch window is retranslated live when the main language changes, while keeping the entered configuration.
- Adds a future focused deterministic/manual iconography pass to the roadmap.

## v1.8 DEV_3_R1 — 2026-08-22
- Replaces the reserved Batch button with a dedicated bilingual Batch Generation window.
- Configures 1 to 4 maps independently: mode, archetype, modifiers placeholder, size, player count and seed.
- Runs the existing protected v1.5 pipeline sequentially and reuses matching session-cache results.
- Displays per-map waiting/running/success/error/cancelled states and progress without interrupting the active engine call.
- Adds every successful result to session history; after completion, each result can be displayed or assigned directly to comparison slot A or B.
- Pending maps can be cancelled after the current synchronous generation finishes; successful and failed maps remain available in the window.
- Adds `.pytest_cache/` to Git exclusions; generation engine, protected profiles and native library unchanged.

## v1.8 DEV_2_R7 — 2026-08-22
- Resets the inherited elastic header column left behind by the pre-R6 layout, allowing Language/Help/Theme to reach the actual right edge.
- Raises the wide-to-compact breakpoint from 1600 to 1750 px after GIF review showed the theme button clipping immediately before reflow.
- A/B identity buttons now use natural translated text width whenever Session has room and compact only near the real minimum.
- Active individual A/B delete actions use a deterministic red cross icon; empty slots keep a disabled muted cross.
- R6 three-region structure and minimum layout preserved; generation engine v1.5 unchanged.
- Windows resize validation completed from the user-provided R7 GIF, both with empty and populated A/B slots: wide/compact transition, right anchoring, adaptive A/B widths, active red crosses and minimum layout validated.

## v1.8 DEV_2_R6 — 2026-08-22
- Replaces the widget-by-widget header grid with three independent functional regions: Generation, Session/Comparison and global controls.
- Wide mode keeps Session/Comparison genuinely centered between Generation and Language/Help/Theme.
- Compact mode moves whole regions only; global controls no longer mix with generation parameters.
- Generation selectors and action rows use independent local layouts, so button spacing no longer depends on unrelated columns above.
- Import/Export/PNG Preview buttons use their natural translated text width and are no longer clipped.
- Viewer Zoom minimum behavior intentionally unchanged; generation engine v1.5 and protected assets unchanged.

## v1.8 DEV_2_R5_R5 — 2026-08-22
- Header/layout aligned to the Paint 3 reference; stable shared structure across widths.
- Reserved `Générer lot…` / `Generate batch…` action slot for v1.8 Batch.
- Session/Comparison compact A/B layout; compact mode fits the 900 px minimum runtime width.

## v1.8 DEV_2
- Responsive header/layout v1 for 1080p and smaller windows.
- Formal Status/Feedback bar v1 with FR/EN user-facing messages.
- Fast generator stages remain in progress UI instead of replacing readable status text.

# v1.8 DEV_1 — 2026-08-21

- Start of the v1.8 Workflow / Accessibility / Production line.
- Full FR/EN window-title localization.
- A/B comparison reset controls (A, B, A+B) and removal of redundant summary text.
- Post-v1.7 recovery/archaeology references integrated.
- Release-note archive cleanup for v1.5/v1.6.
- No generator-engine changes.

## v1.7 STABLE — 2026-08-21
- Promoted RC_1 after user validation on Windows.
- User smoke validation: GUI operational, exports operational, exported EDM reloads correctly, and in-game View Map works without regression.
- No feature changes from RC_1; release promotion and documentation/archive hygiene only.
- Archived v1.7 DEV/RC notes under `references/release_notes/v1_7_history/`.

## v1.7 RC_1 — 2026-08-21
- Feature freeze after user validation of DEV_11_R2.
- Global release review completed; no functional blocker found.
- Fixed stale GUI window title (`DEV_9` → `v1.7 RC_1`).
- Refreshed README, release validation and current snapshot for the real v1.7 RC phase.
- No generation-engine change.

## v1.7 DEV_11 — 2026-08-21
- Final planned feature DEV before v1.7 RC.
- Corrected Terrain ID24 classification: Grass now includes and visually segments Green Grass ID16 + Dry Grass ID24.
- Added contextual terrain/object/resource IDs to graph tooltips; global mining tooltips identify both mineral ID and open-rock/Snow-family terrain IDs.
- Confirmed Statistics as a structured FR/EN user-facing surface; Stats schema v7.
- Updated forward TODOs without adding Graph↔Map coupling or extra proximity radii.
- Generation engine v1.5 unchanged.

## v1.7 DEV_9 — 2026-08-21
- Mini-polish DEV_8 review: external chart values always use the left annotation lane.
- Nearby mining excludes Snow-family-covered ore; Stats schema v5.
- Nearest-opponent cue reordered to `→ [color] Pn`.
- Top-3 component labels replaced by compact `# + medal` badges.
- Generation engine v1.5 unchanged.

## v1.7 DEV_2 — 2026-08-20

## v1.7 DEV_5 — 2026-08-20
- Stats chart redesign: vertical normal charts, semantic colors and segmented bars.
- Water split Ocean/Lakes; Mountain split non-snow/Snow; mining stock split outside/under Snow family.
- Building Stone states renamed by remaining stock; Forestry Resources category; Agriculture colors aligned with map view.
- Compact same-row A/B comparison.
- Land-height distribution used for height chart; global min removed from chart.
- Read-only selectable report panes and progress feedback for uncached Stats during history/comparison.
- Stats schema v3; 49 tests PASS.
- Cache LRU dédié aux statistiques dérivées pour accélérer historique et bascule A/B.
- Correction du comptage des arbres adultes : IDs 68–77 et 80–81 pris en compte ; 73–77/80–81 libellés comme arbres adultes sans inventer d’espèce.
- ID84 conservé comme « Pousse d’arbre » / « Tree sapling ».
- Graphes explicitement horizontaux (catégories Y, valeurs X) avec grille de lecture.
- Police système Unicode pour accents français (Segoe UI/Arial/DejaVu selon plateforme).
- Familles terrain ordonnées : Herbe, Montagne, Désert, Marais, Boue, Rivage, Rivière, Eau.
- Ajout de la famille Boue (23/144/145), visible même à 0 dans le graphe.
- Transitions agrégées dans leurs familles analytiques (Désert, Marais, Montagne).
- Palette graphique centralisée pour permettre une refonte couleur ultérieure sans toucher aux calculs.
- 42 tests automatisés PASS ; hashes du moteur v1.5 inchangés.

## v1.7 DEV_1 — 2026-08-20

- Première passe GIGA Stats sans modification du moteur de génération v1.5.
- Nouveau modèle d’analyse structuré : terrain, objets, minerais, poissons, végétation, Building Stones, agriculture, relief, hydrologie et starts.
- `Object ID 84` exposé comme **Pousse d’arbre / Tree sapling**, jamais comme identifiant technique utilisateur.
- Stock minier réel (quantité basse du byte ressource), distributions et occupation du support montagne.
- Building Stones 115..127 : anchors, états, stock exploitable exact et ID127 à stock nul.
- Premiers graphes intégrés : terrains, stock minier, états de pierres, végétation, hauteurs, agriculture et distances de starts.
- Exports Stats JSON, CSV et graphe PNG.
- 38 tests automatisés PASS ; hashes moteur/profils/librairie v1.5 inchangés.

## v1.6 STABLE — 2026-08-20

- RC_9 validée comme checkpoint final v1.6.
- UI/outillage post-v1.5 consolidé : Heatmap, vues Chemins/Cultures, FR/EN, inspecteur, cache/historique/A-B, raccourcis, thèmes, palettes, import SAV runtime et territoire initial exact.
- Overlay de chargement centré dans la zone carte validé en thèmes clair et sombre.
- Nettoyage des checklists, notes et manifests temporaires de RC avant packaging STABLE.
- Moteur de génération v1.5 et profils Legacy/Upgraded conservés inchangés.
- Prochaine étape : grosse passe Statistiques.

## v1.6 RC_9 — 2026-08-20

- Ajustement ultra ciblé de l’overlay de progression : en thème clair, suppression du halo/contour noir autour du texte dans la barre.
- Couleur du texte inchangée ; rendu thème sombre inchangé.
- Moteur v1.5, profils et données natives inchangés.

# Changelog

## v1.6 RC_8 — 2026-08-20

- remplace la popup de progression par un overlay responsive centré dans la vue carte ;
- conserve une seule barre de progression ;
- affiche le détail technique directement dans la barre ;
- adapte automatiquement la largeur et le centrage au viewport carte ;
- aucune modification du moteur de génération v1.5.

## v1.6 RC_7 — popup robuste / molette / hover menus raster

- Popup de chargement : abandon du placement absolu interne ; le contenu remplit maintenant réellement le `Toplevel` fixe 420×108, avec barre 384 px et marges symétriques de 18 px.
- Le changement de texte de progression ne modifie plus la géométrie du dialogue ni de la barre.
- Molette restaurée sur les sélecteurs raster Vue, Filtre carte thermique et Langue.
- Hover/pressed des sélecteurs raster explicitement thémé : sombre lisible en thème sombre, clair lisible en thème clair.
- Nommage de release normalisé : `DEV`, `RC`, `STABLE`; dossier de cette build `mapgen_v1_6_RC_7`.
- Moteur de génération v1.5 inchangé.

## v1.6 RC_6 — popup fixe / filtre thermique / drapeaux

- Fenêtre de chargement à géométrie fixe 420×108 : les changements de libellé ne redimensionnent plus la popup et la barre reste centrée avec marges symétriques.
- `Ressource carte thermique` renommé **Filtre carte thermique** / **Heatmap filter**, pour ne pas limiter le sélecteur aux seules ressources à terme.
- Sélecteur de langue remplacé par le même système raster coloré que Vue/Carte thermique, avec drapeaux France et Royaume-Uni dessinés par Pillow (aucun emoji dépendant du rendu Windows).
- Icônes Vue/Carte thermique, cadenas, palettes joueurs/minerais, traductions et thème clair conservés tels que validés en R5/R4.
- Moteur de génération v1.5 inchangé.

## v1.6 RC_5 — sélecteurs raster / verrouillage / finition popup

- Remplacement des emoji de couleur des listes Vue et Carte thermique par de vraies icônes raster dessinées par Pillow : rendu coloré indépendant du support emoji Windows/Tk.
- Vue : pictogrammes distincts (global, élévation, ressources, territoires, chemins, cultures, carte thermique) au lieu de simples pastilles.
- Carte thermique : pastilles raster par ressource, avec les couleurs métier centralisées.
- Verrou Carte thermique : icône raster rouge fermée / verte ouverte, sans disque Unicode gris.
- Listes Mode/Archétype élargies pour limiter les débordements des traductions.
- Fenêtre de chargement : marge horizontale symétrique autour de la barre Canvas.
- Palette joueurs, palette ressources minières, traductions, thème clair et moteur v1.5 conservés tels que validés en R4.
- Moteur de génération v1.5 inchangé.

## v1.6 RC_4 — corrections visuelles/localisation

- Palette joueurs : P9 quasi blanc/ivoire ; halo noir autour des contours initiaux colorés.
- Vue Ressources recalée sur la capture éditeur : charbon noir, fer orange, or jaune, gemmes rouge, soufre beige/ocre mieux séparé.
- Icônes colorées renforcées dans Vue et Carte thermique.
- Cadenas jaune fermé / vert ouvert pour le sélecteur de Carte thermique.
- Traductions FR/EN renforcées, y compris modes, archétypes, Élévation et Carte thermique.
- Correction robuste des listes déroulantes en thème clair.
- Fenêtre de chargement : barre Canvas unique pour supprimer le glitch de fragment ttk.
- TODO enrichi pour la future refonte UI, Outils Map et loupe flottante d’inspection.
- Moteur de génération v1.5 inchangé.

## v1.6 RC_1 — UI/outillage post-v1.5

- Moteur de génération v1.5 stable conservé sans changement de règle.
- Regroupement des ajouts post-v1.5 : Heatmap, Chemins/Terrain28, Cultures, FR/EN, inspecteur, cache LRU, historique, A/B léger, raccourcis configurables et aide F1.
- Palette joueurs P1..P20 remplacée par une candidate plus fidèle au jeu, centralisée pour validation/calibration.
- SAV v11 : extraction des coordonnées de départ d'origine depuis le bloc joueur type 6.
- Territoire initial : remplacement de l'ellipse approximative par le masque natif exact 3500 cellules / 71×71 / bord HEX6 210 cellules.
- Terrain22/28 runtime préservé à l'import SAV.
- Export nommé `MapGenV1_6`; SAV toujours copié inchangé uniquement.
- Tests modernisés sur le moteur final v1.5 et nouveaux tests SAV/territoire/cache/préférences/preview.

## v1.4 candidate — dark mode / visualization comfort
- Thème sombre/clair, préférences persistantes, overlays, drag/zoom et progression étendue.
- Projection parallélogramme à décalage de 0,5 cellule par ligne.
- P1..P20 bitmap nets, couleur joueur, non déformés.
- Contour territoire initial SAV : 3500 cellules, étendue ±35.
- Combobox corrigées en sombre et sliders click-to-position.
- Bug connu : fournitures `Défaut` à investiguer.


## v1.3.2 — editor-safe starts / snow blocking / swamp transitions
- Starts : ajout d'une marge de sécurité éditeur autour des 33 cellules natives, sans nettoyage artificiel du terrain.
- Starts : distance conservatrice accrue vis-à-vis de l'eau et exclusion stricte des objets statiques dans le halo éditeur.
- Building Stones : le footprint complet doit désormais rester hors du halo protégé du start, pas seulement l'ancre.
- Neige : `Snow129` et `Snow128` deviennent non marchables via l'accessibility statique, sur le même principe que le correctif Water.
- Marais : reconstruction systématique `Grass16 -> 21 -> 81 -> 80` depuis le masque complet ; les mini-marais de départ utilisent désormais une famille cohérente.
- Validators : ajout de contrôles d'accessibilité Snow et de chaînes de transitions Desert/Swamp/Snow.
- TODO Markdown enrichi avec les prochaines améliorations UI/statistiques demandées.
- Suppression de `docs/user_todo_20260818.txt`, désormais entièrement absorbé dans `TODO_MAPGEN.md`.
- Développé avec l'assistance de ChatGPT.

## v1.3.1 — preview crash fix / README presentation
- Correction du crash `NameError: Image is not defined` lors de la génération/rafraîchissement de l'aperçu.
- Import explicite de `PIL.Image` utilisé par le redimensionnement/zoom.
- Ajout d'un test de non-régression dédié au rendu GUI.
- README entièrement remis à jour avec une présentation du projet, les modes, archétypes, architecture des starts et état réel de la v1.3.1.
- Aucun changement dans les règles de génération Legacy/Upgraded.

## v1.3 — tooling / UX
- Ajout barre de progression par étapes de pipeline.
- Bouton seed aléatoire.
- Import EDM/MAP/SAV (SAV en lecture seule).
- Vues Global / Heightmap / Ressources / Territoires.
- Zoom par slider et molette.
- Sélecteur de toutes les tailles natives + max joueurs dynamique.
- Génération reste volontairement limitée à 768 tant que les autres tailles ne sont pas calibrées.
- Onglet Statistiques basique.
- Scrollbars sur les onglets texte.
- Export SAV non inventé : copie inchangée seulement si la source importée est déjà un SAV.
- TODO actualisé avec la généralisation future de la morphologie Upgraded.

## v1.7 DEV_10
- Stats/debug: exhaustive Terrain/Object ID inventories.
- Stats schema v6 with normalized /1000 densities using relevant support denominators.
- Generic interactive chart tooltips, including A/B.
- A/B slot buttons now expose a visible set-state (green LED + short map identity).
- Documentation/TODO cleanup before RC preparation.
## v1.8 DEV_2_R3 — header layout refinement

- Reorganizes the application header by function instead of historical grid position.
- On normal 1080p-width windows, Generation stays left, Session/Comparison uses the center, and Language/Help/Theme stay right.
- `Copier seed` / `Copy seed` stays next to the Seed controls.
- Inspector remains visible in the upper application area rather than being hidden under the map viewer.
- Feedback/status remains a prominent thin messenger strip immediately above the main map/data area.
- Compact mode is now reserved for genuinely narrow windows instead of being forced solely by 1080p screen height.
- Viewer toolbar/progress/feedback behavior from R2 is preserved.

## v1.8 DEV_2_R2 — responsive/feedback follow-up
- 1080p explicit compact target.
- Viewer-specific toolbar for View / Heatmap filter / Recenter / Zoom, with its own reflow.
- Removed the obsolete header Progressbar from layout to prevent the persistent pale strip after resize.
- Expanded Status/Feedback v1 for A/B toggle, empty cache, theme button, recenter, random seed, graph/stat exports, opacity lock and player-count changes.
- No generation-engine changes.
## v1.8 DEV_2_R4 — header density + modifiers reservation

- Reserved a future multi-select **Modifiers** control after Archetype; current value is None only.
- Wired modifiers into generation cache/history/status semantics without touching generator v1.5.
- Reduced Session history field width and reflowed Load/Clear cache actions on constrained widths.
- Stacked Help/Theme below Language in compact mode.
- Progress overlay unchanged and validated.
