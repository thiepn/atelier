import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import v14_build


class V14BuildTests(unittest.TestCase):
    def fixture(self, root: Path, baseline: bytes = b"<html><head></head><body><script>function legacy(){return 1;}</script><main>Atelier</main></body></html>"):
        (root / "src/v14/dev-status").mkdir(parents=True)
        (root / "src/v14/patches").mkdir(parents=True)
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
        worker = (
            "const CACHE='atelier-space-studio-13.2.0';\n"
            "const RELEASE='13.2.0';\n"
            "const CORE=['./','./index.html','./asset.txt'];\n"
            "async function one(){const keys=await caches.keys();return keys.filter(k=>k.startsWith('atelier-space-studio-')&&k!==CACHE);}\n"
            "async function two(){const keys=await caches.keys();return keys.filter(k=>k.startsWith('atelier-space-studio-')&&k!==CACHE);}\n"
            "self.addEventListener('fetch',event=>{\n"
            " if(event.request.method!=='GET')return;\n"
            " event.respondWith((async()=>{\n"
            "   const cached=await caches.match(event.request);\n"
            "   if(cached)return cached;\n"
            "   try{const response=await fetch(event.request);return response;}catch{\n"
            "     if(event.request.mode==='navigate')return (await caches.match('./index.html'))||(await caches.match('./'))||Response.error();\n"
            "     return Response.error();\n"
            "   }\n"
            " })());\n"
            "});\n"
        )
        (root / "sw.js").write_text(worker, "utf-8")
        manifest = {
            "schema": "atelier-v14-module-manifest-v1",
            "version": "14.0.0-dev.8",
            "styles": ["dev-status/dev-status.css"],
            "modules": ["dev-status/dev-status.js"],
            "patches": [],
            "passthrough": ["asset.txt"],
            "serviceWorker": {
                "source": "sw.js",
                "output": "sw.js",
                "expectedSourceSha256": hashlib.sha256(worker.encode("utf-8")).hexdigest(),
                "baselineCachePrefix": "atelier-space-studio-",
                "cachePrefix": "atelier-v14-dev-",
                "ownCacheLookupOnly": True,
            },
        }
        manifest_path = root / "src/v14/manifest.json"
        manifest_path.write_text(json.dumps(manifest), "utf-8")
        return manifest_path

    def add_patch(self, manifest: Path, *, find="function legacy(){return 1;}", replace="function legacy(){return 2;}", expected=1):
        patch = manifest.parent / "patches/test.json"
        patch.write_text(json.dumps({
            "schema": "atelier-v14-exact-patch-v1",
            "id": "test-bridge",
            "changes": [{"id": "legacy", "find": find, "replace": replace, "expectedOccurrences": expected}],
        }), "utf-8")
        data = json.loads(manifest.read_text("utf-8"))
        data["patches"] = ["patches/test.json"]
        manifest.write_text(json.dumps(data), "utf-8")

    def test_deterministic_build_and_injection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            a = v14_build.build(root, manifest, root / "out-a")
            b = v14_build.build(root, manifest, root / "out-b")
            self.assertEqual(a["artifact"]["indexSha256"], b["artifact"]["indexSha256"])
            self.assertEqual(a["serviceWorker"]["outputSha256"], b["serviceWorker"]["outputSha256"])
            html = (root / "out-a/index.html").read_text("utf-8")
            self.assertIn('href="v14/dev-status/dev-status.css"', html)
            self.assertIn('src="v14/dev-status/dev-status.js"', html)
            self.assertEqual((root / "out-a/v14/dev-status/dev-status.js").read_text("utf-8"), "console.log('v14');\n")
            self.assertEqual((root / "out-a/asset.txt").read_text("utf-8"), "asset\n")

    def test_service_worker_isolated_and_offline_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            result = v14_build.build(root, manifest, root / "out")
            worker = (root / "out/sw.js").read_text("utf-8")
            record = result["serviceWorker"]
            self.assertIn("const CACHE='atelier-v14-dev-14.0.0-dev.8';", worker)
            self.assertIn("const RELEASE='14.0.0-dev.8';", worker)
            self.assertIn('./v14/dev-status/dev-status.css', worker)
            self.assertIn('./v14/dev-status/dev-status.js', worker)
            self.assertNotIn("k.startsWith('atelier-space-studio-')", worker)
            self.assertEqual(worker.count("k.startsWith('atelier-v14-dev-')"), 2)
            self.assertNotIn("caches.match(", worker)
            self.assertIn("const cache=await caches.open(CACHE);", worker)
            self.assertIn("cache.match(event.request)", worker)
            self.assertIn("cache.match('./index.html')", worker)
            self.assertIn("cache.match('./')", worker)
            self.assertEqual(record["cache"], "atelier-v14-dev-14.0.0-dev.8")
            self.assertEqual(record["stalePrefixReplacements"], 2)
            self.assertTrue(record["ownCacheLookupOnly"])
            self.assertEqual(record["cacheLookupIsolationReplacements"], 3)
            self.assertIn('./v14/dev-status/dev-status.css', record["core"])
            self.assertIn('./v14/dev-status/dev-status.js', record["core"])

    def test_service_worker_requires_own_cache_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            data = json.loads(manifest.read_text("utf-8"))
            data["serviceWorker"]["ownCacheLookupOnly"] = False
            manifest.write_text(json.dumps(data), "utf-8")
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, root / "out")

    def test_service_worker_rejects_changed_cache_lookup_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            worker_path = root / "sw.js"
            worker = worker_path.read_text("utf-8").replace(
                "const cached=await caches.match(event.request);",
                "const cached=await customCache.match(event.request);",
            )
            worker_path.write_text(worker, "utf-8")
            data = json.loads(manifest.read_text("utf-8"))
            data["serviceWorker"]["expectedSourceSha256"] = hashlib.sha256(worker.encode("utf-8")).hexdigest()
            manifest.write_text(json.dumps(data), "utf-8")
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, root / "out")

    def test_service_worker_source_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            (root / "sw.js").write_text("changed", "utf-8")
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, root / "out")

    def test_service_worker_output_cannot_be_passthrough(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            data = json.loads(manifest.read_text("utf-8"))
            data["passthrough"].append("sw.js")
            manifest.write_text(json.dumps(data), "utf-8")
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, root / "out")

    def test_exact_patch_applied_and_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            self.add_patch(manifest)
            result = v14_build.build(root, manifest, root / "out")
            html = (root / "out/index.html").read_text("utf-8")
            self.assertNotIn("function legacy(){return 1;}", html)
            self.assertIn("function legacy(){return 2;}", html)
            self.assertEqual(result["patches"][0]["id"], "test-bridge")
            self.assertEqual(result["patches"][0]["changes"][0]["occurrences"], 1)

    def test_patch_occurrence_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.fixture(root)
            self.add_patch(manifest, find="missing()", replace="replacement()")
            with self.assertRaises(ValueError):
                v14_build.build(root, manifest, root / "out")

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
