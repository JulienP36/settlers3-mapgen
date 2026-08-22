# v1.8 DEV_3_R7 — Final Batch spacing

## Changements depuis R6

- Suppression du bouton redondant « Appliquer » / « Apply » situé après le nombre de cartes.
- Le nombre de cartes affichées réagit immédiatement aux flèches et aux valeurs 1–4 saisies au clavier.
- Entrée ou perte de focus normalise toute valeur finale dans l'intervalle 1–4.
- Marge de 8 px entre la barre progression/feedback et la zone miniature.
- Conteneur miniature : 182×122.
- Rendu : 180×120 maximum, parfaitement adapté au rapport du parallélogramme et sans diminution de sa taille R6 effective.
- La vue Carrée reste centrée dans cette même zone.

## Validation automatisée

- 109 tests de régression PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Moteur, profils et bibliothèque native protégés inchangés.

## Validation Windows demandée

1. Vérifier l'espace entre les quatre barres et les miniatures.
2. Vérifier que le parallélogramme remplit correctement la largeur réduite.
3. Basculer en Carrée et vérifier son centrage.
4. Modifier le nombre de cartes avec les flèches puis au clavier : aucun bouton de confirmation ne doit être nécessaire.

Après validation, synchroniser exactement R7 sur `dev`, puis demander à l'utilisateur ses dernières notes du TODO local avant la suite.

## Validation Windows finale

- R7 validée par l'utilisateur ; DEV_3 complète est acceptée.
- Promotion sur `dev` autorisée.
- Capture de diversité multi-seeds archivée pour investigation différée à v1.10, sans modification du moteur dans DEV_3.
