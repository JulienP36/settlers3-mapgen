# Windows standalone build

PyInstaller 6.22.2, onedir, Windows x64 and Python 3.12. The delivered folder
runs without Python/pip installation or dependency downloads. Keep _internal
beside Settlers3MapGen.exe; no BAT launcher is included in the portable.

## Build

On a Windows build machine with Python 3.12:

```bat
build\windows\build_windows.bat
```

The runtime versions match the qualified source baseline: NumPy 2.3.5,
SciPy 1.17.0 and Pillow 12.3.0 (requirements-runtime.txt).

This development command installs build/runtime dependencies on the build
machine, verifies the two source drawings and generated ICO, generates version
resources, builds the executable, runs its frozen resource self-test, then
qualifies a relocated copy from a path with spaces and accents.

Qualification uses an unrelated working directory, an external Python
installation made unavailable to the process, and isolated temporary APPDATA.
It tests fresh startup and pre-existing preferences/configurations/masks,
checks native small/large window icon handles, closes the GUI normally and
checks preservation of user data. It never targets the builder's real APPDATA.
The executable's x64 GUI type, version and icon resources are inspected as well.

artifacts/ receives the ZIP, SHA-256, frozen SELFTEST.json and QUALIFICATION.json.
A failing check stops the build before its archive is produced.

Julien's small 16×16 and large 64×64 drawings are copied without artistic edits.
The multi-resolution ICO is generated deterministically with nearest-neighbor
resizing by generate_icons.py. Windows shell identity is stable across versions.
Explorer/taskbar/Alt+Tab/Task Manager still require visual confirmation on Windows.

The existing GitHub Actions workflow runs these checks on windows-latest at
complete DEV checkpoints. Suffixed local candidates are not pushed to trigger it.
No updater/check mechanism is included; users download published ZIPs manually.

A Linux source self-test or successful static checks do not constitute a
Windows portable qualification. The current build environment must be stated
in each candidate's qualification notes.

## Current DEV11 handoff order

Before closing DEV11, build the local source candidate on Windows with the BAT
above. Python and dependency downloads are required on this build machine;
users of the resulting portable do not need them. Keep the source folder intact
while building, and send the four generated `artifacts/` files for review:
portable ZIP, its `.sha256`, `_SELFTEST.json` and `_QUALIFICATION.json`.
If the command fails, keep its exact error and do not treat the older artifacts
as outputs of the failed run.

After a successful build, test the fully extracted ZIP directly on Windows,
check visible icons and preservation of user data. Only then close/validate the
whole DEV11 checkpoint and publish it on `dev`; CI rechecks that published state.
No temporary branch or suffixed-candidate push is required. STABLE publication
remains a separate explicit decision. See `../../docs/RELEASE_2_0_CHECKLIST.md`.
