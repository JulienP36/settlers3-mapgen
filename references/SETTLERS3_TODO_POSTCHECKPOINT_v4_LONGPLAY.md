# Settlers III MapGen — TODO post-checkpoint v4 — long-play

## Highest priority before next fresh Continental generation

1. **Fix Building Stone footprint serialization**
   - full 7-cell accessibility/occupation footprint;
   - stone-stone footprint collision;
   - stone-object collision;
   - prevent building overlap;
   - apply to global and start-bonus stones;
   - controlled harvestability test.

2. **Integrate water accessibility invariant**
   - Water0..7 Area accessibility=1;
   - verify in immediate SAV.

3. **Restore/generate fish after final hydrology**
   - nonzero fish mandatory;
   - validated spatial footprint only;
   - +30% quantity per fish-bearing cell, cap15;
   - no increase in fish-bearing-cell count.

4. **Increase mineral stock**
   - +30% quantity per existing mineralized cell, cap15;
   - no increase in mineralized-cell count.

5. **Final river validator**
   - remove orphan rivers after micro-pond cleanup;
   - practical size caps by map side:
     384=44, 448=47, 512=48, 576=49, 640=47, 704=53, 768=55.

## Validated — do not retune without reason

- SmallTree84 current placement/use: **VALIDATED by long-play**.
- Start-first robustness: 10/10 valid on tested 768/10P short-form lineage.
- Water non-walkability fix: **runtime validated**.
- Current river shapes/meandering: visually accepted; only orphan/maximum-length handling needs correction.
- Start bonuses remain outside global quota, resource volume +50% vs original 384 rule.
- Controlled mini-swamp bonus per player.
- Desert decoration x2; swamp decoration x2.

## Long-play caveat

Current played v3 map has no fish. Continue using its saves for every other subsystem, but never use it to judge fish economy.

## After long-play / next generation

Return to one-map-at-a-time native size progression:
448 -> 512 -> 576 -> 640 -> 704 -> 768

Do not begin a generation without first reading:
`SETTLERS3_PREGEN_READ_FIRST.md`.
