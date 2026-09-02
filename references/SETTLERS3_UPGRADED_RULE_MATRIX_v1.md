# Settlers III MapGen v1.2 — Upgraded rule matrix

Date: 2026-08-18

This file records how the recovered Upgraded rules are represented in executable form.

| Rule | Source status | Program representation |
|---|---|---|
| Starts early | latest user architecture lock | pipeline + tests |
| 33-cell start footprint / slope limits | validated checkpoint | validator |
| Start technical zone protected | validated start-first lineage | pipeline |
| Start forest/stone bonus outside global quota | validated 768/10P | config contract; placement deferred with native starts |
| Controlled mini-swamp per player | validated 768/10P | config contract; placement deferred with native starts |
| Water access=1 / H=0 | long-play runtime validated | pipeline + validator |
| 0 inland water comps 1..4 | custom locked | cleanup + validator |
| Removed micro-water grows existing lake only | custom locked | cleanup |
| Rivers connected / no orphans | long-play | cleanup + validator |
| River stops at first Water | latest rule | cleanup + validator |
| River max 768=55 | 21-SAV calibration | config + validator |
| External edge deep Water7 | validated short-form rule | pipeline + validator |
| Fish after final hydro | long-play | pipeline ordering |
| Fish 32,313 cells | validated 768 | config + validator |
| Fish real Shore only, <=12 HEX, no River, no edge-derived | validated + regression fix | generator + validators |
| Fish quantity x1.30 cap15 | long-play | config + generator |
| Minerals v7 no-gap | user validated 100% | generator |
| Ore cell totals 28375/12202/8164/3098/4745 | validated 768 | config + validators |
| Ore quantity x1.30 cap15 | long-play | config + generator |
| Snow from relief: p80 / H135 / depth4 | accepted | generator |
| Adult global 1352 | validated | config + validator |
| Adult cluster share ~44%, 38 centers | accepted calibration | generator metadata |
| SmallTree84 406 separate | long-play validated | config + validator |
| SmallTree84 cluster share ~76% | accepted calibration | generator metadata |
| Building Stone 1683 global anchors / 14160 global stock | locked | config + validators |
| Start Stone bonus 53 units/player | latest 20P profile | config contract; separate pool deferred |
| 7-cell Stone footprint | long-play critical fix | placement + validator |
| Stone anchor min HEX4 | conservative latest rule | placement + validator |
| Stone global cluster share ~30%, ~60 centers | profile | generator metadata |
| Desert decor x2 = 60 on 768 | validated 10P correction | config + validator |
| Swamp decor x2 = 2 Reeds on 768 | validated 10P correction | config + validator |
| Decorative Stones1..28 = 89 on reference 768 | validated reference count (/10 native intent) | config + validator |
| Reefs ~10–12, target11 | locked | config + validator |
| No ordinary objects on Mountain | crash/legality lock | placement + validator |
| Deterministic preview only | project hard rule | preview module |

## Important limitation

Upgraded v1.2 activates the recovered gameplay/profile rules, but the **fresh generalized local-morphology generator is not yet complete**. For Continental 768, v1.2 uses the canonical validated `resourcepass_v8_relief_snow` EDM terrain/height as an executable morphology reference and applies safe identity/180/axial-transpose transforms before the start-first/resource/object pipeline. This is intentional: it is safer than silently inventing a replacement for already validated forms. Future work should replace this transitional reference step with the generalized Upgraded shape library while keeping every validator above unchanged.
