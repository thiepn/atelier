# Atelier 14.0.0-dev.9 — Modular SVG Icon Renderer

## Scope

Ninth V14 development milestone. Dev.9 resumes incremental migration after the dev.8 integration hardening gate by extracting one deliberately low-state presentation helper: SVG icon serialization.

## Added

- `src/v14/shell/icons.js` — modular SVG icon renderer.
- `src/v14/patches/icons-bridge.json` — exact legacy bridge for `icon(name, size)`.
- `tools/test_v14_icons.mjs` — isolated icon-renderer behavior suite.
- Dev.9 icon service registration in the generated-artifact browser matrix.
- Dev.9 icon service verification in the controlled offline/PWA gate.

## Migration boundary

The icon path registry remains inside the locked legacy runtime for this milestone. The exact bridge passes that existing registry into the V14 renderer.

This is intentional:

- rendering ownership moves into the V14 module;
- icon data is not duplicated;
- the original function body remains an exact fallback;
- initial legacy boot behavior remains valid before V14 overlay modules register;
- no project, persistence, geometry, catalog or renderer state is exposed.

The modular renderer preserves the exact legacy SVG structure:

- caller-provided width/height;
- `0 0 24 24` viewBox;
- current-color stroke;
- 1.6 stroke width;
- round caps and joins;
- `aria-hidden="true"`;
- unknown icon fallback to the legacy `cube` path.

## Validation

GitHub Actions run `34815530617` completed successfully.

Passed gates include:

- icon renderer JavaScript syntax;
- isolated icon behavior test;
- exact patch occurrence validation against the locked 13.2.0 baseline;
- V14 artifact build and bridge-structure verification;
- Chromium desktop integration;
- Chromium mobile/touch integration;
- Firefox desktop integration;
- WebKit desktop integration;
- integrated command-palette SVG presence;
- direct modular icon rendering probe;
- controlled offline/PWA reload with icon service restored;
- development artifact upload.

Generated artifact: `atelier-v14-dev.9`.

## Production impact

None. Production remains Atelier 13.2.0 on `main`. V14 remains an uncertified development branch, and automated V14 coverage does not substitute for the outstanding V13.3.1 physical-device evidence.
