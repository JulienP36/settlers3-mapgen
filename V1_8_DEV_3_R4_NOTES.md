# v1.8 DEV_3_R4 — Dynamic Batch previews

## Changements depuis R3

- Zone de miniature agrandie de 152×88 à 210×116 pixels.
- Rendu réel agrandi de 144×80 à 202×108 pixels.
- Suppression du relief/cadre clair autour des miniatures.
- Le passage Carrée ↔ Parallélogramme dans les paramètres principaux recalcule immédiatement toutes les miniatures Batch déjà disponibles.
- Un tooltip déjà visible est également reconstruit immédiatement avec la nouvelle projection.
- Position prévisible : tooltip adjacent à la miniature, côté disposant du plus d'espace, puis contraint aux limites verticales de l'écran.
- TODO ajouté pour de futurs marqueurs de départ basés exclusivement sur les sprites natifs exacts et validés du jeu.

## Validation automatisée

- 105 tests de régression PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Moteur, profils et bibliothèque native protégés inchangés.

## Validation Windows demandée

1. Contrôler la taille et la lisibilité des quatre miniatures ainsi que l'absence de cadre clair.
2. Laisser Batch ouverte avec des résultats, puis basculer Carrée/Parallélogramme dans Paramètres : les quatre miniatures doivent changer immédiatement.
3. Garder un tooltip affiché par clic, changer la projection et vérifier sa mise à jour immédiate.
4. Tester clic et survol sur plusieurs lignes : le tooltip doit toujours apparaître adjacent à la miniature, sans suivre la position exacte du curseur.
5. Vérifier le placement près des bords de l'écran et l'absence de débordement.

Après validation, synchroniser exactement R4 sur `dev`, puis demander à l'utilisateur ses dernières notes du TODO local avant la suite.
