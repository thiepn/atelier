# Atelier Space Studio

> **V14 DEVELOPMENT BRANCH** — `v14-development` currently builds **14.0.0-dev.14** as a separate, uncertified artifact. Production remains Atelier **13.2.0** on `main`.

Atelier is a local-first browser space-planning studio with a static PWA deployment.

## V14 development status

V14 is being developed as an isolated successor line rather than by mutating the frozen production runtime.

Completed development milestones:

1. **dev.1 — Reproducible source boundary** — lossless extraction, byte-for-byte rebuild and frozen 13.2.0 source lock.
2. **dev.2 — Deterministic module overlay** — separate V14 artifact, ordered manifest, exact patches and hashed build manifest.
3. **dev.3 — Shell notifications** — announcements, toasts and status handling.
4. **dev.4 — Command palette** — opening/search/rendering while legacy execution contracts remain unchanged.
5. **dev.5 — Browser file utilities** — download delivery and safe filenames.
6. **dev.6 — Dialog shell** — modal DOM, focus and confirmation composition through narrow adapters.
7. **dev.7 — Real-browser shell integration** — generated artifact exercised in Chromium.
8. **dev.8 — Cross-browser/responsive/offline gate** — Chromium desktop/mobile, Firefox, WebKit and controlled offline reload.
9. **dev.9 — SVG icon renderer** — pure SVG serialization behind an exact fallback bridge.
10. **dev.10 — Text escaping** — centralized HTML/SVG/XML escaping behind exact fallback bridges.
11. **dev.11 — Migration/dependency inventory** — machine-validated risk policy for remaining legacy ownership.
12. **dev.12 — Dimension formatting** — pure `fmtDim` behavior moved into the units service.
13. **dev.13 — Stabilization freeze** — module/bridge architecture frozen; new legacy bridges and production cutover explicitly disallowed.
14. **dev.14 — Isolated V14 offline shell** — generated V14-specific service worker/cache, overlay pre-cache and baseline-cache preservation.

Build the current development artifact with:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir dist --force
```

Architecture: `ARCHITECTURE_V14.md`

## Current validation

The latest validated artifact is **`atelier-v14-dev.14`**, workflow run **`34872824160`**.

The current gate passes:

- source and overlay unit tests;
- migration-inventory policy tests and validation;
- behavior tests for notifications, dialogs, commands, files, icons, text escaping and dimensions;
- frozen 13.2.0 baseline verification;
- byte-for-byte source round trip;
- exact bridge occurrence checks;
- architecture-freeze enforcement;
- generated V14 service-worker identity/cache/core verification;
- Chromium desktop integration;
- Chromium 390×844 mobile/touch integration;
- Firefox desktop integration;
- WebKit desktop integration;
- responsive overflow, focus/Escape and accessibility checks;
- direct text and unit-formatting browser probes;
- controlled offline reload;
- V14 stale-cache cleanup without deleting the 13.2.0 baseline cache namespace;
- artifact upload.

## Current V14 architecture state

The V14 module/bridge surface is frozen during stabilization.

V14 currently owns post-bootstrap generic shell/helper behavior for:

- notifications/status;
- dialogs/focus;
- command-palette presentation/search;
- browser file delivery/naming;
- SVG icon serialization;
- HTML/SVG/XML escaping;
- dimension display formatting.

Legacy 13.2.0 still owns project persistence, backups, schema/validation, geometry, rendering, catalog/application state, command execution, project identity and domain export semantics.

The generated development service worker now uses an isolated `atelier-v14-dev-<version>` cache and pre-caches all V14 overlay assets. It does not use the production `atelier-space-studio-*` namespace for stale-cache deletion.

## Production / cutover status

**V14 is not production-ready and is not deployed.**

Current hard blockers include:

1. `CERTIFICATION_MATRIX_13.3.1.json` still records **0/5** physical targets and `runtimeMayAdvanceToV14: false`.
2. The V14 build manifest is intentionally `developmentOnly: true`.
3. `dev-status/` is still injected and visibly labels the artifact `V14 DEV`.
4. `production.config.json` still identifies release `13.2.0` and its production certification contract.
5. No V14 physical-device production acceptance has been completed.
6. No V14 production-origin cutover verification has been performed.

Therefore the stabilization policy keeps `allowProductionCutover: false` and has no `selected-next` migration boundary.

## Production status

**Production runtime: 13.2.0 — V13.3.1 physical evidence completion/sign-off remains blocked.**

- Production URL: `https://thiepn.github.io/atelier/`
- Production release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- Production `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- Production `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`
- Production PWA cache: `atelier-space-studio-13.2.0`

Required V13.3.1 physical targets remain:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

The required final validator result remains `SIGNOFF_READY=true` with five distinct valid physical targets.

Automated V14 browser/PWA tests do not substitute for those physical tests.

## Key architecture files

- `ARCHITECTURE_V13.md`
- `ARCHITECTURE_V14.md`
- `src/source.lock.json`
- `src/v14/manifest.json`
- `src/v14/migration-inventory.json`
- `production.config.json`
- `.github/workflows/v14-source-roundtrip.yml`
- `CERTIFICATION_MATRIX_13.3.1.json`
