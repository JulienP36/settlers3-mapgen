"""Contracts for the stable package boundaries introduced during v1.9."""

from __future__ import annotations

import ast
import re
from pathlib import Path


PACKAGE_ROOT = Path(__file__).parents[1] / "s3mapgen"
TEST_ROOT = Path(__file__).parent


def _absolute_relative_target(path: Path, node: ast.ImportFrom) -> str:
    package = ["s3mapgen", *path.relative_to(PACKAGE_ROOT).parts[:-1]]
    keep = len(package) - node.level + 1
    prefix = package[:keep]
    return ".".join([*prefix, *(node.module or "").split(".")]).rstrip(".")


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    targets: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            targets.add(
                _absolute_relative_target(path, node)
                if node.level
                else node.module or ""
            )
    return targets


def test_package_root_contains_only_shared_metadata():
    assert {path.name for path in PACKAGE_ROOT.glob("*.py")} == {
        "__init__.py",
        "version.py",
    }


def test_map_data_never_depends_on_application_or_generation():
    for path in (PACKAGE_ROOT / "map_data").glob("*.py"):
        imports = _imports(path)
        assert not any(
            target.startswith(("s3mapgen.application", "s3mapgen.generation"))
            for target in imports
        ), path


def test_generation_never_depends_on_application():
    for path in (PACKAGE_ROOT / "generation").glob("*.py"):
        assert not any(
            target.startswith("s3mapgen.application") for target in _imports(path)
        ), path


def test_numbered_compatibility_modules_do_not_return():
    forbidden = {"gui.py", "generator.py"}
    assert not any(path.name in forbidden or "_v1" in path.stem for path in PACKAGE_ROOT.rglob("*.py"))


def test_tests_describe_subsystems_and_behaviors_not_historical_revisions():
    historical = re.compile(r"(?:^|_)(?:v\d+|dev\d+|r\d+)(?:_|$)")
    paths = list(TEST_ROOT.rglob("test_*.py"))
    assert not any(historical.search(path.stem) for path in paths)
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        test_names = (
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name.startswith("test_")
        )
        assert not any(historical.search(name) for name in test_names), path


def test_gui_has_one_named_tk_foundation_and_one_engine_factory():
    from s3mapgen.application.main_window import MainWindow
    from s3mapgen.application.shell import ShellWindow

    assert ShellWindow in MainWindow.mro()
    assert not any((PACKAGE_ROOT / "application" / name).exists() for name in (
        "base_window.py", "settings_window.py", "export_window.py",
    ))
    main_source = (PACKAGE_ROOT / "application" / "main_window.py").read_text(encoding="utf-8")
    foundation_source = (
        PACKAGE_ROOT / "application" / "shell" / "foundation.py"
    ).read_text(encoding="utf-8")
    runtime_source = (PACKAGE_ROOT / "application" / "runtime.py").read_text(encoding="utf-8")
    assert "MapGenerator(" not in main_source
    assert runtime_source.count("MapGenerator(") == 1
    assert "self.header_root" in foundation_source
    assert "ttk.Progressbar" not in foundation_source
    assert "top=self.winfo_children()[0]" not in main_source
    for disposable_control in (
        "self.mode_combo=", "self.arch_combo=", "self.size_combo=",
        "self.players_spin=", "self.export_btn=", "self.zoom_scale=",
    ):
        assert disposable_control not in foundation_source
