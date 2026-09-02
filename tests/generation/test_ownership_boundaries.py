"""Keep archetype descriptions separate from concrete generator behavior."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parents[2] / "s3mapgen" / "generation"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
    return imports


def test_continental_archetype_does_not_import_a_concrete_generator():
    imports = _imports(ROOT / "archetypes" / "continental.py")
    assert not any("generators" in target for target in imports)


def test_legacy_pipeline_assembles_the_archetype_but_executes_legacy_rules():
    source = (ROOT / "generators" / "legacy" / "native_pipeline.py").read_text(encoding="utf-8")
    assert "assemble_continental_state" in source
    assert "generate_primary_terrain" in source
    assert "place_starts" in source
    assert "populate_native_content" not in source


def test_legacy_native_modules_own_global_content_and_starts():
    native_terrain = (ROOT / "generators" / "legacy" / "native_terrain.py").read_text(encoding="utf-8")
    native_content = (ROOT / "generators" / "legacy" / "native_content.py").read_text(encoding="utf-8")
    starts = (ROOT / "generators" / "legacy" / "starts.py").read_text(encoding="utf-8")
    assert "populate_native_content" in native_terrain
    assert "def populate_native_content" in native_content
    assert "START_FOOTPRINT" in starts
    assert "place_starts" in starts


def test_upgraded_facade_does_not_move_into_legacy_native_modules():
    for path in (
        ROOT / "generators" / "legacy" / "native_pipeline.py",
        ROOT / "generators" / "legacy" / "native_terrain.py",
        ROOT / "generators" / "legacy" / "native_content.py",
    ):
        source = path.read_text(encoding="utf-8")
        assert "generation.continental" not in source, path
        assert "validated" not in source, path


def test_upgraded_pipeline_is_a_separate_complete_copy():
    pipeline_path = ROOT / "generators" / "upgraded" / "pipeline.py"
    pipeline = pipeline_path.read_text(encoding="utf-8")
    terrain = (ROOT / "generators" / "upgraded" / "native_terrain.py").read_text(encoding="utf-8")
    assert "assemble_continental_state" in pipeline
    assert "generate_primary_terrain" in pipeline
    assert "UpgradedContent" in pipeline
    assert not any("generators.legacy" in target for target in _imports(pipeline_path))
    assert "_FamilyPlan(DESERT" in terrain
    assert "_FamilyPlan(SWAMP" in terrain
    assert "_FamilyPlan(MUD" not in terrain


def test_old_upgraded_monoliths_are_removed():
    assert not (ROOT / "base.py").exists()
    assert not (ROOT / "continental.py").exists()
    assert not (ROOT / "validated.py").exists()
