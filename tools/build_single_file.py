#!/usr/bin/env python3
"""Rebuild Atelier's deployment index from extracted development sources."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

STYLE_TOKEN = b"{{ATELIER_STYLES}}"
RUNTIME_TOKEN = b"{{ATELIER_RUNTIME}}"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def checked_replace(data: bytes, token: bytes, value: bytes, label: str) -> bytes:
    count = data.count(token)
    if count != 1:
        raise SystemExit(f"Expected one {label} placeholder, found {count}.")
    return data.replace(token, value, 1)


def first_difference(a: bytes, b: bytes) -> int | None:
    limit = min(len(a), len(b))
    for i in range(limit):
        if a[i] != b[i]:
            return i
    return None if len(a) == len(b) else limit


def load_source(src_dir: Path) -> tuple[dict, bytes, bytes, bytes]:
    manifest_path = src_dir / "modules.json"
    if not manifest_path.exists():
        raise SystemExit("src/modules.json is missing. Run tools/extract_source_modules.py first.")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    shell_path = src_dir / manifest["shell"]["path"]
    style_path = src_dir / manifest["styles"]["path"]
    shell = shell_path.read_bytes()
    css = style_path.read_bytes()

    entries = sorted(manifest["runtime"]["modules"], key=lambda item: item["order"])
    paths = [item["path"] for item in entries]
    if len(paths) != len(set(paths)):
        raise SystemExit("Duplicate module paths in src/modules.json")
    runtime = b"".join((src_dir / path).read_bytes() for path in paths)
    return manifest, shell, css, runtime


def verify_extracted_hashes(manifest: dict, src_dir: Path, shell: bytes, css: bytes, runtime: bytes) -> None:
    failures: list[str] = []
    if sha256(shell) != manifest["shell"]["sha256"]:
        failures.append("shell.html")
    if sha256(css) != manifest["styles"]["sha256"]:
        failures.append("styles/app.css")
    if sha256(runtime) != manifest["runtime"]["sha256"]:
        failures.append("combined runtime")
    for item in manifest["runtime"]["modules"]:
        data = (src_dir / item["path"]).read_bytes()
        if sha256(data) != item["sha256"]:
            failures.append(item["path"])
    if failures:
        raise SystemExit("Extracted baseline hash mismatch: " + ", ".join(failures))


def build(src_dir: Path) -> tuple[dict, bytes]:
    manifest, shell, css, runtime = load_source(src_dir)
    built = checked_replace(shell, STYLE_TOKEN, css, "style")
    built = checked_replace(built, RUNTIME_TOKEN, runtime, "runtime")
    return manifest, built


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", default="src", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-index", nargs="?", const="index.html", type=Path)
    parser.add_argument("--verify-extracted-hashes", action="store_true")
    args = parser.parse_args()

    manifest, shell, css, runtime = load_source(args.src)
    if args.verify_extracted_hashes:
        verify_extracted_hashes(manifest, args.src, shell, css, runtime)

    built = checked_replace(shell, STYLE_TOKEN, css, "style")
    built = checked_replace(built, RUNTIME_TOKEN, runtime, "runtime")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(built)
        print(f"BUILD_OUTPUT={args.output.as_posix()} bytes={len(built)} sha256={sha256(built)}")

    if args.verify_index:
        expected = args.verify_index.read_bytes()
        if built != expected:
            offset = first_difference(built, expected)
            print("BUILD_MATCH=false")
            print(f"built_bytes={len(built)} built_sha256={sha256(built)}")
            print(f"index_bytes={len(expected)} index_sha256={sha256(expected)}")
            print(f"first_difference={offset}")
            raise SystemExit(1)
        print(f"BUILD_MATCH=true bytes={len(built)} sha256={sha256(built)}")

    if not args.output and not args.verify_index:
        print(f"BUILD_OK=true bytes={len(built)} sha256={sha256(built)}")


if __name__ == "__main__":
    main()
