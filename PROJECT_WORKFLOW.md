# Settlers III MapGen — Project Workflow

> **CANONICAL PROJECT WORKFLOW — READ THIS AT THE START OF EVERY WORK SESSION.**

This file defines how the project is resumed, developed, validated, checkpointed and released. It complements the technical generation references.

## Session start
1. Read `PROJECT_WORKFLOW.md`.
2. Read `references/SETTLERS3_CURRENT_SNAPSHOT.md`.
3. Read `TODO_MAPGEN.md`.
4. Work on the correct permanent branch.
5. If generation/export rules are touched, also read `references/SETTLERS3_PREGEN_READ_FIRST.md` and the references it requires.

Do not rely on conversation memory when the repository contains a newer canonical state.

## Permanent branches
- `main` = STABLE only.
- `dev` = current development + frequent tested recovery checkpoints.
- `rc` = Release Candidate currently under external validation.

Normal promotion flow: `dev` → `rc` → `main`.

## Checkpoint policy
Checkpoint `dev` frequently whenever a coherent unit of work is testable or when a long session has materially changed the project. A checkpoint should normally include affected code, tests, TODO/changelog/reference updates when relevant, and the living snapshot when the resumable project state changed.

DEV/RC builds do not need tags or GitHub Releases. STABLE receives an annotated `vX.Y` tag and GitHub Release.

## Standing authorization for `dev`

The project owner authorizes Codex to create, modify, rename and delete project files, then make non-destructive commits and pushes to the public repository `JulienP36/settlers3-mapgen` on branch `dev`, without requesting confirmation for every routine checkpoint.

This standing authorization covers source code, tests, documentation, TODOs, snapshots, DEV notes, technical references and visual material explicitly provided by the project owner. Unless the owner states otherwise, files and images supplied for integration into this project may be published in that public repository.

After every functional change, run the relevant validations and verify protected assets before pushing.

This standing authorization does **not** cover `main`, tags, GitHub Releases, force-pushes, history rewrites, repository or branch deletion, repository settings, secrets/credentials, personal data, license changes, or publication of external assets whose provenance or rights are uncertain. Those actions always require explicit authorization.

## Protected v1.5 baseline
Do not alter these without an explicit generation-engine reason:
- `s3mapgen/generator_v15.py` — `3bbc9180719ebfae2bc37b29d81025731dc821e861c7b0e66894f7460f296090`
- `s3mapgen/generator.py` — `1b73f2536c6db75dfb3856a1667d0b619d3462d9c0efa14f406c78a05556be77`
- `config/legacy_768_v1.json` — `bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85`
- `config/upgraded_768_v1.json` — `11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441`
- `data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz` — `fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d`

Check these hashes after significant tooling/UI/Stats work.

## Validation discipline
- Run automated regression tests before checkpointing a meaningful build.
- Smoke-test real EDM/MAP/SAV data when the changed code parses or analyses those formats.
- UI visual changes still need Windows/user validation before RC/STABLE.
- Never use imaginary/generated map artwork; map previews must be deterministic renders from actual EDM/MAP/SAV data.

## Documentation roles
- `PROJECT_WORKFLOW.md`: how to work and recover.
- `references/SETTLERS3_CURRENT_SNAPSHOT.md`: current resumable state, updated in place.
- `TODO_MAPGEN.md`: roadmap / remaining work.
- `VERSIONING.md`: detailed version/tag/release rules.
- `references/SETTLERS3_PREGEN_READ_FIRST.md`: mandatory entry point before touching generation/map bytes.
- dated `SETTLERS3_SNAPSHOT_*`: historical checkpoints only.

## GitHub Issues
- `TODO_MAPGEN.md` reste la roadmap exhaustive et accueille les idées lointaines, hypothèses et sujets encore flous.
- Une Issue est réservée à un bug, une amélioration ou une investigation suffisamment actionnable qui doit survivre à la passe courante ; ne pas en créer lorsqu’une tâche établie sera traitée immédiatement.
- Les Issues peuvent être rédigées en français. Conserver les labels et conventions GitHub en anglais.
- Les modèles Bug, Amélioration et Investigation sont proposés, mais les Issues libres restent autorisées pour enregistrer rapidement une idée depuis un téléphone.
- Ne pas recréer rétroactivement les problèmes déjà corrigés : les notes DEV et l’historique Git suffisent.
- Pour une correction nécessitant une validation Windows ou visuelle, référencer l’Issue dans le premier commit puis ne la fermer qu’après validation utilisateur.
- Créer des milestones uniquement pour les versions dont le focus est suffisamment stable ; éviter les milestones par révision DEV/R.

## Recovery after context loss
1. Open branch `dev`.
2. Read this workflow.
3. Read `SETTLERS3_CURRENT_SNAPSHOT.md`.
4. Read TODO + latest DEV notes.
5. Verify current `dev` tip and protected hashes before making generation-sensitive changes.
6. Continue from the "Next work" section of the living snapshot unless the user gives a newer explicit direction.

## Release path
See `VERSIONING.md` for the full release checklist. STABLE publication is intentionally conservative: validate RC, update docs/tests, package, verify source state, promote to `main`, tag, then publish GitHub Release.

## Post-v1.7 discoverability / publication workflow
The project remains primarily a personal tool, but public releases should be discoverable by Settlers III players who are actively looking for this kind of utility. Treat discoverability as release hygiene, not as an SEO/marketing campaign.

After v1.7 STABLE:
1. Review the GitHub repository **About** description and keep it short, explicit and keyword-natural.
2. Add useful repository topics such as `settlers-iii`, `settlers3`, `map-generator`, `procedural-generation`, `reverse-engineering`, `python` and other format-specific topics only when they genuinely fit.
3. Preserve the French README while adding an accessible English entry point/summary (or a clearly linked `README_EN.md`). Naturally include useful search terminology such as `Settlers III map generator`, `Settlers 3 procedural map generator`, `Siedler III Kartengenerator`, `.EDM`, `.MAP` and `.SAV`; never keyword-stuff.
4. Continue publishing **STABLE versions as proper GitHub Releases** with a version tag, downloadable package and readable release notes. DEV/RC remain non-release checkpoints.
5. Community outreach (Discord/wiki/map sites) is optional and only if the project owner later chooses to present the tool publicly; do not make it a prerequisite for development or releases.
## v1.8 accessibility / public-facing rules
- Public-facing README material must transparently mention the substantial use of ChatGPT/OpenAI in implementation assistance, especially backend, analysis and reverse-engineering tooling, while keeping project direction/validation accurately attributed to the project owner.
- Prioritize a self-contained Windows `.exe` during v1.8 so external users do not need to install Python/pip/dependencies.
- Evolve the GitHub-Releases updater for packaged executable updates; preserve user settings and verify release integrity.
- **No AI-generated imagery/assets for this project.** Application/executable artwork and icons are to be manually created (final icon planned as user-drawn pixel art). Deterministic previews rendered from actual EDM/MAP/SAV data remain allowed and required.
