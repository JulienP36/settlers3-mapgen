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

## Recovery after context loss
1. Open branch `dev`.
2. Read this workflow.
3. Read `SETTLERS3_CURRENT_SNAPSHOT.md`.
4. Read TODO + latest DEV notes.
5. Verify current `dev` tip and protected hashes before making generation-sensitive changes.
6. Continue from the "Next work" section of the living snapshot unless the user gives a newer explicit direction.

## Release path
See `VERSIONING.md` for the full release checklist. STABLE publication is intentionally conservative: validate RC, update docs/tests, package, verify source state, promote to `main`, tag, then publish GitHub Release.
