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

État consigné le 25 août 2026 : les neuf Topics ci-dessus ont été appliqués à `JulienP36/settlers3-mapgen`.

## Hors périmètre de la découvrabilité

- L’entrée anglaise est une tâche de présentation du projet.
- Les captures réelles sont une tâche de présentation du README.
- Les GitHub Releases sont une tâche de publication STABLE.
- Aucun de ces éléments ne doit être transformé automatiquement en campagne SEO ou communautaire.

## Dossier `references/`

Le dossier local `references/` est volontairement ignoré pour les commits et
push GitHub pendant la réorganisation des notes d’audit et de récupération. Il
reste conservé dans les ZIP sources remis avec chaque candidate : le script de
packaging le réintègre explicitement même lorsqu’il est ignoré par Git. Les
ressources nécessaires à l’exécution, comme les marqueurs de départ, vivent
dans `data/` et restent donc disponibles dans le dépôt public.

## README publication checklist

- French remains the primary historical README.
- `README_EN.md` is linked at the top of both language entrypoints.
- The substantial ChatGPT/OpenAI implementation assistance remains explicit.
- Current STABLE and active DEV state are not confused.
- Limits are visible: native sizes capped at 768, small-map viability, supported SAV-to-new-map conversion and omitted game-session entities; see MAP_EXPORT.md.
- Screenshots show the current UI and real generated/imported map data only.
- Each screenshot is checked for personal paths, private filenames and obsolete version labels.
- Visual provenance is added to `references/SETTLERS3_VISUAL_ASSET_PROVENANCE.md` before publication.

## Real screenshots integrated

The README uses seven real Windows captures supplied by the owner: six DEV11
R11 captures (team islands, generator settings, custom archetype, mask editor,
configurations and resource charts), plus the final R13 batch capture with
shared settings, cache reuse and A/B assignments, integrated in R14. PNGs are
copied unchanged. Historical v1.8 captures remain in the recovery references;
the truncated Statistics PNG is not displayed. Provenance:
references/SETTLERS3_VISUAL_ASSET_PROVENANCE.md.

The About/Topics state above records the application reported on 25 August;
check the live repository again at publication. No repository setting was
queried or changed during this documentation review.

## Release hygiene

- DEV checkpoints are not GitHub Releases. Historical RC names remain historical.
- STABLE receives an annotated tag, release notes, source package, portable Windows package and SHA-256 values.
- Release artifacts must be built from the validated source state, not from an unrelated working directory.
- All qualification, fixes, polish, optimization and documentation happen on `dev` before direct STABLE publication; no separate RC phase (owner decision, 14 October 2026).
- Community outreach is optional and never a prerequisite for development.


## Checkpoint DEV9 — 2026-10-04

DEV9 completes the validated Large islands scope. The unsuffixed checkpoint
is published to `dev` with source/tests/public notes. `references/` and local
DEV9 candidate map examples remain outside the Git push, inside the recovery
ZIP. No tag or Release. Earlier out-of-scope DEV9 work moves to DEV10 for
prioritization; This is historical: Small islands is no longer a 2.0 task; follow RELEASE_2_0_SCOPE.md. See `DEV_9_CHECKPOINT.md`.
