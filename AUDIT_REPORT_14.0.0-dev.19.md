# Atelier V14 — dev.19 Audit Report

## Outcome

The V14 code/build/staging/certification infrastructure audit is complete for `14.0.0-dev.19`.

Automated/tooling status: **PASS**.

Production promotion status: **BLOCKED** pending real external certification.

## Findings and resolutions

### 1. Cross-cache service-worker reads — fixed

**Finding:** V14 workers inherited origin-wide `caches.match(...)` behavior. Because production and staging share an origin, a production-cache response could be returned to V14.

**Resolution:** generated V14 workers now read only their own named cache. Residual global cache-match calls fail the build. A poison regression verifies isolation online/offline.

### 2. Evidence policy/validator mismatch — fixed

**Finding:** the staging policy claimed exact candidate URL binding while the older validator primarily bound the host origin.

**Resolution:** evidence v3 binds the exact immutable candidate URL, cache-busted runner URL, staging-status URL, hashes, cache and target metadata.

### 3. Mutable staging path — fixed

**Finding:** the first staging layout reused an unversioned path.

**Resolution:** candidates use immutable `v14-rc-staging/<version>/` paths. Existing candidate paths cannot be overwritten with different bytes. Prior versioned candidates are preserved.

### 4. Promotion state ambiguity — fixed

**Finding:** prior-release readiness could be confused with final V14 production eligibility.

**Resolution:** RC packaging always keeps final `productionEligible=false` until V14 physical and cutover gates also pass. Explicit V14 physical/cutover blockers remain present.

### 5. WebKit touch smoke defect — fixed

**Finding:** the command-palette smoke helper internally validated success but returned `undefined`; the WebKit touch branch then asserted its return value.

**Resolution:** the helper now returns the already-validated value. WebKit desktop, phone/touch and tablet/touch all pass.

### 6. Evidence validator re-ingested generated output — fixed

**Finding:** a report/signoff written into the evidence directory could be scanned as if it were device evidence on a later run.

**Resolution:** explicitly supplied RC status/report/signoff paths are excluded from evidence discovery. The self-test proves repeated validation is idempotent without ignoring arbitrary malformed evidence files.

### 7. CI publication permissions — fixed

**Finding:** validation and publication were previously coupled more tightly than necessary.

**Resolution:** validation/build uses read-only permissions; a separate dependent publication job receives write permission only after all validation gates pass.

### 8. Stale unversioned staging alias — fixed

**Finding:** the obsolete dev.17 unversioned runner/app/status remained public after immutable candidates were introduced.

**Resolution:** those obsolete files were removed from `main` in commit `29e6c0fe07e1ab3b74f90d5fb58aaa643c3f32fb`. Only versioned dev.18/dev.19 candidates remain under `v14-rc-staging/`.

## Validation evidence

Primary workflow `34895451320` passed every automated gate, including the six-browser matrix, offline checks, cache poisoning regression, strict evidence validation, physical-runner tooling, immutable publish and live HTTPS verification.

The live dev.19 candidate remains bound to:

- index SHA-256 `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- service-worker SHA-256 `796f11fe4d8a5142b94a28600a5fb7cccf24039c6f73fc4f77879121121aa7e3`
- cache `atelier-v14-rc-14.0.0-dev.19`

## Not fixable through automated audit

These are not software defects and remain deliberately unresolved:

- V14 real physical evidence: **0/5**
- V13.3.1 real physical evidence: **0/5**
- `runtimeMayAdvanceToV14`: **false**
- V14 production-origin update/recovery verification: pending
- rollback verification: pending
- project-data preservation through update/rollback: pending

No automated test or synthetic fixture may substitute for these gates.
