# V14 modules

## Current checkpoint

**14.0.0-dev.19** is the current audited V14 checkpoint.

The application architecture remains frozen at eight modules and seven exact legacy bridges. Dev.18–dev.19 are audit/release-hardening checkpoints and do not move stateful legacy ownership.

## Build pipeline

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir v14-dist --force
python tools/v14_rc_package.py --repo-root . --source-dir v14-dist --output-dir v14-rc --force
python tools/v14_staging_package.py --repo-root . --rc-dir v14-rc --output-dir v14-staging --force
```

The staging package is emitted to a versioned immutable path:

`v14-rc-staging/14.0.0-dev.19/`

## Frozen module surface

1. `shell/notifications.js`
2. `shell/dialogs.js`
3. `shell/commands.js`
4. `shell/files.js`
5. `shell/icons.js`
6. `shell/text.js`
7. `shell/units.js`
8. `dev-status/dev-status.js` — development artifact only

Seven exact legacy bridges remain frozen under `patches/`.

## Audit hardening

Current stabilization policy requires:

- no new legacy bridges;
- no production cutover;
- own-cache-only V14 service-worker reads;
- no cross-namespace cache reads;
- cross-cache poison regression coverage;
- diagnostics stripped from RC packaging;
- immutable versioned staging candidates;
- prior candidates preserved;
- cache-busted evidence runner URL;
- strict exact-URL/hash/cache evidence binding;
- live HTTPS staging verification;
- frozen production root verification;
- final production promotion always fail-closed until physical + cutover gates pass.

## Current live candidate

- Runner: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/acceptance.html?v=14.0.0-dev.19`
- Candidate: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/app/`
- Status: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/staging-status.json`
- Cache: `atelier-v14-rc-14.0.0-dev.19`
- Index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- SW SHA-256: `796f11fe4d8a5142b94a28600a5fb7cccf24039c6f73fc4f77879121121aa7e3`

The obsolete unversioned staging alias was removed. Dev.18 and dev.19 immutable candidates remain preserved.

## Evidence contract

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v3`.

The validator binds each evidence file to the exact immutable candidate, runner, status document, RC hashes/cache, target identity and full required test set. Generated report/signoff output files can safely live beside evidence without being re-ingested on later validator runs.

Five genuine targets remain required. Synthetic CI evidence is tooling-only.

## Validation

Workflow **`34895451320` — PASS**.

Automated coverage includes Chromium desktop/mobile, Firefox desktop, WebKit desktop/phone/tablet, development offline PWA, cross-cache poison regression, stripped RC offline/cache isolation, runner export/validator compatibility, immutable publication and live HTTPS verification.

Real V14 physical evidence: **0/5**.

Production promotion: **blocked**.

## Ownership boundary

Legacy runtime ownership still includes command execution, project persistence/backups, schema/validation, geometry/project math, identity generation, catalog/application state, numeric editing/project unit state, domain export semantics and 2D/3D rendering.

Do not resume stateful extraction during stabilization merely to increase modularization count.
