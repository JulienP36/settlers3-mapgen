# Settlers III MapGen v1.1 — release validation

Date : 2026-08-18

## Résultat automatisé

- `pytest`: **6/6 tests PASS**.
- 4P Legacy/Continental : HARD checks PASS.
- 20P Legacy/Continental : HARD checks PASS.
- starts placés avant `hydrology.micro_water_cleanup` : PASS.
- les 20 starts restent valides après pipeline complet : PASS.
- export checksum EDM : PASS.
- Upgraded non implémenté : refus explicite PASS.
- Custom non implémenté : refus explicite PASS.

## Architecture désormais vérifiée

```text
Archetype.macro_layout
    -> starts.maximin_early
    -> starts.reserve_zones
    -> hydrology / terrain detail
    -> resources / balance
    -> objects
    -> validators
```

## Important

Cette release ne prétend pas encore fournir Upgraded. Elle garantit seulement que l'architecture est prête à le recevoir sans mélanger la macro-forme de l'archétype avec les règles du mode de génération.
