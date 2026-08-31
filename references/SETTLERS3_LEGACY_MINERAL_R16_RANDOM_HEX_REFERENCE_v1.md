# Settlers III — méthode Legacy R16 par zones HEX aléatoires

> Candidate locale produite le 30 août 2026, à partir des 16 SAV natifs
> 768×768 déjà audités. R16 est un essai de mécanique ; elle n'est pas encore
> une validation visuelle définitive.

## Décision de méthode

La reconstruction R16 applique uniquement les éléments suffisamment établis :

1. le support est la montagne intérieure `32, 33, 34, 35, 128, 129` ; l'ID
   `17`, transition extérieure, n'a pas de cellule minéralisée dans le corpus
   des 16 SAV ;
2. les familles sont peintes dans l'ordre observé : charbon `0x10`, fer
   `0x20`, or `0x30`, gemmes `0x40`, souffre `0x50` ; une famille suivante peut
   donc remplacer une cellule déjà peinte ;
3. chaque zone est un disque HEX6 indépendant de rayon 3, 4 ou 5, soit une
   capacité théorique de 37, 61 ou 91 cellules ; le rayon 6/diamètre 13 reste
   exclu faute de preuve ;
4. le taux de remplissage est tiré uniformément entre un minimum provisoire
   par famille et 1,00. Les pixels choisis dans la zone sont aléatoires, avec
   conservation du centre pour qu'une zone faiblement remplie reste visible ;
5. aucun chaînage de centres, biais radial, lissage HEX6, réservation de même
   famille, rayon d'exclusion des starts ou halo de terrain/décor n'est ajouté.

Le nombre de cellules finales est calibré sur l'occupation native d'environ
53 % de la montagne intérieure. Les proportions de familles viennent des
cellules mesurées dans le corpus, avec les deux profils de densité déjà
présents dans `continental_legacy_v2.json`.

## Paramètres R16

| Paramètre | Valeur |
|---|---|
| support | `32/33/34/35/128/129` |
| occupation cible | `0,53` du support intérieur |
| rayons | `3/4/5` |
| poids de rayons | `0,30/0,50/0,20` |
| remplissage maximal | `1,00` |
| remplissage minimal charbon | `0,20` |
| remplissage minimal fer | `0,26` |
| remplissage minimal or | `0,29` |
| remplissage minimal gemmes | `0,28` |
| remplissage minimal souffre | `0,29` |
| distribution du remplissage | uniforme |

Les minima sont des bornes de travail : les SAV ne conservent ni le centre ni
l'historique d'un hexagone natif et ne permettent donc pas de mesurer le
minimum exact d'une zone élémentaire. Ils sont inspirés de la borne basse du
proxy de remplissage, pas présentés comme une constante du jeu.

## Contrôle réel R16

Les valeurs suivantes proviennent de `MapState` réellement générés, pas d'une
image composée à la main.

| Sortie | Support intérieur | Cible | Final | Occupation finale | Rocky32 minéralisé |
|---|---:|---:|---:|---:|---:|
| 768, 2P, seed 2026083001 | 75 887 | 40 220 | 39 899 | 52,58 % | 53,95 % |
| 768, 20P, seed 2026083002 | 76 911 | 40 763 | 40 447 | 52,59 % | 53,74 % |

Les shortfalls de zones sont nuls sur ces deux sorties. La différence entre la
cible et le final vient des recouvrements spatiaux entre familles, conservés
volontairement par la méthode.

### Familles finales

| Famille | R16 2P | R16 20P |
|---|---:|---:|
| Charbon | 20 084 | 20 664 |
| Fer | 8 561 | 8 768 |
| Or | 5 946 | 6 026 |
| Gemmes | 2 059 | 2 046 |
| Souffre | 3 249 | 2 943 |

Les quotas restent proches des cellules natives moyennes : environ 39 937 en
2P et 39 936 en 20P. La répartition finale doit néanmoins être recontrôlée
sur une matrice de seeds, car les écrasements font varier les familles les
plus anciennes.

### Forme observable et limite connue

La méthode supprime les longues poches logiques et la dérive en ruban de R15.
Elle produit bien des zones de diamètre 7/9/11, remplies plus ou moins, et
réparties sur les massifs existants. En revanche, le tirage uniforme interne
reste volontairement une hypothèse testable : les premières mesures R16 donnent
encore davantage de petites composantes que les SAV natifs, surtout pour les
gemmes et le souffre. Il faudra décider après comparaison dans le jeu si les
pixels manquants sont réellement indépendants ou s'il existe une cohérence
très légère à l'intérieur de chaque zone.

Cette limite ne remet pas en cause les garde-fous de terrain : les minerais ne
peuvent être peints que sur le support montagneux établi et la passe ne touche
ni la chaîne Eau → Shore → terrain, ni les starts, ni la branche Upgraded.
