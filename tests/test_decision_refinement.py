"""Origin integrity and offline setup failures; no downloaded or generated evidence."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from navigator.common import ROOT, load_config
from navigator.monitoring import observed_tables
from navigator.rag import generate, retrieval_policy
from navigator.retrieval import EncoderUnavailableError, Retriever, embedding_text, prepare_encoder
from navigator.storage import Journal, Postgres, feedback_record


class OriginIntegrityTests(unittest.TestCase):
    def test_all_scope_cannot_relabel_qa_as_user(self):
        record = generate('fixture', [], load_config(), 'fixture', traffic_origin='qa')
        valid = feedback_record(record['id'], -1, '', 'qa-vote', 'qa')
        mismatch = feedback_record(record['id'], 1, '', 'mislabelled-vote', 'user')
        data = observed_tables([record], [valid, mismatch], 'all')
        self.assertEqual(data['rated_requests'], 1)
        self.assertEqual(data['feedback'].to_dict(), {'Not helpful': 1})
        self.assertEqual(data['excluded_mismatched_feedback'], 1)

    def test_journal_rejects_mismatch_and_unknown_legacy_origin(self):
        with tempfile.TemporaryDirectory() as temp:
            store = Journal(Path(temp) / 'events.jsonl')
            store.save_answer({'id': 'qa', 'traffic_origin': 'qa'})
            store.save_answer({'id': 'legacy'})
            for answer in ('qa', 'legacy'):
                with self.assertRaisesRegex(ValueError, 'origin'):
                    store.save_feedback(answer, 1, traffic_origin='user')
            self.assertFalse(store.read()[1])
            store.save_feedback('qa', 1, feedback_id='f', traffic_origin='qa')
            store.save_feedback('qa', 1, feedback_id='f', traffic_origin='qa')
            self.assertEqual(len(store.read()[1]), 1)

    def test_postgres_checks_origin_before_insert_without_migration(self):
        # Adapter test, not a live PostgreSQL transaction.
        store = Postgres()
        conn = MagicMock()
        conn.execute.return_value.fetchone.return_value = ({'id': 'a', 'traffic_origin': 'qa'},)
        with patch.object(store, 'connect') as connect:
            connect.return_value.__enter__.return_value = conn
            with self.assertRaisesRegex(ValueError, 'origin'):
                store.save_feedback('a', 1, traffic_origin='user')
            self.assertEqual(conn.execute.call_count, 1)
            store.save_feedback('a', 1, traffic_origin='qa')
            self.assertTrue(conn.execute.call_args.args[0].startswith('INSERT INTO feedback'))


class EncoderPreparationTests(unittest.TestCase):
    def test_browser_app_contract_shows_setup_action_without_provider_details(self):
        from streamlit.testing.v1 import AppTest
        from navigator.corpus import ingest
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'NAVIGATOR_RUNTIME': temp, 'TELEMETRY_BACKEND': 'jsonl'}):
            ingest()
            app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
            app.text_area[0].set_value('Which passages describe limitations?')
            with patch.object(Retriever, 'load_vectors', side_effect=EncoderUnavailableError('SECRET_FIXTURE')):
                app.button[0].click().run()
            self.assertFalse(app.exception)
            self.assertTrue(any('prepare-encoder' in error.value for error in app.error))
            self.assertFalse(any('SECRET_FIXTURE' in error.value for error in app.error))
            self.assertFalse(Journal(Path(temp) / 'events.jsonl').read()[0])

    def test_missing_encoder_is_offline_and_actionable(self):
        engine = Retriever([{'id': 'a', 'title': 'fixture', 'section': 'text',
                             'content': 'fixture content'}], load_config())
        with patch('sentence_transformers.SentenceTransformer', side_effect=OSError('fixture')) as model:
            with self.assertRaisesRegex(RuntimeError, 'prepare-encoder'):
                engine.load_vectors()
            self.assertTrue(model.call_args.kwargs['local_files_only'])
            with self.assertRaises(RuntimeError):
                engine.load_vectors(allow_download=True)
            self.assertFalse(model.call_args.kwargs['local_files_only'])

    def test_preparation_failure_writes_blocked_receipt_and_cli_exits_nonzero(self):
        from navigator.__main__ import emit_report
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ, {'NAVIGATOR_RUNTIME': temp}):
            report = prepare_encoder()
            self.assertEqual(report['status'], 'BLOCKED_ENCODER_SETUP')
            self.assertFalse(report['allow_download'])
            self.assertEqual(json.loads((Path(temp) / 'encoder-preparation.json').read_text()), report)
            with patch('builtins.print'), self.assertRaises(SystemExit) as exit_status:
                emit_report(report)
            self.assertEqual(exit_status.exception.code, 1)

    def test_heading_experiment_preserves_original_passage_and_is_bound_to_context(self):
        doc = {'title': 'Study', 'section_heading': 'Limitations', 'content': 'Original evidence.'}
        self.assertEqual(embedding_text(doc, 'title_heading_content'), 'Study\nLimitations\nOriginal evidence.')
        self.assertEqual(doc['content'], 'Original evidence.')
        baseline = load_config()
        candidate = {**baseline, 'lexical_fields': ['title', 'section_heading', 'content']}
        self.assertNotEqual(retrieval_policy(baseline), retrieval_policy(candidate))


if __name__ == '__main__':
    unittest.main()
