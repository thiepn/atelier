# Atelier Space Studio 13.2.0 — Production Deployment & Real-Device Acceptance

## Purpose
V13.2 closes the production-deployment phase: it hardens touch targets, formalizes the production GitHub Pages origin, strengthens service-worker update rollback, validates keyboard/touch accessibility, and records production/external acceptance without claiming engines or physical devices that were not actually executed.

## User-facing changes
- All currently visible mobile/touch controls meet the 32 px minimum interaction target in the automated mobile acceptance viewport.
- Release certification now reports the expected production URL, whether the current page is running on that origin, HTTPS status, expected service-worker cache, and cache identity.
- Production release exports use V13.2 filenames.

## PWA/update hardening
- Interrupted service-worker installs delete the partial V13.2 cache and leave the prior production cache untouched.
- Stale Atelier caches are deleted only after a successful worker activation.
- Worker status reports stale cache identities.
- `PING`, `GET_STATUS`, `VERIFY_CORE`, `ACTIVATE_UPDATE`, and `CLEAR_STALE_CACHES` are available for diagnostics/recovery.
- Service-worker code remains isolated from project data stores.

## Compatibility
- App release: 13.2.0
- Project schema: V10
- Accepted project schemas: V1–V10
- PWA cache: `atelier-space-studio-13.2.0`
- Production URL: `https://thiepn.github.io/atelier/`
- No project migration required.
