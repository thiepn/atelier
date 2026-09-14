# V14 modules

This directory contains authored V14 development code.

## Current checkpoint

**14.0.0-dev.15** is the current validated V14 checkpoint. It produces two isolated artifacts:

- a development artifact with diagnostics;
- a stripped release-candidate artifact.

Neither artifact is production certification.

## Build and package

Build the normal development artifact:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir v14-dist --force
```

Package the RC artifact:

```bash
python tools/v14_rc_package.py --repo-root . --source-dir v14-dist --output-dir v14-rc --force
```

The development builder verifies the locked 13.2.0 baseline, applies exact bridges, injects the frozen V14 module surface, generates the isolated development worker and emits `v14-build-manifest.json`.

The RC packager then:

- removes `dev-status` CSS/JS and their HTML tags;
- removes those diagnostic assets from the service-worker core;
- changes the cache namespace from `atelier-v14-dev-*` to `atelier-v14-rc-*`;
- evaluates `CERTIFICATION_MATRIX_13.3.1.json`;
- writes RC promotion state to `v14-build-manifest.json` and `v14-rc-status.json`.

## Frozen module surface

1. `shell/notifications.js`
2. `shell/dialogs.js`
3. `shell/commands.js`
4. `shell/files.js`
5. `shell/icons.js`
6. `shell/text.js`
7. `shell/units.js`
8. `dev-status/dev-status.js` — development packaging only

Seven exact legacy bridges remain frozen under `patches/`.

## Stabilization policy

`migration-inventory.json` is validated by `tools/v14_migration_inventory.py`.

Current rules include:

- `phase: stabilization`;
- `architectureFrozen: true`;
- `allowNewLegacyBridges: false`;
- `allowProductionCutover: false`;
- no `selected-next` migration;
- isolated development cache prefix `atelier-v14-dev-`;
- isolated RC cache prefix `atelier-v14-rc-`;
- RC diagnostics must be stripped;
- RC promotion must require prior production sign-off.

Persistence, schema, geometry and rendering remain blocked from opportunistic extraction.

## Validation

Latest successful workflow: **`34882066210`**.

The workflow validates:

1. source/build and migration-policy tests;
2. shell/helper behavior tests;
3. exact baseline and source round trip;
4. development artifact structure and cache isolation;
5. RC packaging and diagnostic stripping;
6. RC certification metadata;
7. fail-closed promotion behavior;
8. Chromium desktop/mobile, Firefox and WebKit development integration;
9. development offline reload;
10. stripped RC Chromium startup and offline reload;
11. upload of both development and RC artifacts.

## RC promotion state

Current RC promotion eligibility is **false**.

Current blockers:

- `prior-final-signoff-not-pass`
- `runtime-advance-not-authorized`
- `physical-evidence-incomplete`

`--require-production-eligible` must continue to fail until those conditions are genuinely resolved.

## Ownership boundary

V14 owns only the generic shell/helper and packaging surfaces listed above.

Legacy runtime ownership remains for:

- command execution;
- icon registry data;
- project persistence/backups;
- schema/validation;
- geometry/project math;
- identity generation;
- catalog/application state;
- numeric editing/project unit state;
- domain export semantics;
- 2D/3D rendering.

Do not resume stateful extraction during stabilization merely to increase modularization count.
