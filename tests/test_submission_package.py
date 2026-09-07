"""Submission-language checks use synthetic text, never scientific examples."""
import json
import unittest
from urllib.parse import quote

from tools import audit_public_package as audit


class SubmissionLanguageTests(unittest.TestCase):
    def test_literal_text_is_reported_without_copying_its_content(self):
        sample = "English introduction\n" + chr(0x05D0)
        findings = audit.language_findings(sample)
        self.assertEqual(findings, [{"kind": "HEBREW_CONTENT", "line": 2}])
        self.assertNotIn(chr(0x05D0), json.dumps(findings, ensure_ascii=False))

    def test_encoded_links_json_and_html_cannot_hide_language(self):
        letter = chr(0x05D0)
        samples = ["https://example.org/" + quote(letter),
                   json.dumps({"description": letter}),
                   "&#" + str(ord(letter)) + ";",
                   "&#x" + format(ord(letter), "x") + ";"]
        for text in samples:
            with self.subTest(text=text):
                self.assertEqual(audit.language_findings(text),
                                 [{"kind": "HEBREW_CONTENT", "line": 1}])

    def test_english_scientific_text_and_unicode_symbols_remain_valid(self):
        text = "PHOX2B: 19/22 (86%). Source -> claim.\n" + chr(0x03B1)
        self.assertEqual(audit.language_findings(text), [])
        self.assertEqual(audit.language_findings("Model cost: 0.0; source: 0x05D0"), [])

    def test_presentation_form_is_detected(self):
        self.assertEqual(audit.language_findings(chr(0xFB2A)),
                         [{"kind": "HEBREW_CONTENT", "line": 1}])


if __name__ == "__main__":
    unittest.main()
