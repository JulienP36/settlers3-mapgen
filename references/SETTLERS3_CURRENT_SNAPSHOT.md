# Settlers III MapGen — CURRENT SNAPSHOT

> **Point de reprise vivant — état actuel uniquement.**
>
> Dernière mise à jour : **2026-08-26 — DEV_11 validée, passage en RC**

## 1. État immédiat

- Dépôt : `JulienP36/settlers3-mapgen`.
- Branche de travail : `dev`.
- Dernier checkpoint de développement : **v1.8 DEV_11**, validé et destiné à la branche `dev` sans suffixe de révision.
- Dernière STABLE : **v1.7**, publiée sur `main`, tag `v1.7`, commit de promotion `780bc5e`.
- **DEV_11 validée** : maintenance, ZIP source déterministe, documentation, README anglais, quatre captures Windows réelles, About/Topics GitHub, architecture/diagnostic et clarification de `V` terminés.
- Validations : 231 tests pytest, autodiagnostic depuis le ZIP extrait, 49 validations moteur, checksum binaire et cinq hashes protégés PASS ; contrôles Windows R1 puis R2 validés.
- Les candidates R1/R2 et le paquet `CAPTURE_ONLY` restent des artefacts locaux historiques. Aucune révision suffixée `R` n’est publiée ; la feuille de candidate roulante est retirée à la clôture.
- Prochaine ligne de travail : **v1.8 RC** sur la branche `rc`, avec gel fonctionnel, packaging Windows portable et updater v2.

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

- `s3mapgen/generator_v15.py` — `3bbc9180719ebfae2bc37b29d81025731dc821e861c7b0e66894f7460f296090`
- `s3mapgen/generator.py` — `1b73f2536c6db75dfb3856a1667d0b619d3462d9c0efa14f406c78a05556be77`
- `config/legacy_768_v1.json` — `bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85`
- `config/upgraded_768_v1.json` — `11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441`
- `data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz` — `fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d`

Ne modifier aucun de ces fichiers sans raison explicite liée au moteur et lecture préalable de `SETTLERS3_PREGEN_READ_FIRST.md`.

## 3. Fonctionnalités v1.8 déjà validées

- **DEV_1–2** : titre i18n, reset A/B, responsive/header fonctionnel et Status/Feedback v1.
- **DEV_3** : Batch 1–4 cartes, paramètres indépendants, seeds communes/individuelles, historique, miniatures réelles et affectation A/B.
- **DEV_4** : vues Départs/Territoires, palette J1–J20, frontière exacte de 210 cellules, marqueurs et calques de rendu optimisés.
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

### Priorité v1.9 DEV_1 — imports EDM partiellement défaillants

- Certains fichiers `.EDM` s’ouvrent correctement ; d’autres échouent.
- Les `.MAP` et `.SAV` utilisés pendant le sanity check DEV_11_R1 fonctionnent.
- Le défaut peut être ancien et devient urgent avant les tests contrôlés d’IDs de v1.9.
- Conserver le futur screenshot utilisateur, les vrais fichiers concernés, leurs SHA-256 et le traceback complet.
- Diagnostiquer en lecture seule ; ne pas inventer de structure binaire ni assouplir aveuglément les contrôles.

### Limites non bloquantes

- Le rapport texte Statistiques ne se retraduit qu’après rechargement de la carte.
- Un calcul Statistiques exceptionnellement long a été observé une fois sans reproduction ; profiler seulement si un cas reproductible apparaît.
- Génération calibrée uniquement pour Continental 768×768.
- SAV : lecture ciblée et copie inchangée uniquement, aucun writer.

## 7. Suite de la roadmap

- **RC v1.8** : gel des nouvelles fonctionnalités, mais corrections/polish/optimisation/documentation autorisés ; ZIP sources et ZIP Windows x64 portable séparés ; updater v2, SHA, rollback, préservation des settings et tests d’échec réseau/intégrité.
- **v1.9** : d’abord corriger les imports EDM concernés, puis archéologie/Data Mapping, bornes Terrain/Object IDs, catégories runtime, couleurs effectives joueurs et tests contrôlés IDs 18/19.
- **v1.10** : audit seed/RNG et diversité morphologique, détection objective des doublons/rotations, puis Continental multi-tailles 384 → 448 → 512 → 576 → 640 → 704 → 768.
- Après Continental : Large Islands, puis Small Islands.
- Comparaison multi-cartes 3+, Modifiers et éditeur intégré restent prévus plus tard sans numéro prématuré.

## 8. Prochaine action

1. Créer/actualiser la branche `rc` depuis le checkpoint DEV_11 validé.
2. Geler les nouvelles fonctionnalités tout en autorisant corrections, polish, optimisation et documentation.
3. Construire séparément le ZIP sources et le ZIP Windows x64 portable `onedir`.
4. Finaliser et tester l’updater v2, l’intégrité SHA-256, la préservation des settings et le rollback.

## 9. Procédure de reprise

1. Vérifier que `dev` contient le checkpoint final `DEV_11`, puis travailler sur `rc` pour la phase Release Candidate.
2. Lire `PROJECT_WORKFLOW.md`.
3. Lire ce snapshot.
4. Lire `TODO_MAPGEN.md`, puis `DEV_CANDIDATE_NOTES.md` si une candidate locale existe.
5. Consulter `references/dev_notes/V1_8_DEVELOPMENT_LOG.md` seulement pour l’historique accepté.
6. Avant tout changement génération/format, lire `references/SETTLERS3_PREGEN_READ_FIRST.md` et ses références obligatoires.
7. Mettre ce snapshot à jour après chaque DEV validée, chaque RC et chaque STABLE, avant le commit/package final correspondant.
