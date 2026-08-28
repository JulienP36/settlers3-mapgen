# Settlers III MapGen — CURRENT SNAPSHOT

> **Point de reprise vivant — état actuel uniquement.**
>
> Dernière mise à jour : **2026-08-28 — v1.9 DEV_3 validée sous Windows et promue sur `dev`**

## 1. État immédiat

- Dépôt : `JulienP36/settlers3-mapgen`.
- Branche de travail : `dev`.
- Dernier checkpoint validé : **v1.9 DEV_3**, validé sous Windows et promu sur
  `dev`. Il consolide R1–R7 : catalogue contrôlé, graphes de végétation,
  champs joueurs SAV, masque direct type-3 byte 8 et contrôles automatisés ;
  aucune candidate suffixée n'est active.
- Dernière STABLE : **v1.7**, publiée sur `main`, tag `v1.7`, commit de promotion `780bc5e`.
- **DEV_11 validée** : maintenance, ZIP source déterministe, documentation, README anglais, quatre captures Windows réelles, About/Topics GitHub, architecture/diagnostic et clarification de `V` terminés.
- Validations : 231 tests pytest, autodiagnostic depuis le ZIP extrait, 49 validations moteur, checksum binaire et cinq hashes protégés PASS ; contrôles Windows R1 puis R2 validés.
- Les candidates R1/R2 et le paquet `CAPTURE_ONLY` restent des artefacts locaux historiques. Aucune révision suffixée `R` n’est publiée ; la feuille de candidate roulante est retirée à la clôture.
- Réconciliation de branches terminée au commit `f56ee1a` : `dev` contient désormais `main` dans son ascendance sans modification de l’arbre DEV_11.
- **v1.9 DEV_1 validée** : les deux EDM fautifs chargent sous Windows ; la candidate R1 est consolidée sans suffixe et sa feuille roulante retirée.
- **v1.9 DEV_2 validée** : l’ancien monolithe et les modules versionnés sont
  remplacés par les couches `application/`, `generation/` et `map_data/`, avec
  contrôleurs par sous-système, fondation Tk unique et un seul factory moteur.
  `main_window.py` passe de 3168 à 372 lignes ; 243 tests actuels passent, sans
  doublon exact ni nom de révision historique. Les petits modules/entrypoints
  restants portent tous une responsabilité justifiée. `AGENTS.md` devient
  l’entrée courte auto-découverte pour limiter le contexte répété.
- La v1.9 est requalifiée : restructuration interne prioritaire ; Data Mapping ciblé est clôturé dans DEV_3.
- La v1.8 reste une série de checkpoints DEV sans RC ni Release ; aucune STABLE
  n’est prévue avant la reconstruction réelle du générateur, potentiellement v2.0.

## 2. Socle validé à préserver

### Génération

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
- `s3mapgen/generation/validated.py` — `aec27207b47d09134a5205a08d72a9b5e759f947d87080922dd61251c0c7ccce`
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

## 5. DEV_11 — résultat validé

- Version runtime et packaging centralisée en `1.8 DEV_11`.
- Règles d’ordre/protection isolées en helpers purs ; cache documenté sans changement de contrat.
- ZIP source déterministe avec racine unique, exclusions, fichiers obligatoires et autodiagnostic depuis l’extraction.
- Documents canoniques nettoyés et rôles séparés ; snapshot obligatoire après chaque DEV/RC/STABLE validée.
- README anglais et quatre captures Windows réelles intégrés avec provenance.
- Description About et neuf Topics appliqués au dépôt GitHub.
- Guides architecture/diagnostic et commentaires de frontières ajoutés sans instrumentation ni coût runtime permanent.
- Protection `V` expliquée dans l’aide et l’infobulle, comportement d’éviction inchangé.
- Contrôles Windows R1 et R2 validés ; le détail historique est consolidé dans `references/dev_notes/V1_8_DEVELOPMENT_LOG.md`.

## 6. Problèmes connus et reports explicites

### v1.9 DEV_1 — import EDM, Issue #4

- Deux vrais fichiers fautifs et le screenshot/traceback utilisateur ont été fournis.
- Les deux sources sont en version 10 avec checksum exact et parties complètes.
- Cause confirmée : après la partie terminale `type 0 / taille 8`, certains EDM conservent 1 à 3 octets opaques afin d’aligner la taille du fichier sur un DWORD.
- Le lecteur accepte désormais uniquement ce cas borné ; une queue sans terminateur reste rejetée et le parseur de scaffolds/export reste strict.
- Régressions automatisées : remplissages de 1, 2 et 3 octets, refus sans terminateur, import réel 256×256/20 départs et 768×768/10 départs.
- Détails, hashes et offsets : `references/SETTLERS3_EDM_TERMINAL_PADDING_20260826.md`.
- Validation Windows : les deux sources fautives chargent correctement. Issue #4 à fermer après publication du checkpoint final.

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

## 7. Suite de la roadmap

- **v1.9 DEV_3** : Data Mapping ciblé et consolidation du checkpoint terminés ;
  pas de nouvel audit de génération dans cette ligne.
- **Prochaine RC/STABLE** : après la reconstruction majeure du générateur,
  potentiellement v2.0 ; elle reprendra alors le portable Windows et l'updater.
- **v2.0 potentielle** : reconstruction réelle du générateur, seed/RNG et
  diversité morphologique ; l'ancien « audit v1.10 » est reporté car le moteur
  actuel ne produit pas encore une vraie diversité.
- Après Continental : Large Islands, puis Small Islands.
- Comparaison multi-cartes 3+, Modifiers et éditeur intégré restent prévus plus tard sans numéro prématuré.

## 8. Prochaine action

1. Garder objets `82/83`, couleur SAV, mana et tribu nominale pour Datamining v2,
   sur corpus contrôlé et sans writer SAV.
2. N'ouvrir le chantier suivant qu'après décision explicite : reconstruction réelle du générateur/diversité morphologique, potentiellement v2.0.

## 9. Procédure de reprise

1. Lire `AGENTS.md`, puis `PROJECT_WORKFLOW.md` et ce snapshot.
2. Lire uniquement la section active de `TODO_MAPGEN.md`, puis
   `DEV_CANDIDATE_NOTES.md` si une candidate locale existe.
3. Vérifier l’état réel de `dev`; ne consulter les journaux historiques que si
   le snapshot ne suffit pas.
4. Avant tout changement génération/format, suivre
   `references/SETTLERS3_PREGEN_READ_FIRST.md`.
