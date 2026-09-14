# Atelier 14.0.0-dev.16 — RC Certification Infrastructure

## Scope

Dev.16 adds V14-specific release-candidate certification infrastructure without changing the frozen application architecture and without promoting V14 to production.

## Added

- `acceptance/v14-rc-required-targets.json` — five-target V14 RC physical acceptance plan.
- `acceptance/validate_v14_rc_acceptance.py` — hash-bound physical evidence validator and aggregator.
- `acceptance/v14-rc-cutover-plan.json` — explicit staging, production cutover and rollback gates.
- `acceptance/V14_RC_CERTIFICATION.md` — certification runbook.
- `CERTIFICATION_MATRIX_14.0.0-rc.json` — V14-specific current certification state.

## Evidence identity

Every V14 RC physical evidence file is bound to the exact candidate through:

- RC version;
- RC `index.html` SHA-256;
- RC `sw.js` SHA-256;
- RC cache identity;
- one normalized HTTPS candidate origin.

All files in one evidence set must use the same candidate origin.

## Separate readiness gates

The validator deliberately distinguishes:

- `PHYSICAL_READY` — five valid real-device evidence files;
- `PRIOR_RELEASE_GATE_READY` — the prior-release certification gate allows V14 advancement;
- `PROMOTION_READY` — both gates are true.

Physical RC evidence may therefore be collected before the prior-release gate is resolved, but it cannot authorize promotion by itself.

## Cutover policy

The cutover plan requires, in addition to V14 physical acceptance:

- prior-release final sign-off;
- exact production artifact identity;
- production-origin verification;
- installed-PWA update recovery;
- offline cold start after update;
- rollback to the 13.2.0 baseline;
- project data surviving update and rollback;
- stale-cache cleanup without project-data loss.

Automatic promotion remains forbidden.

## Validation

GitHub Actions run `34883134671` completed successfully.

Passed gates include:

- source/build and migration-policy suites;
- RC certification-plan structure validation;
- V14 RC physical validator synthetic self-test;
- tampered identity rejection and duplicate-target rejection inside the self-test;
- fail-closed promotion gate;
- Chromium desktop/mobile, Firefox and WebKit development matrix;
- development offline reload;
- stripped RC Chromium startup and offline reload;
- development and RC artifact upload.

Synthetic fixtures verify validator behavior only and do not count as physical evidence.

## Current certification state

- V14 RC real physical evidence: **0/5**.
- Staging HTTPS candidate origin: **not provisioned**.
- Prior V13.3.1 release gate: **blocked**.
- Production cutover: **blocked**.
- V14 promotion ready: **false**.

## Production impact

None. Production remains Atelier 13.2.0 on `main`.
