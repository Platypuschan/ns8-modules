"""Regression checks for the release selection and published/local distinction."""

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("quality", SCRIPTS / "check-quality.py")
quality = importlib.util.module_from_spec(spec)
spec.loader.exec_module(quality)


class QualityTests(unittest.TestCase):
    def test_catalog_listing_assets_and_metadata_meet_local_criteria(self):
        entries = quality.local_entries(SCRIPTS.parent / "apps", [])
        for entry in entries:
            with self.subTest(app=entry["id"]):
                result = quality.checks(entry, {})
                for criterion in ("categories", "logo", "screenshots", "description", "translations", "docs"):
                    self.assertTrue(result[criterion], criterion)

    def test_stable_labels_take_precedence_over_newer_testing(self):
        entry = {"versions": [
            {"tag": "2.0.0-testing.1", "labels": {"org.nethserver.min-core": "3.23.0"}},
            {"tag": "1.0.0", "labels": {}},
        ]}
        self.assertEqual(quality.displayed_version(entry)["tag"], "1.0.0")
        self.assertFalse(quality.checks(entry, {})["min_core"])

    def test_highest_testing_is_used_when_there_is_no_stable(self):
        entry = {"versions": [{"tag": t} for t in ["dev", "1.0.0-testing.2", "1.0.0-testing.10"]]}
        self.assertEqual(quality.displayed_version(entry)["tag"], "1.0.0-testing.10")

    def test_description_boundary_and_all_categories(self):
        entry = {"description": {"en": "x" * 59}, "categories": ["security", "custom"]}
        self.assertFalse(quality.checks(entry, {})["description"])
        self.assertFalse(quality.checks(entry, {})["categories"])
        entry["description"]["en"] += "x"
        entry["categories"].pop()
        self.assertTrue(quality.checks(entry, {})["description"])
        self.assertTrue(quality.checks(entry, {})["categories"])

    def test_local_assets_do_not_invent_published_image_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            app = root / "example"
            app.mkdir()
            (app / "metadata.json").write_text(json.dumps({"description": {"en": "x" * 60}}))
            (app / "logo.png").write_bytes(b"not a PNG")
            (app / "screenshots").mkdir()
            (app / "screenshots/example.png").write_bytes(quality.PNG)
            entry = quality.local_entries(root, [{"id": "example", "versions": [{"tag": "1.0.0", "labels": {}}]}])[0]
            result = quality.checks(entry, {})
            self.assertFalse(result["logo"])
            self.assertTrue(result["screenshots"])
            self.assertFalse(result["min_core"])


if __name__ == "__main__":
    unittest.main()
