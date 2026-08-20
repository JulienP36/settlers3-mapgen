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

- [ ] **Finaliser la synchro byte-for-byte de `dev` avec le ZIP DEV_5 testé** pour tous les gros fichiers source/runtime/tests/docs concernés. Le lancement depuis `dev` est réparé, mais le connecteur GitHub ne peut pas ingérer directement les gros fichiers locaux et le runtime n'a pas de DNS GitHub ; ne pas déclarer DEV_5 totalement checkpointé tant que cette équivalence n'est pas vérifiée.
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
- [ ] Comparaison A/B avancée côte-à-côte/diff uniquement si l'usage réel le justifie.
- [ ] Étendre éventuellement les commandes rebindables après retour d'usage.

## v1.7 DEV — GIGA passe Statistiques

### Socle implémenté jusqu'à DEV_5

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
- [x] graphes normaux testés en orientation verticale ;
- [x] comparaison A/B compacte : une métrique par ligne, barre A + barre B côte à côte, valeur dans chaque barre ;
- [x] panneaux texte d'analyse read-only mais sélectionnables/copiëables ;
- [x] feedback de progression lors d'un calcul Stats non caché sur historique/comparaison ;
- [x] invariants mathématiques pour les nouvelles barres segmentées ;
- [x] validation DEV_5 locale : 49 tests PASS + smoke SAV 768×768 / 10 joueurs + hashes protégés inchangés.

### Après DEV_5 — Stats / UI à poursuivre

- [ ] Recalibrer les distances de ressources autour des starts : conserver les rayons DEV_4 comme exploration mais étudier une lecture gameplay autour de ~50/60 HEX (claim rapide probable) et ~100 HEX (sécurité stratégique, notamment minerais).
- [ ] Permettre d'ajouter aux slots A/B des cartes importées `.SAV`, `.EDM` et `.MAP`, pas seulement des générations conservées dans la session.
- [ ] Couleurs A/B personnalisables.
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
