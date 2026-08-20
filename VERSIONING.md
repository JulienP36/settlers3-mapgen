# Convention de versionnage

> Pour le workflow projet complet, toujours commencer par `PROJECT_WORKFLOW.md`, puis consulter `references/SETTLERS3_CURRENT_SNAPSHOT.md` pour l'état courant.

Convention validée pour les builds du projet :

- `DEV` : build de travail intermédiaire ;
- `RC` : Release Candidate destinée aux tests ;
- `STABLE` : version finale validée.

## Nommage des builds

Dossier : `mapgen_v<MAJEURE>_<MINEURE>_<ETAT>[_<NUMERO>]`

Archive : `SETTLERS3_MAPGEN_V<MAJEURE>_<MINEURE>_<ETAT>[_<NUMERO>]_<DATE>.zip`

Exemples :

- `mapgen_v1_6_DEV_1`
- `mapgen_v1_6_RC_7`
- `mapgen_v1_6_STABLE`
- `SETTLERS3_MAPGEN_V1_6_RC_7_20260820.zip`
- `SETTLERS3_MAPGEN_V1_6_STABLE_20260820.zip`

L'historique v1.6 est documenté rétroactivement avec `RC_n` afin d'éviter une rupture de nomenclature. Les anciennes archives déjà produites peuvent conserver leur ancien nom physique ; la documentation canonique utilise désormais `RC`.

### Nommage interne des modules versionnés

Pour les futurs renommages/refactors, utiliser une écriture explicite de la version avec underscore : `v1_5`, `v1_6`, etc., plutôt que les formes ambiguës `v15`, `v16`.

Exemples cibles : `gui_v1_5.py`, `gui_v1_6.py`, `gui_v1_6_runtime.py`, `generator_v1_5.py`.

Les fichiers historiques/validés existants ne doivent pas être renommés isolément : la migration doit être atomique et couvrir imports, tests, scripts, entry points, documentation et contrôles de hashes lorsque nécessaire.

## Branches permanentes

Trois branches permanentes matérialisent le niveau de stabilité du projet :

- `main` : uniquement les versions STABLE validées ;
- `dev` : développement courant et checkpoints fréquents testés ;
- `rc` : Release Candidates en cours de validation.

Le flux normal est `dev` → `rc` → `main`. Les checkpoints DEV suffisamment cohérents doivent être enregistrés régulièrement sur `dev` afin de conserver une trace durable du travail même entre deux longues sessions. Une RC est promue sur `rc` uniquement lorsqu'elle est destinée à une validation externe. `main` ne reçoit le changement qu'après validation de la RC.

La politique détaillée de fréquence des checkpoints, reprise après perte de contexte, fichiers protégés, intégrité package ↔ branche et documentation vivante est définie dans `PROJECT_WORKFLOW.md`.

## Tags Git

Les versions STABLE reçoivent un tag de version `vX.Y` (par exemple `v1.6`). Les builds `DEV` et `RC` ne nécessitent pas de tag Git sauf besoin exceptionnel d'archivage.

Le tag d'une version STABLE doit pointer vers le premier commit où l'état publié est réellement complet : code, documentation canonique et métadonnées de release cohérents.

## Workflow canonique d'une release STABLE

1. développer et checkpoint régulièrement sur `dev` ;
2. maintenir `references/SETTLERS3_CURRENT_SNAPSHOT.md` à jour aux jalons significatifs ;
3. figer une candidate suffisamment mature et la promouvoir sur `rc` ;
4. valider la RC sans ajouter de fonctionnalité ;
5. nettoyer les fichiers temporaires/artefacts de test qui n'ont pas vocation à être conservés ;
6. mettre à jour le code, `README.md`, `TODO_MAPGEN.md`, les références pertinentes et toute documentation affectée ;
7. exécuter les tests smoke/régression et les contrôles de non-régression du moteur ;
8. mettre à jour `CHANGELOG.md` et `RELEASE_VALIDATION.md` ;
9. préparer le package `STABLE` et son manifest/hash ;
10. promouvoir l'état validé sur `main` ;
11. vérifier l'état publié sur GitHub, l'équivalence du source avec le package testé et corriger toute omission documentaire avant le tag ;
12. créer le tag annoté `vX.Y` sur le commit STABLE complet ;
13. pousser/synchroniser `main` et les tags ;
14. publier l'archive ZIP et les gros checkpoints binaires via GitHub Release ou Git LFS selon la politique de stockage.

## Branches temporaires

Les branches `feat/*`, `fix/*` et `research/*` restent possibles pour un travail isolé ou expérimental. Une fois leur contenu utile intégré ou explicitement supplanté sur `dev`, `rc` ou `main`, elles doivent être auditées puis supprimées afin d'éviter qu'un ancien état soit confondu avec la baseline courante.

Une branche divergente ne doit jamais être supprimée uniquement parce qu'une branche permanente est plus récente : ses commits uniques doivent d'abord être vérifiés. Les informations historiques utiles doivent être intégrées à une branche permanente, à une référence canonique ou être conservées par un tag avant suppression.
