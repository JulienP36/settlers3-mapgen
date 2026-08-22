# v1.8 DEV_3_R1 — Batch Generation v1

## Fonctionnalités

- Fenêtre Batch séparée, bilingue FR/EN.
- 1 à 4 cartes configurables indépendamment.
- Paramètres par carte : mode, archétype, modificateurs réservés, taille, joueurs et seed.
- Bouton de renouvellement global des seeds et seed aléatoire par carte.
- File de génération séquentielle réutilisant exclusivement le pipeline v1.5 existant.
- Réutilisation transparente du cache de session.
- États et progression individuels : attente, génération, succès, cache, erreur et annulation.
- Annulation des cartes encore en attente après la carte en cours.
- Ajout automatique des réussites à l'historique de session.
- Après le lot : afficher chaque résultat ou l'affecter directement à A ou B.
- Aucun export automatique ; l'export unifié reste une étape v1.8 séparée.

## Validation automatisée

- 95 tests pytest PASS.
- Génération smoke : 49 validations PASS.
- Binary checksum PASS.
- Moteur, profils et bibliothèque native protégés inchangés.

## Validation Windows demandée

1. Ouvrir puis fermer la fenêtre Batch en FR et en EN.
2. Afficher 1, 2, 3 puis 4 cartes sans chevauchement ni zone inaccessible.
3. Vérifier l'indépendance des modes, joueurs et seeds.
4. Générer un lot de 2 à 4 cartes et contrôler la progression séquentielle.
5. Relancer au moins une configuration identique afin de voir l'état cache.
6. Demander une annulation pendant une génération et vérifier que seules les cartes suivantes sont annulées.
7. Contrôler l'arrivée des réussites dans l'historique, puis Afficher et Affecter à A/B.

Après validation et synchronisation sur `dev`, demander à l'utilisateur ses dernières notes du TODO local avant la suite.
