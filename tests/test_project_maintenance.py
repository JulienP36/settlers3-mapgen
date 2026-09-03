from __future__ import annotations

import ast
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import tools.package_source as package_source
from s3mapgen.application.ui.i18n.history import _CONTEXT_TEXT
from s3mapgen.application.ui.i18n.shortcuts import SHORTCUT_UI_TEXT
from s3mapgen.application.history.order import (
    cached_protected_outputs,
    move_visual_key,
    reconcile_visual_order,
)
from tools.package_source import (
    FORBIDDEN_ARCHIVE_PARTS,
    REQUIRED_SOURCE_PATHS,
    build_source_archive,
)
from s3mapgen.version import APP_VERSION


ROOT = Path(__file__).resolve().parent.parent


def test_source_zip_readds_references_when_git_excludes_them(monkeypatch):
    class GitResult:
        stdout = b'AGENTS.md\0'

    monkeypatch.setattr(package_source.subprocess, 'run', lambda *args, **kwargs: GitResult())
    files = package_source._source_files(ROOT)
    has_local_references = (ROOT / 'references').is_dir()
    assert any(path.parts and path.parts[0] == 'references' for path in files) == has_local_references


def test_visual_order_helpers_keep_manual_order_and_drop_evictions():
    order, entries = reconcile_visual_order(
        [('d', 4), ('c', 3), ('b', 2)],
        ['c', 'a', 'b'],
    )

    assert order == ['d', 'c', 'b']
    assert entries == [('d', 4), ('c', 3), ('b', 2)]


def test_visual_move_is_clamped_and_does_not_mutate_input():
    original = ['c', 'b', 'a']
    moved, changed = move_visual_key(original, 'a', -1)
    clamped, changed_at_edge = move_visual_key(moved, 'c', -50)

    assert original == ['c', 'b', 'a']
    assert moved == ['c', 'a', 'b'] and changed
    assert clamped == moved and not changed_at_edge


def test_cached_protections_are_unique_by_identity_and_resident_only():
    shared = object()
    manual = object()
    outside = object()

    protected = cached_protected_outputs(
        [('shared', shared), ('manual', manual)],
        [shared, outside, shared, manual],
    )

    assert protected == [shared, manual]


def test_source_zip_is_complete_clean_and_self_tests_after_extraction(tmp_path):
    archive_path = tmp_path / 'candidate.zip'
    report = build_source_archive(
        output_path=archive_path,
        root_name='mapgen_source_test',
        project_root=ROOT,
    )

    assert report['status'] == 'PASS'
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        assert all(name.startswith('mapgen_source_test/') for name in names)
        assert all(
            not FORBIDDEN_ARCHIVE_PARTS.intersection(Path(name).parts)
            for name in names
        )
        assert all(
            f'mapgen_source_test/{required}' in names
            for required in REQUIRED_SOURCE_PATHS
        )
        archive.extractall(tmp_path / 'extracted')

    extracted_root = tmp_path / 'extracted' / 'mapgen_source_test'
    repacked_report = build_source_archive(
        output_path=tmp_path / 'repacked.zip',
        root_name='mapgen_repacked',
        project_root=extracted_root,
    )
    assert repacked_report['status'] == 'PASS'

    result = subprocess.run(
        [sys.executable, 'run_gui.py', '--self-test'],
        cwd=extracted_root,
        check=True,
        capture_output=True,
        text=True,
    )
    runtime_report = json.loads(result.stdout)
    assert runtime_report['status'] == 'PASS', runtime_report
    assert runtime_report['app_version'] == APP_VERSION


def test_publication_and_maintenance_docs_are_linked_and_packaged():
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    english = (ROOT / 'README_EN.md').read_text(encoding='utf-8')
    gitignore = (ROOT / '.gitignore').read_text(encoding='utf-8')
    github_policy = (ROOT / 'GITHUB_STORAGE_POLICY.md').read_text(encoding='utf-8')
    github_publication = (ROOT / 'docs/GITHUB_PUBLICATION.md').read_text(encoding='utf-8')

    assert '[English](README_EN.md)' in readme
    assert '[Français](README.md)' in english
    assert 'Settlers III' in readme and 'Settlers III' in english
    assert 'references/' in gitignore
    assert 'pushed to GitHub' in github_policy
    assert 'ZIP' in github_policy and 'ZIP' in github_publication
    for relative_path in (
        'AGENTS.md',
        'docs/ARCHITECTURE.md',
        'docs/DEBUGGING.md',
        'docs/GITHUB_PUBLICATION.md',
    ):
        assert relative_path in readme or relative_path in english
        assert (ROOT / relative_path).is_file()
        assert relative_path in REQUIRED_SOURCE_PATHS

    for screenshot_path in (
        'docs/screenshots/v1_8_generation_viewer.png',
        'docs/screenshots/v1_8_statistics.png',
        'docs/screenshots/v1_8_charts.png',
        'docs/screenshots/v1_8_batch.png',
    ):
        screenshot = ROOT / screenshot_path
        assert screenshot_path in readme and screenshot_path in english
        assert screenshot_path in REQUIRED_SOURCE_PATHS
        assert screenshot.is_file() and screenshot.stat().st_size > 10_000

    provenance_path = ROOT / 'references/SETTLERS3_VISUAL_ASSET_PROVENANCE.md'
    if provenance_path.is_file():
        provenance = provenance_path.read_text(encoding='utf-8')
        assert 'docs/screenshots/v1_8_batch.png' in provenance
        assert 'Reused from cache' in provenance
    else:
        assert 'source-package builder' in github_policy


def test_recovery_documents_stay_compact_current_and_role_separated():
    agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
    snapshot_path = ROOT / 'references/SETTLERS3_CURRENT_SNAPSHOT.md'
    snapshot = snapshot_path.read_text(encoding='utf-8') if snapshot_path.is_file() else ''
    todo = (ROOT / 'TODO_MAPGEN.md').read_text(encoding='utf-8')
    workflow = (ROOT / 'PROJECT_WORKFLOW.md').read_text(encoding='utf-8')
    changelog = (ROOT / 'CHANGELOG.md').read_text(encoding='utf-8')

    assert len(agents.splitlines()) < 40
    assert 'PROJECT_WORKFLOW.md' in agents
    assert 'SETTLERS3_PREGEN_READ_FIRST.md' in agents

    if snapshot:
        assert len(snapshot.splitlines()) < 180
        assert APP_VERSION in snapshot
        assert 'references/dev_notes/V1_8_DEVELOPMENT_LOG.md' in snapshot
    else:
        assert 'hand-off ZIPs' in workflow

    assert len(todo.splitlines()) < 220
    assert 'Roadmap orientée **travail restant**' in todo
    assert '## v1.9 —' in todo and '## v2.0 — reconstruction native Legacy, puis Custom' in todo
    assert 'reconstruction complète des pipelines' in todo

    assert 'DEV complets uniquement' in workflow
    assert 'Ne pousser sur `dev` que le checkpoint **DEV complet sans suffixe**' in workflow
    assert 'description courte de la section **About**' in workflow
    assert 'activer des **Topics** pertinents' in workflow
    assert 'bourrage de mots-clés' in workflow
    assert 'Checklist obligatoire à chaque étape validée' in workflow
    assert 'avant de fabriquer l’archive ou le commit final correspondant' in workflow
    assert changelog.count('# Changelog') == 1


def test_viewer_protection_exception_is_discoverable_in_every_language():
    for language in ('fr', 'en', 'de', 'es'):
        help_text = SHORTCUT_UI_TEXT[language]['viewer_protection']
        tooltip_text = _CONTEXT_TEXT[language]['viewer_role']
        assert 'V' in help_text and 'V' in tooltip_text
        assert help_text and tooltip_text


def test_maintenance_boundaries_have_module_documentation():
    for relative_path in (
        's3mapgen/application/paths.py',
        's3mapgen/map_data/binary.py',
        's3mapgen/application/exports/planning.py',
        's3mapgen/application/shell/foundation.py',
        's3mapgen/application/settings/controller.py',
        's3mapgen/application/imports/controller.py',
        's3mapgen/application/exports/controller.py',
        's3mapgen/application/main_window.py',
        's3mapgen/application/runtime.py',
        's3mapgen/map_data/hexgrid.py',
        's3mapgen/map_data/model.py',
        's3mapgen/application/settings/preferences.py',
        's3mapgen/application/rendering/preview.py',
        's3mapgen/application/analysis/core.py',
        's3mapgen/application/analysis/charts.py',
    ):
        source = (ROOT / relative_path).read_text(encoding='utf-8')
        assert ast.get_docstring(ast.parse(source)), relative_path
