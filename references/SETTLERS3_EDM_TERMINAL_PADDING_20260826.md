# Settlers III EDM — terminal DWORD padding

Date: 2026-08-26  
Status: confirmed and Windows-validated in v1.9 DEV_1  
Tracking: GitHub Issue #4

## Symptom

The v1.8 reader rejected some otherwise valid `.EDM` files with:

```text
ValueError: Part scan did not end at EOF
```

The traceback supplied by the project owner reaches `read_area()` and then the
strict final-offset check in `parse_parts()`.

## Supplied evidence

| File | SHA-256 | Bytes | Version | Parsed parts | End of terminal part | Tail | Checksum |
|---|---|---:|---:|---:|---:|---|---|
| `Map de test all starts alignes.edm` | `ec67435636bcacda915777470a467e36038fcb7208ffb6d855647695480266c3` | 402,996 | 10 | 14 | 402,995 | `03` | valid |
| `1-S3_Continental_10P_768x768_seed_2026081801_checkpoint_rules_v2_final_played.edm` | `f9c6a55dec15252fde0a76d431c6652e3664145987f1737a5548348f329cfb8f` | 3,550,988 | 10 | 13 | 3,550,985 | `01 00 00` | valid |

Both files end with the confirmed terminal part header:

```text
part_type = 0
total_size = 8
```

The remaining one or three bytes bring the complete file length to a DWORD
boundary. Their values are opaque and are not assigned invented semantics.

## Comparison controls

The repository controls `data/scaffold_768.edm` and
`data/upgraded_reference_768.edm` also use version 10 and the same sequential
part framing. Their terminal part already ends exactly at EOF, so they need no
alignment tail and continue to parse unchanged.

## Reader rule

Read-only EDM/MAP imports may accept a tail only when all conditions hold:

1. at least one complete part was parsed;
2. the final complete part is `type 0` with an empty payload;
3. the complete file length is divisible by four;
4. exactly one, two or three bytes remain.

Any other incomplete tail remains an error. The writer/scaffold parser keeps
strict EOF behavior so rebuilding a file cannot silently discard unknown bytes.

## Verified result

After the reader change:

- the 3,550,988-byte source loads as 768×768 with 10 starts;
- the 402,996-byte source loads as 256×256 with 20 starts;
- synthetic regressions cover terminal tails of length 1, 2 and 3;
- a tail without the terminal part remains rejected.

Both original files were imported successfully through the Windows GUI
candidate; the fix is accepted in v1.9 DEV_1.
