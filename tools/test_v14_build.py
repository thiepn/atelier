import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import v14_build


class V14BuildTests(unittest.TestCase):
    def fixture(self, root: Path, baseline: bytes = b"<html><head></head><body><main>Atelier</main></body></html>"):
        (root / "src/v14/dev-status").mkdir(parents=True)
        (root / "index.html").write_bytes(baseline)
        (root / "src/source.lock.json").write_text(json.dumps({
            "schema": "atelier-v14-source-lock-v1",
            "runtimeRelease": "13.2.0",
            "productionCommit": "baseline",
            "expectedIndexSha256": hashlib.sha256(baseline).hexdigest(),
        }), "utf-8")
        (root / "src/v14/dev-status/dev-status.css").write_text("#v14{display:block}\n", "utf-8")
        (root / "src/v14/dev-status/dev-status.js").write_text("console.log('v14');\n", "utf-8")
        (root / "asset.txt").write_text("asset\n", "utf-8")
        manifest = {
            "schema": "atelier-v14-module-manifest-v1",
            "version": "14.0.0-dev.2",
            "styles": ["dev-status/dev-status.css"],
            "modules": ["dev-status/dev-status.js"],
            "passthrough": ["asset.txt"],
        }
        manifest_path = root / "src/v14/manifest.json"
        manifest_path.write_text(json.dumps(manifest), "utf-8")
        return manifest_path

    def test_deterministic_build_and_injection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            a = v14_build.build(root, manifest, root / "out-a")
            b = v14_build.build(root, manifest, root / "out-b")
            self.assertEqual(a["artifact"]["indexSha256"], b["artifact"]["indexSha256"])
            html = (root / "out-a/index.html").read_text("utf-8")
            self.assertIn('href="v14/dev-status/dev-status.css"', html)
            self.assertIn('src="v14/dev-status/dev-status.js"', html)
            self.assertEqual((root / "out-a/v14/dev-status/dev-status.js").read_text("utf-8"), "console.log('v14');\n")
            self.assertEqual((root / "out-a/asset.txt").read_text("utf-8"), "asset\n")

    def test_unsafe_asset_path_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            data = json.loads(manifest.read_text("utf-8"))
            data["modules"] = ["../escape.js"]
            manifest.write_text(json.dumps(data), "utf-8")
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, root / "out")

    def test_existing_marker_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = b"<html><head><!-- ATELIER_V14_STYLES:BEGIN --></head><body></body></html>"
            manifest = self.fixture(root, baseline)
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, root / "out")

    def test_baseline_lock_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            (root / "index.html").write_text("changed", "utf-8")
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, root / "out")

    def test_existing_output_requires_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            output = root / "out"
            v14_build.build(root, manifest, output)
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, output)
            v14_build.build(root, manifest, output, force=True)


if __name__ == "__main__":
    unittest.main()
