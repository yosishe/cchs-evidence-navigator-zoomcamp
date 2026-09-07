"""Streamlit interaction and monitoring based on course Module 5."""
import json
import os
import time

import pandas as pd
import streamlit as st

from navigator.common import digest, load_config, read_documents
from navigator.exports import claim_rows, csv_export, passage_rows, comparison_rows, tag_proposal_rows
from navigator.providers import provider_name
from navigator.monitoring import observed_tables
from navigator.rag import run_request
from navigator.retrieval import EncoderUnavailableError, Retriever
from navigator.storage import get_store

st.set_page_config(page_title="CCHS Evidence Navigator", page_icon="🔬", layout="wide")
st.title("CCHS Evidence Navigator")
st.caption("Trace a literature question to the passages behind it. Research evidence requires human review.")


@st.cache_resource
def resources(corpus_fingerprint, config_fingerprint):
    return Retriever(read_documents(), load_config())


try:
    cfg, documents = load_config(), read_documents()
    engine = resources(digest(documents), digest(cfg))
    # Storage follows the current runtime/backend; never reuse another environment's
    # journal simply because its corpus/config happen to have the same fingerprint.
    store = get_store()
except Exception as exc:
    st.error(f"Setup is incomplete ({type(exc).__name__}). Run ingestion and check the configured storage service.")
    st.code("python -m navigator ingest")
    st.stop()

with st.sidebar:
    st.header("Corpus and run")
    st.write(f"{len({d['source_id'] for d in documents})} publications · {len(documents)} passages/windows")
    st.caption(f"Corpus {engine.corpus_id[:12]} · config {digest(cfg)[:12]}")
    st.caption("Retrieval: " + cfg["retrieval"] + ". " + (
        "Selected on provisional development labels; researcher review remains pending."
        if cfg["selection_status"].startswith("SELECTED") else "Configuration is still under evaluation."
    ))
    source_ids = sorted({d["source_id"] for d in documents})
    selected = st.selectbox("Publication filter", ["All publications"] + source_ids)
    model_available = provider_name(cfg) == "ollama" or (os.getenv("ENABLE_PAID_LLM") == "1" and bool(os.getenv("OPENAI_API_KEY")))
    mode = st.radio("Mode", ["Evidence preview", "LLM answer"] if model_available else ["Evidence preview"])
    if not model_available:
        st.info("Preview makes no model calls. Select a local course-model configuration for generated answers.")
    st.caption("Population/model context is unknown unless reviewed; article type is separate.")
    traffic_origin = os.getenv("NAVIGATOR_TRAFFIC_ORIGIN", "user")
    if traffic_origin != "user":
        st.info(f"This session records {traffic_origin} activity, separately from researcher feedback.")

search_tab, dashboard_tab = st.tabs(["Find evidence", "Monitoring"])
with search_tab:
    with st.form("question"):
        question = st.text_area("Research question", placeholder="Which passages discuss PHOX2B and respiratory control?", max_chars=2000)
        submitted = st.form_submit_button("Find evidence", type="primary")
    if submitted:
        if not question.strip():
            st.warning("Enter a research question.")
        else:
            with st.spinner("Retrieving passages…"):
                try:
                    filters = {} if selected == "All publications" else {"source_id": selected}
                    record = run_request(question, engine, cfg, filters=filters,
                                         use_llm=mode == "LLM answer", traffic_origin=traffic_origin)
                    storage_start = time.perf_counter()
                    store.save_answer(record)
                    st.session_state["last_storage_seconds"] = time.perf_counter() - storage_start
                    st.session_state["answer"] = record
                except EncoderUnavailableError:
                    st.error("Encoder setup is incomplete. No answer was saved. Run python -m navigator prepare-encoder; downloads require installation approval.")
                except Exception as exc:
                    st.error(f"Search or storage failed ({type(exc).__name__}). No result was saved.")
    record = st.session_state.get("answer")
    if record:
        st.subheader(record["question"])
        st.caption(f"{record['mode']} · {record['status']} · {record['id']}")
        st.caption(f"Result corpus {record['corpus_id'][:12]} · result config {record['config_id'][:12]}")
        if record["limitations"]:
            st.info(record["limitations"])
        extractive = record.get("answer_style") == "verbatim_source_selection"
        if extractive and record["claims"]:
            st.caption("This answer uses original source excerpts selected by the model. Check their relevance, completeness and qualifications.")
        for claim in record["claims"]:
            st.text(claim["text"])
            st.caption("Evidence: " + claim["evidence_id"])
            if not extractive:
                st.text(claim["exact_quote"])
                st.caption("Verbatim quotation; whether it supports the claim still requires review.")
        hits = record["hits"]
        rows = passage_rows(record)
        if rows:
            st.dataframe(pd.DataFrame(rows)[["id", "source_id", "title", "section", "article_type", "year", "population_or_model"]], hide_index=True, width="stretch")
        for h in hits:
            with st.expander(f"{h['rank']}. {h['title']} — {h['section']}"):
                st.text(h["content"])
                st.link_button("Open publication", h["source_url"])
                st.caption(f"Passage {h['passage_index']} · characters [{h['start_in_passage']}, {h['end_in_passage']}) · source {h['source_version'][:12]}")
        st.download_button("Export evidence JSON", json.dumps(record, indent=2), file_name=f"evidence-{record['id']}.json", mime="application/json")
        if rows:
            st.download_button("Export passages CSV", csv_export(rows), file_name=f"passages-{record['id']}.csv", mime="text/csv")
        if record["claims"]:
            st.markdown("**Evidence comparison** — one claim per source row; differences require review.")
            st.dataframe(pd.DataFrame(comparison_rows(record))[["claim_text", "source_id", "article_type", "year", "exact_quote", "answer_limitations"]], hide_index=True)
            proposals = tag_proposal_rows(record)
            if proposals:
                st.markdown("**Research tag proposals** — literal terms in cited quotations; pending researcher review.")
                st.dataframe(pd.DataFrame(proposals)[["proposed_term", "source_id", "exact_quote", "proposal_reason", "review_status"]], hide_index=True)
                st.download_button("Export tag proposals CSV", csv_export(proposals), file_name=f"tag-proposals-{record['id']}.csv", mime="text/csv")
            try:
                st.download_button("Export claim review CSV", csv_export(claim_rows(record)), file_name=f"claims-{record['id']}.csv", mime="text/csv")
            except ValueError:
                st.error("Claim export failed integrity validation. Inspect the source record before using it.")
        with st.form("feedback-" + record["id"]):
            relevance = st.radio("Did this result help locate relevant evidence?", ["Helpful", "Not helpful"], horizontal=True)
            comment = st.text_input("Optional correction (do not enter patient information)", max_chars=2000)
            if st.form_submit_button("Save feedback"):
                try:
                    store.save_feedback(record["id"], 1 if relevance == "Helpful" else -1, comment, feedback_id=record["id"] + ":user", traffic_origin=record.get("traffic_origin", traffic_origin))
                    st.success("Feedback saved once for this answer.")
                except Exception as exc:
                    st.error(f"Feedback was not saved ({type(exc).__name__}).")

def show_monitoring():
    st.subheader("Observed application activity")
    st.caption("QA, evaluation and researcher activity are separate. Older records without an origin are labeled legacy_unknown.")
    try:
        answers, feedback = store.read()
    except Exception as exc:
        st.warning(f"Monitoring is temporarily unavailable ({type(exc).__name__}). No substitute activity is shown; retry after storage recovers.")
        return
    origins = ["user", "qa", "evaluation", "legacy_unknown", "all"]
    chosen_origin = st.selectbox("Activity origin", origins,
                                index=origins.index(traffic_origin) if traffic_origin in origins else 0)
    chosen_mode = st.selectbox("Activity mode", ["all", "evidence_preview", "llm"])
    try:
        data = observed_tables(answers, feedback, chosen_origin, chosen_mode)
    except Exception as exc:
        st.warning(f"Monitoring records could not be summarized ({type(exc).__name__}). Inspect stored records before relying on these charts.")
        return
    if data is None:
        st.info("No recorded activity in this scope. Select an existing origin or run a question; no artificial activity is generated.")
        return
    st.caption(f"Scope: {data['requests']} stored requests; origin={chosen_origin}; mode={chosen_mode}. Daily buckets use UTC. Feedback uses these answers and this origin only.")
    if data["excluded_mismatched_feedback"]:
        st.warning(f"Excluded {data['excluded_mismatched_feedback']} feedback records whose origin differs from their answer. Inspect the stored records.")
    if chosen_origin != "user":
        st.info("This scope may contain test or unclassified activity. It is not a researcher-satisfaction estimate.")
    st.markdown("**1. Request volume by day** — recorded requests, including failures.")
    st.bar_chart(data["volume"])
    st.markdown("**2. Generation/validation duration** — seconds; excludes retrieval, storage and initial index build.")
    # A bar remains visible for a single request; a line needs two observations.
    st.bar_chart(data["generation_seconds"])
    st.markdown("**3. Retrieved passage count by request** — number passed to answer generation or preview; a count is not relevance.")
    st.bar_chart(data["passage_counts"])
    st.markdown("**4. Feedback distribution** — unique rated answers in the selected origin and mode.")
    st.caption(f"Feedback coverage: {data['rated_requests']}/{data['requests']} requests.")
    if data["feedback"].empty:
        st.info("No feedback in this scope.")
    else:
        st.bar_chart(data["feedback"])
    st.markdown("**5. Request outcomes** — count by final status; errors are included.")
    st.bar_chart(data["outcomes"])
    st.markdown("**6. Provider tokens by model (when observed)** — previews have no model tokens.")
    if data["tokens"] is None:
        st.info("No provider usage has been recorded.")
    else:
        st.bar_chart(data["tokens"])
    st.caption("Local calls have zero API billing; electricity and compute are unmeasured. Missing token usage stays unknown. Commercial estimates require explicit rates.")


with dashboard_tab:
    show_monitoring()
