import json
import tempfile
import unittest
from pathlib import Path

from navigator.common import digest
from tools.stage_corpus_expansion import stage_corpus_expansion


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")


def bioc(source_id, text="Evidence about PHOX2B and ventilation."):
    return {"documents": [{"id": source_id, "passages": [
        {"offset": 0, "infons": {"type": "title", "section_type": "TITLE"}, "text": "Title"},
        {"offset": 6, "infons": {"type": "paragraph", "section_type": "ABSTRACT"}, "text": text},
    ]}]}


class CorpusExpansionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.package = self.base / "package"
        self.intake = self.base / "intake"
        self.destination = self.base / "candidate"
        for relative, content in {
            "app.py": "print('app')\n",
            "navigator/core.py": "VALUE = 1\n",
            "tools/helper.py": "VALUE = 2\n",
            "tests/original.py": "VALUE = 3\n",
            "docs/history.md": "historical report context\n",
            "docs/private.pdf": "private source artifact\n",
            "reports/history.json": "{\"historical\": true}\n",
            "reports/approved-screenshot.png": "approved screenshot\n",
            "README.md": "package\n",
            "requirements.lock": "frozen\n",
            "data/evaluation/questions-v2.json": "{\"corpus_id\": \"old\"}\n",
            "data/raw/UNLISTED.json": "stale baseline raw file\n",
            "data/models/model.safetensors": "weights\n",
            "data/cache/model.gguf": "weights\n",
            ".env": "SECRET=do-not-copy\n",
            "runtime/private.bin": "runtime\n",
        }.items():
            path = self.package / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        self.config = {
            "retrieval": "vector", "model": "phi3", "chunk_chars": 80,
            "overlap_chars": 10, "selection_status": "SELECTED_OLD",
            "generation_selection_status": "SELECTED_OLD",
            "question_bank": "data/evaluation/questions-v2.json",
        }
        write_json(self.package / "configs/app.json", self.config)
        write_json(self.package / "data/manifest.json", {"version": 1, "sources": []})
        self.raw = json.dumps(bioc("S1"), ensure_ascii=False).encode()
        (self.intake / "raw").mkdir(parents=True)
        (self.intake / "raw/S1.json").write_bytes(self.raw)
        self.source = {
            "source_id": "S1", "status": "included", "title": "Synthetic title",
            "article_type": "primary", "article_url": "https://example.test/1",
            "license": "CC-BY", "raw_file": "raw/S1.json", "sha256": digest(self.raw),
            "pmid": "123", "custom_metadata": {"review": "approved"},
        }

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self, sources=None):
        path = self.intake / "manifest.json"
        write_json(path, {"version": 7, "selection": "reviewed intake", "sources": sources or [
            self.source, {"source_id": "BLOCKED1", "status": "blocked", "error": "license unavailable",
                          "custom_metadata": "preserve me"},
        ]})
        return path

    def stage(self, manifest=None, destination=None):
        return stage_corpus_expansion(
            manifest or self.manifest(), destination or self.destination,
            package_root=self.package,
        )

    def test_hash_mutation_and_wrong_identity_are_rejected_before_destination_exists(self):
        manifest = self.manifest()
        (self.intake / "raw/S1.json").write_bytes(self.raw + b" ")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.stage(manifest)
        self.assertFalse(self.destination.exists())

        (self.intake / "raw/S1.json").write_bytes(
            json.dumps(bioc("OTHER"), ensure_ascii=False).encode()
        )
        changed = json.loads(manifest.read_text())
        changed["sources"][0]["sha256"] = digest((self.intake / "raw/S1.json").read_bytes())
        write_json(manifest, changed)
        with self.assertRaisesRegex(ValueError, "publication identity"):
            self.stage(manifest)
        self.assertFalse(self.destination.exists())

    def test_duplicate_publications_are_rejected_even_when_ids_differ(self):
        second_raw = json.dumps(bioc("S2"), ensure_ascii=False).encode()
        (self.intake / "raw/S2.json").write_bytes(second_raw)
        second = {**self.source, "source_id": "S2", "raw_file": "raw/S2.json",
                  "sha256": digest(second_raw), "pmid": "456", "article_url": "https://example.test/2"}
        with self.assertRaisesRegex(ValueError, "Duplicate publication content"):
            self.stage(self.manifest([self.source, second]))
        self.assertFalse(self.destination.exists())

    def test_duplicate_identifiers_are_canonicalized_for_supported_forms(self):
        second_raw = json.dumps(bioc("S2", "Distinct publication text."), ensure_ascii=False).encode()
        (self.intake / "raw/S2.json").write_bytes(second_raw)
        cases = [
            ("doi", "10.1234/Example", "https://doi.org/10.1234/example"),
            ("doi", "doi:10.1234/example", "http://dx.doi.org/10.1234/EXAMPLE"),
            ("pmid", "12345", "PMID: 12345"),
            ("pmcid", "PMC12345", "pmcid: PMC12345"),
        ]
        for field, first_value, second_value in cases:
            with self.subTest(field=field, second=second_value):
                first = {**self.source, field: first_value}
                second = {**self.source, "source_id": "S2", "raw_file": "raw/S2.json",
                          "sha256": digest(second_raw), "pmid": "67890",
                          "article_url": "https://example.test/2", field: second_value}
                with self.assertRaisesRegex(ValueError, "Duplicate publication identifier"):
                    self.stage(self.manifest([first, second]))
                self.assertFalse(self.destination.exists())

    def test_existing_and_overlapping_destinations_fail_without_mutation(self):
        self.destination.mkdir()
        marker = self.destination / "keep.txt"
        marker.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.stage(destination=self.destination)
        self.assertEqual(marker.read_text(), "keep")

        overlap = self.intake / "candidate"
        with self.assertRaisesRegex(ValueError, "overlaps"):
            self.stage(destination=overlap)
        self.assertFalse(overlap.exists())

        package_child = self.package / "candidate"
        with self.assertRaisesRegex(ValueError, "active package"):
            self.stage(destination=package_child)
        self.assertFalse(package_child.exists())

    def test_unsafe_source_id_and_source_symlink_are_rejected(self):
        unsafe = {**self.source, "source_id": "../escape"}
        with self.assertRaisesRegex(ValueError, "Unsafe source_id"):
            self.stage(self.manifest([unsafe]))
        self.assertFalse(self.destination.exists())

    def test_manifest_config_and_destination_symlink_ancestors_are_rejected(self):
        manifest = self.manifest()
        intake_link = self.base / "intake-link"
        intake_link.symlink_to(self.intake, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink ancestor"):
            self.stage(intake_link / "manifest.json")
        self.assertFalse(self.destination.exists())

        config_link = self.base / "config-link"
        config_link.symlink_to(self.package / "configs", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink ancestor"):
            stage_corpus_expansion(manifest, self.destination,
                                   config=config_link / "app.json", package_root=self.package)
        self.assertFalse(self.destination.exists())

        output = self.base / "real-output"
        output.mkdir()
        output_link = self.base / "output-link"
        output_link.symlink_to(output, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink ancestor"):
            self.stage(manifest, output_link / "candidate")
        self.assertFalse((output / "candidate").exists())

        link = self.intake / "linked.json"
        link.symlink_to(self.intake / "raw/S1.json")
        linked = {**self.source, "raw_file": "linked.json"}
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.stage(self.manifest([linked]))
        self.assertFalse(self.destination.exists())

    def test_success_preserves_bytes_metadata_defaults_and_historical_files(self):
        manifest = self.manifest()
        requested_hash = digest(json.loads(manifest.read_text()))
        original_config_bytes = (self.package / "configs/app.json").read_bytes()
        stale_bank_bytes = (self.package / "data/evaluation/questions-v2.json").read_bytes()

        receipt = self.stage(manifest)

        copied_raw = self.destination / "data/raw/S1.json"
        self.assertEqual(copied_raw.read_bytes(), self.raw)
        candidate_manifest = json.loads((self.destination / "data/manifest.json").read_text())
        included = candidate_manifest["sources"][0]
        self.assertEqual(included["raw_file"], "raw/S1.json")
        self.assertEqual(included["custom_metadata"], {"review": "approved"})
        self.assertEqual(candidate_manifest["sources"][1]["status"], "blocked")
        self.assertEqual(candidate_manifest["sources"][1]["custom_metadata"], "preserve me")

        candidate_config = json.loads((self.destination / "configs/app.json").read_text())
        self.assertEqual(candidate_config["retrieval"], self.config["retrieval"])
        self.assertEqual(candidate_config["model"], self.config["model"])
        self.assertEqual(candidate_config["selection_status"], "UNSELECTED_FOR_EXPANDED_CORPUS")
        self.assertEqual(candidate_config["generation_selection_status"], "UNSELECTED_FOR_EXPANDED_CORPUS")
        self.assertEqual(candidate_config["question_bank"], "data/evaluation/expansion-development.json")
        self.assertFalse((self.destination / candidate_config["question_bank"]).exists())
        self.assertEqual((self.destination / "data/evaluation/questions-v2.json").read_bytes(), stale_bank_bytes)
        self.assertFalse((self.destination / "data/raw/UNLISTED.json").exists())
        self.assertEqual((self.destination / "reports/history.json").read_text(), "{\"historical\": true}\n")
        self.assertEqual((self.destination / "reports/approved-screenshot.png").read_text(),
                         "approved screenshot\n")
        self.assertFalse((self.destination / "docs/private.pdf").exists())
        self.assertFalse((self.destination / "data/models/model.safetensors").exists())
        self.assertFalse((self.destination / "data/cache/model.gguf").exists())
        self.assertFalse((self.destination / ".env").exists())
        self.assertFalse((self.destination / "runtime").exists())
        self.assertEqual((self.package / "configs/app.json").read_bytes(), original_config_bytes)

        on_disk_receipt = json.loads((self.destination / "reports/corpus-expansion-staging.json").read_text())
        self.assertEqual(receipt, on_disk_receipt)
        self.assertEqual(receipt["status"], "STAGED_VALIDATED_NOT_EVALUATED")
        self.assertEqual(receipt["requested_manifest_hash"], requested_hash)
        self.assertEqual(receipt["candidate_manifest_hash"], digest(candidate_manifest))
        self.assertEqual(receipt["candidate_config_hash"], digest(candidate_config))
        self.assertEqual(receipt["copied_sources"], [{"source_id": "S1", "sha256": digest(self.raw)}])
        self.assertEqual(receipt["baseline_runtime_code_id"], receipt["candidate_runtime_code_id"])
        self.assertFalse(receipt["generation_performed"])
        self.assertFalse(receipt["quality_evaluation_performed"])
        self.assertFalse(receipt["promotion_performed"])
        self.assertIn("configs/app.json", receipt["baseline_file_hashes"])
        self.assertIn("reports/approved-screenshot.png", receipt["baseline_file_hashes"])
        self.assertNotIn("docs/private.pdf", receipt["baseline_file_hashes"])
        self.assertNotIn("data/models/model.safetensors", receipt["baseline_file_hashes"])
        self.assertNotIn("data/cache/model.gguf", receipt["baseline_file_hashes"])


if __name__ == "__main__":
    unittest.main()
