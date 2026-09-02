from __future__ import annotations

import struct
import sys
import tempfile
from pathlib import Path


# Keep this explicit validation script runnable as documented from the project
# root (``python tests/run_smoke.py``), independently from pytest path setup.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from s3mapgen.application.paths import (  # noqa: E402
    EDM_SCAFFOLD,
    LEGACY_PROFILE,
    LIBRARY,
    UPGRADED_PROFILE,
    UPGRADED_REFERENCE,
)
from s3mapgen.map_data.binary import checksum, export_with_scaffold  # noqa: E402
from s3mapgen.generation import MapGenerator  # noqa: E402


generator = MapGenerator(
    LEGACY_PROFILE,
    LIBRARY,
    UPGRADED_PROFILE,
    UPGRADED_REFERENCE,
)
upgraded = generator.generate(
    4,
    2026082202,
    mode="upgraded",
    archetype="continental",
)
failures = [
    validation.label()
    for validation in upgraded.validations
    if validation.hard and not validation.passed
]
if failures:
    raise SystemExit("\n".join(failures))

print(f"4P Upgraded compatibility engine: {len(upgraded.validations)} validations PASS")
legacy = generator.generate(
    2,
    297650040,
    mode="legacy",
    archetype="continental",
    side=256,
    mirror_mode=3,
)
legacy_failures = [
    validation.label()
    for validation in legacy.validations
    if validation.hard and not validation.passed
]
if legacy_failures:
    raise SystemExit("\n".join(legacy_failures))
print(f"2P Legacy native 256×256 mirror: {len(legacy.validations)} validations PASS")
with tempfile.TemporaryDirectory() as temporary_directory:
    output_path = Path(temporary_directory) / "smoke_legacy_256.edm"
    export_with_scaffold(legacy.state, EDM_SCAFFOLD, output_path)
    payload = output_path.read_bytes()
    assert struct.unpack_from("<I", payload, 0)[0] == checksum(payload)
print("binary checksum PASS")
