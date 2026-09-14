# Atelier Space Studio

> **V14 DEVELOPMENT BRANCH** — current validated checkpoint: **14.0.0-dev.17**. Production remains Atelier **13.2.0** on `main`.

Atelier is a local-first browser space-planning studio with a static PWA deployment.

## V14 milestone status

Completed milestones:

1. dev.1 — Reproducible source boundary
2. dev.2 — Deterministic module overlay
3. dev.3 — Shell notifications
4. dev.4 — Command palette
5. dev.5 — Browser file utilities
6. dev.6 — Dialog shell
7. dev.7 — Real-browser shell integration
8. dev.8 — Cross-browser/responsive/offline gate
9. dev.9 — SVG icon renderer
10. dev.10 — Text escaping
11. dev.11 — Migration/dependency inventory
12. dev.12 — Dimension formatting
13. dev.13 — Stabilization freeze
14. dev.14 — Isolated V14 offline shell
15. dev.15 — Release-candidate packaging boundary
16. dev.16 — RC certification infrastructure
17. **dev.17 — HTTPS staging origin & physical evidence capture runner**

The application architecture remains frozen at eight modules and seven exact legacy bridges. Dev.17 changes staging/certification infrastructure only.

## Live V14 RC staging

- **Physical evidence runner:** `https://thiepn.github.io/atelier/v14-rc-staging/acceptance.html`
- **Staged RC:** `https://thiepn.github.io/atelier/v14-rc-staging/app/`
- **Staging identity:** `https://thiepn.github.io/atelier/v14-rc-staging/staging-status.json`
- **Production:** `https://thiepn.github.io/atelier/`

The staging app is an isolated subtree on the existing GitHub Pages HTTPS host. Its service worker is scoped to the staging app path and uses the V14 RC cache namespace.

### Exact staged candidate

- Version: `14.0.0-dev.17`
- Cache: `atelier-v14-rc-14.0.0-dev.17`
- `index.html` SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- `sw.js` SHA-256: `bf668c12ecf58f3d7c11cf0ceb98dada3edf6408947ab42caf5aff56802c7043`

The runner verifies these hashes automatically before it can mark evidence ready.

## Physical evidence workflow

Use the live runner on each genuine target:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

For each target:

1. open the physical runner;
2. confirm candidate identity verification passes;
3. open the staged RC from the runner;
4. perform every target-specific test on the actual device/browser;
5. mark each result truthfully;
6. fill tester/device/OS/browser details;
7. attest the test;
8. export the evidence JSON.

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v2`.

Real physical evidence currently remains **0/5**. Automated/synthetic tests never count toward that number.

## Validation

Primary dev.17 workflow: **`34885183276` — PASS**.

Independent live HTTPS verification: **`34885579138` — PASS**.

Validated:

- source/build and migration-policy regression;
- development + stripped RC generation;
- Chromium desktop/mobile, Firefox and WebKit automated integration;
- development and RC offline reload;
- exact staging RC hashes;
- physical runner identity verification;
- browser-generated evidence export;
- evidence-validator compatibility;
- public HTTPS staging identity;
- public production root remains frozen at Atelier 13.2.0.

See `TEST_REPORT_14.0.0-dev.17.md` and `CERTIFICATION_MATRIX_14.0.0-rc.json`.

## Production boundary

The staging publication adds only `v14-rc-staging/**` to `main`. The production root remains unchanged:

- `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`
- production cache: `atelier-space-studio-13.2.0`

V14 promotion is still blocked by:

1. V13.3.1 final sign-off not PASS;
2. runtime advancement to V14 not authorized;
3. V14 physical evidence incomplete.

No automatic production promotion is permitted.

## Key files

- `ARCHITECTURE_V14.md`
- `src/v14/manifest.json`
- `src/v14/migration-inventory.json`
- `tools/v14_build.py`
- `tools/v14_rc_package.py`
- `tools/v14_staging_package.py`
- `acceptance/v14-rc-required-targets.json`
- `acceptance/validate_v14_rc_acceptance.py`
- `acceptance/v14-rc-cutover-plan.json`
- `acceptance/V14_RC_CERTIFICATION.md`
- `CERTIFICATION_MATRIX_14.0.0-rc.json`
- `RELEASE_NOTES_14.0.0-dev.17.md`
- `TEST_REPORT_14.0.0-dev.17.md`
