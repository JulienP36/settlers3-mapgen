# Versioning workflow

Current reconstructed tags / milestones:
- `v1.0` — initial MapGen GUI release;
- `v1.0.1` — Windows launcher/Python detection fix;
- `v1.1` — modes/archetypes separation and early-start architecture;
- `v1.2` — Upgraded profile implementation;
- `v1.3` — tooling/UX pass (imports, views, zoom, statistics, dynamic size/player UI);
- `v1.3.1` — preview resize crash fix + README project presentation;
- `v1.3.2` — editor-safe starts, Snow blocking and Swamp transition hardening; **validated externally on Legacy/Upgraded 4P/20P Continental 768×768**;
- `v1.4` — dark/light UI, persistent settings, overlays, improved progress/navigation, parallelogram visualization, SAV-calibrated start-territory outlines, crisp player labels, dark combobox fixes and click-to-position sliders; **validated visually by the user**;
- `v1.5` — **candidate**: audit complet Legacy/Upgraded, hydrologie/minerais/biomes/objets séparés, pool d'arbres natif complet, nouveaux clusters de départ Upgraded sur la bordure du territoire initial, Building Stones `115..127` variées avec stock réel séparé des ancres, ID127 natif et constructible, nouveaux validateurs et exports `MapGenV1_5`.

La ligne v1.4 reste la dernière release entièrement validée/promue. La v1.5 est préparée dans le code mais **ne doit pas être taguée comme stable avant validation éditeur + View Map/in-game d'une génération fraîche**.

Correctifs déjà validés et conservés dans v1.5 :
- Goods Default : `Legacy=Medium/2`, `Upgraded=High/3`, fallback Medium ;
- starts placés tôt et protégés ;
- Water accessibility ;
- Snow intérieur non traversable ;
- footprint actif des Building Stones.

Future releases should follow:
1. update code + references/TODO;
2. run smoke/regression tests;
3. update `CHANGELOG.md` and `RELEASE_VALIDATION.md`;
4. commit with a focused message;
5. create an annotated version tag once the release is explicitly promoted;
6. push branch + tags;
7. optionally attach release ZIP and large binary checkpoints to a GitHub Release or Git LFS.
