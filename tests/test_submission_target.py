import io
import json
import unittest
from contextlib import redirect_stdout

import requests

from tools.verify_submission_target import check_submission_target, main


REPOSITORY_URL = "https://github.com/yosishe/cchs-evidence-navigator-zoomcamp"
COMMIT_SHA = "0123456789abcdef0123456789abcdef01234567"
FULL_NAME = "yosishe/cchs-evidence-navigator-zoomcamp"


class FakeCookies:
    def __init__(self):
        self.cleared = False

    def clear(self):
        self.cleared = True


class FakeResponse:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload
        self.closed = False

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload

    def iter_content(self, chunk_size):
        if isinstance(self._payload, Exception):
            raise self._payload
        body = json.dumps(self._payload).encode("utf-8")
        for offset in range(0, len(body), chunk_size):
            yield body[offset:offset + chunk_size]

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.trust_env = True
        self.auth = object()
        self.cookies = FakeCookies()
        self.headers = {}
        self.adapters = {}

    def mount(self, prefix, adapter):
        self.adapters[prefix] = adapter

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def successful_responses(commit_sha=COMMIT_SHA):
    return [
        FakeResponse(200),
        FakeResponse(200, {"full_name": FULL_NAME, "private": False}),
        FakeResponse(200, {"sha": commit_sha}),
        FakeResponse(200),
    ]


class SubmissionTargetTests(unittest.TestCase):
    def test_invalid_repository_or_commit_never_reaches_network(self):
        invalid_cases = [
            ("not-a-url", COMMIT_SHA),
            ("https://example.com/yosishe/cchs-evidence-navigator-zoomcamp", COMMIT_SHA),
            ("https://user@github.com/yosishe/cchs-evidence-navigator-zoomcamp", COMMIT_SHA),
            (f"{REPOSITORY_URL}?tab=readme", COMMIT_SHA),
            (f"{REPOSITORY_URL}#readme", COMMIT_SHA),
            (f"{REPOSITORY_URL}.git", COMMIT_SHA),
            (REPOSITORY_URL, "0123456"),
        ]

        for repository_url, commit_sha in invalid_cases:
            with self.subTest(repository_url=repository_url, commit_sha=commit_sha):
                session = FakeSession([])
                result = check_submission_target(repository_url, commit_sha, session=session)
                self.assertFalse(result["ok"])
                self.assertEqual(result["error"]["kind"], "invalid_input")
                self.assertEqual(session.calls, [])

    def test_wrong_commit_is_rejected_despite_successful_http(self):
        wrong_sha = "f" * 40
        session = FakeSession(successful_responses(commit_sha=wrong_sha)[:3])

        result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["kind"], "commit_mismatch")
        self.assertEqual(result["error"]["actual_sha"], wrong_sha)
        self.assertEqual(len(session.calls), 3)

    def test_redirect_sign_in_and_private_metadata_cannot_pass(self):
        cases = [
            (
                [FakeResponse(302)],
                "redirect",
                1,
            ),
            (
                successful_responses()[:3] + [FakeResponse(302)],
                "redirect",
                4,
            ),
            (
                [
                    FakeResponse(200),
                    FakeResponse(200, {"full_name": FULL_NAME, "private": True}),
                ],
                "repository_private",
                2,
            ),
        ]

        for responses, expected_kind, expected_calls in cases:
            with self.subTest(expected_kind=expected_kind, expected_calls=expected_calls):
                session = FakeSession(responses)
                result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)
                self.assertFalse(result["ok"])
                self.assertEqual(result["error"]["kind"], expected_kind)
                self.assertEqual(len(session.calls), expected_calls)

    def test_metadata_404_does_not_claim_the_repository_is_private(self):
        session = FakeSession([FakeResponse(200), FakeResponse(404)])

        result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["kind"], "http")
        self.assertIn("does not prove", result["error"]["message"])

    def test_timeout_and_auth_failures_have_distinct_error_kinds(self):
        cases = [
            ([requests.Timeout("timed out")], "timeout"),
            ([FakeResponse(200), FakeResponse(401)], "auth"),
        ]

        for responses, expected_kind in cases:
            with self.subTest(expected_kind=expected_kind):
                session = FakeSession(responses)
                result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)
                self.assertFalse(result["ok"])
                self.assertEqual(result["error"]["kind"], expected_kind)

    def test_platform_fallback_is_used_only_for_documented_statuses(self):
        for status_code in (403, 405, 501):
            with self.subTest(status_code=status_code):
                session = FakeSession([FakeResponse(status_code)] + successful_responses())
                result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)
                self.assertTrue(result["ok"])
                self.assertEqual([call[0] for call in session.calls[:2]], ["HEAD", "GET"])

        session = FakeSession([FakeResponse(500)])
        result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["kind"], "http")
        self.assertEqual([call[0] for call in session.calls], ["HEAD"])

    def test_requests_are_anonymous_and_use_platform_inactivity_timeout(self):
        session = FakeSession(successful_responses())
        session.headers.update({
            "Authorization": "synthetic-test-value",
            "Proxy-Authorization": "synthetic-test-value",
            "Cookie": "synthetic-test-cookie",
        })

        result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)

        self.assertTrue(result["ok"])
        self.assertFalse(session.trust_env)
        self.assertIsNone(session.auth)
        self.assertTrue(session.cookies.cleared)
        self.assertNotIn("Authorization", session.headers)
        self.assertNotIn("Proxy-Authorization", session.headers)
        self.assertNotIn("Cookie", session.headers)
        self.assertEqual(set(session.adapters), {"http://", "https://"})
        for _method, _url, kwargs in session.calls:
            self.assertEqual(kwargs["timeout"], 3)
            self.assertFalse(kwargs["allow_redirects"])

    def test_oversized_api_body_fails_without_claiming_public_access(self):
        payload = {"full_name": FULL_NAME, "private": False, "extra": "x" * (1024 * 1024)}
        response = FakeResponse(200, payload)
        session = FakeSession([FakeResponse(200), response])

        result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["kind"], "response_too_large")
        self.assertEqual(len(session.calls), 2)
        self.assertTrue(session.calls[1][2]["stream"])
        self.assertTrue(response.closed)

    def test_api_body_read_timeout_is_not_reported_as_success_or_total_deadline(self):
        response = FakeResponse(200, requests.Timeout("synthetic body inactivity"))
        session = FakeSession([FakeResponse(200), response])

        result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"]["kind"], "timeout")
        self.assertIn("inactivity", result["error"]["message"])
        self.assertTrue(response.closed)

    def test_success_receipt_contains_the_exact_verified_sha(self):
        session = FakeSession(successful_responses())

        result = check_submission_target(REPOSITORY_URL, COMMIT_SHA, session=session)

        self.assertTrue(result["ok"])
        self.assertEqual(result["verified"]["commit_sha"], COMMIT_SHA)
        self.assertEqual(result["verified"]["repository_full_name"], FULL_NAME)
        self.assertEqual(
            result["verified"]["tree_url"],
            f"{REPOSITORY_URL}/tree/{COMMIT_SHA}",
        )
        self.assertEqual([check["status_code"] for check in result["checks"]], [200] * 4)

    def test_cli_writes_structured_failure_to_stdout_and_exits_nonzero(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main([REPOSITORY_URL, "short-sha"])

        receipt = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["error"]["kind"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
