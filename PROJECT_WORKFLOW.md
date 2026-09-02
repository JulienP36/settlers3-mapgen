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

## Context and quota budget

The repository is the canonical memory. `AGENTS.md` is the concise automatic
entry point; this workflow owns the complete operational rules. Project-level
ChatGPT instructions should point to these files instead of duplicating them.
Long conversations and old attached archives must not substitute for the
current snapshot.

- At session start, read only this workflow, the living snapshot and the exact
  active TODO section. Open other references only when the touched subsystem
  requires them.
- Never search or replay old chats when the current repository already answers
  the question. Ask for missing user evidence only when it is genuinely absent.
- Prefer narrow `rg`/targeted ranges and summarized diagnostics. Do not dump
  whole large files or unrestricted tool registries into the conversation.
- During implementation, run focused tests. Run the complete pytest suite once
  before a candidate, then the packaged/extracted self-test once. Repeat a full
  suite only after code changed materially.
- Do not rebuild, upload or preserve a new ZIP after every internal edit. Build
  one archive for the candidate actually sent to Windows and one final archive
  for a validated DEV checkpoint.
- After every validated and published DEV checkpoint, refresh the living
  snapshot and start the next distinct outcome in a fresh chat when practical.
- Keep one active candidate sheet only. Consolidate it and remove it immediately
  when the DEV is validated.
- External LLM answers supplied by the owner are unverified research inputs.
  Prefer one attached text/Markdown file per topic, extract only actionable
  claims, and validate every claim against project evidence before adoption.

Recommended minimal ChatGPT Project instruction:

> Répondre en français. Pour Settlers III MapGen, suivre `AGENTS.md`, puis le
> workflow et le snapshot vivant qu'il désigne. La dernière instruction ou
> validation explicite de l'utilisateur reste prioritaire.

## Permanent branches
- `main` = STABLE only.
- `dev` = current development, avec publication des checkpoints **DEV complets uniquement** (`DEV_1`, `DEV_2`, etc.).
- `rc` = Release Candidate currently under external validation.

Normal promotion flow: `dev` → `rc` → `main`.

## Checkpoint policy
Créer fréquemment des **points de reprise locaux** lorsqu’une unité cohérente est testable ou qu’une longue session a matériellement changé le projet. Une candidate suffixée (`DEV_X_R1`, `R2`, etc.) reste locale et peut être remplacée autant de fois que nécessaire.

Ne pousser sur `dev` que le checkpoint **DEV complet sans suffixe**, après validation utilisateur explicite de l’ensemble de son périmètre. Une correction minuscule demandée après validation peut être intégrée avant ce push final ; elle ne justifie pas la publication d’une révision intermédiaire.

Le checkpoint final doit inclure le code concerné, les tests, TODO/changelog/références utiles et le snapshot vivant à jour. Ne jamais confondre une archive de test Windows avec un checkpoint Git publiable.

DEV/RC builds do not need tags or GitHub Releases. STABLE receives an annotated `vX.Y` tag and GitHub Release.

### Mandatory living-snapshot refresh

Update `references/SETTLERS3_CURRENT_SNAPSHOT.md` immediately after every explicitly validated DEV stage/checkpoint and every validated RC or STABLE release. This refresh is mandatory before the final commit, package or push for that stage; it must record the validation result, known limitations and the actual next work.

When a suffixed local candidate such as `DEV_X_RY` is validated but its full DEV scope is not complete, update the snapshot locally without publishing that intermediate revision. Keep `TODO_MAPGEN.md`, `DEV_CANDIDATE_NOTES.md` and the changelog synchronized whenever the validation changes the known issues or next action. La validation d’une tranche ne clôt jamais implicitement la DEV entière.

Checklist obligatoire à chaque étape validée :

1. consigner le résultat réel de la validation et les anomalies/report éventuels ;
2. mettre à jour le snapshot vivant avant de fabriquer l’archive ou le commit final correspondant ;
3. synchroniser TODO, feuille de candidate, journal DEV et changelog uniquement là où l’état a réellement changé ;
4. si l’étape reste une `DEV_X_Rn`, conserver tous les changements et artefacts localement ;
5. ne publier sur `dev` qu’après clôture et validation du périmètre complet sous le nom `DEV_X` sans suffixe.

## Standing authorization for `dev`

The project owner authorizes Codex to create, modify, rename and delete project files, then make non-destructive commits and pushes to the public repository `JulienP36/settlers3-mapgen` on branch `dev`, without requesting confirmation for every routine checkpoint.

This standing authorization covers source code, tests, documentation, TODOs, snapshots, DEV notes, technical references and visual material explicitly provided by the project owner. Unless the owner states otherwise, files and images supplied for integration into this project may be published in that public repository.

After every functional change, run the relevant validations and verify protected assets before pushing.

This standing authorization does **not** cover `main`, tags, GitHub Releases, force-pushes, history rewrites, repository or branch deletion, repository settings, secrets/credentials, personal data, license changes, or publication of external assets whose provenance or rights are uncertain. Those actions always require explicit authorization.

## Protected generation and runtime baselines
Do not alter these retained baselines without an explicit generation-engine
reason. The obsolete procedural Legacy generator is absent after the DEV_2
reset; the replacement native Legacy v1 lives in the separate
`generation/generators/legacy/` package. The former 768 Legacy profile remains
only as a protected compatibility resource for packaging diagnostics, while
the active native profile is `config/generation_profiles/continental_legacy_v2.json`.
- `s3mapgen/generation/base.py` — `b2df5cc0329be2e63ba27b06501a5661547ce23f2b2ea739d3ec23de497bce88`
- `s3mapgen/generation/continental.py` — `29d2413a742e4b5f446fed0cb4eed5b362b1ead431632d4a0397c3f4ea32c4d2`
- `s3mapgen/generation/validated.py` — `cabcc24fc8a5eac99d2a9a9a5009d41addc1cc49d05815d2d3567e105f8277c5`
- `config/legacy_768_v1.json` — `bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85`
- `config/upgraded_768_v1.json` — `11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441`
- `data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz` — `fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d`

Check these hashes after significant tooling/UI/Stats work. These values are
the computed DEV_2 baseline.

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
- `references/dev_notes/V1_8_DEVELOPMENT_LOG.md`: consolidated history of accepted DEV decisions and significant failed experiments.
- `DEV_CANDIDATE_NOTES.md`: single rolling Windows-test sheet while a candidate exists; overwrite it for each R, consolidate it at DEV closure, then remove it.
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
4. Read TODO, the consolidated development log and `DEV_CANDIDATE_NOTES.md` when a candidate is active.
5. Verify current `dev` tip and protected hashes before making generation-sensitive changes.
6. Continue from the "Next work" section of the living snapshot unless the user gives a newer explicit direction.

## Release path
See `VERSIONING.md` for the full release checklist. STABLE publication is intentionally conservative: validate RC, update docs/tests, package, verify source state, promote to `main`, tag, then publish GitHub Release.

## Post-v1.7 GitHub discoverability / publication workflow

Dans ce projet, **découvrabilité GitHub** désigne précisément l’exploitation de surfaces du dépôt jusque-là inutilisées :

1. renseigner la description courte de la section **About** ;
2. activer des **Topics** pertinents (`settlers-3` ou `settlers3`, `map-generator`, `procedural-generation`, `reverse-engineering`, puis autres uniquement s’ils sont réellement utiles).

Ne pas élargir automatiquement ce chantier à une stratégie SEO, à du bourrage de mots-clés dans le README ou à une campagne communautaire.

Les éléments suivants appartiennent aussi à la finition/publication de DEV_11, mais restent des tâches distinctes de la découvrabilité GitHub :

- conserver le README français et fournir une entrée anglaise clairement liée ;
- ajouter des captures réelles et récentes de l’application ;
- publier les versions STABLE comme vraies GitHub Releases avec tag, artefacts et notes lisibles ; DEV/RC restent hors Releases.

Le partage Discord/wiki/sites de maps reste optionnel et seulement sur décision ultérieure du propriétaire.
## v1.8 accessibility / public-facing rules
- Public-facing README material must transparently mention the substantial use of ChatGPT/OpenAI in implementation assistance, especially backend, analysis and reverse-engineering tooling, while keeping project direction/validation accurately attributed to the project owner.
- Keep daily DEV work source-first through `run_gui.bat` / `run_gui.py`; do not rebuild or carry PyInstaller output during ordinary feature revisions.
- At v1.8 RC, freeze new features while still allowing fixes, polish, optimization and documentation, then produce two separate artifacts: a Python/source ZIP and an installation-free Windows x64 portable ZIP.
- Rebuild and validate the standalone Windows `.exe` and evolve the GitHub-Releases updater during RC; preserve user settings, verify release integrity and never require an installer.
- **No AI-generated imagery/assets for this project.** Application/executable artwork and icons are to be manually created (final icon planned as user-drawn pixel art). Deterministic previews rendered from actual EDM/MAP/SAV data remain allowed and required.
