# v1.8 DEV_7_R5 — Correctifs ciblés après revue Windows R4

## Périmètre

- cercle coché conservé à la taille validée, sans couronne ni pixels blancs saillants ;
- loupes R4 retirées de Batch et du Centre ; leur refonte complète est reportée vers la fin de DEV_7 ;
- interactions des miniatures conservées directement : survol temporisé et clic sur la miniature ;
- prévision de capacité Batch corrigée : carte du viewer, A, B et futurs verrous manuels sont comptés une seule fois lorsqu’ils occupent réellement le cache ;
- dernier résultat Batch affiché automatiquement uniquement si aucune carte n’est déjà présente dans le viewer ;
- anomalie rare de calcul statistique apparemment bloqué consignée pour surveillance, sans correction spéculative.

## Garanties

- tous les points R4 validés sont conservés : ordre stable, cadenas et infobulles, aperçu Historique, remplacement atomique et avertissement hors historique ;
- moteur de génération v1.5, formats binaires et données déterministes inchangés ;
- aucune publication sur `dev` avant validation Windows.

## Validation interne

- 178 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés.

## Checklist Windows

1. Vérifier les cercles cochés en clair/sombre : aucun pixel blanc ne doit dépasser.
2. Vérifier l’absence des loupes et le fonctionnement direct des miniatures Batch/Historique.
3. Avec une capacité 4 et trois cartes distinctes protégées par Viewer/A/B, lancer quatre seeds distinctes : l’avertissement doit annoncer une seule place disponible.
4. Annuler puis relancer l’avertissement afin de vérifier les deux chemins.
5. Lancer un lot avec une carte déjà affichée : elle doit rester dans le viewer.
6. Vider le viewer, si possible dans le scénario de test, puis lancer un lot : le dernier résultat doit remplir le viewer vide.
7. Surveiller tout calcul Statistiques anormalement long et noter le fichier, l’action précédente et la vue active si le problème réapparaît.
