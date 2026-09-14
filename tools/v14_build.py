#!/usr/bin/env python3
"""Build an isolated Atelier V14 development artifact from the locked runtime baseline."""
from __future__ import annotations

import argparse
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
    return {**data, "styles": styles, "modules": modules, "patches": patches, "passthrough": passthrough}


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

    # Insert at the later anchor first so the original head offset remains valid.
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
            f"assets={len(result['assets'])}"
        )
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
