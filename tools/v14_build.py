#!/usr/bin/env python3
"""Build an isolated Atelier V14 development artifact from the locked runtime baseline."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path, PurePosixPath
from typing import Any

import v14_source

MODULE_SCHEMA = "atelier-v14-module-manifest-v1"
PATCH_SCHEMA = "atelier-v14-exact-patch-v1"
BUILD_SCHEMA = "atelier-v14-development-build-v1"
STYLE_BEGIN = b"<!-- ATELIER_V14_STYLES:BEGIN -->"
STYLE_END = b"<!-- ATELIER_V14_STYLES:END -->"
MODULE_BEGIN = b"<!-- ATELIER_V14_MODULES:BEGIN -->"
MODULE_END = b"<!-- ATELIER_V14_MODULES:END -->"
SAFE_PATH = re.compile(r"^[A-Za-z0-9._/-]+$")
SAFE_CACHE_PREFIX = re.compile(r"^[A-Za-z0-9._-]+$")
SHA256_HEX = re.compile(r"^[0-9a-f]{64}$")
CACHE_DECL_RE = re.compile(rb"const CACHE='[^'\r\n]+';")
RELEASE_DECL_RE = re.compile(rb"const RELEASE='[^'\r\n]+';")
CORE_DECL_RE = re.compile(rb"const CORE=\[[^\r\n]*\];")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text("utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return data


def validate_relative_asset(value: str, expected_suffix: str | None = None) -> str:
    if not isinstance(value, str) or not value or not SAFE_PATH.fullmatch(value):
        raise ValueError(f"Unsafe asset path: {value!r}")
    posix = PurePosixPath(value)
    if posix.is_absolute() or ".." in posix.parts or "." in posix.parts:
        raise ValueError(f"Unsafe asset path: {value!r}")
    normalized = posix.as_posix()
    if expected_suffix and not normalized.lower().endswith(expected_suffix):
        raise ValueError(f"Expected {expected_suffix} asset, got: {value}")
    return normalized


def normalize_service_worker(value: Any, passthrough: list[str]) -> dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError("serviceWorker must be an object")
    source = validate_relative_asset(value.get("source"), ".js")
    output = validate_relative_asset(value.get("output", source), ".js")
    expected = value.get("expectedSourceSha256")
    if not isinstance(expected, str) or not SHA256_HEX.fullmatch(expected):
        raise ValueError("serviceWorker.expectedSourceSha256 must be a lowercase SHA-256 hex digest")
    baseline_prefix = value.get("baselineCachePrefix", "atelier-space-studio-")
    cache_prefix = value.get("cachePrefix", "atelier-v14-dev-")
    for label, prefix in (("baselineCachePrefix", baseline_prefix), ("cachePrefix", cache_prefix)):
        if not isinstance(prefix, str) or not prefix or not SAFE_CACHE_PREFIX.fullmatch(prefix):
            raise ValueError(f"Unsafe serviceWorker.{label}: {prefix!r}")
    if baseline_prefix == cache_prefix:
        raise ValueError("V14 service-worker cache prefix must be isolated from the baseline prefix")
    if value.get("ownCacheLookupOnly") is not True:
        raise ValueError("serviceWorker.ownCacheLookupOnly must be true")
    if output in passthrough:
        raise ValueError(f"Generated service worker output must not also be passthrough: {output}")
    return {
        "source": source,
        "output": output,
        "expectedSourceSha256": expected,
        "baselineCachePrefix": baseline_prefix,
        "cachePrefix": cache_prefix,
        "ownCacheLookupOnly": True,
    }


def load_module_manifest(path: Path) -> dict[str, Any]:
    data = load_json(path)
    if data.get("schema") != MODULE_SCHEMA:
        raise ValueError(f"Unsupported V14 module manifest schema: {data.get('schema')!r}")
    version = data.get("version")
    if not isinstance(version, str) or not version.strip():
        raise ValueError("V14 module manifest requires a non-empty version")
    styles = [validate_relative_asset(x, ".css") for x in data.get("styles", [])]
    modules = [validate_relative_asset(x, ".js") for x in data.get("modules", [])]
    patches = [validate_relative_asset(x, ".json") for x in data.get("patches", [])]
    passthrough = [validate_relative_asset(x) for x in data.get("passthrough", [])]
    for label, values in (("style", styles), ("module", modules), ("patch", patches), ("passthrough", passthrough)):
        if len(values) != len(set(values)):
            raise ValueError(f"Duplicate V14 {label} asset in manifest")
    service_worker = normalize_service_worker(data.get("serviceWorker"), passthrough)
    return {
        **data,
        "styles": styles,
        "modules": modules,
        "patches": patches,
        "passthrough": passthrough,
        "serviceWorker": service_worker,
    }


def apply_patch_file(data: bytes, patch_path: Path, relative: str) -> tuple[bytes, dict[str, Any]]:
    raw = patch_path.read_bytes()
    patch = json.loads(raw.decode("utf-8"))
    if not isinstance(patch, dict) or patch.get("schema") != PATCH_SCHEMA:
        schema = patch.get("schema") if isinstance(patch, dict) else None
        raise ValueError(f"Unsupported V14 patch schema in {patch_path}: {schema!r}")
    patch_id = patch.get("id")
    changes = patch.get("changes")
    if not isinstance(patch_id, str) or not patch_id.strip():
        raise ValueError(f"Patch requires a non-empty id: {patch_path}")
    if not isinstance(changes, list) or not changes:
        raise ValueError(f"Patch requires at least one change: {patch_path}")

    applied: list[dict[str, Any]] = []
    output = data
    for index, change in enumerate(changes):
        if not isinstance(change, dict):
            raise ValueError(f"Patch change #{index} must be an object: {patch_path}")
        change_id = change.get("id", f"change-{index + 1}")
        find = change.get("find")
        replace = change.get("replace")
        expected = change.get("expectedOccurrences", 1)
        if not isinstance(find, str) or not find:
            raise ValueError(f"Patch change {change_id!r} has an empty find string")
        if not isinstance(replace, str):
            raise ValueError(f"Patch change {change_id!r} replacement must be a string")
        if not isinstance(expected, int) or expected < 1:
            raise ValueError(f"Patch change {change_id!r} expectedOccurrences must be >= 1")
        find_bytes = find.encode("utf-8")
        replace_bytes = replace.encode("utf-8")
        count = output.count(find_bytes)
        if count != expected:
            raise ValueError(
                f"Patch {patch_id}/{change_id} expected {expected} occurrence(s), found {count}; "
                "refusing a non-deterministic patch"
            )
        output = output.replace(find_bytes, replace_bytes, expected)
        applied.append({
            "id": str(change_id),
            "occurrences": count,
            "findSha256": sha256(find_bytes),
            "replaceSha256": sha256(replace_bytes),
        })

    return output, {
        "id": patch_id,
        "source": relative,
        "sourceSha256": sha256(raw),
        "changes": applied,
    }


def apply_patches(data: bytes, source_root: Path, patches: list[str]) -> tuple[bytes, list[dict[str, Any]]]:
    output = data
    records: list[dict[str, Any]] = []
    for relative in patches:
        path = source_root / Path(*PurePosixPath(relative).parts)
        if not path.is_file():
            raise ValueError(f"Missing V14 patch file: {path}")
        output, record = apply_patch_file(output, path, relative)
        records.append(record)
    return output, records


def inject_modules(baseline: bytes, styles: list[str], modules: list[str]) -> bytes:
    for marker in (STYLE_BEGIN, STYLE_END, MODULE_BEGIN, MODULE_END):
        if marker in baseline:
            raise ValueError("Baseline already contains a V14 injection marker")

    lower = baseline.lower()
    head_at = lower.rfind(b"</head>")
    body_at = lower.rfind(b"</body>")
    if head_at < 0 or body_at < 0 or head_at > body_at:
        raise ValueError("Baseline must contain ordered </head> and </body> anchors")

    style_lines = [STYLE_BEGIN]
    style_lines.extend(f'<link rel="stylesheet" href="v14/{path}">'.encode("utf-8") for path in styles)
    style_lines.append(STYLE_END)
    style_block = b"\n" + b"\n".join(style_lines) + b"\n"

    module_lines = [MODULE_BEGIN]
    module_lines.extend(f'<script type="module" src="v14/{path}"></script>'.encode("utf-8") for path in modules)
    module_lines.append(MODULE_END)
    module_block = b"\n" + b"\n".join(module_lines) + b"\n"

    output = baseline[:body_at] + module_block + baseline[body_at:]
    output = output[:head_at] + style_block + output[head_at:]
    return output


def copy_asset(source_root: Path, output_root: Path, relative: str, prefix: str = "v14") -> dict[str, Any]:
    source = source_root / Path(*PurePosixPath(relative).parts)
    if not source.is_file():
        raise ValueError(f"Missing V14 asset: {source}")
    payload = source.read_bytes()
    destination = output_root / prefix / Path(*PurePosixPath(relative).parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return {
        "source": source.as_posix(),
        "output": destination.relative_to(output_root).as_posix(),
        "bytes": len(payload),
        "sha256": sha256(payload),
    }


def copy_passthrough(repo_root: Path, output_root: Path, relative: str) -> dict[str, Any]:
    source = repo_root / Path(*PurePosixPath(relative).parts)
    if not source.is_file():
        raise ValueError(f"Missing passthrough asset: {source}")
    payload = source.read_bytes()
    destination = output_root / Path(*PurePosixPath(relative).parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    return {
        "source": source.relative_to(repo_root).as_posix(),
        "output": destination.relative_to(output_root).as_posix(),
        "bytes": len(payload),
        "sha256": sha256(payload),
    }


def build_service_worker(
    repo_root: Path,
    output_root: Path,
    version: str,
    styles: list[str],
    modules: list[str],
    config: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if config is None:
        return None

    source_path = repo_root / Path(*PurePosixPath(config["source"]).parts)
    if not source_path.is_file():
        raise ValueError(f"Missing service-worker source: {source_path}")
    source = source_path.read_bytes()
    actual_source_hash = sha256(source)
    if actual_source_hash != config["expectedSourceSha256"]:
        raise ValueError(
            f"Service-worker source hash mismatch: expected {config['expectedSourceSha256']}, got {actual_source_hash}"
        )

    cache_match = CACHE_DECL_RE.findall(source)
    release_match = RELEASE_DECL_RE.findall(source)
    core_match = CORE_DECL_RE.findall(source)
    if len(cache_match) != 1 or len(release_match) != 1 or len(core_match) != 1:
        raise ValueError("Service-worker source must contain exactly one CACHE, RELEASE and CORE declaration")

    core_literal = core_match[0][len(b"const CORE="):-1].decode("utf-8")
    try:
        core = ast.literal_eval(core_literal)
    except (SyntaxError, ValueError) as exc:
        raise ValueError("Unable to parse service-worker CORE list") from exc
    if not isinstance(core, list) or not all(isinstance(item, str) for item in core):
        raise ValueError("Service-worker CORE must be a flat string list")

    for path in [*styles, *modules]:
        asset = f"./v14/{path}"
        if asset not in core:
            core.append(asset)

    cache_name = f"{config['cachePrefix']}{version}"
    output = CACHE_DECL_RE.sub(f"const CACHE='{cache_name}';".encode("utf-8"), source, count=1)
    output = RELEASE_DECL_RE.sub(f"const RELEASE='{version}';".encode("utf-8"), output, count=1)
    core_js = "const CORE=" + json.dumps(core, separators=(",", ":")) + ";"
    output = CORE_DECL_RE.sub(core_js.encode("utf-8"), output, count=1)

    baseline_token = f"k.startsWith('{config['baselineCachePrefix']}')".encode("utf-8")
    isolated_token = f"k.startsWith('{config['cachePrefix']}')".encode("utf-8")
    prefix_occurrences = output.count(baseline_token)
    if prefix_occurrences < 1:
        raise ValueError("Service-worker stale-cache prefix guard was not found")
    output = output.replace(baseline_token, isolated_token)

    cache_read_replacements = 0
    request_lookup = b"const cached=await caches.match(event.request);"
    if output.count(request_lookup) != 1:
        raise ValueError("Service-worker request cache lookup boundary changed unexpectedly")
    output = output.replace(
        request_lookup,
        b"const cache=await caches.open(CACHE);\n   const cached=await cache.match(event.request);",
        1,
    )
    cache_read_replacements += 1
    for old, new in (
        (b"caches.match('./index.html')", b"cache.match('./index.html')"),
        (b"caches.match('./')", b"cache.match('./')"),
    ):
        if output.count(old) != 1:
            raise ValueError("Service-worker navigation fallback cache lookup boundary changed unexpectedly")
        output = output.replace(old, new, 1)
        cache_read_replacements += 1
    if b"caches.match(" in output:
        raise ValueError("Generated V14 service worker still contains cross-cache cache reads")

    destination = output_root / Path(*PurePosixPath(config["output"]).parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(output)
    return {
        "source": config["source"],
        "output": config["output"],
        "sourceSha256": actual_source_hash,
        "outputSha256": sha256(output),
        "release": version,
        "cache": cache_name,
        "cachePrefix": config["cachePrefix"],
        "baselineCachePrefix": config["baselineCachePrefix"],
        "stalePrefixReplacements": prefix_occurrences,
        "ownCacheLookupOnly": True,
        "cacheLookupIsolationReplacements": cache_read_replacements,
        "core": core,
    }


def build(repo_root: Path, manifest_path: Path, output_dir: Path, force: bool = False) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    manifest_path = manifest_path.resolve()
    output_dir = output_dir.resolve()

    module_manifest = load_module_manifest(manifest_path)
    baseline_path = repo_root / "index.html"
    lock_path = repo_root / "src/source.lock.json"
    baseline = baseline_path.read_bytes()
    lock = v14_source.load_lock(lock_path)
    assert lock is not None
    v14_source.verify_lock_bytes(baseline, lock, baseline_path)

    if output_dir.exists():
        if not force:
            raise ValueError(f"Output directory already exists: {output_dir}; use --force to replace it")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)

    source_root = manifest_path.parent
    patched_baseline, patch_records = apply_patches(baseline, source_root, module_manifest["patches"])

    assets: list[dict[str, Any]] = []
    for path in module_manifest["styles"]:
        assets.append(copy_asset(source_root, output_dir, path))
    for path in module_manifest["modules"]:
        assets.append(copy_asset(source_root, output_dir, path))

    passthrough: list[dict[str, Any]] = []
    for path in module_manifest["passthrough"]:
        passthrough.append(copy_passthrough(repo_root, output_dir, path))

    output_index = inject_modules(patched_baseline, module_manifest["styles"], module_manifest["modules"])
    (output_dir / "index.html").write_bytes(output_index)

    service_worker = build_service_worker(
        repo_root,
        output_dir,
        module_manifest["version"],
        module_manifest["styles"],
        module_manifest["modules"],
        module_manifest["serviceWorker"],
    )

    build_manifest = {
        "schema": BUILD_SCHEMA,
        "version": module_manifest["version"],
        "developmentOnly": True,
        "baseline": {
            "runtimeRelease": lock.get("runtimeRelease"),
            "productionCommit": lock.get("productionCommit"),
            "indexSha256": sha256(baseline),
            "bytes": len(baseline),
        },
        "patchedBaseline": {
            "indexSha256": sha256(patched_baseline),
            "bytes": len(patched_baseline),
        },
        "artifact": {
            "indexSha256": sha256(output_index),
            "bytes": len(output_index),
        },
        "patches": patch_records,
        "styles": module_manifest["styles"],
        "modules": module_manifest["modules"],
        "assets": assets,
        "passthrough": passthrough,
        "serviceWorker": service_worker,
    }
    (output_dir / "v14-build-manifest.json").write_text(json.dumps(build_manifest, indent=2) + "\n", "utf-8")
    return build_manifest


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo-root", default=".")
    p.add_argument("--manifest", default="src/v14/manifest.json")
    p.add_argument("--output-dir", default="dist")
    p.add_argument("--force", action="store_true")
    return p


def main() -> int:
    try:
        args = parser().parse_args()
        manifest = Path(args.manifest)
        if not manifest.is_absolute():
            manifest = Path(args.repo_root) / manifest
        result = build(Path(args.repo_root), manifest, Path(args.output_dir), args.force)
        print(
            "V14_BUILD_OK=true "
            f"version={result['version']} "
            f"index_sha256={result['artifact']['indexSha256']} "
            f"patches={len(result['patches'])} "
            f"assets={len(result['assets'])} "
            f"offline_core={len(result['serviceWorker']['core']) if result['serviceWorker'] else 0}"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
