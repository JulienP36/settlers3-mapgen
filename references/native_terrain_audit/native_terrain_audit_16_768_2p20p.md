# Settlers III — audit des terrains natifs SAV 768 (2P/20P)

> Première tranche du point 1 de la v2.0. Analyse en lecture seule des 16 SAV fournis le 29 août 2026 : 8 cartes à 2 joueurs et 8 cartes à 20 joueurs.
> Ce document ne modifie pas le générateur. Les objets, les joueurs en profondeur et les ressources seront traités dans les phases suivantes.

## Méthode et limites

- Exécution : `2026-08-30T00:56:42+00:00` ; 16 SAV, tous traités individuellement.
- Terrain brut : byte 6 runtime tel qu'enregistré. Terrain normalisé : remplacement analytique de `28 → 16` pour isoler le terrain de départ ajouté par le runtime.
- L'ID 28 est aussi décrit séparément par composantes dans le CSV (`representation=raw_runtime`) afin de conserver sa forme runtime sans la mélanger à l'herbe.
- Composantes, périmètres, voisinages et distances : topologie HEX6 confirmée `(+1,0), (-1,0), (0,+1), (0,-1), (+1,+1), (-1,-1)`.
- Les formes mesurées ici sont géométriques (cellules, composantes, périmètres, bounding boxes, compacité, allongement). La texture graphique exacte doit rester corrélée plus tard aux EDM/MAP/PNG.
- Les tableaux complets, y compris chaque composante, sont dans les CSV/JSON du même dossier.

## Corpus

| Carte | Groupe | Joueurs décodés | Départs | Taille SAV | Checksum | Fichier |
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

## Tous les IDs de terrain bruts présents

`28` est conservé ici : il ne doit pas être oublié dans l'inventaire, même s'il est normalisé en 16 pour les comparaisons statiques.

| ID | Nom actuel | Cartes | Total cellules | Moyenne/carte | Min–max/carte | % moyen carte |
|---:|---|---:|---:|---:|---:|---:|
| 0 | Water 1 | 16/16 | 152,331 | 9520.69 | 7,647–10,619 | 1.614 % |
| 1 | Water 2 | 16/16 | 139,910 | 8744.38 | 7,165–9,963 | 1.483 % |
| 2 | Water 3 | 16/16 | 126,763 | 7922.69 | 6,698–8,993 | 1.343 % |
| 3 | Water 4 | 16/16 | 115,613 | 7225.81 | 6,188–8,228 | 1.225 % |
| 4 | Water 5 | 16/16 | 105,201 | 6575.06 | 5,656–7,435 | 1.115 % |
| 5 | Water 6 | 16/16 | 96,557 | 6034.81 | 5,302–6,704 | 1.023 % |
| 6 | Water 7 | 16/16 | 88,839 | 5552.44 | 4,988–6,045 | 0.941 % |
| 7 | Water 8 | 16/16 | 1,161,776 | 72611.00 | 67,025–78,746 | 12.311 % |
| 16 | Grass | 16/16 | 4,991,587 | 311974.19 | 303,399–326,462 | 52.893 % |
| 17 | Rock transition 1 | 16/16 | 118,095 | 7380.94 | 6,111–8,548 | 1.251 % |
| 18 | Grass detail 1 | 16/16 | 2,028 | 126.75 | 101–157 | 0.021 % |
| 19 | Grass detail 2 | 16/16 | 1,932 | 120.75 | 91–153 | 0.020 % |
| 20 | Grass/desert transition | 16/16 | 96,815 | 6050.94 | 5,272–6,800 | 1.026 % |
| 21 | Grass/swamp transition | 16/16 | 27,066 | 1691.62 | 1,119–2,234 | 0.287 % |
| 23 | Mud | 16/16 | 28,691 | 1793.19 | 1,329–2,581 | 0.304 % |
| 24 | Dry grass | 16/16 | 209,138 | 13071.12 | 9,666–15,952 | 2.216 % |
| 28 | Runtime start-area terrain | 16/16 | 5,538 | 346.12 | 54–644 | 0.059 % |
| 32 | Rocky core | 16/16 | 886,660 | 55416.25 | 52,832–58,769 | 9.395 % |
| 33 | Rock transition 2 | 16/16 | 102,018 | 6376.12 | 5,272–7,148 | 1.081 % |
| 34 | Rocky detail | 16/16 | 394 | 24.62 | 10–39 | 0.004 % |
| 35 | Rock/snow transition | 16/16 | 38,498 | 2406.12 | 2,034–2,732 | 0.408 % |
| 48 | Shore | 16/16 | 336,642 | 21040.12 | 16,467–23,376 | 3.567 % |
| 64 | Desert core | 16/16 | 179,356 | 11209.75 | 8,104–14,353 | 1.901 % |
| 65 | Desert transition | 16/16 | 58,838 | 3677.38 | 3,225–4,223 | 0.623 % |
| 80 | Swamp core | 16/16 | 1,729 | 108.06 | 23–175 | 0.018 % |
| 81 | Swamp transition | 16/16 | 6,572 | 410.75 | 234–569 | 0.070 % |
| 96 | River 1 | 16/16 | 126,328 | 7895.50 | 6,428–10,415 | 1.339 % |
| 97 | River 2 | 16/16 | 24,094 | 1505.88 | 1,007–2,105 | 0.255 % |
| 98 | River 3 | 16/16 | 4,082 | 255.12 | 133–403 | 0.043 % |
| 99 | River 4 | 16/16 | 1,014 | 63.38 | 17–115 | 0.011 % |
| 128 | Snow core | 16/16 | 155,635 | 9727.19 | 8,942–10,409 | 1.649 % |
| 129 | Snow transition | 16/16 | 30,581 | 1911.31 | 1,699–2,167 | 0.324 % |
| 144 | Mud transition 1 | 16/16 | 6,495 | 405.94 | 193–864 | 0.069 % |
| 145 | Mud transition 2 | 16/16 | 10,368 | 648.00 | 403–1,063 | 0.110 % |

## Cas particulier du terrain runtime 28

L'ID 28 est un état ajouté autour des départs par le runtime. Sa géométrie brute est conservée séparément ; elle ne doit pas être traitée comme une nouvelle famille géographique.

| Groupe | Cartes | Cellules moyennes | Cellules moyennes par départ | Min–max total | Composantes moyennes |
|---|---:|---:|---:|---:|---:|
| 2p | 8 | 63.62 | 31.81 | 54–66 | 2.0 |
| 20p | 8 | 628.62 | 31.43 | 616–644 | 20.1 |
- Les deux premières cartes 2P sont des cas à surveiller (`54` et `59` cellules 28 au total) ; les autres cartes 2P sont à `66`, tandis que les cartes 20P restent proches de 20 × 33 cellules. Cette anomalie est conservée pour l'analyse joueurs/runtime et n'est pas corrigée ici.

## IDs normalisés — forme, position et relief

Les métriques de forme sont calculées sur les composantes HEX6 de chaque ID exact. Les métriques `when_present` ne prennent en compte que les cartes où l'ID apparaît.

| ID | Nom | Moy. cellules | % terre moyen | Composantes moy. | Médiane composante | P90 composante | Allongement médian | Bord moyen | Eau adjacente moyenne | Distance eau médiane |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | Water 1 | 9520.69 | 0.000 % | 208.1 | 25.0 | 123.3 | 3.14 | 0.0 % | 99.8 % | 0.0 |
| 1 | Water 2 | 8744.38 | 0.000 % | 92.1 | 33.0 | 259.4 | 2.47 | 0.0 % | 100.0 % | 0.0 |
| 2 | Water 3 | 7922.69 | 0.000 % | 57.5 | 31.0 | 206.7 | 2.26 | 0.0 % | 100.0 % | 0.0 |
| 3 | Water 4 | 7225.81 | 0.000 % | 44.0 | 28.5 | 169.0 | 2.25 | 0.0 % | 100.0 % | 0.0 |
| 4 | Water 5 | 6575.06 | 0.000 % | 38.0 | 28.8 | 146.9 | 2.28 | 0.0 % | 100.0 % | 0.0 |
| 5 | Water 6 | 6034.81 | 0.000 % | 31.1 | 32.0 | 120.0 | 2.34 | 0.0 % | 100.0 % | 0.0 |
| 6 | Water 7 | 5552.44 | 0.000 % | 27.9 | 31.2 | 105.8 | 2.21 | 0.0 % | 100.0 % | 0.0 |
| 7 | Water 8 | 72611.00 | 0.000 % | 24.1 | 38.8 | 395.4 | 2.40 | 4.2 % | 100.0 % | 0.0 |
| 16 | Grass | 312320.31 | 67.071 % | 95.8 | 2.0 | 53.5 | 1.72 | 0.0 % | 0.0 % | 26.5 |
| 17 | Rock transition 1 | 7380.94 | 1.585 % | 69.6 | 7.2 | 242.8 | 1.73 | 0.0 % | 0.0 % | 52.5 |
| 18 | Grass detail 1 | 126.75 | 0.027 % | 126.8 | 1.0 | 1.0 | 1.00 | 0.0 % | 0.0 % | 29.5 |
| 19 | Grass detail 2 | 120.75 | 0.026 % | 120.8 | 1.0 | 1.0 | 1.00 | 0.0 % | 0.0 % | 28.5 |
| 20 | Grass/desert transition | 6050.94 | 1.299 % | 340.5 | 1.0 | 50.5 | 1.00 | 0.0 % | 0.0 % | 28.5 |
| 21 | Grass/swamp transition | 1691.62 | 0.363 % | 246.5 | 1.0 | 22.1 | 1.00 | 0.0 % | 0.0 % | 30.0 |
| 23 | Mud | 1793.19 | 0.385 % | 221.6 | 1.0 | 22.4 | 1.00 | 0.0 % | 0.0 % | 30.5 |
| 24 | Dry grass | 13071.12 | 2.805 % | 575.1 | 1.0 | 53.1 | 1.00 | 0.0 % | 0.0 % | 33.0 |
| 32 | Rocky core | 55416.25 | 11.901 % | 41.6 | 17.8 | 3776.6 | 2.07 | 0.0 % | 0.0 % | 59.5 |
| 33 | Rock transition 2 | 6376.12 | 1.370 % | 43.6 | 21.0 | 421.5 | 2.05 | 0.0 % | 0.0 % | 53.0 |
| 34 | Rocky detail | 24.62 | 0.005 % | 24.6 | 1.0 | 1.0 | 1.00 | 0.0 % | 0.0 % | 66.8 |
| 35 | Rock/snow transition | 2406.12 | 0.517 % | 38.1 | 13.0 | 176.5 | 1.87 | 0.0 % | 0.0 % | 65.5 |
| 48 | Shore | 21040.12 | 4.522 % | 359.8 | 36.0 | 134.3 | 3.08 | 0.0 % | 45.3 % | 2.0 |
| 64 | Desert core | 11209.75 | 2.408 % | 57.9 | 43.2 | 628.4 | 1.99 | 0.0 % | 0.0 % | 33.0 |
| 65 | Desert transition | 3677.38 | 0.790 % | 62.2 | 35.5 | 150.3 | 1.85 | 0.0 % | 0.0 % | 29.5 |
| 80 | Swamp core | 108.06 | 0.023 % | 18.3 | 2.0 | 14.7 | 1.94 | 0.0 % | 0.0 % | 32.2 |
| 81 | Swamp transition | 410.75 | 0.088 % | 38.2 | 7.0 | 25.6 | 1.95 | 0.0 % | 0.0 % | 32.0 |
| 96 | River 1 | 7895.50 | 1.697 % | 431.8 | 18.0 | 31.0 | 4.16 | 0.0 % | 6.3 % | 9.5 |
| 97 | River 2 | 1505.88 | 0.324 % | 94.9 | 14.8 | 25.5 | 4.40 | 0.0 % | 10.4 % | 7.0 |
| 98 | River 3 | 255.12 | 0.055 % | 19.8 | 12.0 | 19.6 | 4.51 | 0.0 % | 12.6 % | 5.8 |
| 99 | River 4 | 63.38 | 0.014 % | 4.4 | 12.8 | 19.8 | 4.86 | 0.0 % | 16.6 % | 4.2 |
| 128 | Snow core | 9727.19 | 2.089 % | 18.9 | 70.0 | 1485.5 | 2.27 | 0.0 % | 0.0 % | 72.0 |
| 129 | Snow transition | 1911.31 | 0.411 % | 24.9 | 35.8 | 193.4 | 2.24 | 0.0 % | 0.0 % | 67.5 |
| 144 | Mud transition 1 | 405.94 | 0.087 % | 24.8 | 7.0 | 37.2 | 2.34 | 0.0 % | 0.0 % | 35.2 |
| 145 | Mud transition 2 | 648.00 | 0.139 % | 34.3 | 14.0 | 43.5 | 1.90 | 0.0 % | 0.0 % | 31.5 |

## Familles analytiques

Les familles `mountain_full`, `mountain_core` et `snow` se recouvrent volontairement ; leurs pourcentages ne doivent donc pas être additionnés.

| Famille | IDs | Cartes | % moyen carte | % moyen terre | Composantes médianes | Taille composante médiane | Périmètre/√aire médian | Trous moyens |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Desert family | `20,64,65` | 16/16 | 3.550 % | 4.497 % | 347.5 | 1.0 | 6.00 | 51.3 |
| Grass | `16,18,19,24` | 16/16 | 55.210 % | 69.929 % | 92.0 | 2.0 | 7.07 | 0.0 |
| Rocky core | `32,34` | 16/16 | 9.400 % | 11.906 % | 39.5 | 17.8 | 8.71 | 0.0 |
| Full mountain family | `17,32,33,34,35,128,129` | 16/16 | 14.113 % | 17.877 % | 59.0 | 4.5 | 8.12 | 1328.1 |
| Mud family | `23,144,145` | 16/16 | 0.483 % | 0.611 % | 216.5 | 1.0 | 6.00 | 2.1 |
| River | `96,97,98,99` | 16/16 | 1.648 % | 2.089 % | 320.5 | 26.0 | 20.79 | 0.0 |
| Shore | `48` | 16/16 | 3.567 % | 4.522 % | 348.0 | 36.0 | 12.02 | 0.0 |
| Snow family | `35,128,129` | 16/16 | 2.381 % | 3.016 % | 37.0 | 13.5 | 9.06 | 122.6 |
| Swamp family | `21,80,81` | 16/16 | 0.375 % | 0.475 % | 241.0 | 1.0 | 6.00 | 2.6 |
| Water | `0,1,2,3,4,5,6,7` | 16/16 | 21.055 % | 0.000 % | 71.5 | 11.0 | 8.38 | 0.0 |

## Transitions HEX6 observées

Le fichier `transitions_normalized.csv` contient tous les couples d'IDs, y compris les auto-voisinages. Voici les 30 couples inter-terrains les plus fréquents, agrégés sur les 16 cartes :

| ID A | ID B | Familles | Cartes | Arêtes HEX6 totales | Part de toutes les arêtes |
|---:|---:|---|---:|---:|---:|
| 16 (Grass) | 96 (River 1) | `grass ↔ river` | 16/16 | 468,031 | 1.656 % |
| 0 (Water 1) | 48 (Shore) | `water ↔ shore` | 16/16 | 303,090 | 1.072 % |
| 16 (Grass) | 48 (Shore) | `grass ↔ shore` | 16/16 | 289,219 | 1.023 % |
| 16 (Grass) | 24 (Dry grass) | `grass ↔ grass` | 16/16 | 287,708 | 1.018 % |
| 0 (Water 1) | 1 (Water 2) | `water ↔ water` | 16/16 | 281,781 | 0.997 % |
| 1 (Water 2) | 2 (Water 3) | `water ↔ water` | 16/16 | 257,972 | 0.913 % |
| 16 (Grass) | 17 (Rock transition 1) | `grass ↔ mountain_full` | 16/16 | 246,220 | 0.871 % |
| 16 (Grass) | 20 (Grass/desert transition) | `grass ↔ desert` | 16/16 | 236,630 | 0.837 % |
| 2 (Water 3) | 3 (Water 4) | `water ↔ water` | 16/16 | 236,218 | 0.836 % |
| 3 (Water 4) | 4 (Water 5) | `water ↔ water` | 16/16 | 215,275 | 0.762 % |
| 17 (Rock transition 1) | 33 (Rock transition 2) | `mountain_full ↔ mountain_full` | 16/16 | 209,118 | 0.740 % |
| 4 (Water 5) | 5 (Water 6) | `water ↔ water` | 16/16 | 197,454 | 0.699 % |
| 32 (Rocky core) | 33 (Rock transition 2) | `mountain_full ↔ mountain_full` | 16/16 | 189,668 | 0.671 % |
| 5 (Water 6) | 6 (Water 7) | `water ↔ water` | 16/16 | 181,499 | 0.642 % |
| 6 (Water 7) | 7 (Water 8) | `water ↔ water` | 16/16 | 168,082 | 0.595 % |
| 20 (Grass/desert transition) | 65 (Desert transition) | `desert ↔ desert` | 16/16 | 125,684 | 0.445 % |
| 64 (Desert core) | 65 (Desert transition) | `desert ↔ desert` | 16/16 | 96,892 | 0.343 % |
| 32 (Rocky core) | 35 (Rock/snow transition) | `mountain_full ↔ snow` | 16/16 | 82,924 | 0.293 % |
| 16 (Grass) | 23 (Mud) | `grass ↔ mud` | 16/16 | 82,810 | 0.293 % |
| 16 (Grass) | 21 (Grass/swamp transition) | `grass ↔ swamp` | 16/16 | 81,606 | 0.289 % |
| 16 (Grass) | 97 (River 2) | `grass ↔ river` | 16/16 | 81,020 | 0.287 % |
| 35 (Rock/snow transition) | 129 (Snow transition) | `snow ↔ snow` | 16/16 | 64,344 | 0.228 % |
| 128 (Snow core) | 129 (Snow transition) | `snow ↔ snow` | 16/16 | 54,014 | 0.191 % |
| 48 (Shore) | 96 (River 1) | `shore ↔ river` | 16/16 | 32,790 | 0.116 % |
| 23 (Mud) | 145 (Mud transition 2) | `mud ↔ mud` | 16/16 | 24,848 | 0.088 % |
| 21 (Grass/swamp transition) | 81 (Swamp transition) | `swamp ↔ swamp` | 16/16 | 17,706 | 0.063 % |
| 16 (Grass) | 98 (River 3) | `grass ↔ river` | 16/16 | 13,104 | 0.046 % |
| 144 (Mud transition 1) | 145 (Mud transition 2) | `mud ↔ mud` | 16/16 | 12,820 | 0.045 % |
| 16 (Grass) | 18 (Grass detail 1) | `grass ↔ grass` | 16/16 | 12,168 | 0.043 % |
| 16 (Grass) | 19 (Grass detail 2) | `grass ↔ grass` | 16/16 | 11,592 | 0.041 % |

Contacts inter-familles observés : `desert ↔ grass`, `grass ↔ mountain_full`, `grass ↔ mud`, `grass ↔ river`, `grass ↔ shore`, `grass ↔ swamp`, `mountain_full ↔ snow`, `river ↔ shore`, `river ↔ water`, `shore ↔ water`.
Aucun contact direct entre une famille montagneuse et une famille désert/marais/boue/rivière n'apparaît dans cette tranche ; les contacts eau/rivière sont détaillés par ID dans le CSV et correspondent aux raccords peu profonds observés.

## Comparaison 2 joueurs / 20 joueurs

Cette comparaison mesure les terrains, pas encore les règles de placement des joueurs. Elle indique si la densité de joueurs semble modifier la géographie native à taille identique.

| ID normalisé | % terre moyen 2P | % terre moyen 20P | Écart 20P–2P | Cellules moy. 2P | Cellules moy. 20P |
|---:|---:|---:|---:|---:|---:|
| 0 (Water 1) | 0.000 % | 0.000 % | 0.000 pp | 9465.25 | 9576.12 |
| 1 (Water 2) | 0.000 % | 0.000 % | 0.000 pp | 8734.88 | 8753.88 |
| 2 (Water 3) | 0.000 % | 0.000 % | 0.000 pp | 7924.38 | 7921.00 |
| 3 (Water 4) | 0.000 % | 0.000 % | 0.000 pp | 7256.38 | 7195.25 |
| 4 (Water 5) | 0.000 % | 0.000 % | 0.000 pp | 6641.50 | 6508.62 |
| 5 (Water 6) | 0.000 % | 0.000 % | 0.000 pp | 6113.50 | 5956.12 |
| 6 (Water 7) | 0.000 % | 0.000 % | 0.000 pp | 5639.50 | 5465.38 |
| 7 (Water 8) | 0.000 % | 0.000 % | 0.000 pp | 73704.62 | 71517.38 |
| 16 (Grass) | 67.110 % | 67.032 % | -0.078 pp | 311614.75 | 313025.88 |
| 17 (Rock transition 1) | 1.529 % | 1.642 % | 0.112 pp | 7095.50 | 7666.38 |
| 18 (Grass detail 1) | 0.028 % | 0.027 % | -0.001 pp | 128.00 | 125.50 |
| 19 (Grass detail 2) | 0.025 % | 0.026 % | 0.001 pp | 118.38 | 123.12 |
| 20 (Grass/desert transition) | 1.317 % | 1.282 % | -0.035 pp | 6116.12 | 5985.75 |
| 21 (Grass/swamp transition) | 0.345 % | 0.382 % | 0.037 pp | 1602.25 | 1781.00 |
| 23 (Mud) | 0.370 % | 0.400 % | 0.031 pp | 1716.88 | 1869.50 |
| 24 (Dry grass) | 2.636 % | 2.973 % | 0.337 pp | 12256.00 | 13886.25 |
| 32 (Rocky core) | 12.005 % | 11.796 % | -0.209 pp | 55753.38 | 55079.12 |
| 33 (Rock transition 2) | 1.321 % | 1.419 % | 0.098 pp | 6127.88 | 6624.38 |
| 34 (Rocky detail) | 0.005 % | 0.005 % | 0.000 pp | 23.75 | 25.50 |
| 35 (Rock/snow transition) | 0.529 % | 0.505 % | -0.024 pp | 2456.50 | 2355.75 |
| 48 (Shore) | 4.502 % | 4.542 % | 0.040 pp | 20892.00 | 21188.25 |
| 64 (Desert core) | 2.556 % | 2.259 % | -0.297 pp | 11875.25 | 10544.25 |
| 65 (Desert transition) | 0.811 % | 0.769 % | -0.042 pp | 3765.62 | 3589.12 |
| 80 (Swamp core) | 0.023 % | 0.023 % | 0.000 pp | 107.25 | 108.88 |
| 81 (Swamp transition) | 0.087 % | 0.090 % | 0.003 pp | 403.50 | 418.00 |
| 96 (River 1) | 1.689 % | 1.705 % | 0.016 pp | 7834.50 | 7956.50 |
| 97 (River 2) | 0.331 % | 0.316 % | -0.015 pp | 1537.75 | 1474.00 |
| 98 (River 3) | 0.053 % | 0.057 % | 0.003 pp | 246.88 | 263.38 |
| 99 (River 4) | 0.015 % | 0.012 % | -0.003 pp | 69.75 | 57.00 |
| 128 (Snow core) | 2.067 % | 2.110 % | 0.043 pp | 9601.62 | 9852.75 |
| 129 (Snow transition) | 0.424 % | 0.397 % | -0.028 pp | 1970.88 | 1851.75 |
| 144 (Mud transition 1) | 0.087 % | 0.087 % | -0.001 pp | 407.12 | 404.75 |
| 145 (Mud transition 2) | 0.134 % | 0.144 % | 0.010 pp | 622.50 | 673.50 |

## Premières observations, sans modification du générateur

- Les IDs présents, leurs quantités et leurs formes exactes sont maintenant enregistrés séparément en brut et en couche normalisée.
- La distinction `28 → 16` est indispensable : compter 28 comme un biome autonome fausserait la surface d'herbe et les contours autour des starts.
- Les tableaux de composantes permettent de distinguer une grande famille cohérente d'une multitude de petits composants indépendants ; les trous de famille sont mesurés séparément et ne sont pas assimilés à des micro-composants.
- Les transitions sont mesurées par couples d'IDs adjacents, avant toute décision sur l'ordre de génération. Cette sortie servira à confronter les règles actuelles `eau → rive → terrains` aux observations natives.
- Aucun changement de règle ou de terrain n'est déduit de la seule moyenne 2P/20P : les écarts seront confrontés aux formes, aux starts et aux ressources dans les phases suivantes.

## Sorties détaillées

- `native_terrain_audit_16_768_2p20p.json` : corpus et statistiques agrégées/par carte ; les composantes détaillées sont dans le CSV dédié.
- `native_terrain_audit_16_768_2p20p_manifest.json` : provenance, tailles, hash SHA-256 et contrôles de format.
- `native_terrain_audit_16_768_2p20p_per_map.csv` : tableau large par carte et ID.
- `native_terrain_audit_16_768_2p20p_terrain_ids.csv` : agrégats par ID brut/normalisé.
- `native_terrain_audit_16_768_2p20p_families.csv` : agrégats par famille analytique.
- `native_terrain_audit_16_768_2p20p_components.csv` : une ligne par composante des IDs normalisés, plus les composantes brutes de l'ID 28.
- `native_terrain_audit_16_768_2p20p_transitions_normalized.csv` : matrice longue des transitions normalisées.
