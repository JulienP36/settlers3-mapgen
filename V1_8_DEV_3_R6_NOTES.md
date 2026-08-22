# v1.8 DEV_3_R6 — Final mini-map sizing

## Changement unique depuis R5

- Carte miniature : 222×120 maximum au lieu de 202×108.
- Conteneur : 224×122 au lieu de 204×110.
- Marge interne carte/conteneur : 1 px conservé.
- Marge conteneur/cadre blanc extérieur : environ 1 px.
- Les contrôles conservent leur propre marge et tous les comportements R5 restent inchangés.

## Validation automatisée

- 107 tests de régression PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Moteur, profils et bibliothèque native protégés inchangés.

## Validation Windows demandée

Contrôler uniquement que les quatre miniatures sont sensiblement plus grandes, restent propres en Carrée et Parallélogramme, et occupent correctement l'espace jusqu'au cadre extérieur sans chevauchement.

Après validation, synchroniser exactement R6 sur `dev`, puis demander à l'utilisateur ses dernières notes du TODO local avant la suite.
