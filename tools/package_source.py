from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import zipfile
from pathlib import Path, PurePosixPath


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_TIMESTAMP = (2020, 1, 1, 0, 0, 0)
REFERENCE_ROOT = "references"

REQUIRED_SOURCE_PATHS = (
    "AGENTS.md",
    "run_gui.py",
    "run_gui.bat",
    "install_and_run.bat",
    "requirements.txt",
    "README.md",
    "README_EN.md",
    "PROJECT_WORKFLOW.md",
    "TODO_MAPGEN.md",
    "CHANGELOG.md",
    "docs/ARCHITECTURE.md",
    "docs/DEBUGGING.md",
    "docs/GITHUB_PUBLICATION.md",
    "docs/screenshots/v1_8_generation_viewer.png",
    "docs/screenshots/v1_8_statistics.png",
    "docs/screenshots/v1_8_charts.png",
    "docs/screenshots/v1_8_batch.png",
    "s3mapgen/application/runtime.py",
    "s3mapgen/application/diagnostics/package_runtime.py",
    "s3mapgen/application/paths.py",
    "s3mapgen/application/analysis/core.py",
    "s3mapgen/application/ui/widgets/icons.py",
    "s3mapgen/application/ui/i18n/shell.py",
    "s3mapgen/generation/archetypes/continental.py",
    "s3mapgen/generation/facade.py",
    "s3mapgen/generation/contracts.py",
    "s3mapgen/generation/generators/legacy/__init__.py",
    "s3mapgen/generation/generators/legacy/native.py",
    "s3mapgen/generation/generators/legacy/native_pipeline.py",
    "s3mapgen/generation/generators/legacy/native_content.py",
    "s3mapgen/generation/generators/legacy/native_terrain.py",
    "s3mapgen/generation/generators/legacy/native_validators.py",
    "s3mapgen/generation/generators/legacy/starts.py",
    "s3mapgen/generation/generators/legacy/objects.py",
    "s3mapgen/generation/generators/legacy/profile.py",
    "s3mapgen/generation/generators/upgraded/__init__.py",
    "s3mapgen/generation/generators/upgraded/content.py",
    "s3mapgen/generation/generators/upgraded/native.py",
    "s3mapgen/generation/generators/upgraded/native_terrain.py",
    "s3mapgen/generation/generators/upgraded/pipeline.py",
    "s3mapgen/generation/generators/upgraded/profile.py",
    "s3mapgen/generation/generators/upgraded/starts.py",
    "s3mapgen/generation/generators/upgraded/validators.py",
    "s3mapgen/map_data/binary.py",
    "config/legacy_768_v1.json",
    "config/upgraded_768_v1.json",
    "data/SETTLERS3_NATIVE_768_STATIC_LIBRARY_v1.npz",
    "data/scaffold_768.edm",
    "data/scaffold_768.map",
    "data/SETTLERS3_PLAYER_START_MARKERS_J1_J20_REFERENCE_20260822.png",
)

FORBIDDEN_ARCHIVE_PARTS = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "artifacts",
    "dist",
    "output",
    "updates",
}

EXCLUDED_SOURCE_SUFFIXES = {".log", ".pyc", ".pyo", ".sav", ".zip"}
EXCLUDED_SOURCE_NAMES = {".DS_Store", "Thumbs.db"}


class SourcePackageError(RuntimeError):
    """Raised when a source archive cannot be built or validated safely."""


def _filesystem_source_files(project_root: Path) -> list[Path]:
    """List clean source files when packaging an already extracted source ZIP."""

    files: list[Path] = []
    for source in project_root.rglob("*"):
        if not source.is_file():
            continue
        relative_path = source.relative_to(project_root)
        if FORBIDDEN_ARCHIVE_PARTS.intersection(relative_path.parts):
            continue
        if source.name in EXCLUDED_SOURCE_NAMES:
            continue
        if source.suffix.lower() in EXCLUDED_SOURCE_SUFFIXES:
            continue
        files.append(relative_path)
    return sorted(files, key=lambda path: path.as_posix())


def _source_files(project_root: Path) -> list[Path]:
    """List Git candidates plus local references retained for source ZIPs."""

    command = (
        "git",
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
    )
    try:
        result = subprocess.run(
            command,
            cwd=project_root,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return _filesystem_source_files(project_root)

    relative_paths = [
        Path(raw.decode("utf-8"))
        for raw in result.stdout.split(b"\0")
        if raw
    ]
    files = [path for path in relative_paths if (project_root / path).is_file()]
    # ``references/`` is intentionally ignored by the GitHub working tree, but
    # it remains part of the hand-off source ZIP so the recovery/audit context
    # is not lost between candidate packages.
    files.extend(
        path
        for path in _filesystem_source_files(project_root)
        if path.parts and path.parts[0] == REFERENCE_ROOT
    )
    return sorted(set(files), key=lambda path: path.as_posix())


def _validate_input_files(project_root: Path, files: list[Path]) -> None:
    relative_names = {path.as_posix() for path in files}
    missing = [path for path in REQUIRED_SOURCE_PATHS if path not in relative_names]
    if missing:
        raise SourcePackageError(
            "Required source-package files are missing: " + ", ".join(missing)
        )

    for relative_path in files:
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise SourcePackageError(f"Unsafe source path: {relative_path}")
        source = project_root / relative_path
        if source.is_symlink():
            raise SourcePackageError(f"Source ZIP does not accept symlinks: {relative_path}")


def _validate_root_name(root_name: str) -> str:
    candidate = PurePosixPath(root_name)
    if (
        not root_name
        or candidate.is_absolute()
        or len(candidate.parts) != 1
        or candidate.parts[0] in {".", ".."}
    ):
        raise SourcePackageError(f"Unsafe archive root name: {root_name!r}")
    return candidate.parts[0]


def build_source_archive(
    output_path: Path,
    root_name: str,
    project_root: Path = PROJECT_ROOT,
) -> dict[str, object]:
    """Build a deterministic source ZIP and return its validation report."""

    project_root = project_root.resolve()
    output_path = output_path.resolve()
    root_name = _validate_root_name(root_name)
    files = _source_files(project_root)
    _validate_input_files(project_root, files)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(
        output_path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for relative_path in files:
            source = project_root / relative_path
            archive_name = f"{root_name}/{relative_path.as_posix()}"
            info = zipfile.ZipInfo(archive_name, ARCHIVE_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (
                stat.S_IFREG | stat.S_IMODE(source.stat().st_mode)
            ) << 16
            archive.writestr(info, source.read_bytes(), compresslevel=9)

    return validate_source_archive(output_path, expected_root=root_name)


def validate_source_archive(
    archive_path: Path,
    expected_root: str | None = None,
) -> dict[str, object]:
    """Reject corrupt, incomplete, unsafe or multi-root source archives."""

    archive_path = archive_path.resolve()
    with zipfile.ZipFile(archive_path) as archive:
        corrupt_member = archive.testzip()
        if corrupt_member is not None:
            raise SourcePackageError(f"Corrupt archive member: {corrupt_member}")

        names = [PurePosixPath(name) for name in archive.namelist()]
        if not names:
            raise SourcePackageError("Source archive is empty.")
        if any(path.is_absolute() or ".." in path.parts for path in names):
            raise SourcePackageError("Source archive contains an unsafe path.")

        roots = {path.parts[0] for path in names if path.parts}
        if len(roots) != 1:
            raise SourcePackageError("Source archive must contain one root folder.")
        root_name = next(iter(roots))
        if expected_root is not None and root_name != expected_root:
            raise SourcePackageError(
                f"Unexpected source archive root: {root_name!r}"
            )

        forbidden = sorted(
            path.as_posix()
            for path in names
            if FORBIDDEN_ARCHIVE_PARTS.intersection(path.parts)
        )
        if forbidden:
            raise SourcePackageError(
                "Source archive contains excluded paths: " + ", ".join(forbidden)
            )

        archived_relative = {
            PurePosixPath(*path.parts[1:]).as_posix()
            for path in names
            if len(path.parts) > 1
        }
        missing = [
            path for path in REQUIRED_SOURCE_PATHS if path not in archived_relative
        ]
        if missing:
            raise SourcePackageError(
                "Source archive is incomplete: " + ", ".join(missing)
            )

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    return {
        "status": "PASS",
        "archive": str(archive_path),
        "root": root_name,
        "files": len(names),
        "size_bytes": archive_path.stat().st_size,
        "sha256": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and validate a Settlers III MapGen source ZIP."
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root-name", required=True)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()

    report = build_source_archive(
        output_path=args.output,
        root_name=args.root_name,
        project_root=args.project_root,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
