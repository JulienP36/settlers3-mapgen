import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pathlib import Path
import tempfile, struct
from s3mapgen.app_paths import PROFILE,LIBRARY,EDM_SCAFFOLD
from s3mapgen.engine import Continental768Generator
from s3mapgen.binary import export_with_scaffold,checksum


def test_generation_4p_hard_checks():
    res=Continental768Generator(PROFILE,LIBRARY).generate(4,2026081901)
    assert all(v.passed for v in res.validations if v.hard), [v.label() for v in res.validations if v.hard and not v.passed]


def test_export_checksum():
    res=Continental768Generator(PROFILE,LIBRARY).generate(4,2026081901)
    with tempfile.TemporaryDirectory() as td:
        out=Path(td)/'test.edm'
        export_with_scaffold(res.state,EDM_SCAFFOLD,out)
        b=out.read_bytes()
        assert struct.unpack_from('<I',b,0)[0] == checksum(b)
