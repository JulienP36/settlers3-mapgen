# Settlers III MapGen — Project Workflow

> **CANONICAL PROJECT WORKFLOW — READ THIS AT THE START OF EVERY WORK SESSION.**
>
> This file describes how the project is developed, validated, documented, checkpointed and released. It is intentionally separate from the generation rules themselves.

## 1. Mandatory session start

Before changing code, data, references or release metadata:

1. read `PROJECT_WORKFLOW.md`;
2. read `references/SETTLERS3_CURRENT_SNAPSHOT.md`;
3. read `TODO_MAPGEN.md`;
4. identify the correct working branch;
5. inspect the latest relevant DEV/RC notes if the current work follows one;
6. if the task touches map generation, regeneration, EDM/MAP export or generation rules, also read `references/SETTLERS3_PREGEN_READ_FIRST.md` and all references it requires.

Do not rely on conversation memory alone when the repository contains a newer canonical state.

## 2. Permanent branches

The repository uses three permanent branches:

- `main` = **STABLE only**;
- `rc` = current **Release Candidate** under validation;
- `dev` = current **development** branch and frequent recovery checkpoints.

Normal flow:

`dev` → `rc` → `main`

Rules:

- normal feature work goes to `dev`;
- a coherent/tested DEV checkpoint should be pushed frequently;
- `rc` is updated only when a build is explicitly promoted for external validation;
- no new feature work is added directly to an RC under validation;
- `main` changes only after the RC is validated as STABLE;
- temporary `feat/*`, `fix/*`, `research/*` branches are allowed when useful, but must be audited for unique commits before deletion.

Detailed version/tag/release rules remain in `VERSIONING.md`.

## 3. Checkpoint policy

A DEV checkpoint should be committed to `dev` whenever at least one of these is true:

- a coherent feature or correction is working;
- automated tests are green after a meaningful change;
- a risky/refactoring phase is about to begin;
- an external/user validation has just been received;
- the current conversation/session has become long enough that context loss would be costly;
- several related source files have changed and represent a recoverable state.

Do not wait for RC/STABLE to preserve work.

At each meaningful checkpoint, update `references/SETTLERS3_CURRENT_SNAPSHOT.md` if project state, known issues, next steps, validation status or protected baselines changed.

### Package ↔ branch integrity rule

A DEV/RC/STABLE build is **not considered fully checkpointed** until the tested package and the corresponding Git branch contain the same intended source/runtime/tests/docs state (excluding explicitly ignored build artifacts, caches and release-only binaries).

Before announcing a checkpoint as durable:

1. run the relevant tests from the packaged source tree;
2. verify protected hashes;
3. verify the archive integrity;
4. synchronize the affected source/runtime/tests/docs to the target branch;
5. compare critical files or Git blob hashes when practical;
6. launch/smoke the branch checkout when the GUI/runtime changed.

If direct synchronization is technically unavailable, the snapshot must explicitly state that the ZIP is the exact runnable reference and that the branch is incomplete. Do not silently mix source files from different DEV checkpoints.

## 4. Canonical state vs history

Use these roles consistently:

- `PROJECT_WORKFLOW.md` = how to work on the project;
- `references/SETTLERS3_CURRENT_SNAPSHOT.md` = current resumable state;
- `TODO_MAPGEN.md` = forward-looking roadmap/tasks;
- `VERSIONING.md` = DEV/RC/STABLE, branches, tags and releases;
- `CHANGELOG.md` = published/version history;
- `RELEASE_VALIDATION.md` = validation evidence for a release candidate/stable release;
- `references/SETTLERS3_PREGEN_READ_FIRST.md` = mandatory generation-specific entry point;
- `references/SETTLERS3_MAPGEN_REFERENCE_v15_LONGPLAY_RULES.md` and subsystem references = canonical technical/generation rules;
- old dated `SETTLERS3_SNAPSHOT_*` files = historical checkpoints only.

A current snapshot never silently overrides a validated technical rule. If there is a conflict, update the relevant canonical reference explicitly.

## 5. Protected generation baseline

The v1.5 generation engine is validated and must remain unchanged unless a task explicitly requires a generation change.

Protected files and expected SHA-256:

- `s3mapgen/generator_v15.py` — `3bbc9180719ebfae2bc37b29d81025731dc821e861c7b0e66894f7460f296090`
- `s3mapgen/generator.py` — `1b73f2536c6db75dfb3856a1667d0b619d3462d9c0efa14f406c78a05556be77`
- `config/legacy_768_v1.json` — `bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85`
- `config/upgraded_768_v1.json` — `11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441`
- `data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz` — `fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d`

For UI, Stats, tooling, parser or documentation work, these hashes should remain unchanged. If one changes unexpectedly, stop and investigate before publishing a checkpoint.

## 6. Validation before checkpoint

Run the tests relevant to the change. For a normal DEV checkpoint, prefer the full automated suite when practical.

For generation-sensitive work also run the validators and checks required by `SETTLERS3_PREGEN_READ_FIRST.md`.

A test PASS is not equivalent to editor/game validation. For release promotion, use the validation hierarchy appropriate to the feature: parser/checksum → automated tests → official editor → View Map/in-game → SAV runtime → long-play where relevant.

## 7. Build naming

Use the naming convention from `VERSIONING.md`:

- development: `mapgen_v1_7_DEV_5`, `SETTLERS3_MAPGEN_V1_7_DEV_5_YYYYMMDD.zip`;
- release candidate: `mapgen_v1_7_RC_1`, `SETTLERS3_MAPGEN_V1_7_RC_1_YYYYMMDD.zip`;
- stable: `mapgen_v1_7_STABLE`, `SETTLERS3_MAPGEN_V1_7_STABLE_YYYYMMDD.zip`.

Do not use ambiguous names such as `v17_release`.

Internal module names should also prefer explicit dotted-version spelling with underscores (`v1_5`, `v1_6`) rather than ambiguous compact spellings (`v15`, `v16`) when modules are next migrated/refactored. Existing validated filenames are not renamed casually because imports/tests/package entry points must be migrated together.

## 8. RC promotion

Promote `dev` to `rc` only when the intended feature set is coherent and ready for explicit validation.

Before promotion:

- update the current snapshot;
- update TODO/notes affected by the candidate;
- run the full relevant automated suite;
- verify protected hashes;
- package the RC;
- record the package SHA-256;
- verify package ↔ branch integrity;
- keep further feature development on `dev`, not on the RC under validation.

## 9. STABLE promotion

After user/external validation of an RC:

1. freeze feature work for that release;
2. clean temporary artifacts;
3. update README, TODO, canonical references and snapshot;
4. run full tests and non-regression checks;
5. update CHANGELOG and RELEASE_VALIDATION;
6. build the STABLE package and manifest/hash;
7. promote validated state to `main`;
8. verify GitHub content completeness and package ↔ branch integrity;
9. create annotated tag `vX.Y` on the complete STABLE commit;
10. publish the GitHub Release and official STABLE ZIP;
11. only the GitHub Release channel is considered by the updater.

## 10. Updater policy

The updater must follow **GitHub Releases only**, not `main`, `dev` or `rc`.

Current updater behavior is intentionally conservative:

- query the latest published Release;
- prefer the official `SETTLERS3_MAPGEN_*_STABLE_*.zip` asset;
- download into `updates/`;
- never overwrite/extract/install automatically.

Future updater work may add version comparison, SHA-256 verification, atomic extraction, preference preservation and rollback.

## 11. Documentation update policy

Update the living documents when their domain changes:

- current development/recovery state → `references/SETTLERS3_CURRENT_SNAPSHOT.md`;
- task priorities → `TODO_MAPGEN.md`;
- branch/tag/release mechanics → `VERSIONING.md`;
- generation/gameplay rule → appropriate canonical reference;
- generation preflight list → `SETTLERS3_PREGEN_READ_FIRST.md`;
- published release history → `CHANGELOG.md`;
- stable release evidence → `RELEASE_VALIDATION.md`.

Do not create a new dated snapshot for every small change. The living current snapshot is updated in place; dated snapshots are reserved for historical milestones worth preserving.

## 12. Context-loss recovery procedure

If a conversation ends or context is lost:

1. inspect branch `dev` first;
2. read `PROJECT_WORKFLOW.md`;
3. read `references/SETTLERS3_CURRENT_SNAPSHOT.md`;
4. read `TODO_MAPGEN.md`;
5. inspect the latest DEV notes/commit history;
6. if touching generation, read `SETTLERS3_PREGEN_READ_FIRST.md` and required canonical references;
7. verify tests/protected hashes before continuing risky work;
8. resume from repository state, not from guessed conversation history.

## 13. Project-wide non-negotiables

- Never use imaginary/generated Settlers III map visuals; previews must be deterministic renders from real EDM/MAP/SAV data.
- Unknown binary/object semantics remain unknown until calibrated; do not invent labels or rules.
- Internal technical IDs may remain in code, but user-facing labels should use known semantics. In particular object ID `84` is a **tree sapling / pousse d'arbre**, not a user-facing name `SmallTree84`.
- Preserve validated generation behavior unless an explicit generation task requires change.
- Prefer frequent recoverable Git checkpoints over relying on chat history.
