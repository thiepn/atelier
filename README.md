# Atelier Space Studio

> **V14 DEVELOPMENT BRANCH** — current audited checkpoint: **14.0.0-dev.19**. Production remains Atelier **13.2.0** on `main`.

Atelier is a local-first browser space-planning studio with a static PWA deployment.

## V14 status

The V14 application architecture is frozen at **8 modules / 7 exact legacy bridges**. The stabilization line after dev.12 has focused on packaging, offline isolation, certification, staging and release hardening rather than moving more application state.

Current checkpoint: **14.0.0-dev.19**.

Primary validated workflow: **`34895451320` — PASS**.

### Current immutable staging candidate

- Runner: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/acceptance.html?v=14.0.0-dev.19`
- Candidate: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/app/`
- Status: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/staging-status.json`
- Version: `14.0.0-dev.19`
- Cache: `atelier-v14-rc-14.0.0-dev.19`
- `index.html` SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- `sw.js` SHA-256: `796f11fe4d8a5142b94a28600a5fb7cccf24039c6f73fc4f77879121121aa7e3`

The old unversioned dev.17 staging alias has been removed. Versioned dev.18 and dev.19 candidates remain preserved.

## Audit / hardening completed in dev.18–dev.19

The full audit found and fixed several release-blocking infrastructure defects:

- V14 workers now read only from their own named cache instead of using origin-wide `caches.match(...)` lookups.
- Cross-cache poison regression tests prove production-cache responses cannot leak into the V14 development or RC worker.
- Physical evidence is bound to the exact immutable candidate URL, cache-busted runner URL, staging-status URL, RC hashes and cache identity.
- Staging candidates are versioned and immutable; an existing candidate path cannot be overwritten with different bytes.
- RC packaging can never claim final production eligibility before V14 physical and cutover certification.
- WebKit coverage now includes desktop, phone-touch and tablet-touch projects.
- The WebKit touch smoke harness return-contract bug was corrected.
- The physical-evidence validator is output-safe/idempotent when its report and signoff files live beside the evidence JSON files.
- Staging publication uses a read-only validation job followed by a separate least-privilege write job.
- Live HTTPS verification checks the exact public RC and the frozen 13.2.0 production root after publication.
- The obsolete unversioned staging alias was removed from `main` without changing production root files.

## Automated validation

The dev.19 gate passes:

- deterministic source/build and migration-policy tests;
- exact baseline round-trip and bridge checks;
- strict RC evidence-validator self-tests;
- fail-closed production promotion gate;
- Chromium desktop;
- Chromium mobile/touch;
- Firefox desktop;
- WebKit desktop;
- WebKit phone/touch;
- WebKit tablet/touch;
- development offline PWA reload;
- development cross-cache poison regression;
- stripped RC Chromium startup/offline/cache isolation;
- physical evidence runner browser/export/validator compatibility;
- immutable staging artifact publication;
- live HTTPS candidate identity verification;
- frozen production-root verification.

Artifacts from workflow `34895451320`:

- `atelier-v14-dev.19`
- `atelier-v14-dev.19-rc`
- `atelier-v14-dev.19-staging`

## Physical certification

Required real targets:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v3`.

**Real V14 physical evidence remains 0/5.** Automated and synthetic tests never count toward that gate.

V13.3.1 also remains **0/5**, so `runtimeMayAdvanceToV14` is still false.

## Production boundary

Production is still Atelier **13.2.0**:

- URL: `https://thiepn.github.io/atelier/`
- release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`
- cache: `atelier-space-studio-13.2.0`

V14 production promotion remains **blocked** until the prior-release gate, 5/5 V14 physical evidence, production-origin update/recovery testing, rollback testing and project-data preservation gates genuinely pass.

## Key files

- `ARCHITECTURE_V14.md`
- `CERTIFICATION_MATRIX_14.0.0-rc.json`
- `src/v14/manifest.json`
- `src/v14/migration-inventory.json`
- `tools/v14_build.py`
- `tools/v14_rc_package.py`
- `tools/v14_staging_package.py`
- `tools/v14-cache-isolation.spec.js`
- `acceptance/v14-rc-required-targets.json`
- `acceptance/validate_v14_rc_acceptance.py`
- `acceptance/v14-rc-cutover-plan.json`
- `acceptance/V14_RC_CERTIFICATION.md`
- `RELEASE_NOTES_14.0.0-dev.19.md`
- `TEST_REPORT_14.0.0-dev.19.md`
