# Settlers III SAV — territoire initial d'origine (v1.6)

## Statut

Implémenté dans v1.6 pour l'affichage déterministe des starts/territoires initiaux lors d'un import SAV v11.

## Coordonnées de départ d'origine

Un bloc SAV de type 6 contient les données joueurs : préfixe 96 octets ; stride joueur 328 octets ; début de record actif `<III>` = `player_id`, `start_x`, `start_y` ; records actifs continus à partir du joueur 0 ; maximum pratique 20 joueurs.

## Masque initial canonique

Analyse du corpus natif : 145 claims initiaux exploitables de 3500 cellules, bbox 71×71, tous strictement identiques après recentrage ; bord HEX6 210 cellules.

Le masque exact est encodé dans `s3mapgen/preview.py` par 71 intervalles autour du start.

## Séparation importante

- Vue Global : contour du territoire initial autour du start d'origine.
- Vue Territoires : claims runtime actuels du SAV.
