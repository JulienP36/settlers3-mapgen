# Changelog

## v1.1 — 2026-08-18

- séparation explicite **Generation Mode** / **Archetype** ;
- noms de travail : **Legacy / Upgraded / Custom** ;
- archétypes réservés : Continental / Large Islands / Small Islands ;
- Legacy + Continental reste le seul couple activé ;
- Upgraded et Custom sont visibles mais refusés proprement tant qu'ils ne sont pas implémentés ;
- starts déplacés très tôt dans le pipeline, immédiatement après le macro-layout ;
- réservation explicite de leur zone avant hydrologie détaillée ;
- redistribution micro-water interdite dans la zone protégée des starts ;
- métadonnées enrichies : mode, archétype, `starts_placed_early` ;
- CLI : `--mode` et `--archetype` ;
- noms d'exports incluent mode + archétype ;
- nouveaux tests de non-régression architecture/starts/20P.

## v1 — 2026-08-18

Première GUI persistante, aperçu réel, génération, validators et export EDM/MAP.
