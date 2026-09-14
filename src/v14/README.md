# V14 modules

This directory is the home for authored V14 code.

## Current checkpoint

**14.0.0-dev.7** is the current V14 development artifact. It is isolated from production and is not a V13.3.1 production certification result.

## Build

The root `index.html` remains the locked Atelier 13.2.0 baseline. V14 modules are injected only into a separate development artifact:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir dist --force
```

The builder:

- verifies the frozen baseline through `src/source.lock.json`;
- rejects duplicate V14 injection markers;
- validates module, patch and passthrough paths and blocks path traversal;
- applies exact legacy bridges with fail-closed occurrence counts;
- injects V14 styles before `</head>` and modules before `</body>`;
- copies declared V14 and passthrough assets;
- writes `v14-build-manifest.json` with baseline, patched-baseline, patch, artifact and asset hashes;
- never modifies the root `index.html`.

## Layout

- `manifest.json` — authoritative development version, ordered styles, modules, bridges and runtime assets.
- `patches/notifications-bridge.json` — legacy announcement/toast/status delegation.
- `patches/dialogs-bridge.json` — legacy modal/open/close/confirm delegation.
- `patches/commands-bridge.json` — legacy command-palette opening/render delegation.
- `patches/files-bridge.json` — legacy download and safe-filename delegation.
- `shell/notifications.js` — accessibility announcements, toasts and save/status messaging.
- `shell/dialogs.js` — generic modal rendering, focus and confirmation composition.
- `shell/commands.js` — command-palette opening, search and result rendering.
- `shell/files.js` — browser downloads and safe filename normalization.
- `dev-status/` — isolated V14 development diagnostics.

## Bridge rules

A bridge is accepted only when its exact legacy source occurs the declared number of times. If the baseline changes unexpectedly, the build stops rather than applying an approximate patch.

Bridged functions keep their original implementation as fallback. Modules return `false` when an adapter or required DOM surface is unavailable so the legacy path can still execute. Private IIFE state is passed through narrow callbacks rather than exposed globally.

## Automated validation

The V14 workflow currently performs:

1. source-tool unit tests;
2. overlay-build/patch-engine unit tests;
3. JavaScript syntax checks for every V14 module;
4. independent behavior tests for notifications, dialogs, commands and file utilities;
5. exact 13.2.0 baseline lock verification;
6. byte-for-byte source round-trip verification;
7. real development artifact generation and manifest/bridge validation;
8. Chromium integration smoke against the generated artifact;
9. hashed artifact upload.

The Chromium smoke drives the actual legacy keyboard and action paths through the V14 bridges, rather than testing the modules only in isolation.

## Current ownership boundary

V14 now owns post-bootstrap generic shell behavior for:

- notifications/status;
- modal/dialog DOM behavior;
- command-palette presentation/search;
- browser file delivery/naming.

The legacy runtime still owns:

- command execution;
- project persistence;
- backup semantics;
- project schema;
- geometry;
- catalog/application state;
- rendering.

## Development rules

1. Keep new functionality isolated here until the deterministic build path integrates it.
2. Prefer small subsystem boundaries over another monolithic script.
3. Do not migrate persistence, project schema, geometry or rendering merely to increase extraction count.
4. Every migrated subsystem needs independent behavior coverage plus integrated artifact coverage.
5. Exact bridges must fail closed if the locked legacy source no longer matches.
6. `main` remains the production/certification line until an explicit V14 release cutover.

## Next milestone

Dev.8 should prioritize **cross-browser, responsive, keyboard and PWA/offline integration hardening** of the generated artifact before another more stateful subsystem is extracted.
