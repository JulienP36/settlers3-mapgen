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
- Validated development checkpoint: `v2.0 DEV_9`, from local R25, on `dev`.
- Runtime version `2.0 DEV_9`, Windows tuple `(2, 0, 9, 0)` ; no R suffix.
- DEV9 closes the Large islands focus and the related improved river/profile work.
- The small source-label rename is included in this checkpoint, with saved keys intact.
- R25 qualification: 818 tests, seven complete maps, four exports and extracted ZIP PASS.
- Next line: DEV10, prioritizing previous DEV9 work outside the completed scope.
  Small islands is DEV10 or DEV11; further derived archetypes are undecided.
- DEV/RC are not Releases. Only complete unsuffixed DEV checkpoints are pushed.
- Read PROJECT_WORKFLOW, TODO and the available recovery snapshot before next work.
