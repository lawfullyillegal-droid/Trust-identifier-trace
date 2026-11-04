import json
import tempfile
import unittest
from pathlib import Path
from scripts.incrimination_nation import build


class IncriminationNationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "intake.json"

    def generate(self, payload):
        self.path.write_text(json.dumps(payload), encoding="utf-8")
        return build(self.path)

    def test_empty_is_truthful(self):
        result = self.generate({"sources": [], "claims": [], "links": []})
        self.assertEqual(result["counts"], {"sources": 0, "claims": 0, "links": 0})
        self.assertNotIn("sample_data", json.dumps(result))

    def test_private_entries_are_not_exported(self):
        result = self.generate({"sources": [{"public": False, "id": "secret", "title": "test"}],
                                "claims": [], "links": []})
        self.assertEqual(result["sources"], [])

    def test_hashed_local_source_and_supported_relation(self):
        (Path(self.temp.name) / "source.txt").write_text("Public source bytes")
        source = {"id": "court-1", "title": "Public docket", "url": "https://example.gov/case",
                  "local_path": "source.txt", "public": True}
        claim = {"id": "claim-1", "statement": "A filing is listed", "source_ids": ["court-1"],
                 "status": "documented", "public": True}
        result = self.generate({"sources": [source], "claims": [claim], "links": []})
        self.assertEqual(result["sources"][0]["verification"], "local_bytes_hashed")
        self.assertEqual(len(result["sources"][0]["sha256"]), 64)
        self.assertNotIn("local_path", json.dumps(result))

    def test_rejects_unsupported_link(self):
        with self.assertRaises(ValueError):
            self.generate({"sources": [], "claims": [], "links": [{"from": "a", "to": "b", "public": True}]})

    def test_rejects_private_identifier(self):
        with self.assertRaises(ValueError):
            self.generate({"sources": [{"public": True, "id": "x", "title": "SSN 123-45-6789", "url": "https://example.gov"}]})

    def test_committed_manifest_cannot_contain_private_entries(self):
        public = Path(self.temp.name) / "public_records"
        public.mkdir()
        path = public / "intake.json"
        path.write_text(json.dumps({"sources": [{"id": "secret", "public": False}], "claims": [], "links": []}))
        with self.assertRaises(ValueError):
            build(path)

    def test_rejects_non_https(self):
        with self.assertRaises(ValueError):
            self.generate({"sources": [{"public": True, "id": "x", "title": "Test", "url": "http://example.gov"}]})


if __name__ == "__main__":
    unittest.main()
