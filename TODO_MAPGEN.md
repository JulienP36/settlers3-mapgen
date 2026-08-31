# Settlers III MapGen — TODO

> Roadmap orientée **travail restant**. Les étapes validées et les essais remplacés appartiennent à `references/dev_notes/V1_8_DEVELOPMENT_LOG.md` et au `CHANGELOG.md`.

## Socle validé

- [x] **v1.5 STABLE** : moteur Continental 768×768 validé dans l’éditeur, View Map et en jeu ; référence `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- [x] **v1.6 STABLE** : UI/outillage, import EDM/MAP/SAV, vues, inspecteur, thèmes, préférences et A/B.
- [x] **v1.7 STABLE** : Statistiques/Graphiques et exports d’analyse.
- [x] **v1.8 DEV_1 à DEV_11** : workflow, responsive, Batch, vues joueurs, exports, quatre langues, historique, raccourcis v2, preuve `.exe`, verrou `M`, capacité dure, publication et maintenabilité.
- [x] **v1.9 DEV_3** : Data Mapping ciblé, masque initial SAV direct, champs joueurs démontrés, catalogue objets confirmé, terrains `18/19`, nids `247–253` et graphes de végétation cumulés.

Règle absolue : ne pas modifier le moteur v1.5 ni ses fichiers protégés sans raison explicite. Lire `references/SETTLERS3_PREGEN_READ_FIRST.md` avant toute modification génération/format.

## Prochaine RC/STABLE — après v1.10

La v1.8 reste une série de checkpoints DEV : aucune Release ne sera publiée
tant que la génération réelle et la diversité morphologique ne sont pas
corrigées en v1.10. Les tâches ci-dessous sont conservées pour la prochaine
RC, quel que soit son numéro final.

- [ ] Geler les nouvelles fonctionnalités ; corrections, polish, optimisation et documentation restent autorisés.
- [ ] Produire deux artefacts séparés : ZIP sources/Python et ZIP Windows x64 portable `onedir`, sans installateur.
- [ ] Revalider chemins de ressources, exports près de l’exécutable et settings sous `%APPDATA%/Settlers3MapGen`.
- [ ] Finaliser l’icône seulement à partir du pixel art fourni manuellement par le propriétaire ; aucune image IA.
- [ ] Updater v2 : version locale/dernière STABLE, téléchargement, SHA-256, préservation des settings, remplacement propre et rollback.
- [ ] Tester installation propre, mise à jour, absence réseau, téléchargement interrompu, mauvais checksum, rollback et conservation des préférences.
- [ ] Mettre à jour README, notes, manifests, validation et snapshot avant promotion.

## v1.9 — Restructuration interne, puis Data Mapping

### DEV_1 / Restructuration — validées et reste technique

- [x] Imports EDM, architecture, séparation des modes, validations, déterminisme, batch, UI et publication consolidés ; le détail historique est dans `CHANGELOG.md` et `references/dev_notes/V1_8_DEVELOPMENT_LOG.md`.
- [ ] Remplacer progressivement les assertions GUI fondées sur le texte source
  par des contrats comportementaux ou de widgets ; commencer par Batch et
  Historique, qui concentrent la majorité de ces caractérisations.
- [x] Simplifier la chaîne des fenêtres et le runtime : une fondation Tk nommée, un `MainWindow` composé et un seul point de construction du générateur dans `runtime.App`.
- [x] À la clôture de la restructuration, auditer le coût de contexte : raccourcir
  les instructions projet, supprimer les doublons/états obsolètes et router
  chaque tâche vers les seules références nécessaires.
- [ ] Procéder par extractions mécaniques courtes, avec comportement inchangé, tests ciblés puis validation complète à chaque DEV terminée.
- [ ] Intégrer les apports d’autres LLM comme hypothèses traçables et non comme vérité de référence.
- [ ] Auditer toutes les références après publication de DEV_2 : conserver les
  références spécialisées importantes, compacter les répétitions, puis
  fusionner/renommer/supprimer uniquement avec preuve d’obsolescence et liens
  entrants migrés.

### Data Mapping — fin de v1.9

- [ ] Déterminer les bornes réellement valides des Terrain IDs et Object IDs ; `0–255` reste une grille technique, pas une borne démontrée.
- [x] Compléter la première passe des objets contrôlés : souches `208–214`, pousses
  stade 2 `216–222`, pousses stade 1 `224–230`, panneaux `232–242`, arbres en
  feu `243–246`, nids `247–253` et marqueurs `254–255` sont catalogués. Les
  probes `215`, `223` et `231` sont documentées comme crash-prone et restent
  hors nomenclature sémantique.
- [x] Abandonner la cartographie large `128–207` : la zone mélange des éléments
  de placement/éditeur et des probes qui crashent ; aucune nouvelle campagne
  n'est planifiée sur cette plage.
- [x] Consolider le catalogue confirmé dans les statistiques, exports,
  tooltips, inspecteur et le graphique **Arbres et pousses** : adultes, pousses
  stade 2, pousses stade 1, plantations et palmiers adultes ; les pousses de
  palmier `221/229` restent incluses dans leurs stades respectifs.
- [ ] Compléter `SETTLERS3_TERRAIN_IDS_REFERENCE.md` et
  `SETTLERS3_OBJECT_IDS_REFERENCE.md` sans inventer les inconnus.
- [ ] Clarifier trous/réservés, transitions et catégories SAV : settlers, marchandises, outils, ressources transformées, bâtiments, armes, etc.
- [x] Consolider les tables utilisées par Statistiques, Graphiques, tooltips et inspecteur.
- [ ] Vérifier si EDM/MAP/SAV expose l’identité ou la couleur effective des joueurs ; utiliser l’information seulement si elle est démontrée. La palette de slot du viewer est affichée séparément ; aucun champ SAV de couleur effective n’est encore prouvé.
- [ ] Cartographier les informations joueurs indépendantes de la carte dans les SAV :
  couleur effective, niveau de mana (courant et maximum si disponibles), tribu,
  statut, nom/équipe, ressources de départ et autres champs démontrables ;
  rester en lecture ciblée, sans writer SAV.
  - [x] Bloc type 6 natif, drapeau actif, départs et offsets documentés ; code
    race/faction exposé comme candidat numérique.
  - [x] Décoder directement le masque initial complet du SAV immédiat : type-3
    byte 8, coordonnées copiées cellule par cellule ; ne jamais le reconstruire
    à partir des coordonnées de départ. La signature confirmée est
    `3500/3500/4000/4000` pour le triplet 4P fourni.
  - [ ] Décoder couleur effective, mana courant/maximum, tribu nominale,
    nom/équipe et ressources de départ sur un corpus contrôlé.
- [x] Valider les Terrain IDs 18/19 comme détails d’herbe : blobs d’une cellule
  entourés exclusivement d’herbe ID16 ; ils sont intégrés à la famille `Herbe`,
  aux statistiques, au graphique et à l’inspecteur.
- [x] Reporter les objets `82` et `83` à **Datamining v2** : aucune occurrence
  naturelle n’a été trouvée dans le corpus actuel, et la carte qui les injecte
  volontairement ne constitue pas une preuve.
- [x] Brancher les nids `247–253` sur les surfaces Agriculture/Cultures et leurs
  tooltips ; la teinte miel est distincte du blé et les nids restent absents du
  graphique forestier.

## v2.0 DEV_1_R10 — affinage du générateur Legacy

- [x] Poser un premier pipeline Continental Legacy réellement procédural,
  modulaire et sans lecture runtime du corpus natif.
- [x] Brancher la génération Legacy dans l’application pour les sept tailles
  natives et réparer le contrat de progression simple/Batch.
- [x] Ajouter le pipeline par étapes séparées : eau/continent, starts,
  montagnes-neige, lacs-rivières, marais, autres terrains, objets de
  ressources, décorations, poissons-minerais et validations.
- [x] Faire respecter à chaque étape terrain son masque d'occupation et ses
  transitions légales : aucune nouvelle zone ne doit recouvrir une autre
  famille, créer un trou ou produire un contour invalide.
- [x] Ne pas découper les familles autour des starts : seul le footprint exact
  est protégé, sans halo hexagonal visible.
- [x] Renforcer le détail des côtes et la sinuosité des rivières sans relâcher
  les invariants de connexion et de bordure d'eau.
- [x] Ajouter une passe bathymétrique dédiée après les lacs et avant les rivières : résidus Water0..7 calibrés sur les 16 SAV, rive Shore48 intacte, validations dures contre Eau→Herbe / Eau→terrain sans rive.
- [x] Borner le coût des placements et découpler la génération simple du thread Tk afin qu'une carte 768 ne rende plus la fenêtre « Ne répond pas ».
- [ ] Affiner les six axes visuels Legacy à partir de comparaisons PNG déterministes avec les cartes du jeu.
- [ ] Créer le dérivé Upgraded seulement après validation visuelle suffisante du
  Legacy ; ne pas mélanger ses règles au générateur actuel.
- [ ] Ajouter modificateurs et autres archétypes seulement après ce socle.
- [ ] Concevoir puis implémenter le mode **Custom laboratoire** dans une passe séparée : catalogue complet, presets exportables, batch et garde-fous, sans le mélanger au preset Legacy.

## v2.0 — audit exhaustif Legacy, amélioration, puis Custom

> Nouveau périmètre prioritaire : mesurer d’abord le Legacy natif, consigner les résultats, puis corriger et revalider son générateur. Le Custom ne commence qu’après cette stabilisation. Le corpus actuel est constitué des 21 SAV natifs disponibles, avec Legacy et Upgraded strictement séparés.

> Les côtes et la forme macro restent à affiner plus tard : elles sont assez proches pour que l’analyse détaillée des terrains, joueurs et ressources soit maintenant prioritaire.

### Séquence obligatoire

- [x] **0 — Corpus et méthode, première tranche** : inventorier et hasher les 16 SAV natifs 768×768 fournis (8×2P, 8×20P), avec extraction reproductible en lecture seule.
- [x] **1 — Tous les terrains, première tranche** : relever par ID/famille les cellules, composantes, tailles, surfaces, bounding boxes, formes/aspects, trous/singletons et densités des 16 SAV ; l’extension aux autres tailles reste ouverte.
- [x] **1bis — Placement et transitions, première tranche** : mesurer bord/intérieur, voisinages et terrains supports observés, avec topologie HEX6 et séparation du runtime 28.
- [x] **2 — Joueurs, première tranche** : mesurer les 176 départs, distances, footprint, masque initial/territoire et buffers techniques des 16 SAV ; les champs joueurs opaques restent à décoder.
- [x] **3 — Ressources Legacy et proximité des objets, première tranche** : analyser minerais/poissons (IDs, cellules, stocks, composantes, quantités, densités et distances aux starts) et mesurer les objets statiques/runtime proches des départs, sans conclure sur les hitbox non décodées.
- [ ] **3bis — Objets, plus tard** : reprendre ensuite l’audit exhaustif des objets (dont 82/83) : quantités, regroupements, espacements, terrains supports, positions et interactions ; aucune conclusion objet ne doit être anticipée ici.
- [ ] **Extension du corpus** : répéter les audits terrains/joueurs/ressources sur les SAV natifs des autres tailles avant de figer des profils multi-size.
- [x] **4 — Règles et ordre** : comparer les observations au pipeline R6 (occupation, transitions, hydrologie, relief, rives/profondeurs, starts et ressources), classer chaque règle comme native, calibrée, approximée ou inconnue, puis décider les changements avec preuves. Audit : `references/SETTLERS3_LEGACY_PIPELINE_AUDIT_v1.md`.
  - [x] Confirmer la chaîne dure Eau → Shore48 → Water0..7 → terrain, les chaînes de familles HEX6 et la connexion des rivières.
  - [x] Résoudre le conflit d'ordre : conserver les starts précoces validés par le projet ; ne pas déduire un ordre natif exact à partir des seuls SAV finaux.
  - [x] Isoler les écarts actionnables : Shore48 sous-produite, quotas/supports Legacy des ressources divergents, décorations absentes, routage des rivières sous la cible.
- [x] **5 — Références durables** : conserver mesures et échantillons dans des références versionnées (Markdown + CSV/JSON/NPZ si utile), avec SAV source, hash, seed, version d’analyse, profils et limites du corpus.
  - [x] Première tranche ressources/objets enregistrée dans `references/native_resource_object_audit/`, avec synthèse `SETTLERS3_NATIVE_RESOURCES_OBJECT_PROXIMITY_REFERENCE_v1.md`.
  - [x] Audit du pipeline R6 et mesures de contrôle documentés dans `SETTLERS3_LEGACY_PIPELINE_AUDIT_v1.md`.
- [x] **5bis — Architecture avant R11** : maintenir `generation/archetypes/`
  et `generation/generators/` comme deux branches sœurs ; ne pas dupliquer les
  archétypes dans les moteurs ; conserver l’API publique et le comportement
  Legacy pendant la migration. Le moteur actif est regroupé sous
  `generation/generators/legacy/`. La migration ultérieure de la compatibilité
  v1.5 fera l’objet d’une passe séparée et testée. Imports, compilation, smoke
  v1.5, générations Legacy 768 2P/20P et packaging sont validés ; `pytest`
  reste à exécuter dans un environnement qui le fournit.
- [ ] **6 — Amélioration Legacy** : transformer les mesures validées en paramètres/profils par taille, joueurs et famille, puis générer une matrice multi-seeds et comparer sorties/statistiques/PNG déterministes aux SAV natifs.
  - [ ] Reprendre la première tranche R8 : R7 est rejetée. Ne créer aucun
    rayon d’exclusion de ressources autour des starts ; poisson Legacy sur
    toute l’eau valide, et règles côtières réservées à Upgraded.
  - [x] Remplacer le modèle R9 de champs exclusifs par des hexagones de
    minerais séquentiels : charbon → fer → or → gemmes → soufre, avec
    écrasement inter-familles et taux de remplissage dépendant de la taille.
  - [x] R12 : remplacer les rayons issus directement des tailles groupées par
    une palette discrète 3/4/5, construire les grandes poches avec des
    hexagones élémentaires proches, élargir la variation de remplissage et
    vérifier les shortfalls sur 768 2P/20P.
  - [x] R13 : remplacer le tirage uniforme des cellules par une sélection
    radiale HEX bruitée, réintroduire une variation contrôlée des tailles de
    poches et calibrer la compacité sur le soufre final des SAV ; totaux,
    rayons 3/4/5, ordre de pose et séparation Upgraded conservés.
  - [x] R14 : réduire le biais radial de R13 jusqu'à une sélection interne
    quasi aléatoire, en conservant seulement une très légère cohérence locale.
  - [x] R15 : remplacer l'aléatoire indépendant de R14 par une corrélation
    spatiale HEX6 légère et fixer l'ancrage des poches pour éviter les traînées.
  - [x] R16 : tester la méthode directe demandée : support montagneux intérieur,
    occupation ~53 %, zones HEX6 indépendantes, rayons 3/4/5, remplissage
    uniforme entre minimum provisoire et 100 %, pixels aléatoires et ordre
    charbon → fer → or → gemmes → souffre avec écrasement.
  - [x] R17 : conserver la géométrie R16 et corriger uniquement les quantités
    Legacy vers un tirage uniforme natif `1..15` pour minerais et poissons ;
    confirmer que la composition charbon/fer/or/gemmes/soufre reste proche des
    proportions natives.
  - [x] **Clôture DEV_1** : les générations Legacy minerais + poissons sont
    validées par l'utilisateur ; le checkpoint est prêt à être promu sur
    `dev` sous le nom officiel `v2.0 DEV_1`.
  - [ ] Comparer R17 à plusieurs SAV/PNG dans l'éditeur et le jeu ; mesurer si
    le tirage uniforme interne recrée assez de noyaux connectés ou s'il faut
    seulement une très légère cohérence dans les pixels d'une zone.
  - [ ] Poursuivre séparément avec Shore48, rivières et décorations : ne pas
    confondre ces passes avec le calibrage de ressources.
- [ ] **7 — Validation Legacy** : revalider progressivement terrains, transitions, joueurs, ressources puis macro-forme/côtes dans l’éditeur/jeu ; ajouter les tests de non-régression, de déterminisme, de couverture et d’absence de crash avant tout nouveau mode.
- [ ] **8 — Custom complet** : seulement après validation Legacy, exposer dans un chemin séparé un catalogue très complet : macro-forme/eau/côtes, terrains et transitions, starts, relief/hydrologie, ressources Legacy, objets ultérieurs, quotas, seed, taille/joueurs, contraintes, presets import/export, diagnostics et batch.

### Garde-fous

- [ ] Respecter la chaîne de transition mesurée et validée (notamment eau → plage/rive → herbe), la topologie HEX6, les règles hydrologiques et l’interdiction des transitions graphiquement invalides.
- [ ] Ne jamais mélanger les règles Upgraded (notamment ses règles de ressources/no-gap) avec le chemin Legacy ; chaque mode garde ses références, profils et tests.
- [x] Maintenir le footprint natif des starts et leur protection sans halo visible ; l'ordre start-first du projet est conservé, tandis que l'ordre interne natif reste explicitement inconnu.
- [x] Séparer le décor initial byte 14 du champ objet runtime byte 7 ; ne pas interpréter le byte 9 SAV comme une accessibilité tant que sa sémantique n’est pas démontrée.
- [ ] Ne produire aucune référence visuelle imaginaire : toute comparaison doit venir d’un SAV/EDM/MAP réel ou d’une génération déterministe identifiée.

## Analyse et UI futures

- [ ] Rafraîchir immédiatement le rapport texte Statistiques lors d’un changement de langue.
- [ ] Ajouter un tri d’inventaire debug par quantité / ID / nom et l’affichage optionnel des IDs connus absents.
- [ ] Étendre les inventaires aux nouvelles familles runtime seulement après mapping confirmé.
- [ ] Enrichir les distributions de composants : massifs, lacs, rivières et clusters.
- [ ] Étudier histogrammes, profils radiaux/cumulatifs, variantes donut et références corpus ; radar seulement s’il reste non trompeur.
- [ ] Garder exactement **deux rayons** configurables pour les ressources proches, jamais trois dans l’UI actuelle.
- [ ] Revoir netteté/résolution des exports PNG de carte et de graphiques.
- [ ] Repenser éventuellement la Vue Hauteurs en carte topographique/classes d’altitude.
- [ ] Concevoir les vues composables : compatibilités, ordre de rendu, légendes et conflits avant implémentation.
- [ ] Concevoir le **Pilotage de la vue** depuis les Graphiques, optionnel et désactivable, avec restauration de l’état précédent.
- [ ] Repenser légèrement Comparaison et la signalétique Chargée/Affichée/Affectée sans dépendre uniquement de la couleur.
- [ ] Comparaison A/B avancée côte-à-côte/diff seulement si l’usage le justifie.
- [ ] Comparaison multi-cartes 3+ planifiée après une grosse passe générateur : viewer scindable en 2/3/4 zones.
- [ ] Label J1–J20 de la Vue Départs : conception dédiée pour ancrage, position et collisions.
- [ ] Loupe locale et informations d’inspecteur près du curseur, avec toggles indépendants.
- [ ] Responsive UI v2, Status/Feedback v2 et audit global des états interactifs lors d’une future refonte.
- [ ] Centres d’export : si le contenu grandit, ajouter contrainte écran et scroll de secours.
- [ ] Surveiller l’incident Statistiques exceptionnellement long ; profiler uniquement avec reproduction complète.
- [ ] Diagnostic mémoire possible v1.11 : mesures NumPy/Pillow factuelles, estimations Python/Tk explicites et déduplication par identité.
- [ ] Tester le calcul raster en arrière-plan uniquement si les optimisations simples deviennent insuffisantes ; Tk reste sur le thread principal.

## Personnalisation et communauté — plus tard

- [ ] Relecture humaine DE/ES ; FR/EN restent les langues de référence jusqu’à validation compétente.
- [ ] Packs de langue déclaratifs versionnés, sans code exécutable, héritage/repli et validation stricte des variables `{...}`.
- [ ] Écosystème de thèmes déclaratifs fondé sur des rôles sémantiques et sans duplication widget par widget.
- [ ] Étendre éventuellement les commandes rebindables après retour d’usage.
- [ ] Passe d’iconographie UI déterministe et validée manuellement.
- [ ] Pixel art fait main pour l’application/exécutable et éventuelle modernisation des marqueurs J1–J20.
- [ ] Maintenir `SETTLERS3_VISUAL_ASSET_PROVENANCE.md` avant chaque intégration visuelle externe.
- [ ] Couleurs A/B personnalisables seulement dans une passe UI dédiée.

## Après Continental

- [ ] **Large Islands / Grandes îles** : constituer et analyser les références natives nécessaires.
- [ ] **Small Islands / Petites îles** ensuite.
- [ ] Conserver l’idée d’un moteur expérimental réellement différent de Legacy/Upgraded, mais seulement après l’audit v1.10.
- [ ] Ne pas confondre Mode, Archetype et Modifier.
- [ ] **Modifiers** : variations contrôlées et parfois fortes, particulièrement utiles avec Batch et comparaison multi-cartes.
- [ ] Ne pas réserver `v2.0` au simple multi-size ; attendre une évolution structurelle réelle.

## ENDGAME — éditeur intégré

- [ ] Attendre que le générateur/workbench soit pratiquement finalisé.
- [ ] Permettre à terme de générer, importer, inspecter, modifier, valider et exporter.
- [ ] Dépasser l’éditeur officiel seulement pour les données EDM/MAP/SAV réellement comprises et validées.
- [ ] Décider tardivement entre fenêtre dédiée et mode/ espace Édition complet.
- [ ] Ne créer maintenant ni placeholder, ni refonte anticipée, ni numéro de version artificiel.

## Invariants à préserver

- Archetype = macro-géographie ; Legacy/Upgraded = contenu, règles, balance, ressources et objets.
- Starts placés tôt et protégés.
- Minerais Upgraded v7 no-gap.
- Aucun aperçu ou asset imaginaire ; toute carte montrée provient de données réelles générées/importées.
- SAV jamais réinventé : lecture ciblée et copie source inchangée seulement.
- IDs inconnus explicitement inconnus.
- Ne jamais repartir d’une version invalidée du générateur.
