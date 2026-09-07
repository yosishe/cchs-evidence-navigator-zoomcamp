"""No-download fixtures for config-driven Compose model initialization."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

from navigator.common import load_config

spec = importlib.util.spec_from_file_location("compose_setup", Path(__file__).resolve().parents[1] / "tools/prepare_compose_model.py")
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class ComposeSetupTests(unittest.TestCase):
    def test_existing_model_needs_no_download(self):
        with patch.object(setup, "model_identity", return_value={"digest": "fixture"}), patch("requests.Session") as session:
            self.assertEqual(setup.prepare_model(load_config()), {"digest": "fixture"})
            session.assert_not_called()

    def test_missing_model_without_flag_never_downloads(self):
        with patch.object(setup, "model_identity", side_effect=RuntimeError("absent")), patch("requests.Session") as session:
            with self.assertRaises(PermissionError): setup.prepare_model(load_config())
            session.assert_not_called()

    def test_mismatched_installed_weights_are_not_overwritten(self):
        with patch.object(setup, "model_identity", side_effect=ValueError("digest mismatch")), patch("requests.Session") as session:
            with self.assertRaises(ValueError): setup.prepare_model(load_config(), True)
            session.assert_not_called()

    def test_download_uses_config_model_and_requires_completed_stream_and_digest_check(self):
        cfg = {**load_config(), "model": "gemma3:12b"}
        response = Mock(); response.iter_lines.return_value = [b'{"status":"success"}']
        with patch.object(setup, "model_identity", side_effect=[RuntimeError("absent"), {"digest": "fixture"}]) as identity, patch("requests.Session") as session:
            session.return_value.post.return_value.__enter__ = Mock(return_value=response)
            session.return_value.post.return_value.__exit__ = Mock(return_value=False)
            self.assertEqual(setup.prepare_model(cfg, True), {"digest": "fixture"})
            self.assertEqual(session.return_value.post.call_args.kwargs["json"]["model"], cfg["model"])
            self.assertEqual(identity.call_count, 2)

    def test_interrupted_download_is_not_reported_ready(self):
        response = Mock(); response.iter_lines.return_value = [b'{"status":"pulling manifest"}']
        with patch.object(setup, "model_identity", side_effect=RuntimeError("absent")), patch("requests.Session") as session:
            session.return_value.post.return_value.__enter__ = Mock(return_value=response)
            session.return_value.post.return_value.__exit__ = Mock(return_value=False)
            with self.assertRaises(RuntimeError): setup.prepare_model(load_config(), True)


if __name__ == "__main__": unittest.main()
