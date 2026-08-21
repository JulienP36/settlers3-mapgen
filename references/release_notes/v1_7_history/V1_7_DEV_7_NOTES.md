# Settlers III MapGen — v1.7 DEV_7

## Objectif

Consolider les retours utilisateur DEV_5 + DEV_6 sur les graphes Stats sans modifier le moteur de génération v1.5 validé.

## Changements

- Échelles quantitatives rouge→jaune→vert pour les graphes concernés.
- Building Stones : dégradé 3 couleurs, 12 pierres = vert, milieu = jaune, épuisé = rouge.
- Les segments non nuls trop petits pour contenir leur valeur reçoivent un label extérieur relié au segment ; aucune valeur positive ne doit disparaître silencieusement.
- Stock minier : légende Accessible / Sous neige conservée et valeurs des petits segments rendues visibles.
- Ressources forestières : ordre Arbres adultes → Palmiers → Pousses.
- Hauteurs : labels courts mais plus descriptifs.
- Nouveau raccourci configurable `Ctrl+Shift+T` : bascule thème clair/sombre.
- Distances au plus proche adversaire : rouge=min observé, jaune=zone médiane, vert=max ; affichage P joueur → P adversaire avec les deux couleurs joueurs.
- Ressources locales : analyse étendue à R50 et R100 ; graphes Arbres/Pierres/Poissons = segment 0–50 + segment 50–100.
- Stock minier proche : deux barres par joueur, A=≤50 HEX et B=50–100 HEX, chacune segmentée par minerai.
- Massifs/lacs/rivières : gradients inversés pour que les composantes les plus grandes soient les plus foncées.
- Comparaison A/B : Terre, Stock pierre et Stock poisson ont désormais des couleurs sémantiques cohérentes.
- Stats schema version 4.

## Validation

- 55 tests automatisés PASS.
- Smoke visuel sur SAV réel 768×768 / 10 joueurs PASS.
- Les cinq hashes protégés de la baseline v1.5 sont inchangés.

## Suite / TODO conservé

- Tooltips interactifs détaillés sur segments/barres, potentiellement généralisés à tous les graphes.
- Synchronisation optionnelle graphe ↔ vue map (désactivable).
- Imports SAV/EDM/MAP dans historique session + taille d'historique configurable.
- Export PNG plus haute définition / netteté à revoir.
- Couleurs A/B personnalisables.
- Refactor contrôlé des noms de modules `v15/v16` vers `v1_5/v1_6`.
