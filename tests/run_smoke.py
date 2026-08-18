import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pathlib import Path
import struct,tempfile
from s3mapgen.app_paths import PROFILE,LIBRARY,EDM_SCAFFOLD
from s3mapgen.engine import Continental768Generator
from s3mapgen.binary import export_with_scaffold,checksum

g=Continental768Generator(PROFILE,LIBRARY)
for players,seed in [(4,2026081901),(20,2026081902)]:
    r=g.generate(players,seed)
    fails=[v.label() for v in r.validations if v.hard and not v.passed]
    if fails:raise SystemExit('\n'.join(fails))
    print(f'{players}P: {len(r.validations)} validations PASS')
with tempfile.TemporaryDirectory() as td:
    r=g.generate(4,2026081901);p=Path(td)/'smoke.edm';export_with_scaffold(r.state,EDM_SCAFFOLD,p);b=p.read_bytes()
    assert struct.unpack_from('<I',b,0)[0]==checksum(b)
print('binary checksum PASS')
