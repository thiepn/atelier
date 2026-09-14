# Atelier V14 Development Architecture

## Status

V14 is an **uncertified development cycle** on branch `v14-development`. The current validated checkpoint is **14.0.0-dev.12**. Production remains Atelier 13.2.0 on `main`; V13.3.1 physical-device sign-off is a separate unresolved production gate and is not implied by V14 development.

## Core architecture rule

V14 incrementally extracts low-state, testable boundaries from the locked Atelier 13.2.0 monolith while preserving an exact fallback path. It is not a big-bang rewrite.

The following remain excluded by default from opportunistic migration:

- project persistence;
- project schema;
- backup semantics;
- geometry and renderer ownership;
- catalog/application state.

Those boundaries may move only after an explicit dependency/risk review and a concrete V14 requirement.

## Milestone 1 — Reproducible source boundary

`14.0.0-dev.1` made the development-source contract concrete.

Components:

- `src/source.lock.json` pins the exact 13.2.0 runtime baseline;
- `tools/v14_source.py` losslessly extracts inline HTML/CSS/JS/data segments and rebuilds them byte-for-byte;
- `tools/test_v14_source.py` verifies round-trip integrity, tamper rejection, external-script handling and runtime-lock enforcement;
- `src/generated/` is a reproducible local source view;
- `src/v14/` is the authored V14 module workspace.

Invariant: extracting and rebuilding the frozen baseline must reproduce `index.html` exactly.

## Milestone 2 — Deterministic module overlay

`14.0.0-dev.2` added a separate V14 artifact rather than modifying the root runtime.

Components:

- `src/v14/manifest.json` — ordered styles, modules, exact bridges and passthrough assets;
- `tools/v14_build.py` — baseline verification, path validation, exact patching, deterministic injection and build-manifest generation;
- `tools/test_v14_build.py` — deterministic output, path traversal, marker, lock and exact-patch tests;
- `src/v14/dev-status/` — isolated development diagnostics;
- `.github/workflows/v14-source-roundtrip.yml` — CI gate.

Build flow:

```text
index.html (locked Atelier 13.2.0)
        │
        ├── source lock verification
        ├── byte-for-byte source round trip
        │
        ▼
tools/v14_build.py + src/v14/manifest.json
        │
        ├── exact occurrence-checked bridges
        ├── ordered V14 styles/modules
        ├── passthrough runtime assets
        │
        ▼
separate V14 development artifact
        │
        ├── v14-build-manifest.json
        └── browser/offline integration gates
```

The root `index.html` is never rewritten by the V14 overlay builder.

## Exact bridge policy

`atelier-v14-exact-patch-v1` is the controlled migration boundary for functions hidden inside the legacy IIFE.

1. Every bridge declares exact source text and required occurrence count.
2. Missing or duplicate matches fail the build instead of guessing.
3. Patch source, find string and replacement are hash-bound in the build manifest.
4. Legacy behavior remains available as fallback.
5. Modules fail safely when required adapters or DOM surfaces are unavailable.
6. IIFE-owned state is passed through narrow adapters rather than exposed globally.
7. A migration must not change project schema, persistence or geometry merely to simplify extraction.

## Milestone 3 — Shell notifications

`14.0.0-dev.3` moved accessibility announcements, toasts and save/status messaging into `src/v14/shell/notifications.js` while preserving exact legacy fallback.

Validated workflow: `34793861206`.

## Milestone 4 — Command palette

`14.0.0-dev.4` moved command-palette opening, search and result rendering into `src/v14/shell/commands.js` while retaining legacy command execution and `data-command` contracts.

Validated workflow: `34794079679`.

## Milestone 5 — Browser file utilities

`14.0.0-dev.5` moved browser download delivery and safe filename normalization into `src/v14/shell/files.js`, preserving Blob/MIME/download/revocation and filename behavior.

Validated workflow: `34794229852`.

## Milestone 6 — Dialog shell

`14.0.0-dev.6` moved modal rendering, focus management and confirmation composition into `src/v14/shell/dialogs.js`. Application-owned state remains private to the legacy IIFE and is exposed only through narrow adapters.

Validated workflow: `34794378836`.

## Milestone 7 — Real-browser shell integration

`14.0.0-dev.7` added generated-artifact Chromium integration testing and made CI manifest-driven and concurrency-safe. The test drives actual legacy keyboard/action paths through the V14 bridges instead of validating modules only in isolation.

Validated workflow: `34794583346`.

## Milestone 8 — Cross-browser, responsive & offline integration

`14.0.0-dev.8` hardened the migration layer before further extraction.

Browser matrix:

1. Chromium desktop — 1280×800;
2. Chromium mobile/touch — 390×844;
3. Firefox desktop — 1280×800;
4. WebKit desktop — 1280×800.

Integrated requirements include:

- V14 shell-service registration;
- <= 1 px document horizontal overflow;
- touch-capability verification in the mobile project;
- diagnostics keyboard semantics;
- `Ctrl+K` legacy shortcut -> V14 command/dialog path;
- dialog `aria-modal`, accessible search naming and autofocus;
- native Escape cancellation and deterministic focus restoration;
- preservation of existing command action contracts;
- zero uncaught page and console errors.

A separate Chromium gate verifies a real inherited-service-worker warm load -> offline reload cycle and requires the generated V14 overlay to return while the 13.2.0 core cache remains complete.

Validated workflow: `34815078492`.

## Milestone 9 — Modular SVG icon renderer

`14.0.0-dev.9` extracted pure SVG icon serialization into `src/v14/shell/icons.js`.

The icon path registry deliberately remains in the locked legacy runtime. The exact bridge passes that registry into the V14 renderer, so rendering ownership moves without duplicating icon data or changing bootstrap behavior.

Preserved contract:

- requested width/height;
- `0 0 24 24` viewBox;
- current-color stroke;
- stroke width/caps/joins;
- `aria-hidden="true"`;
- unknown icon fallback to the legacy `cube` path.

Validation covers isolated rendering behavior, exact bridge integrity, the four-browser matrix, command-palette SVG presence and controlled offline restoration.

Validated workflow: `34815530617`.

## Milestone 10 — Modular text escaping service

`14.0.0-dev.10` centralizes repeated deterministic escaping in `src/v14/shell/text.js`.

Two explicit contracts are retained:

- `escapeHtml(value)` — `&`, `<`, `>`, `"`, `'` with legacy apostrophe encoding `&#39;`;
- `escapeXml(value)` — same core entities with XML apostrophe encoding `&apos;`.

The service preserves null/undefined -> empty string conversion, `String(...)` coercion and the legacy single-pass behavior.

Four exact legacy helpers are bridged:

1. generic `esc` -> HTML escaping;
2. `svgEsc` -> HTML escaping;
3. plan `xml` helper -> HTML-style escaping to preserve its existing `&#39;` output;
4. dedicated `escXML` -> XML escaping.

The bridge patches only unique helper prefixes. The original `.replace(...)` expressions remain physically present as fallback branches, reducing duplicated exact-source text in the patch specification while preserving the locked implementation.

Dev.10 validation includes isolated text behavior, all four exact occurrence checks, deterministic artifact generation, Chromium desktop/mobile, Firefox, WebKit, direct HTML/XML browser probes, controlled offline restoration and artifact upload.

Validated workflow: `34816085941`.

## Milestone 11 — Migration & dependency inventory

`14.0.0-dev.11` stopped automatic helper extraction and introduced a machine-validated boundary inventory.

Components:

- `src/v14/migration-inventory.json` — ownership/risk/testability decisions for the remaining legacy boundaries;
- `tools/v14_migration_inventory.py` — fail-closed policy validator;
- `tools/test_v14_migration_inventory.py` — regression tests for duplicate IDs, excluded ownership, selection cardinality and mutation constraints;
- CI synchronization between inventory version, module-manifest version and generated-artifact version.

Selection policy requires an authorized migration to be low state risk, non-mutating, highly testable, at most low browser coupling and compatible with an explicit legacy fallback.

The inventory blocks persistence, project schema, geometry and rendering from opportunistic extraction. It selected only `dimension-formatting` for dev.12.

Validated workflow: `34816530041`.

## Milestone 12 — Dimension formatting boundary

`14.0.0-dev.12` implements the only migration authorized by dev.11.

`src/v14/shell/units.js` owns deterministic display formatting previously provided by legacy `fmtDim`.

Preserved formats:

- `m` — two decimals;
- `ft` — two decimals;
- `cm` — two decimals;
- `mm` — integer display;
- `in` — two decimals;
- `ft-in` — nearest one-eighth inch using the existing prime notation;
- unknown unit strings — factor fallback `1` and supplied suffix preserved.

`src/v14/patches/units-bridge.json` replaces only the unique `fmtDim` function prefix. The complete original formatter body remains immediately after the V14 delegation as fallback.

The migration does **not** move or alter:

- project unit state;
- stored numeric values;
- numeric editing/conversion;
- geometry;
- project schema;
- persistence;
- plan/3D renderer ownership.

Validation includes isolated formatter behavior, exact bridge occurrence, all four browser projects, direct metric/imperial browser probes and a controlled offline reload that requires the units service to register and execute from the cached development artifact.

After successful dev.12 validation, the inventory marks `dimension-formatting` completed, sets `selectionRequired: false`, and contains no `selected-next` boundary. This is an explicit extraction stop rather than an invitation to choose another helper implicitly.

Validated workflow: `34871518856`.

## Development diagnostics

`src/v14/dev-status/` displays network state, display mode, service-worker controller state, touch-point count, viewport information and the 13.2.0 baseline identity. It is namespaced, keyboard accessible and explicitly development-only.

It does not read or mutate project data, persistence, backups, geometry, catalog state or renderer state.

## Current modular ownership boundary

As of dev.12, V14 owns post-bootstrap generic shell/helper behavior for:

1. notifications/status;
2. modal/dialog DOM behavior;
3. command-palette presentation/search;
4. browser file delivery/naming;
5. SVG icon serialization;
6. generic HTML/SVG/XML text escaping;
7. dimension display formatting.

Legacy ownership remains for:

- command execution;
- icon path registry data;
- project persistence and backups;
- project schema and validation;
- geometry and broadly shared project math;
- project identity generation;
- catalog and application state;
- project unit state and numeric editing;
- exchange/export domain semantics;
- 2D/3D rendering.

## Current validation boundary

V14 has four enforced layers:

1. **Deterministic source/build validation** — locked baseline, lossless source round trip, exact bridge checks and hashed development artifact.
2. **Migration policy validation** — structured ownership/risk inventory and fail-closed selection rules.
3. **Isolated module validation** — behavior suites for each migrated shell/helper service.
4. **Integrated runtime validation** — Chromium desktop/mobile, Firefox, WebKit and controlled offline Chromium execution against the generated artifact.

These layers validate the V14 development branch only. They do not replace V13.3.1 physical-device production acceptance.

## Next V14 milestone

There is intentionally **no selected dev.13 extraction**.

Before dev.13 changes another legacy ownership boundary, V14 must make an explicit direction decision. The valid paths are:

1. identify a concrete product/reliability requirement that justifies another migration and revise the inventory accordingly;
2. enter stabilization/release-readiness work without moving more stateful code;
3. prepare a future cutover plan while keeping the validated dev.12 architecture fixed.

Until that decision is recorded, persistence, schema, geometry, rendering, catalog/application state and broad project/orchestration helpers remain legacy-owned.
