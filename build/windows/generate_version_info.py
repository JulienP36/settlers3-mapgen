"""Generate PyInstaller Windows metadata from the current runtime version."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from s3mapgen.version import APP_VERSION, WINDOWS_FILE_VERSION


def main() -> None:
    version = ', '.join(str(part) for part in WINDOWS_FILE_VERSION)
    content = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version}),
    prodvers=({version}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [StringStruct('CompanyName', 'Settlers III MapGen'),
         StringStruct('FileDescription', 'Settlers III MapGen'),
         StringStruct('FileVersion', '{APP_VERSION}'),
         StringStruct('InternalName', 'Settlers3MapGen'),
         StringStruct('OriginalFilename', 'Settlers3MapGen.exe'),
         StringStruct('ProductName', 'Settlers III MapGen'),
         StringStruct('ProductVersion', '{APP_VERSION}')])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)\n'''
    (ROOT / 'build/windows/version_info.txt').write_text(content, encoding='utf-8')


if __name__ == '__main__':
    main()
