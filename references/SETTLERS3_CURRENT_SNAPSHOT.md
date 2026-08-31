# Settlers III MapGen — CURRENT SNAPSHOT

> **Point de reprise vivant — état actuel uniquement.**
>
> Dernière mise à jour : **2026-08-31 — v2.0 DEV_1 validée, quantités Legacy natives**

## 1. État immédiat

- Dépôt : `JulienP36/settlers3-mapgen`.
- Branche de travail : `dev`.
- Dernier checkpoint validé : **v2.0 DEV_1**, validé par l'utilisateur le
  31 août 2026 et promu sur `dev`. Il consolide les passes Legacy R10 à R17,
  dont la génération des minerais et poissons ; les validations Windows,
  éditeur et jeu restent l'homologation externe à faire.
- Ligne active publiée : **v2.0 DEV_1**. Le chemin Continental Legacy procédural
  reste indépendant et ne lit ni corpus, NPZ, SAV, PNG, cache ni carte précédente
  à l'exécution. R7 est explicitement rejetée : l’exclusion économique `r≤25`
  des starts et le filtre côtier des poissons ne reproduisent pas le Legacy.
  R10 repart donc des composantes natives, sans réserve de ressources autour
  des starts ; les poissons Legacy occupent toute l’eau valide hors rivières.
  Les rivières sont en cours de recalibration vers des systèmes courts, plus
  nombreux et plus côtiers. R6 ajoutait une bathymétrie côtière dérivée des
  16 SAV fournis : la rive Shore48 reste intacte, seuls les IDs Water0..7
  varient localement ; les transitions Eau→Herbe / Eau→terrain sans rive sont des invariants durs. Les starts et footprints passent les contrôles ; les poissons Legacy restent sur toute l'eau valide, et R16 apporte une candidate directe pour les minerais.
- Réorganisation R10 validée localement : `generation/archetypes/` et
  `generation/generators/` sont désormais deux branches sœurs ; le moteur actif
  vit dans `generation/generators/legacy/` et l’API
  `s3mapgen.generation.archetypes` reste compatible. Aucun comportement de
  génération n’a été modifié ; la compatibilité v1.5 reste dans ses fichiers
  historiques jusqu’à une passe dédiée.
- Correctif R6 : contrôle des composants vectorisé sans relâcher la protection
  des départs ; génération simple hors du thread Tk. Les champs de bruit
  internes sont accélérés sans toucher à la macro-côte de référence. Le
  benchmark 768×768 exact passe de ~38–40 s à **13,2 s** (20P 14,4 s), hard
  checks OK.
- Points 1 et 2 de la v2.0 : première tranche de **16 SAV natifs 768×768**
  (8×2P, 8×20P) analysée pour les terrains, composantes, positions, relief,
  transitions HEX6, starts, distances, footprints et masque type-3 byte 8.
- Point 3 première tranche : minerais/poissons et objets proches des starts
  sont mesurés dans `references/native_resource_object_audit/`. Byte 14 est
  séparé du byte 7 runtime ; le byte 9 SAV reste inconnu et n'est pas traité
  comme une accessibilité/hitbox. R17 a modifié uniquement le profil quantitatif
  du générateur Legacy v2, puis cette correction a été validée dans DEV_1.
- Point 4 terminé : `references/SETTLERS3_LEGACY_PIPELINE_AUDIT_v1.md` compare
  l'ordre R6 aux références natives, confirme les garde-fous de transitions et
  classe les règles. Le pipeline reste start-first ; l'ordre interne natif est
  inconnu. Les écarts prioritaires restent Shore48 trop peu abondante, rivières
  sous la cible et décorations encore absentes ; la structure minérale R16/R17 reste
  à valider visuellement dans le jeu.
- Dernière STABLE : **v1.7**, publiée sur `main`, tag `v1.7`, commit de promotion `780bc5e`.
- Validations candidate R6 : 267 tests PASS, matrice des sept tailles natives
  jusqu'aux limites joueurs PASS, autodiagnostic runtime PASS, ZIP source
  déterministe PASS et aperçus 768 4P/20P avec validations dures PASS. Les
  essais Windows/éditeur/jeu restent à faire avant clôture de DEV_1. Les sondes
  intermédiaires R8/R9 restent historiques ; l’archive R10 restructurée est une
  candidate locale à vérifier sous Windows. La suite pytest devra être rejouée
  dans un environnement qui la fournit.
- Validation structurelle DEV_1 : la nouvelle passe minérale est bornée,
  sans shortfall sur les contrôles 768×768 2P/20P, et vise environ 53 % du
  support montagneux intérieur. Les rayons restent limités à 3/4/5 ; les
  quantités Legacy sont uniformes sur `1..15`, comme dans les SAV ;
  la suite `pytest` n’est pas installée dans l’environnement courant.
- Les candidates R1/R2 et le paquet `CAPTURE_ONLY` restent des artefacts locaux historiques. Aucune révision suffixée `R` n’est publiée ; la feuille de candidate roulante est retirée à la clôture.
- Réconciliation de branches terminée au commit `f56ee1a` : `dev` contient désormais `main` dans son ascendance sans modification de l’arbre DEV_11.
- **v1.9 DEV_1 validée** : les deux EDM fautifs chargent sous Windows ; la candidate R1 est consolidée sans suffixe et sa feuille roulante retirée.
- **v1.9 DEV_2 validée** : architecture `application/`, `generation/` et
  `map_data/` séparée par responsabilités ; `AGENTS.md` est l’entrée courte.
- La v1.9 est requalifiée : restructuration interne prioritaire ; Data Mapping ciblé est clôturé dans DEV_3.
- La v1.8 reste une série de checkpoints DEV sans RC ni Release ; aucune STABLE
  n’est prévue avant la reconstruction réelle du générateur, potentiellement v2.0.

## 2. Socle validé à préserver

### Génération

- Générateur actif : **Continental Legacy v2**, pipeline modulaire commun
  `eau → continent → starts → montagnes/neige → lacs/rivières → marais →
  autres terrains → objets de ressources → décorations → poissons/minerais →
  validators`.
- Chaque phase terrain écrit uniquement dans son masque de cellules encore
  compatibles ; elle ne recouvre pas une famille existante et ne crée pas de
  trou. Les objets et ressources restent après les passes de terrain ; le
  validateur final confirme les transitions avant export.
- Entrées runtime Legacy : uniquement `side`, `players`, `seed`.
- Le v1.5 reste une compatibilité historique et un corpus de calibration ; il
  n’est pas consulté durant une génération Legacy v2.

- Moteur de référence : **v1.5**, Continental 768×768.
- Référence : `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- Legacy et Upgraded restent séparés.
- Starts placés tôt, zones réservées protégées.
- Minerais Upgraded : géométrie **v7 no-gap** verrouillée.
- Snow uniquement via la famille Rocky ; aucun remplacement de montagne hors neige validée.
- Rivières HEX6 connectées, sans poisson ; étangs intérieurs de 1 à 4 cellules interdits.
- Building Stones 115..127 ; ID127 = épuisé, stock nul.
- ID84 affiché comme `Pousse d’arbre` / `Tree sapling`.

### Fichiers protégés

- `s3mapgen/generation/base.py` — `5d828abe18c8b84f9845221f588eb8e6583fad99955465ce940cc09ce914ee4b`
- `s3mapgen/generation/continental.py` — `57cb7ce7c45a05906ef60b2d9b1c4306fae40a26c60fa93cde2e481823976e86`
- `s3mapgen/generation/validated.py` — dispatcher modifié explicitement pour
  brancher le générateur Legacy v2 ; le hash v1.5 historique est conservé dans
  le journal de v1.9, pas comme contrainte du nouveau moteur.
- `config/legacy_768_v1.json` — `bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85`
- `config/upgraded_768_v1.json` — `11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441`
- `data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz` — `fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d`

Ne modifier aucun de ces fichiers sans raison explicite liée au moteur et lecture préalable de `SETTLERS3_PREGEN_READ_FIRST.md`.

## 3. Fonctionnalités v1.8 déjà validées

- **DEV_1–2** : titre i18n, reset A/B, responsive/header fonctionnel et Status/Feedback v1.
- **DEV_3** : Batch 1–4 cartes, paramètres indépendants, seeds communes/individuelles, historique, miniatures réelles et affectation A/B.
- **DEV_4** : vues Départs/Territoires, palette J1–J20, marqueurs et calques de
  rendu optimisés ; les frontières initiales sont désormais limitées aux
  cellules natives directes d'un SAV.
- **DEV_5** : centres d’export cartes et Graphiques multi-format.
- **DEV_6** : interface dynamique FR/EN/DE/ES ; FR/EN relues, DE/ES automatiques et partiellement revues.
- **DEV_7** : historique unifié, capacités 4/8/12/16, protections V/A/B, aperçus et cycle de vie Tk sécurisé.
- **DEV_8** : raccourcis v2, conflits inline, aide thémée et capture fiable Ctrl/Shift/Alt sous Windows.
- **DEV_9** : preuve du paquet Windows x64 `onedir` et autodiagnostic du runtime réel ; packaging final reporté aux RC.
- **DEV_10** : verrou manuel `M`, ordre visuel indépendant du LRU et capacité strictement dure.

Le détail accepté de DEV_1 à DEV_10 appartient à `references/dev_notes/V1_8_DEVELOPMENT_LOG.md` et au `CHANGELOG.md`, pas à ce snapshot.

## 4. Sémantique actuelle de l’historique

- `V`, `A`, `B` et `M` protègent les sorties auxquelles ils sont attachés contre l’éviction ordinaire.
- `M` est le verrou manuel persistant pendant la session.
- L’ordre visuel manuel est indépendant de la récence LRU interne.
- Afficher une carte, l’affecter à A/B ou modifier `M` ne réordonne pas visuellement l’historique.
- **Exception observée et acceptée :** une génération simple affiche automatiquement son nouveau résultat et déplace donc `V`. L’ancienne carte affichée perd alors cette protection et peut être évincée si la capacité est pleine et que les autres entrées restent protégées.
- L’aide et l’infobulle du cadenas expliquent cette exception ; la politique d’éviction elle-même reste inchangée.

## 5. Problèmes connus et reports explicites

### Restructuration v1.9 — périmètre actuel

- La chaîne de noms versionnés puis la chaîne temporaire `base/settings/export`
  ont disparu. `ShellWindow` est l’unique fondation Tk, `MainWindow` compose les
  contrôleurs et `runtime.App` injecte seul le moteur.
- Batch et Historique possèdent chacun un paquet et un contrôleur autonome ;
  leurs mixins documentent le contrat d’état hôte pendant la transition.
- Les trois couches moteur vivent sous `generation/base.py`, `continental.py`
  et `validated.py`. Une matrice Legacy 4P / Upgraded 20P confirme une identité
  exacte des octets, départs, validations et journaux par rapport à R3.
- `application/main_window.py` contient environ 370 lignes cohérentes de
  construction responsive, feedback et initialisation d’état.
- La racine `s3mapgen/` ne contient plus que `__init__.py` et `version.py`.
  `map_data/` porte uniquement le modèle, les constantes, HEX6 et les formats
  binaires partagés. Des tests interdisent `map_data → application/generation`
  et `generation → application`.
- Les petits modules ne sont pas mauvais par principe : fusionner seulement ceux qui représentent une abstraction artificielle ou dupliquée.
- Commencer par inventaire des dépendances et tests de caractérisation, puis extractions mécaniques courtes à comportement constant.
- Les réponses d’autres LLM seront reçues comme hypothèses complémentaires, tracées et vérifiées avant adoption.

### Limites non bloquantes

- Le rapport texte Statistiques ne se retraduit qu’après rechargement de la carte.
- Un calcul Statistiques exceptionnellement long a été observé une fois sans reproduction ; profiler seulement si un cas reproductible apparaît.
- Génération calibrée uniquement pour Continental 768×768.
- SAV : lecture ciblée et copie inchangée uniquement, aucun writer.

### DEV_3 — Data Mapping joueur, masque SAV, catalogue et végétation

- Le bloc SAV type 6 natif (`84 + 20×328`), ses départs et le candidat
  race/faction sont documentés ; rapports JSON/CSV exposent aussi les inconnus.
- Le triplet immédiat 4P confirme le masque direct type-3 byte 8 (`3500/3500/4000/4000`) ; aucune reconstruction n'est utilisée. La vue **Masque initial** ajoute un hachurage blanc et reste neutre sans champ direct.
- Aucun fichier de génération protégé n'a été modifié. Les objets `208–214`,
  `216–222`, `224–230` et `232–255` sont nommés ; `215/223/231` restent
  crash-prone et hors nomenclature.
- Les nids `247–253` sont comptés dans Agriculture, présents dans la vue
  Cultures avec une teinte miel distincte du blé, et absents du graphique
  forestier.
- Les objets `82/83` sont explicitement reportés à **Datamining v2** : aucune
  occurrence naturelle n’a été trouvée dans le corpus actuel et l’injection de
  calibration est exclue comme preuve. Les terrains `18/19` sont validés comme
  détails d’herbe singleton entourés d’herbe ID16 et
  intégrés à la famille Herbe, aux statistiques, au graphique et à l’inspecteur.
- Les statistiques distinguent désormais plantations `84`, pousses stade 1/2 et variantes de palmier `229`/`221`. Le graphique **Arbres et pousses** suit l'ordre adultes → stade 2 → stade 1 → plantations → palmiers adultes, avec tooltips et couleurs graduées.
- Validation Windows de la candidate cumulative R7 confirmée ; le checkpoint
  complet **DEV_3** est maintenant promu sur `dev`.

## 6. Suite de la roadmap

- **v1.9 DEV_3** : Data Mapping ciblé et consolidation du checkpoint terminés ;
  pas de nouvel audit de génération dans cette ligne.
- **Audits v2.0 — première tranche et point 4 terminés** : terrains, joueurs, ressources
  Legacy et proximité des objets sont documentés pour les 16 SAV 768. La
  densité statique autour des starts ne montre pas de halo vide fixe de 14 hex ;
  les petits décors peuvent être très proches, sans que leur hitbox soit encore
  démontrée. L'extension aux autres tailles et l'audit exhaustif des objets
  restent à faire avant de figer les profils. Le rapport du point 4 confirme
  que les transitions sont sûres, mais que Shore48, ressources, rivières et
  décorations doivent encore être améliorées.
- **Règles/générateur** : conserver les transitions dures et l'architecture
  start-first ; ne pas déplacer les starts à la fin sur une inférence. La
  prochaine passe Legacy doit corriger les écarts mesurés avant le Custom.
- **RC/STABLE** : seulement après validation Windows/jeu du Legacy v2 ; le
  portable Windows et l’updater reviennent à cette étape.
- Après Continental : Large Islands, puis Small Islands.
- Comparaison multi-cartes 3+, Modifiers et éditeur intégré restent prévus plus tard sans numéro prématuré.

## 7. Prochaine action

1. Rejouer la suite complète `pytest` dans un environnement équipé, puis
   utiliser l’archive source DEV_1 pour la validation Windows.
2. Comparer visuellement DEV_1 aux références 768 2P/20P : occupation du noyau
   montagneux, rayons 3/4/5, remplissage aléatoire et écrasements séquentiels ;
   ajuster seulement avec une nouvelle mesure.
3. Étendre, si nécessaire, les audits aux SAV natifs des autres tailles et
   conserver les séries 2P/20P séparées ; ensuite corriger Shore48, rivières et
   décorations avant le générateur Custom.

## 8. Procédure de reprise

1. Lire `AGENTS.md`, puis `PROJECT_WORKFLOW.md` et ce snapshot.
2. Lire uniquement la section active de `TODO_MAPGEN.md`, puis
   `DEV_CANDIDATE_NOTES.md` si une candidate locale existe.
3. Vérifier l’état réel de `dev`; ne consulter les journaux historiques que si
   le snapshot ne suffit pas.
4. Avant tout changement génération/format, suivre
   `references/SETTLERS3_PREGEN_READ_FIRST.md`.
