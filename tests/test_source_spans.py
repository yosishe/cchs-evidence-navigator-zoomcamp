"""Synthetic source-pointer challenges, separate from biomedical quality totals."""
import copy
import json
import unittest
from navigator.citation_transport import source_spans, decode_source_spans
from navigator.rag import generate, decode_model_answer
from navigator.exports import claim_rows
from config_fixtures import mock_config
import test_core_completion as fixtures
import test_local_quality as local


class SourceSpanTests(unittest.TestCase):
    def setUp(self):
        self.hit = {**fixtures.HIT, 'content': 'The fictional value was 3.5, not 4.0. Second finding!\nPHOX2B is an illustrative token.',
                    'start_in_passage': 80, 'source_version': 'synthetic-version'}
        self.cfg = mock_config(prompt='source_spans_complete', model_digest='fixture-digest',
                               generation_json_schema=True)

    def payload(self):
        return {'status': 'answered', 'claims': [{'text': 'The fictional value was 3.5, not 4.0.',
                'passage': 1, 'from_span': 1, 'to_span': 1}], 'limitations': []}

    def test_partition_preserves_every_original_character_and_decimal(self):
        spans = source_spans(self.hit['content'])
        self.assertEqual(''.join(s['text'] for s in spans), self.hit['content'])
        self.assertEqual(len(spans), 3)
        self.assertIn('3.5, not 4.0.', spans[0]['text'])
        for s in spans:
            self.assertEqual(self.hit['content'][s['start']:s['end']], s['text'])

    def test_pointer_recovers_original_contiguous_span_with_owned_offsets(self):
        value, receipts = decode_source_spans(self.payload(), [self.hit])
        quote = value['claims'][0]['exact_quote']
        self.assertEqual(quote, 'The fictional value was 3.5, not 4.0. ')
        self.assertEqual(value['claims'][0]['evidence_id'], self.hit['id'])
        self.assertEqual(receipts[0]['start_in_passage'], 80)
        self.assertEqual(receipts[0]['quote_origin'], 'application_source_span')
        self.assertNotIn('raw_quote', receipts[0])

    def test_duplicate_text_is_selected_by_position_not_fuzzy_matching(self):
        hit = {**self.hit, 'content': 'Same sentence. Same sentence.'}
        raw = self.payload(); raw['claims'][0].update(from_span=2, to_span=2)
        value, receipts = decode_source_spans(raw, [hit])
        self.assertEqual(value['claims'][0]['exact_quote'], 'Same sentence.')
        self.assertEqual(receipts[0]['start_in_chunk'], 15)

    def test_invalid_foreign_or_noninteger_pointers_fail(self):
        for update in [{'passage': 2}, {'passage': True}, {'from_span': '1'},
                       {'to_span': 1.0}, {'from_span': 0}, {'from_span': 2, 'to_span': 1}, {'to_span': 4}]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                raw = self.payload(); raw['claims'][0].update(update)
                decode_source_spans(raw, [self.hit])

    def test_model_metadata_and_freeform_limitations_are_rejected(self):
        for modification in ['source_version', 'quote', 'limitations']:
            raw = self.payload()
            if modification == 'limitations': raw['limitations'] = 'An invented study limitation.'
            else: raw['claims'][0][modification] = 'model-controlled'
            with self.subTest(modification=modification), self.assertRaises(ValueError):
                decode_source_spans(raw, [self.hit])

    def test_source_qualification_and_export_keep_exact_wording(self):
        raw = self.payload(); raw['limitations'] = [{'passage': 1, 'from_span': 2, 'to_span': 2}]
        rec = generate('Synthetic question', [self.hit], self.cfg, 'fixture-corpus',
                       use_llm=True, client=local.local_client(raw))
        self.assertEqual(rec['status'], 'answered')
        self.assertIn('Second finding!', rec['limitations'])
        self.assertEqual(claim_rows(rec)[0]['answer_limitations'], rec['limitations'])
        self.assertEqual(len(rec['citation_resolutions']), 2)
        props = rec['calls'][0]['response_format']['json_schema']['schema']['properties']
        self.assertEqual(props['limitations']['type'], 'array')
        self.assertEqual(set(props['claims']['items']['properties']), {'text', 'passage', 'from_span', 'to_span'})

    def test_abstention_cannot_add_an_invented_premise_or_source_payload(self):
        raw = {'status': 'insufficient_evidence', 'claims': [], 'limitations': []}
        result, receipts = decode_source_spans(raw, [self.hit])
        self.assertEqual(result['limitations'], 'The supplied passages do not establish the information requested.')
        self.assertEqual(receipts, [])
        raw['limitations'] = [{'passage': 1, 'from_span': 1, 'to_span': 1}]
        with self.assertRaises(ValueError): decode_source_spans(raw, [self.hit])

    def test_mechanical_mapping_does_not_assert_semantic_support(self):
        raw = self.payload(); raw['claims'][0]['text'] = 'The fictional value was 99.'
        answer = decode_model_answer(json.dumps(raw), [self.hit], self.cfg)
        self.assertEqual(answer['claims'][0]['text'], 'The fictional value was 99.')
        self.assertIn('not 4.0', answer['claims'][0]['exact_quote'])
        # Source meaning remains an explicit review responsibility. Never repair
        # the claim or upgrade it merely because the quotation is genuine.


if __name__ == '__main__': unittest.main()
