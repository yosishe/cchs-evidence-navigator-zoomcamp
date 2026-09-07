"""Fault-oriented fixtures, never evidence of a live model's answer quality."""
import copy,json,os,tempfile,unittest
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path
from navigator.common import load_config,digest
from navigator.corpus import prepare
from navigator.rag import generate
from navigator.providers import local_endpoint,complete
from navigator.rewriting import rewrite_query
from navigator.exports import tag_proposal_rows,comparison_rows
from navigator.evaluation import summarize_answer_review
import test_review_regressions
from config_fixtures import mock_config

def local_client(payload,fail=None):
    def call(**kwargs):
        if fail: raise fail
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)),finish_reason='stop')],usage=SimpleNamespace(prompt_tokens=15,completion_tokens=12))
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=call)))

class LocalBoundaryTests(unittest.TestCase):
    def test_changed_installed_model_digest_is_rejected(self):
        from navigator.providers import model_identity
        from unittest.mock import MagicMock
        session = MagicMock()
        with patch('requests.Session', return_value=session), patch.dict(os.environ, {'OLLAMA_BASE_URL': 'http://localhost:11434/v1'}):
            for requested, installed in [('phi3', 'phi3:latest'),
                    ('phi3:3.8b-mini-128k-instruct-q8_0', 'phi3:3.8b-mini-128k-instruct-q8_0')]:
                with self.subTest(model=requested):
                    session.get.return_value.json.return_value = {'models': [
                        {'name': installed, 'digest': 'new-weights', 'size': 100}]}
                    with self.assertRaises(ValueError):
                        model_identity({'provider': 'ollama', 'model': requested, 'model_digest': 'selected-weights'})
                    self.assertEqual(model_identity({'provider': 'ollama', 'model': requested})['digest'], 'new-weights')
                    session.get.return_value.json.return_value = {'models': [
                        {'name': 'gemma:2b', 'digest': 'new-weights', 'size': 100}]}
                    with self.assertRaises(RuntimeError):
                        model_identity({'provider': 'ollama', 'model': requested})

    def fixture(self):
        cfg=mock_config()
        hit=next(d for d in prepare()[0] if 'PHOX2B' in d['content'])
        payload={'status':'answered','claims':[{'text':'Fixture claim, not a validated biomedical statement','evidence_id':hit['id'],'exact_quote':'PHOX2B'}],'limitations':'Synthetic fixture'}
        return cfg,hit,payload
    def test_local_answer_is_generated_without_paid_flag_or_key(self):
        cfg,h,p=self.fixture()
        with patch.dict(os.environ,{'ENABLE_PAID_LLM':'0','OPENAI_API_KEY':''}):
            r=generate('q',[h],cfg,'fixture',use_llm=True,client=local_client(p))
        self.assertEqual(r['status'],'answered');self.assertEqual(len(r['calls']),1)
        self.assertEqual(r['cost_usd'],0);self.assertEqual(r['input_tokens'],15)
        self.assertEqual(r['scientific_review'],'PENDING_HUMAN_REVIEW')
    def test_local_endpoint_cannot_redirect_configuration_to_external_provider(self):
        for url in ['https://api.openai.com/v1','http://localhost.evil/v1','http://user:pass@localhost:11434/v1','http://localhost:11434/v1?x=1']:
            with self.subTest(url=url),patch.dict(os.environ,{'OLLAMA_BASE_URL':url}),self.assertRaises(ValueError):local_endpoint({})
    def test_missing_provider_and_untaught_model_cannot_fallback(self):
        cfg,h,p=self.fixture()
        # The owner explicitly approved gemma3:12b; the family remains restricted.
        for update in [{'provider':'external'},{'model':'gemma3:27b'}]:
            r=generate('q',[h],{**cfg,**update},'fixture',use_llm=True,client=local_client(p))
            self.assertEqual(r['status'],'error');self.assertEqual(r['calls'],[])
    def test_failed_actual_call_is_counted_once_and_secret_not_persisted(self):
        cfg,h,p=self.fixture()
        r=generate('q',[h],cfg,'fixture',use_llm=True,client=local_client(p,TimeoutError('SECRET')))
        self.assertEqual(len(r['calls']),1);self.assertEqual(r['calls'][0]['status'],'error')
        self.assertNotIn('SECRET',json.dumps(r))
    def test_invalid_json_retains_actual_usage_but_not_claims(self):
        cfg,h,p=self.fixture();r=generate('q',[h],cfg,'fixture',use_llm=True,client=local_client({'bad':'shape'}))
        self.assertEqual(r['status'],'error');self.assertEqual(r['input_tokens'],15);self.assertFalse(r['claims'])
    def test_rewrite_preserves_identifiers_negation_and_falls_back_on_bad_output(self):
        cfg,h,p=self.fixture();q='What was not observed with PHOX2B c.780dupT in 2021?'
        for rewritten in ['What was observed with PHOX2B c.780dupT in 2021?',
                          'What was not observed with PHOX2A in 2021?',
                          'What was not observed with PHOX2B p.780dupT in 2021?']:
            r=rewrite_query(q,cfg,enabled=True,client=local_client({'query':rewritten}))
            self.assertEqual(r['query'],q);self.assertEqual(r['status'],'fallback_original');self.assertEqual(len(r['calls']),1)
        r=rewrite_query(q,cfg,enabled=True,client=local_client({'query':q}))
        self.assertEqual(r['status'],'rewritten')
    def test_proposals_use_only_quote_terms_and_keep_uncertainty(self):
        cfg,h,p=self.fixture();r=generate('q',[h],cfg,'fixture',use_llm=True,client=local_client(p))
        proposals=tag_proposal_rows(r)
        self.assertEqual([x['proposed_term'] for x in proposals],['PHOX2B'])
        self.assertEqual(proposals[0]['registry_action'],'NONE')
        self.assertIn('PENDING',proposals[0]['review_status'])
        self.assertEqual(comparison_rows(r)[0]['answer_limitations'],'Synthetic fixture')

class CompletenessTests(unittest.TestCase):
    def fixture(self):return test_review_regressions.ReviewWorkflowTests().fixture()
    def test_supported_but_incomplete_answer_is_not_acceptable(self):
        results,reviews=self.fixture();reviews['reviews'][0]['fact_coverage']=['missing']
        summary=summarize_answer_review(results,reviews)
        self.assertEqual(summary['aggregates'][0]['acceptable_answers'],0)
        self.assertEqual(summary['eligible_best_prompts'],['evidence_first'])
    def test_omitted_qualification_is_not_acceptable(self):
        results,reviews=self.fixture();results['questions'][0]['required_qualifications']=[{'text':'Fixture caveat'}]
        reviews['results_hash']=digest(results)
        for row in reviews['reviews']:row['qualification_coverage']=['missing']
        self.assertEqual(summarize_answer_review(results,reviews)['eligible_best_prompts'],[])
    def test_zero_acceptable_responses_do_not_nominate_a_winner(self):
        results,reviews=self.fixture()
        for row in reviews['reviews']:row['claim_support']=['unsupported']
        self.assertEqual(summarize_answer_review(results,reviews)['eligible_best_prompts'],[])
    def test_legacy_without_completeness_cannot_be_promoted(self):
        results,reviews=self.fixture();del results['questions'][0]['required_facts'];reviews['results_hash']=digest(results)
        self.assertFalse(summarize_answer_review(results,reviews)['completeness_available'])
        self.assertEqual(summarize_answer_review(results,reviews)['eligible_best_prompts'],[])
    def test_test_split_cannot_select_prompt(self):
        results,reviews=self.fixture();results['split']='test';reviews['results_hash']=digest(results)
        self.assertEqual(summarize_answer_review(results,reviews)['eligible_best_prompts'],[])

class HeadingAndBankTests(unittest.TestCase):
    def test_headings_are_metadata_not_evidence_windows(self):
        docs,excluded,_=prepare()
        self.assertFalse(any(d['source_id']=='PMC8039127' and d['passage_index'] in {53,71} for d in docs))
        paragraph=next(d for d in docs if d['source_id']=='PMC8039127' and d['passage_index']==68)
        self.assertEqual(paragraph['section_heading'],'Discussion')
        self.assertTrue(any(e['reason']=='heading_retained_as_metadata_only' for e in excluded))
    def test_bank_has_six_slices_and_disjoint_source_passages(self):
        from navigator.evaluation import load_question_bank
        from collections import Counter
        docs=prepare()[0];bank=load_question_bank(load_config(),docs)
        self.assertEqual(len(bank['questions']),60)
        self.assertEqual(Counter(q['split'] for q in bank['questions']),{'tuning':42,'test':18})
        self.assertEqual(set(Counter(q['slice'] for q in bank['questions']).values()),{10})
        groups={}
        for q in bank['questions']:
            for r in q['reference_quotes']:
                key=(r['source_id'],r['passage_index'])
                self.assertEqual(groups.setdefault(key,q['split']),q['split'])
    def test_corpus_changed_after_bank_freeze_is_rejected(self):
        from navigator.evaluation import load_question_bank
        docs=prepare()[0];docs[0]['content']+=' changed'
        with self.assertRaises(ValueError):load_question_bank(load_config(),docs)

class ExperimentFailureTests(unittest.TestCase):
    def test_missing_models_leave_durable_preflight_without_generation(self):
        from navigator.experiments import generation_matrix
        with tempfile.TemporaryDirectory() as tmp, patch('navigator.experiments.ROOT',Path(tmp)), patch('navigator.experiments.model_identity',side_effect=RuntimeError('missing')), patch('navigator.experiments.answer_evaluation') as run:
            report=generation_matrix(max_questions=2)
            self.assertEqual(report['status'],'BLOCKED_MODEL_PREFLIGHT')
            self.assertEqual(report['actual_generation_requests'],0)
            self.assertTrue((Path(tmp)/report['run_directory']/'matrix.json').exists())
            run.assert_not_called()
    def test_failed_retrieval_checkpoints_an_interrupted_run(self):
        from navigator.evaluation import answer_evaluation
        cfg=mock_config()
        docs=prepare()[0]
        with tempfile.TemporaryDirectory() as tmp, patch('navigator.evaluation.ROOT',Path(tmp)), patch('navigator.evaluation.read_documents',return_value=docs), patch('navigator.evaluation.answer_plan') as plan, patch('navigator.evaluation.Retriever') as retriever:
            plan.return_value={'config':cfg,'corpus_id':digest(docs),'questions':[{'id':'x','question':'q','required_facts':[],'required_qualifications':[]}],'prompts':['concise'],'split':'tuning'}
            retriever.return_value.search.side_effect=RuntimeError('failed')
            report=answer_evaluation(client=local_client({}),config=cfg)
            self.assertEqual(report['status'],'STOPPED_ON_RETRIEVAL_ERROR')
            self.assertEqual(report['actual_provider_requests'],0)
            self.assertTrue((Path(tmp)/report['run_directory']/'results.json').exists())
