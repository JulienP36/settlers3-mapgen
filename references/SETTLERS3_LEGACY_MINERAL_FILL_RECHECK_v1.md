# Settlers III — recontrôle du remplissage des gisements Legacy v1

> Analyse produite le 30 août 2026 à partir des 16 SAV natifs 768×768
> disponibles : 8 cartes à 2 joueurs et 8 cartes à 20 joueurs. Comparaison
> avec deux sorties de la génération R12, une en 2P et une en 20P.

## Conclusion courte

Le total de cellules de soufre de R12 est du bon ordre de grandeur, mais sa
structure est nettement trop fragmentée. Le problème observé n'est donc pas
seulement un manque de variation du paramètre `fill_jitter` : les cellules
choisies dans un hexagone sont trop dispersées et les gisements ne forment pas
assez souvent des noyaux compacts et pleins.

Le soufre est le meilleur candidat pour cette mesure : il est peint après les
autres minerais et les poissons sont placés sur l'eau. Son masque final ne
subit donc pas l'écrasement d'une famille minérale ultérieure.

## Méthode et limite

Le SAV ne conserve pas les centres ni l'historique des hexagones peints. On ne
peut donc pas reconstruire le taux exact de chaque hexagone natif.

Pour obtenir un proxy reproductible, le masque final du soufre est séparé en
composantes HEX6. Pour chaque composante, on cherche le maximum de cellules de
cette composante contenues dans une fenêtre HEX de rayon 3, 4 ou 5 :

| Rayon | Diamètre | Capacité théorique |
|---:|---:|---:|
| 3 | 7 | 37 cellules |
| 4 | 9 | 61 cellules |
| 5 | 11 | 91 cellules |

Par exemple, un taux de 0,50 au rayon 3 signifie qu'une fenêtre locale
contient environ 19 cellules de soufre sur 37. Ce calcul mesure la compacité
visible du masque final ; il ne prétend pas identifier l'hexagone interne du
jeu. Les résultats sont particulièrement utiles pour comparer la variance et
la fragmentation de deux générateurs.

## Résultat principal : fenêtres locales les plus pleines

Les quantiles ci-dessous sont calculés sur les composantes, donc chaque petite
occurrence compte comme une composante. La colonne `p50 / p75 / p90` donne les
quantiles du meilleur remplissage local.

| Source | Rayon 3 | Rayon 4 | Rayon 5 |
|---|---:|---:|---:|
| Natif 2P | 0,27 / 0,73 / 0,92 | 0,16 / 0,59 / 0,80 | 0,11 / 0,42 / 0,64 |
| Natif 20P | 0,22 / 0,70 / 0,89 | 0,13 / 0,53 / 0,79 | 0,09 / 0,37 / 0,63 |
| R12 2P | 0,05 / 0,14 / 0,35 | 0,03 / 0,08 / 0,24 | 0,02 / 0,06 / 0,17 |
| R12 20P | 0,05 / 0,11 / 0,32 | 0,03 / 0,07 / 0,20 | 0,02 / 0,04 / 0,13 |

Le natif possède donc bien une distribution beaucoup plus étalée : petites
occurrences clairsemées, gisements intermédiaires, et noyaux très remplis.
R12 concentre au contraire la majorité de ses composantes dans les faibles
taux de remplissage.

## Résultat pondéré par les cellules

Cette lecture est plus proche de l'impression visuelle d'une carte : elle
répond à « dans quel type de gisement tombe une cellule de soufre choisie au
hasard ? ». Au rayon 3 :

| Source | Cellules de soufre | Composantes | Médiane de taille | Part des cellules dans une fenêtre locale au moins… |
|---|---:|---:|---:|---:|
| Natif 2P | 25 633 cumulées | 1 134 | 10 | 87 % à 0,50 ; 80 % à 0,60 ; 72 % à 0,70 |
| Natif 20P | 24 570 cumulées | 1 189 | 8 | 86 % à 0,50 ; 79 % à 0,60 ; 68 % à 0,70 |
| R12 2P | 3 284 | 575 | 2 | 46 % à 0,50 ; 29 % à 0,60 ; 19 % à 0,70 |
| R12 20P | 2 950 | 599 | 2 | 37 % à 0,50 ; 21 % à 0,60 ; 13 % à 0,70 |

Les valeurs natives sont agrégées sur huit cartes, tandis que R12 correspond à
une sortie de contrôle par population de joueurs. La comparaison est donc
diagnostique, pas une validation statistique finale.

## La fragmentation explique l'impression visuelle

La quantité totale est relativement proche, mais les cellules ne sont pas
regroupées de la même façon :

| Source | p25 taille composante | p50 | p75 | p90 | p95 | maximum |
|---|---:|---:|---:|---:|---:|---:|
| Natif 2P | 2 | 10 | 39 | 60 | 73 | 217 |
| Natif 20P | 2 | 8 | 34 | 58 | 71 | 139 |
| R12 2P | 1 | 2 | 5 | 15 | 28 | 98 |
| R12 20P | 1 | 2 | 4 | 12 | 22 | 60 |

Part des cellules dans des composantes de taille 26 ou plus :

- natif 2P : 83,3 % ; natif 20P : 81,1 % ;
- R12 2P : 42,4 % ; R12 20P : 33,1 %.

À l'inverse, les composantes de taille 10 ou moins contiennent seulement
6,5–7,2 % des cellules natives, contre 37,4–41,6 % dans R12.

## Interprétation pour le générateur

La cause probable est dans la mécanique de peinture actuelle :

1. R12 tire uniformément des cellules dans l'enveloppe HEX, puis en peint une
   fraction. Un tirage uniforme produit des trous et des îlots disjoints, même
   lorsque le taux moyen est correct.
2. La réservation anti-répétition d'une famille empêche de réutiliser les
   cellules déjà peintes, mais ne force pas la nouvelle cellule à toucher le
   noyau précédent.
3. Le chaînage des centres rapproche les enveloppes, sans garantir une forme
   compacte à l'intérieur de chaque enveloppe.

Augmenter uniquement `fill_jitter` ne corrigera donc pas le problème. La
prochaine correction devra conserver une variation large des taux, mais
sélectionner les cellules par noyau/fondation HEX contiguë ou par biais de
distance vers un centre, avec quelques irrégularités contrôlées. Les totaux,
la palette de rayons 3–5 et l'ordre charbon → fer → or → gemmes → soufre ne
doivent pas être modifiés sur la base de cette seule mesure.

## Cible de calibration provisoire

Pour une prochaine itération, le rayon 3 est le meilleur indicateur de
compacité locale, sans conclure que tous les hexagones natifs ont ce rayon. Une
cible raisonnable est de retrouver :

- une médiane de composante autour de 8–10 cellules ;
- environ 80 % des cellules dans des composantes d'au moins 26 cellules ;
- une présence visible de noyaux locaux à 0,60–0,70 et davantage, tout en
  conservant des occurrences faibles ;
- une distribution de remplissage nettement plus étalée que la distribution
  actuelle de R12.

Ces objectifs décrivent la forme finale observable. Ils devront être
recontrôlés sur plusieurs seeds et par comparaison visuelle dans le jeu avant
de devenir des paramètres fixes du générateur custom.

## Contrôle de l'implémentation R13

R13 applique une sélection radiale bruitée (`selection_noise = 0,60`), une
fenêtre de chaînage de 6 cellules et une dispersion de tailles groupées de
`0,65`. Sur les deux seeds de contrôle :

| Sortie R13 | Cellules | Composantes | Taille p50 / p75 / p90 | Part des cellules dans des composantes ≥26 |
|---|---:|---:|---:|---:|
| 768 2P, seed 2026083001 | 3 284 | 143 | 14 / 34 / 56 | 81,0 % |
| 768 20P, seed 2026083002 | 2 950 | 147 | 15 / 34 / 47 | 73,4 % |

Pour le meilleur remplissage local au rayon 3, les parts de cellules atteignant
au moins `0,50 / 0,60 / 0,70` sont respectivement `86,3 % / 78,1 % / 73,9 %`
en 2P et `84,8 % / 74,9 % / 69,1 %` en 20P. Elles sont proches des références
natives `87,1 % / 80,0 % / 71,5 %` et `85,8 % / 78,8 % / 67,9 %`.

Cette validation est structurelle et statistique sur deux sorties ; elle ne
remplace pas le contrôle visuel dans l'éditeur et en jeu. La calibration
multi-seeds reste ouverte avant de figer définitivement le modèle.
