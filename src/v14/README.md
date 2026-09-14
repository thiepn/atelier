# V14 modules

This directory contains authored V14 development code.

## Current checkpoint

**14.0.0-dev.16** is the current validated checkpoint.

The application architecture remains frozen at eight modules and seven exact bridges. Dev.16 adds certification infrastructure around the already validated RC package; it does not move more legacy state or rendering ownership.

## Build and package

Development artifact:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir v14-dist --force
```

Release-candidate artifact:

```bash
python tools/v14_rc_package.py --repo-root . --source-dir v14-dist --output-dir v14-rc --force
```

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

## Stabilization and RC certification policy

`migration-inventory.json` is validated by `tools/v14_migration_inventory.py` and currently requires:

- `phase: stabilization`;
- frozen module/patch lists;
- no new legacy bridges;
- no production cutover;
- isolated development and RC cache namespaces;
- diagnostics stripped from RC packaging;
- prior sign-off required before promotion;
- V14 RC physical plan `acceptance/v14-rc-required-targets.json`;
- validator `acceptance/validate_v14_rc_acceptance.py`;
- cutover plan `acceptance/v14-rc-cutover-plan.json`;
- physical evidence may be collected before prior sign-off;
- promotion may not occur before prior sign-off.

## RC physical evidence contract

Real evidence is bound to the exact candidate through:

- RC version;
- RC `index.html` SHA-256;
- RC `sw.js` SHA-256;
- RC cache identity;
- one normalized HTTPS candidate origin.

Five targets are required:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

The validator reports `PHYSICAL_READY`, `PRIOR_RELEASE_GATE_READY` and `PROMOTION_READY` separately.

Synthetic CI evidence is permitted only to test validator behavior and never counts as physical evidence.

## Current validation

Latest successful workflow: **`34883134671`**.

Passed:

- source/build tests;
- migration/stabilization policy tests;
- certification-plan structure validation;
- RC evidence-validator synthetic positive/tamper/duplicate self-tests;
- fail-closed promotion gate;
- Chromium desktop/mobile, Firefox and WebKit development integration;
- development offline reload;
- stripped RC Chromium startup/offline reload;
- development and RC artifact upload.

## Current real-world state

- V14 RC physical evidence: **0/5**
- HTTPS staging origin: **not provisioned**
- prior V13.3.1 release gate: **blocked**
- production cutover: **blocked**
- rollback certification: **not run**

See `CERTIFICATION_MATRIX_14.0.0-rc.json` and `acceptance/V14_RC_CERTIFICATION.md`.

## Ownership boundary

Legacy runtime ownership still includes:

- command execution;
- project persistence/backups;
- schema/validation;
- geometry/project math;
- project identity;
- catalog/application state;
- numeric editing/project unit state;
- domain export semantics;
- 2D/3D rendering.

Do not resume stateful extraction during stabilization merely to increase modularization count.
