"""Resolve bundled resources and writable output locations in source/frozen modes."""

from pathlib import Path
import sys


FROZEN=bool(getattr(sys,'frozen',False))
# PyInstaller exposes bundled read-only resources through _MEIPASS.  In source
# mode the repository root remains the resource base.
BASE=Path(getattr(sys,'_MEIPASS',Path(__file__).resolve().parent.parent.parent)).resolve()
# User-visible exports belong beside the executable, never inside PyInstaller's
# private _internal directory and never in the caller's current directory.
APP_DIR=(Path(sys.executable).resolve().parent if FROZEN else BASE)
LEGACY_PROFILE=BASE/'config'/'legacy_768_v1.json'
UPGRADED_PROFILE=BASE/'config'/'upgraded_768_v1.json'
LIBRARY=BASE/'data'/'SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz'
UPGRADED_REFERENCE=BASE/'data'/'upgraded_reference_768.edm'
EDM_SCAFFOLD=BASE/'data'/'scaffold_768.edm'
MAP_SCAFFOLD=BASE/'data'/'scaffold_768.map'
START_MARKER_SHEET=BASE/'references'/'SETTLERS3_PLAYER_START_MARKERS_J1_J20_REFERENCE_20260822.png'
OUTPUT=APP_DIR/'output'
