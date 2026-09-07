"""Check relative Markdown file targets and anchors, ignoring fenced examples."""
from pathlib import Path
import re
import sys
import urllib.parse
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, utc_now, write_json


def visible_markdown(text):
    return re.sub(r'^(```|~~~).*?^\1\s*$', '', text, flags=re.M | re.S)


def anchors(path):
    text = visible_markdown(path.read_text())
    output = set(re.findall(r'<a\s+[^>]*id=["\']([^"\']+)', text))
    used = {}
    for line in text.splitlines():
        match = re.match(r'^#{1,6}\s+(.+?)\s*#*$', line)
        if not match: continue
        title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', match[1]).lower()
        title = re.sub(r'<[^>]+>', '', title)
        slug = re.sub(r'[^\w\- ]', '', title).replace(' ', '-')
        count = used.get(slug, 0); used[slug] = count + 1
        output.add(slug + (f'-{count}' if count else ''))
    return output


def run():
    files = [ROOT/'README.md', *sorted((ROOT/'docs').rglob('*.md')), ROOT/'data/README.md']
    findings = []; checked = 0
    for path in files:
        text = visible_markdown(path.read_text())
        for match in re.finditer(r'!?\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)', text):
            target = match[1].strip('<>'); url = urllib.parse.urlsplit(target)
            if url.scheme or url.netloc: continue
            checked += 1
            destination = (path.parent/urllib.parse.unquote(url.path)).resolve() if url.path else path
            reason = None
            if not destination.is_relative_to(ROOT): reason = 'OUTSIDE_PUBLIC_ROOT'
            elif not destination.exists(): reason = 'MISSING_LOCAL_TARGET'
            elif url.fragment and destination.suffix == '.md' and urllib.parse.unquote(url.fragment) not in anchors(destination):
                reason = 'MISSING_MARKDOWN_ANCHOR'
            if reason:
                findings.append({'file': str(path.relative_to(ROOT)), 'target': target, 'reason': reason})
    report = {'created_at': utc_now(), 'scope': 'README/docs/data relative Markdown links; fenced examples and external URLs excluded; not an HTTP availability or rendered-browser check',
              'files_checked': len(files), 'links_checked': checked, 'findings': findings,
              'status': 'PASS' if not findings else 'FIX_REQUIRED'}
    write_json(ROOT/'reports/release-migration/link-audit.json', report)
    print(report)
    return 1 if findings else 0


if __name__ == '__main__': raise SystemExit(run())
