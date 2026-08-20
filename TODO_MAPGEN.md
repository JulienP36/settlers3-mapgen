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

## Règle de release / branches

**Ne pas modifier la génération v1.5 validée sans raison explicite.**

- `dev` = développement courant + checkpoints fréquents ;
- `rc` = candidate en validation ;
- `main` = STABLE uniquement.

v1.6 est une surcouche UI/outillage ; `generator_v15.py` reste le moteur de référence.

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
- [ ] Comparaison A/B avancée côte-à-côte/diff uniquement si l'usage réel le justifie.
- [ ] Étendre éventuellement les commandes rebindables après retour d'usage.

## v1.7 DEV — GIGA passe Statistiques

### Socle déjà implémenté

- [x] nombre exact de cellules par Terrain ID ;
- [x] familles de terrain avec transitions agrégées ;
- [x] Boue/Mud incluse (`23/144/145`) ;
- [x] quantité par Object ID ;
- [x] minerais : cases occupées + stock réel + percentiles ;
- [x] stock total exploitable Building Stones ;
- [x] distribution des états 115..127, avec ID127 = 0 stock exploitable ;
- [x] végétation : arbres adultes séparés des pousses d'arbre ID84 ;
- [x] poissons / hydrologie de base ;
- [x] agriculture runtime SAV ;
- [x] relief / percentiles de hauteur ;
- [x] distances entre starts ;
- [x] exports JSON / CSV ;
- [x] graphes intégrés + export PNG ;
- [x] graphes en barres horizontales ;
- [x] police de graphes compatible accents français ;
- [x] ordre logique des familles de terrain ;
- [x] cache Stats de session pour éviter le recalcul lors des bascules A/B/historique ;
- [x] tests Stats intégrés ; suite courante : 42 PASS au checkpoint DEV_2/DEV_3.

### Suite immédiate Stats

- [ ] richesse locale par joueur/start aux rayons HEX10/20/30/40 ;
- [ ] comparaison joueurs/fair-play plus riche ;
- [ ] comparaison A/B Stats dédiée : tableaux + graphes ;
- [ ] densités par 1000 cellules de land/eau/support pertinent ;
- [ ] blobs / composantes : désert, marais, boue, montagne/neige, forêts, lacs, minerais ;
- [ ] massifs / lacs / rivières / clusters : tailles et distributions ;
- [ ] statistiques de morphologie/compacité/longueur pertinentes ;
- [ ] comparaison MapGen ↔ corpus natif ;
- [ ] passe complète de nomenclature des Object IDs connus sans inventer les espèces/objets non calibrés ;
- [ ] nouvelle palette/couleurs de graphes ;
- [ ] suivi Terrain24 / Terrain22 / Terrain28 ;
- [ ] autres métriques et graphes pertinents tant que lisibles/exploitables.

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
