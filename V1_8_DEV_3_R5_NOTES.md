# v1.8 DEV_3_R5 — Batch density and initial geometry

## Changements depuis R4

- Conteneur miniature resserré de 210×116 à 204×110.
- Carte rendue toujours jusqu'à 202×108 : aucune perte de lisibilité volontaire.
- Marges du header, des cadres, des quatre lignes et du footer légèrement réduites.
- Après construction, la fenêtre mesure la taille réellement demandée par tous ses widgets.
- Si l'écran dispose de la place nécessaire, elle s'ouvre directement avec les quatre cartes et le footer visibles.
- Si l'espace est insuffisant, la taille est limitée à la surface écran disponible ; la fenêtre reste redimensionnable.
- Placement initial centré relativement à l'application principale puis contraint aux limites visibles.

## Validation automatisée

- 106 tests de régression PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Moteur, profils et bibliothèque native protégés inchangés.

## Validation Windows demandée

1. Ouvrir Batch sur le grand écran et vérifier que les quatre cartes, le statut et les boutons du footer sont visibles immédiatement.
2. Vérifier que les miniatures sont plus serrées sans diminution sensible de la carte rendue.
3. Déplacer la fenêtre principale puis rouvrir Batch : la nouvelle fenêtre doit rester centrée et entièrement dans l'écran.
4. Vérifier que le redimensionnement manuel reste normal.

Après validation, synchroniser exactement R5 sur `dev`, puis demander à l'utilisateur ses dernières notes du TODO local avant la suite.
