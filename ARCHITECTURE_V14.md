# Atelier V14 Development Architecture

## Status

V14 is an **uncertified development cycle** on branch `v14-development`. The current checkpoint is **14.0.0-dev.7**. Production remains Atelier 13.2.0 on `main`; V13.3.1 physical-device sign-off is a separate gate and is not implied by V14 development.

## Milestone 1 — Reproducible source boundary

The V13 architecture described a deterministic `src/` + `tools/` development model, while the deployed repository ultimately retained only the generated monolithic `index.html`. V14 makes that development boundary concrete without rewriting the application runtime.

### Components

- `src/source.lock.json` — pins the exact 13.2.0 runtime used as the V14 baseline.
- `tools/v14_source.py` — losslessly extracts inline HTML/CSS/JS/data segments and rebuilds them byte-for-byte.
- `tools/test_v14_source.py` — regression tests for round-trip integrity, external-script handling, tamper rejection and runtime-lock enforcement.
- `src/generated/` — reproducible local source snapshot generated from the current runtime; not required to be committed.
- `src/v14/` — home for new or migrated V14 modules.

### Milestone 1 invariants

1. V14 work does not mutate the frozen production artifacts on `main`.
2. A source extraction followed by a build must reproduce `index.html` exactly.
3. Every generated segment is SHA-256 bound in its manifest.
4. The baseline lock fails closed if the starting runtime changes unexpectedly.
5. Existing code migrates incrementally; there is no big-bang rewrite.
6. V14 development status must never be presented as V13.3.1 production certification.

## Milestone 2 — Deterministic module overlay

V14 adds a second build layer that can add modular development code without editing the locked baseline.

### Components

- `src/v14/manifest.json` — ordered V14 styles, JavaScript modules, exact patches and passthrough assets.
- `tools/v14_build.py` — verifies the baseline lock, validates paths, applies audited exact patches, injects V14 assets at deterministic HTML anchors and emits a separate development artifact.
- `tools/test_v14_build.py` — regression tests for deterministic output, unsafe paths, duplicate markers, lock mismatches, exact-patch behavior and output replacement rules.
- `src/v14/dev-status/` — isolated development diagnostics module.
- `.github/workflows/v14-source-roundtrip.yml` — verifies the source boundary, modules, bridges and generated artifact in CI.

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
        ├── v14-build-manifest.json
        └── automated browser smoke gate
```

The root `index.html` is never rewritten by the V14 overlay builder.

## Exact bridge policy

V14 modules cannot directly replace functions hidden inside the legacy IIFE. `atelier-v14-exact-patch-v1` provides a controlled migration boundary:

1. Every source bridge is a complete exact-string replacement.
2. Every bridge declares its required occurrence count.
3. A missing or duplicate match fails the build instead of guessing.
4. Patch source, find string and replacement are SHA-256 recorded in the build manifest.
5. Bridged legacy functions retain their original implementation as fallback.
6. A module returns an explicit failure signal when it cannot safely handle a call, allowing the fallback to execute.
7. IIFE-owned state is passed through narrow adapters rather than exposed globally.
8. Project schema, persistence and geometry are not changed merely to modularize shell behavior.

## Milestone 3 — Shell notifications

`14.0.0-dev.3` is the first real legacy-shell migration.

`src/v14/shell/notifications.js` owns post-bootstrap accessibility announcements, toast display/lifetime, save/status text and error announcements. `src/v14/patches/notifications-bridge.json` delegates legacy `announce`, `toast` and `status` calls when the module is available while retaining their original bodies as fallback.

Dev.3 completed successfully in workflow run `34793861206`.

## Milestone 4 — Command palette

`14.0.0-dev.4` moves command-palette presentation/search logic out of the monolith while deliberately leaving command execution unchanged.

`src/v14/shell/commands.js` owns palette opening, command-label filtering, catalog search, the existing 24-object result cap, result markup, empty state and search autofocus. Existing `data-command` and `data-command-place` attributes remain unchanged, so the legacy action dispatcher continues to execute commands.

Dev.4 completed successfully in workflow run `34794079679`.

## Milestone 5 — Browser file utilities

`14.0.0-dev.5` moves generic browser file delivery and filename normalization behind `src/v14/shell/files.js`.

The service preserves existing behavior for Blob reuse/creation, MIME types, temporary download anchors, 1000 ms object-URL revocation and 80-character lowercase safe filenames. `downloadFile` and `safeName` remain available as exact legacy fallback through `src/v14/patches/files-bridge.json`.

Dev.5 completed successfully in workflow run `34794229852`.

## Milestone 6 — Dialog shell

`14.0.0-dev.6` migrates generic modal behavior into `src/v14/shell/dialogs.js`.

The module owns modal title/kicker/content rendering, wide state, `aria-modal`, `showModal()`, preferred initial focus, close behavior, focus restoration and confirmation-dialog composition. Application state such as `exportBusy`, `modalReturn` and `confirmCallback` remains private to the legacy IIFE and is exposed only through narrow bridge adapters.

Dev.6 completed successfully in workflow run `34794378836`.

## Milestone 7 — Real-browser shell integration

`14.0.0-dev.7` changes the quality gate rather than adding another arbitrary shell extraction.

### Browser gate

`tools/v14-shell-smoke.spec.js` launches the generated V14 artifact in Chromium and verifies the real integration path:

- all V14 shell services register;
- the development diagnostics surface is present;
- `Ctrl+K` travels through Atelier's existing keyboard handler;
- the legacy command bridge opens the modular dialog shell;
- command-search autofocus works;
- `Export deliverables` resolves to the preserved `data-command="export"` action contract;
- the existing dialog close-action path closes the modal;
- the notification service updates the real toast surface;
- filename normalization works in-browser;
- uncaught page errors and console errors remain zero.

The final dev.7 CI run `34794583346` passed the full source/build/unit/behavior pipeline plus this browser integration smoke.

### CI hardening

The V14 workflow is now manifest-driven:

- development version, style list, module list and patch sources are read from `src/v14/manifest.json`;
- artifact names are derived from the manifest version;
- superseded runs on the same branch are cancelled;
- Markdown-only changes do not reinstall Chromium or rerun the development artifact suite.

This removes duplicated milestone metadata from the workflow and reduces unnecessary CI work.

## Development diagnostics

`src/v14/dev-status/` displays network state, display mode, service-worker controller state, touch-point count, viewport information and the 13.2.0 baseline identity. It is namespaced under `atelier-v14-devtools`, keyboard accessible and explicitly labels itself as development-only.

It does not read or mutate project data, persistence, backups, geometry, catalog state or renderer state.

## Current modular shell boundary

As of dev.7, V14 modularizes four generic shell services:

1. notifications;
2. dialogs;
3. command-palette presentation/search;
4. browser file utilities.

Command execution, project persistence, backup semantics, project schema, geometry, catalog ownership and rendering remain legacy-owned.

## Next V14 milestone

**Milestone 8 should harden cross-browser and responsive integration before extracting another stateful subsystem.** Recommended scope:

- run generated-artifact browser smoke at desktop and mobile viewport sizes;
- add Firefox and WebKit automated integration where stable;
- verify keyboard focus/escape behavior and shell accessibility in the integrated artifact;
- check offline/PWA behavior of the generated development artifact without claiming physical-device certification;
- only after that gate is stable, choose the next legacy subsystem based on isolation and testability rather than extraction count.
