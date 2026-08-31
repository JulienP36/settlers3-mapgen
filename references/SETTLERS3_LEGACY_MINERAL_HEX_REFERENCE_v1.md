# Settlers III — morphologie des minerais Legacy par hexagones v1

> Mesure produite le 30 août 2026 à partir des 16 SAV natifs 768×768
> disponibles : 8 cartes à 2 joueurs et 8 cartes à 20 joueurs.

## Ce qui est observé et ce qui est déduit

Un SAV ne conserve pas l'historique des écritures d'une cellule. Il ne permet
donc pas de prouver directement qu'un patch a été peint avant un autre. La
séquence **charbon → fer → or → gemmes → soufre** vient de l'observation du
propriétaire et constitue l'hypothèse de reconstruction retenue pour Legacy.

La mesure exploitable est le masque final de chaque famille. Pour estimer les
unités hexagonales visibles, chaque masque est dilaté d'un voisinage HEX6 puis
étiqueté. Une unité mesurée contient les cellules finales de la famille et son
enveloppe à une distance HEX. C'est un proxy reproductible du patch peint, pas
une prétention à décoder la fonction interne du jeu.

## Nombre de patchs visibles par carte

Les valeurs ci-dessous sont les médianes par carte ; le comptage inclut les
petits groupes d'au moins une cellule finale.

| Famille | 2 joueurs | 20 joueurs |
|---|---:|---:|
| Charbon | 229 | 244 |
| Fer | 196,5 | 192 |
| Or | 133,5 | 147 |
| Gemmes | 55,5 | 61 |
| Soufre | 79,5 | 84 |

La légère hausse du charbon, de l'or, des gemmes et du soufre en 20P ne
justifie pas de multiplier les tailles des patchs : c'est d'abord le nombre
de patchs qui varie.

## Taille des patchs et longue traîne

« Cellules » désigne ici les cellules finales de la famille dans une unité
regroupée ; « enveloppe » désigne cette unité après dilatation HEX6 d'un pas.
Les quantiles sont calculés sur les 16 cartes.

| Famille | cellules p25 / p50 / p75 / p90 | enveloppe p50 | remplissage p50 |
|---|---:|---:|---:|
| Charbon | 4 / 22 / 78 / 225 | 57 | 0,37 |
| Fer | 11 / 31 / 59 / 102 | 71 | 0,42 |
| Or | 15 / 33 / 56 / 87 | 72 | 0,44 |
| Gemmes | 16 / 32 / 51 / 69 | 71 | 0,45 |
| Soufre | 18 / 35 / 53 / 74 | 74 | 0,46 |

Le charbon a la traîne la plus longue : p95 409, p99 955 et maximum observé
2237 cellules dans une unité regroupée. Pour le fer, l'or, les gemmes et le
soufre, les p99 sont respectivement 252, 176, 110 et 134 cellules. Ces maxima
ne doivent pas devenir la taille moyenne : ils sont conservés comme une
traîne rare.

## Remplissage dépendant de la taille

Le taux n'est pas uniforme. Mesuré comme cellules finales / enveloppe HEX1,
il monte avec la taille du groupe :

| Taille finale du groupe | Charbon | Fer | Or | Gemmes | Soufre |
|---|---:|---:|---:|---:|---:|
| 1–20 cellules | 0,20 | 0,26 | 0,29 | 0,28 | 0,29 |
| 21–50 | 0,43 | 0,45 | 0,46 | 0,46 | 0,47 |
| 51–100 | 0,50 | 0,54 | 0,58 | 0,57 | 0,58 |
| 101–250 | 0,52 | 0,56 | 0,57 | 0,62 | 0,60 |
| >250 | 0,55 | 0,57 | 0,57 | 0,62 | 0,60 |

La reconstruction R10 utilise donc une courbe de remplissage par famille,
interpolée selon la taille du patch, avec une petite variation aléatoire. Les
petits hexagones restent lacunaires ; les grands deviennent plus pleins sans
être des disques uniformes.

## Règle de peinture R10

1. Le support est limité aux terrains montagneux observés :
   `17, 32, 33, 34, 35, 128, 129`.
2. Chaque famille reçoit son propre nombre de patchs et sa distribution de
   tailles, sans masque `available` partagé entre familles.
3. Un patch est une aire HEX compacte, découpée par le support montagneux,
   puis remplie selon sa taille ; il peut être partiellement vide.
4. Les patchs d'une même famille sont espacés pour conserver des unités
   distinctes. Les familles suivantes sont libres de peindre sur les cellules
   déjà écrites, ce qui réalise l'écrasement observé.
5. Aucun rayon d'exclusion autour des départs n'est appliqué. Les quantités
   restent indépendantes de la forme : valeurs 1–15 et multiplicateur Legacy
   existant.

## Limites et validation restante

Le regroupement HEX1 est une mesure de morphologie finale. Il ne distingue pas
un hexagone natif qui a été fragmenté par un recouvrement d'un groupe de petits
hexagones proches. L'ordre d'écriture ne peut pas être récupéré des SAV seuls.
Il faudra donc comparer R10 sur plusieurs seeds et dans le jeu, puis ajuster
les espacements, le support montagneux et les distributions si l'overlay
visuel montre encore des chaînes trop longues.
