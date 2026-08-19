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
- `v1.5` — **VALIDÉE / STABLE** pour le périmètre Continental 768 calibré : audit complet Legacy/Upgraded, hydrologie/minerais/biomes/objets séparés, géométrie minière v7 no-gap canonique, pool d'arbres natif complet, clusters de départ Upgraded sur la bordure du territoire initial, Building Stones `115..127` variées avec stock réel séparé des ancres, ID127 natif/constructible dans le modèle statique, récifs éloignés des bords, nouveaux validateurs et exports `MapGenV1_5`.

La **v1.5 est la release stable actuelle**. Sa génération de référence `S3_V1_5_V7NOGAP_CORRECTED_UPGRADED_4P_768x768_seed_2026082202` a passé l'ouverture éditeur, la validation des starts et View Map/in-game sans crash. Le micro-test pratique ID127 reste facultatif/non bloquant.

Correctifs validés et conservés dans v1.5 :
- Goods Default : `Legacy=Medium/2`, `Upgraded=High/3`, fallback Medium ;
- starts placés tôt et protégés ;
- Water accessibility ;
- Snow intérieur non traversable ;
- footprint actif des Building Stones ;
- ID127 épuisé exclu du stock et footprint statique libéré ;
- géométrie minière Upgraded v7 no-gap canonique ;
- marge de 2 cellules pour les récifs Upgraded.

Ordre de développement retenu après v1.5 :
1. terminer les TODO UI/outillage ;
2. enrichir massivement l'onglet Statistiques ;
3. calibrer et valider les tailles 384–704 ;
4. démarrer l'archétype Large Islands / Grandes îles ;
5. reprendre ensuite modificateurs et autres évolutions.

Future releases should follow:
1. update code + references/TODO;
2. run smoke/regression tests;
3. update `CHANGELOG.md` and `RELEASE_VALIDATION.md`;
4. commit with a focused message;
5. create an annotated version tag once the release is explicitly promoted;
6. push branch + tags;
7. optionally attach release ZIP and large binary checkpoints to a GitHub Release or Git LFS.
