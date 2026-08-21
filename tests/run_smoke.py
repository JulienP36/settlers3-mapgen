from pathlib import Path
import struct,tempfile
from s3mapgen.app_paths import LEGACY_PROFILE,UPGRADED_PROFILE,UPGRADED_REFERENCE,LIBRARY,EDM_SCAFFOLD
from s3mapgen.generator_v15 import MapGenerator
from s3mapgen.binary import export_with_scaffold,checksum

g=MapGenerator(LEGACY_PROFILE,LIBRARY,UPGRADED_PROFILE,UPGRADED_REFERENCE)
r=g.generate(4,2026082202,mode='upgraded',archetype='continental');fails=[v.label() for v in r.validations if v.hard and not v.passed]
if fails:raise SystemExit('\n'.join(fails))
print(f'4P v1.5 engine: {len(r.validations)} validations PASS')
with tempfile.TemporaryDirectory() as td:
 p=Path(td)/'smoke.edm';export_with_scaffold(r.state,EDM_SCAFFOLD,p);b=p.read_bytes();assert struct.unpack_from('<I',b,0)[0]==checksum(b)
print('binary checksum PASS')
