"""Regressions from the examiner review; fixtures never count as live LLM quality."""
import copy
import csv
import io
import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from navigator.common import ROOT, digest
from navigator.corpus import prepare, ingest
from navigator.exports import claim_rows, csv_export, passage_rows
from navigator.monitoring import observed_tables
from navigator.rag import generate, validate_answer
from navigator.storage import Journal, feedback_record
from navigator.evaluation import answer_plan, summarize_answer_review
from config_fixtures import mock_config


def evidence():
    hit = dict(prepare()[0][0], rank=1)
    cfg = mock_config(provider="openai", model="gpt-5.4-mini", json_mode=False)
    payload = {"status": "answered", "claims": [{"text": "Synthetic regression claim", "evidence_id": hit["id"], "exact_quote": hit["content"][:30]}], "limitations": "Mock output; not biomedical evidence."}
    return hit, cfg, payload


def fake_response(payload):
    return SimpleNamespace(responses=SimpleNamespace(create=lambda **kw: SimpleNamespace(output_text=json.dumps(payload), usage=SimpleNamespace(input_tokens=17, output_tokens=9))))


class OutputOwnershipTests(unittest.TestCase):
    def test_model_cannot_overwrite_any_application_field(self):
        hit, cfg, valid = evidence()
        for key, value in {"id":"forged", "config_id":"forged", "corpus_id":"forged", "mode":"evidence_preview", "hits":[], "retrieved_ids":[], "input_tokens":0, "cost_usd":0, "traffic_origin":"user", "question":"forged"}.items():
            with self.subTest(key=key), patch.dict(os.environ, {"ENABLE_PAID_LLM":"1"}):
                rec=generate("regression",[hit],cfg,"fixture",paid=True,client=fake_response({**valid,key:value}),traffic_origin="qa")
                self.assertEqual(rec["status"],"error")
                self.assertNotEqual(rec["id"],"forged")
                self.assertEqual(rec["config_id"],digest(cfg))
                self.assertEqual(rec["mode"],"llm")
                self.assertEqual(rec["hits"],[hit])
                self.assertEqual(rec["retrieved_ids"],[hit["id"]])
                self.assertEqual(rec["input_tokens"],17)
                self.assertEqual(rec["traffic_origin"],"qa")
                self.assertFalse(rec["claims"])

    def test_nested_foreign_fields_and_non_string_id_rejected(self):
        hit,cfg,payload=evidence()
        for edit in [{"unexpected":1},{"evidence_id":[]},{"evidence_id":{}}]:
            bad=copy.deepcopy(payload);bad["claims"][0].update(edit)
            with self.assertRaises(ValueError):validate_answer(bad,[hit])

    def test_record_owns_configuration_and_sources(self):
        hit,cfg,payload=evidence();rec=generate("fixture",[hit],cfg,"corpus")
        cfg["prompt"]="changed";hit["content"]="changed"
        self.assertNotEqual(rec["config"]["prompt"],cfg["prompt"])
        self.assertNotEqual(rec["hits"][0]["content"],hit["content"])

    def test_context_includes_scientific_provenance(self):
        from navigator.rag import build_context
        hit,cfg,payload=evidence();row=json.loads(build_context([hit]))[0]
        for k in ["year","population_or_model","source_version","source_url"]:self.assertEqual(row[k],hit[k])


class ExportTests(unittest.TestCase):
    def test_claim_csv_round_trip_retains_quote_source_and_identity(self):
        hit,cfg,payload=evidence()
        with patch.dict(os.environ,{"ENABLE_PAID_LLM":"1"}):
            rec=generate('Question, with "quotes"\nand newline',[hit],cfg,"corpus",paid=True,client=fake_response(payload))
        rows=list(csv.DictReader(io.StringIO(csv_export(claim_rows(rec)))))
        self.assertEqual(len(rows),1)
        row=rows[0]
        for key in ["answer_id","config_id","corpus_id","source_url","source_version","start_in_passage","end_in_passage","exact_quote","claim_text"]:self.assertTrue(row[key])
        self.assertEqual(row["answer_id"],rec["id"])
        self.assertEqual(row["exact_quote"],payload["claims"][0]["exact_quote"])
        self.assertEqual(row["question"],rec["question"])

    def test_csv_formula_defense_and_preview_has_no_claims(self):
        hit,cfg,payload=evidence();rec=generate('=SUM(1,2)',[hit],cfg,'corpus')
        self.assertEqual(claim_rows(rec),[])
        row=next(csv.DictReader(io.StringIO(csv_export(passage_rows(rec)))))
        self.assertTrue(row['question'].startswith("'="))
        self.assertEqual(rec['question'],'=SUM(1,2)')

    def test_export_rejects_legacy_tampered_record(self):
        hit,cfg,payload=evidence();rec=generate('q',[hit],cfg,'corpus');rec.update(payload);rec['hits']=[]
        with self.assertRaises(ValueError):claim_rows(rec)


class MonitoringTests(unittest.TestCase):
    def test_origin_mode_denominators_and_legacy_are_separate(self):
        hit,cfg,payload=evidence()
        user=generate('q',[hit],cfg,'c',traffic_origin='user')
        qa=generate('q',[hit],cfg,'c',traffic_origin='qa')
        legacy=generate('q',[],cfg,'c');del legacy['traffic_origin']
        feedback=[feedback_record(user['id'],1,'','u','user'),feedback_record(qa['id'],-1,'','q','qa')]
        data=observed_tables([user,qa,legacy],feedback,'user','evidence_preview')
        self.assertEqual((data['requests'],data['rated_requests']),(1,1))
        self.assertEqual(data['feedback'].to_dict(),{'Helpful':1})
        self.assertEqual(data['passage_counts'].iloc[0,0],1)
        self.assertIsNone(data['tokens'])
        self.assertEqual(observed_tables([user,qa,legacy],feedback,'qa')['feedback'].to_dict(),{'Not helpful':1})
        self.assertEqual(observed_tables([user,qa,legacy],feedback,'legacy_unknown')['requests'],1)
        self.assertIsNone(observed_tables([user,qa,legacy],feedback,'user','llm'))

    def test_mismatched_feedback_origin_not_counted(self):
        hit,cfg,payload=evidence();user=generate('q',[hit],cfg,'c')
        f=feedback_record(user['id'],1,'','f','qa')
        self.assertEqual(observed_tables([user],[f],'user')['rated_requests'],0)

    def test_monitor_read_outage_is_handled_and_recovers(self):
        from streamlit.testing.v1 import AppTest
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ,{'NAVIGATOR_RUNTIME':temp,'ENABLE_PAID_LLM':'0','TELEMETRY_BACKEND':'jsonl'}):
            ingest()
            with patch.object(Journal,'read',side_effect=ConnectionError('fixture-secret-detail')):
                app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
                self.assertFalse(app.exception)
                self.assertTrue(any('Monitoring is temporarily unavailable' in w.value for w in app.warning))
                self.assertFalse(any('fixture-secret-detail' in w.value for w in app.warning))
                self.assertTrue(app.text_area)
            app.run();self.assertFalse(app.exception)
            self.assertTrue(any('No recorded activity' in v.value for v in app.info))



class ReviewWorkflowTests(unittest.TestCase):
    def test_plan_covers_unanswerable_questions_without_calls(self):
        with patch('navigator.evaluation.read_documents',return_value=prepare()[0]):
            plan=answer_plan('tuning',4)
            self.assertEqual({q['answerable'] for q in plan['questions']},{True,False})
            self.assertEqual(plan['maximum_provider_requests'],8)
            self.assertEqual(plan['status'],'PLANNED_NOT_EXECUTED')
            self.assertEqual(len(answer_plan()['questions']),42)
            with self.assertRaises(ValueError):answer_plan('tuning',1)

    def fixture(self):
        hit,cfg,payload=evidence()
        rows=[];reviews=[]
        for prompt in ['concise','evidence_first']:
            cfg=copy.deepcopy(cfg);cfg['prompt']=prompt
            with patch.dict(os.environ,{'ENABLE_PAID_LLM':'1'}):
                rec=generate('q',[hit],cfg,'corpus',paid=True,client=fake_response(payload),traffic_origin='evaluation')
            rows.append({'question_id':'fixture','answerable':True,'prompt':prompt,'record':rec,'record_hash':digest(rec)})
            reviews.append({'answer_id':rec['id'],'record_hash':digest(rec),'relevance':'relevant','claim_support':['supported'],'abstention_correct':False,'fact_coverage':['covered'],'qualification_coverage':[],'reason':'Synthetic test judgment, not real source support.'})
        results={'status':'EXECUTED_AWAITING_REVIEW','questions':[{'id':'fixture','required_facts':[{'text':'Synthetic fact'}],'required_qualifications':[]}],'prompts':['concise','evidence_first'],'per_question':rows}
        review={'reviewer':'fixture','reviewer_kind':'assistant','results_hash':digest(results),'reviews':reviews}
        return results,review

    def test_complete_reviews_report_ties_without_promoting_config(self):
        results,review=self.fixture();summary=summarize_answer_review(results,review)
        self.assertEqual(summary['status'],'REVIEWED_COMPLETE')
        self.assertEqual(summary['eligible_best_prompts'],['concise','evidence_first'])
        self.assertEqual(summary['reviewer_kind'],'assistant')

    def test_missing_judgments_or_changed_answer_cannot_pass(self):
        for mutation in ['pending','duplicate','hash','claim']:
            results,review=self.fixture()
            if mutation=='pending':review['reviews'][0]['relevance']=None
            elif mutation=='duplicate':review['reviews'][1]=review['reviews'][0]
            elif mutation=='hash':results['per_question'][0]['record']['question']='changed'
            else:review['reviews'][0]['claim_support']=[]
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):summarize_answer_review(results,review)

    def test_incomplete_run_never_proposes_winner(self):
        results,review=self.fixture();results['status']='STOPPED_ON_ERROR';review['results_hash']=digest(results)
        summary=summarize_answer_review(results,review)
        self.assertEqual(summary['eligible_best_prompts'],[])

    def test_different_contexts_cannot_be_a_paired_comparison(self):
        results,review=self.fixture()
        results['per_question'][1]['record']['question']='different question'
        review['results_hash']=digest(results)
        with self.assertRaises(ValueError):summarize_answer_review(results,review)
