# Atelier V14 Development Architecture

## Status

V14 is an **uncertified development cycle** on branch `v14-development`. Production remains Atelier 13.2.0 on `main`; V13.3.1 physical-device sign-off is a separate gate and is not implied by V14 development.

## Milestone 1 — Reproducible source boundary

The V13 architecture described a deterministic `src/` + `tools/` development model, while the deployed repository ultimately retained only the generated monolithic `index.html`. V14 makes that development boundary concrete without rewriting the application runtime.

### Components

- `src/source.lock.json` — pins the exact 13.2.0 runtime used as the V14 baseline.
- `tools/v14_source.py` — losslessly extracts inline HTML/CSS/JS/data segments and rebuilds them byte-for-byte.
- `tools/test_v14_source.py` — regression tests for round-trip integrity, external-script handling, tamper rejection and runtime-lock enforcement.
- `src/generated/` — reproducible local source snapshot generated from the current runtime; not required to be committed.
- `src/v14/` — home for new or migrated V14 modules.

### Milestone 1 invariants

1. V14 work does not mutate the certified/frozen production artifacts on `main`.
2. A source extraction followed by a build must reproduce `index.html` exactly.
3. Every generated segment is SHA-256 bound in its manifest.
4. The baseline lock must fail closed if the starting runtime changes unexpectedly.
5. Existing code migrates incrementally; there is no big-bang rewrite.
6. V14 development status must never be presented as V13.3.1 production certification.

## Milestone 2 — Deterministic module overlay

V14 now has a second build layer that can add modular development code without editing the locked baseline.

### Components

- `src/v14/manifest.json` — ordered V14 styles, JavaScript modules and passthrough assets.
- `tools/v14_build.py` — verifies the baseline lock, validates module paths, injects V14 assets at deterministic HTML anchors and emits a separate development artifact.
- `tools/test_v14_build.py` — regression tests for deterministic output, unsafe paths, duplicate markers, lock mismatches and output replacement rules.
- `src/v14/dev-status/` — first isolated module, used to prove the module boundary without touching project state.
- `.github/workflows/v14-source-roundtrip.yml` — verifies both the lossless source boundary and the real V14 development artifact in CI.

### Build flow

```text
index.html (locked 13.2.0 baseline)
        │
        ├── source.lock verification
        │
        ├── lossless source round-trip tests
        │
        ▼
tools/v14_build.py + src/v14/manifest.json
        │
        ├── validate module paths/assets
        ├── inject styles before </head>
        ├── inject modules before </body>
        ├── preserve declared runtime assets
        │
        ▼
separate V14 development artifact
        │
        └── v14-build-manifest.json with hashes
```

The root `index.html` is not rewritten by the V14 overlay builder.

### Development diagnostics module

The first module is intentionally low risk. It displays network state, display mode, service-worker control state, touch-point count, viewport information and the 13.2.0 baseline identity. It is namespaced under `atelier-v14-devtools`, keyboard accessible, and explicitly labels itself as development-only.

It does not read or mutate project data, persistence, backups, geometry, catalog state or the renderer.

## Next V14 milestone

Milestone 3 should use the now-tested module boundary for the first **real application-shell extraction or replacement**. Candidate code must be low-risk, independently testable and outside core project persistence/geometry. The preferred next target is a shell-level interaction such as command/help infrastructure, non-project notifications/status handling, or another isolated application-shell service that can be introduced alongside the legacy implementation before cutover.
