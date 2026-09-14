# Atelier 14.0.0-dev.19 — Test Report

## Result

**PASS — automated/tooling release-hardening gate**

Workflow: `34895451320`

Validated source revision: `cc86e74485850750ff2a3c1affdd0eae4199fd48`

This report does not count as physical-device acceptance.

## Deterministic / policy gates

- source/build unit tests: PASS
- migration/stabilization policy: PASS
- frozen 13.2.0 baseline verification: PASS
- byte-for-byte source round trip: PASS
- exact bridge/build identity checks: PASS
- strict RC evidence-validator self-test: PASS
- validator output idempotence: PASS
- production-promotion fail-closed test: PASS

## Browser matrix

- Chromium desktop: PASS
- Chromium mobile/touch: PASS
- Firefox desktop: PASS
- WebKit desktop: PASS
- WebKit phone/touch: PASS
- WebKit tablet/touch: PASS

## Offline / cache gates

- development offline PWA reload: PASS
- development cross-cache poison regression: PASS
- stripped RC Chromium startup: PASS
- stripped RC offline reload: PASS
- stripped RC own-cache isolation: PASS

## Physical-runner tooling

- automatic RC/status/hash verification: PASS
- browser-generated evidence JSON export: PASS
- evidence schema v3: PASS
- validator compatibility: PASS
- synthetic evidence remains non-counting: PASS

## Staging / publication

- immutable dev.19 staging artifact: PASS
- publication to versioned candidate path: PASS
- existing-candidate overwrite protection: PASS
- live HTTPS exact-RC verification: PASS
- frozen production `index.html` verification: PASS
- frozen production `sw.js` verification: PASS
- obsolete unversioned dev.17 staging alias removed after successful publication: PASS

## Artifact digests

- `atelier-v14-dev.19`: `b7ec8343350179c16ac16086714e3135bdd707de6cd51956fe1ad6ce10286fb1`
- `atelier-v14-dev.19-rc`: `5a8227b639819703185fbb917976328402c0de111197a0f6fcd38a591793b1fd`
- `atelier-v14-dev.19-staging`: `e5597fb6bc73150fb4108dd724524056cb42b7a2e20dcec8f31356ae61f5d639`

## RC identity

- index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- service-worker SHA-256: `796f11fe4d8a5142b94a28600a5fb7cccf24039c6f73fc4f77879121121aa7e3`
- cache: `atelier-v14-rc-14.0.0-dev.19`

## External gates not satisfied by this report

- V14 physical evidence: **0/5**
- V13.3.1 prior physical sign-off: **0/5**
- runtime advancement authorization: **false**
- production update/recovery: pending
- rollback/data preservation: pending
- production promotion: **blocked**
