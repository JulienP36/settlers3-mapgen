# Settlers III — audit Legacy des ressources et objets proches des départs

> Première tranche du point 3 de la v2.0 : 16 SAV natifs 768×768 (8 cartes 2 joueurs et 8 cartes 20 joueurs), analysés le 2026-08-30T11:02:58+00:00.
> L’analyse est en lecture seule. Elle ne modifie pas le générateur et ne mélange pas les règles Upgraded.

## Méthode et limites

- Les minerais et poissons sont lus dans le byte 17 de chaque cellule type 3. Les minerais utilisent les familles haut-nibble `0x10` à `0x50`; un poisson est retenu seulement pour un low-nibble non nul sur les terrains Water 0..7.
- Les objets sont séparés en deux représentations : byte 14 (`static`) pour le décor initial de la carte, byte 7 (`runtime`) pour l’état courant du SAV. Les distances et densités de placement utilisent d’abord byte 14.
- Les distances sont des distances HEX6 exactes. L’empreinte nominale de départ est la constante validée de 33 cellules ; elle ne constitue pas à elle seule la hitbox complète d’un bâtiment ou d’un objet.
- La proximité d’un objet est une observation géométrique, pas une preuve d’accessibilité ou d’absence de collision. Le byte 4 décrit la hauteur dans le SAV ; le byte 9 reste inconnu et n’est donc pas utilisé comme indice de hitbox. Les empreintes de collision complètes restent à calibrer dans le jeu/éditeur.

## Corpus et intégrité

16 SAV analysés, 176 départs décodés depuis les blocs type 6, checksum valide pour 16/16 fichiers.

| Carte | Groupe | Joueurs | Départs | Taille SAV | Checksum | Fichier |
|---|---:|---:|---:|---:|---|---|
| `sav_001` | 2p | 2 | 2 | 18 217 620 octets | OK | `8 maps 768 2 joueurs.zip::768 2 joueurs (1).sav` |
| `sav_002` | 2p | 2 | 2 | 18 215 928 octets | OK | `8 maps 768 2 joueurs.zip::768 2 joueurs (2).sav` |
| `sav_003` | 2p | 2 | 2 | 18 213 652 octets | OK | `8 maps 768 2 joueurs.zip::768 2 joueurs (3).sav` |
| `sav_004` | 2p | 2 | 2 | 18 216 168 octets | OK | `8 maps 768 2 joueurs.zip::768 2 joueurs (4).sav` |
| `sav_005` | 2p | 2 | 2 | 18 215 020 octets | OK | `8 maps 768 2 joueurs.zip::768 2 joueurs (5).sav` |
| `sav_006` | 2p | 2 | 2 | 18 214 502 octets | OK | `8 maps 768 2 joueurs.zip::768 2 joueurs (6).sav` |
| `sav_007` | 2p | 2 | 2 | 18 215 296 octets | OK | `8 maps 768 2 joueurs.zip::768 2 joueurs (7).sav` |
| `sav_008` | 2p | 2 | 2 | 18 215 594 octets | OK | `8 maps 768 2 joueurs.zip::768 2 joueurs (8).sav` |
| `sav_009` | 20p | 20 | 20 | 18 783 070 octets | OK | `8 maps 768 20 joueurs.zip::768 20 joueurs (1).sav` |
| `sav_010` | 20p | 20 | 20 | 18 782 650 octets | OK | `8 maps 768 20 joueurs.zip::768 20 joueurs (2).sav` |
| `sav_011` | 20p | 20 | 20 | 18 783 010 octets | OK | `8 maps 768 20 joueurs.zip::768 20 joueurs (3).sav` |
| `sav_012` | 20p | 20 | 20 | 18 782 406 octets | OK | `8 maps 768 20 joueurs.zip::768 20 joueurs (4).sav` |
| `sav_013` | 20p | 20 | 20 | 18 784 768 octets | OK | `8 maps 768 20 joueurs.zip::768 20 joueurs (5).sav` |
| `sav_014` | 20p | 20 | 20 | 18 782 420 octets | OK | `8 maps 768 20 joueurs.zip::768 20 joueurs (6).sav` |
| `sav_015` | 20p | 20 | 20 | 18 782 912 octets | OK | `8 maps 768 20 joueurs.zip::768 20 joueurs (7).sav` |
| `sav_016` | 20p | 20 | 20 | 18 789 562 octets | OK | `8 maps 768 20 joueurs.zip::768 20 joueurs (8).sav` |

## Ressources Legacy — mesures globales

Les lignes `minerals` sont l’union des cinq familles et ne doivent pas être additionnées aux lignes de minerais individuels. Les valeurs de cellules sont des cellules portant un code de ressource, tandis que `stock` additionne les low-nibbles.

| Groupe | Famille | Cellules médianes/carte | Stock médian/carte | % moyen carte | Composantes médianes | Taille composante médiane | Quantité moyenne | Hors support attendu |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2p | `coal` | 20180.50 | 161214.00 | 3.421 % | 1176.5 | 2.0 | 8.00 | 0 |
| 2p | `iron` | 8633.50 | 68903.00 | 1.464 % | 519.5 | 3.0 | 7.97 | 0 |
| 2p | `gold` | 5731.00 | 45607.00 | 0.972 % | 289.0 | 5.0 | 8.00 | 0 |
| 2p | `gems` | 2092.50 | 16513.00 | 0.355 % | 103.5 | 7.0 | 7.98 | 0 |
| 2p | `sulfur` | 3219.50 | 25343.50 | 0.546 % | 136.5 | 11.8 | 7.94 | 0 |
| 2p | `minerals` | 39937.00 | 318893.50 | 6.771 % | 481.5 | 3.0 | 7.99 | 0 |
| 2p | `fish` | 46071.00 | 362478.00 | 7.811 % | 8822.0 | 2.0 | 7.86 | 0 |
| 20p | `coal` | 20291.00 | 161725.50 | 3.440 % | 1212.5 | 2.0 | 8.00 | 0 |
| 20p | `iron` | 8739.00 | 69509.00 | 1.482 % | 532.5 | 3.0 | 7.99 | 0 |
| 20p | `gold` | 6054.00 | 48568.00 | 1.026 % | 319.0 | 5.0 | 8.00 | 0 |
| 20p | `gems` | 2085.00 | 16740.50 | 0.353 % | 115.0 | 5.5 | 8.02 | 0 |
| 20p | `sulfur` | 2892.00 | 23061.50 | 0.490 % | 150.5 | 7.0 | 7.99 | 0 |
| 20p | `minerals` | 39935.50 | 320330.00 | 6.771 % | 506.0 | 3.0 | 8.00 | 0 |
| 20p | `fish` | 43736.50 | 343577.50 | 7.415 % | 8400.5 | 2.0 | 7.87 | 0 |

### Répartition des quantités

Le low-nibble est détaillé dans `resource_families.csv` et `resource_per_map.csv`. Sur cette tranche, la moyenne reste proche de 8 unités par cellule codée ; il n’y a pas de signal justifiant une quantité systématiquement dépendante de la famille.

| Groupe | Famille | Min–max quantité | Médiane pooled | Moyenne pooled |
|---|---|---:|---:|---:|
| 2p | `coal` | 1–15 | 8.0 | 8.0 |
| 2p | `iron` | 1–15 | 8.0 | 8.0 |
| 2p | `gold` | 1–15 | 8.0 | 8.0 |
| 2p | `gems` | 1–15 | 8.0 | 8.0 |
| 2p | `sulfur` | 1–15 | 8.0 | 7.9 |
| 2p | `fish` | 1–15 | 8.0 | 7.9 |
| 20p | `coal` | 1–15 | 8.0 | 8.0 |
| 20p | `iron` | 1–15 | 8.0 | 8.0 |
| 20p | `gold` | 1–15 | 8.0 | 8.0 |
| 20p | `gems` | 1–15 | 8.0 | 8.0 |
| 20p | `sulfur` | 1–15 | 8.0 | 8.0 |
| 20p | `fish` | 1–15 | 8.0 | 7.9 |

## Ressources autour des départs

Les rayons sont mesurés à partir de chaque départ, puis résumés par médiane sur tous les départs du groupe.

| Groupe | Famille | Plus proche médian | r10 cellules | r25 cellules | r50 cellules | r100 cellules | r100 stock |
|---|---|---:|---:|---:|---:|---:|---:|
| 2p | `minerals` | 42.5 hex | 0.0 | 0.0 | 83.5 | 2644.0 | 21000.0 |
| 2p | `fish` | 35.5 hex | 0.0 | 0.0 | 39.0 | 463.5 | 3636.0 |
| 20p | `minerals` | 29.0 hex | 0.0 | 0.0 | 334.0 | 2449.0 | 19666.0 |
| 20p | `fish` | 38.0 hex | 0.0 | 0.0 | 38.0 | 746.5 | 6054.5 |

- Observation nette : les médianes à `r10` et `r25` sont nulles pour les minerais et les poissons dans les deux groupes. La ressource n’est donc pas posée au voisinage immédiat des starts dans cette tranche.
- Cela ne signifie pas qu’un rayon dur universel est démontré : la distance du premier minerai varie fortement entre 2P et 20P, et la disponibilité locale dépend du relief/eau généré.

## Objets — inventaire et séparation statique/runtime

Le tableau complet par ID et terrain support est dans `objects_per_map.csv`. Le byte 9 est exporté séparément comme champ encore inconnu ; il n’est pas interprété comme accessibilité.

| Groupe | Représentation | IDs observés | Cellules totales | Différence exacte byte14/byte7 | Différence présence |
|---|---|---:|---:|---:|---:|
| 2p | `static` | 93 | 45 970 | 144 | 143 |
| 2p | `runtime` | 96 | 46 109 | 0 | 0 |
| 20p | `static` | 92 | 46 016 | 2 506 | 2 493 |
| 20p | `runtime` | 95 | 48 479 | 0 | 0 |
- Le nombre d’IDs est un inventaire, pas une preuve que chaque ID a la même règle de collision. Les différences runtime sont concentrées dans les valeurs de cycle/overlay (notamment 112/113/255 selon les cartes) ; byte 14 reste la base de reproduction du décor initial.

## Proximité des objets aux starts

### Première présence du décor

La distance est mesurée depuis l’ancre du start vers la cellule d’objet statique la plus proche. `r≤14` compte toutes les cellules d’objets statiques 1..127 dans ce rayon.

| Groupe | Starts | Premier objet médian | Cellules dans r≤14 médianes | Cellules dans l’empreinte nominale |
|---|---:|---:|---:|---:|
| 2p | 16 | 3.5 hex | 10.5 | 6 |
| 20p | 160 | 5.0 hex | 9.5 | 26 |

### Densité locale comparée à la densité globale

`world_decor` désigne ici les IDs statiques 1..127 non nuls. La densité locale est calculée dans le rayon HEX6 indiqué, après correction des bords de carte.

| Groupe | Représentation | Densité globale médiane /1000 cellules | r10 | r25 | r50 | r100 |
|---|---|---:|---:|---:|---:|---:|
| 2p | `static` | 9.70 | 16.62 | 15.63 | 15.68 | 12.44 |
| 2p | `runtime` | 9.73 | 19.64 | 18.20 | 16.27 | 12.49 |
| 20p | `static` | 9.79 | 12.08 | 16.40 | 14.38 | 11.18 |
| 20p | `runtime` | 10.33 | 21.15 | 22.55 | 16.34 | 11.88 |

La densité autour des starts n’est pas inférieure à la densité globale : il n’y a donc pas d’évidence d’une zone stérile fixe de 14 hex dans le décor statique. La marge de sécurité actuelle du générateur est probablement trop restrictive pour reproduire l’apparence native, mais sa réduction doit attendre une mesure de hitbox/occupation dans le jeu.

### Résumé par famille statique

`IDs ≤5` et `IDs >14` indiquent respectivement les variantes dont au moins une cellule atteint cette distance dans le groupe. L’éloignement peut venir du terrain support ou du biome ; il n’est pas assimilé à une règle de réservation des starts.

| Groupe | Famille | IDs présents | IDs ≤5 hex | IDs >14 hex | Plus proche | Empreinte nominale |
|---|---|---:|---|---|---:|---:|
| 2p | `adult_tree` | 12 | 69,73,74,80,81 | — | 3 | 0 |
| 2p | `big_stone` | 8 | 7 | 2,4,6,8 | 2 | 1 |
| 2p | `border_stone` | 8 | 18 | 13,14,16,17,19,20 | 5 | 0 |
| 2p | `building_stone` | 13 | 119,120,123 | — | 4 | 0 |
| 2p | `bush` | 5 | 58 | 59,60 | 2 | 1 |
| 2p | `cactus` | 4 | — | 45,46,47,48 | 34 | 0 |
| 2p | `dead_tree` | 2 | — | 43,44 | 88 | 0 |
| 2p | `decorative_stone` | 4 | 12 | 9 | 2 | 1 |
| 2p | `grave` | 1 | — | — | 12 | 0 |
| 2p | `palm` | 2 | — | 78,79 | 32 | 0 |
| 2p | `reed` | 5 | — | 62,63,64,65,66 | 24 | 0 |
| 2p | `skeleton` | 1 | — | 49 | 86 | 0 |
| 2p | `small_bush` | 4 | 55 | 56 | 3 | 1 |
| 2p | `small_flower` | 3 | — | 52 | 7 | 0 |
| 2p | `small_plant` | 3 | 37 | 35,36 | 3 | 1 |
| 2p | `small_stone` | 8 | — | 23,24,27 | 9 | 0 |
| 2p | `stump` | 2 | 42 | 41 | 4 | 0 |
| 2p | `toadstool` | 3 | 39 | 38,40 | 2 | 1 |
| 2p | `wreck` | 5 | — | 29,30,31,32,33 | 15 | 0 |
| 20p | `adult_tree` | 12 | 68,69,70,71,72,73,74,75,76,77,80,81 | — | 4 | 0 |
| 20p | `big_stone` | 8 | 1,2,3,4,5,6,7,8 | — | 1 | 4 |
| 20p | `border_stone` | 8 | 14,15,18 | — | 5 | 0 |
| 20p | `building_stone` | 13 | 115,116,117,119,120,123,124,126,127 | — | 1 | 1 |
| 20p | `bush` | 5 | 57,58,59,60,61 | — | 3 | 2 |
| 20p | `cactus` | 4 | — | 45,46,47,48 | 18 | 0 |
| 20p | `dead_tree` | 2 | — | 43,44 | 17 | 0 |
| 20p | `decorative_stone` | 4 | 10,11 | — | 2 | 2 |
| 20p | `grave` | 1 | — | — | 6 | 0 |
| 20p | `palm` | 2 | — | — | 12 | 0 |
| 20p | `reed` | 4 | — | 62,65,67 | 14 | 0 |
| 20p | `skeleton` | 1 | — | 49 | 28 | 0 |
| 20p | `small_bush` | 4 | 53,54,56 | — | 1 | 4 |
| 20p | `small_flower` | 3 | 51,52 | — | 2 | 2 |
| 20p | `small_plant` | 3 | 35,36,37 | — | 2 | 2 |
| 20p | `small_stone` | 8 | 21,22,23,24,25,26 | — | 1 | 6 |
| 20p | `stump` | 2 | 41 | — | 4 | 0 |
| 20p | `toadstool` | 3 | 38,39,40 | — | 2 | 3 |
| 20p | `wreck` | 5 | — | 29,30,31,32,33 | 35 | 0 |

### IDs observés très près des starts

Les IDs ci-dessous ont au moins une occurrence à cinq hex ou moins dans le corpus du groupe. La colonne `empreinte` compte les occurrences dans la fenêtre nominale validée de 33 cellules autour d’un start.

| Groupe | ID | Nom | Famille | Plus proche | Starts ≤2 | Starts ≤5 | Empreinte nominale |
|---|---:|---|---|---:|---:|---:|---:|
| 2p | 7 | Big Stone 7 | `big_stone` | 2 | 1 | 1 | 1 |
| 2p | 12 | Decorative Stone 4 | `decorative_stone` | 2 | 1 | 1 | 1 |
| 2p | 39 | Toadstool 2 | `toadstool` | 2 | 1 | 1 | 1 |
| 2p | 58 | Bush 2 | `bush` | 2 | 1 | 1 | 1 |
| 2p | 37 | Small Plant 3 | `small_plant` | 3 | 0 | 1 | 1 |
| 2p | 55 | Small Bush 3 | `small_bush` | 3 | 0 | 1 | 1 |
| 2p | 74 | Adult Tree 7 | `adult_tree` | 3 | 0 | 1 | 0 |
| 2p | 81 | Adult Tree 14 | `adult_tree` | 3 | 0 | 1 | 0 |
| 2p | 42 | Tree Stump 2 | `stump` | 4 | 0 | 1 | 0 |
| 2p | 69 | Birch 2 | `adult_tree` | 4 | 0 | 2 | 0 |
| 2p | 80 | Adult Tree 13 | `adult_tree` | 4 | 0 | 2 | 0 |
| 2p | 119 | Building Stone 5 | `building_stone` | 4 | 0 | 1 | 0 |
| 2p | 18 | Border Stone 6 | `border_stone` | 5 | 0 | 1 | 0 |
| 2p | 73 | Adult Tree 6 | `adult_tree` | 5 | 0 | 1 | 0 |
| 2p | 120 | Building Stone 6 | `building_stone` | 5 | 0 | 1 | 0 |
| 2p | 123 | Building Stone 9 | `building_stone` | 5 | 0 | 1 | 0 |
| 20p | 2 | Big Stone 2 | `big_stone` | 1 | 1 | 1 | 1 |
| 20p | 8 | Big Stone 8 | `big_stone` | 1 | 2 | 4 | 3 |
| 20p | 21 | Small Stone 1 | `small_stone` | 1 | 1 | 2 | 1 |
| 20p | 56 | Small Bush 4 | `small_bush` | 1 | 3 | 4 | 3 |
| 20p | 127 | Building Stone 13 | `building_stone` | 1 | 1 | 1 | 1 |
| 20p | 10 | Decorative Stone 2 | `decorative_stone` | 2 | 2 | 3 | 2 |
| 20p | 24 | Small Stone 4 | `small_stone` | 2 | 1 | 1 | 1 |
| 20p | 25 | Small Stone 5 | `small_stone` | 2 | 2 | 2 | 2 |
| 20p | 26 | Small Stone 6 | `small_stone` | 2 | 1 | 2 | 1 |
| 20p | 35 | Small Plant 1 | `small_plant` | 2 | 1 | 2 | 1 |
| 20p | 38 | Toadstool 1 | `toadstool` | 2 | 1 | 1 | 1 |
| 20p | 40 | Toadstool 3 | `toadstool` | 2 | 2 | 4 | 2 |
| 20p | 51 | Small Flower 2 | `small_flower` | 2 | 1 | 2 | 2 |
| 20p | 5 | Big Stone 5 | `big_stone` | 3 | 0 | 3 | 0 |
| 20p | 7 | Big Stone 7 | `big_stone` | 3 | 0 | 3 | 0 |
| 20p | 22 | Small Stone 2 | `small_stone` | 3 | 0 | 2 | 1 |
| 20p | 37 | Small Plant 3 | `small_plant` | 3 | 0 | 2 | 1 |
| 20p | 52 | Small Flower 3 | `small_flower` | 3 | 0 | 1 | 0 |
| 20p | 53 | Small Bush 1 | `small_bush` | 3 | 0 | 2 | 0 |
| 20p | 54 | Small Bush 2 | `small_bush` | 3 | 0 | 1 | 1 |
| 20p | 57 | Bush 1 | `bush` | 3 | 0 | 1 | 1 |
| 20p | 58 | Bush 2 | `bush` | 3 | 0 | 1 | 1 |
| 20p | 4 | Big Stone 4 | `big_stone` | 4 | 0 | 5 | 0 |
| 20p | 11 | Decorative Stone 3 | `decorative_stone` | 4 | 0 | 3 | 0 |

### Lecture hitbox / objets décoratifs

- Dans la fenêtre nominale de 33 cellules, le corpus contient 6 cellules d’objets statiques pour les 16 starts 2P et 26 cellules pour les 160 starts 20P. Elles sont principalement constituées de petites pierres, plantes, champignons et buissons ; aucun arbre adulte n’y apparaît.
- Le byte 9 est conservé dans les CSV comme champ encore inconnu ; il ne signifie ni « bloquant » ni « sans hitbox ».
- Quelques objets plus volumineux ou potentiellement bloquants apparaissent néanmoins à très faible distance dans le byte 14. Cela interdit de conclure que toute décoration proche est sans hitbox : la cellule d’ancrage et l’empreinte réelle peuvent différer, et le byte 9 ne permet pas encore de trancher.
- Les familles très éloignées dans cette tranche sont surtout les roseaux, épaves, cactus, arbres morts, squelettes et palmiers. Leur éloignement est compatible avec des contraintes de biome/terrain support ; il ne permet pas d’isoler une règle de distance aux starts.
- Conclusion opérationnelle : distinguer les familles décoratives et les arbres dans le placement peut être pertinent, mais la règle ne doit pas être figée comme « sans hitbox » avant calibration contrôlée.

## Conclusion pour le générateur

1. Conserver la chaîne terrain → supports → ressources/objets ; byte 17 est directement exploitable pour calibrer les ressources Legacy.
2. Générer le décor initial depuis la représentation statique byte 14 et traiter byte 7 comme une observation runtime, jamais comme une vérité de placement initial.
3. Ne pas imposer un halo objet vide de 14 hex autour des starts. La reproduction visuelle devra autoriser des petits décors proches, sous réserve de la validation d’occupation réelle.
4. Ne pas retoucher encore les quotas Legacy à partir de cette seule tranche : les 16 cartes donnent une bonne base 768×768, mais les tailles plus petites et les cartes jouées doivent rester séparées.

## Sorties détaillées

- `native_resource_object_audit_16_768_2p20p.json` : corpus, mesures par carte et agrégats sans duplication des cellules.
- `native_resource_object_audit_16_768_2p20p_manifest.json` : provenance, hashes et méthode.
- `native_resource_object_audit_16_768_2p20p_resources_per_map.csv` et `_resource_families.csv` : ressources par carte et agrégats 2P/20P.
- `native_resource_object_audit_16_768_2p20p_resource_components.csv` : une ligne par composante HEX6 de ressource.
- `native_resource_object_audit_16_768_2p20p_resource_cells_partNN.csv` : table exhaustive de chaque cellule ressource physique, sans doublon d’agrégat `minerals`, scindée en parties de 500 000 lignes de données avec en-tête répété.
- `native_resource_object_audit_16_768_2p20p_objects_per_map.csv` : inventaire statique/runtime par ID et terrains supports.
- `native_resource_object_audit_16_768_2p20p_object_start_proximity.csv` : distances et comptes par ID et par start.
- `native_resource_object_audit_16_768_2p20p_object_proximity_aggregate.csv` et `_object_family_proximity.csv` : synthèses par ID/famille.
- `native_resource_object_audit_16_768_2p20p_object_start_overview.csv`, `_object_start_local.csv` et `_object_runtime_differences.csv` : fenêtres nominales, densités locales et différences byte14/byte7.
