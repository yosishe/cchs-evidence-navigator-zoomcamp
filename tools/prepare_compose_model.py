"""Explicit model setup for Compose, separate from normal app inference.

Reads the actual app config, never a second hardcoded model choice. Downloads
require --allow-download. Uses Ollama's official /api/pull and verifies the exact
installed artifact before the app may start. No paid provider or fallback.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from navigator.common import load_config
from navigator.providers import local_endpoint, model_identity, validate_provider


def prepare_model(config, allow_download=False):
    import requests
    if validate_provider(config) != "ollama":
        raise ValueError("Compose setup supports the local provider only")
    try:
        return model_identity(config)
    except RuntimeError:
        # Only an absent model can trigger setup. Digest mismatches or an
        # unavailable service must fail, not overwrite an existing installation.
        if not allow_download:
            raise PermissionError("Model is absent; explicit download approval is required")
    session = requests.Session(); session.trust_env = False
    root = local_endpoint(config).removesuffix("v1/")
    with session.post(root + "api/pull", json={"model": config["model"], "stream": True},
                      stream=True, timeout=(10, 300), allow_redirects=False) as response:
        response.raise_for_status()
        finished = False
        for line in response.iter_lines():
            if not line: continue
            event = json.loads(line)
            if event.get("error"): raise RuntimeError("Ollama model preparation failed")
            finished = event.get("status") == "success"
        if not finished: raise RuntimeError("Ollama model preparation did not finish")
    return model_identity(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-download", action="store_true")
    args = parser.parse_args()
    identity = prepare_model(load_config(), args.allow_download)
    print(json.dumps({k:v for k,v in identity.items() if k != "endpoint"}, indent=2))
