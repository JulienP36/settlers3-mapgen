# Settlers III MapGen v1.2 — Release validation

Date: 2026-08-18

## Targeted automated tests
- Architecture names / Upgraded enabled / Custom reserved: PASS
- Starts before detailed hydrology: PASS
- Upgraded 4P full HARD validators: PASS
- Upgraded 20P full HARD validators: PASS
- Legacy still generates: PASS
- Custom fails explicitly: PASS

(The complete historical smoke suite is computationally long in this environment; targeted v1.2 tests were run individually.)

## Upgraded sample 20P — seed 2026082002
- 35/35 validators PASS.
- Starts static: 20/20 PASS.
- Water H/access: PASS.
- External edge Water7: PASS.
- Micro-water 1–4: 0.
- River orphans: 0; bad Water mouths: 0; max=55.
- Fish: 32,313; Water-only; no River; <=HEX12 true Shore; 0 on map edge.
- Minerals exact family occupied-cell totals: PASS.
- Adult trees: 1,652 total in 20P (=1,352 global + up to 15/player bonus).
- SmallTree84: 406.
- Building Stones: 1,783 anchors total / 15,220 units total; footprint PASS; min HEX4.
- Decorations: desert60 / swamp2 / pure stones89 / reefs11.
- No ordinary objects on Mountain.
- EDM + MAP exported successfully.

## Remaining external validation
- Official editor start acceptance, especially high player counts.
- View Map / game crash smoke.
- Immediate SAV runtime Water check.
- Controlled Building Stone harvestability / exact editor hitbox.
- Visual validation of Upgraded morphology before generalized fresh-shape work.
