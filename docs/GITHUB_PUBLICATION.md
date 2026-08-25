# Settlers III MapGen — découvrabilité et publication GitHub

La **découvrabilité** visée ici correspond aux emplacements GitHub jusque-là inutilisés dans la section About du dépôt : sa description courte et ses Topics. Leur contenu a été appliqué au dépôt public le **2026-08-25**, après autorisation explicite du propriétaire.

## Description About appliquée

> Procedural Settlers III map generator and analysis workbench for EDM, MAP and SAV files.

Cette description courte indique immédiatement l’objet réel du dépôt.

## Topics appliqués

- `settlers-iii`
- `settlers3`
- `siedler-iii`
- `map-generator`
- `procedural-generation`
- `reverse-engineering`
- `python`
- `tkinter`
- `game-tools`

Ne multiplier ni les variantes orthographiques ni les tags populaires sans rapport. Le cœur attendu reste `settlers-iii` ou `settlers3`, `map-generator`, `procedural-generation` et `reverse-engineering` ; les autres Topics restent optionnels.

État appliqué : les neuf Topics ci-dessus sont actifs sur `JulienP36/settlers3-mapgen`.

## Hors périmètre de la découvrabilité

- L’entrée anglaise est une tâche de présentation du projet.
- Les captures réelles sont une tâche de présentation du README.
- Les GitHub Releases sont une tâche de publication STABLE.
- Aucun de ces éléments ne doit être transformé automatiquement en campagne SEO ou communautaire.

## README publication checklist

- French remains the primary historical README.
- `README_EN.md` is linked at the top of both language entrypoints.
- The substantial ChatGPT/OpenAI implementation assistance remains explicit.
- Current STABLE and active DEV state are not confused.
- Limits are visible: generation calibration, read-only SAV handling and partial EDM import defect.
- Screenshots show the current UI and real generated/imported map data only.
- Each screenshot is checked for personal paths, private filenames and obsolete version labels.
- Visual provenance is added to `references/SETTLERS3_VISUAL_ASSET_PROVENANCE.md` before publication.

## Real screenshots integrated

The v1.8 README set now covers:

1. main generation and Viewer;
2. Statistics with a real map loaded;
3. Charts with a meaningful real dataset;
4. Batch generation and its real previews.

The four files are stored in `docs/screenshots/` and recorded in `references/SETTLERS3_VISUAL_ASSET_PROVENANCE.md`. They are recent Windows captures of the actual application. The Batch image deliberately includes one cache-reuse status; it does not pretend that the current generator already provides full morphological diversity. Do not reuse format-reference images, the v1.10 seed-diversity evidence or invented illustrations as generic product screenshots.

## Release hygiene

- DEV and RC checkpoints are not GitHub Releases.
- STABLE receives an annotated tag, release notes, source package, portable Windows package and SHA-256 values.
- Release artifacts must be built from the validated source state, not from an unrelated working directory.
- The RC phase may fix defects, polish, optimize and improve documentation after feature freeze.
- Community outreach is optional and never a prerequisite for development.
