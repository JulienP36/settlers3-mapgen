from pathlib import Path
import tempfile,struct
from s3mapgen.app_paths import LEGACY_PROFILE,UPGRADED_PROFILE,UPGRADED_REFERENCE,LIBRARY,EDM_SCAFFOLD
from s3mapgen.generator_v15 import MapGenerator
from s3mapgen.binary import export_with_scaffold,checksum

def test_v15_engine_export_checksum():
    g=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_PROFILE,UPGRADED_REFERENCE);res=g.generate(4,2026082202,mode='upgraded',archetype='continental')
    assert all(v.passed for v in res.validations if v.hard)
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'test.edm';export_with_scaffold(res.state,EDM_SCAFFOLD,out);b=out.read_bytes();assert struct.unpack_from('<I',b,0)[0]==checksum(b)
