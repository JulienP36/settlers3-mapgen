# Settlers III — Summit Snow Reference v1

> **Canonical Continental snow rule — accepted 2026-08-18**
>
> Snow is no longer an independent shape library layer and must never be translated from an earlier snow mask.
> It is generated **from the final relief of each mountain massif**.

## 1. Native observations

The 21-save corpus established that Snow belongs inside the mountain family and uses the transition:

```text
Rocky32 -> 35 -> 129 -> Snow128
```

The three native 768 references show Snow strongly biased toward high parts of snowy massifs, but not as a simple global fixed polygon.

Earlier native-768 measurements:

```text
mean normalized snow height within massif ≈ 0.747
mean snow fraction in top 25% height range ≈ 0.495
mean snow fraction in top 33% height range ≈ 0.686
```

These statistics are descriptive, not a direct generation algorithm.

## 2. Validated logical rule

Current Continental rule:

1. Generate the full Mountain-family mask **without Snow**.
2. Generate the heightmap.
3. For each mountain massif, consider only internal mountain cells deep enough to keep a complete Rocky/Snow transition:
   `mountain HEX depth >= 4`.
4. Compute the height percentile of those valid cells.
5. A cell can become part of a summit snow candidate when:

```text
H >= max(absolute_min_height, massif_percentile(relative_height_percentile))
```

6. Keep only coherent components that contain a true summit/high local maximum.
7. Remove meaningless tiny speckles.
8. Paint the final Snow family from the coherent binary mask using HEX6 depth:

```text
snow depth 1 -> 35
snow depth 2 -> 129
snow depth >=3 -> Snow128
```

9. Full mountain silhouette must remain unchanged.
10. Snow quantity may be **lower** than the reference/profile cap, but must not exceed it merely to satisfy a percentage target.

## 3. Accepted 768 calibration

Accepted candidate:

`S3_Continental_4P_768x768_seed_2026081801_resourcepass_v8_relief_snow.edm`

Parameters:

```text
relative_height_percentile = 80
absolute_min_height = 135
valid mountain depth >= 4
minimum coherent raw component ≈ 18 cells
near-summit requirement: component local max within ~5 height units of massif max
```

Result:

```text
previous v7 snow cells: 14247
accepted v8 snow cells: 11618
accepted snow map share: 1.970%
volume ratio vs v7: 0.815
snow components: 16
singletons: 0
weighted mean height-rank inside massif: 0.925
weighted fraction in top height quartile: 1.000
transition violations: 0
```

The user explicitly accepted this as the current Snow rule.

## 4. Important invariants

- Do **not** translate old snow shapes.
- Do **not** increase Snow merely to match native surface percentage.
- Snow is a consequence of mountain relief.
- Low mountains may have no Snow.
- Multiple summit caps are allowed inside a large massif if the relief contains multiple genuine peaks.
- Do not modify the heightmap just to create Snow.
- Minerals may exist beneath Snow.
- Snow-covered minerals are excluded from the accessible-Rocky mineral balance.
- When rebuilding Snow, preserve resource bytes unless a resource pass is explicitly requested.

## 5. Multi-size status

The rule is accepted on the validated 768 Continental map.

During the upcoming multi-size matrix, keep the same logical rule. The `80th percentile + H>=135` calibration is the initial cross-size value; only change it if the new sizes demonstrate a systematic problem.
