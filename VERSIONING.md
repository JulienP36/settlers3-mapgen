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
  `RC`/`STABLE` prévu ; R48 n’est ni poussée ni publiée comme release.


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
- Latest published development checkpoint: `v2.0 DEV_7`.
- Active development line: `v2.0 DEV_7` (prochaine tranche : archétypes
  Custom).
- Current local candidate: none. The former `v2.0 DEV_7_R26` candidate was
  validated and promoted as `v2.0 DEV_7`. It contains only the validated
  Générateur UI finish: terrain microcopy removal, dense-block ordering, the
  three-column Bonus layout and the earlier responsive split threshold; the
  engine, data, exports and generation rules are unchanged.
- No suffixed DEV_7 candidate remains active after validation of the checkpoint.
- Suffixed candidates (`DEV_X_R1`, `R2`, etc.) are local Windows-test/recovery artifacts. Publish only the completed `DEV_X` checkpoint without a revision suffix on `dev`.
- Every validated DEV candidate, RC or STABLE stage must refresh `references/SETTLERS3_CURRENT_SNAPSHOT.md` before its final archive, commit or push. Validating a local `DEV_X_Rn` updates recovery state but never authorizes publishing that suffix.
- v2.0 DEV_2 was the validated native-generator reset/reconstruction line;
  v2.0 DEV_3 is the validated calibration line, v2.0 DEV_4 is the published
  UI/export line, and v2.0 DEV_5 is the validated Upgraded finishing line.
  The next development checkpoint is v2.0 DEV_6, focused on the Custom
  generator. R-suffixed archives remain local Windows-test candidates; only
  completed unsuffixed DEVs may be promoted to `dev`.
