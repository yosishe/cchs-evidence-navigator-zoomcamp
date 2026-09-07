"""Build an agent-review packet for the active bank from matching tuning evidence."""
import sys
import uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT,read_json,read_documents,digest,utc_now,write_json,load_config
from navigator.evaluation import load_question_bank
from navigator.exports import csv_export

cfg=load_config();docs=read_documents();bank=load_question_bank(cfg,docs)
report=read_json(ROOT/'reports/retrieval-tuning.json')
lookup={r['id']:r for r in docs}
if report['corpus_id']!=digest(docs):raise ValueError('Evaluation corpus differs from active source records')
if report['questions_hash']!=digest(bank):raise ValueError('Evaluation question bank differs from active labels')
questions={q['id']:q for q in bank['questions'] if q['split']=='tuning'}
rows=[]
for result in report['per_question']:
    if result['method']!=cfg['retrieval']:continue
    q=questions[result['question_id']]
    ids=list(dict.fromkeys(q['relevant_ids']+result['ranked_ids']))
    for key in ids:
        d=lookup[key]
        rows.append({'question_id':q['id'],'question':q['question'],'answerable':q['answerable'],
                     'label_status':q['label_status'],'evidence_id':key,'reference_label':key in q['relevant_ids'],
                     'retrieved_rank':result['ranked_ids'].index(key)+1 if key in result['ranked_ids'] else None,
                     **{k:d[k] for k in ['source_id','source_version','source_url','title','section','article_type','year','population_or_model','passage_index','start_in_passage','end_in_passage','content']},
                     'reviewed_relevance':'PENDING','reviewer':'','reason':'','missing_other_evidence':''})
packet={'status':'PENDING_AGENT_REVIEW','created_at':utc_now(),'corpus_id':digest(docs),
        'questions_hash':digest(bank),'source_evaluation_hash':digest(report),
        'retrieval_method':cfg['retrieval'],
        'scope':'Tuning questions only; original labels remain unchanged. No new measured quality claim.',
        'rows':rows}
folder=ROOT/'reports/experiments'/('retrieval-review-'+str(uuid.uuid4()))
write_json(folder/'packet.json',packet)
(folder/'packet.csv').write_text(csv_export(rows))
print(folder)
print(f'{len(rows)} evidence rows for {len(questions)} tuning questions; no labels changed')
