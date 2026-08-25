from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

from .app_paths import (
    APP_DIR,
    BASE,
    EDM_SCAFFOLD,
    FROZEN,
    LEGACY_PROFILE,
    LIBRARY,
    MAP_SCAFFOLD,
    OUTPUT,
    START_MARKER_SHEET,
    UPGRADED_PROFILE,
    UPGRADED_REFERENCE,
)
from .version import APP_VERSION, ENGINE_VERSION


PROTECTED_RESOURCE_HASHES={
    'legacy_profile':'bdd091afeafcce88aa558d656e6d2728d101440368642e0c50568821d3f25c85',
    'upgraded_profile':'11a4feba38372a63d6dd32959d7578377ffc6da82a0e33fd918d597b15a5b441',
    'native_library':'fbc43b2bba99f995c659753ef423656dfd3b61df8308cc186a7cae72b5db3d4d',
}


def _sha256(path:Path)->str:
    digest=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_package() -> dict:
    """Read every bundled runtime resource without modifying user data."""
    checks: dict[str, dict] = {}
    errors: list[str] = []

    for name,path in (
        ('legacy_profile',LEGACY_PROFILE),
        ('upgraded_profile',UPGRADED_PROFILE),
    ):
        try:
            payload=json.loads(path.read_text(encoding='utf-8'))
            actual_hash=_sha256(path);expected_hash=PROTECTED_RESOURCE_HASHES[name]
            ok=isinstance(payload,dict) and actual_hash==expected_hash
            checks[name]={
                'path':str(path),'ok':ok,'bytes':path.stat().st_size,
                'sha256':actual_hash,'expected_sha256':expected_hash,
            }
            if not ok: errors.append(name)
        except Exception as exc:
            checks[name]={'path':str(path),'ok':False,'error':str(exc)}
            errors.append(name)

    try:
        with np.load(LIBRARY,allow_pickle=False) as native:
            actual_hash=_sha256(LIBRARY);expected_hash=PROTECTED_RESOURCE_HASHES['native_library']
            checks['native_library']={
                'path':str(LIBRARY),'ok':bool(native.files) and actual_hash==expected_hash,
                'arrays':len(native.files),'bytes':LIBRARY.stat().st_size,
                'sha256':actual_hash,'expected_sha256':expected_hash,
            }
            if actual_hash!=expected_hash: errors.append('native_library')
    except Exception as exc:
        checks['native_library']={'path':str(LIBRARY),'ok':False,'error':str(exc)}
        errors.append('native_library')

    for name,path in (
        ('upgraded_reference',UPGRADED_REFERENCE),
        ('edm_scaffold',EDM_SCAFFOLD),
        ('map_scaffold',MAP_SCAFFOLD),
    ):
        try:
            size=path.stat().st_size
            checks[name]={'path':str(path),'ok':size>0,'bytes':size}
            if size<=0: errors.append(name)
        except Exception as exc:
            checks[name]={'path':str(path),'ok':False,'error':str(exc)}
            errors.append(name)

    try:
        with Image.open(START_MARKER_SHEET) as marker:
            marker.verify()
        checks['start_markers']={
            'path':str(START_MARKER_SHEET),'ok':True,'bytes':START_MARKER_SHEET.stat().st_size,
        }
    except Exception as exc:
        checks['start_markers']={'path':str(START_MARKER_SHEET),'ok':False,'error':str(exc)}
        errors.append('start_markers')

    return {
        'status':'PASS' if not errors else 'FAIL',
        'app_version':APP_VERSION,
        'engine_version':ENGINE_VERSION,
        'frozen':FROZEN,
        'resource_base':str(BASE),
        'application_dir':str(APP_DIR),
        'output_dir':str(OUTPUT),
        'checks':checks,
        'errors':errors,
    }


def main() -> None:
    report=inspect_package()
    rendered=json.dumps(report,ensure_ascii=False,indent=2)
    report_path=os.environ.get('S3MAPGEN_SELFTEST_REPORT')
    if report_path:
        Path(report_path).write_text(rendered+'\n',encoding='utf-8')
    print(rendered)
    raise SystemExit(0 if report['status']=='PASS' else 1)


if __name__ == '__main__':
    main()
