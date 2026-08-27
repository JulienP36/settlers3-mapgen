# Settlers III SAV — territoire initial d'origine (v1.6)

## Statut

Implémenté dans v1.6 pour l'affichage déterministe des starts/territoires initiaux lors d'un import SAV v11.

## Coordonnées de départ d'origine

Un bloc SAV de type 6 contient les données joueurs :

- préfixe : 96 octets ;
- stride joueur : 328 octets ;
- début de chaque record actif : `<III>` = `player_id`, `start_x`, `start_y` ;
- records actifs continus à partir du joueur 0 ;
- maximum pratique : 20 joueurs.

Cette structure permet de retrouver le start d'origine même lorsque le claim runtime a déjà beaucoup évolué.

## Masque initial canonique

Analyse du corpus natif :

- 145 claims initiaux exploitables de 3500 cellules ;
- chacun possède une bbox 71×71 ;
- après recentrage, les 145 masques sont strictement identiques ;
- masque canonique : 3500 cellules ;
- bord HEX6 : 210 cellules.

Le masque exact est encodé dans `s3mapgen/application/rendering/preview.py` par 71 intervalles de lignes autour du start.

## Rendu

- projection carrée : trajectoire du contour sur les vraies cellules ;
- projection parallélogramme : même trajectoire projetée avec la carte ;
- depuis v1.8 DEV_4_R4, exactement 210 marqueurs J1–J20 minimaux sans chevauchement, un par cellule de cette trajectoire exacte ;
- opacité 0–100 % appliquée seulement aux marqueurs centraux et frontaliers, jamais au terrain sous-jacent ;
- wrap-around de map géré par modulo pour les starts proches d'un bord.

## Séparation importante

- **Vue Global** : terrain épuré, sans start ni contour initial depuis v1.8 DEV_4_R1 ;
- **Vue Départs** : contour du territoire **initial** autour du start d'origine + sprite joueur central ;
- **Vue Territoires — SAV** : claims **runtime actuels** lus dans le fichier ;
- **Vue Territoires — EDM/MAP** : reconstruction d'affichage du masque initial exact autour des starts, sans claim runtime prétendument lu dans le fichier.

Les deux informations ne sont plus confondues.
