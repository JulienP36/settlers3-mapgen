# Settlers III MapGen v1.7 DEV_1 — Stats foundation

Première livraison de la passe GIGA Stats.

## Inclus
- analyse structurée multi-source sur `MapState` ;
- compte exact Terrain IDs / Object IDs ;
- familles terrain et végétation ;
- Object 84 nommé **Pousse d’arbre** / **Tree sapling** ;
- minerais : cellules, stock, moyenne, percentiles et occupation montagne ;
- Building Stones 115..127 avec stock exact et ID127 épuisé = 0 ;
- poissons, agriculture runtime, hydrologie, relief, composantes et starts ;
- rapports textuels FR/EN ;
- exports JSON et CSV ;
- 7 graphes intégrés + export PNG ;
- 38 tests PASS.

## Moteur
Le moteur de génération v1.5 et ses profils/données protégés restent strictement inchangés.

## Suite immédiate
- richesse locale par joueur (HEX10/20/30/40) ;
- graphes cases minières vs stock ;
- blobs/massifs/lacs/rivières plus détaillés ;
- comparaison A/B Stats ;
- comparaison corpus natif.
