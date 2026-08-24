# Settlers III MapGen v1.8 DEV_7_R10 — notes de test Windows

Cette dernière révision DEV_7, validée sous Windows, ajoute une règle anticollision aux grands aperçus temporaires sans modifier les comportements validés en R9.

- Un aperçu ouvert après 700 ms ne peut plus recouvrir sa miniature source.
- Le programme choisit la meilleure zone libre parmi les côtés gauche, droit, supérieur et inférieur.
- Si le zoom mémorisé est trop grand pour cette zone, seul le rendu temporaire est réduit.
- La valeur de zoom mémorisée reste inchangée et redevient disponible dès que l’espace le permet.
- Un aperçu épinglé conserve sa position, son zoom et sa liberté de déplacement, y compris au-dessus des miniatures.
- `Échap` ferme le grand aperçu visible comme sortie de secours.
- Le comportement est commun aux aperçus Batch et Historique.

Validation interne : 192 tests de régression, 49 validations moteur, checksum binaire et cinq hashes protégés.

## Vérification Windows

1. Agrandir fortement un grand aperçu Batch, puis le fermer.
2. Laisser la souris 700 ms sur une miniature : l’aperçu temporaire doit préserver l’accès à cette miniature.
3. Répéter avec des miniatures placées à différents endroits de la fenêtre et avec les deux projections.
4. Vérifier que la réduction automatique éventuelle n’altère pas le zoom retrouvé après épinglage ou lorsque davantage d’espace est disponible.
5. Épingler l’aperçu : il doit conserver la liberté totale de déplacement et pouvoir recouvrir une miniature.
6. Appuyer sur `Échap` pour le fermer.
7. Refaire les mêmes contrôles dans le Centre d’historique.
