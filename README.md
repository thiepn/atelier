# Atelier Space Studio

> **V14 DEVELOPMENT BRANCH** — `v14-development` currently builds **14.0.0-dev.15** development and release-candidate artifacts. Production remains Atelier **13.2.0** on `main`.

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
14. **dev.14 — Isolated V14 offline shell** — generated V14-specific development worker/cache and baseline-cache preservation.
15. **dev.15 — Release-candidate packaging boundary** — stripped RC artifact, isolated RC cache, machine-readable certification gate and fail-closed promotion check.

Build the normal development artifact with:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir v14-dist --force
```

Package its RC form with:

```bash
python tools/v14_rc_package.py --repo-root . --source-dir v14-dist --output-dir v14-rc --force
```

Architecture: `ARCHITECTURE_V14.md`

## Current validation

Latest successful workflow: **`34882066210`**.

Uploaded artifacts:

- `atelier-v14-dev.15`
- `atelier-v14-dev.15-rc`

The current gate passes:

- source and overlay tests;
- migration/stabilization policy validation;
- RC packaging-policy validation;
- all shell/helper behavior tests;
- frozen 13.2.0 baseline and byte-for-byte source reconstruction;
- exact bridge and architecture-freeze checks;
- isolated development worker/cache validation;
- RC diagnostics removal;
- isolated `atelier-v14-rc-*` RC worker/cache validation;
- Chromium desktop integration;
- Chromium mobile/touch integration;
- Firefox desktop integration;
- WebKit desktop integration;
- development offline reload;
- stripped RC Chromium startup and offline reload;
- separate development and RC artifact uploads.

## RC packaging state

Dev.15 creates a genuine **release-candidate-shaped artifact**, but it does not promote it.

The RC package:

- removes `dev-status/dev-status.css` and `dev-status/dev-status.js`;
- removes the visible `V14 DEV` diagnostics surface;
- uses `atelier-v14-rc-<version>` rather than the development cache namespace;
- removes diagnostic files from its service-worker offline core;
- emits `v14-rc-status.json`;
- records `artifactKind: release-candidate` and `diagnosticsStripped: true`;
- calculates `productionEligible` from the prior certification state.

The current RC correctly reports `productionEligible: false`.

Current promotion blockers are:

1. `prior-final-signoff-not-pass`
2. `runtime-advance-not-authorized`
3. `physical-evidence-incomplete`

A packaging attempt with `--require-production-eligible` fails closed while those blockers exist.

## Architecture state

The V14 module/bridge surface remains frozen during stabilization.

V14 owns only generic post-bootstrap shell/helper presentation plus V14 packaging. Legacy 13.2.0 remains authoritative for project persistence, backups, schema/validation, geometry, rendering, catalog/application state, command execution, identity and domain export semantics.

No stateful subsystem was migrated in dev.13, dev.14 or dev.15.

## Production / cutover status

**V14 is not deployed and production cutover is not authorized.**

`CERTIFICATION_MATRIX_13.3.1.json` still records:

- physical evidence: **0/5**;
- final sign-off: blocked;
- `runtimeMayAdvanceToV14: false`.

Production therefore remains:

- Runtime: Atelier **13.2.0**
- URL: `https://thiepn.github.io/atelier/`
- Release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- Production PWA cache: `atelier-space-studio-13.2.0`

Required V13.3.1 physical targets remain:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Automated V14 browser/PWA testing does not substitute for those physical tests.

## Key files

- `ARCHITECTURE_V13.md`
- `ARCHITECTURE_V14.md`
- `src/source.lock.json`
- `src/v14/manifest.json`
- `src/v14/migration-inventory.json`
- `tools/v14_build.py`
- `tools/v14_rc_package.py`
- `.github/workflows/v14-source-roundtrip.yml`
- `RELEASE_NOTES_14.0.0-dev.15.md`
- `TEST_REPORT_14.0.0-dev.15.md`
- `production.config.json`
- `CERTIFICATION_MATRIX_13.3.1.json`
