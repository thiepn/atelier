# Atelier V14 Development Architecture

## Status

V14 is an **uncertified development cycle** on branch `v14-development`.

Current validated checkpoint: **14.0.0-dev.14**.

Production remains Atelier **13.2.0** on `main`. V13.3.1 physical-device sign-off remains a separate unresolved production gate.

## Architecture objective

V14 incrementally extracts small, deterministic, low-state boundaries from the locked Atelier 13.2.0 monolith while preserving exact legacy fallback behavior.

It is not a big-bang rewrite, and stabilization now explicitly prevents further ownership migration without a new architecture decision.

### Excluded by default

The following remain legacy-owned unless an explicit dependency/risk review authorizes otherwise:

- project persistence and backups;
- project schema and validation;
- geometry/precision engines;
- 2D/3D rendering;
- catalog/application state;
- broad project/orchestration helpers.

## Source and build model

The V14 development line starts from the exact production 13.2.0 runtime and creates a separate artifact.

```text
index.html (locked 13.2.0 baseline)
        │
        ├── src/source.lock.json verification
        ├── lossless extraction/rebuild check
        │
        ▼
tools/v14_build.py + src/v14/manifest.json
        │
        ├── exact occurrence-checked bridges
        ├── ordered V14 styles/modules
        ├── isolated V14 development service worker
        ├── declared passthrough assets
        │
        ▼
V14 development artifact
        │
        ├── index.html
        ├── sw.js
        ├── v14/*
        └── v14-build-manifest.json
```

The root production `index.html` and `sw.js` are source inputs only. The builder does not rewrite them.

## Exact bridge policy

`atelier-v14-exact-patch-v1` is the migration boundary for helpers hidden inside the legacy IIFE.

1. Every bridge specifies exact source text and required occurrence count.
2. Missing or duplicate matches fail the build.
3. Patch inputs and replacements are SHA-256 recorded in the build manifest.
4. Legacy function bodies remain available as fallback.
5. IIFE-owned state remains private and is exposed only through narrow adapters where required.
6. A bridge may not be added during stabilization without explicitly leaving the frozen architecture phase.

## Milestones

### dev.1 — Reproducible source boundary

Added `src/source.lock.json`, `tools/v14_source.py`, source-tool tests and a byte-for-byte extraction/rebuild invariant.

### dev.2 — Deterministic module overlay

Added the V14 module manifest, overlay builder, exact patch engine, build manifest and development diagnostics.

### dev.3 — Shell notifications

Moved accessibility announcements, toasts and save/status presentation into `shell/notifications.js`.

Validated workflow: `34793861206`.

### dev.4 — Command palette

Moved command-palette opening/search/result presentation into `shell/commands.js`. Legacy command execution remains unchanged.

Validated workflow: `34794079679`.

### dev.5 — Browser file utilities

Moved generic download delivery and safe filename normalization into `shell/files.js`.

Validated workflow: `34794229852`.

### dev.6 — Dialog shell

Moved modal DOM behavior, focus handling and confirmation composition into `shell/dialogs.js` through narrow legacy-state adapters.

Validated workflow: `34794378836`.

### dev.7 — Real-browser shell integration

Added generated-artifact Chromium integration and made CI manifest-driven/concurrency-safe.

Validated workflow: `34794583346`.

### dev.8 — Cross-browser, responsive and offline integration

Added four Playwright projects:

1. Chromium desktop — 1280×800
2. Chromium mobile/touch — 390×844
3. Firefox desktop — 1280×800
4. WebKit desktop — 1280×800

The integrated gate verifies responsive overflow, keyboard paths, native dialog Escape, focus restoration, accessible command search, service registration and zero uncaught page/console errors.

Validated workflow: `34815078492`.

### dev.9 — SVG icon renderer

Moved pure SVG serialization into `shell/icons.js`. The immutable path registry remains legacy-owned and is passed into the renderer by the bridge.

Validated workflow: `34815530617`.

### dev.10 — Text escaping

Centralized repeated HTML/SVG/XML escaping in `shell/text.js` while preserving the existing `&#39;` versus `&apos;` contracts through four exact fallback bridges.

Validated workflow: `34816085941`.

### dev.11 — Migration/dependency inventory

Added `src/v14/migration-inventory.json`, its validator and policy tests.

The inventory makes migration decisions machine-readable and blocks opportunistic persistence/schema/geometry/rendering extraction.

Validated workflow: `34816530041`.

### dev.12 — Dimension formatting

Moved pure display formatting from legacy `fmtDim` into `shell/units.js`.

Preserved formats:

- metres: two decimals;
- decimal feet: two decimals;
- centimetres: two decimals;
- millimetres: integer display;
- inches: two decimals;
- feet + inches: nearest one-eighth inch;
- unknown suffixes: legacy factor fallback.

No project unit state, numeric editing, geometry or renderer ownership moved.

Validated workflow: `34871518856`.

### dev.13 — Stabilization freeze

V14 deliberately stopped extracting legacy ownership.

`migration-inventory.json` now enforces:

- `phase: stabilization`;
- `architectureFrozen: true`;
- `allowNewLegacyBridges: false`;
- `allowProductionCutover: false`;
- exact frozen module list;
- exact frozen patch list;
- zero `selected-next` migration boundaries.

CI compares the manifest to the frozen module/patch surface, so accidental architecture drift fails the build.

Validated workflow: `34872208603`.

### dev.14 — Isolated V14 offline shell

Dev.14 fixes a release-packaging weakness without moving any application ownership.

Previously the generated V14 artifact passed through the 13.2.0 production worker unchanged. The builder already had a deterministic worker-generation path; dev.14 activates it.

The manifest now supplies a hash-locked service-worker source contract:

- source: production `sw.js`;
- expected source SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`;
- source cache prefix: `atelier-space-studio-`;
- development cache prefix: `atelier-v14-dev-`.

The generated worker:

1. identifies itself as the current V14 development version;
2. uses `atelier-v14-dev-<version>`;
3. appends every V14 style/module to the offline core;
4. cleans stale caches only within `atelier-v14-dev-`;
5. leaves the production/baseline `atelier-space-studio-*` namespace untouched.

CI verifies the generated worker source structure, syntax, release/cache identity, core list and prefix replacement.

The real Chromium offline test additionally creates:

- a baseline `atelier-space-studio-13.2.0` cache;
- a stale `atelier-v14-dev-stale-probe` cache.

It then invokes worker stale-cache cleanup and requires the stale V14 cache to be deleted while the baseline production cache survives. The artifact is subsequently reloaded fully offline and all V14 modules must return.

Validated workflow: `34872824160`.

## Current module surface

The stabilization freeze contains eight modules:

1. `shell/notifications.js`
2. `shell/dialogs.js`
3. `shell/commands.js`
4. `shell/files.js`
5. `shell/icons.js`
6. `shell/text.js`
7. `shell/units.js`
8. `dev-status/dev-status.js`

Seven exact bridge files correspond to the migrated legacy helpers. `dev-status` is development-only and does not bridge legacy application behavior.

## Current ownership boundary

V14 owns only generic post-bootstrap shell/helper presentation and development packaging:

- notifications/status;
- modal/focus presentation;
- command search/results presentation;
- browser file delivery/naming;
- SVG icon serialization;
- HTML/SVG/XML escaping;
- dimension display formatting;
- V14 development artifact/offline packaging.

Legacy 13.2.0 remains authoritative for:

- project persistence/backups;
- project schema and normalization;
- geometry and precision;
- 2D/3D rendering;
- catalog/application state;
- command/action execution;
- project identity;
- numeric editing and stored unit state;
- exchange/export domain semantics.

## Validation layers

V14 currently has four enforced validation layers.

### 1. Deterministic source/build validation

- exact baseline hash lock;
- byte-for-byte source round trip;
- exact bridge matching;
- hashed V14 asset/build manifest;
- hash-locked service-worker source transformation.

### 2. Architecture policy validation

- structured dependency/migration inventory;
- blocked/deferred ownership classes;
- stabilization freeze;
- no new bridge or selected migration;
- production cutover disallowed.

### 3. Isolated behavior validation

Independent behavior suites cover:

- notifications;
- dialogs;
- commands;
- browser files;
- icons;
- text escaping;
- dimension formatting;
- service-worker build transformation.

### 4. Integrated runtime validation

Generated artifacts run in:

- Chromium desktop;
- Chromium mobile/touch;
- Firefox desktop;
- WebKit desktop;
- controlled Chromium offline mode.

Integrated tests cover responsive overflow, keyboard/focus/accessibility paths, direct modular helper probes, offline restoration and V14/baseline cache isolation.

## Release-readiness audit

Dev.14 is a stable **development** checkpoint, not a release candidate.

### Resolved development concerns

- deterministic source reconstruction;
- exact bridge safety;
- architecture drift prevention;
- multi-browser shell compatibility;
- responsive/mobile smoke coverage;
- development offline shell completeness;
- V14 cache namespace isolation from production.

### Hard cutover blockers

1. `CERTIFICATION_MATRIX_13.3.1.json` currently records `runtimeMayAdvanceToV14: false` and 0/5 required physical targets.
2. `v14-build-manifest.json` intentionally emits `developmentOnly: true`.
3. `dev-status/` is still included and visibly labels the runtime `V14 DEV`.
4. `production.config.json` still identifies release 13.2.0 and the 13.2 production certification contract.
5. No V14-specific physical-device acceptance has been completed.
6. No V14 production-origin deployment/cutover verification has been completed.
7. V14 production update/rollback certification has not yet been defined for a release candidate.

No automated development test may silently convert these blockers into a production claim.

## Next architecture decision

Do **not** resume stateful code extraction.

The next meaningful V14 work should be release-candidate preparation only after its prerequisites are explicit. That work should separate a production candidate from the development artifact, remove development-only diagnostics, define production release/cache identity, and create V14-specific production/physical acceptance gates.

Until those gates are designed and satisfied, `allowProductionCutover` remains `false` and production stays on Atelier 13.2.0.
