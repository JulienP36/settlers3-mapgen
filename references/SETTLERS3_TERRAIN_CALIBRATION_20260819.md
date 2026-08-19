# Settlers III — Terrain calibration — 2026-08-19

Controlled editor calibration using `S3_CALIBRATION_TERRAINS_18_19_24_34.edm`.

The Grass16 control patch blends invisibly into the surrounding map, so the six visible zones correspond, left-to-right / top-to-bottom, to IDs:

```text
18  19  24
34 144 145
```

## Visual observations confirmed by user

| ID | Calibration result | Minimap | Notes |
|---:|---|---|---|
| 18 | unknown technical/transition-like terrain | displayed as Grass / no distinct minimap zone | visually resembles invalid/intermediate water-like transition texture; jagged/sawtooth border |
| 19 | unknown technical/transition-like terrain | displayed as Grass / no distinct minimap zone | visually resembles ID18; jagged/sawtooth border |
| 24 | **yellow/dry Grass-like terrain variant** | displayed as Grass / no distinct minimap zone | clean visual blend into Grass16 without transition artifacts; likely safe decorative/visual Grass variant, official game name unknown |
| 34 | unknown/technical Rocky-Snow-related terrain | visible | water-like/placeholder-looking texture in this isolated calibration; straight borders; should not be emitted as isolated residual pixels |
| 144 | Mud core | visible | expected edge artifacts when isolated without its legal transition family |
| 145 | Mud transition | visible | expected edge artifacts when isolated without the full legal chain |

## Generation decisions

- Do **not** intentionally add Terrain24 to Upgraded yet.
- Include Terrain24 explicitly in future terrain statistics instead of folding it silently into generic Grass.
- Keep IDs18/19/34 separately tracked as technical/unknown terrain IDs until their exact role is established.
- During Upgraded Snow reconstruction, residual isolated ID34 cells should be normalized away rather than left as singleton artifacts.
- Do not assign an official Settlers III terrain name to ID24 until confirmed; use the project label `Yellow/Dry Grass-like (24)`.
