"""Predeclared development ablation of taught embedding-text alternatives.

Original project experiment glue, no new retrieval algorithm or library. The
frozen corpus, reference labels, top-k and zero-based RRF convention stay fixed.
"""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, read_json, write_json, digest, utc_now, runtime_code_id, read_documents
from navigator.evaluation import load_question_bank, metrics
from navigator.rag import prepare_context
from navigator.retrieval import Retriever


def run():
    out = ROOT / 'reports/release-quality'
    plan_path = out / 'representation-plan.json'
    result_path = out / 'representation-results.json'
    if plan_path.exists() or result_path.exists():
        raise ValueError('A declared iteration cannot be silently repeated')
    base = read_json(ROOT / 'configs/browser-qa-candidate.json')
    docs = read_documents(); bank = load_question_bank(base, docs)
    questions = [q for q in bank['questions'] if q['split'] == 'tuning']
    variants = []
    for template in ['title_content', 'content', 'title_heading_content']:
        for method in ['vector', 'hybrid']:
            cfg = copy.deepcopy(base)
            cfg.update(embedding_text=template, retrieval=method)
            variants.append({'name': template + '-' + method, 'config': cfg})
    plan = {'status': 'PLANNED', 'created_at': utc_now(), 'runtime_code_id': runtime_code_id(),
            'corpus_id': digest(docs), 'questions_hash': digest(bank), 'split': 'tuning',
            'question_ids': [q['id'] for q in questions], 'variants': variants,
            'planned_searches': 252, 'planned_generation_requests': 0,
            'hypothesis': 'Full publication titles may dilute passage-specific meaning. Compare content alone and title plus section heading against the existing title/content template.',
            'fixed': 'Same MiniLM weights, normalized 384 dimensions, 377 windows, top-10, candidate-20, title boost zero and zero-based RRF-50. No reference answers or final questions enter inference.',
            'decision_rule': 'Inspect paired per-question reference coverage and all losses, including annotation equivalence. Higher coverage is only a retrieval candidate; answer quality and actual serving-context feasibility are separate gates.'}
    write_json(plan_path, plan)
    result = {'status': 'RUNNING', 'created_at': utc_now(), 'plan_hash': digest(plan),
              'actual_searches': 0, 'actual_generation_requests': 0, 'arms': []}
    write_json(result_path, result)
    engine = None; previous_template = None
    for arm in variants:
        cfg = arm['config']
        if cfg['embedding_text'] != previous_template:
            engine = Retriever(docs, cfg); engine.load_vectors()
            previous_template = cfg['embedding_text']
        engine.config = cfg
        contexts = {}; rows = []
        for q in questions:
            context = prepare_context(q['question'], engine, cfg, filters=q.get('filters', {}))
            contexts[q['id']] = context
            ids = [h['id'] for h in context['hits']]
            refs = q['reference_quotes']
            covered = [any(i in ref.get('acceptable_ids', [ref['id']]) for i in ids) for ref in refs]
            rows.append({'id': q['id'], 'slice': q['slice'], 'answerable': q['answerable'],
                         'reference_covered': covered, 'reference_coverage': sum(covered)/len(covered) if covered else None,
                         'ranked_ids': ids, 'metrics': metrics(ids, q['relevant_ids']) if q['answerable'] else None,
                         'retrieval_seconds': context['retrieval_seconds'],
                         'context_id': context['context_id']})
            result['actual_searches'] += 1
        eligible = [r for r in rows if r['answerable']]
        contexts_path = out / ('representation-' + arm['name'] + '-contexts.json')
        write_json(contexts_path, contexts)
        embedding = read_json(ROOT / 'runtime/embedding-report.json')
        embedding['cache_directory'] = '<LOCAL_MODEL_CACHE>'
        entry = {**arm, 'per_question': rows, 'contexts_path': str(contexts_path.relative_to(ROOT)),
                 'contexts_hash': digest(contexts), 'answerable_denominator': len(eligible),
                 'fully_covered': sum(r['reference_coverage'] == 1 for r in eligible),
                 'mean_reference_coverage': sum(r['reference_coverage'] for r in eligible)/len(eligible),
                 'hit_at_10': sum(r['metrics']['hit'] for r in eligible)/len(eligible),
                 'mrr_at_10': sum(r['metrics']['reciprocal_rank'] for r in eligible)/len(eligible),
                 'embedding': embedding}
        result['arms'].append(entry); write_json(result_path, result)
        print({k: entry[k] for k in ['name', 'fully_covered', 'mean_reference_coverage', 'hit_at_10', 'mrr_at_10']}, flush=True)
    result['status'] = 'EXECUTED_PROVISIONAL_LABELS_NO_PROMOTION'
    write_json(result_path, result)


if __name__ == '__main__':
    run()
