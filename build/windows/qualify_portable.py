"""Qualify a built Windows folder using isolated data and a relocated copy."""
from __future__ import annotations

import argparse
from copy import deepcopy
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def inspect_executable(executable):
    import pefile
    from s3mapgen.version import WINDOWS_FILE_VERSION

    pe = pefile.PE(str(executable))
    try:
        if pe.FILE_HEADER.Machine != 0x8664 or pe.OPTIONAL_HEADER.Subsystem != 2:
            raise ValueError('Expected a Windows x64 GUI executable.')
        info = pe.VS_FIXEDFILEINFO[0]
        version = (info.FileVersionMS >> 16, info.FileVersionMS & 65535,
                   info.FileVersionLS >> 16, info.FileVersionLS & 65535)
        if version != WINDOWS_FILE_VERSION:
            raise ValueError(f'Executable version mismatch: {version}')
        sizes = set()
        for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            if kind.id == 14:  # RT_GROUP_ICON
                for group in kind.directory.entries:
                    for language in group.directory.entries:
                        entry = language.data.struct
                        data = pe.get_data(entry.OffsetToData, entry.Size)
                        count = struct.unpack_from('<H', data, 4)[0]
                        for index in range(count):
                            width, height = struct.unpack_from('<BB', data, 6 + 14*index)
                            sizes.add((width or 256, height or 256))
        required = {(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)}
        if not required <= sizes:
            raise ValueError(f'Executable icon resources incomplete: {sizes}')
        return {'machine': 'x64', 'subsystem': 'GUI', 'version': version,
                'icon_sizes': sorted(sizes)}
    finally:
        pe.close()


def launch_and_close(executable, environment, cwd):
    user32 = ctypes.windll.user32
    callback_type = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = (callback_type, wintypes.LPARAM)
    user32.EnumWindows.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
    user32.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
    user32.IsWindowVisible.argtypes = (wintypes.HWND,)
    user32.PostMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
    user32.SendMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
    user32.SendMessageW.restype = ctypes.c_ssize_t
    user32.GetClassLongPtrW.argtypes = (wintypes.HWND, ctypes.c_int)
    user32.GetClassLongPtrW.restype = ctypes.c_void_p
    process = subprocess.Popen([str(executable)], cwd=cwd, env=environment)
    found = []

    @callback_type
    def visit(window, _):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(window, ctypes.byref(pid))
        if pid.value == process.pid and user32.IsWindowVisible(window):
            title = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(window, title, len(title))
            if 'settlers' in title.value.casefold():
                found.append((window, title.value))
        return True

    try:
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline and process.poll() is None:
            user32.EnumWindows(visit, 0)
            if found:
                break
            time.sleep(.1)
        if not found:
            raise RuntimeError(f'No application window; process exit={process.poll()}')
        window, title = found[0]
        small = user32.SendMessageW(window, 0x7f, 0, 0) or user32.GetClassLongPtrW(window, -34)
        large = user32.SendMessageW(window, 0x7f, 1, 0) or user32.GetClassLongPtrW(window, -14)
        if not small or not large:
            raise RuntimeError('The native window has no small/large icon handle.')
        user32.PostMessageW(window, 0x10, 0, 0)  # WM_CLOSE
        if process.wait(timeout=15) != 0:
            raise RuntimeError('Application exited with an error after closing its window.')
        return {'title': title, 'small_icon': bool(small), 'large_icon': bool(large)}
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=10)


def qualify(folder):
    from PIL import Image
    from s3mapgen.application.configurations.model import document, preset, write_collection
    from s3mapgen.application.settings.preferences import DEFAULTS
    from s3mapgen.generation.custom import build_custom_config
    from s3mapgen.version import APP_VERSION

    report = {'app_version': APP_VERSION, 'status': 'PASS', 'checks': {}}
    report['checks']['executable'] = inspect_executable(folder/'Settlers3MapGen.exe')
    if not (folder/'_internal').is_dir() or list(folder.glob('*.bat')):
        raise ValueError('Expected the runtime folder and no BAT launcher in the portable.')
    with tempfile.TemporaryDirectory(prefix='MapGen portable é ', ignore_cleanup_errors=True) as tmp:
        base = Path(tmp)
        relocated = base/'application déplacée avec espaces'
        shutil.copytree(folder, relocated)
        appdata = base/'données utilisateur'
        unrelated = base/'autre dossier courant'
        unrelated.mkdir()
        environment = dict(os.environ, APPDATA=str(appdata),
                           PATH=str(Path(os.environ['SystemRoot'])/'System32'),
                           PYTHONHOME=str(base/'python absent'), PYTHONPATH=str(base/'modules absents'),
                           PIP_NO_INDEX='1', HTTP_PROXY='http://127.0.0.1:9',
                           HTTPS_PROXY='http://127.0.0.1:9', NO_PROXY='')
        for scenario in ('fresh', 'existing_data'):
            files = []
            if scenario == 'existing_data':
                data = appdata/'Settlers3MapGen'
                data.mkdir(parents=True, exist_ok=True)
                preferences = deepcopy(DEFAULTS)
                preferences.update(language='de', theme='light', history_capacity=12)
                settings = data/'settings.json'
                settings.write_text(json.dumps(preferences), encoding='utf-8')
                snapshot = dict(mode='upgraded', archetype='continental', size=512, players=4,
                                mirror=0, starts='auto', nations=[0]*20, teams=[0]*20,
                                random_team_count=2, custom=build_custom_config().to_dict())
                collection = data/'configurations.json'
                write_collection(collection, [preset('À conserver', snapshot)])
                mask = data/'masks'/'masque conservé.png'
                mask.parent.mkdir(exist_ok=True)
                Image.new('L', (64, 64), 128).save(mask)
                files = [settings, collection, mask]
            before = {file: file.read_bytes() for file in files}
            selftest = base/f'{scenario}_selftest.json'
            environment['S3MAPGEN_SELFTEST_REPORT'] = str(selftest)
            completed = subprocess.run([str(relocated/'Settlers3MapGen.exe'), '--self-test'],
                                       env=environment, cwd=unrelated, timeout=60)
            if completed.returncode:
                raise RuntimeError(f'Frozen self-test exit {completed.returncode}')
            diagnostic = json.loads(selftest.read_text(encoding='utf-8'))
            if diagnostic.get('status') != 'PASS' or not diagnostic.get('frozen') or diagnostic.get('app_version') != APP_VERSION:
                raise RuntimeError(f'Frozen self-test failed: {diagnostic}')
            for key, expected in (('application_dir', relocated),
                                  ('resource_base', relocated/'_internal'),
                                  ('output_dir', relocated/'output')):
                if Path(diagnostic[key]).resolve() != expected.resolve():
                    raise RuntimeError(f'Relocated {key} points outside the portable: {diagnostic[key]}')
            window = launch_and_close(relocated/'Settlers3MapGen.exe', environment, unrelated)
            if any(file.read_bytes() != payload for file, payload in before.items()):
                raise RuntimeError('User data changed during startup/self-test/normal close.')
            report['checks'][scenario] = {'selftest': 'PASS', 'window': window,
                                          'preserved_files': len(files)}
        report['checks']['relocated_unicode_path'] = True
        report['checks']['unrelated_working_directory'] = True
        report['checks']['external_python_unavailable'] = True
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, default=ROOT/'dist/Settlers3MapGen')
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    if sys.platform != 'win32':
        parser.exit(2, 'Native Windows is required for portable qualification.\n')
    try:
        report = qualify(args.folder.resolve())
    except Exception as exc:
        report = {'status': 'FAIL', 'error': repr(exc)}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
