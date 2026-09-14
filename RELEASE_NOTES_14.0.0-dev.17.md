# Atelier 14.0.0-dev.17 — HTTPS Staging & Physical Evidence Runner

## Summary

Dev.17 makes genuine V14 RC physical testing practical without changing the frozen application architecture or promoting V14 to production.

## Added

- Isolated GitHub Pages staging path: `https://thiepn.github.io/atelier/v14-rc-staging/app/`.
- Physical acceptance runner: `https://thiepn.github.io/atelier/v14-rc-staging/acceptance.html`.
- Staging identity endpoint: `https://thiepn.github.io/atelier/v14-rc-staging/staging-status.json`.
- `tools/v14_staging_package.py` for deterministic RC staging packaging.
- Acceptance plan v2 with exact candidate URL and runner URL binding.
- Evidence schema `atelier-v14-rc-physical-acceptance-evidence-v2`.
- Browser smoke that exports an evidence file and passes it through the V14 RC validator.
- Independent live-HTTPS verification workflow.

## Staging safety

The staging publish writes only `v14-rc-staging/**` on `main`.

The workflow verifies the production root before and after publication against the frozen 13.2.0 hashes:

- `index.html`: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js`: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`

The staging RC has its own path-scoped service worker and `atelier-v14-rc-*` cache namespace.

## Validated candidate identity

- Version: `14.0.0-dev.17`
- RC cache: `atelier-v14-rc-14.0.0-dev.17`
- RC index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- RC service-worker SHA-256: `bf668c12ecf58f3d7c11cf0ceb98dada3edf6408947ab42caf5aff56802c7043`

## Validation

Primary dev.17 workflow: `34885183276` — PASS.

Independent live HTTPS verification: `34885579138` — PASS.

The validation covers the full development browser matrix, RC offline startup, physical runner identity verification, exported-evidence compatibility, exact public HTTPS RC hashes and frozen production-root hashes.

## Certification state

No physical-device result was fabricated or inferred from automated tests.

- Real V14 RC evidence: **0/5**
- Prior V13.3.1 release gate: **blocked**
- V14 promotion ready: **false**
- Production runtime: **Atelier 13.2.0**

The next actual work is real-device evidence capture using the dev.17 runner.
