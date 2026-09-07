"""Scoped publication audit of Git-includable files, never print secret values.

This is a credential-pattern and private-dependency check, not a guarantee that
arbitrary personal content or all possible credentials have been recognized.
"""
from pathlib import Path
import hashlib
import html
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from navigator.common import utc_now, write_json

ROOT_FILES = {'.dockerignore', '.env.example', '.gitignore', 'Dockerfile', 'README.md',
              'app.py', 'compose.yaml', 'pyproject.toml', 'uv.lock',
              'requirements.lock', 'requirements-vectors.lock',
              'requirements-container-arm64.lock', 'requirements-container-amd64.lock'}
DIRECTORIES = {'configs', 'data', 'docs', 'navigator', 'reports', 'tests', 'tools'}
PATTERNS = {
    'PRIVATE_KEY': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'GITHUB_TOKEN': rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    'MODEL_API_KEY': rb'\bsk-[A-Za-z0-9_-]{30,}',
    'OWNER_ABSOLUTE_PATH': rb'(?:/(?:Users|home)/[^/\s]+/|[A-Z]:\\Users\\)',
}


def language_findings(text):
    """Enforce the owner's no-Hebrew submission rule without storing content.

    Inspect literal text, URL encoding, HTML entities and JSON Unicode escapes.
    This is a bounded script check, not a general natural-language classifier.
    English scientific writing can legitimately contain non-ASCII symbols.
    """
    findings = []
    for line_number, line in enumerate(text.splitlines(), 1):
        decoded = line
        for _ in range(2):
            decoded = html.unescape(unquote(decoded))
            def decode_escape(match):
                number = int(match.group(1) or match.group(2), 16)
                return chr(number) if number <= 0x10FFFF else match.group(0)
            decoded = re.sub(r"\\(?:u([0-9a-fA-F]{4})|U([0-9a-fA-F]{8}))",
                             decode_escape, decoded)
        if any(0x0590 <= ord(char) <= 0x05FF or 0xFB1D <= ord(char) <= 0xFB4F
               for char in decoded):
            findings.append({'kind': 'HEBREW_CONTENT', 'line': line_number})
    return findings


def run():
    raw = subprocess.check_output(['git', 'ls-files', '--cached', '--others',
                                   '--exclude-standard', '-z'], cwd=ROOT)
    paths = sorted({p.decode() for p in raw.split(b'\0') if p})
    findings, inventory = [], []
    for relative in paths:
        # The audit's own changing output is evidence, not an input to its hash.
        if relative == 'reports/release-migration/public-package-audit.json':
            continue
        path = ROOT / relative
        for finding in language_findings(relative):
            findings.append({'path': relative, 'location': 'filename', **finding})
        if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            findings.append({'path': relative, 'kind': 'SYMLINK_OR_OUTSIDE_ROOT'})
            continue
        if (relative not in ROOT_FILES and Path(relative).parts[0] not in DIRECTORIES):
            findings.append({'path': relative, 'kind': 'OUTSIDE_PUBLIC_ALLOWLIST'})
        if (path.name.startswith('.env') and relative != '.env.example') or path.suffix in {
                '.pem', '.key', '.sqlite', '.db', '.duckdb', '.safetensors', '.gguf', '.pkl'}:
            findings.append({'path': relative, 'kind': 'PRIVATE_OR_GENERATED_ASSET'})
        data = path.read_bytes()
        inventory.append({'path': relative, 'size_bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest()})
        if b'\0' in data:
            continue  # Screenshots still need separate visual review.
        for finding in language_findings(data.decode('utf-8', errors='replace')):
            findings.append({'path': relative, **finding})
        for kind, expression in PATTERNS.items():
            for match in re.finditer(expression, data):
                findings.append({'path': relative, 'kind': kind,
                                 'line': data[:match.start()].count(b'\n') + 1})
    report = {'created_at': utc_now(), 'status': 'PASS_SCOPED_SCAN' if not findings else 'REVIEW_REQUIRED',
              'scope': 'Git-includable files; explicit directories, credential patterns, private paths, asset types, and literal/URL/JSON/HTML-encoded Hebrew content. No secret values are printed or stored in findings. Binary content requires visual review; absence of Hebrew is not general English-language certification.',
              'files_checked': len(inventory), 'size_bytes': sum(p['size_bytes'] for p in inventory),
              'findings': findings, 'files': inventory,
              'not_established': ['absence of every possible credential or personal detail',
                                  'legal clearance of all third-party content',
                                  'model quality', 'clean execution', 'publication approval']}
    write_json(ROOT/'reports/release-migration/public-package-audit.json', report)
    print(json.dumps({k: report[k] for k in ('status', 'files_checked', 'size_bytes', 'findings')}, indent=2))
    return 0 if not findings else 1


if __name__ == '__main__':
    raise SystemExit(run())
