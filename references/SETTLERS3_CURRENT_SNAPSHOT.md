# Settlers III MapGen — CURRENT SNAPSHOT

> **Point de reprise vivant — état actuel uniquement.**
>
> Dernière mise à jour : **2026-08-31 — v2.0 DEV_1 validée, quantités Legacy natives**

## 1. État immédiat

- Dépôt : `JulienP36/settlers3-mapgen` ; branche de travail : `dev`.
- Dernier checkpoint validé : **v2.0 DEV_1**, validé le 31 août 2026 et
  promu sur `dev`. Il consolide les passes Legacy R10 à R17, dont la
  génération des minerais et poissons. Les validations Windows, éditeur et
  jeu restent à faire.
- Le générateur actif est **Continental Legacy v2**. Il est procédural,
  indépendant du corpus natif à l'exécution et ne lit ni SAV, PNG, NPZ, cache
  ni carte précédente. Ses entrées sont uniquement `side`, `players`, `seed`.
- Le pipeline publié suit l'ordre `eau → continent → starts →
  montagnes/neige → lacs/rivières → marais → autres terrains → objets de
  ressources → décorations → poissons/minerais → validators`.
- R7 est rejetée : pas d'exclusion économique autour des starts et pas de
  filtre côtier pour les poissons Legacy. Les poissons occupent toute l'eau
  valide hors rivières. Les rivières sont encore à recalibrer vers des
  systèmes plus courts, nombreux et côtiers.
- R17 conserve la géométrie minérale R16 : zones HEX6 indépendantes, rayons
  3/4/5, remplissage variable, occupation du support montagneux intérieur et
  écrasement séquentiel charbon → fer → or → gemmes → soufre. Les quantités
  Legacy sont tirées uniformément dans `1..15`.
- Les transitions Eau → Shore48 → Water0..7 → terrain, les chaînes HEX6, les
  footprints de départ et l'interdiction des étangs de 1 à 4 cellules restent
  des invariants durs. La structure minérale et les écarts Shore48/rivières/
  décorations doivent encore être vérifiés visuellement dans le jeu.
- La réorganisation interne est validée : `generation/archetypes/` et
  `generation/generators/` sont deux branches sœurs ; le moteur actif vit sous
  `generation/generators/legacy/`, avec l'API publique conservée.
- Le gate Windows v1.5 vérifie désormais cinq fichiers de référence. Le
  `validated.py` historique est la façade du Legacy v2 depuis DEV_1 et reste
  hors de cette baseline ; toute modification de cette façade doit rester
  explicitement liée au moteur.

## 2. Audits natifs et socle à préserver

- Première tranche v2.0 : 16 SAV natifs 768×768 (8×2P, 8×20P) analysés pour
  terrains, composantes, relief, transitions HEX6, starts, distances,
  footprints, masque type-3 byte 8, minerais, poissons et objets proches des
  starts. Les références reproductibles sont dans `references/`.
- Le bloc type 6, les départs, le masque initial direct et le candidat
  race/faction sont documentés. Le byte 14 est séparé du byte 7 runtime ; le
  byte 9 SAV reste inconnu et n'est pas traité comme une hitbox.
- Les objets `208–214`, `216–222`, `224–230` et `232–255` sont catalogués ;
  `215/223/231` restent crash-prone. Les objets `82/83` sont reportés à
  Datamining v2 faute d'occurrence naturelle démontrée.
- Les terrains `18/19` sont des détails d'herbe singleton entourés d'herbe
  ID16. Les nids `247–253` appartiennent à Agriculture/Cultures, avec une
  teinte miel distincte et sans présence dans le graphe forestier.
- Le moteur de référence historique est v1.5, Continental 768×768. Legacy et
  Upgraded restent séparés ; la géométrie Upgraded v7 no-gap est verrouillée.
- Le moteur v1.5 et les cinq fichiers suivants restent protégés :
  `s3mapgen/generation/base.py`, `s3mapgen/generation/continental.py`,
  `config/legacy_768_v1.json`, `config/upgraded_768_v1.json` et
  `data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz`. Leurs hashes canoniques
  sont ceux de `PROJECT_WORKFLOW.md` et doivent être revérifiés après tout
  travail significatif.
- Aucun asset visuel généré par IA n'est autorisé. Les aperçus doivent rester
  des rendus déterministes de données EDM/MAP/SAV réelles.

## 3. Fonctionnalités applicatives validées

- Les DEV v1.8 ont validé le workflow, le responsive, Batch, l'historique,
  les vues Départs/Territoires, les exports, les langues FR/EN/DE/ES, les
  protections `V/A/B/M`, les raccourcis, la capacité dure et le self-test du
  paquet Windows. Le détail historique appartient à
  `references/dev_notes/V1_8_DEVELOPMENT_LOG.md` et au `CHANGELOG.md`.
- `V`, `A`, `B` et `M` protègent les sorties contre l'éviction ordinaire.
  L'affichage automatique d'un résultat de génération déplace `V` ; cette
  exception est documentée et acceptée.

## 4. Problèmes connus et reports

- La génération est calibrée principalement sur Continental 768×768. Le
  dérivé Upgraded, les modificateurs, les autres archétypes et le mode Custom
  attendent la stabilisation du Legacy.
- L'extension des audits aux autres tailles reste ouverte. L'audit exhaustif
  des objets, dont `82/83`, reste reporté.
- Le rapport du point 4 confirme les garde-fous de transitions et l'architecture
  start-first, mais classe Shore48 sous-produite, rivières sous la cible,
  décorations absentes et validation visuelle des ressources comme écarts
  prioritaires.
- SAV : lecture ciblée et copie inchangée uniquement ; aucun writer SAV.

## 5. Suite de la roadmap

- **Amélioration Legacy** : comparer DEV_1 à plusieurs SAV/PNG déterministes
  dans l'éditeur et le jeu, puis mesurer séparément Shore48, rivières,
  décorations et ressources avant toute nouvelle règle.
- **Validation** : rejouer la suite pytest dans l'environnement équipé,
  exécuter le smoke-test moteur et valider l'archive Windows sous Windows.
- **Après Continental** : dérivés Large Islands puis Small Islands ; le Custom
  et l'éditeur intégré restent ultérieurs.
- Aucune RC, Release ou promotion sur `main` avant validation Windows/jeu du
  Legacy v2. `main` reste réservé à la STABLE.

## 6. Procédure de reprise

1. Lire `AGENTS.md`, `PROJECT_WORKFLOW.md`, ce snapshot et la section active de
   `TODO_MAPGEN.md`.
2. Vérifier l'état réel de `dev` et les hashes protégés avant toute modification
   sensible à la génération ou aux formats.
3. Lire `references/SETTLERS3_PREGEN_READ_FIRST.md` avant toute modification
   de génération, export ou données natives.
4. Lancer les tests ciblés pendant le travail, puis la suite complète avant un
   checkpoint ; conserver les candidates suffixées localement et ne publier
   sur `dev` qu'un DEV complet validé.
