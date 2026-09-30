# Convention de versionnage

Convention validée pour les builds du projet :

- `DEV` : build de travail intermédiaire ;
- `RC` : Release Candidate destinée aux tests ;
- `STABLE` : version finale validée.

## Nommage

Dossier : `mapgen_v<MAJEURE>_<MINEURE>_<ETAT>[_<NUMERO>]`

Archive : `SETTLERS3_MAPGEN_V<MAJEURE>_<MINEURE>_<ETAT>[_<NUMERO>]_<DATE>.zip`

Exemples :

- `mapgen_v1_6_DEV_1`
- `mapgen_v1_6_RC_7`
- `mapgen_v1_6_STABLE`
- `SETTLERS3_MAPGEN_V1_6_RC_7_20260820.zip`

L'historique v1.6 est documenté rétroactivement avec `RC_n` afin d'éviter une rupture de nomenclature. Les anciennes archives déjà produites peuvent conserver leur ancien nom physique ; la documentation canonique utilise désormais `RC`.

## Règle de révision du projet

- Chaque modification apportée à la candidate locale incrémente son suffixe
  `R` : `DEV_6_R41` devient donc `DEV_6_R42` pour cette tranche.
- Tant qu’aucun push n’est effectué, le compteur `DEV` reste celui de la ligne
  en cours ; les candidates `R` restent des états locaux de travail et de test.
- Lorsqu’un checkpoint est poussé, la ligne de développement suivante incrémente
  le compteur `DEV`. Un push n’est pas une release.
- Une release n’existe qu’après la fin du périmètre, sa validation et le cycle
  `RC`/`STABLE` prévu ; R49 n’est ni poussée ni publiée comme release.


## Références de workflow

Le workflow projet global est défini dans `PROJECT_WORKFLOW.md`. Le routage
des références et le point de reprise courant sont
`references/REFERENCE_INDEX.md` et `references/SETTLERS3_CURRENT_SNAPSHOT.md`.
Ces fichiers doivent être consultés avant une nouvelle session de développement.


## v1.7 STABLE
- RC_1 validated and promoted without feature changes.
- GitHub Release policy: publish STABLE only.
- v1.7 historical DEV/RC notes are archived under `references/release_notes/v1_7_history/`.

## Current development

- Latest published STABLE: `v1.7`.
- Latest published development checkpoint: `v2.0 DEV_8`, built from local
  candidate R86 and pushed to branch `dev`.
- Active development line: `v2.0 DEV_9` (Great Islands and remaining work).
- DEV8 closes the Archetype tab with named `Classique` and `Continental`
  profiles, and a dynamic `Personnalisé` state in the main Archetype selector.
  Full noisemap generation remains available as an experimental option.
- DEV8 validation: 641 regression tests, smoke checks and extracted-package
  self-test PASS. The user confirmed Windows visual validation of R85; Custom
  rivers and multi-size tests are declared complete.
- `DEV_X_Rn` archives remain local candidates. Publish only complete unsuffixed
  DEV checkpoints on `dev`; never publish an R suffix as a checkpoint.
- Before the next DEV9 work, read `PROJECT_WORKFLOW.md`, the active TODO and
  the current recovery snapshot.
