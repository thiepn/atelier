# V14 modules

This directory contains authored V14 development code.

## Current checkpoint

**14.0.0-dev.14** is the current validated V14 development artifact. It is isolated from production and is not production certification.

## Build

The root `index.html` remains the locked Atelier 13.2.0 baseline. V14 modules are injected only into a separate development artifact:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir dist --force
```

The builder verifies the baseline lock, applies exact occurrence-checked bridges, injects ordered V14 assets, generates an isolated V14 service worker, copies declared passthrough assets, emits `v14-build-manifest.json`, and never rewrites root `index.html`.

## Current modules

- `shell/notifications.js` — announcements, toasts and save/status messaging.
- `shell/dialogs.js` — modal rendering, focus and confirmation composition.
- `shell/commands.js` — command-palette opening, search and results.
- `shell/files.js` — browser downloads and safe filenames.
- `shell/icons.js` — SVG icon serialization using the legacy registry passed through the bridge.
- `shell/text.js` — deterministic HTML/SVG/XML escaping.
- `shell/units.js` — dimension display formatting.
- `dev-status/` — development-only diagnostics.

Exact legacy bridges live under `patches/`.

## Stabilization freeze

`migration-inventory.json` is validated by `tools/v14_migration_inventory.py`.

Current stabilization policy:

- `phase: stabilization`;
- `architectureFrozen: true`;
- `allowNewLegacyBridges: false`;
- `allowProductionCutover: false`;
- the current eight modules are frozen;
- the current seven exact bridge files are frozen;
- there is no `selected-next` migration boundary.

Persistence, schema, geometry and rendering remain blocked from opportunistic extraction. Project math, identity, application orchestration, catalog ownership and domain export orchestration remain deferred/held.

## Isolated development service worker

Dev.14 no longer passes through the production 13.2.0 `sw.js` unchanged.

The builder now derives a development worker from the hash-locked 13.2.0 worker source and rewrites only the development packaging contract:

- release identity -> current V14 development version;
- cache -> `atelier-v14-dev-<version>`;
- stale-cache cleanup -> only the `atelier-v14-dev-` namespace;
- V14 styles/modules -> added to the offline core;
- production/baseline `atelier-space-studio-*` caches -> preserved.

The worker source hash must match the locked 13.2.0 source before generation. The generated worker is syntax-checked and its release/cache/core are verified in CI.

## Automated validation

The V14 workflow currently performs:

1. source-tool tests;
2. overlay/build tests, including service-worker generation tests;
3. migration-inventory policy tests and validation;
4. JavaScript syntax checks;
5. isolated behavior tests for all migrated shell/helper services;
6. exact 13.2.0 baseline lock verification;
7. byte-for-byte source round-trip verification;
8. generated artifact, exact-bridge and architecture-freeze verification;
9. generated service-worker identity/cache/core validation;
10. Chromium desktop integration;
11. Chromium mobile/touch integration;
12. Firefox desktop integration;
13. WebKit desktop integration;
14. responsive, keyboard, focus and accessibility checks;
15. controlled Chromium offline reload;
16. cache-isolation proof: stale V14 caches are removed while a seeded 13.2.0 baseline cache survives;
17. hashed artifact upload.

Latest successful workflow: `34872824160`.

## Ownership boundary

V14 owns only generic post-bootstrap shell/helper behavior and development packaging listed above.

The legacy runtime still owns:

- command execution;
- icon path registry data;
- project persistence/backups;
- project schema/validation;
- geometry and broadly shared project math;
- project identity;
- catalog/application state;
- numeric editing/project unit state;
- exchange/export domain semantics;
- 2D/3D rendering.

## Release-readiness boundary

Dev.14 removes the inherited-service-worker blocker, but it is still not a production artifact.

Known blockers:

- V13.3.1 physical sign-off is still blocked and currently says the runtime may not advance to V14;
- `v14-build-manifest.json` deliberately sets `developmentOnly: true`;
- `dev-status/` remains injected;
- `production.config.json` remains release 13.2.0;
- V14 physical-device acceptance and production-origin verification have not been completed.

Do not remove these blockers implicitly. A future release-candidate milestone must define a distinct production packaging/certification path without weakening the development freeze or the current production safeguards.
