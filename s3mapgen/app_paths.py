from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
LEGACY_PROFILE=BASE/'config'/'legacy_768_v1.json'
UPGRADED_PROFILE=BASE/'config'/'upgraded_768_v1.json'
PROFILE=LEGACY_PROFILE  # backward-compatible alias
LIBRARY=BASE/'data'/'SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz'
UPGRADED_REFERENCE=BASE/'data'/'upgraded_reference_768.edm'
EDM_SCAFFOLD=BASE/'data'/'scaffold_768.edm'
MAP_SCAFFOLD=BASE/'data'/'scaffold_768.map'
OUTPUT=BASE/'output'
