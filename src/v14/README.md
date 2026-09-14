# V14 modules

This directory is the home for authored V14 code.

## Current checkpoint

**14.0.0-dev.12** is the current validated V14 development artifact. It is isolated from production and is not a V13.3.1 production certification result.

## Build

The root `index.html` remains the locked Atelier 13.2.0 baseline. V14 modules are injected only into a separate development artifact:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir dist --force
```

The builder verifies the frozen baseline, applies exact occurrence-checked bridges, injects ordered V14 assets, copies declared passthrough assets, emits a hashed `v14-build-manifest.json`, and never rewrites the root `index.html`.

## Current V14 modules

- `shell/notifications.js` — announcements, toasts and save/status messaging.
- `shell/dialogs.js` — generic modal rendering, focus and confirmation composition.
- `shell/commands.js` — command-palette opening, search and result rendering.
- `shell/files.js` — browser downloads and safe filename normalization.
- `shell/icons.js` — SVG icon serialization using the locked legacy icon registry supplied through the bridge.
- `shell/text.js` — deterministic HTML/SVG/XML text escaping.
- `shell/units.js` — deterministic dimension display formatting for metric and imperial modes.
- `dev-status/` — isolated V14 development diagnostics.

Exact bridges live under `patches/` for each migrated legacy helper.

## Migration inventory

`migration-inventory.json` records remaining legacy ownership boundaries and is validated by `tools/v14_migration_inventory.py`.

As of dev.12:

- `dimension-formatting` is completed;
- persistence, project schema, geometry and rendering are blocked from opportunistic extraction;
- broader project math, identity, application orchestration, catalog ownership and export orchestration remain deferred/held;
- `selectionRequired` is `false`;
- there is no `selected-next` boundary.

Therefore another extraction cannot be treated as the automatic dev.13 task. The inventory must be explicitly revised first.

## Automated validation

The V14 workflow currently performs:

1. source-tool unit tests;
2. overlay-build/patch-engine unit tests;
3. migration-inventory policy tests and validation;
4. JavaScript syntax checks for every V14 module and browser-test file;
5. independent behavior tests for notifications, dialogs, commands, files, icons, text escaping and dimension formatting;
6. exact 13.2.0 baseline lock verification;
7. byte-for-byte source round-trip verification;
8. generated development artifact and exact-bridge validation;
9. Chromium desktop integration;
10. Chromium 390×844 mobile/touch integration;
11. Firefox desktop integration;
12. WebKit desktop integration;
13. responsive horizontal-overflow checks;
14. keyboard, Escape, focus-restoration and shell accessibility checks;
15. direct text and unit-formatting browser probes;
16. controlled Chromium offline/PWA reload verification;
17. hashed artifact upload.

## Current ownership boundary

V14 owns post-bootstrap generic shell/helper behavior for:

- notifications/status;
- modal/dialog DOM behavior;
- command-palette presentation/search;
- browser file delivery/naming;
- SVG icon serialization;
- generic HTML/SVG/XML text escaping;
- dimension display formatting.

The legacy runtime still owns:

- command execution;
- icon path registry data;
- project persistence;
- backup semantics;
- project schema and validation;
- geometry and broadly shared project math;
- catalog/application state;
- numeric editing and project unit state;
- 2D/3D rendering.

## Development rules

1. Keep new functionality isolated here until the deterministic build path integrates it.
2. Prefer small subsystem boundaries over another monolithic script.
3. Do not migrate persistence, project schema, geometry or rendering merely to increase extraction count.
4. Every migrated subsystem needs independent behavior coverage plus integrated artifact coverage.
5. Exact bridges must fail closed if the locked legacy source no longer matches.
6. `main` remains the production/certification line until an explicit V14 release cutover.
7. Automated browser/PWA development checks never substitute for V13.3.1 physical-device evidence.
8. Do not begin another legacy extraction while the migration inventory has no selected-next boundary.

## Next milestone

Dev.12 closes the currently authorized low-risk extraction. **The next milestone should be an explicit V14 direction/cutover-readiness decision, not an automatic dev.13 helper extraction.** The branch should now determine whether V14 needs another concrete architectural migration, stabilization work, or release-readiness preparation before changing ownership of any stateful subsystem.
