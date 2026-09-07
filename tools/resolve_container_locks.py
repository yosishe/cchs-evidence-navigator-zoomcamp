"""Resolve CPU-only Linux locks from existing exact uv versions; installs nothing.

Resolution can cache wheel archives to inspect metadata. Run only when network
access for dependency preparation is intended. Container build remains separate.
"""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import tomllib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, digest, utc_now, write_json

WHEELS = {
    'arm64': ('aarch64', 'da8140c3d4a41500d29710e35bf8e66a4295ec31026487c69f54a3f583310f8d'),
    'amd64': ('x86_64', 'a09987c95ec4cffdb6df798d3d641558110a334cfccce22f2f046d83142bc260'),
}


def resolve(arch, uv):
    versions = {}
    for package in tomllib.loads((ROOT / 'uv.lock').read_text())['package']:
        name = package['name']
        if name.startswith('nvidia-') or name in {'triton', 'cchs-evidence-navigator'}:
            continue
        versions.setdefault(name, set()).add(package['version'])
    if any(len(v) != 1 for v in versions.values()) or versions.get('torch') != {'2.14.0'}:
        raise ValueError('Locked versions changed; review exact CPU artifact compatibility')
    folder = ROOT / 'runtime/container-lock-preparation'; folder.mkdir(parents=True, exist_ok=True)
    constraints = folder / 'constraints.txt'
    constraints.write_text('\n'.join(f'{n}=={next(iter(v))}' for n, v in sorted(versions.items())) + '\n')
    platform, sha = WHEELS[arch]
    source = folder / (arch + '.in')
    source.write_text('torch @ https://download-r2.pytorch.org/whl/cpu/'
        f'torch-2.14.0%2Bcpu-cp312-cp312-manylinux_2_28_{platform}.whl#sha256={sha}\n')
    output = ROOT / f'requirements-container-{arch}.lock'
    args = [uv, 'pip', 'compile', 'pyproject.toml', str(source.relative_to(ROOT)),
        '--extra', 'vectors', '--constraints', str(constraints.relative_to(ROOT)),
        '--python', sys.executable, '--python-platform', f'{platform}-manylinux_2_28',
        '--python-version', '3.12', '--generate-hashes', '--no-header', '--no-annotate',
        '--quiet', '--output-file', output.name]
    env = {**os.environ, 'UV_CACHE_DIR': str(ROOT / 'runtime/uv-resolution-cache'), 'UV_NO_PROGRESS': '1'}
    result = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)
    report = {'created_at': utc_now(), 'architecture': arch, 'exit_code': result.returncode,
        'status': 'RESOLVED_NOT_INSTALLED' if result.returncode == 0 else 'RESOLUTION_FAILED',
        'source_uv_lock_hash': digest((ROOT/'uv.lock').read_bytes()),
        'cpu_wheel_sha256': sha, 'constraints_hash': digest(constraints.read_bytes()),
        'stdout': result.stdout, 'stderr': result.stderr,
        'scope': 'Pinned-version CPU variant resolution. Wheel archives may be cached for metadata; no package installation or container execution.'}
    if result.returncode == 0:
        text = output.read_text()
        if 'nvidia-' in text or '\ntriton==' in text:
            raise ValueError('CPU lock unexpectedly retains GPU runtime packages')
        output.write_text('# CPU-only Linux / CPython 3.12 lock. Regenerate with tools/resolve_container_locks.py.\n' + text)
        report['output_hash'] = digest(output.read_bytes())
    write_json(ROOT/f'reports/release-migration/container-lock-{arch}.json', report)
    print({k:v for k,v in report.items() if k not in {'stdout','stderr'}}, flush=True)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
    return result.returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('architecture', choices=WHEELS)
    parser.add_argument('--uv', default='uv'); args = parser.parse_args()
    raise SystemExit(resolve(args.architecture, args.uv))
