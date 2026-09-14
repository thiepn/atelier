# Atelier V14 source workspace

V14 development starts from the frozen Atelier 13.2.0 runtime but no longer treats the 1.31 MB root `index.html` as the only development representation.

## Source bootstrap

```bash
python tools/v14_source.py extract --input index.html --out src/generated --force
```

The extractor verifies `index.html` against `src/source.lock.json`, then creates lossless HTML/CSS/JS/data segments plus a manifest. Rebuilding those segments must reproduce the input byte-for-byte.

```bash
python tools/v14_source.py check --input index.html --source src/generated
```

`src/generated/` is a generated working snapshot, not an independently certified runtime. The production artifact remains `index.html` until a later V14 cutover milestone explicitly changes the build/deployment contract.

## V14 migration rule

New V14 modules should be authored under `src/v14/` and integrated through deterministic tooling. Existing monolithic code is migrated incrementally; V14 does not require a risky all-at-once rewrite.

The 13.2.0 production runtime and V13.3.1 certification records on `main` remain unchanged.
