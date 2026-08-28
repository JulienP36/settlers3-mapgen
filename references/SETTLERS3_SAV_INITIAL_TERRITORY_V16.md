# Settlers III SAV — territoire initial d'origine (v1.6)

## Statut

Le masque est maintenant décodé directement dans les SAV immédiats qui portent
la signature native confirmée. La forme canonique historique reste uniquement
une référence d'analyse et n'est jamais utilisée comme repli de rendu.

## Coordonnées de départ d'origine

Un bloc SAV de type 6 contient les données joueurs. La série native de SAV
fournie pour le Data Mapping fixe la structure suivante :

- préfixe : **84 octets** ;
- stride joueur : 328 octets ;
- 20 records de 328 octets ;
- dans un record natif : `+0` = drapeau actif, `+4` = code race/faction
  candidat, `+16` / `+20` = `start_x` / `start_y` ;
- les autres octets restent opaques tant qu'une variation contrôlée ne les
  identifie pas.

Le lecteur conserve aussi la compatibilité d'un ancien fixture synthétique
`96 + 20×328`, mais cette variante n'est pas considérée comme la structure
native observée.

Cette structure permet de retrouver le start d'origine même lorsque le claim runtime a déjà beaucoup évolué.

## Masque initial : état réel du décodage

Analyse historique du corpus natif :

- 145 claims initiaux exploitables de 3500 cellules ;
- chacun possède une bbox 71×71 ;
- après recentrage, les 145 masques sont strictement identiques ;
- masque canonique : 3500 cellules ;
- bord HEX6 : 210 cellules.

Ces observations ont permis de conserver une **reconstruction canonique** de
référence (71 intervalles, 3 500 cellules, bordure de 210 cellules), mais cette
forme n'est pas utilisée pour remplir un fichier.

Le triplet immédiat 4P fourni le 2026-08-28 a identifié le champ natif :

- EDM généré : claim `255` partout ;
- MAP exporté : claim `255` partout ;
- SAV immédiat : type-3, octet `8`, avec les cellules exactes du masque ;
- comptes observés : `P1=3500`, `P2=3500`, `P3=4000`, `P4=4000` ;
- source des départs : type-6, préfixe 84, records de 328 octets.

Le lecteur copie les coordonnées `(x,y)` de chaque cellule directement depuis
l'octet 8. Il publie le masque comme `initial_territory_direct_cells` seulement
si la signature stricte de cette sauvegarde immédiate est présente. Une SAV
plus avancée conserve ses claims runtime exacts mais ne reçoit pas
abusivement l'étiquette « masque initial ».

## Rendu

- Le rendu du contour historique est désactivé lorsqu'aucune cellule native
  directe n'est fournie par le décodeur.
- Les coordonnées de départ restent rendues avec leurs marqueurs ; elles ne
  servent pas à remplir un masque implicite.

## Séparation importante

- **Vue Global** : terrain épuré, sans start ni contour initial depuis v1.8 DEV_4_R1 ;
- **Vue Départs** : contour du territoire **initial** uniquement lorsqu'il est
  calculé à partir des cellules natives directes + sprite joueur central ;
- **Vue Masque initial** : couleurs par joueur sur les cellules natives directes
  du SAV ; sans ces cellules, le fond reste neutre ;
- **Vue Territoires — SAV** : claims **runtime actuels** lus dans le fichier ;
- **Vue Territoires — EDM/MAP** : aucune zone n'est remplie lorsque la source
  ne fournit pas de claims ; aucune reconstruction du masque initial n'est
  présentée comme donnée de la carte.

Les deux informations ne sont plus confondues.
