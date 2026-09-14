#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "tools" / "extract_source_modules.py"
BUILD = ROOT / "tools" / "build_single_file.py"

SAMPLE = b"""<!doctype html>\n<html><head><style>body{color:red}\n.x{display:grid}</style></head>\n<body><main>Atelier</main><script>(()=>{\n'use strict';\n\n// === foundation ===\nconst a=1;\n\n// === app ===\nwindow.a=a;\n})();</script></body></html>\n"""


def run(*args: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(result.returncode)
    return result


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        index = base / "index.html"
        src = base / "src"
        rebuilt = base / "rebuilt.html"
        index.write_bytes(SAMPLE)

        run(str(EXTRACT), "--index", str(index), "--src", str(src))
        result = run(str(BUILD), "--src", str(src), "--output", str(rebuilt), "--verify-index", str(index), "--verify-extracted-hashes")

        if rebuilt.read_bytes() != SAMPLE:
            raise SystemExit("Synthetic source pipeline did not round-trip exactly.")
        if "BUILD_MATCH=true" not in result.stdout:
            raise SystemExit("Builder did not report an exact match.")

    print("SOURCE_PIPELINE_SELFTEST=true")


if __name__ == "__main__":
    main()
