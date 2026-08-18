# Settlers III — Native Heightmap Reference (21 SAV) v3

> Canonical relief reference. Derived only from the 21 native generator SAVs. The 768 target is the mean of the three native 768 saves.

## Adjacent HEX6 slopes

- Grass: `{'p50': 2.0, 'p75': 3.0, 'p90': 5.0, 'p95': 5.0, 'p99': 5.0}`
- Mountain family: `{'p50': 2.0, 'p75': 3.6666666666666665, 'p90': 5.0, 'p95': 5.0, 'p99': 5.0}`

## Native Grass amplitude on windows entirely inside Grass

These are max(height)-min(height) percentiles for windows containing only Grass cells:
```text
{
  "3": {
    "p50": 8.0,
    "p75": 10.0,
    "p90": 13.0,
    "p95": 15.0,
    "p99": 18.666666666666668
  },
  "5": {
    "p50": 14.0,
    "p75": 18.333333333333332,
    "p90": 23.0,
    "p95": 26.333333333333332,
    "p99": 33.666666666666664
  },
  "9": {
    "p50": 25.333333333333332,
    "p75": 32.333333333333336,
    "p90": 39.333333333333336,
    "p95": 44.666666666666664,
    "p99": 57.0
  },
  "17": {
    "p50": 42.0,
    "p75": 51.666666666666664,
    "p90": 62.333333333333336,
    "p95": 69.0,
    "p99": 82.39666666666744
  },
  "33": {
    "p50": 65.0,
    "p75": 74.33333333333333,
    "p90": 84.33333333333333,
    "p95": 89.66666666666667,
    "p99": 96.33333333333333
  },
  "65": {
    "p50": 86.5,
    "p75": 90.33333333333333,
    "p90": 94.33333333333333,
    "p95": 96.14999999999999,
    "p99": 97.91000000000001
  }
}
```

## Mean Grass height versus water distance

```text
{
  "0-2": 6.1087815661777904,
  "11-20": 44.37437102529751,
  "21-40": 64.2606936014144,
  "3-5": 11.636441293769101,
  "41-80": 77.10241575421465,
  "6-10": 24.67741318621532,
  "81-160": 79.85220301057626
}
```

## Mean mountain height versus depth inside the full mountain family

```text
{
  "1-2": 115.95970857987835,
  "17-32": 171.36871789484394,
  "3-4": 125.55007162296276,
  "33-9999": 181.32846639743192,
  "5-8": 137.13010047870088,
  "9-16": 153.6536526480064
}
```

## Rules inferred

- A valid native-like heightmap must match both immediate slopes and multi-scale amplitudes.
- Plains rise strongly away from coasts/lakes during the first ~40 cells, then settle around the inland mean plateau.
- Mountains have a monotonic depth-to-height structure, reaching native means around 170–180 in their deepest zones on 768.
- P99 adjacent HEX6 slope is ~5 for both Grass and mountain family.
- Shore belongs exclusively to actual sea/lake rims; isolated inland Shore pixels are invalid for generation.

## Validation status

The statistical model above is the canonical native target, but **heightmap/elevation has not yet received an explicit final user validation equivalent to the terrain-shape validation**.

Current state:

- the latest generated lineage uses this 21-SAV-derived model;
- terrain morphology and transitions are locked;
- if elevation is revisited, modify the height field only and preserve the validated terrain masks;
- do not infer that matching `p50/p90/p99` adjacent slopes alone is enough: the multi-scale window amplitudes and coast/mountain-depth trends are equally important.

## Current implementation rules

- use HEX6 neighbour slope validation;
- Grass adjacent p99 target ≈ 5;
- mountain-family adjacent p99 target ≈ 5;
- reproduce strong medium/large-scale plain amplitude;
- plains rise away from water through the first ~40 cells;
- mountain mean elevation rises monotonically with depth into the full massif;
- do not flatten/reshape terrain around player starts;
- Shore is tied to actual sea/lake rims.
