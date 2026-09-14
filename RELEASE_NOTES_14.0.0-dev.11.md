# Atelier 14.0.0-dev.11 — Migration & Dependency Inventory

## Scope

Eleventh V14 development milestone. Dev.11 deliberately pauses automatic extraction and introduces a machine-validated migration inventory so deeper legacy boundaries are selected by state ownership, dependency surface, testability and regression risk rather than by convenience.

## Added

- `src/v14/migration-inventory.json` — structured legacy-boundary inventory and migration policy.
- `tools/v14_migration_inventory.py` — fail-closed inventory validator.
- `tools/test_v14_migration_inventory.py` — policy regression suite.
- CI version synchronization between the V14 manifest, migration inventory and generated artifact.
- CI enforcement of the single authorized next migration.

## Policy

The inventory excludes these ownership boundaries from opportunistic extraction by default:

- project persistence;
- project schema;
- geometry;
- rendering.

A `selected-next` boundary must be:

- low state risk;
- non-mutating;
- highly testable;
- no more than low browser coupling;
- compatible with an explicit legacy fallback.

## Inventory result

The inventory classifies twelve remaining boundaries.

The only boundary selected for the next milestone is:

**`dimension-formatting` → `14.0.0-dev.12`**

The target is the pure legacy `fmtDim` helper. It formats dimensions for the plan, inspector, annotations and transform HUD but owns no project state, persistence, geometry mutation, catalog state or renderer state.

High-risk boundaries such as persistence, schema validation, 2D/3D rendering and geometry remain blocked. Application orchestration, catalog ownership, project identity, broad project math helpers and exchange/export orchestration remain deferred.

## Validation

GitHub Actions run `34816530041` completed successfully.

Passed gates include:

- migration-inventory unit tests;
- inventory policy validation;
- exact single-candidate selection for `dimension-formatting`;
- source/build unit tests;
- frozen 13.2.0 baseline lock;
- byte-for-byte source round trip;
- generated artifact build and structure validation;
- Chromium desktop integration;
- Chromium mobile/touch integration;
- Firefox desktop integration;
- WebKit desktop integration;
- controlled offline/PWA reload;
- development artifact upload.

Generated artifact: `atelier-v14-dev.11`.

## Production impact

None. Production remains Atelier 13.2.0 on `main`. V14 remains an uncertified development branch, and V14 automation does not satisfy the outstanding V13.3.1 physical-device evidence requirement.
