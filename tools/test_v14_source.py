import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import v14_source


class SourceRoundTripTests(unittest.TestCase):
    def test_extract_build_roundtrip(self):
        sample = (b'<!doctype html><html><head><style>.a{color:red}</style>'
                  b'<script src="vendor.js"></script></head><body>'
                  b'<script>const x = 1 < 2;</script>'
                  b'<script type="application/json">{"x":1}</script></body></html>')
        segments = v14_source.segment_runtime(sample)
        self.assertEqual([kind for kind, _ in segments], ["html", "css", "html", "js", "html", "data", "html"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            v14_source.write_manifest(root / "index.html", source, sample, segments)
            self.assertEqual(v14_source.build_bytes(source), sample)

    def test_external_script_is_not_extracted(self):
        sample = b'<script src="a.js">ignored body</script><style>x{}</style>'
        segments = v14_source.segment_runtime(sample)
        self.assertEqual([kind for kind, _ in segments], ["html", "css", "html"])
        self.assertIn(b'ignored body', segments[0][1])

    def test_tampered_segment_is_rejected(self):
        sample = b'<style>a{}</style><script>let a=1;</script>'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            v14_source.write_manifest(root / "index.html", source, sample, v14_source.segment_runtime(sample))
            manifest = json.loads((source / "manifest.json").read_text("utf-8"))
            target = source / manifest["segments"][1]["file"]
            target.write_bytes(target.read_bytes() + b"tamper")
            with self.assertRaises(ValueError):
                v14_source.build_bytes(source)

    def test_lock_mismatch_is_rejected(self):
        data = b"abc"
        lock = {"schema": v14_source.LOCK_SCHEMA, "expectedIndexSha256": hashlib.sha256(b"other").hexdigest()}
        with self.assertRaises(ValueError):
            v14_source.verify_lock_bytes(data, lock, Path("index.html"))

    def test_literal_script_close_matches_html_boundary(self):
        sample = b'<script>const x="</script>";<style>a{}</style>'
        segments = v14_source.segment_runtime(sample)
        self.assertEqual(segments[1], ("js", b'const x="'))


if __name__ == "__main__":
    unittest.main()
