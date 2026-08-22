# Settlers III MapGen v1.8 DEV_2

## Responsive UI v1
- Fenêtre initiale adaptée à la résolution réelle.
- Cible principale : 1920×1080 ; disposition compacte sous ~1500 px de largeur.
- Reflow des contrôles supérieurs en plusieurs bandes ; pas de réduction agressive des polices.
- Minimum de fenêtre abaissé à 900×650.
- Splitter carte/panneaux et proportions du contenu principal préservés.

## Status / Feedback bar v1
- La zone d’état devient un canal de feedback utilisateur explicite et semi-persistant.
- Les détails de progression rapides restent dans l’overlay/barre de progression.
- Génération : contexte complet dans le statut ; étapes techniques dans la progression ; confirmation lisible à la fin.
- Feedback FR/EN pour principaux événements et hint du filtre Heatmap verrouillé.
- Symboles légers de statut v1 ; couleurs/icônes enrichies réservées à une future v2.

## Validation
- 73 tests automatisés PASS.
- Smoke moteur : 49 validations PASS.
- Binary checksum PASS.
- Fichiers moteur/config/data protégés inchangés.
