"""Execute a frozen development-only plan with identical prepared contexts.

No evaluation labels enter model messages. Every arm and failed attempt remains
in its own immutable result; existing plans/indexes are never silently rerun.
"""
from pathlib import Path
import argparse
import copy
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT, read_json, write_json, digest, read_documents, runtime_code_id, utc_now
from navigator.evaluation import answer_evaluation, load_question_bank
from navigator.rag import retrieval_policy
from release_experiments import metadata


def run(plan_path):
    plan_path = Path(plan_path)
    plan = read_json(plan_path)
    index_path = plan_path.with_name(plan_path.stem.replace('-plan', '') + '-index.json')
    if index_path.exists():
        raise ValueError('Experiment already started; inspect its receipts instead of rerolling')
    if plan['runtime_code_id'] != runtime_code_id():
        raise ValueError('Runtime changed after experiment declaration')
    docs = read_documents()
    bank = load_question_bank(plan['variants'][0]['config'], docs)
    if digest(docs) != plan['corpus_id'] or digest(bank) != plan['questions_hash']:
        raise ValueError('Protected source or benchmark changed')
    allowed = {q['id'] for q in bank['questions'] if q['split'] == 'tuning'}
    ids = plan['question_ids']
    if len(ids) != len(set(ids)) or not set(ids) <= allowed:
        raise ValueError('Only distinct development questions are allowed')
    contexts = read_json(ROOT / plan['contexts_path'])
    if digest(contexts) != plan['contexts_hash'] or not set(ids) <= set(contexts):
        raise ValueError('Frozen contexts are incomplete or changed')
    for arm in plan['variants']:
        policy = retrieval_policy(arm['config'])
        if any(contexts[key]['retrieval_policy'] != policy for key in ids):
            raise ValueError('Generation arms must use the same declared retrieval')
    report = {'status': 'RUNNING', 'created_at': utc_now(), 'plan_hash': digest(plan),
              'arms': [], 'actual_attempts': 0, 'planned_attempts': len(ids) * len(plan['variants'])}
    write_json(index_path, report)
    for arm in plan['variants']:
        print('Starting ' + arm['arm'], flush=True)
        result = answer_evaluation(config=copy.deepcopy(arm['config']), question_ids=ids,
                    prepared_contexts=contexts, prompt_names=[arm['config']['prompt']])
        entry = {'arm': arm['arm'], 'status': result['status'],
                 'results_path': result['run_directory'] + '/results.json',
                 'actual_attempts': result['actual_provider_requests'], 'after': metadata()}
        report['arms'].append(entry)
        report['actual_attempts'] += entry['actual_attempts']
        write_json(index_path, report)
        print(entry, flush=True)
        if result['status'] != 'EXECUTED_AWAITING_REVIEW':
            report['status'] = 'STOPPED_INCOMPLETE'; write_json(index_path, report); return
    report['status'] = 'EXECUTED_AWAITING_AGENT_REVIEW'; write_json(index_path, report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('plan')
    run(parser.parse_args().plan)
