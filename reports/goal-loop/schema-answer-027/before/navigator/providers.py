"""Course 2024 Ollama Chat Completions; application-owned call receipts.

No model download, installation, provider fallback or automatic retry occurs here.
The endpoint restriction is a project adaptation of the user's no-paid-call boundary.
"""
from __future__ import annotations

import os
import copy
import time
import uuid
from urllib.parse import urlparse
from .common import runtime_dir, runtime_code_id, utc_now, write_json, digest

# The exact Q8 Mini variant is a project precision experiment on the taught
# Phi3 route, informed by the 2024 quantization example. No family wildcard,
# automatic download, default switch or permission to install is implied.
LOCAL_MODELS = {"phi3", "phi3:latest", "phi3:mini", "gemma:2b",
                "phi3:3.8b-mini-128k-instruct-q8_0"}


class IncompleteModelOutput(ValueError):
    """The provider completed its attempt, but its output cannot be accepted."""


def provider_name(config):
    return config.get("provider", "openai")


def local_endpoint(config):
    endpoint = os.getenv("OLLAMA_BASE_URL", config.get("base_url", "http://localhost:11434/v1/"))
    parsed = urlparse(endpoint)
    if (parsed.scheme != "http" or parsed.hostname not in {
            "localhost", "127.0.0.1", "::1", "ollama", "host.docker.internal"}
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or parsed.path.rstrip("/") != "/v1"):
        raise ValueError("Only the local Ollama /v1 endpoint is allowed")
    return endpoint.rstrip("/") + "/"


def validate_provider(config):
    provider = provider_name(config)
    if provider == "ollama":
        local_endpoint(config)
        if config["model"] not in LOCAL_MODELS:
            raise ValueError("Local model has no approved course implementation source")
    elif provider == "openai":
        if os.getenv("ENABLE_PAID_LLM") != "1":
            raise PermissionError("Paid LLM execution is disabled")
    else:
        raise ValueError("Unknown provider; fallback is forbidden")
    return provider


def model_identity(config):
    """Read installed weights, never pull. A missing digest blocks an experiment."""
    import requests
    provider = validate_provider(config)
    if provider != "ollama":
        return {"provider": provider, "model": config["model"], "digest": None}
    root = local_endpoint(config).removesuffix("v1/")
    session = requests.Session()
    session.trust_env = False
    response = session.get(root + "api/tags", timeout=10, allow_redirects=False)
    response.raise_for_status()
    requested = config["model"]
    aliases = {requested, requested + ":latest" if ":" not in requested else requested}
    match = next((m for m in response.json().get("models", []) if m.get("name") in aliases), None)
    if not match or not match.get("digest"):
        raise RuntimeError("Requested course model is not installed with a verifiable digest")
    if config.get("model_digest") and config["model_digest"] != match["digest"]:
        raise ValueError("Installed model differs from the selected digest")
    return {"provider": provider, "model": requested, "resolved_model": match["name"],
            "digest": match["digest"], "size_bytes": match.get("size"), "endpoint": root}


def complete(config, messages, *, stage, ledger, client=None):
    """Append the receipt before the actual API attempt; retain it on failure."""
    provider = validate_provider(config)
    live_client = client is None
    json_mode = provider == "ollama" and config.get("json_mode", True)
    if type(config.get("json_mode", True)) is not bool:
        raise ValueError("json_mode must be a boolean")
    if client is None:
        from openai import OpenAI, DefaultHttpxClient
        options = {"timeout": config.get("request_timeout_seconds", 120), "max_retries": 0}
        if provider == "ollama":
            client = OpenAI(base_url=local_endpoint(config), api_key="ollama",
                            http_client=DefaultHttpxClient(follow_redirects=False, trust_env=False), **options)
        else:
            if not os.getenv("OPENAI_API_KEY"):
                raise PermissionError("OPENAI_API_KEY is not configured locally")
            client = OpenAI(**options)
    receipt = {"id": str(uuid.uuid4()), "stage": stage, "provider": provider,
               "execution_kind": "live_provider_client" if live_client else "sdk_fixture",
               "created_at": utc_now(), "config_id": digest(config), "runtime_code_id": runtime_code_id(),
               "model": config["model"], "model_digest": config.get("model_digest"),
               "json_mode": json_mode,
               "request_timeout_seconds": config.get("request_timeout_seconds", 120),
               "status": "attempted", "input_tokens": None, "output_tokens": None,
               "api_cost_usd": 0.0 if provider == "ollama" else None,
               "cost_scope": "No API billing; local compute/energy not measured" if provider == "ollama" else "Unknown until configured"}
    receipt["messages"] = copy.deepcopy(messages)
    ledger.append(receipt)
    journal_path = runtime_dir() / "provider-attempts" / (receipt["id"] + ".json") if live_client else None
    if journal_path:
        # A process interruption leaves an attempted/unknown-outcome receipt.
        # This is not proof that the server received or completed the request.
        write_json(journal_path, receipt)
    start = time.perf_counter()
    try:
        if provider == "ollama":
            options = {"response_format": {"type": "json_object"}} if json_mode else {}
            response = client.chat.completions.create(model=config["model"], messages=messages,
                temperature=config.get("temperature", 0), max_tokens=config["max_output_tokens"], **options)
            content = response.choices[0].message.content
            reason = response.choices[0].finish_reason
            usage = response.usage
            if usage:
                receipt.update(input_tokens=usage.prompt_tokens, output_tokens=usage.completion_tokens)
        else:
            response = client.responses.create(model=config["model"],
                max_output_tokens=config["max_output_tokens"], input=messages)
            content = response.output_text
            reason = "length" if getattr(response, "status", None) == "incomplete" else "stop"
            if response.usage:
                receipt.update(input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens)
        receipt.update(status="completed", finish_reason=reason, raw_output=content)
        if reason == "length" or not isinstance(content, str):
            raise IncompleteModelOutput("Incomplete model output")
        return content
    except Exception as exc:
        # A token-limited completion is an observed generation failure, not an
        # unavailable service. Keep the completed receipt and its raw output.
        if isinstance(exc, IncompleteModelOutput):
            receipt["output_error_type"] = type(exc).__name__
        else:
            receipt.update(status="error", error_type=type(exc).__name__)
        raise
    finally:
        receipt["seconds"] = time.perf_counter() - start
        if journal_path:
            write_json(journal_path, receipt)
