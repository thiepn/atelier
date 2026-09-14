# Atelier V14 Development Architecture

## Status

Current audited checkpoint: **14.0.0-dev.19**.

V14 is an uncertified successor-development line on `v14-development`. Production remains Atelier **13.2.0** at `https://thiepn.github.io/atelier/`.

The application architecture is frozen at **8 modules and 7 exact legacy bridges**. Dev.13 onward is stabilization/release infrastructure; persistence, schema, geometry, rendering, catalog state and command execution remain legacy-owned.

## Frozen application boundary

### V14 modules

1. `shell/notifications.js`
2. `shell/dialogs.js`
3. `shell/commands.js`
4. `shell/files.js`
5. `shell/icons.js`
6. `shell/text.js`
7. `shell/units.js`
8. `dev-status/dev-status.js` — development packaging only

### Exact bridges

Seven exact bridges remain: notifications, dialogs, commands, files, icons, text escaping and dimension formatting.

No new bridge or stateful ownership migration is permitted during stabilization.

## Build and certification pipeline

```text
frozen 13.2.0 index.html + sw.js
        │
        ├── source-lock + byte-for-byte reconstruction
        ├── exact bridges
        ▼
v14-dist (development)
        │  atelier-v14-dev-*
        │  own-cache-only worker reads
        ▼
v14-rc (stripped release candidate)
        │  atelier-v14-rc-*
        │  no dev diagnostics
        │  productionEligible=false
        ▼
versioned immutable staging package
        │
        ├── exact RC hashes
        ├── generated physical runner
        ├── staging-status.json
        ▼
v14-rc-staging/<version>/
        │
        ├── live HTTPS verification
        ├── physical-device evidence
        ├── prior-release gate
        ├── production update/recovery
        └── rollback/data-preservation certification
```

Production promotion is never automatic.

## Service-worker cache isolation

The audit identified a cross-cache correctness risk caused by origin-wide `caches.match(...)` calls. Production and V14 staging share one origin, so a response cached by the frozen production worker could otherwise be returned to a V14 worker.

Dev.18/19 hardening therefore requires:

- all V14 runtime reads use the worker's own named cache;
- generated workers contain no residual `caches.match(...)` reads;
- production cache namespaces remain preserved but unread by V14;
- a browser regression deliberately poisons the production cache and proves V14 never consumes the poisoned response;
- RC status records `ownCacheLookupOnly: true`.

This is a packaging/runtime-isolation fix, not an application ownership migration.

## Immutable staging topology

Current candidate:

- app: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/app/`
- runner: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/acceptance.html?v=14.0.0-dev.19`
- status: `https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/staging-status.json`

Identity:

- RC version: `14.0.0-dev.19`
- index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- service-worker SHA-256: `796f11fe4d8a5142b94a28600a5fb7cccf24039c6f73fc4f77879121121aa7e3`
- cache: `atelier-v14-rc-14.0.0-dev.19`

Each candidate is stored under its versioned directory and cannot be overwritten with different bytes. Dev.18 and dev.19 remain preserved. The obsolete unversioned dev.17 alias was removed after the dev.19 audit.

The frozen production root is checked before publication and independently over public HTTPS after publication.

## Physical evidence contract v3

The five required real targets remain:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v3`.

Each evidence file binds:

- RC version;
- index/SW SHA-256;
- RC cache identity;
- candidate origin;
- exact immutable candidate URL;
- exact cache-busted runner URL;
- exact staging-status URL;
- target label/id;
- device/OS/browser/tester metadata;
- timezone-aware capture timestamp;
- the exact required result set;
- tester attestation;
- deterministic evidence fingerprint.

The validator rejects missing/extra/duplicate results, wrong candidate paths, wrong target labels, malformed timestamps and tampered fingerprints.

Generated report/signoff output paths are excluded from subsequent evidence scans, making validation idempotent without ignoring arbitrary malformed JSON.

## Promotion-state separation

The release-candidate packager keeps distinct states:

- prior-release gate readiness;
- V14 physical readiness;
- cutover eligibility;
- final production promotion readiness.

The RC itself always reports `productionEligible: false` until the complete production cutover certification exists. Current blockers include both the unresolved V13.3.1 gate and explicit V14 physical/cutover requirements.

## Browser / device simulation coverage

The automated integration matrix now includes:

- Chromium desktop;
- Chromium mobile/touch;
- Firefox desktop;
- WebKit desktop;
- WebKit phone/touch;
- WebKit tablet/touch.

Dev.19 corrected a WebKit touch smoke-harness return-contract defect discovered during the audit. All six projects pass in workflow `34895451320`.

Automated WebKit is not a substitute for real Safari physical evidence.

## CI publication boundary

The workflow is split into:

1. a read-only validation/build job; and
2. a separate write-enabled staging publication job that runs only after validation passes.

The publication job:

- downloads the already-validated staging artifact;
- checks frozen production root hashes;
- refuses to overwrite an existing immutable candidate with different bytes;
- writes only `v14-rc-staging/<version>/`;
- verifies the public HTTPS candidate and frozen production root afterward.

## Validation checkpoint

Primary audited workflow: **`34895451320` — PASS**.

Passed gates include:

- deterministic source/build tests;
- migration/stabilization policy;
- strict evidence validator + output idempotence;
- fail-closed production promotion;
- six-browser matrix;
- development offline PWA;
- development cross-cache poison regression;
- RC Chromium/offline/cache isolation;
- physical-runner browser/export/validator compatibility;
- immutable staging publication;
- live HTTPS exact-candidate verification;
- production root immutability.

## Milestone history

- dev.1–dev.12: controlled low-state extraction
- dev.13: stabilization freeze
- dev.14: isolated V14 development worker/cache
- dev.15: RC packaging boundary
- dev.16: V14 RC certification infrastructure
- dev.17: live HTTPS staging + physical evidence runner
- dev.18: cache-isolation / immutable-staging / strict v3 evidence audit hardening
- **dev.19: expanded WebKit audit, harness correction, validator output idempotence and full audit closeout**

## Current certification state

- Automated/tooling: **PASS**
- HTTPS staging: **LIVE / VERIFIED**
- Real V14 physical evidence: **0/5**
- V13.3.1 physical evidence: **0/5**
- `runtimeMayAdvanceToV14`: **false**
- V14 production promotion: **BLOCKED**
- Production runtime: **13.2.0**

The next legitimate release work is genuine physical-device evidence and later cutover/rollback certification, not additional application extraction.
