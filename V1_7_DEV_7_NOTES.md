# Settlers III MapGen — v1.7 DEV_7

## Objectif
Consolider les retours utilisateur DEV_5 + DEV_6 sur les graphes Stats sans modifier le moteur de génération v1.5 validé.

## Changements
- échelles quantitatives rouge → jaune → vert pour les graphes concernés ;
- Building Stones : 12 pierres = vert, milieu = jaune, épuisé = rouge ;
- segments non nuls trop petits : label extérieur relié au segment au lieu de masquer la valeur ;
- Ressources forestières : Adultes → Palmiers → Pousses ;
- labels de hauteur plus descriptifs ;
- raccourci configurable `Ctrl+Shift+T` pour basculer clair/sombre ;
- distances adversaires : min rouge, zone médiane jaune, max vert, adversaire le plus proche identifié avec couleurs joueurs ;
- ressources locales étendues à R50/R100 : Arbres/Pierres/Poissons = 0–50 + 50–100 ;
- minage local : deux barres par joueur, A = ≤50 HEX, B = 50–100 HEX, segmentées par minerai ;
- massifs/lacs/rivières : plus grand = plus foncé ;
- A/B : couleurs sémantiques ajoutées à Terre, Stock pierre et Stock poisson ;
- Stats schema v4.

## Validation
- 55 tests automatisés PASS ;
- smoke visuel SAV réel 768×768 / 10 joueurs PASS ;
- cinq hashes protégés de la baseline v1.5 inchangés ;
- ZIP DEV_7 testé sans erreur.

## TODO conservé
- tooltips interactifs détaillés sur les graphes ;
- synchronisation optionnelle/désactivable graphe ↔ vue map ;
- imports dans historique + taille historique configurable ;
- netteté/résolution export PNG ;
- couleurs A/B personnalisables ;
- refactor contrôlé des noms `v15/v16` vers `v1_5/v1_6` ;
- audit/synchro byte-for-byte du source GitHub avec le dernier ZIP testé.