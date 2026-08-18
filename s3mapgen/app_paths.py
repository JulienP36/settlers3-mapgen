from pathlib import Path
BASE=Path(__file__).resolve().parent.parent
PROFILE=BASE/'config'/'continental_768_v1.json'  # v1 baseline profile; Legacy currently uses this implementation
LIBRARY=BASE/'data'/'SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz'
EDM_SCAFFOLD=BASE/'data'/'scaffold_768.edm'
MAP_SCAFFOLD=BASE/'data'/'scaffold_768.map'
OUTPUT=BASE/'output'
