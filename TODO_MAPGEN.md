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
génération ou de format. Depuis le reset DEV_2, la protection concerne le
chemin de compatibilité Upgraded ; l'ancien Legacy v1.5 et le générateur
procédural DEV_1 ont été explicitement retirés.

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

La **reconstruction complète du pipeline** est maintenant le périmètre v2.0.
Le générateur procédural Continental de DEV_1 a été retiré : ses volumes
minéraux étaient calibrés, mais ses formes n’étaient pas assez proches du
jeu. DEV_2 repart de l’audit décompilé et conserve uniquement le chemin
Upgraded validé pendant cette reconstruction.

- [x] Ancien pipeline Legacy DEV_1 retiré, y compris ses profils, helpers et
  bibliothèques de silhouettes dérivées.
- [x] Chemin Upgraded isolé et conservé avec ses règles, profils et validations
  de compatibilité.
- [x] Comparaison des minerais DEV_1/natif archivée : mix proche, géométrie
  trop fragmentée ; aucune heuristique minérale DEV_1 ne devient une règle.
- [x] Première passe de l'audit non-terrain ajoutée : ordre Area/bâtiments/
  colons/départs/ressources de départ/métadonnées, cellules runtime, couches
  ressources/objets et filtre exact des positions de départ.
- [x] Deuxième passe approfondie : layout exact du type 9 et de son registre,
  catalogue paramétrique `0x51B010/0x51B1A0`, compteurs d'essais distincts,
  chemin `GameDataSave::Save` et records SAV générés.
- [ ] Achever l'audit non-terrain : retrouver le producteur aléatoire type 9,
  relier l'export des objets runtime au byte 2 Area, décoder les empreintes et
  tables d'offsets, nommer les métadonnées et identifier le writer EDM/MAP ; voir
  `references/S3_EXE_STATIC_NON_TERRAIN_AUDIT_20260901.md`.
- [ ] Implémenter le noyau Legacy natif séparé : seed, relief, familles de
  terrains, transitions, hydrologie et ordre d’écriture démontrés.
- [ ] Définir l’archétype Continental v1 au-dessus de ce noyau sans lui
  appliquer une seconde macro-forme.
- [ ] Reproduire ensuite les starts, minerais, objets et validations Legacy
  avec les mesures natives, puis tester chaque taille et densité de joueurs.
- [ ] Ajouter modificateurs et autres archétypes après ce socle.
- [ ] Concevoir ensuite le mode **Custom laboratoire** séparé : catalogue,
  presets, batch, diagnostics et garde-fous.
- [ ] Revalider progressivement terrains, transitions, joueurs, ressources,
  macro-forme et côtes dans l'éditeur/jeu avant tout nouveau mode.

### Garde-fous

- [ ] Préserver la chaîne eau → plage/rive → terrain, la topologie HEX6 et les
  règles hydrologiques mesurées.
- [ ] Ne jamais mélanger Legacy et Upgraded ; chaque mode garde profils,
  références et tests séparés.
- [x] Maintenir l'ordre start-first du projet, le footprint natif et la
  protection sans halo ; l'ordre interne natif reste inconnu.
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
- [ ] Concevoir les vues composables, légendes, conflits et le Pilotage de la
  vue depuis les Graphiques.
- [ ] Repenser Comparaison, signalétique Chargée/Affichée/Affectée et A/B avancé
  seulement si l'usage le justifie ; multi-cartes 3+ après le générateur.
- [ ] Concevoir labels J1–J20, loupe locale, inspecteur près du curseur et
  indépendance des toggles.
- [ ] Reporter responsive UI v2, Status/Feedback v2, centres d'export et
  diagnostic mémoire v1.11 à une passe dédiée avec mesures factuelles.

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
- Starts placés tôt et protégés ; minerais Upgraded v7 no-gap préservés.
- Aucun aperçu ou asset imaginaire ; SAV lu sans réinvention et copié inchangé.
- IDs inconnus explicitement inconnus ; ne jamais repartir d'une version
  invalidée du générateur.
