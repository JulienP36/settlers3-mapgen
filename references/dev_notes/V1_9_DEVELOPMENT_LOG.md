# Settlers III MapGen — v1.9 development log

## DEV_1 — tolerant EDM terminal padding

Validated on Windows: 2026-08-26  
Tracking: GitHub Issue #4

- Reproduced `Part scan did not end at EOF` on two real EDM files supplied by
  the project owner.
- Confirmed valid version-10 structures and checksums; the files retain one or
  three opaque bytes after the terminal `type 0 / size 8` part to reach DWORD
  alignment.
- Read-only EDM/MAP import now accepts only the confirmed 1–3-byte terminal
  alignment case. Scaffold reconstruction remains strict.
- Both original files load under Windows: 256×256/20 starts and 768×768/10
  starts.
- 236 pytest tests, 49 engine validations, binary checksum, extracted package
  self-test and five protected hashes passed.
- The protected v1.5 generation engine was not modified.

DEV_1 closes the urgent import defect. The main v1.9 scope is now internal
restructuring; Data Mapping is deliberately moved toward the end of v1.9.
