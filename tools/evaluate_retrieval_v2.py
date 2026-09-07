"""Tuning-only chunk/retrieval comparison; no provider calls or test-set tuning."""
from pathlib import Path
import sys,time,copy
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from navigator.common import ROOT,digest,load_config,write_json
from navigator.corpus import prepare
from navigator.retrieval import Retriever
from navigator.evaluation import metrics
from build_question_bank_v2 import build

def run():
    base=load_config(); reports=[]
    for size,overlap,template in [(n,o,t) for n,o in [(1000,150),(750,150),(500,100)] for t in ['title_content','content']]:
        cfg={**base,'chunk_chars':size,'overlap_chars':overlap,'embedding_text':template}
        docs,excluded,_=prepare(cfg=cfg); bank=build(cfg)
        questions=[q for q in bank['questions'] if q['split']=='tuning']
        engine=Retriever(docs,cfg)
        for method in ['lexical','vector','hybrid']:
            rows=[];start=time.perf_counter()
            for q in questions:
                trace={};t=time.perf_counter();hits=engine.search(q['question'],method=method,trace=trace)
                score=metrics([h['id'] for h in hits],q['relevant_ids']) if q['answerable'] else None
                refs=q['reference_quotes'];coverage=sum(any(h['id'] in r['acceptable_ids'] for h in hits) for r in refs)/len(refs) if refs else None
                rows.append({'id':q['id'],'slice':q['slice'],'metrics':score,'reference_coverage':coverage,'seconds':time.perf_counter()-t,'trace':trace})
            eligible=[r for r in rows if r['metrics'] is not None]
            from navigator.common import runtime_dir,read_json
            embedding=read_json(runtime_dir()/'embedding-report.json') if method!='lexical' else None
            report={'method':method,'chunk_chars':size,'overlap_chars':overlap,'embedding_text':template,'config':cfg,'corpus_id':digest(docs),'questions_hash':digest(bank),'chunks':len(docs),'excluded_passages':len(excluded),'embedding':embedding,'split':'tuning','answerable_denominator':len(eligible),'hit_at_5':sum(r['metrics']['hit'] for r in eligible)/len(eligible),'mrr_at_5':sum(r['metrics']['reciprocal_rank'] for r in eligible)/len(eligible),'mean_reference_coverage_at_5':sum(r['reference_coverage'] for r in eligible)/len(eligible),'total_seconds_with_setup':time.perf_counter()-start,'per_question':rows}
            reports.append(report)
            print({k:report[k] for k in ['method','embedding_text','chunk_chars','chunks','hit_at_5','mrr_at_5','mean_reference_coverage_at_5']},flush=True)
            write_json(ROOT/'reports/remediation-v2/retrieval-comparison-v2.json',{'status':'RUNNING','results':reports})
    # Reject configurations with silent encoder truncation; maximize full reference coverage
    # before first-hit MRR, because the product compares multi-part evidence.
    eligible=[r for r in reports if r['method']=='lexical' or r['embedding']['truncated_input_count']==0]
    ranked=sorted(eligible,key=lambda r:(-r['mean_reference_coverage_at_5'],-r['hit_at_5'],-r['mrr_at_5'],r['chunks'],['lexical','vector','hybrid'].index(r['method'])))
    winner=ranked[0]
    result={'status':'EXECUTED_PROVISIONAL_LABELS','split':'tuning','results':reports,'recommended':{k:winner[k] for k in ['method','chunk_chars','overlap_chars','embedding_text','corpus_id']},'selection_rule':'No encoder truncation, highest reference coverage, then Hit/MRR, then fewer chunks/simpler retrieval. Project-specific criterion; no human relevance labels.','test_evaluated':False,'runtime_promoted':False}
    write_json(ROOT/'reports/remediation-v2/retrieval-comparison-v2.json',result)
    print(result['recommended'],flush=True)
if __name__=='__main__':run()
