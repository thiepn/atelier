# V14 modules

This directory is the home for authored V14 code.

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

- `manifest.json` — ordered development version, styles, modules, bridges and runtime assets.
- `patches/` — audited exact bridges from the legacy IIFE into V14 modules.
- `shell/notifications.js` — accessibility announcements, toasts and save/status messaging.
- `shell/commands.js` — command-palette opening, search and result rendering.
- `dev-status/` — isolated V14 development diagnostics.

## Bridge rules

A bridge is accepted only when its exact legacy source occurs the declared number of times. If the baseline changes unexpectedly, the build stops rather than applying an approximate patch.

Bridged functions keep their original implementation as fallback. Modules should return `false` when an adapter or required DOM surface is unavailable so the legacy path can still execute.

## Current development artifact

`14.0.0-dev.4` includes:

1. deterministic source/build infrastructure;
2. development diagnostics;
3. modular shell notifications;
4. modular command-palette presentation/search.

Command execution, project persistence, project schema, geometry and renderer behavior remain legacy-owned at this milestone.

## Rules

1. Keep new functionality isolated here until the deterministic build path integrates it.
2. Prefer small subsystem boundaries over another monolithic script.
3. Do not move persistence, backup, project-schema, geometry, or rendering-core code first; begin with low-risk shell/UI modules.
4. Every migrated subsystem needs regression coverage before the old inline implementation is removed.
5. `main` remains the production/certification line until an explicit V14 release cutover.
