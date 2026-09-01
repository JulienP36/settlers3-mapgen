# Settlers III MapGen — CURRENT SNAPSHOT

> **Point de reprise vivant — état actuel uniquement.**
>
> Dernière mise à jour : **2026-09-01 — v2.0 DEV_2, reset du générateur Legacy**

## 1. État immédiat

- Dépôt : `JulienP36/settlers3-mapgen` ; branche de travail : `dev`.
- Dernier checkpoint publié : **v2.0 DEV_1**, validé et poussé sur `dev`. Le
  travail local courant prépare **v2.0 DEV_2** ; il n'est pas encore poussé.
- DEV_2 retire complètement l'ancien chemin Legacy v1.5 et le générateur
  Legacy procédural DEV_1, avec leurs profils, helpers, tests spécifiques et
  bibliothèques de silhouettes. Le mode Legacy reste réservé dans l'API, mais
  ne génère plus de carte pendant la reconstruction native.
- L'audit non-terrain du binaire est maintenant approfondi et archivé
  dans `references/S3_EXE_STATIC_NON_TERRAIN_AUDIT_20260901.md`, avec une
  transcription comportementale progressive dans
  `references/S3_EXE_NON_TERRAIN_RECONSTRUCTION_20260901.cpp`. Elle couvre le
  flot Area -> bâtiments -> colons/départs -> ressources de départ ->
  métadonnées, la séparation des couches runtime, le filtre des starts, le
  layout du registre type 9, le catalogue paramétrique des objets statiques et
  le writer `GameDataSave::Save` des principaux records SAV. La convention
  d'appel du noyau et la réinitialisation du PRNG avant les couches de partie
  sont également confirmées ; les sous-records SAV type 2 sont séparés du
  futur writer EDM/MAP. Le producteur aléatoire type 9, le catalogue métier
  complet et le writer EDM/MAP exact restent ouverts.
- Le seul moteur de génération conservé est **Upgraded Continental 768×768**.
  Son profil, ses règles, ses validations et ses références restent isolés.
- La comparaison des minerais a été archivée avant suppression dans
  `references/SETTLERS3_LEGACY_MINERAL_COMPARISON_DEV2.md` : le mix familial
  de DEV_1 était proche du corpus natif, mais la géométrie des gisements était
  trop fragmentée ; aucune de ses heuristiques n'est reconduite.
- La prochaine implémentation devra séparer l'archétype Continental (macro-
  forme) du générateur Legacy natif (relief, terrains, hydrologie, ressources,
  objets, départs et validations), conformément à l'audit décompilé.
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
  reverse-engineering décrivent encore des branches partielles et ne valent
  pas implémentation tant qu'elles ne sont pas validées sur des sorties du jeu.
- L'audit non-terrain confirme que le byte ressource de l'Area, le byte objet
  statique, les ressources type 9 et les entités runtime sont des couches
  distinctes. Les producteurs initiaux `0x51AD40`, `0x518A08`, `0x51B010` et
  `0x51B1A0`, le loader `0x504420` et la sérialisation SAV `0x509995` sont
  reliés ; les règles non démontrées restent explicitement interdites.
- La compatibilité Upgraded 768×768 et sa géométrie v7 no-gap restent le socle
  exécutable conservé. Les anciens fichiers Legacy supprimés sont historiques
  dans Git, mais ne font plus partie du runtime ni de l'archive source.
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

- La génération active est calibrée sur Upgraded Continental 768×768. Le
  Legacy natif, les modificateurs, les autres archétypes et le mode Custom
  attendent la reconstruction et la validation de leur socle respectif.
- L'extension des audits aux autres tailles reste ouverte. L'audit exhaustif
  des objets, dont `82/83`, reste reporté.
- Les écarts de formes Legacy DEV_1 sont volontairement abandonnés ; il ne faut
  pas les corriger par petites touches avant d'avoir porté l'algorithme natif.
- SAV : le writer natif a été localisé et documenté statiquement, mais notre
  application ne l'implémente toujours pas ; lecture ciblée et copie inchangée
  restent les seules opérations applicatives autorisées.

## 5. Suite de la roadmap

- **Audit natif** : poursuivre la partie non-terrain restante : remonter le
  producteur type 9, décoder les tables d'empreintes/offsets et identifier le
  writer EDM/MAP ; ne pas implémenter sur la seule base d'une analogie SAV.
- **Implémentation** : construire le générateur Legacy natif séparément de
  l'archétype Continental v1, puis ajouter starts, ressources, objets,
  validations et export à partir des mesures confirmées.
- **Validation** : rejouer la suite pytest dans l'environnement équipé,
  exécuter le smoke-test moteur et valider l'archive Windows sous Windows.
- **Après Continental** : dérivés Large Islands puis Small Islands ; le Custom
  et l'éditeur intégré restent ultérieurs.
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
