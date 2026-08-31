# Settlers III — calibration ressources Legacy R7 — écartée

> Candidate écartée le 30 août 2026. Elle reste documentée pour préserver la
> trace de l’erreur, mais ne doit servir ni de référence Legacy ni de base au
> futur mode Custom.
> Sources : les 16 SAV natifs 768×768 analysés dans
> `native_resource_object_audit/` et les règles long-play maintenues dans les
> références lues par `SETTLERS3_PREGEN_READ_FIRST.md`.

## Périmètre

R7 ne modifie ni les masques de terrains, ni les transitions, ni la
bathymétrie, ni les objets, ni le placement des starts. La couche ressources
s’exécute après l’hydrologie et ne peut donc créer aucune transition
graphique.

## Paramètres appliqués puis retirés

| Mesure 768 | Profil faible densité (≤8 joueurs) | Profil forte densité (>8 joueurs) |
|---|---:|---:|
| Minerais | 39 859 cellules | 40 061 cellules |
| Poissons | 46 071 cellules | 43 737 cellules |
| Supports minerai | `17,32,33,34,35,128,129` | identique |
| Exclusion économique start | **retirée en R8** | **retirée en R8** |

Les quotas par famille et les statistiques de composantes sont stockés dans
`continental_legacy_v2.json`, issus des médianes 2P et 20P. La reconstruction
des blobs emploie une majorité de petites poches, une tranche intermédiaire et
une longue traîne ; elle reste une approximation procédurale, pas une
déduction de l’algorithme interne du jeu.

## Règles préservées

- Les quantités restent soumises au multiplicateur historique +30 % et au cap
  15. Les SAV natifs mesurent une moyenne proche de 8, mais cette règle de
  stock long-play reste explicitement protégée et est distincte du calibrage
  spatial R7.
- Les poissons sont seulement sur Water0..7, jamais sur River96..99. Le filtre
  R7 de distance à la Shore est retiré : il appartient au futur profil
  Upgraded, pas au Legacy.
- L’exclusion R7 de ressources autour des starts est retirée : l’observation
  sur 16 SAV ne démontrait pas une interdiction générale.

## Validation R7

Deux sondes procédurales 768 ont produit les cibles exactes :

| Sonde | Minerais | Poissons | Validations |
|---|---:|---:|---|
| 2P, seed `2026083001` | 39 859 | 46 071 | 20/20 PASS |
| 20P, seed `2026083002` | 40 061 | 43 737 | 20/20 PASS |

Les prochaines sorties Legacy doivent être comparées par composantes, supports
et répartition spatiale, sans déduire un rayon interdit autour des starts.
