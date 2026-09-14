# Atelier V14 RC Certification

## Current physical-testing entry point

Use this runner on each genuine target:

`https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/acceptance.html?v=14.0.0-dev.19`

Exact candidate:

`https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/app/`

Staging identity:

`https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/staging-status.json`

## Exact candidate identity

- version: `14.0.0-dev.19`
- cache: `atelier-v14-rc-14.0.0-dev.19`
- index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- service-worker SHA-256: `796f11fe4d8a5142b94a28600a5fb7cccf24039c6f73fc4f77879121121aa7e3`
- service-worker reads: own-cache only
- production eligibility: false

The runner verifies the live RC status plus staged index/SW bytes before evidence can become ready.

## Required real targets

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Automated Chromium/Firefox/WebKit tests do not satisfy these physical targets.

## Evidence contract v3

Schema: `atelier-v14-rc-physical-acceptance-evidence-v3`.

Every exported file binds:

- acceptance milestone;
- exact RC version;
- exact `index.html` hash;
- exact `sw.js` hash;
- RC cache identity;
- candidate host origin;
- exact immutable candidate URL;
- exact cache-busted runner URL;
- exact staging-status URL;
- target id + label;
- tester/device/OS/browser metadata;
- timezone-aware timestamp;
- the complete target-specific result set;
- explicit tester attestation;
- deterministic evidence fingerprint.

The validator rejects wrong versions/URLs/hashes/cache, target-label mismatch, extra/missing/duplicate results, malformed timestamps, missing metadata and fingerprint tampering.

## Validator

```bash
python acceptance/validate_v14_rc_acceptance.py \
  --rc-status /path/to/v14-rc-status.json \
  --evidence-dir /path/to/physical-evidence \
  --write-report /path/to/physical-evidence/v14-rc-physical-report.json \
  --write-signoff /path/to/physical-evidence/v14-rc-physical-signoff.json
```

Generated report/signoff files and the explicitly supplied RC status path are excluded from evidence discovery, so repeated validation is idempotent even when outputs live inside the evidence directory. Arbitrary malformed JSON is still rejected.

The validator reports physical readiness and cutover eligibility separately. A 5/5 physical result still does not authorize production promotion.

## Cache isolation

Production and staging share an origin. V14 workers therefore use only their own named cache for reads and never use origin-wide `caches.match(...)` lookups.

CI includes a cross-cache poison regression that injects a malicious matching response into the frozen production cache namespace and verifies that the V14 development/RC worker never consumes it online or offline.

## Immutable staging

Each candidate is published under `v14-rc-staging/<version>/`.

Publication refuses to replace an existing versioned candidate with different bytes. Dev.18 and dev.19 remain preserved. The old unversioned dev.17 staging alias was removed after the audit.

The publication job runs only after the read-only validation job succeeds. It verifies the frozen production root before writing and verifies the live HTTPS RC plus production root afterward.

## Current automated state

Workflow **`34895451320` — PASS**.

Passed:

- strict validator self-test and output idempotence;
- six-browser development matrix;
- development offline PWA;
- development cross-cache poison regression;
- stripped RC Chromium/offline/cache-isolation smoke;
- physical-runner browser export + validator compatibility;
- immutable staging publication;
- live HTTPS exact-RC verification;
- frozen production-root verification.

## Cutover boundary

`v14-rc-cutover-plan.json` still requires before production promotion:

- V13.3.1 prior-release final sign-off;
- V14 physical sign-off;
- exact V14 production artifact identity;
- production HTTPS-origin verification;
- installed-PWA update recovery;
- offline cold start after update;
- rollback to Atelier 13.2.0;
- project data surviving update and rollback;
- safe stale-cache cleanup.

Automatic promotion is forbidden.

## Current real-world state

- HTTPS staging: **LIVE / VERIFIED**
- V14 automated/tooling validation: **PASS**
- Real V14 physical evidence: **0/5**
- V13.3.1 physical evidence: **0/5**
- V13.3.1 runtime advancement authorization: **false**
- V14 production promotion: **BLOCKED**
- Production runtime: **Atelier 13.2.0**
