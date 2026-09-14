# Atelier V14 Development Architecture

## Status

V14 is an **uncertified successor-development cycle** on branch `v14-development`.

Current validated checkpoint: **14.0.0-dev.15**.

Production remains Atelier **13.2.0** on `main`. V13.3.1 physical-device sign-off remains a separate unresolved production gate.

## Architecture objective

V14 incrementally extracts small, deterministic, low-state boundaries from the locked Atelier 13.2.0 monolith while preserving exact legacy fallback behavior.

The architecture is now in **stabilization**. No additional application ownership may move without an explicit new architecture decision.

Excluded from opportunistic migration:

- project persistence and backups;
- project schema and validation;
- geometry/precision engines;
- 2D/3D rendering;
- catalog/application state;
- broad project/orchestration helpers.

## Source, development build and RC packaging

```text
index.html + sw.js (locked Atelier 13.2.0 sources)
        │
        ├── source-lock verification
        ├── byte-for-byte extraction/rebuild check
        │
        ▼
tools/v14_build.py + src/v14/manifest.json
        │
        ├── exact occurrence-checked legacy bridges
        ├── frozen V14 styles/modules
        ├── isolated atelier-v14-dev-* worker/cache
        │
        ▼
v14-dist — development artifact
        │
        ├── diagnostics present
        ├── developmentOnly: true
        │
        ▼
tools/v14_rc_package.py
        │
        ├── strip dev-status CSS/JS
        ├── strip diagnostics from offline core
        ├── switch worker cache to atelier-v14-rc-*
        ├── evaluate CERTIFICATION_MATRIX_13.3.1.json
        │
        ▼
v14-rc — release-candidate artifact
        ├── v14-build-manifest.json
        └── v14-rc-status.json
```

The root production runtime is never rewritten by either path.

## Exact bridge policy

`atelier-v14-exact-patch-v1` is the migration boundary for helpers hidden inside the legacy IIFE.

1. Every bridge specifies exact source text and required occurrence count.
2. Missing or duplicate matches fail the build.
3. Patch inputs and replacements are SHA-256 recorded in the build manifest.
4. Legacy function bodies remain available as fallback.
5. IIFE-owned state remains private and is exposed only through narrow adapters where required.
6. Stabilization forbids new bridges unless the architecture phase is explicitly reopened.

## Milestone history

### dev.1 — Reproducible source boundary

Added the source lock, lossless extraction/rebuild tooling and byte-for-byte baseline invariant.

### dev.2 — Deterministic module overlay

Added the ordered V14 manifest, overlay builder, exact patch engine and hashed build manifest.

### dev.3 — Shell notifications

Moved generic announcements, toasts and status presentation into `shell/notifications.js`.

### dev.4 — Command palette

Moved command-palette opening/search/result presentation into `shell/commands.js`; legacy command execution remains unchanged.

### dev.5 — Browser file utilities

Moved generic browser download delivery and safe filename normalization into `shell/files.js`.

### dev.6 — Dialog shell

Moved modal DOM behavior, focus handling and confirmation composition into `shell/dialogs.js` through narrow adapters.

### dev.7 — Real-browser shell integration

Added generated-artifact Chromium integration and concurrency-safe CI.

### dev.8 — Cross-browser, responsive and offline integration

Added Chromium desktop, Chromium mobile/touch, Firefox and WebKit integration plus controlled offline testing.

### dev.9 — SVG icon renderer

Moved pure SVG serialization into `shell/icons.js`; immutable icon registry data stays legacy-owned.

### dev.10 — Text escaping

Centralized HTML/SVG/XML escaping in `shell/text.js` while preserving exact fallback behavior.

### dev.11 — Migration/dependency inventory

Added machine-readable ownership/risk decisions and blocked opportunistic migration of persistence/schema/geometry/rendering.

Validated workflow: `34816530041`.

### dev.12 — Dimension formatting

Moved pure display formatting from legacy `fmtDim` into `shell/units.js` without moving project unit state or geometry.

Validated workflow: `34871518856`.

### dev.13 — Stabilization freeze

The inventory began enforcing:

- `phase: stabilization`;
- `architectureFrozen: true`;
- `allowNewLegacyBridges: false`;
- `allowProductionCutover: false`;
- exact frozen module/patch lists;
- zero `selected-next` migration boundaries.

Validated workflow: `34872208603`.

### dev.14 — Isolated V14 development offline shell

Activated deterministic worker generation from the hash-locked 13.2.0 worker source.

Development artifacts now:

- identify as the current V14 dev version;
- use `atelier-v14-dev-<version>`;
- pre-cache all V14 overlay assets;
- clean only stale `atelier-v14-dev-*` caches;
- preserve `atelier-space-studio-*` baseline/production caches.

Validated workflow: `34872824160`.

### dev.15 — Release-candidate packaging & certification boundary

Dev.15 creates a distinct RC package without changing the frozen application architecture.

`tools/v14_rc_package.py`:

1. copies the already validated development artifact;
2. removes the `dev-status` stylesheet, module and generated files;
3. removes diagnostics from the offline core;
4. changes the worker cache namespace to `atelier-v14-rc-<version>`;
5. reads `CERTIFICATION_MATRIX_13.3.1.json`;
6. writes promotion eligibility and blockers into both RC metadata files;
7. supports `--require-production-eligible`, which fails closed while prerequisites are missing.

The RC package intentionally uses a separate cache namespace from both production and V14 development.

Validated workflow: **`34882066210`**.

## Frozen module surface

The source architecture remains eight modules:

1. `shell/notifications.js`
2. `shell/dialogs.js`
3. `shell/commands.js`
4. `shell/files.js`
5. `shell/icons.js`
6. `shell/text.js`
7. `shell/units.js`
8. `dev-status/dev-status.js` — development packaging only

Seven exact bridge files correspond to migrated legacy helpers.

The RC package removes only item 8 from the packaged runtime. That is a packaging transformation, not an ownership migration.

## Current ownership boundary

V14 owns only generic post-bootstrap shell/helper presentation and V14 packaging:

- notifications/status;
- modal/focus presentation;
- command search/result presentation;
- browser file delivery/naming;
- SVG icon serialization;
- HTML/SVG/XML escaping;
- dimension display formatting;
- development and RC packaging.

Legacy 13.2.0 remains authoritative for:

- persistence/backups;
- schema/normalization;
- geometry/precision;
- 2D/3D rendering;
- catalog/application state;
- command/action execution;
- project identity;
- numeric editing/stored unit state;
- domain export semantics.

## Validation layers

### 1. Deterministic source/build

- exact baseline hash lock;
- byte-for-byte source round trip;
- exact bridge matching;
- hashed assets/build manifest;
- hash-locked worker transformation.

### 2. Architecture and packaging policy

- migration inventory;
- stabilization freeze;
- frozen module/patch lists;
- isolated development and RC cache namespaces;
- mandatory RC diagnostics stripping;
- prior-signoff requirement for RC promotion.

### 3. Isolated behavior

Independent tests cover notifications, dialogs, commands, files, icons, text escaping, dimension formatting and worker generation.

### 4. Integrated development runtime

Development artifact runs in:

- Chromium desktop;
- Chromium mobile/touch;
- Firefox desktop;
- WebKit desktop;
- controlled Chromium offline mode.

### 5. RC packaging/runtime

CI additionally verifies:

- diagnostics are absent from RC HTML/files/offline core;
- RC cache identity is `atelier-v14-rc-*`;
- RC certification metadata is correct;
- promotion fails closed while prerequisites are missing;
- stripped RC starts in Chromium;
- stripped RC reloads offline under its own worker/cache;
- development and RC artifacts are uploaded separately.

## Current RC certification state

The generated dev.15 RC is technically package-valid but **not promotion-eligible**.

Current blockers recorded by the RC gate:

1. `prior-final-signoff-not-pass`
2. `runtime-advance-not-authorized`
3. `physical-evidence-incomplete`

These derive from the actual V13.3.1 certification matrix, which still reports 0/5 physical evidence and `runtimeMayAdvanceToV14: false`.

## Cutover rule

A validated RC artifact is not equivalent to production authorization.

Production cutover remains forbidden until all of the following are true:

1. V13.3.1 prior-release physical sign-off genuinely passes;
2. runtime advance to V14 is authorized by the certification state;
3. the V14 RC promotion gate reports no blockers;
4. V14-specific physical-device acceptance is defined and completed;
5. production-origin deployment/update/rollback verification is completed;
6. production configuration is explicitly advanced from 13.2.0.

Until then, `allowProductionCutover` remains `false` and production stays on Atelier 13.2.0.

## Next milestone

Do not resume stateful code extraction.

The next meaningful V14 work is **RC certification infrastructure**: define V14-specific physical acceptance and production-origin cutover/rollback evidence while continuing to keep actual promotion blocked by the unresolved prior-release gate.
