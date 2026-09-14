#!/usr/bin/env python3
"""Deterministically extract Atelier's single-file deployment artifact into development sources.

This tool is intentionally byte-preserving. It never reformats HTML, CSS, or JavaScript.
The current deployment artifact remains authoritative until a later V14 milestone explicitly
changes that relationship.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import unicodedata
from pathlib import Path

STYLE_TOKEN = b"{{ATELIER_STYLES}}"
RUNTIME_TOKEN = b"{{ATELIER_RUNTIME}}"
MARKER_RE = re.compile(rb"(?m)^// === (.+?) ===\r?$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def slug(label: str) -> str:
    text = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "module"


def unique_module_name(order: int, label: str, used: set[str]) -> str:
    base = f"{order:02d}-{slug(label)}"
    name = base
    suffix = 2
    while name in used:
        name = f"{base}-{suffix}"
        suffix += 1
    used.add(name)
    return name + ".js"


def require_single(haystack: bytes, needle: bytes, label: str) -> int:
    first = haystack.find(needle)
    if first < 0:
        raise SystemExit(f"Missing {label}: {needle!r}")
    if haystack.find(needle, first + len(needle)) >= 0:
        raise SystemExit(f"Expected exactly one {label}: {needle!r}")
    return first


def extract(index_path: Path, src_dir: Path, *, clean: bool = True) -> dict:
    raw = index_path.read_bytes()
    if STYLE_TOKEN in raw or RUNTIME_TOKEN in raw:
        raise SystemExit("Deployment artifact already contains source placeholders.")

    style_open = require_single(raw, b"<style>", "inline style block")
    style_close = require_single(raw, b"</style>", "inline style closing tag")
    script_open = require_single(raw, b"<script>", "inline runtime script")
    script_close = require_single(raw, b"</script>", "inline runtime script closing tag")

    css_start = style_open + len(b"<style>")
    css_end = style_close
    js_start = script_open + len(b"<script>")
    js_end = script_close

    if not (style_open < css_start <= css_end < script_open < js_start <= js_end):
        raise SystemExit("Unexpected style/script ordering in index.html")

    css = raw[css_start:css_end]
    runtime = raw[js_start:js_end]
    shell = raw[:css_start] + STYLE_TOKEN + raw[css_end:js_start] + RUNTIME_TOKEN + raw[js_end:]

    markers = list(MARKER_RE.finditer(runtime))
    if not markers:
        raise SystemExit("No logical runtime module markers were found.")

    runtime_dir = src_dir / "runtime"
    if clean and src_dir.exists():
        for child in (src_dir / "runtime",):
            if child.exists():
                shutil.rmtree(child)
    runtime_dir.mkdir(parents=True, exist_ok=True)

    (src_dir / "shell.html").write_bytes(shell)
    styles_dir = src_dir / "styles"
    styles_dir.mkdir(parents=True, exist_ok=True)
    (styles_dir / "app.css").write_bytes(css)

    modules: list[dict] = []
    used: set[str] = set()

    preamble = runtime[: markers[0].start()]
    if preamble:
        path = "runtime/00-preamble.js"
        (src_dir / path).write_bytes(preamble)
        modules.append(
            {
                "order": 0,
                "label": "preamble",
                "path": path,
                "bytes": len(preamble),
                "sha256": sha256(preamble),
            }
        )

    for index, marker in enumerate(markers, start=1):
        end = markers[index].start() if index < len(markers) else len(runtime)
        chunk = runtime[marker.start():end]
        label = marker.group(1).decode("utf-8")
        filename = unique_module_name(index, label, used)
        path = f"runtime/{filename}"
        (src_dir / path).write_bytes(chunk)
        modules.append(
            {
                "order": index,
                "label": label,
                "path": path,
                "bytes": len(chunk),
                "sha256": sha256(chunk),
            }
        )

    manifest = {
        "schema": "atelier-source-modules-v14-bootstrap-1",
        "sourceArtifact": index_path.as_posix(),
        "sourceArtifactBytes": len(raw),
        "sourceArtifactSha256": sha256(raw),
        "shell": {
            "path": "shell.html",
            "bytes": len(shell),
            "sha256": sha256(shell),
            "styleToken": STYLE_TOKEN.decode(),
            "runtimeToken": RUNTIME_TOKEN.decode(),
        },
        "styles": {
            "path": "styles/app.css",
            "bytes": len(css),
            "sha256": sha256(css),
        },
        "runtime": {
            "bytes": len(runtime),
            "sha256": sha256(runtime),
            "markerCount": len(markers),
            "modules": modules,
        },
    }
    (src_dir / "modules.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="index.html", type=Path)
    parser.add_argument("--src", default="src", type=Path)
    parser.add_argument("--no-clean", action="store_true")
    args = parser.parse_args()

    manifest = extract(args.index, args.src, clean=not args.no_clean)
    print(
        "EXTRACT_OK=true "
        f"modules={len(manifest['runtime']['modules'])} "
        f"index_sha256={manifest['sourceArtifactSha256']}"
    )


if __name__ == "__main__":
    main()
