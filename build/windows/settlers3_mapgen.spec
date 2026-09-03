from pathlib import Path


project_root=Path.cwd().resolve()
version_file=project_root/'build'/'windows'/'version_info.txt'
icon_path=project_root/'assets'/'Settlers3MapGen.ico'
optional_icon=str(icon_path) if icon_path.is_file() else None

datas=[
    (str(project_root/'config'),'config'),
    (str(project_root/'data'),'data'),
]

a=Analysis(
    [str(project_root/'run_gui.py')],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Do not hand-exclude standard or third-party modules: SciPy/NumPy/Tk may
    # reach apparently unrelated helpers during their normal import chain.
    excludes=[],
    noarchive=False,
    optimize=1,
)
pyz=PYZ(a.pure)

exe=EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Settlers3MapGen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=optional_icon,
    version=str(version_file),
    contents_directory='_internal',
)

coll=COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='Settlers3MapGen',
)
