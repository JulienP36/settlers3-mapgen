# v1.8 DEV_7_R3 — États visuels et aperçu Historique

## Périmètre

- colonne compacte `#` : `1` est toujours la carte la plus récente dans l’ordre MRU ;
- compteur `cartes utilisées / capacité` sous la liste ;
- cadenas intégré à la cellule `#` pour toute carte protégée par la vue principale ou A/B ;
- indicateurs accessibles cercle vide / cercle vert coché, plus grands que les anciennes puces ;
- indicateurs synchronisés sur les boutons Afficher/Charger/A/B du header, de Batch et du Centre ;
- format importé affiché dans Détails sous la forme `(.edm)`, `(.map)` ou `(.sav)` ;
- libellé `Slot de comparaison` dans le panneau ;
- zone de miniature de hauteur fixe ;
- clic sur la miniature : grand aperçu déterministe sans bordure ;
- déplacement du grand aperçu, zoom à la molette, position et zoom conservés lors du changement de sélection ;
- remplacement atomique de l’image, synchronisation projection/marqueurs et fermeture avec le Centre ;
- avertissements de suppression et de vidage étendus à la carte actuellement affichée ;
- une carte courante retirée manuellement reste visible, avec un avertissement `hors historique`, jusqu’à son remplacement.

## Garanties

- carte courante et sorties A/B toujours protégées des évictions automatiques ;
- suppression manuelle possible uniquement après avertissement lorsqu’un rôle protégé est concerné ;
- A/B sont libérés après confirmation, sans laisser une comparaison hors historique ;
- historique et statistiques restent limités à la session ;
- moteur de génération v1.5, formats binaires et rendu déterministe inchangés ;
- aucune publication sur `dev` avant validation Windows.

## Validation interne

- 168 tests de régression PASS ;
- 49 validations moteur PASS ;
- checksum binaire PASS ;
- cinq hashes protégés inchangés.

## Checklist Windows

1. Vérifier `#1` pour la carte la plus récente et le compteur utilisé/capacité après génération, Batch, import, chargement et suppression.
2. Vérifier les cadenas pour la carte affichée et A/B, y compris les rôles cumulés.
3. Sélectionner plusieurs lignes et contrôler les coches Afficher/A/B ; faire de même avec Charger dans le header et Afficher/A/B dans Batch.
4. Vérifier les extensions importées `(.edm)`, `(.map)` et `(.sav)`.
5. Ouvrir le grand aperçu, le déplacer, zoomer, changer de ligne puis projection et taille des marqueurs ; position et zoom doivent rester stables.
6. Vérifier que l’image miniature ne remonte pas lorsque le panneau gagne ou perd une ligne d’information.
7. Supprimer une carte A/B, puis une carte affichée : annuler et confirmer chaque avertissement.
8. Après suppression de la carte affichée, contrôler le panneau d’avertissement hors historique puis sa disparition au prochain chargement.
9. Utiliser Tout vider avec des cartes protégées et vérifier A/B, viewer principal et message explicatif.
10. Refaire les contrôles essentiels en clair/sombre et FR/EN/DE/ES.
