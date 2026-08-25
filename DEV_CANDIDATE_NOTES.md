# v1.8 DEV_10_R1 — candidate source

Date : 2026-08-25  
Base : DEV_9_R2, preuve Windows autonome clôturée  
Moteur : v1.5 protégé, inchangé

## Objet

Première passe de verrouillage et d’organisation manuelle du Centre d’historique. Le développement revient au ZIP source classique et à `launch_gui`; aucun paquet `.exe` n’est produit pendant DEV_10.

## Principaux changements à vérifier

1. Sélectionner une carte puis utiliser **Verrouiller** : un cadenas `M` apparaît et la carte résiste aux évictions automatiques.
2. Le même bouton devient **Déverrouiller** et retire uniquement la protection manuelle ; V/A/B restent indépendants et combinables.
3. Utiliser `↑` / `↓` : le rang `#`, le tableau et le sélecteur principal suivent le nouvel ordre.
4. Afficher une carte, l’affecter à A/B ou provoquer un hit cache ne doit jamais modifier cet ordre visible.
5. Une nouvelle génération ou un nouvel import apparaît en tête sans déranger l’ordre relatif existant.
6. Suppression et vidage avertissent aussi pour `M`, puis retirent correctement le verrou si l’action est confirmée.
7. Une réduction de capacité inférieure au nombre de cartes protégées V/A/B/M est refusée par une fenêtre traduisible et thémée.
8. Batch tient compte immédiatement des verrous manuels dans sa prévision d’évictions et de résultats non conservés.
9. Vérifier FR/EN, puis changement dynamique DE/ES, ainsi que thèmes clair/sombre dans le Centre.
10. Fermer et rouvrir le programme : ordre et verrous disparaissent normalement, car l’historique reste une mémoire de session.

## Validation automatisée

- 219 tests de régression PASS ;
- tests dédiés à l’indépendance ordre visuel/LRU, aux protections uniques et aux traductions DEV_10 ;
- 49 validations moteur et checksum binaire PASS ;
- cinq hashes protégés inchangés (5/5).

## Hors périmètre

- aucun drag-and-drop des lignes en R1 : boutons accessibles et déterministes d’abord ;
- aucune persistance inter-session de l’historique, de l’ordre ou des cadenas `M` ;
- paquet Windows portable et updater reportés à la phase RC v1.8 ;
- aucun installateur prévu.
