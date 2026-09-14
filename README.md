# Atelier Space Studio

> **V14 DEVELOPMENT BRANCH** — `v14-development` currently builds **14.0.0-dev.8** as a separate, uncertified artifact. Nothing on this branch changes the live production runtime. Production remains Atelier **13.2.0** from `main` while V13.3.1 physical acceptance is still incomplete.

Atelier is a local-first browser space-planning studio with a static PWA deployment.

## V14 development status

V14 is being developed as an isolated successor line rather than by mutating the frozen production file.

Completed development milestones:

1. **14.0.0-dev.1 — Reproducible source boundary**
   - lossless `index.html` source segmentation;
   - byte-for-byte rebuild verification;
   - frozen 13.2.0 source lock.
2. **14.0.0-dev.2 — Deterministic module overlay**
   - separate V14 artifact;
   - ordered module manifest;
   - hashed build manifest;
   - path/traversal guards;
   - development diagnostics.
3. **14.0.0-dev.3 — Shell notifications**
   - exact-patch bridge system;
   - modular announcements, toasts and save/status handling;
   - legacy fallback retained.
4. **14.0.0-dev.4 — Command palette**
   - modular palette opening/search/rendering;
   - existing command execution contract preserved.
5. **14.0.0-dev.5 — Browser file utilities**
   - modular browser download delivery;
   - existing safe-filename behavior preserved.
6. **14.0.0-dev.6 — Dialog shell**
   - modular modal DOM/focus behavior;
   - private IIFE state retained through narrow adapters.
7. **14.0.0-dev.7 — Browser shell integration gate**
   - generated artifact driven in real Chromium;
   - legacy keyboard/action paths exercised through V14 bridges;
   - uncaught page/console error gate;
   - manifest-driven, concurrency-safe CI.
8. **14.0.0-dev.8 — Cross-browser, responsive & offline integration gate**
   - Chromium desktop, Chromium mobile/touch, Firefox and WebKit integration matrix;
   - responsive horizontal-overflow gate;
   - keyboard/Escape/focus-restoration and shell accessibility checks;
   - controlled service-worker offline reload of the generated V14 artifact.

Build the current development artifact with:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir dist --force
```

Architecture: `ARCHITECTURE_V14.md`

### Current V14 validation

Dev.8 passes:

- source and overlay unit tests;
- independent behavior tests for all four shell services;
- exact locked-baseline verification;
- byte-for-byte source round-trip;
- exact bridge verification;
- generated artifact structure checks;
- Chromium desktop shell integration;
- Chromium 390×844 mobile/touch shell integration;
- Firefox desktop shell integration;
- WebKit desktop shell integration;
- responsive overflow, dialog focus/Escape and accessibility assertions;
- controlled Chromium offline/PWA reload with the V14 overlay restored from cache;
- artifact upload pipeline.

Validated workflow run: `34815078492`.

## Production status

**Production runtime: 13.2.0 — V13.3.1 physical evidence completion/sign-off milestone active**

V13.2 is deployed from `main` on GitHub Pages.

- Production URL: `https://thiepn.github.io/atelier/`
- Production release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- Production `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- Production `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`
- PWA cache: `atelier-space-studio-13.2.0`

The production runtime has not changed during V13.3, V13.3.1, or V14 branch development.

## V13.3 / V13.3.1 physical acceptance

Recommended physical runner: `acceptance/DEVICE_ACCEPTANCE_13.3.1.html`

Final production sign-off still requires five genuine physical targets:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

The required final validator result remains:

`SIGNOFF_READY=true`

Until genuine evidence from all five targets exists, V13.3.1 production sign-off remains **BLOCKED**. Automated V14 browser testing does not substitute for those physical tests.

V14 development may continue on its isolated branch, but **V14 must not be promoted, merged as the production successor, or described as production-certified until the relevant release gates are satisfied.**

## Architecture and release files

- `ARCHITECTURE_V13.md`
- `ARCHITECTURE_V14.md`
- `production.config.json`
- `RELEASE_NOTES_13.2.0.md`
- `RELEASE_NOTES_13.3.1.md`
- `RELEASE_NOTES_14.0.0-dev.1.md`
- `RELEASE_NOTES_14.0.0-dev.2.md`
- `RELEASE_NOTES_14.0.0-dev.3.md`
- `RELEASE_NOTES_14.0.0-dev.4.md`
- `RELEASE_NOTES_14.0.0-dev.5.md`
- `RELEASE_NOTES_14.0.0-dev.6.md`
- `RELEASE_NOTES_14.0.0-dev.7.md`
- `RELEASE_NOTES_14.0.0-dev.8.md`
- `TEST_REPORT_13.2.0.md`
- `TEST_REPORT_13.3.1.md`
- `TEST_REPORT_14.0.0-dev.3.md`
- `TEST_REPORT_14.0.0-dev.4.md`
- `TEST_REPORT_14.0.0-dev.5.md`
- `TEST_REPORT_14.0.0-dev.6.md`
- `TEST_REPORT_14.0.0-dev.7.md`
- `TEST_REPORT_14.0.0-dev.8.md`
- `CERTIFICATION_MATRIX_13.3.1.json`
