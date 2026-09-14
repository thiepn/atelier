# Atelier 14.0.0-dev.19 — Audit Hardening

## Scope

Dev.19 closes the V14 release-infrastructure audit. It does not migrate additional application ownership and does not authorize production promotion.

## Fixes

- Added/validated own-cache-only V14 service-worker reads; origin-wide cache matching is forbidden.
- Added production-cache poison regression coverage for development and RC workers.
- Hardened immutable versioned staging under `v14-rc-staging/<version>/`.
- Bound physical evidence v3 to exact candidate, runner and staging-status URLs plus RC hashes/cache.
- Kept `productionEligible=false` until V14 physical and cutover certification are complete.
- Expanded automated WebKit coverage to desktop, phone/touch and tablet/touch.
- Fixed the WebKit touch smoke helper return-contract defect discovered by the audit.
- Made physical-evidence validation idempotent when its generated report/signoff files live beside evidence.
- Separated read-only validation from write-enabled staging publication.
- Verified live HTTPS RC identity and the frozen 13.2.0 production root after publication.
- Removed the obsolete unversioned dev.17 staging alias while preserving immutable dev.18/dev.19 candidates.

## Current RC identity

- Version: `14.0.0-dev.19`
- Index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- Service-worker SHA-256: `796f11fe4d8a5142b94a28600a5fb7cccf24039c6f73fc4f77879121121aa7e3`
- Cache: `atelier-v14-rc-14.0.0-dev.19`
- Production eligible: `false`

## Validation

Primary audited workflow: `34895451320` — PASS.

All automated browser, offline, cache-isolation, evidence-runner, immutable publication and live HTTPS gates passed.

## Remaining external gates

- V14 physical evidence: **0/5**
- V13.3.1 physical evidence: **0/5**
- `runtimeMayAdvanceToV14`: **false**
- production update/recovery certification: pending
- rollback/data-preservation certification: pending
- V14 production promotion: **blocked**

Production remains Atelier 13.2.0.
