# Settlers III MapGen — TODO programme

## État de validation

- [x] **v1.5 VALIDÉE / STABLE** pour Continental 768×768.
- [x] Référence finale : `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202`.
- [x] Starts / éditeur / View Map / in-game / aucun crash.
- [x] Minerais Upgraded géométrie **v7 no-gap** verrouillée.
- [x] Legacy / Upgraded séparés.
- [x] Building Stones 115..127 et ID127 constructible gérés.
- [x] Bonus de départ Upgraded validés.
- [x] **v1.6 STABLE UI/outillage** : validation utilisateur terminée (RC_9 validée).

## Règle de release

**Ne pas modifier la génération v1.5 validée sans raison explicite.**

v1.6 est une surcouche UI/outillage ; `generator_v15.py` reste le moteur de référence.

## UX / outillage — v1.6

- [x] Import EDM / MAP / SAV ; export EDM+MAP 768.
- [x] Global / Heightmap / Ressources / Territoires.
- [x] Chemins / Terrain28 et Terrain22 runtime.
- [x] Cultures.
- [x] Heatmap ressources.
- [x] FR/EN persistant.
- [x] Inspecteur exact de cellule au survol.
- [x] Zoom / drag / projection / recentrage.
- [x] Thème sombre/clair ; combobox lisibles ; sliders click-to-position.
- [x] Cache transparent LRU mémoire de session, 8 générations.
- [x] Historique de session.
- [x] Comparaison A/B légère avec conservation du contexte visuel.
- [x] Raccourcis configurables/persistants + conflits + reset.
- [x] Aide F1 dynamique.
- [x] Palette P1..P20 validée visuellement ; P9 quasi blanc/ivoire et contours noirs validés.
- [x] Contour de zone de départ d'origine sur import SAV : bloc joueur SAV + masque natif exact 3500 cellules, validé visuellement.
- [ ] Comparaison A/B avancée côte-à-côte/diff uniquement si l'usage réel le justifie — non prioritaire.
- [ ] Étendre éventuellement les commandes rebindables après retour d'usage.

## Après validation v1.6 — GIGA passe Statistiques

- [ ] nombre exact de cellules par Terrain ID ;
- [ ] quantité de chaque objet/ressource ;
- [ ] stock total exploitable Building Stones ;
- [ ] distribution des états 115..127 ;
- [ ] graphes des ressources minières : cases + stock réel ;
- [ ] densités par 1000 cellules de land ;
- [ ] ratios land/ocean, biomes, eau intérieure, forêts, ressources ;
- [ ] blobs / massifs / lacs / rivières / clusters ;
- [ ] distances aux starts ;
- [ ] percentiles utiles ;
- [ ] suivi Terrain24 / Terrain22 / Terrain28 ;
- [ ] autres métriques et graphes pertinents tant que lisibles/exploitables.

## Calibration multi-tailles — après UI + Stats

Continental, une taille à la fois : 384×384 → 448×448 → 512×512 → 576×576 → 640×640 → 704×704 → reconfirmation 768×768.

Pour chaque taille : starts, morphologie, montagnes/neige, minerais, arbres, Building Stones, poissons, marais, désert, décorations, récifs, rivières/lacs, quotas et stabilité éditeur/View Map/in-game.

Après validation du cycle Continental : préparer **v2.0** avec premier exécutable Windows portable et build reproductible.

## Après Continental

- [ ] Large Islands / Grandes îles.
- [ ] Constituer/analyser les références natives nécessaires.
- [ ] Small Islands / Petites îles ensuite.

## À préserver

- Archetype = macro-géographie.
- Legacy/Upgraded = contenu, règles, balance, ressources et objets.
- Starts placés tôt et protégés.
- Upgraded conserve impérativement les minerais v7 no-gap.
- Aucun aperçu imaginaire.
- Toute image/preview = rendu déterministe réellement issu des données EDM/MAP/SAV.
- Ne jamais repartir d'une version invalidée du générateur.

## Futur UI / analyse

- [ ] Vue dédiée Forêts / Carrières.
- [ ] Éventuellement déplacer les contours initiaux SAV vers une vue dédiée pour épurer Global.
- [ ] Nids d'abeilles amazones uniquement après identification IDs/runtime.
- [ ] Passe complète de nomenclature des IDs et intégration inspecteur.
- [ ] Refonte générale UI et section **Outils Map**.
- [ ] Loupe flottante près du curseur, bouton + raccourci.
- [ ] Passe dédiée police des labels joueurs P 1..P 20 avec propositions visuelles.
