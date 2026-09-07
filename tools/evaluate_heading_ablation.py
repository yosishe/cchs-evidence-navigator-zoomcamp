"""Bounded heading ablation on development data; no model downloads or promotion."""
import copy
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, digest, load_config, read_json, runtime_code_id, write_json
from navigator.corpus import prepare
from navigator.evaluation import metrics, validate_questions
from navigator.retrieval import Retriever


def run():
    # Existing cached MiniLM only. Never select from or score final-test questions.
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    base = load_config()
    docs, _, _ = prepare(cfg=base)
    bank = read_json(ROOT / base['question_bank'])
    questions = [q for q in bank['questions'] if q['split'] == 'tuning']
    validate_questions(questions, docs)
    if bank['corpus_id'] != digest(docs):
        raise ValueError('Question/corpus mismatch')
    out = ROOT / 'reports/decision-refinement'
    prior_runtime = os.environ.get('NAVIGATOR_RUNTIME')
    # Avoid overwriting the application's embedding receipt with a candidate's.
    os.environ['NAVIGATOR_RUNTIME'] = str(out / 'heading-runtime')
    variants = []
    for representation in ('baseline', 'headings'):
        for method in ('lexical', 'vector', 'hybrid'):
            cfg = copy.deepcopy(base)
            cfg['retrieval'] = method
            if representation == 'headings':
                cfg['embedding_text'] = 'title_heading_content'
                cfg['lexical_fields'] = ['title', 'section', 'section_heading', 'content']
                cfg['boosts']['section_heading'] = 1
            variants.append((representation + '-' + method, cfg))
    report = {'status': 'PLANNED', 'runtime_code_id': runtime_code_id(),
              'corpus_id': digest(docs), 'development_questions_hash': digest(questions),
              'split': 'tuning', 'test_evaluated': False, 'runtime_promoted': False,
              'generation_requests': 0, 'labels': 'ASSISTANT_AUTHORED_PROVISIONAL',
              'design': 'Six predeclared variants; fixed corpus, 42 development questions, top-5. '
                        'Heading vector/text are separate branch ablations; heading hybrid combines them. '
                        'No encoder truncation; rank by reference coverage then Hit then MRR. '
                        'Report all slice regressions; no automatic promotion.',
              'variants': [{'id': name, 'config': cfg} for name, cfg in variants], 'results': []}
    write_json(out / 'heading-ablation.json', report)
    try:
        for name, cfg in variants:
            started = time.perf_counter()
            engine = Retriever(docs, cfg)
            setup = time.perf_counter()
            if cfg['retrieval'] != 'lexical':
                engine.load_vectors()
            setup_seconds = time.perf_counter() - setup
            rows = []
            for q in questions:
                start = time.perf_counter()
                trace = {}
                hits = engine.search(q['question'], trace=trace)
                elapsed = time.perf_counter() - start
                refs = q['reference_quotes']
                coverage = (sum(any(h['id'] in ref['acceptable_ids'] for h in hits) for ref in refs) / len(refs)) if refs else None
                rows.append({'id': q['id'], 'slice': q['slice'], 'answerable': q['answerable'],
                             'metrics': metrics([h['id'] for h in hits], q['relevant_ids']) if q['answerable'] else None,
                             'reference_coverage': coverage, 'query_seconds': elapsed,
                             'context_characters': sum(len(h['content']) for h in hits), 'trace': trace})
            def aggregate(subset):
                eligible = [r for r in subset if r['answerable']]
                n = len(eligible)
                return {'questions': len(subset), 'answerable_denominator': n,
                        'hits': sum(r['metrics']['hit'] for r in eligible),
                        'hit_at_5': sum(r['metrics']['hit'] for r in eligible)/n if n else None,
                        'mrr_at_5': sum(r['metrics']['reciprocal_rank'] for r in eligible)/n if n else None,
                        'reference_coverage': sum(r['reference_coverage'] for r in eligible)/n if n else None,
                        'fully_covered': sum(r['reference_coverage'] == 1 for r in eligible)}
            result = {'id': name, 'config': cfg, 'aggregate': aggregate(rows),
                      'slices': {s: aggregate([r for r in rows if r['slice'] == s]) for s in sorted({r['slice'] for r in rows})},
                      'setup_seconds': setup_seconds, 'total_seconds': time.perf_counter()-started,
                      'embedding': read_json(out / 'heading-runtime/embedding-report.json') if cfg['retrieval'] != 'lexical' else None,
                      'per_question': rows}
            report['results'].append(result)
            report['status'] = 'RUNNING'
            write_json(out / 'heading-ablation.json', report)
            print(name, result['aggregate'], flush=True)
        report['status'] = 'EXECUTED_PROVISIONAL_LABELS'
        write_json(out / 'heading-ablation.json', report)
    except Exception as exc:
        report['status'] = 'INCOMPLETE'
        report['error_type'] = type(exc).__name__
        write_json(out / 'heading-ablation.json', report)
        raise
    finally:
        if prior_runtime is None:
            os.environ.pop('NAVIGATOR_RUNTIME', None)
        else:
            os.environ['NAVIGATOR_RUNTIME'] = prior_runtime


if __name__ == '__main__':
    run()
