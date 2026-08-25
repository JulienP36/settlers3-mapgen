from __future__ import annotations

import json
from pathlib import Path

from s3mapgen import app_paths
from s3mapgen.package_runtime import inspect_package
from s3mapgen.version import APP_VERSION, ENGINE_VERSION, WINDOWS_FILE_VERSION


ROOT=Path(__file__).resolve().parent.parent


def test_dev9_version_metadata():
    assert APP_VERSION=='1.8 DEV_9_R2'
    assert ENGINE_VERSION=='1.5'
    assert WINDOWS_FILE_VERSION==(1,8,9,2)


def test_source_paths_are_independent_from_current_working_directory(monkeypatch,tmp_path):
    monkeypatch.chdir(tmp_path)
    assert app_paths.BASE==ROOT
    assert app_paths.APP_DIR==ROOT
    assert app_paths.OUTPUT==ROOT/'output'
    assert app_paths.LEGACY_PROFILE.is_file()
    assert app_paths.LIBRARY.is_file()
    assert app_paths.START_MARKER_SHEET.is_file()


def test_source_package_self_test_reads_all_required_resources():
    report=inspect_package()
    assert report['status']=='PASS',report
    assert report['frozen'] is False
    assert set(report['checks'])=={
        'gui_runtime_import',
        'legacy_profile','upgraded_profile','native_library','upgraded_reference',
        'edm_scaffold','map_scaffold','start_markers',
    }
    assert all(check['ok'] for check in report['checks'].values())
    for key in ('legacy_profile','upgraded_profile','native_library'):
        assert report['checks'][key]['sha256']==report['checks'][key]['expected_sha256']


def test_pyinstaller_spec_is_onedir_and_bundles_runtime_resources():
    spec=(ROOT/'build/windows/settlers3_mapgen.spec').read_text(encoding='utf-8')
    for resource in ('config','data','SETTLERS3_PLAYER_START_MARKERS_J1_J20_REFERENCE_20260822.png'):
        assert resource in spec
    assert 'COLLECT(' in spec
    assert "name='Settlers3MapGen'" in spec
    assert 'optional_icon' in spec
    assert "'unittest'" not in spec


def test_windows_workflow_runs_binary_self_test_before_upload():
    workflow=(ROOT/'.github/workflows/build-windows-dev.yml').read_text(encoding='utf-8')
    assert '--self-test' in workflow or 'build_windows.ps1' in workflow
    assert 'upload-artifact@v4' in workflow
    assert 'windows-latest' in workflow
    assert 'verify_protected_hashes.ps1' in workflow


def test_runtime_report_is_json_serializable():
    json.dumps(inspect_package())
