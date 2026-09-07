"""Extractive source-selection safety and usefulness contracts; synthetic only."""
import copy
import json
import unittest

from navigator.common import digest, load_config
from navigator.rag import generate, run_request, decode_model_answer
from navigator.experiments import verify_candidate_record
from navigator.exports import claim_rows, tag_proposal_rows
from navigator.evaluation import summarize_answer_review
from config_fixtures import mock_config
import test_core_completion as fixtures
import test_local_quality as local


class SourceExtractTests(unittest.TestCase):
    def setUp(self):
        self.hits = [{**fixtures.HIT, 'content': 'The fictional value is 3.5, not 4.0. PHOX2B is an illustrative token.',
                      'start_in_passage': 80, 'source_version': 'synthetic-version'},
                     {**fixtures.HIT, 'id': 'fixture:2', 'source_id': 'fixture-two',
                      'content': 'A fictional limitation applies.', 'start_in_passage': 120,
                      'source_version': 'second-synthetic-version'}]
        self.cfg = mock_config(prompt='source_extract_complete', model_digest='fixture-digest',
                               generation_json_schema=True)

    def payload(self):
        return {'status': 'answered', 'claims': [{'span': 2}], 'limitations': [{'span': 3}]}

    def record(self):
        return generate('Synthetic question', self.hits, self.cfg, 'fixture-corpus', use_llm=True,
                        client=local.local_client(self.payload()))

    def test_shipped_config_drives_source_excerpt_transport_and_export(self):
        cfg = load_config()
        rec = generate('Synthetic question', self.hits, cfg, 'fixture-corpus', use_llm=True,
                       client=local.local_client(self.payload()))
        self.assertEqual(rec['status'], 'answered')
        self.assertEqual(rec['config'], cfg)
        self.assertEqual(rec['config']['model'], 'gemma3:12b')
        self.assertEqual(rec['config']['prompt'], 'source_extract_complete')
        self.assertEqual(rec['config']['retrieval'], 'hybrid')
        self.assertEqual(rec['config']['top_k'], 10)
        message = json.loads(rec['calls'][0]['messages'][-1]['content'])
        self.assertEqual([[span['span'] for span in passage['spans']]
                          for passage in message['passages']], [[1, 2], [3]])
        self.assertEqual(rec['calls'][0]['response_format']['type'], 'json_schema')
        exported = claim_rows(rec)
        self.assertEqual(exported[0]['exact_quote'], 'PHOX2B is an illustrative token.')
        self.assertEqual(exported[0]['scientific_review'], 'PENDING_HUMAN_REVIEW')

    def test_shipped_generation_binding_remains_below_full_quality_approval(self):
        cfg = load_config()
        self.assertEqual(cfg['generation_selection_status'],
                         'BEST_OF_EVALUATED_ALTERNATIVES_INTERNAL_BAR_NOT_MET')
        self.assertNotEqual(cfg['generation_selection_status'], 'QUALITY_SELECTED')

    def test_global_ids_and_messages_retain_every_source_character(self):
        for prompt in ('source_extract_concise', 'source_extract_complete', 'source_extract_checked'):
            cfg = {**self.cfg, 'prompt': prompt}
            rec = generate('Synthetic question', self.hits, cfg, 'fixture-corpus', use_llm=True,
                           client=local.local_client(self.payload()))
            message = json.loads(rec['calls'][0]['messages'][-1]['content'])
            self.assertEqual(message['question'], 'Synthetic question')
            self.assertEqual([[s['span'] for s in p['spans']] for p in message['passages']], [[1, 2], [3]])
            for p, hit in zip(message['passages'], self.hits):
                self.assertEqual(''.join(s['text'] for s in p['spans']), hit['content'])
                self.assertNotIn('passage', p)
                self.assertNotIn('evidence_id', p)
            self.assertNotIn('required_facts', rec['calls'][0]['messages'][-1]['content'])

    def test_application_copies_text_identity_and_exact_offsets(self):
        rec = self.record(); claim = rec['claims'][0]
        self.assertEqual(claim['text'], 'PHOX2B is an illustrative token.')
        self.assertEqual(claim['text'], claim['exact_quote'])
        self.assertEqual(claim['evidence_id'], 'fixture:1')
        receipt = rec['citation_resolutions'][0]
        self.assertEqual(receipt['claim_text_origin'], 'application_source_verbatim')
        self.assertEqual(receipt['start_in_passage'], 80 + self.hits[0]['content'].index('PHOX2B'))
        self.assertNotIn('raw_quote', receipt)
        self.assertEqual(rec['answer_style'], 'verbatim_source_selection')

    def test_model_cannot_supply_paraphrase_metadata_or_raw_quote(self):
        for key in ('text', 'quote', 'evidence_id', 'source_version', 'answer_style'):
            raw = self.payload(); raw['claims'][0][key] = 'model-controlled'
            with self.subTest(key=key), self.assertRaises(ValueError):
                decode_model_answer(json.dumps(raw), self.hits, self.cfg)

    def test_foreign_noninteger_and_nonpositive_span_ids_fail(self):
        for value in (0, -1, 4, True, 1.0, '2', None):
            raw = self.payload(); raw['claims'][0]['span'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                decode_model_answer(json.dumps(raw), self.hits, self.cfg)

    def test_empty_answer_and_refusal_with_payload_are_rejected(self):
        for raw in ({'status':'answered','claims':[],'limitations':[]},
                    {'status':'insufficient_evidence','claims':[],'limitations':[{'span':3}]}):
            with self.assertRaises(ValueError): decode_model_answer(json.dumps(raw), self.hits, self.cfg)

    def test_export_labels_style_and_preserves_source_qualification(self):
        rec = self.record(); row = claim_rows(rec)[0]
        self.assertEqual(row['answer_style'], 'verbatim_source_selection')
        self.assertIn('fictional limitation', row['answer_limitations'])
        self.assertEqual(row['scientific_review'], 'PENDING_HUMAN_REVIEW')
        proposal = tag_proposal_rows(rec)[0]
        self.assertEqual(proposal['registry_action'], 'NONE')
        self.assertEqual(proposal['proposed_term'], 'PHOX2B')
        self.assertEqual(set(rec['calls'][0]['response_format']['json_schema']['schema']['properties']['claims']['items']['properties']), {'span'})

    def test_export_rejects_tampered_prose_or_answer_style(self):
        for mutation in ('alter_text', 'remove_style', 'rename_style'):
            rec=self.record()
            if mutation=='alter_text':rec['claims'][0]['text']='The fictional value was 99.'
            elif mutation=='remove_style':rec.pop('answer_style')
            else:rec['answer_style']='generated_paraphrase'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):claim_rows(rec)

    def test_replay_rejects_changed_receipts_even_when_quote_is_real(self):
        engine=fixtures.Engine();engine.search=lambda *a,**kw:self.hits;engine.corpus_id=digest(self.hits)
        q={'question':'Synthetic question'}
        rec=run_request(q['question'],engine,self.cfg,client=local.local_client(self.payload()),traffic_origin='evaluation')
        rec['runtime_code_id']='fixture-code'
        rec['calls'][0].update(runtime_code_id='fixture-code',execution_kind='live_provider_client')
        row={'record':rec,'prompt':self.cfg['prompt']}
        verify_candidate_record(row,q,self.cfg,self.hits,'fixture-code')
        changed=copy.deepcopy(row);changed['record']['citation_resolutions'][0]['global_span']=1
        with self.assertRaises(ValueError): verify_candidate_record(changed,q,self.cfg,self.hits,'fixture-code')

    def test_true_excerpt_does_not_pass_when_required_answer_is_missing(self):
        results,reviews=local.CompletenessTests().fixture()
        prompts = ['source_extract_concise', 'source_extract_complete']
        results['prompts'] = prompts
        for i,(entry,review) in enumerate(zip(results['per_question'],reviews['reviews'])):
            rec=entry['record'];rec['answer_style']='verbatim_source_selection'
            entry['prompt'] = prompts[i % len(prompts)]
            rec['config']['prompt'] = entry['prompt']
            rec['config_id'] = digest(rec['config'])
            rec['claims'][0]['text']=rec['claims'][0]['exact_quote']
            entry['record_hash']=digest(rec);review['record_hash']=digest(rec)
            review['fact_coverage']=['missing']
        reviews['results_hash']=digest(results)
        summary=summarize_answer_review(results,reviews)
        self.assertEqual(summary['eligible_best_prompts'],[])
        self.assertTrue(all(a['acceptable_answers']==0 for a in summary['aggregates']))

    def test_selection_note_stays_diagnostic_and_cannot_supply_answer_text(self):
        cfg = {**self.cfg, 'prompt': 'source_extract_reasoned'}
        payload = {**self.payload(), 'selection_note': 'Synthetic model diagnostic, not evidence.'}
        rec = generate('Synthetic question', self.hits, cfg, 'fixture-corpus', use_llm=True,
                       client=local.local_client(payload))
        self.assertEqual(rec['status'], 'answered')
        self.assertEqual(rec['claims'][0]['text'], rec['claims'][0]['exact_quote'])
        self.assertNotIn('selection_note', rec)
        self.assertNotIn('Synthetic model diagnostic', json.dumps(claim_rows(rec)))
        self.assertIn('Synthetic model diagnostic', rec['raw_output'])
        schema = rec['calls'][0]['response_format']['json_schema']['schema']
        self.assertEqual(next(iter(schema['properties'])), 'selection_note')
        self.assertEqual(schema['properties']['selection_note']['maxLength'], 600)

    def test_missing_or_unbounded_selection_note_is_not_silently_accepted(self):
        cfg = {**self.cfg, 'prompt': 'source_extract_reasoned'}
        for note in (None, '', '   ', 7, 'x' * 601):
            with self.subTest(note_type=type(note).__name__), self.assertRaises(ValueError):
                decode_model_answer(json.dumps({**self.payload(), 'selection_note': note}), self.hits, cfg)
        with self.assertRaises(ValueError):
            decode_model_answer(json.dumps(self.payload()), self.hits, cfg)
        with self.assertRaises(ValueError):
            decode_model_answer(json.dumps({**self.payload(), 'selection_note': 'Unexpected'}), self.hits, self.cfg)


if __name__=='__main__': unittest.main()
