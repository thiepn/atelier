#!/usr/bin/env python3
"""Lossless source segmentation for Atelier V14 development.

The production runtime remains a single index.html. This tool decomposes that file
into deterministic HTML/CSS/JS/data segments for development work and can rebuild
it byte-for-byte.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

SCHEMA = "atelier-v14-source-segments-v1"
LOCK_SCHEMA = "atelier-v14-source-lock-v1"
OPEN_TAG = re.compile(br"<(style|script)\b[^>]*>", re.IGNORECASE)
TYPE_ATTR = re.compile(br"\btype\s*=\s*([\"'])(.*?)\1", re.IGNORECASE | re.DOTALL)
SRC_ATTR = re.compile(br"\bsrc\s*=", re.IGNORECASE)
JS_TYPES = {
    b"text/javascript", b"application/javascript", b"application/ecmascript",
    b"text/ecmascript", b"module",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_lock(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    data = json.loads(path.read_text("utf-8"))
    if data.get("schema") != LOCK_SCHEMA:
        raise ValueError(f"Unsupported lock schema in {path}: {data.get('schema')!r}")
    return data


def verify_lock_bytes(data: bytes, lock: dict[str, Any], input_path: Path) -> None:
    expected = lock.get("expectedIndexSha256")
    actual = sha256(data)
    if expected and actual != expected:
        raise ValueError(
            f"Runtime hash mismatch for {input_path}: expected {expected}, got {actual}. "
            "Update the lock only after intentionally changing the runtime."
        )


def script_extension(opening_tag: bytes) -> str:
    match = TYPE_ATTR.search(opening_tag)
    if not match:
        return "js"
    value = match.group(2).strip().lower()
    return "js" if value in JS_TYPES else "data"


def segment_runtime(data: bytes) -> list[tuple[str, bytes]]:
    """Split raw HTML while preserving exact bytes and browser script/style boundaries."""
    lower = data.lower()
    segments: list[tuple[str, bytes]] = []
    cursor = 0
    search_from = 0

    while True:
        match = OPEN_TAG.search(data, search_from)
        if not match:
            break
        tag = match.group(1).lower()
        opening = data[match.start():match.end()]
        closing = b"</" + tag + b">"
        close_start = lower.find(closing, match.end())
        if close_start < 0:
            raise ValueError(f"Unclosed <{tag.decode()}> tag at byte {match.start()}")
        close_end = close_start + len(closing)

        # External scripts carry no source body we want to edit. Keep the entire block
        # in the surrounding HTML segment and continue scanning after it.
        if tag == b"script" and SRC_ATTR.search(opening):
            search_from = close_end
            continue

        # HTML includes the opening tag; extracted source is body-only; the closing tag
        # becomes part of the following HTML segment. Concatenation is therefore exact.
        html_chunk = data[cursor:match.end()]
        if html_chunk:
            segments.append(("html", html_chunk))

        body = data[match.end():close_start]
        if tag == b"style":
            segments.append(("css", body))
        else:
            segments.append((script_extension(opening), body))

        cursor = close_start
        search_from = close_end

    tail = data[cursor:]
    if tail:
        segments.append(("html", tail))
    return segments


def write_manifest(input_path: Path, out_dir: Path, data: bytes, segments: list[tuple[str, bytes]]) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for index, (kind, payload) in enumerate(segments):
        extension = {"html": "html", "css": "css", "js": "js", "data": "data"}[kind]
        filename = f"{index:04d}.{extension}"
        (out_dir / filename).write_bytes(payload)
        entries.append({
            "file": filename,
            "kind": kind,
            "bytes": len(payload),
            "sha256": sha256(payload),
        })
    manifest = {
        "schema": SCHEMA,
        "inputName": input_path.name,
        "sourceBytes": len(data),
        "sourceSha256": sha256(data),
        "segmentCount": len(entries),
        "segments": entries,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", "utf-8")
    return manifest


def load_manifest(source_dir: Path) -> dict[str, Any]:
    path = source_dir / "manifest.json"
    data = json.loads(path.read_text("utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError(f"Unsupported source manifest schema in {path}: {data.get('schema')!r}")
    return data


def build_bytes(source_dir: Path) -> bytes:
    manifest = load_manifest(source_dir)
    pieces: list[bytes] = []
    for entry in manifest["segments"]:
        path = source_dir / entry["file"]
        payload = path.read_bytes()
        actual = sha256(payload)
        if actual != entry["sha256"]:
            raise ValueError(f"Segment hash mismatch: {path} expected {entry['sha256']}, got {actual}")
        if len(payload) != entry["bytes"]:
            raise ValueError(f"Segment byte-count mismatch: {path}")
        pieces.append(payload)
    output = b"".join(pieces)
    actual = sha256(output)
    if actual != manifest["sourceSha256"]:
        raise ValueError(f"Rebuilt runtime hash mismatch: expected {manifest['sourceSha256']}, got {actual}")
    return output


def command_extract(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    out_dir = Path(args.out)
    data = input_path.read_bytes()
    lock = load_lock(Path(args.lock) if args.lock else None)
    if lock:
        verify_lock_bytes(data, lock, input_path)
    if out_dir.exists():
        if not args.force:
            raise ValueError(f"Output directory already exists: {out_dir}; use --force to replace it")
        shutil.rmtree(out_dir)
    segments = segment_runtime(data)
    manifest = write_manifest(input_path, out_dir, data, segments)
    rebuilt = build_bytes(out_dir)
    if rebuilt != data:
        raise AssertionError("Internal round-trip mismatch after extraction")
    print(f"EXTRACT_OK=true segments={manifest['segmentCount']} sha256={manifest['sourceSha256']}")


def command_build(args: argparse.Namespace) -> None:
    source_dir = Path(args.source)
    output_path = Path(args.output)
    data = build_bytes(source_dir)
    lock = load_lock(Path(args.lock) if args.lock else None)
    if lock:
        verify_lock_bytes(data, lock, output_path)
    output_path.write_bytes(data)
    print(f"BUILD_OK=true bytes={len(data)} sha256={sha256(data)}")


def command_check(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    data = input_path.read_bytes()
    lock = load_lock(Path(args.lock) if args.lock else None)
    if lock:
        verify_lock_bytes(data, lock, input_path)
    rebuilt = build_bytes(Path(args.source))
    if rebuilt != data:
        raise ValueError("CHECK_OK=false: rebuilt bytes differ from input runtime")
    print(f"CHECK_OK=true bytes={len(data)} sha256={sha256(data)}")


def command_verify_lock(args: argparse.Namespace) -> None:
    path = Path(args.input)
    data = path.read_bytes()
    lock = load_lock(Path(args.lock))
    assert lock is not None
    verify_lock_bytes(data, lock, path)
    print(f"LOCK_OK=true bytes={len(data)} sha256={sha256(data)}")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)

    ex = sub.add_parser("extract", help="Split index.html into lossless source segments")
    ex.add_argument("--input", default="index.html")
    ex.add_argument("--out", default="src/generated")
    ex.add_argument("--lock", default="src/source.lock.json")
    ex.add_argument("--force", action="store_true")
    ex.set_defaults(func=command_extract)

    bu = sub.add_parser("build", help="Rebuild index.html from source segments")
    bu.add_argument("--source", default="src/generated")
    bu.add_argument("--output", default="dist/index.html")
    bu.add_argument("--lock")
    bu.set_defaults(func=command_build)

    ch = sub.add_parser("check", help="Verify committed/generated segments round-trip to index.html")
    ch.add_argument("--input", default="index.html")
    ch.add_argument("--source", default="src/generated")
    ch.add_argument("--lock", default="src/source.lock.json")
    ch.set_defaults(func=command_check)

    vl = sub.add_parser("verify-lock", help="Verify index.html against the frozen runtime lock")
    vl.add_argument("--input", default="index.html")
    vl.add_argument("--lock", default="src/source.lock.json")
    vl.set_defaults(func=command_verify_lock)
    return p


def main() -> int:
    try:
        args = parser().parse_args()
        args.func(args)
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
