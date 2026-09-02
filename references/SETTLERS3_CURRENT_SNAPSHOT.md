# Settlers III MapGen — CURRENT SNAPSHOT

> **Point de reprise vivant — état actuel uniquement.**
>
> Dernière mise à jour : **2026-09-02 — v2.0 DEV_3 validé et poussé**

## 1. État immédiat

- Dépôt : `JulienP36/settlers3-mapgen` ; branche de travail : `dev`.
- Dernier checkpoint publié : **v2.0 DEV_3**, validé et poussé sur `dev`.
- DEV_3 conserve le socle Legacy natif de DEV_2 et valide la première passe
  Upgraded de calibration visuelle : `34 = Patch d’herbe rocheuse` dans
  Montagne, segment et couleur dédiés dans les graphes, couleur cohérente dans
  la carte, et blobs miniers compensés pour la projection parallélogramme.
- DEV_2 retire complètement l'ancien chemin Legacy v1.5 et le générateur
  Legacy procédural DEV_1, avec leurs profils, helpers, tests spécifiques et
  bibliothèques de silhouettes. Le mode Legacy public est maintenant relié au
  nouveau moteur natif v1 ; l'ancien chemin ne doit pas réapparaître.
- L'audit non-terrain du binaire est maintenant approfondi et archivé
  dans `references/S3_EXE_STATIC_NON_TERRAIN_AUDIT_20260901.md`, avec une
  transcription comportementale progressive dans
  `references/S3_EXE_NON_TERRAIN_RECONSTRUCTION_20260901.cpp`. Elle couvre le
  flot nouvelle carte/carte chargée, la séparation des couches runtime, le
  filtre des starts, la banque exacte d'offsets, le layout du registre type 9,
  le catalogue paramétrique des objets statiques et le writer
  `GameDataSave::Save` des principaux records SAV. La convention d'appel du
  noyau et la réinitialisation du PRNG avant les couches de partie sont
  également confirmées. Le producteur du stock initial est relié à
  `0x506CF0 -> 0x5046B0 -> 0x504420`; seuls les noms métier, la source externe
  type 9 et le writer EDM/MAP exact restent ouverts.
- Les deux moteurs restent isolés : **Legacy Continental natif v1** accepte
  `256, 320, 384, 448, 512, 576, 640, 704, 768, 832, 896, 960 et 1024` ;
  **Upgraded Continental** reste calibré en 768×768 avec son profil, ses
  règles, ses validations et ses références.
- La comparaison des minerais a été archivée avant suppression dans
  `references/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md` : le mix familial
  de DEV_1 était proche du corpus natif, mais la géométrie des gisements était
  trop fragmentée ; aucune de ses heuristiques n'est reconduite.
- L'implémentation sépare l'archétype Continental (contexte macro-forme) du
  générateur Legacy natif (relief, terrains, hydrologie, ressources, objets,
  départs et validations), conformément à l'audit décompilé.
- Le Legacy natif expose les miroirs Axe long, Axe court et Les deux. Les
  avertissements de viabilité pour les tailles sous 384 et au-dessus de 768
  passent par la zone de feedback ; le seed `297650040` en 256×256 ne reste
  plus bloqué dans la sculpture du relief. La bordure extérieure est normalisée
  en Water7 plutôt qu'en Water1.
- Le gate Windows protège désormais cinq éléments du chemin Upgraded : les
  trois modules Python de génération conservés, le profil Upgraded et la
  bibliothèque statique native. Les hashes canoniques sont dans
  `PROJECT_WORKFLOW.md`.

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
- L'audit natif du générateur reste la source de vérité ; les documents de
  reverse-engineering distinguent le contrat démontré des résidus de format et
  de nomenclature qui devront être validés sur des sorties du jeu.
- L'audit non-terrain confirme que le byte ressource de l'Area, le byte objet
  statique, les ressources type 9 et les entités runtime sont des couches
  distinctes. Les producteurs initiaux `0x51AD40`, `0x518A08`, `0x51B010` et
  `0x51B1A0`, le loader/producteur `0x504420` et la sérialisation SAV
  `0x509995` sont reliés ; les règles non démontrées restent explicitement
  interdites.
- La compatibilité Upgraded 768×768 et sa géométrie v7 no-gap restent le socle
  exécutable conservé. Les anciens fichiers Legacy supprimés sont historiques
  dans Git, mais ne font plus partie du runtime natif actif.
- La forme minérale DEV_3 utilise la métrique linéaire de la projection
  parallélogramme (`X=2x-y`, `Y=2y`) afin de réduire l’étirement visuel sans
  modifier la topologie HEX6, les quotas, les quantités ni la règle no-gap.
- Le terrain ID34 est documenté et localisé comme **Patch d’herbe rocheuse** /
  **Rocky grass patch** ; il est compté dans Montagne et reste distingué des
  autres IDs dans l’inspecteur et le graphique.
- La comparaison minière conservée est une mesure de proximité, pas une règle
  de génération : les volumes étaient proches, les formes ne l'étaient pas.
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

- La génération active expose maintenant les chemins Legacy Continental natif
  et Upgraded Continental 768×768. Les modificateurs et les autres archétypes
  restent ultérieurs. L’export EDM/MAP est disponible sur toutes les tailles
  du contrat via le scaffold 768, mais les tailles hors 768 restent des
  candidates de test à valider dans l’éditeur communautaire/jeu.
- Le checkpoint DEV_3 est validé sur les contrôles source, smoke, graphiques
  FR/EN/DE/ES, self-test runtime et archive extraite. La validation visuelle
  utilisateur confirme les deux ajouts de cette passe.
- L'extension des audits aux autres tailles reste ouverte. L'audit exhaustif
  des objets, dont `82/83`, reste reporté.
- Les écarts de formes Legacy DEV_1 sont volontairement abandonnés ; il ne faut
  pas les corriger par petites touches avant d'avoir porté l'algorithme natif.
- SAV : le writer natif a été localisé et documenté statiquement, mais notre
  application ne l'implémente toujours pas ; lecture ciblée et copie inchangée
  restent les seules opérations applicatives autorisées.

## 5. Suite de la roadmap

- **Résidus d'audit** : décoder plus tard la couverture complète des tables,
  les noms métier, la source externe type 9 et le writer EDM/MAP ; aucun de ces
  points ne doit être remplacé par une hypothèse.
- **Implémentation** : le générateur Legacy natif et l’archétype Continental v1
  sont séparés dans le dépôt ; le moteur Upgraded possède sa copie indépendante
  et sa calibration DEV_3 validée. Le prochain chantier fonctionnel est la
  passe dédiée du positionnement des starts, bonus et objets de départ.
- **Validation externe** : rejouer la suite pytest dans l'environnement
  équipé, exécuter le smoke-test moteur et valider l'archive Windows, les
  exports étendus et le comportement en jeu.
- **Après la passe starts/bonus/objets** : dérivés Large Islands puis Small
  Islands ; le Custom et l’éditeur intégré restent ultérieurs.
- Aucune RC, Release ou promotion sur `main` avant validation Windows/jeu du
  nouveau Legacy. `main` reste réservé à la STABLE.

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
