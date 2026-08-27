# Settlers III MapGen — v1.9 development log

This log keeps accepted outcomes and regression lessons. Candidate-by-candidate
implementation detail remains available in Git history and is not repeated here.

## DEV_1 — tolerant EDM terminal padding

Validated on Windows: 2026-08-26
Tracking: GitHub Issue #4, closed after DEV_2 publication.

- Reproduced `Part scan did not end at EOF` on two real EDM files.
- Confirmed valid version-10 structures and checksums with one or three opaque
  bytes after the terminal `type 0 / size 8` part for DWORD alignment.
- Read-only EDM/MAP import accepts only this bounded 1–3-byte case. Scaffold
  reconstruction remains strict.
- Both original files load under Windows: 256×256/20 starts and 768×768/10
  starts.
- The protected v1.5 generation engine was not modified.

## DEV_2 — architecture restructuring

Validated on Windows: 2026-08-27
Published on `dev`: commit `9494a6a`.

| Slice | Accepted outcome |
|---|---|
| R1/R2 | Extracted UI primitives and catalogues. R1 exposed a missing residual `ImageDraw` import; R2 restored it and made Ruff `F821` mandatory for structural moves. |
| R3 | Split i18n catalogues by feature and moved viewer options to their owner. |
| R4 | Removed active `gui_v*`/`generator_v*` names; introduced stable application, generation, Batch and History packages. |
| R5 | Classified runtime code under `application/`, `generation/` and shared lower-level `map_data/`; added dependency-direction contracts. |
| R6 | Extracted Viewer, Analysis/Graphs, Exports and Shortcuts/Help controllers; reorganized tests by subsystem. |
| R7 | Replaced the historical window inheritance chain with one `ShellWindow`, explicit controllers and a single generator factory in `runtime.App`. |
| R8 | Removed the disposable legacy header/progress state and seven obsolete or duplicated tests. |

Final state:

- `s3mapgen/` root contains only package/version metadata.
- The protected engine lives under `generation/`; binary formats and shared map
  structures live under `map_data/`; GUI/runtime responsibilities live under
  `application/`.
- `application/main_window.py` fell from 3168 to 372 cohesive lines.
- Batch, History, Viewer, Analysis, Exports, Imports, Shortcuts/Help, Settings,
  Theme, Language, Tasks and generation workflow have explicit controllers.
- 243 current tests pass with no exact duplicate body or historical revision
  name. Source-shaped GUI contracts remain tracked for gradual widget-level
  replacement, starting with Batch and History.
- Final runtime behavior is identical to the Windows-validated R8 candidate;
  protected hashes and Legacy 4P / Upgraded 20P reference outputs are unchanged.
- A compact root `AGENTS.md` routes work to repository-owned instructions and
  only the references relevant to the current task.

Release decision:

- v1.8 remains a DEV-only series; the missed v1.8 release will not be recreated.
- No new RC/STABLE is planned before v1.10 fixes real generation morphology and
  diversity.
