# Windows standalone build

The build uses PyInstaller 6.22.2 in `onedir` mode. The resulting folder is autonomous: users do not need Python, pip or the source tree.

## Reproducible build

From a Windows x64 checkout with Python 3.12:

```bat
build\windows\build_windows.bat
```

The script installs runtime/build dependencies, derives archive and Windows metadata from the runtime version, creates the folder, runs the packaged executable's startup/resource self-test and writes the ZIP plus its SHA-256 file under `artifacts/`. Git attributes force the protected text resources to retain their repository LF bytes on Windows; the workflow verifies all five retained Upgraded compatibility hashes before building, and the packaged self-test imports the normal GUI runtime before rechecking the protected resources actually bundled.

An unsigned neutral executable is intentional until the owner supplies the final handmade pixel-art `.ico` at `assets/Settlers3MapGen.ico`. The spec automatically adopts that file when present.

The GitHub Actions workflow performs the same build on `windows-latest` and uploads the candidate without publishing a GitHub Release.
