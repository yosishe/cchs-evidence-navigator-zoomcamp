"""Predeclared per-passage RAG diagnostic; never application selection evidence."""
import copy
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from navigator.common import ROOT, read_json, write_json, digest, runtime_code_id, utc_now
from navigator.providers import complete, model_identity
from navigator.rag import validate_answer
from navigator.whole_review import export_payload, whole_review_template
import source_attached_prototype as attachment


def run(plan_path):
    plan_path = Path(plan_path)
    plan = read_json(plan_path)
    if plan['status'] != 'PLANNED':
        raise ValueError('A dispatched diagnostic cannot be restarted')
    attachment.check_adapter()
    source = read_json(ROOT / plan['source_run'])
    if digest(source) != plan['source_results_hash']:
        raise ValueError('Frozen source input changed')
    if [q['id'] for q in source['questions']] != plan['question_ids']:
        raise ValueError('Question order differs from plan')
    cfg = {**plan['config'], 'prompt': 'prototype_single_source_claims'}
    identity = model_identity(cfg)
    folder = ROOT / 'reports/goal-loop' / ('single-source-prototype-' + str(uuid.uuid4()))
    report = {'created_at': utc_now(), 'status': 'RUNNING', 'split': 'source_isolation_diagnostic',
        'scope': 'PROTOTYPE_NOT_APPLICATION_OR_SELECTION_EVIDENCE', 'runtime_code_id': runtime_code_id(),
        'prototype_code_id': digest(Path(__file__).read_bytes()),
        'attachment_code_id': digest(Path(attachment.__file__).read_bytes()),
        'config': cfg, 'config_id': digest(cfg), 'model_identity': identity,
        'questions': source['questions'], 'prompts': [cfg['prompt']],
        'per_question': [], 'actual_provider_requests': 0, 'official_points': None}
    plan.update(status='RUNNING', run_directory=str(folder.relative_to(ROOT)))
    write_json(plan_path, plan); write_json(folder / 'plan.json', plan)
    (folder / 'prototype-source.py').write_bytes(Path(__file__).read_bytes())
    (folder / 'attachment-source.py').write_bytes(Path(attachment.__file__).read_bytes())
    write_json(folder / 'results.json', report)
    for q in source['questions']:
        if runtime_code_id() != report['runtime_code_id']:
            raise ValueError('Runtime changed during diagnostic')
        model_identity(cfg)
        old = next(r['record'] for r in source['per_question']
                   if r['question_id'] == q['id'] and r['prompt'] == 'evidence_first')
        rec = {'id': str(uuid.uuid4()), 'timestamp': utc_now(), 'mode': 'llm', 'prototype_only': True,
            'question': q['question'], 'config': cfg, 'config_id': digest(cfg),
            'corpus_id': old['corpus_id'], 'runtime_code_id': report['runtime_code_id'],
            'hits': copy.deepcopy(old['hits']), 'context': old['context'], 'context_id': old['context_id'],
            'instructions': plan['instructions'], 'calls': [], 'passage_results': [],
            'status': 'started', 'claims': [], 'limitations': '',
            'quote_selection_method': 'application_full_source_window',
            'support_review': 'PENDING_AGENT_REVIEW', 'scientific_review': 'PENDING_HUMAN_REVIEW'}
        failed, stop, claims = False, False, []
        for passage, hit in zip(json.loads(old['context']), old['hits'], strict=True):
            assert passage['evidence_id'] == hit['id']
            passage.update(evidence_id='E1')
            passage.pop('source_url'); passage.pop('source_version')
            messages = [{'role': 'system', 'content': plan['instructions']},
                        {'role': 'user', 'content': json.dumps({'question': q['question'], 'passages': [passage]})}]
            item = {'evidence_id': hit['id'], 'call_start_index': len(rec['calls'])}
            try:
                raw = complete(cfg, messages, stage='generation', ledger=rec['calls'])
                answer = attachment.attach_claims_only(raw, [hit])
                claims.extend(answer['claims']); item.update(status='decoded', answer=answer)
            except (ValueError, TypeError, KeyError) as exc:
                failed = True
                item.update(status='invalid_output', error_type=type(exc).__name__)
            except Exception as exc:
                failed, stop = True, True
                item.update(status='provider_error', error_type=type(exc).__name__)
            item['call_ids'] = [c['id'] for c in rec['calls'][item['call_start_index']:]]
            rec['passage_results'].append(item)
            # Preserve each completed source attempt before starting the next one.
            write_json(folder / ('pending-' + q['id'] + '.json'), rec)
            if stop:
                break
        if failed:
            rec.update(status='error', claims=[], error_stage='provider' if stop else 'output_validation',
                limitations='At least one source-level attempt failed; no combined answer is accepted. All attempts are retained.')
        else:
            note = ('The cited source windows are attached in full. Human review is pending.' if claims else
                'No sourced answer was produced from the retrieved passages. This does not establish absence from the wider literature. Human review is pending.')
            rec.update(validate_answer({'status': 'answered' if claims else 'insufficient_evidence',
                                        'claims': claims, 'limitations': note}, rec['hits']))
        for key in ['input_tokens', 'output_tokens', 'seconds']:
            values = [c.get(key) for c in rec['calls']]
            rec[key] = sum(values) if values and all(v is not None for v in values) else None
        rec.update(raw_output=json.dumps([c.get('raw_output') for c in rec['calls']]), cost_usd=0.0)
        report['per_question'].append({'question_id': q['id'], 'answerable': q['answerable'],
            'prompt': cfg['prompt'], 'record': rec, 'record_hash': digest(rec)})
        report['actual_provider_requests'] += len(rec['calls'])
        write_json(folder / 'results.json', report)
        if stop:
            report['status'] = 'STOPPED_ON_ERROR'
            break
    else:
        report['status'] = 'EXECUTED_AWAITING_REVIEW'
    report['completed_at'] = utc_now()
    write_json(folder / 'results.json', report)
    write_json(folder / 'whole-answer-review-template.json', whole_review_template(report))
    write_json(folder / 'export-adapter-payloads.json', {'scope': 'Diagnostic payloads, not browser downloads. No production integration.',
        'quote_selection_method': 'application_full_source_window',
        'answers': [{'answer_id': row['record']['id'], 'payload': export_payload(row['record'])} for row in report['per_question']]})
    print({'status': report['status'], 'run_directory': str(folder.relative_to(ROOT)),
           'actual_provider_requests': report['actual_provider_requests']})


if __name__ == '__main__':
    run(sys.argv[1])
