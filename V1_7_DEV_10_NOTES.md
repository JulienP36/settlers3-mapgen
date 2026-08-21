# Settlers III MapGen v1.7 DEV_10

DEV_10 consolide le socle **Statistiques + Graphiques** avant passage en Release Candidate.

## Statistiques / debug
- inventaire exhaustif de tous les Terrain IDs présents ;
- inventaire exhaustif de tous les Object IDs présents ;
- densités normalisées `/1000` avec dénominateur adapté à la donnée : terre, eau ou montagne ;
- export CSV des densités ;
- schema Stats v6.

## Graphiques
- tooltips interactifs génériques au survol des barres et segments ;
- support des tooltips pour les graphes A/B ;
- aucun couplage automatique graphe ↔ vue map dans cette version.

## Comparaison A/B
- les boutons A/B affichent une LED verte lorsqu’un slot est défini ;
- le bouton affiche également une identification courte de la map affectée au slot ;
- aucune refonte fonctionnelle de la comparaison.

## Documentation
- TODO nettoyé des éléments Stats déjà réalisés et anciens points devenus obsolètes.
