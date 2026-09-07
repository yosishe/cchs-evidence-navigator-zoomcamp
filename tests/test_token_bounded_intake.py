import json
import tempfile
import unittest
from pathlib import Path

from navigator.common import digest
from navigator.corpus import prepare
from navigator.retrieval import embedding_text
from tools.prepare_token_bounded_intake import prepare_token_bounded_intake


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")


def bioc(source_id, title, passages):
    offset = len(title) + 1
    values = [{
        "offset": 0,
        "infons": {"type": "title", "section_type": "TITLE"},
        "text": title,
        "sentences": [],
    }]
    for text, infons in passages:
        values.append({
            "offset": offset,
            "infons": infons,
            "text": text,
            "sentences": [],
            "annotations": [],
        })
        offset += len(text) + 1
    return {"documents": [{"id": source_id, "passages": values}]}


class VariableDensityCounter:
    """A deterministic tokenizer double where '#' costs four tokens."""

    def __init__(self, maximum=18):
        self.max_seq_length = maximum

    def count(self, text):
        return 2 + sum(4 if char == "#" else 1 for char in text)


class NonMonotonicCounter:
    max_seq_length = 12

    def count(self, text):
        # A shorter string can cost more, so binary-search assumptions are unsafe.
        return len(text) + (8 if text.endswith("x") else 0)


class TokenBoundedIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.intake = self.base / "intake"
        self.destination = self.base / "bounded"
        self.config_path = self.base / "app.json"
        self.model_cache = self.base / "model-cache"
        self.model_cache.mkdir()
        self.config = {
            "chunk_chars": 12,
            "overlap_chars": 3,
            "embedding_text": "title_content",
            "embedding_model": "fixture/model",
            "embedding_revision": "fixture-revision",
            "embedding_device": "cpu",
        }
        write_json(self.config_path, self.config)

        self.stable_raw = json.dumps(
            bioc("STABLE", "A", [("ordinary", {"type": "paragraph", "section_type": "ABSTRACT"})]),
            ensure_ascii=False,
        ).encode()
        self.dense_text = "ab####cdefghij"
        self.affected_raw = json.dumps(
            bioc("AFFECTED", "T", [
                (self.dense_text, {"type": "paragraph", "section_type": "RESULTS", "custom": "kept"}),
                ("short", {"type": "paragraph", "section_type": "DISCUSS"}),
            ]),
            ensure_ascii=False,
        ).encode()
        (self.intake / "raw").mkdir(parents=True)
        (self.intake / "raw/STABLE.json").write_bytes(self.stable_raw)
        (self.intake / "raw/AFFECTED.json").write_bytes(self.affected_raw)
        self.manifest_path = self.intake / "manifest.json"
        write_json(self.manifest_path, {"version": 4, "sources": [
            self.source("STABLE", self.stable_raw),
            self.source("AFFECTED", self.affected_raw),
            {"source_id": "BLOCKED", "status": "blocked", "error": "kept"},
        ]})

    def tearDown(self):
        self.temp.cleanup()

    def source(self, source_id, raw):
        return {
            "source_id": source_id,
            "status": "included",
            "title": "A" if source_id == "STABLE" else "T",
            "article_url": f"https://example.test/{source_id}",
            "article_type": "fixture",
            "license": "CC-BY",
            "raw_file": f"raw/{source_id}.json",
            "sha256": digest(raw),
        }

    def run_prepare(self, **kwargs):
        return prepare_token_bounded_intake(
            self.manifest_path,
            self.config_path,
            self.destination,
            self.model_cache,
            token_counter=VariableDensityCounter(),
            active_package=self.base / "unrelated-active-package",
            **kwargs,
        )

    def test_only_overflowing_source_changes_and_lineage_maps_exact_quotes(self):
        original_rows, _, _ = prepare(self.manifest_path, cfg=self.config)

        receipt = self.run_prepare()

        output_manifest = json.loads((self.destination / "manifest.json").read_text())
        by_id = {source["source_id"]: source for source in output_manifest["sources"]}
        self.assertEqual((self.destination / "raw/STABLE.json").read_bytes(), self.stable_raw)
        self.assertEqual(by_id["STABLE"]["sha256"], digest(self.stable_raw))
        self.assertEqual(by_id["BLOCKED"], {"source_id": "BLOCKED", "status": "blocked", "error": "kept"})
        self.assertNotEqual(by_id["AFFECTED"]["sha256"], digest(self.affected_raw))
        self.assertEqual((self.destination / "parents/AFFECTED.json").read_bytes(), self.affected_raw)

        lineage = by_id["AFFECTED"]["token_bounded_intake"]
        self.assertEqual(lineage["parent_snapshot_sha256"], digest(self.affected_raw))
        self.assertEqual(lineage["parent_snapshot"], "parents/AFFECTED.json")
        self.assertEqual(lineage["path_semantics"], "Paths are relative to this manifest directory.")
        self.assertEqual({item["original_passage_index"] for item in lineage["transforms"]}, {1})

        bounded_raw = json.loads((self.destination / "raw/AFFECTED.json").read_text())
        derived = bounded_raw["documents"][0]["passages"][1:-1]
        transforms = lineage["transforms"]
        self.assertEqual(len(derived), len(transforms))
        parent = json.loads(self.affected_raw)["documents"][0]["passages"][1]
        for passage, item in zip(derived, transforms):
            start, end = item["original_start"], item["original_end"]
            self.assertEqual(passage["text"], parent["text"][start:end])
            self.assertEqual(passage["offset"], parent["offset"] + start)
            self.assertEqual(item["adjusted_bioc_offset"], passage["offset"])
            self.assertEqual(item["inherited_infons"], parent["infons"])
            self.assertEqual(passage["infons"], parent["infons"])
            self.assertLessEqual(len(passage["text"]), self.config["chunk_chars"])
        self.assertEqual(transforms[0]["original_start"], 0)
        self.assertEqual(transforms[-1]["original_end"], len(self.dense_text))
        self.assertTrue(all(next_["original_start"] <= previous["original_end"]
                            for previous, next_ in zip(transforms, transforms[1:])))

        output_rows, _, _ = prepare(self.destination / "manifest.json", cfg=self.config)
        stable_before = [row for row in original_rows if row["source_id"] == "STABLE"]
        stable_after = [row for row in output_rows if row["source_id"] == "STABLE"]
        self.assertEqual(stable_after, stable_before)
        self.assertTrue(all(
            VariableDensityCounter().count(embedding_text(row, "title_content")) <= 18
            for row in output_rows
        ))
        self.assertEqual(receipt["overflow_rows_before"], 1)
        self.assertEqual(receipt["overflow_rows_after"], 0)
        self.assertEqual(receipt["affected_sources"], ["AFFECTED"])
        self.assertEqual(receipt["unchanged_source_rows_verified"], 1)

    def test_non_monotonic_token_counts_still_make_progress(self):
        self.config.update(chunk_chars=10, overlap_chars=2, embedding_text="content")
        write_json(self.config_path, self.config)
        raw = json.dumps(
            bioc("AFFECTED", "T", [("abcdxefghijklmnop", {"type": "paragraph", "section_type": "BODY"})]),
            ensure_ascii=False,
        ).encode()
        (self.intake / "raw/AFFECTED.json").write_bytes(raw)
        manifest = json.loads(self.manifest_path.read_text())
        manifest["sources"][1]["sha256"] = digest(raw)
        write_json(self.manifest_path, manifest)

        receipt = prepare_token_bounded_intake(
            self.manifest_path, self.config_path, self.destination, self.model_cache,
            token_counter=NonMonotonicCounter(), active_package=self.base / "package",
        )

        rows, _, _ = prepare(self.destination / "manifest.json", cfg=self.config)
        self.assertEqual(receipt["overflow_rows_after"], 0)
        self.assertTrue(all(NonMonotonicCounter().count(row["content"]) <= 12 for row in rows))

    def test_unsplittable_prefix_rejects_without_destination(self):
        counter = VariableDensityCounter(maximum=3)
        with self.assertRaisesRegex(ValueError, "Unsplittable embedding prefix"):
            prepare_token_bounded_intake(
                self.manifest_path, self.config_path, self.destination, self.model_cache,
                token_counter=counter, active_package=self.base / "package",
            )
        self.assertFalse(self.destination.exists())

    def test_invalid_hash_missing_and_unsafe_destinations_are_rejected(self):
        manifest = json.loads(self.manifest_path.read_text())
        manifest["sources"][0]["sha256"] = "0" * 64
        write_json(self.manifest_path, manifest)
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            self.run_prepare()
        self.assertFalse(self.destination.exists())

        self.manifest_path.unlink()
        with self.assertRaisesRegex(ValueError, "Manifest"):
            self.run_prepare()

        self.manifest_path = self.intake / "elsewhere.json"
        write_json(self.manifest_path, {"sources": []})
        self.destination.mkdir()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.run_prepare()

        self.destination.rmdir()
        real_output = self.base / "real-output"
        real_output.mkdir()
        output_link = self.base / "output-link"
        output_link.symlink_to(real_output, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            prepare_token_bounded_intake(
                self.manifest_path, self.config_path, output_link / "bounded", self.model_cache,
                token_counter=VariableDensityCounter(), active_package=self.base / "package",
            )

    def test_unsafe_source_id_is_rejected_before_writing_output(self):
        manifest = json.loads(self.manifest_path.read_text())
        manifest["sources"][0]["source_id"] = "../escape"
        write_json(self.manifest_path, manifest)
        with self.assertRaisesRegex(ValueError, "Unsafe source_id"):
            self.run_prepare()
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
