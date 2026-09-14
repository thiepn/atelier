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

V14 adds a second build layer that can add modular development code without editing the locked baseline.

### Components

- `src/v14/manifest.json` — ordered V14 styles, JavaScript modules, exact patches and passthrough assets.
- `tools/v14_build.py` — verifies the baseline lock, validates paths, applies audited exact patches, injects V14 assets at deterministic HTML anchors and emits a separate development artifact.
- `tools/test_v14_build.py` — regression tests for deterministic output, unsafe paths, duplicate markers, lock mismatches, exact-patch behavior and output replacement rules.
- `src/v14/dev-status/` — isolated development diagnostics module.
- `.github/workflows/v14-source-roundtrip.yml` — verifies the source boundary and the real V14 development artifact in CI.

### Build flow

```text
index.html (locked 13.2.0 baseline)
        │
        ├── source.lock verification
        ├── lossless source round-trip tests
        │
        ▼
tools/v14_build.py + src/v14/manifest.json
        │
        ├── apply exact, occurrence-checked bridge patches
        ├── inject styles before </head>
        ├── inject modules before </body>
        ├── preserve declared runtime assets
        │
        ▼
separate V14 development artifact
        │
        └── v14-build-manifest.json with baseline, patch and asset hashes
```

The root `index.html` is never rewritten by the V14 overlay builder.

## Exact bridge policy

V14 modules cannot directly replace functions hidden inside the legacy IIFE. `atelier-v14-exact-patch-v1` provides a controlled migration boundary:

1. Every source bridge is a complete exact-string replacement.
2. Every bridge declares its required occurrence count.
3. A missing or duplicate match fails the build instead of guessing.
4. Patch source, find string and replacement are SHA-256 recorded in the build manifest.
5. Bridged legacy functions retain their original implementation as a fallback.
6. The module must return an explicit failure signal when it cannot safely handle a call, allowing the fallback to execute.
7. Project schema, persistence and geometry are not changed merely to modularize shell behavior.

## Milestone 3 — Shell notifications

`14.0.0-dev.3` is the first real legacy-shell migration.

### Module

`src/v14/shell/notifications.js` owns post-bootstrap:

- accessibility announcements;
- toast display and timeout behavior;
- save/status text;
- error announcements.

### Bridge

`src/v14/patches/notifications-bridge.json` delegates legacy `announce`, `toast` and `status` calls to `AtelierV14Shell.notifications` when available. Their original bodies remain boot-time fallback.

### Validation

The notification service has an independent Node behavior test and CI verifies all three bridge points against the real locked baseline. Dev.3 completed successfully in workflow run `34793861206`.

## Milestone 4 — Command palette

`14.0.0-dev.4` moves command-palette presentation/search logic out of the monolith while deliberately leaving command execution unchanged.

### Module

`src/v14/shell/commands.js` owns:

- command-palette opening;
- command-label filtering;
- catalog-object search;
- the existing 24-object result cap;
- result markup and empty state;
- command-search autofocus.

### Bridge

`src/v14/patches/commands-bridge.json` delegates `commandsDialog` and `renderCommands` after module bootstrap. Existing `data-command` and `data-command-place` attributes remain unchanged, so the legacy action dispatcher continues to execute commands.

### Validation

The command service has an independent behavior test. CI verifies both exact command bridges plus both shell service suites against the real baseline. Dev.4 completed successfully in workflow run `34794079679`.

## Development diagnostics

`src/v14/dev-status/` displays network state, display mode, service-worker control state, touch-point count, viewport information and the 13.2.0 baseline identity. It is namespaced under `atelier-v14-devtools`, keyboard accessible, and explicitly labels itself as development-only.

It does not read or mutate project data, persistence, backups, geometry, catalog state or the renderer.

## Next V14 milestone

Milestone 5 should continue extracting a **pure or shell-level utility with no project-schema impact**. The preferred next boundary is file delivery/naming (`downloadFile` and `safeName`): it is centralized, independently testable, used across export/backup workflows, and can retain exact legacy fallback while removing another generic browser service from the monolith.
