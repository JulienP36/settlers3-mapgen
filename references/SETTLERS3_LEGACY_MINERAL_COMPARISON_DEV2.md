# Settlers III — comparaison du placement des minerais avant DEV_2

> Relevé du 1er septembre 2026, effectué avant le retrait du générateur
> procédural Legacy v2.0 DEV_1.

## Résultat

L’ancien générateur Legacy était proche des références natives pour les
**volumes et la répartition des familles**, mais pas pour la **géométrie des
amas**. Il ne constitue donc pas une base utile pour porter l’algorithme du
jeu.

La sortie comparée est une carte `768×768`, `4P`, seed `2026083004`. Les
références sont les médianes du corpus natif de 8 SAV `768×768`, groupe `2P`.

| Famille | Natif : cellules/map | Ancien Legacy | Écart | Natif : composantes/map | Ancien Legacy |
|---|---:|---:|---:|---:|---:|
| Charbon | 20 180,5 | 19 880 | −1,5 % | 1 176,5 | 1 859 |
| Fer | 8 633,5 | 8 376 | −3,0 % | 519,5 | 733 |
| Or | 5 731,0 | 5 790 | +1,0 % | 289,0 | 413 |
| Gemmes | 2 092,5 | 1 988 | −5,0 % | 103,5 | 181 |
| Soufre | 3 219,5 | 3 181 | −1,2 % | 136,5 | 239 |

Les parts finales de l’ancienne sortie étaient `50,69 % / 21,36 % /
14,76 % / 5,07 % / 8,11 %`, contre `50,19 % / 21,56 % / 14,42 % /
5,45 % / 8,39 %` dans le corpus natif pooled. Cette proximité vient de la
calibration des quotas, pas d’une reproduction démontrée du tirage natif.

## Écart géométrique

Les composantes finales de l’ancien générateur sont beaucoup trop nombreuses
et trop petites : leurs tailles médianes étaient `2 / 2 / 3 / 2 / 3` cellules
pour charbon, fer, or, gemmes et soufre, alors que les médianes natives sont
`2 / 3 / 5 / 7 / 11,75`. Les p90 de l’ancien code (`27 / 36 / 43 / 37 /
48,2`) restent également sous les références natives (`47,05 / 52,35 / 59 /
53,8 / 57`).

L’ancien code tirait bien des enveloppes HEX6 de rayon `3/4/5` et des
remplissages aléatoires, mais ses passes de sélection et ses écrasements
produisaient une fragmentation incompatible avec les amas observés. Ces
mesures sont conservées uniquement comme comparaison historique ; elles ne
doivent pas être réutilisées comme contrat du nouveau générateur natif.

## Décision DEV_2

- supprimer le pipeline `continental_legacy_v2` et ses helpers de placement ;
- conserver les mesures natives dans les audits et références existants ;
- reconstruire séparément le générateur Legacy à partir du comportement
  décompilé, sans hériter des quotas ou de la géométrie de DEV_1 ;
- laisser le chemin `Upgraded` et ses règles validées fonctionner pendant la
  reconstruction.
