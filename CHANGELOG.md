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
