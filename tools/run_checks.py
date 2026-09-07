"""Run contracts and available integration tests; report skipped and external gates."""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from navigator.common import digest, utc_now, write_json, load_config, runtime_code_id
from navigator.corpus import prepare
from navigator.evaluation import validate_questions

result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                        cwd=ROOT, capture_output=True, text=True)
text = result.stdout + result.stderr
docs, excluded, manifest = prepare()
bank = json.loads((ROOT / load_config().get("question_bank", "data/evaluation/questions.json")).read_text())
validate_questions(bank["questions"], docs)
if bank["corpus_id"] != digest(docs):
    raise RuntimeError("Question bank belongs to a different corpus")
missing = [m for m in ["dlt", "duckdb", "minsearch", "streamlit", "openai", "psycopg", "sentence_transformers"] if importlib.util.find_spec(m) is None]
skipped = len(re.findall(r"\.\.\. skipped ", text))
count = int(re.search(r"Ran (\d+) tests", text).group(1))
report = {
    "created_at": utc_now(),
    "runtime_code_id": runtime_code_id(),
    "status": ("PASS_WITH_SKIPPED_TESTS" if skipped else "LOCAL_SUITE_PASS_EXTERNAL_GATES_PENDING") if result.returncode == 0 else "FAIL",
    "suite_passed": result.returncode == 0,
    "test_count": count, "passed_count": count - skipped if result.returncode == 0 else None,
    "skipped_count": skipped,
    "test_output": text, "source_hashes_verified": True,
    "question_anchors_verified": True, "corpus_id": digest(docs),
    "chunk_count": len(docs), "excluded_passages": len(excluded),
    "missing_dependencies_in_this_interpreter": missing,
    "docker_available": shutil.which("docker") is not None,
    "test_scope": "Python contracts plus real minsearch, dlt/DuckDB and Streamlit AppTest when their dependencies are present. SDK responses in contracts are mocks; AppTest is not a browser.",
    "not_established_by_this_check": ["live provider response", "retrieval quality", "answer quality", "browser interaction (separate report)", "PostgreSQL persistence", "Compose startup", "human scientific review", "submission readiness"],
}
write_json(ROOT / "reports/checks.json", report)
print(json.dumps({k:v for k,v in report.items() if k != "test_output"}, indent=2))
raise SystemExit(result.returncode)
