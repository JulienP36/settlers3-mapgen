# Settlers III — profil quantitatif Legacy R17

> Candidate locale du 30 août 2026. Cette référence complète la méthode
> géométrique R16 sans modifier ses zones HEX, ses rayons, ses remplissages,
> son occupation montagneuse ni son ordre de peinture.

## Décision R17

Le low nibble des ressources est tiré uniformément dans l'intervalle natif
`1..15`. Le profil procédural `continental_legacy_v2.json` utilise donc
`quantity_multiplier = 1.0` et conserve `quantity_cap = 15`.

La formule de compatibilité reste la même :

```text
min(15, floor(tirage_uniforme(1..15) * quantity_multiplier + 0.5))
```

Avec `1.0`, elle restitue exactement les quinze valeurs possibles. Les
profils historiques protégés `legacy_768_v1.json` et `upgraded_768_v1.json`
ne sont pas modifiés par cette candidate.

## Mesure native des quantités

Le corpus utilisé comprend 16 SAV natifs 768×768 : 8 cartes 2 joueurs et
8 cartes 20 joueurs. Les cinq minerais totalisent 638 773 cellules mesurées.

| Groupe | Minerais, moyenne par cellule | Médiane | Répartition observée |
|---|---:|---:|---|
| 2P + 20P pooled | 7,994 | 8 | presque uniforme de 1 à 15 |
| 2P | 7,988 | 8 | chaque valeur ≈ 6,67 % |
| 20P | 8,000 | 8 | chaque valeur ≈ 6,67 % |

Les poissons suivent le même domaine `1..15`, avec une moyenne légèrement
plus basse de `7,865`. La valeur `1` y est un peu surreprésentée, mais cela
ne justifie pas un multiplicateur par famille.

### Écart de l'ancienne formule R16

Avec `quantity_multiplier = 1.3`, les entrées uniformes donnaient :

```text
1→1, 2→3, 3→4, 4→5, 5→7, 6→8, 7→9, 8→10,
9→12, 10→13, 11→14, 12→15, 13→15, 14→15, 15→15
```

Les quantités `2`, `6` et `11` étaient impossibles, la quantité `15`
apparaissait 26,67 % du temps et la moyenne théorique montait à `9,733`.
R17 ramène la moyenne théorique à `8,0`, sans changer le nombre de cellules.

## Composition des familles minérales

Les pourcentages sont calculés sur les cellules minéralisées, pas sur toute la
carte.

| Famille | Legacy natif 2P | R16/R17 cible 2P | Legacy natif 20P | R16/R17 cible 20P |
|---|---:|---:|---:|---:|
| Charbon | 50,32 % | 50,63 % | 50,26 % | 50,65 % |
| Fer | 21,93 % | 21,66 % | 21,79 % | 21,81 % |
| Or | 14,48 % | 14,38 % | 15,03 % | 15,11 % |
| Gemmes | 5,22 % | 5,25 % | 5,24 % | 5,20 % |
| Soufre | 8,05 % | 8,08 % | 7,67 % | 7,22 % |

Les cibles sont donc déjà très proches du mélange natif. La légère baisse du
soufre dans le profil 20P est conservée pour cette candidate : elle reste un
écart de composition à surveiller, pas une raison de modifier simultanément
la géométrie et les quantités.

## Contrôle de stock attendu

Après R17, le stock moyen attendu est approximativement `8 × nombre de
cellules`, comme dans les SAV. Les deux sorties R16 mesurées avaient 39 899
et 40 447 cellules minérales finales ; à composition spatiale inchangée, cela
donne environ 319 192 et 323 576 unités, contre environ 318 095 et 320 165
unités dans les références natives 2P et 20P.

La correction porte uniquement sur le low nibble. Les supports, le high
nibble des familles, les recouvrements séquentiels et la branche Upgraded
restent séparés.
