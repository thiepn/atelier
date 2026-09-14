# V14 modules

This directory is the home for authored V14 code.

## Current checkpoint

**14.0.0-dev.10** is the current V14 development artifact. It is isolated from production and is not a V13.3.1 production certification result.

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
- `dev-status/` — isolated V14 development diagnostics.

Exact bridges live under `patches/` for each migrated legacy helper.

## Automated validation

The V14 workflow currently performs:

1. source-tool unit tests;
2. overlay-build/patch-engine unit tests;
3. JavaScript syntax checks for every V14 module and browser-test file;
4. independent behavior tests for notifications, dialogs, commands, files, icons and text escaping;
5. exact 13.2.0 baseline lock verification;
6. byte-for-byte source round-trip verification;
7. generated development artifact and bridge validation;
8. Chromium desktop integration;
9. Chromium 390×844 mobile/touch integration;
10. Firefox desktop integration;
11. WebKit desktop integration;
12. responsive horizontal-overflow checks;
13. keyboard, Escape, focus-restoration and shell accessibility checks;
14. controlled Chromium offline/PWA reload verification;
15. hashed artifact upload.

## Current ownership boundary

V14 owns post-bootstrap generic shell behavior for:

- notifications/status;
- modal/dialog DOM behavior;
- command-palette presentation/search;
- browser file delivery/naming;
- SVG icon serialization;
- generic HTML/SVG/XML text escaping.

The legacy runtime still owns:

- command execution;
- icon path registry data;
- project persistence;
- backup semantics;
- project schema;
- geometry/math helpers;
- catalog/application state;
- rendering.

## Development rules

1. Keep new functionality isolated here until the deterministic build path integrates it.
2. Prefer small subsystem boundaries over another monolithic script.
3. Do not migrate persistence, project schema, geometry or rendering merely to increase extraction count.
4. Every migrated subsystem needs independent behavior coverage plus integrated artifact coverage.
5. Exact bridges must fail closed if the locked legacy source no longer matches.
6. `main` remains the production/certification line until an explicit V14 release cutover.
7. Automated browser/PWA development checks never substitute for V13.3.1 physical-device evidence.

## Next milestone

After dev.10, the obvious shell-only helpers are largely exhausted. **Dev.11 should be an architecture/dependency inventory before any deeper extraction.** It should classify remaining legacy boundaries by state ownership, call surface, browser dependence and regression risk, then select the next migration only when it has a clear payoff. Persistence, project schema, geometry and rendering remain excluded by default.
