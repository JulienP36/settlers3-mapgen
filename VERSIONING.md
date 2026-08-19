# Versioning workflow

Current reconstructed tags / milestones:
- `v1.0` — initial MapGen GUI release;
- `v1.0.1` — Windows launcher/Python detection fix;
- `v1.1` — modes/archetypes separation and early-start architecture;
- `v1.2` — Upgraded profile implementation;
- `v1.3` — tooling/UX pass (imports, views, zoom, statistics, dynamic size/player UI);
- `v1.3.1` — preview resize crash fix + README project presentation;
- `v1.3.2` — editor-safe starts, Snow blocking and Swamp transition hardening; **validated externally on Legacy/Upgraded 4P/20P Continental 768×768**;
- `v1.4` — dark/light UI, persistent settings, overlays, improved progress/navigation, parallelogram visualization, SAV-calibrated start-territory outlines, crisp player labels, dark combobox fixes and click-to-position sliders; **validated visually by the user**.

The v1.4 line is now **validated**. It does not introduce new Legacy/Upgraded generation rules over the validated v1.3.2 engine.

Known issue tracked separately and next priority: in one game-launch control, starting supplies left on `Défaut` caused an error/crash while explicit `Low / Medium / High` presets did not.

Future releases should follow:
1. update code + references/TODO;
2. run smoke/regression tests;
3. update `CHANGELOG.md` and `RELEASE_VALIDATION.md`;
4. commit with a focused message;
5. create an annotated version tag once the release is explicitly promoted;
6. push branch + tags;
7. optionally attach release ZIP and large binary checkpoints to a GitHub Release or Git LFS.
