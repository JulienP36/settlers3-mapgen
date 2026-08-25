# Settlers III MapGen — Release validation

Date : 2026-08-21

> Document historique de la validation **v1.7 STABLE**. Il ne décrit pas l’état courant de v1.8 ; utiliser `PROJECT_WORKFLOW.md`, `VERSIONING.md` et `references/SETTLERS3_CURRENT_SNAPSHOT.md` pour la reprise actuelle.

## v1.7 — STABLE

La v1.7 est la release de fondation **Statistiques / Graphiques** au-dessus du moteur de génération v1.5 stable et inchangé.

Périmètre validé durant les DEV v1.7 : statistiques exactes et debug structurées, inventaires complets Terrain/Object IDs, densités normalisées, analyses locales par joueur, composants géographiques/hydrologiques, exports JSON/CSV, graphiques verticaux sémantiques, comparaison A/B, tooltips interactifs contextuels, segmentation Mer/Lacs, Roche/Neige, Herbe verte/Herbe sèche, ressources minières et agriculture, intégration FR/EN et thèmes clair/sombre.

La DEV_11_R2 a été validée par l'utilisateur et synchronisée exactement sur `dev` au commit `5b04aa5`. RC_1 a ensuite été validée sur Windows : lancement/UI, export, rechargement d'un EDM exporté et View Map in-game sans régression. La STABLE est une promotion de RC_1 sans nouvelle fonctionnalité.

Le moteur de génération de référence reste v1.5 : `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`. Les fichiers moteur/config protégés doivent rester byte-for-byte identiques.

## Validation STABLE

- aucun ajout de fonctionnalité après l'entrée en RC ;
- uniquement corrections de validation/release si nécessaire ;
- tests automatisés complets au vert ;
- hashes protégés inchangés ;
- validation utilisateur Windows de la RC ;
- après validation : promotion vers `main`, tag annoté `v1.7`, GitHub Release STABLE et ZIP final.

## Après v1.7

Courte passe de TODO/outillage, avec notamment la préparation du workflow Batch Generation v1.8, puis retour prioritaire au générateur Continental multi-tailles. La comparaison multi-maps 3+ est planifiée à très forte probabilité après une grosse passe générateur et servira notamment aux futures expérimentations Modifiers.
