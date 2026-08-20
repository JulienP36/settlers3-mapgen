# Settlers III MapGen — TODO programme

> Workflow global : `PROJECT_WORKFLOW.md`  
> Snapshot courant/reprise : `references/SETTLERS3_CURRENT_SNAPSHOT.md`

## État de validation

- [x] **v1.5 VALIDÉE / STABLE** pour Continental 768×768.
- [x] Référence finale : `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- [x] Starts / éditeur / View Map / in-game / aucun crash.
- [x] Minerais Upgraded géométrie **v7 no-gap** verrouillée.
- [x] Legacy / Upgraded séparés.
- [x] Building Stones 115..127 et ID127 constructible gérés.
- [x] Bonus de départ Upgraded validés.
- [x] **v1.6 STABLE UI/outillage** : validation utilisateur terminée (RC_9 validée), tag et GitHub Release publiés.
- [x] Branches permanentes `dev` / `rc` / `main` mises en place.
- [x] Workflow projet canonique + snapshot vivant de reprise mis en place.
- [x] Crash Git checkout lié au mélange `gui_v15.py` / `SessionGenerationCache` réparé sur `dev`.
- [x] Audit branches : seules `main`, `dev`, `rc` subsistent.

## Règle de release / branches

**Ne pas modifier la génération v1.5 validée sans raison explicite.**

- `dev` = développement courant + checkpoints fréquents ;
- `rc` = candidate en validation ;
- `main` = STABLE uniquement.

v1.6 est une surcouche UI/outillage ; le moteur v1.5 reste la référence validée.

## Hygiène GitHub / source

- [ ] **Finaliser la synchro byte-for-byte de `dev` avec le dernier ZIP DEV testé** pour tous les gros fichiers source/runtime/tests/docs concernés. Le lancement depuis `dev` est réparé, mais ne pas déclarer un DEV totalement checkpointé tant que cette équivalence n'est pas vérifiée.
- [ ] Lors du prochain refactor contrôlé, renommer les modules ambigus `v15` / `v16` vers la convention explicite `v1_5` / `v1_6` (ex. `gui_v1_5.py`, `gui_v1_6.py`, runtimes et `generator_v1_5.py`) avec migration atomique des imports, tests, scripts et entry points. **Ne pas renommer à chaud** les fichiers validés.
- [x] Ajouter au workflow la règle : un build n'est pleinement checkpointé que lorsque package testé et branche Git contiennent le même état source/runtime/tests/docs prévu.

## UX / outillage — v1.6

- [x] Import EDM / MAP / SAV ; export EDM+MAP 768.
- [x] Global / Heightmap / Ressources / Territoires.
- [x] Chemins / Terrain28 et Terrain22 runtime.
- [x] Cultures.
- [x] Heatmap ressources.
- [x] FR/EN persistant.
- [x] Inspecteur exact de cellule au survol.
- [x] Zoom / drag / projection / recentrage.
- [x] Thème sombre/clair ; combobox lisibles ; sliders click-to-position.
- [x] Cache transparent LRU mémoire de session, 8 générations.
- [x] Historique de session.
- [x] Comparaison A/B légère avec conservation du contexte visuel.
- [x] Raccourcis configurables/persistants + conflits + reset.
- [x] Aide F1 dynamique.
- [x] Palette P1..P20 validée visuellement ; P9 quasi blanc/ivoire et contours noirs validés.
- [x] Contour de zone de départ d'origine sur import SAV : bloc joueur SAV + masque natif exact 3500 cellules, validé visuellement.
- [ ] Ajouter un raccourci configurable de **toggle thème clair/sombre** pour faciliter les tests.
- [ ] Ajouter les cartes importées `.SAV` / `.EDM` / `.MAP` à l'**historique de session**.
- [ ] Rendre la taille de l'historique de session configurable (valeur actuelle 8 comme défaut possible).
- [ ] Étendre éventuellement les commandes rebindables après retour d'usage.
- [ ] Export PNG : améliorer plus tard la netteté/résolution des graphes et de la vue map lors d'un zoom important.

## v1.7 DEV — GIGA passe Statistiques

### Socle implémenté jusqu'à DEV_6

- [x] nombre exact de cellules par Terrain ID ;
- [x] familles de terrain avec transitions agrégées ;
- [x] Boue/Mud incluse (`23/144/145`) ;
- [x] quantité par Object ID ;
- [x] minerais : cases occupées + stock réel + percentiles ;
- [x] stock total exploitable Building Stones ;
- [x] distribution des états 115..127, avec ID127 = 0 stock exploitable ;
- [x] ressources forestières : arbres adultes séparés des pousses d'arbre ID84 et palmiers ;
- [x] poissons / hydrologie ;
- [x] agriculture runtime SAV ;
- [x] relief / percentiles de hauteur terrestre ;
- [x] distances entre starts ;
- [x] exports JSON / CSV ;
- [x] graphes intégrés + export PNG ;
- [x] cache Stats de session pour éviter le recalcul lors des bascules A/B/historique ;
- [x] analyse locale joueurs en vrais rayons HEX10/20/30/40 ;
- [x] composantes/blobs avancés pour massifs, déserts, marais, forêts, minerais, lacs/rivières ;
- [x] Stats schema v3 ;
- [x] barres segmentées Eau = Mer + Lacs ;
- [x] montagne = partie non-neige + famille Neige ;
- [x] minerais = hors neige + sous neige ;
- [x] Building Stones affichés 12 pierres → 1 pierre → Épuisé ;
- [x] graphes normaux testés/validés en orientation verticale ;
- [x] comparaison A/B compacte : une métrique par ligne, barre A + barre B côte à côte, valeur dans chaque barre ;
- [x] DEV_6 : comparaison A/B segmentée pour Eau, Montagne, Ressources forestières, Minerais et Agriculture ;
- [x] DEV_6 : fichiers importés `.SAV`, `.EDM`, `.MAP` utilisables dans les slots A/B sans perdre leur statut d'import ;
- [x] panneaux texte d'analyse read-only mais sélectionnables/copiëables ;
- [x] feedback de progression prévu lors d'un calcul Stats non caché sur historique/comparaison ;
- [x] invariants mathématiques pour les nouvelles barres segmentées ;
- [x] validation DEV_5 utilisateur : exports PNG/CSV/JSON OK, texte read-only/copie OK, bascule A/B ~0,75 s, pas de Stats stale, thèmes/traductions OK ;
- [x] validation DEV_6 utilisateur : graphe A/B segmenté jugé bon, conclusions générales similaires à DEV_5.

### Corrections / raffinement Stats proches

- [ ] Graphe A/B : attribuer des couleurs sémantiques cohérentes à **Terre**, **Stock pierre** et **Stock poisson**.
- [ ] Ajouter une légende explicite au stock minier pour distinguer la portion **sous neige**.
- [ ] Ne jamais perdre la valeur d'un segment non nul trop petit pour contenir son texte : fallback extérieur/annotation/leader line ou autre solution lisible.
- [ ] Remplacer les gradients quantitatifs 2 couleurs rouge↔vert concernés par une échelle **rouge → jaune → vert** ; choisir une logique de milieu robuste (médiane/percentile 50 à privilégier lorsque pertinent).
- [ ] Stock pierres : conserver les noms validés, refaire uniquement l'échelle de couleurs en 3 points.
- [ ] Ressources forestières : ordre d'affichage **Adultes → Palmiers → Pousses**.
- [ ] Distribution des hauteurs : labels légèrement plus explicites, idéalement 2 mots, 3 maximum si nécessaire.
- [ ] Distance adversaires : rouge = distance minimale observée, jaune = intermédiaire, vert = éloigné ; afficher le nom de l'adversaire le plus proche et des carrés aux couleurs du joueur et de cet adversaire.
- [ ] Arbres proches : remplacer la lecture actuelle par 2 segments **0–50 HEX inclus** puis **>50–100 HEX inclus**, renommer simplement `Arbres proches`, gradient richesse rouge→jaune→vert.
- [ ] Pierres proches : même découpage **0–50 / 50–100**, titre simplifié et gradient 3 couleurs.
- [ ] Poissons proches : même découpage **0–50 / 50–100**, titre simplifié et gradient 3 couleurs.
- [ ] Minerais proches : passer à une lecture 0–50 / 50–100 ; tester soit une barre doublement segmentée, soit deux barres par joueur si la première devient trop dense. **Conserver les couleurs actuelles des minerais.**
- [ ] Taille des massifs : inverser la logique actuelle du gradient pour que les grandes valeurs soient visuellement plus fortes/foncées.
- [ ] Taille des lacs : grand/profond = plus foncé.
- [ ] Taille des rivières : même logique visuelle, grandes valeurs plus fortes/foncées.
- [ ] Vérifier/profiler la bascule A/B (~0,75 s avec cache) uniquement si une optimisation simple existe ; sinon considérer cette latence comme acceptable.
- [ ] Vérifier le feedback de progression A/B sur un cas volontairement non caché ; il peut être trop furtif pour être perceptible actuellement.

### Stats / interactions avancées — à cogiter plus tard

- [ ] **Tooltips interactifs sur les graphes** : survol d'une barre/segment → nom sémantique + valeur exacte. Exemple Montagne : `Libre : N cases` sur la partie grise, `Neige : N cases` sur la partie blanche.
- [ ] Étendre les tooltips à tous les graphes où ils apportent de l'information : détails de segments, joueurs, ressources, composants, ratios, etc. Prévoir une architecture générique plutôt que des handlers spécifiques partout.
- [ ] **Coupler certains graphes à la vue map** : sélectionner/changer de graphe pourrait activer automatiquement une vue contextuelle pertinente.
- [ ] Exemple sérieux : graphe Agriculture → vue Cultures ; Distance joueurs → future vue dédiée avec flèches colorées entre starts, distances et éventuellement adversaire le plus proche ; graphes de ressources → heatmap/vue correspondante lorsque pertinent.
- [ ] Concevoir ce couplage de façon non intrusive : garder possibilité de désactiver/locker la vue si l'utilisateur veut comparer des graphes sans changer la carte.
- [ ] Recalibrer les distances de ressources autour des starts : les rayons DEV_4 restent exploratoires ; lecture gameplay cible autour de **50/60 HEX** (claim rapide probable) et **100 HEX** (sécurité stratégique, notamment minerais).
- [ ] Couleurs A/B personnalisables si l'usage réel le justifie.
- [ ] Vue Hauteurs : remplacer à terme le simple dégradé blanc/gris par un rendu de type carte topographique / courbes ou classes d'altitude.
- [ ] Densités par 1000 cellules de land/eau/support pertinent.
- [ ] Comparaison MapGen ↔ corpus natif et bandes de référence.
- [ ] Per-player agriculture/claims lorsque le runtime SAV permet une lecture fiable.
- [ ] Enrichir les distributions/percentiles des massifs/lacs/rivières/clusters.
- [ ] Continuer la nomenclature des IDs sans inventer les espèces/objets inconnus.
- [ ] Explorer très tard l'utilisation de vrais sprites du jeu dans certains labels, uniquement si extraction propre et légitime des ressources graphiques possible ; ne jamais inventer de pseudo-sprites.
- [ ] Agriculture : ajouter les nids d'abeilles uniquement après identification/calibration exacte.

## Updater

- [x] `update_latest_release.bat` récupère uniquement la dernière GitHub Release STABLE dans `updates/` sans écraser l'installation.
- [ ] comparaison locale de version ;
- [ ] vérification SHA-256 automatique ;
- [ ] extraction/installation atomique sûre ;
- [ ] conservation des préférences ;
- [ ] rollback ;
- [ ] intégration UI éventuelle.

## Calibration multi-tailles — après Stats

Continental, une taille à la fois : 384×384 → 448×448 → 512×512 → 576×576 → 640×640 → 704×704 → reconfirmation 768×768.

Pour chaque taille : starts, morphologie, montagnes/neige, minerais, arbres, Building Stones, poissons, marais, désert, décorations, récifs, rivières/lacs, quotas et stabilité éditeur/View Map/in-game.

Après validation du cycle Continental : préparer **v2.0** avec premier exécutable Windows portable et build reproductible.

## Après Continental

- [ ] Large Islands / Grandes îles.
- [ ] Constituer/analyser les références natives nécessaires.
- [ ] Small Islands / Petites îles ensuite.

## À préserver

- Archetype = macro-géographie.
- Legacy/Upgraded = contenu, règles, balance, ressources et objets.
- Starts placés tôt et protégés.
- Upgraded conserve impérativement les minerais v7 no-gap.
- Objet ID84 = **pousse d'arbre** côté sémantique utilisateur ; ne pas afficher `SmallTree84` dans l'UI/Stats.
- Aucun aperçu imaginaire.
- Toute image/preview = rendu déterministe réellement issu des données EDM/MAP/SAV.
- Ne jamais repartir d'une version invalidée du générateur.
- Checkpointer souvent sur `dev` et maintenir le snapshot courant à jour.

## Futur UI / analyse

- [ ] Vue dédiée Forêts / Carrières.
- [ ] Éventuellement déplacer les contours initiaux SAV vers une vue dédiée pour épurer Global.
- [ ] Nids d'abeilles amazones uniquement après identification IDs/runtime.
- [ ] Refonte générale UI et section **Outils Map**.
- [ ] Loupe flottante près du curseur, bouton + raccourci.
- [ ] Passe dédiée police des labels joueurs P 1..P 20 avec propositions visuelles.
