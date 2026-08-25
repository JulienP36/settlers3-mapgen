# v1.8 DEV_10 — completed development checkpoint

Date : 2026-08-25  
Base : DEV_9_R2, preuve Windows autonome clôturée  
Moteur : v1.5 protégé, inchangé

## Objet

Version complétée du verrouillage manuel et de l’organisation du Centre d’historique. Le développement reste sur le ZIP source classique et `launch_gui`; aucun paquet `.exe` n’est produit pendant DEV_10.

## Principaux changements à vérifier

1. Remplir le cache puis protéger toutes ses cartes avec V/A/B/M ; une génération ou un import supplémentaire reste affiché mais ne crée jamais de neuvième place dans un cache de huit.
2. Répéter l’opération et modifier les verrous : la capacité reste strictement fixe, sans croissance progressive possible.
3. Laisser une ancienne carte non protégée puis générer/importer : cette ancienne carte est évincée et le nouveau résultat est bien conservé.
4. Quand un résultat n’est pas conservé, vérifier le message dynamique FR/EN/DE/ES et le triangle de 20 px placé à côté de **Vue**.
5. Dans le Centre, le rang `#` possède sa propre colonne et les protections V/A/B/M restent lisibles dans une bande distincte, y compris à trois ou quatre rôles.
6. Vérifier que le prévisionnel Batch annonce toujours correctement les résultats non conservés selon la même règle.
7. Rejouer rapidement verrouillage/déverrouillage, déplacement, suppression, vidage et réduction de capacité de R1.

## Validation automatisée

- 223 tests de régression PASS ;
- tests dédiés à l’indépendance ordre visuel/LRU, à la capacité dure, aux protections uniques et aux traductions DEV_10 ;
- 49 validations moteur et checksum binaire PASS ;
- cinq hashes protégés inchangés (5/5).

## Hors périmètre

- aucun drag-and-drop des lignes en R1 : boutons accessibles et déterministes d’abord ;
- aucune persistance inter-session de l’historique, de l’ordre ou des cadenas `M` ;
- paquet Windows portable et updater reportés à la phase RC v1.8 ;
- aucun installateur prévu.
