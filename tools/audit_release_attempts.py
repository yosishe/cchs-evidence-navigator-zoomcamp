"""Reconcile new release experiments with actual local provider-attempt journals.

Imported historical experiments are excluded by the migration manifest. A pending
or orphan attempt is retained as a gap; neither is silently counted as a success.
"""
from pathlib import Path
from collections import Counter
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from navigator.common import read_json, write_json, digest, utc_now


def run():
    imported = {item['path'] for item in read_json(ROOT/'reports/release-migration/baseline-import.json')['files']}
    references, experiments, findings = {}, [], []
    def add(call, location):
        key=call['id']
        entry=references.setdefault(key, {'id':key, 'provider':call['provider'], 'stage':call['stage'],
                                        'status':call['status'], 'locations':[], 'hash':digest(call)})
        entry['locations'].append(location)
        if digest(call)!=entry['hash']:
            findings.append({'kind':'CONFLICTING_CALL_RECEIPTS','call_id':key})
    for path in sorted((ROOT/'reports/experiments').glob('answers-*/results.json')):
        relative=str(path.relative_to(ROOT))
        if relative in imported: continue
        result=read_json(path)
        experiments.append({'path':relative,'status':result['status'],
                            'declared_actual_provider_requests':result.get('actual_provider_requests'),
                            'runtime_code_id':result.get('runtime_code_id')})
        for call in result.get('preparation_calls',[]): add(call,relative)
        for row in result.get('per_question',[]):
            for call in row['record'].get('calls',[]): add(call,relative)
    feasible=ROOT/'reports/release-quality/feasibility.json'
    # Oracle source contexts diagnose a known failure. They never join the
    # normal retrieval-quality denominator, but their actual calls still count.
    for path in sorted((ROOT/'reports/experiments').glob('answers-*/reference-diagnostic-*.json')):
        relative = str(path.relative_to(ROOT))
        if relative in imported: continue
        result = read_json(path)
        experiments.append({'path': relative, 'status': result['status'],
                            'scope': 'KNOWN_REFERENCE_DIAGNOSTIC_NOT_SELECTION',
                            'declared_actual_provider_requests': result.get('actual_provider_requests')})
        for row in result.get('rows', []):
            for call in row['record'].get('calls', []): add(call, relative)
    if feasible.exists():
        for row in read_json(feasible).get('records',[]):
            for call in row['record'].get('calls',[]): add(call,str(feasible.relative_to(ROOT)))
    # A browser action has its own QA origin and is not a development quality row.
    for path in sorted((ROOT/'reports/release-browser').glob('*record.json')):
        for call in read_json(path).get('calls',[]): add(call,str(path.relative_to(ROOT)))
    journal={}
    for folder in (ROOT/'runtime/provider-attempts', ROOT/'runtime/browser-qa/provider-attempts'):
        for path in sorted(folder.glob('*.json')):
            try: call=read_json(path)
            except json.JSONDecodeError:
                findings.append({'kind':'JOURNAL_WRITE_IN_PROGRESS','path':str(path.relative_to(ROOT))});continue
            journal[call['id']]=call
            if call['id'] in references and digest(call)!=references[call['id']]['hash']:
                findings.append({'kind':'JOURNAL_RESULT_MISMATCH','call_id':call['id']})
    unlinked=sorted(set(journal)-set(references))
    missing=sorted(set(references)-set(journal))
    active=any(e['status']=='RUNNING' for e in experiments)
    if missing: findings.append({'kind':'RESULT_WITHOUT_LOCAL_JOURNAL','call_ids':missing})
    report={'created_at':utc_now(), 'status':('RUNNING_RECONCILIATION' if active else
            'REVIEW_REQUIRED' if findings or unlinked else 'RECONCILED'),
            'scope':'New public-copy generation/rewrite attempts only; imported historical results excluded. Read-only model metadata calls and software fixtures are not generation attempts.',
            'journal_attempts':len(journal),'linked_unique_attempts':len(references),
            'journal_statuses':dict(Counter(c['status'] for c in journal.values())),
            'journal_stages':dict(Counter(c['stage'] for c in journal.values())),
            'providers':dict(Counter(c['provider'] for c in journal.values())),
            'unlinked_attempts':[{'id':key,'status':journal[key]['status'],'stage':journal[key]['stage']} for key in unlinked],
            'findings':findings,'experiments':experiments,'linked_calls':list(references.values()),
            'note':'An unlinked attempt during an active run can be in flight; after termination it requires retained failure evidence. Do not omit it or claim a completed experiment.'}
    write_json(ROOT/'reports/release-quality/attempt-accounting.json',report)
    print(json.dumps({k:report[k] for k in ('status','journal_attempts','linked_unique_attempts','journal_statuses','journal_stages','unlinked_attempts','findings')},indent=2))
    return 1 if findings or (unlinked and not active) else 0


if __name__=='__main__': raise SystemExit(run())
