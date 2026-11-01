"""Validate release gates without contacting or modifying GitHub."""
import hashlib
import json
import zipfile

import pytest

from tools import publish_release_2_0 as release


def assets(tmp_path):
    portable = tmp_path / f'{release.STEM}_WINDOWS_X64.zip'
    with zipfile.ZipFile(portable, 'w') as archive:
        archive.writestr('Settlers3MapGen/Settlers3MapGen.exe', b'fixture')
    digest = hashlib.sha256(portable.read_bytes()).hexdigest()
    portable.with_suffix('.zip.sha256').write_text(digest + '  ' + portable.name)
    for suffix in ('SELFTEST', 'QUALIFICATION'):
        (tmp_path / f'{release.STEM}_WINDOWS_X64_{suffix}.json').write_text(json.dumps({
            'status': 'PASS', 'app_version': '2.0 STABLE', 'frozen': True, 'errors': []}))
    return portable


def test_release_accepts_qualified_assets_with_correct_checksum(tmp_path):
    portable = assets(tmp_path)
    assert release.validate_assets(tmp_path) == portable


@pytest.mark.parametrize('failure', ['checksum', 'old_version', 'failed_report', 'not_frozen'])
def test_release_rejects_wrong_or_unqualified_assets(tmp_path, failure):
    portable = assets(tmp_path)
    if failure == 'checksum':
        portable.with_suffix('.zip.sha256').write_text('0' * 64)
    else:
        path = tmp_path / f'{release.STEM}_WINDOWS_X64_SELFTEST.json'
        report = json.loads(path.read_text())
        report[{'old_version': 'app_version', 'failed_report': 'status', 'not_frozen': 'frozen'}[failure]] = {
            'old_version': '2.0 DEV_11', 'failed_report': 'FAIL', 'not_frozen': False}[failure]
        path.write_text(json.dumps(report))
    with pytest.raises(ValueError):
        release.validate_assets(tmp_path)


def test_publication_cannot_run_outside_authorized_main_workflow(tmp_path, monkeypatch):
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(release, 'api', lambda *a, **kw: pytest.fail('Must not call GitHub'))
    with pytest.raises(RuntimeError, match='authorized main'):
        release.publish(tmp_path)
