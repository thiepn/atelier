# Atelier Space Studio

**Production runtime: 13.2.0 — V13.3.1 physical evidence completion/sign-off milestone active**

Atelier is a local-first browser space-planning studio with a static PWA deployment. The application runtime remains byte-frozen at 13.2.0 while V13.3/V13.3.1 collect and validate real-device production evidence.

## Production status

V13.2 is deployed from `main` on GitHub Pages.

- Production URL: `https://thiepn.github.io/atelier/`
- Production release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- Clean release tree: `858762f96799ff6ae522174c5e4bedc701f7df94`
- Production `index.html` blob: `324884caabe3e52963ac3c7a081c627372ccff71`
- Production `sw.js` blob: `cd920b34f76528b0779e87d19c14e01a111841fd`
- PWA cache: `atelier-space-studio-13.2.0`
- `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`

The runtime has not changed during V13.3 or V13.3.1.

## V13.3 / V13.3.1 physical acceptance

V13.3 introduced the real-device acceptance runner. V13.3.1 adds the completion/aggregation layer that turns the five independent evidence files into one deterministic final production sign-off.

### Collect evidence

- Physical runner: `acceptance/DEVICE_ACCEPTANCE_13.3.0.html`
- Required target contract: `acceptance/required-targets.json`

### Complete sign-off

- Final Sign-off Center: `acceptance/SIGNOFF_CENTER_13.3.1.html`
- Offline/CI validator: `acceptance/validate_acceptance.py`
- V13.3.1 matrix: `CERTIFICATION_MATRIX_13.3.1.json`
- Final sign-off state: `FINAL_RELEASE_SIGNOFF_13.3.1.md`

V13.3.1 deliberately continues to accept V13.3.0 evidence. A tester does not need to repeat a genuine physical test because the aggregation tooling changed.

The five mandatory physical targets are:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Final sign-off is mechanically blocked until all five distinct evidence files validate against the frozen production hashes and every required step is PASS.

## Sign-off integrity

The final sign-off layer verifies:

- evidence schema and acceptance milestone
- production URL
- runtime release
- exact `index.html` and `sw.js` SHA-256
- internal evidence fingerprint
- tester identity and attestation
- every target-specific required PASS result
- unique target identity

The final sign-off manifest additionally binds each source evidence file by its raw SHA-256. Editing an evidence file after sign-off therefore breaks the manifest relationship.

## Automated baseline

Before physical acceptance, the frozen runtime already has:

- Full inherited application regression matrix: **325/325 PASS**
- Aggregate automated result: **458 PASS / 2 environment SKIP**
- Mobile touch targets: **37/37 ≥ 32 px**
- Presentation-quality WebGL PNG export: **PASS**
- GitHub Pages production deployment: **PASS**
- Interrupted PWA update recovery: **PASS**

These automated/simulated results do not substitute for the five physical targets.

## Current final sign-off state

**BLOCKED — 0/5 physical evidence files are available in the current implementation conversation.**

Required final validator result:

`SIGNOFF_READY=true`

Only then should `FINAL PRODUCTION SIGN-OFF` be changed to PASS and a V14 feature cycle begin.

## Architecture and production files

- `ARCHITECTURE_V13.md`
- `production.config.json`
- `RELEASE_NOTES_13.2.0.md`
- `TEST_REPORT_13.2.0.md`
- `CERTIFICATION_MATRIX_13.2.0.json`
- `CERTIFICATION_MATRIX_13.3.0.json`
- `CERTIFICATION_MATRIX_13.3.1.json`
- `RELEASE_NOTES_13.3.1.md`
- `TEST_REPORT_13.3.1.md`
