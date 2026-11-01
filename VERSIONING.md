# Convention de versionnage

## Parcours actif — décision du 14 octobre 2026

- `DEV` : développement, corrections, qualification et essais utilisateur sur `dev`.
- `STABLE` : version finale validée et publiée sur `main`.
- L'étape RC est abandonnée. Parcours direct `dev` → `main` / STABLE ; toutes
  les validations nécessaires se font pendant le développement.
- Publier sur `main`, créer un tag ou une GitHub Release exige toujours
  l'autorisation explicite du propriétaire.

## Nommage et révisions

Archive : `SETTLERS3_MAPGEN_V<MAJEURE>_<MINEURE>_<ETAT>[_<NUMERO>]_<DATE>.zip`.
Exemples : `2.0 DEV_11_R1` (candidate locale), `2.0 DEV_11` (checkpoint complet),
`2.0 STABLE` (release finale).

- Chaque modification d'une candidate locale incrémente `R`, y compris une révision documentaire archivée.
- Les candidates `DEV_X_Rn` restent locales ; seuls les checkpoints DEV complets
  validés sont publiés sur `dev`, sans suffixe R.
- Le compteur DEV avance après publication du checkpoint précédent ; un push
  DEV n'est pas une release.
- Les corrections de maintenance d'un checkpoint publié gardent son nom DEV.
- Seule STABLE reçoit un tag annoté `vX.Y` et une GitHub Release avec artefacts.

## État courant

Dernier checkpoint publié : **2.0 DEV_10**, issu de R66 validée. Build Windows
DEV10 validé : 1306 tests, 4 subtests, smokes et auto-test figé PASS
(run `38467559806`, version Windows `(2, 0, 10, 0)`).

Candidate locale : **2.0 DEV_11**, revue documentaire du 31 octobre 2026.
La passe fonctionnelle R13 est acceptée ; captures finales intégrées en R14.
DEV11 reste ouverte pour la construction et qualification du portable Windows,
puis validation globale. Aucun push intermédiaire ni nouvelle branche.
La qualification DEV10 ne vaut pas qualification du portable DEV11.
Checklist active : `docs/RELEASE_2_0_CHECKLIST.md`.

## Historique

Les anciens noms `RC_n`, branches et archives gardent leur signification
historique. v1.6 utilisait RC ; v1.7 STABLE a été promue depuis RC_1 validée.
Cet historique ne définit plus le workflow actif.

## Reprise

Lire `PROJECT_WORKFLOW.md`, `TODO_MAPGEN.md`, puis l'index et le snapshot des
références lorsqu'ils sont disponibles dans le ZIP source.
