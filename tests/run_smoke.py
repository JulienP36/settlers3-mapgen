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

from s3mapgen.app_paths import (  # noqa: E402
    EDM_SCAFFOLD,
    LEGACY_PROFILE,
    LIBRARY,
    UPGRADED_PROFILE,
    UPGRADED_REFERENCE,
)
from s3mapgen.binary import checksum, export_with_scaffold  # noqa: E402
from s3mapgen.generator_v15 import MapGenerator  # noqa: E402


generator = MapGenerator(
    LEGACY_PROFILE,
    LIBRARY,
    UPGRADED_PROFILE,
    UPGRADED_REFERENCE,
)
result = generator.generate(
    4,
    2026082202,
    mode="upgraded",
    archetype="continental",
)
failures = [
    validation.label()
    for validation in result.validations
    if validation.hard and not validation.passed
]
if failures:
    raise SystemExit("\n".join(failures))

print(f"4P v1.5 engine: {len(result.validations)} validations PASS")
with tempfile.TemporaryDirectory() as temporary_directory:
    output_path = Path(temporary_directory) / "smoke.edm"
    export_with_scaffold(result.state, EDM_SCAFFOLD, output_path)
    payload = output_path.read_bytes()
    assert struct.unpack_from("<I", payload, 0)[0] == checksum(payload)
print("binary checksum PASS")
