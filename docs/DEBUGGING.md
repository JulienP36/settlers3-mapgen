# Settlers III MapGen — Debugging and validation

This guide keeps bug reports reproducible and separates source, packaging, parser, UI and game-side failures.

## First checks

From the project root, record:

- the visible application version and the exact archive/folder name;
- Windows version and whether the run is source-based or packaged;
- the action sequence before the failure;
- the source file format, map dimensions and player count when relevant;
- the complete error dialog or traceback as text, plus a screenshot when layout or dialog context matters;
- whether the same file works in the official editor or game.

Do not rename a failing map before recording its original name. Do not commit private `.SAV` files or unreviewed external assets.

## Standard validation commands

Install dependencies, then run:

```text
python -m pytest -q
python tests/run_smoke.py
python run_gui.py --self-test
```

Their roles are distinct:

- pytest covers UI helpers, formats, analysis, cache behavior and regression contracts;
- `tests/run_smoke.py` generates the protected v1.5 reference case, checks all hard validators and verifies the exported binary checksum;
- `--self-test` imports the real GUI runtime chain and reads every required packaged resource.

After significant UI/tooling work, verify the five protected hashes listed in `PROJECT_WORKFLOW.md`. A local PASS never replaces Windows/UI or official editor/game validation where those layers are relevant.

## Deterministic source package

Build a candidate with one explicit root folder:

```text
python tools/package_source.py --output ../SETTLERS3_MAPGEN_V1_8_DEV_11_SOURCE.zip --root-name mapgen_v1_8_DEV_11
```

The builder rejects missing required files, unsafe paths, multiple roots, corruption and known local-output paths. For release confidence, extract into a new directory and rerun both pytest and `run_gui.py --self-test` from that extracted copy.

## Failure domains

| Symptom | First diagnostic area | Evidence to keep |
|---|---|---|
| GUI does not start | dependency/runtime import or resource paths | terminal traceback and `--self-test` JSON |
| Only the packaged executable fails | PyInstaller dependency/resource collection | self-test report, build log, extracted directory listing |
| Import dialog rejects a map | `binary.py` parser and exact source format | original file, extension, size, checksum, full traceback |
| Preview is wrong but import succeeds | `preview.py`, projection and view options | source file, selected view/projection, real screenshot |
| Statistics disagree | `stats_analysis.py` and map channels | source file, exported JSON/CSV, expected count and method |
| History loses or reorders a map | cache identity, V/A/B/M roles and visual order | capacity, row order, role badges and exact action sequence |
| Editor or game rejects an export | scaffold compatibility, player metadata or checksum | exported EDM/MAP, editor/game step and exact error |

## EDM import investigation — v1.9 DEV_1 priority

Some `.EDM` files load correctly while others fail. This is not yet reduced to one cause and may predate v1.8 DEV_11_R1. Because v1.9 ID archaeology will use controlled `.EDM` files, its first DEV must resolve this before beginning the ID experiments.

For each failing and working comparison file, preserve:

1. original filename and SHA-256;
2. file size and whether the official editor opens it;
3. how it was created or exported, when known;
4. the full MapGen traceback/error text;
5. the user-provided screenshot showing the failure context;
6. the result of parsing the same file with a minimal read-only diagnostic;
7. a structurally similar working `.EDM` where available.

Diagnosis must remain read-only until the structural difference is demonstrated. Do not “repair” the file, relax bounds blindly or invent missing parts. Once reproduced, add the smallest non-private fixture that proves the relevant structure, or a synthetic fixture only when every byte used by the test is derived from a confirmed format rule.

## History protection investigation

When testing eviction, distinguish these events:

- displaying an existing history map moves `V` but does not change visual order;
- assigning A/B or toggling `M` changes protection roles without changing visual order;
- a real generation cache hit updates LRU recency but not visual order;
- a simple new generation automatically becomes the Viewer, moving `V` to the new result;
- if all remaining entries are protected, the insertion may evict the former Viewer after it loses `V`, or leave the new result outside history when no evictable retained entry exists under the current state.

Always report the capacity, visible row order and V/A/B/M roles before and after the action.

## Bug-report handoff template

```text
Version/archive:
Windows/source or executable:
Action sequence:
Expected result:
Actual result:
File format/name/SHA-256:
Official editor/game result:
Error text or traceback:
Screenshot/reference:
Reproduces after fresh extraction: yes/no
```

Never place credentials, personal paths that should remain private, or proprietary files in a public issue without review.
