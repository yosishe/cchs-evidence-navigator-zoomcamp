"""Delivery artifact checks; no source-course execution, network or model calls."""
from pathlib import Path
from urllib.parse import unquote
from collections import Counter
import hashlib,json,re,subprocess,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from navigator.common import digest,load_config,runtime_code_id,utc_now,write_json
ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
WORK=ROOT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((HERE/'before.json').read_text())
errors=[]
preserved={p:sha(Path(p))==h for p,h in before['files'].items() if '/data/' in p or '/Downloads/' in p or p.endswith(('configs/app.json','uv.lock'))}
if not all(preserved.values()):errors.append({'preservation':preserved})
checks=json.loads((ROOT/'reports/checks.json').read_text())
assert checks['suite_passed'] and checks['test_count']==98 and checks['skipped_count']==0
ids=re.findall(r'^\w+ \((test_[^)]+)\) \.\.\.',checks['test_output'],re.M)
assert len(ids)==len(set(ids))==98
files=[ROOT/'README.md',*sorted((ROOT/'docs').glob('*.md')),*sorted((ROOT/'reports').rglob('*.md')),WORK/'outputs/course-project-decision-guide.en.md']

def clean(text):
    return re.sub(r'^```[^\n]*\n.*?^```[^\n]*$', '', text, flags=re.M|re.S)

def anchors(text):
    explicit=set(re.findall(r'<a\s+id=[\"\']([^\"\']+)',text))
    counts=Counter()
    for title in re.findall(r'^#{1,6}\s+(.+)$',clean(text),re.M):
        title=re.sub(r'\[([^]]+)\]\([^)]*\)',r'\1',title)
        title=re.sub(r'<[^>]+>','',title).strip().lower()
        slug=re.sub(r'[^\w\- ]','',title).replace(' ','-')
        explicit.add(slug+('-'+str(counts[slug]) if counts[slug] else ''))
        counts[slug]+=1
    return explicit

links=0
for file in files:
    body=clean(file.read_text())
    destinations=re.findall(r'\[[^\]\n]*\]\((<[^>]+>|[^)\n]+)\)',body)
    for target in destinations:
        target=target.strip('<>')
        if re.match(r'^[a-z]+:',target) and not target.startswith('/'):continue
        path,_,anchor=unquote(target).partition('#')
        path=re.sub(r':\d+$','',path)
        dest=(file.parent/path).resolve() if path else file
        links+=1
        if not dest.exists():errors.append({'missing_file':str(file),'target':target})
        elif anchor and dest.suffix=='.md' and anchor not in anchors(dest.read_text()):errors.append({'missing_anchor':str(file),'target':target})
    if len(re.findall(r'^```',file.read_text(),re.M))%2:errors.append({'fences':str(file)})

inventory=WORK/'outputs/.research/course-project-guide/inventory.jsonl'
content_changes=[];metadata_changes=[];missing=[];source_count=0
for line in inventory.read_text().splitlines():
    row=json.loads(line);path=Path(row['path']);source_count+=1
    if not path.is_file():missing.append(str(path))
    elif sha(path)!=row['sha256']:
        (metadata_changes if path.name=='.DS_Store' else content_changes).append(str(path))
if content_changes or missing:errors.append({'source_content_changes':content_changes,'missing_sources':missing})
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert head==before['head']
diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
if diff.returncode:errors.append({'diff_check':diff.stdout+diff.stderr})
report={'checked_at':utc_now(),'status':'PASS_DELIVERY_WITH_RUNTIME_GATES' if not errors else 'FAIL',
        'runtime_code_id':runtime_code_id(),'config_id':digest(load_config()),'head':head,'head_unchanged':True,
        'test_count':98,'distinct_test_ids':len(set(ids)),'skipped_tests':0,'local_links_checked':links,'errors':errors,
        'preserved_inputs':preserved,'source_inventory_files_checked':source_count,'source_content_changes':content_changes,
        'preexisting_source_metadata_drift':metadata_changes,'missing_sources':missing,
        'new_retrieval_diagnostic_searches':35,'new_live_generation_calls':0,
        'browser_check':'browser-check.json','model_setup_approval':'PENDING','docker_rehearsal':'NOT_EXECUTED',
        'no_model_or_dependency_installation':True,'no_publication_commit_push_or_submission':True,
        'not_established':['real LLM quality','selected generator','Compose build and PostgreSQL restart','fresh-release reproduction','passing grade'],
        'artifact_hashes':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'README.md',ROOT/'docs/evaluation.md',ROOT/'docs/decisions.md',ROOT/'reports/checks.json',HERE/'response.en.md',HERE/'retrieval-misses.json',HERE/'runtime-preflight.json',HERE/'browser-check.json',HERE/'pilot-plan.json',HERE/'development-plan.json']}}
write_json(HERE/'delivery.json',report)
print(json.dumps({k:report[k] for k in ['status','test_count','distinct_test_ids','local_links_checked','source_inventory_files_checked','errors']},indent=2))
raise SystemExit(bool(errors))
