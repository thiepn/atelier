# Atelier Space Studio

> **V14 DEVELOPMENT BRANCH** — `v14-development` currently builds **14.0.0-dev.12** as a separate, uncertified artifact. Nothing on this branch changes the live production runtime. Production remains Atelier **13.2.0** from `main` while V13.3.1 physical acceptance is still incomplete.

Atelier is a local-first browser space-planning studio with a static PWA deployment.

## V14 development status

V14 is being developed as an isolated successor line rather than by mutating the frozen production file.

Completed development milestones:

1. **14.0.0-dev.1 — Reproducible source boundary** — lossless source segmentation, byte-for-byte rebuild verification and frozen 13.2.0 source lock.
2. **14.0.0-dev.2 — Deterministic module overlay** — separate V14 artifact, ordered module manifest, hashed build manifest, path guards and development diagnostics.
3. **14.0.0-dev.3 — Shell notifications** — modular announcements, toasts and status handling with exact legacy fallback.
4. **14.0.0-dev.4 — Command palette** — modular opening/search/rendering while preserving legacy execution contracts.
5. **14.0.0-dev.5 — Browser file utilities** — modular browser download delivery and safe-filename behavior.
6. **14.0.0-dev.6 — Dialog shell** — modular modal DOM/focus behavior through narrow state adapters.
7. **14.0.0-dev.7 — Browser shell integration gate** — generated artifact exercised through real Chromium and manifest-driven CI.
8. **14.0.0-dev.8 — Cross-browser, responsive & offline gate** — Chromium desktop/mobile, Firefox, WebKit, keyboard/focus/accessibility checks and controlled offline reload.
9. **14.0.0-dev.9 — Modular SVG icon renderer** — pure icon serialization moved behind an exact legacy bridge while the locked icon registry remains legacy-owned.
10. **14.0.0-dev.10 — Modular text escaping service** — repeated HTML/SVG/XML escaping centralized behind four exact legacy fallbacks.
11. **14.0.0-dev.11 — Migration & dependency inventory** — machine-validated risk inventory that authorizes only explicit low-state migrations and blocks opportunistic persistence/schema/geometry/rendering extraction.
12. **14.0.0-dev.12 — Dimension formatting boundary** — pure `fmtDim` behavior moved into a modular units service with exact legacy fallback and cross-browser/offline verification.

Build the current development artifact with:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir dist --force
```

Architecture: `ARCHITECTURE_V14.md`

### Current V14 validation

Dev.12 passes:

- source and overlay unit tests;
- migration-inventory policy tests and validator;
- independent behavior tests for notifications, dialogs, commands, file utilities, icons, text escaping and dimension formatting;
- exact locked-baseline verification;
- byte-for-byte source round trip;
- all exact bridge occurrence checks;
- generated artifact structure checks;
- Chromium desktop integration;
- Chromium 390×844 mobile/touch integration;
- Firefox desktop integration;
- WebKit desktop integration;
- responsive overflow, dialog focus/Escape and accessibility assertions;
- direct HTML/XML escaping probes;
- direct metric/imperial dimension-formatting probes;
- controlled Chromium offline/PWA reload with all V14 shell/helper services restored;
- artifact upload.

Latest validated artifact: `atelier-v14-dev.12` from workflow run `34871518856`.

The migration inventory intentionally has no `selected-next` boundary after dev.12. A new architecture decision is required before another legacy extraction begins.

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
- `RELEASE_NOTES_14.0.0-dev.1.md` through `RELEASE_NOTES_14.0.0-dev.11.md`
- `TEST_REPORT_13.2.0.md`
- `TEST_REPORT_13.3.1.md`
- `TEST_REPORT_14.0.0-dev.3.md` through `TEST_REPORT_14.0.0-dev.11.md`
- `CERTIFICATION_MATRIX_13.3.1.json`
