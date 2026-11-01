"""Build public source assets and publish the qualified 2.0 from its exact commit."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REPOSITORY = 'JulienP36/settlers3-mapgen'
TAG = 'v2.0'
EXPECTED_RC = '1ed1626492bb0df476d7f01f5528689fcdfb2a01'
STEM = 'SETTLERS3_MAPGEN_V2_0_STABLE'


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def command(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, **kwargs)


def api(path, *, method='GET', data=None, missing_ok=False):
    args = ['gh', 'api', '--method', method, f'repos/{REPOSITORY}/{path}']
    if data is not None:
        args += ['--input', '-']
    result = command(args, input=json.dumps(data) if data is not None else None)
    if result.returncode:
        if missing_ok and 'HTTP 404' in result.stderr:
            return None
        raise RuntimeError(result.stderr.strip() or f'GitHub API failed: {path}')
    return json.loads(result.stdout) if result.stdout.strip() else None


def validate_assets(folder):
    """Refuse incomplete packages or reports for another application version."""
    portable = folder / f'{STEM}_WINDOWS_X64.zip'
    for suffix in ('SELFTEST', 'QUALIFICATION'):
        report = json.loads((folder / f'{STEM}_WINDOWS_X64_{suffix}.json').read_text(encoding='utf-8-sig'))
        if report.get('status') != 'PASS' or report.get('app_version') != '2.0 STABLE':
            raise ValueError(f'Unqualified {suffix} report')
        if suffix == 'SELFTEST' and (not report.get('frozen') or report.get('errors')):
            raise ValueError('The portable must validate as a frozen runtime')
    recorded = (folder / f'{STEM}_WINDOWS_X64.zip.sha256').read_text(encoding='utf-8-sig').split()[0]
    if recorded.lower() != sha256(portable):
        raise ValueError('Portable checksum mismatch')
    with zipfile.ZipFile(portable) as archive:
        names = {name.replace('\\', '/') for name in archive.namelist()}
        if archive.testzip() is not None:
            raise ValueError('Corrupt portable ZIP')
        if 'Settlers3MapGen/Settlers3MapGen.exe' not in names:
            raise ValueError('Portable executable missing')
        if any(name.lower().endswith('.bat') for name in names):
            raise ValueError('Source launchers must not enter the portable')
    return portable


def prepare(folder):
    from s3mapgen.version import APP_VERSION
    if APP_VERSION != '2.0 STABLE':
        raise ValueError('Only the final 2.0 STABLE source can be released')
    folder.mkdir(parents=True, exist_ok=True)
    validate_assets(folder)
    source = folder / f'{STEM}_SOURCES.zip'
    subprocess.run(['git', 'archive', '--format=zip', f'--prefix={STEM}_SOURCES/',
                    '-o', str(source), 'HEAD'], cwd=ROOT, check=True)
    with zipfile.ZipFile(source) as archive:
        names = [name.split('/', 1)[1] for name in archive.namelist()]
        if any(name.startswith('references/') for name in names):
            raise ValueError('Research references are not public release assets')
        if not {'run_gui.bat', 'install_and_run.bat', 'run_gui.py'}.issubset(names):
            raise ValueError('Incomplete public source package')
    (folder / f'{source.name}.sha256').write_text(f'{sha256(source)}  {source.name}\n', encoding='ascii')
    files = [source, source.with_suffix('.zip.sha256'),
             folder / f'{STEM}_WINDOWS_X64.zip', folder / f'{STEM}_WINDOWS_X64.zip.sha256',
             folder / f'{STEM}_WINDOWS_X64_SELFTEST.json', folder / f'{STEM}_WINDOWS_X64_QUALIFICATION.json']
    manifest = {path.name: sha256(path) for path in files}
    (folder / 'release_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return files


def publish(folder):
    if (os.environ.get('GITHUB_ACTIONS') != 'true'
            or os.environ.get('GITHUB_REF') != 'refs/heads/main'
            or os.environ.get('GITHUB_REPOSITORY') != REPOSITORY):
        raise RuntimeError('Publication is restricted to the authorized main workflow')
    commit = command(['git', 'rev-parse', 'HEAD'], check=True).stdout.strip()
    if commit != os.environ.get('GITHUB_SHA'):
        raise RuntimeError('Checkout differs from the workflow commit')
    files = prepare(folder)
    ref = api(f'git/ref/tags/{TAG}', missing_ok=True)
    if ref is None:
        annotated = api('git/tags', method='POST', data={
            'tag': TAG, 'message': 'Settlers III MapGen 2.0 STABLE',
            'object': commit, 'type': 'commit'})
        api('git/refs', method='POST', data={'ref': f'refs/tags/{TAG}', 'sha': annotated['sha']})
    else:
        if ref['object']['type'] != 'tag':
            raise RuntimeError('Existing release tag is not annotated; refusing to replace it')
        tag = api(f"git/tags/{ref['object']['sha']}")
        if tag['object']['sha'] != commit:
            raise RuntimeError('Release tag belongs to another commit; refusing to replace it')
    notes = (ROOT / 'docs/RELEASE_2_0.md').read_text(encoding='utf-8')
    notes += '\n\n## SHA-256\n\n```text\n' + '\n'.join(
        f'{sha256(path)}  {path.name}' for path in files if path.suffix == '.zip') + '\n```\n'
    release = api(f'releases/tags/{TAG}', missing_ok=True)
    if release is None:
        release = api('releases', method='POST', data={
            'tag_name': TAG, 'target_commitish': commit, 'name': 'Settlers III MapGen 2.0',
            'body': notes, 'draft': True, 'prerelease': False})
    if not release.get('draft'):
        raise RuntimeError('Release is already public; refusing to overwrite published assets')
    result = command(['gh', 'release', 'upload', TAG, '--repo', REPOSITORY,
                      '--clobber', *[str(path) for path in files]])
    if result.returncode:
        raise RuntimeError(result.stderr)
    uploaded = api(f"releases/{release['id']}/assets")
    remote = {item['name']: item for item in uploaded}
    for path in files:
        item = remote.get(path.name)
        if not item or item.get('digest') != 'sha256:' + sha256(path):
            raise RuntimeError(f'Uploaded asset digest mismatch: {path.name}')
    public = api(f"releases/{release['id']}", method='PATCH', data={
        'body': notes, 'draft': False, 'prerelease': False, 'make_latest': 'true'})
    if public.get('draft') or public.get('prerelease'):
        raise RuntimeError('Release did not become STABLE')
    rc = api('git/ref/heads/rc', missing_ok=True)
    if rc is not None:
        if rc['object']['sha'] != EXPECTED_RC:
            raise RuntimeError('rc changed since authorization; release is public, branch retained for review')
        api('git/refs/heads/rc', method='DELETE')
    (folder / 'publication.json').write_text(json.dumps({
        'status': 'PASS', 'commit': commit, 'tag': TAG, 'release_url': public['html_url'],
        'release_id': public['id'], 'rc_deleted': True,
        'assets': {path.name: sha256(path) for path in files}}, indent=2) + '\n')
    print(public['html_url'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--folder', type=Path, default=ROOT / 'artifacts')
    args = parser.parse_args()
    publish(args.folder) if args.publish else prepare(args.folder)
