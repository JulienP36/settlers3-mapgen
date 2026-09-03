# Settlers III MapGen — TODO

> Roadmap orientée **travail restant**. Les étapes validées et les essais
> remplacés appartiennent à `references/dev_notes/V1_8_DEVELOPMENT_LOG.md` et
> au `CHANGELOG.md`.

## Socle validé

- [x] **v1.5 STABLE** : moteur Continental 768×768 validé dans l'éditeur,
  View Map et en jeu ; référence `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- [x] **v1.6 STABLE** : UI/outillage, import EDM/MAP/SAV, vues, inspecteur,
  thèmes, préférences et A/B.
- [x] **v1.7 STABLE** : Statistiques/Graphiques et exports d'analyse.
- [x] **v1.8 DEV_1 à DEV_11** : workflow, responsive, Batch, vues joueurs,
  exports, langues, historique, raccourcis, preuve `.exe`, verrou `M`,
  capacité dure, publication et maintenabilité.
- [x] **v1.9 DEV_3** : Data Mapping ciblé, masque SAV direct, champs joueurs,
  catalogue objets, terrains `18/19`, nids `247–253` et graphes de végétation.

Lire `references/SETTLERS3_PREGEN_READ_FIRST.md` avant toute modification de
génération ou de format. Depuis le reset DEV_2, le Legacy natif est le
checkpoint validé ; l'ancien Legacy v1.5 et l'ancien moteur Upgraded sont
remplacés par des pipelines séparés en cours de reconstruction.

## Prochaine RC/STABLE — après v1.10

La v1.8 reste une série de checkpoints DEV : aucune Release ne sera publiée
tant que la génération réelle et la diversité morphologique ne sont pas
stabilisées.

- [ ] Geler les nouvelles fonctionnalités ; garder les corrections, le polish,
  l'optimisation et la documentation autorisés.
- [ ] Produire un ZIP sources/Python et un ZIP Windows x64 portable `onedir`,
  sans installateur.
- [ ] Revalider ressources, exports, settings `%APPDATA%/Settlers3MapGen`,
  installation propre, mise à jour, absence réseau, checksum et rollback.
- [ ] Finaliser l'icône uniquement à partir du pixel art fourni manuellement ;
  aucune image IA.
- [ ] Finaliser l'updater v2 : version, téléchargement, SHA-256, settings,
  remplacement propre et rollback.
- [ ] Mettre à jour README, notes, manifests, validations et snapshot avant
  promotion.

## v1.9 — restructuration interne et Data Mapping

- [x] Imports EDM, architecture, séparation des modes, validations,
  déterminisme, Batch, UI et publication consolidés.
- [x] Fondations Tk, `MainWindow`, `runtime.App`, contrôleurs Batch/Historique
  et séparation `application/`, `generation/`, `map_data/` stabilisés.
- [x] Coût de contexte audité ; les rôles des instructions et références sont
  séparés. Le détail historique est dans le journal DEV.
- [ ] Remplacer progressivement les assertions GUI fondées sur le texte par
  des contrats de widgets, en commençant par Batch et Historique.
- [ ] Poursuivre les extractions mécaniques courtes avec comportement inchangé,
  tests ciblés puis validation complète.
- [ ] Auditer les références après publication : conserver les spécialisées,
  compacter les répétitions et migrer les liens avant toute suppression.
- [x] Première passe des objets contrôlés : souches `208–214`, pousses
  `216–222`/`224–230`, panneaux `232–242`, feu `243–246`, nids `247–253` et
  marqueurs `254–255` ; probes `215/223/231` documentées crash-prone.
- [x] Tables, tooltips, inspecteur, statistiques et graphe **Arbres et pousses**
  consolidés ; la cartographie large `128–207` est abandonnée.
- [ ] Déterminer les bornes démontrées des Terrain IDs/Object IDs et compléter
  les références sans inventer les inconnus.
- [ ] Clarifier trous/réservés, transitions et catégories SAV restantes.
- [ ] Décoder sur corpus contrôlé couleur effective, mana, tribu, nom/équipe,
  statut et ressources de départ ; rester en lecture seule.
- [x] Masque initial direct type-3 byte 8 confirmé pour le triplet 4P
  (`3500/3500/4000/4000`) ; aucune reconstruction par coordonnées.
- [x] Terrains `18/19` validés comme détails d'herbe ; objets `82/83` reportés
  à Datamining v2 faute de preuve naturelle.

## v2.0 — reconstruction native Legacy, puis Custom

La **reconstruction complète des pipelines** est maintenant le périmètre v2.0.
Le générateur procédural Continental de DEV_1 a été retiré et le Legacy natif
est validé dans DEV_2. Le chantier Upgraded a été porté dans une copie
indépendante du pipeline Legacy ; sa calibration DEV_3 et ses finitions DEV_5
sont maintenant validées, avec uniquement ses différences explicites.

### v2.0 — Upgraded indépendant

- [x] Dupliquer le pipeline terrain Legacy dans `generators/upgraded/` sans
  dépendance d’exécution vers `generators/legacy/`.
- [x] Réintégrer la génération calibrée des minerais de montagnes.
- [x] Réintégrer poissons, arbres, décorations et pierres de construction.
- [x] Dev 5 validé : calquer les objets statiques sur les familles Legacy, conserver
  les récifs Upgraded, restaurer les bonus arbres/pierres/mini-marais, placer
  30 % des adultes en mini-forêts, réserver les pousses aux forêts et créer
  les clusters de pierres.
- [x] Désactiver toute génération de boue dans Upgraded.
- [x] Garder le positionnement des joueurs isolé pour une passe dédiée ; le
  pont actuel reste provisoire et ne crée ni ressources ni colons de départ.
- [x] Calibrer les blobs miniers avec compensation de la projection
  parallélogramme, sans changer la topologie HEX6, les quotas, les quantités ou
  la règle no-gap.
- [x] Documenter le terrain `34` comme **Patch d’herbe rocheuse**, l’ajouter au
  graphique Montagne avec une couleur dédiée et harmoniser sa couleur de carte.
- [x] Ajouter les tests de parité terrain et les validations spécifiques
  Upgraded du checkpoint DEV_3 ; la parité externe complète reste à rejouer
  dans l’éditeur/jeu lors de la prochaine validation dédiée.

- [x] Ancien pipeline Legacy DEV_1 retiré, y compris ses profils, helpers et
  bibliothèques de silhouettes dérivées.
- [x] Chemin Upgraded isolé, avec sa copie de pipeline, ses règles, son profil
  et ses validations spécifiques.
- [x] Comparaison des minerais DEV_1/natif archivée : mix proche, géométrie
  trop fragmentée ; aucune heuristique minérale DEV_1 ne devient une règle.
- [x] Première passe de l'audit non-terrain ajoutée : ordre Area/bâtiments/
  colons/départs/ressources de départ/métadonnées, cellules runtime, couches
  ressources/objets et filtre exact des positions de départ.
- [x] Deuxième passe approfondie : layout exact du type 9 et de son registre,
  catalogue paramétrique `0x51B010/0x51B1A0`, compteurs d'essais distincts,
  chemin `GameDataSave::Save` et records SAV générés.
- [x] Compléter le contrat non-terrain nécessaire au portage : banque exacte
  d'offsets hexagonaux, frontière nouvelle carte/carte chargée, choix et
  validation des départs, lots d'entités et producteur du stock initial
  (`0x506CF0 -> 0x5046B0 -> 0x504420`).
- [ ] Poursuivre séparément les résidus de format : couverture complète des
  tokens d'empreinte, nomenclature des IDs/champs, source externe type 9 et
  writer EDM/MAP ; voir `references/S3_EXE_STATIC_NON_TERRAIN_AUDIT_20260901.md`.
- [x] Documenter l'ordre natif complet observable : noyau terrain, objets et
  ressources de sol, re-seed, départs, ville/stock et finalisation.
- [x] Implémenter le noyau Legacy natif séparé : seed, relief, familles de
  terrains, transitions, hydrologie et ordre d’écriture démontrés.
- [x] Définir l’archétype Continental v1 au-dessus de ce noyau sans lui
  appliquer une seconde macro-forme.
- [x] Reproduire le terrain, les ressources globales (minerais/poissons), les
  objets/décorations et les validations Legacy avec les mesures natives ; les
  objets/ressources de départ, colons et writer SAV restent hors périmètre.
- [x] Exposer les tailles natives 256–1024, les miroirs Axe long/Axe court/Les
  deux pour Legacy et Upgraded, les avertissements de viabilité et l'export
  MAP/EDM multi-tailles via scaffold de test.
- [x] Laisser toutes les tailles du contrat générables et exportables pour
  test, sans refus lié au statut « non testé » ; conserver les avertissements
  uniquement comme information.
- [ ] Dev 6 : implémenter le générateur **Custom** séparé : catalogue, presets,
  batch, diagnostics et garde-fous.
- [ ] Dev 7 : définir l’archétype **Custom** au-dessus du générateur dédié.
- [ ] Dev 8 : ajouter les premiers modificateurs, après validation de l’archétype.
- [ ] Revalider progressivement terrains, transitions, joueurs, ressources,
  macro-forme, côtes et exports 832–1024 dans l'éditeur communautaire/jeu.

### Garde-fous

- [ ] Préserver la chaîne eau → plage/rive → terrain, la topologie HEX6 et les
  règles hydrologiques mesurées.
- [ ] Ne jamais mélanger Legacy et Upgraded ; chaque mode garde profils,
  références et tests séparés.
- [x] Maintenir l'ordre natif démontré : terrain/objets/ressources, re-seed,
  départs, ville/stock puis finalisation ; conserver le footprint natif et la
  protection sans halo.
- [x] Séparer décor initial byte 14, objet runtime byte 7 et byte 9 SAV encore
  inconnu.
- [ ] Toute comparaison visuelle doit venir d'un EDM/MAP/SAV réel ou d'une
  génération déterministe identifiée.

## Analyse et UI futures

- [ ] Rafraîchir le rapport Statistiques après changement de langue ; améliorer
  inventaires, IDs absents, familles runtime et distributions de composants.
- [ ] Étudier histogrammes, profils radiaux/cumulatifs et références corpus sans
  produire de visualisation trompeuse.
- [ ] Garder exactement deux rayons configurables pour les ressources proches.
- [ ] Revoir résolution des exports PNG et éventuellement transformer Hauteurs
  en carte topographique/classes d'altitude.
- [x] Première liaison Graphiques → Vue avec payloads sémantiques, cache de
  surbrillance et conservation du cadrage ; A/B reste volontairement
  informatif (tooltip uniquement).
- [x] Router tous les graphes **X proche(s)** vers la vue globale, ancrer leur
  flèche aux bordures des territoires de départ d’origine et conserver le
  contexte des départs via les marqueurs/cercle partagés.
- [x] Ajouter les tailles de marqueurs Petits / Normaux / Grands (plus
  Masqués), conserver la compatibilité des préférences historiques et propager
  le réglage à toutes les vues, Batch et Historique.
- [x] Supprimer la vue dédiée Départs et ajouter l’option indépendante
  **Cercles de départ**, propagée à toutes les vues et previews sans lien avec
  l’opacité couche.
- [x] Renommer le graphique des objets en **Familles d’objets** et figer son
  ordre de colonnes sur les nombres rouges de la référence utilisateur.
- [x] Corriger le flash initial de la fenêtre **Générer un lot** en la gardant
  masquée pendant la construction de ses contrôles et de sa géométrie.
- [x] Corriger le centre d’export multi-taille et conserver `references/` dans
  les ZIP sources tout en l’excluant des commits/push GitHub.
- [ ] Étendre le pilotage de la vue depuis les Graphiques : légendes, conflits,
  clic persistant et multi-cartes 3+.
- [ ] Repenser Comparaison, signalétique Chargée/Affichée/Affectée et A/B avancé
  seulement si l'usage le justifie ; multi-cartes 3+ après le générateur.
- [ ] Concevoir labels J1–J20, loupe locale, inspecteur près du curseur et
  indépendance des toggles.
- [ ] Reporter responsive UI v2, Status/Feedback v2, centres d'export et
  diagnostic mémoire v1.11 à une passe dédiée avec mesures factuelles.

- [ ] Implémenter dans Upgraded la passe séparée du positionnement des starts et
  des données natives `.sav` ; Dev 5 utilise le pont de coordonnées existant
  sans le recalculer.

## Personnalisation, après Continental et ENDGAME

- [ ] Relire DE/ES, versionner les packs de langue et thèmes déclaratifs, puis
  étendre éventuellement les commandes rebindables.
- [ ] Créer l'iconographie UI et le pixel art manuellement ; maintenir la
  provenance des assets et ne rien importer sans validation.
- [ ] Après Continental, analyser les références natives de **Large Islands**,
  puis **Small Islands**, avant les Modifiers.
- [ ] Garder ENDGAME pour la fin : générer, importer, inspecter, modifier,
  valider et exporter seulement les données EDM/MAP/SAV comprises.

## Invariants

- Archetype = macro-géographie ; Legacy/Upgraded = contenu, règles, balance,
  ressources et objets.
- Legacy : terrain/objets/ressources avant re-seed, puis starts/ville/stock ;
  Upgraded : terrain copié indépendant, contenu global spécifique, minerais v7
  no-gap préservés et bonus de contenu autour des coordonnées de départ
  provisoires.
- Aucun aperçu ou asset imaginaire ; SAV lu sans réinvention et copié inchangé.
- IDs inconnus explicitement inconnus ; ne jamais repartir d'une version
  invalidée du générateur.
