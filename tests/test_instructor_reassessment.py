"""Adversarial grading-evidence contracts, never a real model-quality benchmark."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from navigator.common import digest
from navigator.exports import claim_rows, passage_rows
from navigator.experiments import select_generation
from navigator.rag import generate
import test_core_completion
from test_review_regressions import evidence


class ExportBoundaryTests(unittest.TestCase):
    def test_preview_and_empty_whitespace_quotes_cannot_export_claims(self):
        h, cfg, payload = evidence()
        for mode, quote in [('evidence_preview', h['content'][:20]), ('llm', ''), ('llm', ' '), ('llm', None)]:
            record = generate('fixture', [h], cfg, 'fixture')
            record.update(copy.deepcopy(payload))
            record['mode'] = mode
            record['claims'][0]['exact_quote'] = quote
            with self.subTest(mode=mode, quote=quote), self.assertRaises(ValueError):
                claim_rows(record)

    def test_source_exports_include_license_and_language(self):
        h, cfg, _ = evidence()
        row = passage_rows(generate('fixture', [h], cfg, 'fixture'))[0]
        self.assertEqual(row['license'], h['license'])
        self.assertEqual(row['language'], h['language'])


class SelectionConsistencyTests(unittest.TestCase):
    def test_rehashed_inconsistent_evidence_cannot_select(self):
        mutations = ['reference', 'question', 'source', 'context_id', 'config', 'raw_output', 'fixture', 'missing_call', 'request']
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temp:
                folder = Path(temp)
                rp, vp, docs, bank, results = test_core_completion.SelectionEvidenceTests().make_evidence(folder)
                reviews = json.loads(vp.read_text())
                if mutation == 'reference':
                    results['questions'][0]['required_facts'][0]['text'] = 'Changed requirement'
                for row, review in zip(results['per_question'], reviews['reviews']):
                    record = row['record']
                    if mutation == 'question': record['question'] = 'A different question'
                    elif mutation == 'source': record['hits'][0]['content'] += ' Altered source.'
                    elif mutation == 'context_id': record['context_id'] = 'same-but-unverified-context'
                    elif mutation == 'config':
                        record['config']['temperature'] = 0.9
                        record['config_id'] = digest(record['config'])
                    elif mutation == 'raw_output': record['raw_output'] = '{}'
                    elif mutation == 'fixture': record['calls'][0]['execution_kind'] = 'sdk_fixture'
                    elif mutation == 'missing_call': record['calls'] = []
                    elif mutation == 'request': record['calls'][0]['messages'][1]['content'] = 'Unrelated request'
                    row['record_hash'] = digest(record)
                    review['record_hash'] = row['record_hash']
                reviews['results_hash'] = digest(results)
                rp.write_text(json.dumps(results)); vp.write_text(json.dumps(reviews))
                with patch('navigator.experiments.ROOT', folder), \
                     patch('navigator.experiments.runtime_code_id', return_value='fixture-code'), \
                     patch('navigator.experiments.read_documents', return_value=docs), \
                     patch('navigator.experiments.load_question_bank', return_value=bank), self.assertRaises(ValueError):
                    select_generation([rp], [vp], apply=True)
                self.assertFalse((folder / 'configs/app.json').exists())

    def test_runtime_detects_changed_calibration_without_calling_judge(self):
        from navigator.common import verify_generation_selection
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            rp, vp, docs, bank, _ = test_core_completion.SelectionEvidenceTests().make_evidence(folder)
            with patch('navigator.experiments.ROOT', folder), patch('navigator.common.ROOT', folder), \
                 patch('navigator.experiments.runtime_code_id', return_value='fixture-code'), \
                 patch('navigator.common.runtime_code_id', return_value='fixture-code'), \
                 patch('navigator.experiments.read_documents', return_value=docs), \
                 patch('navigator.experiments.load_question_bank', return_value=bank):
                artifact = select_generation([rp], [vp], apply=True)
                path = folder / 'reports/calibration-fixture'
                path.mkdir()
                fixtures, reviews = {'fictional': True}, {'review': 'fixture'}
                calibration = {'fixtures_hash': digest(fixtures), 'reviews_hash': digest(reviews)}
                for name, obj in [('fixtures', fixtures), ('reviews', reviews), ('calibration', calibration)]:
                    (path / (name + '.json')).write_text(json.dumps(obj))
                artifact['inputs'][0]['calibration'] = {'path': 'reports/calibration-fixture/calibration.json', 'artifact_hash': digest(calibration)}
                (folder / 'reports/core-completion/generation-selection.json').write_text(json.dumps(artifact))
                cfg = json.loads((folder / 'configs/app.json').read_text())
                self.assertEqual(verify_generation_selection(cfg)['status'], 'SELECTED_ON_PROVISIONAL_AGENT_REVIEW')
                (path / 'fixtures.json').write_text('{}')
                with self.assertRaisesRegex(ValueError, 'calibration'):
                    verify_generation_selection(cfg)


if __name__ == '__main__':
    unittest.main()
