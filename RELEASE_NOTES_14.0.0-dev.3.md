# Atelier 14.0.0-dev.3 — Shell Notification Migration

## Scope

Third V14 development milestone. This remains an isolated, uncertified development artifact built from the locked Atelier 13.2.0 baseline.

## Added

- Audited exact-patch bridge support in `tools/v14_build.py`.
- Fail-closed occurrence validation for every source bridge.
- Patch-source, find-string and replacement SHA-256 records in the V14 build manifest.
- Modular shell notification service: `src/v14/shell/notifications.js`.
- Legacy `announce`, `toast`, and save-status implementations retained as boot-time fallback.
- Dependency-free notification behavior test in Node.
- CI verification that all three legacy notification bridge points match exactly once.

## Notification service

The V14 shell service now owns post-bootstrap behavior for:

- accessibility announcements;
- toast content and lifetime;
- save/status messages;
- error announcements.

The original IIFE functions delegate to the module only after `AtelierV14Shell.notifications` is available. If the module is absent or has not loaded yet, the original implementation continues to run.

## Validation

GitHub Actions run `34793861206` completed successfully with:

- source round-trip tests;
- overlay-build tests;
- JavaScript syntax checks;
- notification behavior tests;
- frozen baseline verification;
- real 13.2.0 artifact build;
- exact bridge verification;
- development artifact upload.

Generated artifact: `atelier-v14-dev.3`.

## Production impact

None. Production `main`, production Atelier 13.2.0 and the V13.3.1 certification state remain unchanged.
