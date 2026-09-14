# Atelier 14.0.0-dev.15 — Release-Candidate Packaging Boundary

## Scope

Dev.15 adds a reproducible release-candidate packaging path without promoting V14 to production or changing the frozen module/bridge architecture.

## Added

- `tools/v14_rc_package.py` packages a validated V14 development artifact into a stripped RC artifact.
- RC packaging removes `dev-status` CSS/JS and their HTML references.
- RC service-worker cache identity uses `atelier-v14-rc-<version>` and removes diagnostics from the offline core.
- `v14-rc-status.json` records RC identity, hashes and certification-gate state.
- The RC build manifest records `artifactKind: release-candidate`, `diagnosticsStripped: true` and `productionEligible`.
- The migration/stabilization policy now machine-validates the RC cache namespace, diagnostics stripping and prior-signoff requirement.

## Certification boundary

The RC packager reads `CERTIFICATION_MATRIX_13.3.1.json` and currently reports three blockers:

1. prior final sign-off is not PASS;
2. runtime advance to V14 is not authorized;
3. physical evidence remains incomplete.

A `--require-production-eligible` packaging attempt therefore fails closed. Dev.15 does not weaken or bypass the V13.3.1 production gate.

## Validation

GitHub Actions run `34882066210` completed successfully.

Validated paths include:

- deterministic development build;
- stripped RC packaging;
- development and RC service-worker/cache isolation;
- RC diagnostics removal;
- RC certification metadata;
- fail-closed production eligibility gate;
- Chromium desktop/mobile, Firefox and WebKit development matrix;
- development offline reload;
- stripped RC Chromium startup and offline reload;
- separate development and RC artifact uploads.

## Production impact

None. Production remains Atelier 13.2.0 on `main`. The generated RC artifact is a candidate package only and is explicitly not eligible for production promotion while the certification gate is blocked.
