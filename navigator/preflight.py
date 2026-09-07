"""Read-only local setup diagnostics; no pulls, inference, installs or migrations.

This is deployment glue for the taught Ollama route, not a quality evaluation.
Native model details use POST /api/show, whose operation only reads metadata.
"""
import platform
import re
import shutil
import subprocess

import requests

from .common import digest, load_config, read_documents, runtime_code_id, utc_now
from .providers import local_endpoint, validate_provider


def inspect_runtime(config=None):
    cfg = config or load_config()
    report = {"created_at": utc_now(), "status": "PREFLIGHT",
              "scope": "Local setup metadata only; no answer-quality or reproduction claim",
              "runtime_code_id": runtime_code_id(), "config_id": digest(cfg),
              "python_version": platform.python_version(), "platform": platform.system(),
              "architecture": platform.machine(), "docker_available": shutil.which("docker") is not None,
              "configured_model": cfg["model"], "json_mode": cfg.get("json_mode", True),
              "request_timeout_seconds": cfg.get("request_timeout_seconds", 120),
              "provider_requests": 0, "metadata_requests": [], "blockers": [], "warnings": []}
    try:
        docs = read_documents()
        report["corpus"] = {"id": digest(docs), "windows": len(docs)}
    except (OSError, ValueError, KeyError):
        report["blockers"].append("Run python -m navigator ingest; the local corpus is missing or inconsistent.")
    cli = shutil.which("ollama")
    report["ollama_cli_available"] = cli is not None
    if cli:
        try:
            value = subprocess.run([cli, "--version"], capture_output=True, text=True, timeout=5)
            versions = re.findall(r"\b\d+\.\d+\.\d+(?:[-+][\w.]+)?", value.stdout + value.stderr)
            report["ollama_cli_version_candidates"] = list(dict.fromkeys(versions))
        except (OSError, subprocess.TimeoutExpired):
            report["warnings"].append("CLI version was unavailable within the metadata timeout.")
    try:
        if validate_provider(cfg) != "ollama":
            raise ValueError("Local preflight requires Ollama")
        root = local_endpoint(cfg).removesuffix("v1/")
        with requests.Session() as session:
            session.trust_env = False

            def read(method, endpoint, **kwargs):
                report["metadata_requests"].append({"method": method.upper(), "endpoint": endpoint})
                response = getattr(session, method)(root + endpoint, timeout=10,
                                                    allow_redirects=False, **kwargs)
                if response.status_code != 200:
                    raise RuntimeError("Metadata endpoint unavailable")
                return response.json()

            report["ollama_server_version"] = read("get", "api/version")["version"]
            models = read("get", "api/tags").get("models", [])
            report["installed_models"] = [{k: m.get(k) for k in ("name", "digest", "size")} for m in models]
            aliases = {cfg["model"], cfg["model"] + ":latest"}
            selected = next((m for m in models if m.get("name") in aliases and m.get("digest")), None)
            if selected is None:
                report["blockers"].append("Configured course model is missing. Download requires owner approval.")
                report["next_setup_command_after_approval"] = "ollama pull " + cfg["model"]
            else:
                report["selected_model"] = {k: selected.get(k) for k in ("name", "digest", "size")}
                if cfg.get("model_digest") and cfg["model_digest"] != selected["digest"]:
                    report["blockers"].append("Installed weights differ from the evaluated model digest.")
                try:
                    details = read("post", "api/show", json={"model": selected["name"]})
                    report["model_details"] = {k: details.get("details", {}).get(k)
                        for k in ("family", "parameter_size", "quantization_level")}
                    report["architecture_context_limits"] = {k: v for k, v in details.get("model_info", {}).items()
                                                              if k.endswith(".context_length")}
                    loaded = read("get", "api/ps").get("models", [])
                    current = next((m for m in loaded if m.get("digest") == selected["digest"]), {})
                    report["loaded_context_tokens"] = current.get("context_length")
                    report["context_note"] = "Architecture capacity is not the allocated server window. Null means not observed, not zero."
                except (requests.RequestException, RuntimeError, ValueError, KeyError, TypeError):
                    report["warnings"].append("Model capacity/runtime context metadata unavailable; no window size assumed.")
    except (requests.RequestException, RuntimeError, ValueError, KeyError, TypeError, PermissionError):
        report["blockers"].append("Local model metadata preflight failed; check the allowed endpoint and Ollama service.")
    report["status"] = "BLOCKED_RUNTIME_PREFLIGHT" if report["blockers"] else "RUNTIME_METADATA_READY"
    report["still_required"] = ["Offline encoder check: python -m navigator prepare-encoder",
                                "A successful generated answer and paired-prompt review",
                                "Compose and fresh-environment rehearsal before claiming reproduction"]
    return report
