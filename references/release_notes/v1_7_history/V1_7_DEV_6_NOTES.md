# Settlers III MapGen — v1.7 DEV_6

## Objectif

Amélioration ciblée de la comparaison Stats A/B et cohérence des imports dans le chemin de comparaison.

## Changements

- Comparaison A/B compacte conservée : une ligne par métrique, barre A et barre B côte à côte, valeur dans chaque barre.
- Barres A/B segmentées quand la métrique a une composition utile :
  - Eau = mer + lacs ;
  - Montagne = roche/non-neige + neige ;
  - Ressources forestières = pousses + arbres adultes + palmiers ;
  - Stock minier = charbon + fer + or + gemmes + soufre ;
  - Agriculture = blé + vigne + riz.
- Les métriques simples (terre, pierre, poisson) restent des barres simples.
- La bascule A/B conserve explicitement le statut importé des EDM/MAP/SAV via `source_format`.
- Tests dédiés aux sommes des segments A/B et au chemin importé.

## Validation

- 51 tests automatisés PASS.
- Smoke visuel A/B sur SAV réel 768×768 / 10 joueurs PASS.
- Aucun changement volontaire du moteur de génération v1.5.

## Suite

- Calibration gameplay des rayons locaux autour de ~R60 puis R100 : à traiter séparément.
- Couleurs A/B personnalisables : TODO.
- Migration de nomenclature des modules `v15/v16` vers `v1_5/v1_6` : refactor contrôlé futur.
