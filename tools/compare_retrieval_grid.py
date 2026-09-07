"""Tuning-only RRF grid from 2026 Homework 4; never reads final-test questions.

Grid declared before execution: candidate pools 10/20/40 and RRF 1/10/50/100.
Objective: Hit@5, then MRR@5. Preserve the incumbent on ties; otherwise prefer
smaller candidate pools. This is provisional engineering tuning, not new gold.
"""
import copy
import itertools
import sys
import uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT,digest,load_config,read_documents,read_json,utc_now,write_json
from navigator.evaluation import metrics,load_question_bank
from navigator.retrieval import Retriever

cfg=load_config();docs=read_documents();bank=load_question_bank(cfg,docs)
questions=[q for q in bank['questions'] if q['split']=='tuning']
engine=Retriever(docs,cfg);engine.load_vectors()
results=[]
for candidate_k,rrf_k in itertools.product([10,20,40],[1,10,50,100]):
    variant=copy.deepcopy(cfg);variant.update(retrieval='hybrid',candidate_k=candidate_k,rrf_k=rrf_k)
    engine.config=variant;rows=[]
    for q in questions:
        hits=engine.search(q['question']);m=metrics([h['id'] for h in hits],q['relevant_ids']) if q['answerable'] else None
        rows.append({'question_id':q['id'],'ranked_ids':[h['id'] for h in hits],'metrics':m})
    scored=[r['metrics'] for r in rows if r['metrics'] is not None]
    results.append({'candidate_k':candidate_k,'rrf_k':rrf_k,'config':variant,'config_id':digest(variant),
                    'hit_at_5':sum(r['hit'] for r in scored)/len(scored),
                    'mrr_at_5':sum(r['reciprocal_rank'] for r in scored)/len(scored),
                    'denominator':len(scored),'per_question':rows})
quality=lambda r:(r['hit_at_5'],r['mrr_at_5'])
best_quality=max(map(quality,results));ties=[r for r in results if quality(r)==best_quality]
incumbent=next(r for r in results if (r['candidate_k'],r['rrf_k'])==(cfg['candidate_k'],cfg['rrf_k']))
winner=incumbent if incumbent in ties else min(ties,key=lambda r:(r['candidate_k'],r['rrf_k']))
report={'status':'EXECUTED_TUNING_ONLY_PROVISIONAL_LABELS','created_at':utc_now(),'corpus_id':digest(docs),
        'tuning_questions_hash':digest(questions),'input_config':cfg,'input_config_id':digest(cfg),
        'grid':{'candidate_k':[10,20,40],'rrf_k':[1,10,50,100]},'objective':__doc__,
        'selected_candidate':{k:winner[k] for k in ['candidate_k','rrf_k','hit_at_5','mrr_at_5','config_id']},
        'incumbent':{k:incumbent[k] for k in ['candidate_k','rrf_k','hit_at_5','mrr_at_5','config_id']},
        'results':results,'promoted':False,
        'limitations':'Active-bank tuning questions only, assistant-authored provisional labels. Neither independent validation nor a held-out test. Incumbent means current RRF parameters within hybrid, not a claim that hybrid is the deployed method. No automatic configuration promotion.'}
output=ROOT/'reports/experiments'/('retrieval-rrf-grid-'+str(uuid.uuid4())+'.json')
write_json(output,report)
print(output)
print(report['selected_candidate']);print('Incumbent:',report['incumbent'])
