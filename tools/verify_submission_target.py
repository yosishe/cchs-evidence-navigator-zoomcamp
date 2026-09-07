#!/usr/bin/env python3
"""Verify the exact public GitHub repository and commit used for submission."""

from __future__ import annotations

import argparse
import json
import re
from typing import Any
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter


EXPECTED_REPOSITORY_URL = (
    "https://github.com/yosishe/cchs-evidence-navigator-zoomcamp"
)
EXPECTED_FULL_NAME = "yosishe/cchs-evidence-navigator-zoomcamp"
REQUEST_TIMEOUT_SECONDS = 3
# Project resource limit, not a course requirement. This is not a wall-clock deadline.
MAX_API_RESPONSE_BYTES = 1024 * 1024
PLATFORM_GET_FALLBACK_STATUSES = {403, 405, 501}
FULL_SHA_PATTERN = re.compile(r"[0-9a-fA-F]{40}\Z")


class VerificationFailure(Exception):
    def __init__(self, kind: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.kind = kind
        self.message = message
        self.details = details


def _validate_inputs(repository_url: str, commit_sha: str) -> str:
    try:
        parsed = urlsplit(repository_url)
        port = parsed.port
    except (TypeError, UnicodeError, ValueError) as exc:
        raise VerificationFailure("invalid_input", f"Malformed repository URL: {exc}") from exc

    if parsed.scheme != "https" or parsed.hostname != "github.com" or port is not None:
        raise VerificationFailure(
            "invalid_input",
            "Repository URL must use HTTPS on github.com with no explicit port.",
        )
    if parsed.username is not None or parsed.password is not None:
        raise VerificationFailure("invalid_input", "Repository URL must not contain user information.")
    if parsed.query or parsed.fragment:
        raise VerificationFailure("invalid_input", "Repository URL must not contain a query or fragment.")
    if parsed.path.rstrip("/").endswith(".git"):
        raise VerificationFailure("invalid_input", "Repository URL must not use a .git suffix.")
    if repository_url != EXPECTED_REPOSITORY_URL:
        raise VerificationFailure(
            "invalid_input",
            f"Repository URL must exactly equal {EXPECTED_REPOSITORY_URL}.",
        )
    if not isinstance(commit_sha, str) or FULL_SHA_PATTERN.fullmatch(commit_sha) is None:
        raise VerificationFailure(
            "invalid_input",
            "Commit SHA must contain exactly 40 hexadecimal characters.",
        )
    return commit_sha.lower()


def _prepare_session(session: requests.Session) -> None:
    session.trust_env = False
    session.auth = None
    session.cookies.clear()
    session.headers.pop("Authorization", None)
    session.headers.pop("Proxy-Authorization", None)
    session.headers.pop("Cookie", None)
    session.headers.update(
        {
            "Accept": "application/vnd.github+json",
            "User-Agent": "cchs-submission-target-checker/1.0",
        }
    )
    adapter = HTTPAdapter(max_retries=0)
    session.mount("http://", adapter)
    session.mount("https://", adapter)


def _request(
    session: requests.Session,
    method: str,
    url: str,
    check_name: str,
    *,
    stream: bool = False,
) -> requests.Response:
    try:
        session.cookies.clear()
        return session.request(
            method,
            url,
            allow_redirects=False,
            timeout=REQUEST_TIMEOUT_SECONDS,
            stream=stream,
        )
    except requests.Timeout as exc:
        raise VerificationFailure(
            "timeout",
            f"{check_name} exceeded its {REQUEST_TIMEOUT_SECONDS}-second connection/read-inactivity timeout; this is not a total elapsed-time limit.",
            check=check_name,
        ) from exc
    except requests.RequestException as exc:
        raise VerificationFailure(
            "network",
            f"{check_name} failed before an HTTP response was received: {exc}",
            check=check_name,
        ) from exc


def _require_http_200(
    response: requests.Response,
    check_name: str,
    *,
    anonymous_404: bool = False,
) -> None:
    status_code = response.status_code
    if status_code == 200:
        return
    if 300 <= status_code < 400:
        raise VerificationFailure(
            "redirect",
            f"{check_name} redirected; a redirect or sign-in page is not proof of public access.",
            check=check_name,
            status_code=status_code,
        )
    if status_code in {401, 403}:
        raise VerificationFailure(
            "auth",
            f"{check_name} returned HTTP {status_code}; anonymous access was not verified.",
            check=check_name,
            status_code=status_code,
        )
    if status_code == 404 and anonymous_404:
        raise VerificationFailure(
            "http",
            f"{check_name} returned HTTP 404 anonymously; this does not prove the repository is private.",
            check=check_name,
            status_code=status_code,
        )
    raise VerificationFailure(
        "http",
        f"{check_name} returned HTTP {status_code}; HTTP 200 is required.",
        check=check_name,
        status_code=status_code,
    )


def _json_object(response: requests.Response, check_name: str) -> dict[str, Any]:
    try:
        body = bytearray()
        for chunk in response.iter_content(chunk_size=8192):
            if len(body) + len(chunk) > MAX_API_RESPONSE_BYTES:
                raise VerificationFailure(
                    "response_too_large",
                    f"{check_name} exceeded the project API response limit.",
                    check=check_name,
                    maximum_bytes=MAX_API_RESPONSE_BYTES,
                )
            body.extend(chunk)
        payload = json.loads(body)
    except requests.Timeout as exc:
        raise VerificationFailure(
            "timeout",
            f"{check_name} exceeded its {REQUEST_TIMEOUT_SECONDS}-second read-inactivity timeout; this is not a total elapsed-time limit.",
            check=check_name,
        ) from exc
    except requests.RequestException as exc:
        raise VerificationFailure(
            "network", f"{check_name} could not finish reading the response: {exc}",
            check=check_name,
        ) from exc
    except (ValueError, TypeError, UnicodeError) as exc:
        raise VerificationFailure(
            "invalid_response",
            f"{check_name} returned an invalid JSON response.",
            check=check_name,
        ) from exc
    if not isinstance(payload, dict):
        raise VerificationFailure(
            "invalid_response",
            f"{check_name} did not return a JSON object.",
            check=check_name,
        )
    return payload


def _check(repository_url: str, commit_sha: str, session: requests.Session) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    platform_response = _request(session, "HEAD", repository_url, "platform_repository_url")
    platform_method = "HEAD"
    if platform_response.status_code in PLATFORM_GET_FALLBACK_STATUSES:
        platform_response.close()
        platform_response = _request(
            session,
            "GET",
            repository_url,
            "platform_repository_url",
            stream=True,
        )
        platform_method = "GET"
    try:
        _require_http_200(platform_response, "platform_repository_url")
        checks.append(
            {
                "name": "platform_repository_url",
                "method": platform_method,
                "status_code": platform_response.status_code,
                "passed": True,
            }
        )
    finally:
        platform_response.close()

    metadata_url = f"https://api.github.com/repos/{EXPECTED_FULL_NAME}"
    metadata_response = _request(session, "GET", metadata_url, "github_repository_metadata", stream=True)
    try:
        _require_http_200(metadata_response, "github_repository_metadata", anonymous_404=True)
        metadata = _json_object(metadata_response, "github_repository_metadata")
        if metadata.get("full_name") != EXPECTED_FULL_NAME:
            raise VerificationFailure(
                "repository_mismatch",
                "GitHub metadata did not identify the expected repository.",
                actual_full_name=metadata.get("full_name"),
            )
        if metadata.get("private") is True:
            raise VerificationFailure(
                "repository_private",
                "GitHub metadata explicitly reports that the repository is private.",
            )
        if metadata.get("private") is not False:
            raise VerificationFailure(
                "invalid_response",
                "GitHub metadata did not explicitly prove public visibility.",
            )
        checks.append(
            {
                "name": "github_repository_metadata",
                "method": "GET",
                "status_code": metadata_response.status_code,
                "passed": True,
            }
        )
    finally:
        metadata_response.close()

    commit_api_url = f"{metadata_url}/commits/{commit_sha}"
    commit_response = _request(session, "GET", commit_api_url, "github_commit", stream=True)
    try:
        _require_http_200(commit_response, "github_commit", anonymous_404=True)
        commit = _json_object(commit_response, "github_commit")
        actual_sha = commit.get("sha")
        if actual_sha != commit_sha:
            raise VerificationFailure(
                "commit_mismatch",
                "GitHub did not return the exact requested full commit SHA.",
                expected_sha=commit_sha,
                actual_sha=actual_sha,
            )
        checks.append(
            {
                "name": "github_commit",
                "method": "GET",
                "status_code": commit_response.status_code,
                "passed": True,
            }
        )
    finally:
        commit_response.close()

    tree_url = f"{repository_url}/tree/{commit_sha}"
    tree_response = _request(session, "GET", tree_url, "github_public_tree", stream=True)
    try:
        _require_http_200(tree_response, "github_public_tree", anonymous_404=True)
        checks.append(
            {
                "name": "github_public_tree",
                "method": "GET",
                "status_code": tree_response.status_code,
                "passed": True,
            }
        )
    finally:
        tree_response.close()

    return {
        "ok": True,
        "repository_url": repository_url,
        "expected_commit_sha": commit_sha,
        "checks": checks,
        "scope": {
            "anonymous_access_and_exact_commit_only": True,
            "quality_or_course_submission_verified": False,
            "connect_read_inactivity_timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "hard_total_deadline_enforced": False,
            "maximum_api_response_bytes": MAX_API_RESPONSE_BYTES,
            "maximum_requests": 5,
        },
        "verified": {
            "repository_full_name": EXPECTED_FULL_NAME,
            "visibility": "public",
            "commit_sha": commit_sha,
            "tree_url": tree_url,
        },
    }


def check_submission_target(
    repository_url: str,
    commit_sha: str,
    *,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Return a structured, fail-closed verification receipt."""
    try:
        normalized_sha = _validate_inputs(repository_url, commit_sha)
        active_session = session if session is not None else requests.Session()
        _prepare_session(active_session)
        return _check(repository_url, normalized_sha, active_session)
    except VerificationFailure as exc:
        return {
            "ok": False,
            "repository_url": repository_url,
            "expected_commit_sha": commit_sha,
            "error": {
                "kind": exc.kind,
                "message": exc.message,
                **exc.details,
            },
        }
    except Exception as exc:  # Fail closed for unexpected response/session behavior.
        return {
            "ok": False,
            "repository_url": repository_url,
            "expected_commit_sha": commit_sha,
            "error": {
                "kind": "unknown",
                "message": f"Verification could not be completed: {exc}",
            },
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_url")
    parser.add_argument("commit_sha")
    args = parser.parse_args(argv)

    receipt = check_submission_target(args.repository_url, args.commit_sha)
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
