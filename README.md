# Atelier Space Studio

> **V14 DEVELOPMENT BRANCH** — `v14-development` currently builds **14.0.0-dev.16** development and release-candidate artifacts. Production remains Atelier **13.2.0** on `main`.

Atelier is a local-first browser space-planning studio with a static PWA deployment.

## V14 development status

V14 is being developed as an isolated successor line rather than by mutating the frozen production runtime.

Completed milestones:

1. **dev.1 — Reproducible source boundary**
2. **dev.2 — Deterministic module overlay**
3. **dev.3 — Shell notifications**
4. **dev.4 — Command palette**
5. **dev.5 — Browser file utilities**
6. **dev.6 — Dialog shell**
7. **dev.7 — Real-browser shell integration**
8. **dev.8 — Cross-browser/responsive/offline gate**
9. **dev.9 — SVG icon renderer**
10. **dev.10 — Text escaping**
11. **dev.11 — Migration/dependency inventory**
12. **dev.12 — Dimension formatting**
13. **dev.13 — Stabilization freeze**
14. **dev.14 — Isolated V14 offline shell**
15. **dev.15 — Release-candidate packaging boundary**
16. **dev.16 — RC certification infrastructure** — V14-specific physical-evidence identity, five-target validator, certification matrix and cutover/rollback gates.

Build the development artifact:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir v14-dist --force
```

Package the RC artifact:

```bash
python tools/v14_rc_package.py --repo-root . --source-dir v14-dist --output-dir v14-rc --force
```

Validate real V14 RC physical evidence later with:

```bash
python acceptance/validate_v14_rc_acceptance.py \
  --rc-status /path/to/v14-rc-status.json \
  --evidence-dir /path/to/evidence \
  --write-report v14-rc-physical-report.json \
  --write-signoff v14-rc-physical-signoff.json
```

## Current validation

Latest successful workflow: **`34883134671`**.

Uploaded artifacts:

- `atelier-v14-dev.16`
- `atelier-v14-dev.16-rc`

Current automated status:

- source/build regression: PASS;
- migration/stabilization policy: PASS;
- RC packaging: PASS;
- V14 RC certification-plan structure: PASS;
- RC physical-validator synthetic self-test: PASS, tooling-only;
- promotion fail-closed gate: PASS;
- Chromium desktop/mobile: PASS;
- Firefox automated: PASS;
- WebKit automated: PASS;
- development offline reload: PASS;
- stripped RC Chromium startup/offline reload: PASS;
- both artifacts uploaded: PASS.

See `TEST_REPORT_14.0.0-dev.16.md` and `CERTIFICATION_MATRIX_14.0.0-rc.json`.

## V14 RC certification state

Dev.16 separates three different questions:

- **Physical ready** — five genuine V14 RC device/browser evidence files pass.
- **Prior-release gate ready** — V13.3.1 permits runtime advancement to V14.
- **Promotion ready** — both conditions above are true and later cutover gates pass.

Current real-world state:

- V14 RC physical evidence: **0/5**;
- HTTPS staging candidate origin: **not provisioned**;
- V13.3.1 prior-release gate: **blocked**;
- V14 production-origin verification: **not run**;
- update/rollback certification: **not run**;
- promotion ready: **false**.

Synthetic fixtures used by CI validate the evidence validator only. They do not count toward 0/5 physical evidence.

## Physical targets

V14 RC requires:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Evidence is bound to the candidate's version, `index.html` SHA-256, `sw.js` SHA-256, RC cache identity and one normalized HTTPS candidate origin.

## Cutover / rollback boundary

`acceptance/v14-rc-cutover-plan.json` requires, before any production promotion:

- prior-release final sign-off;
- V14 RC physical sign-off;
- exact production artifact identity;
- production HTTPS-origin verification;
- installed-PWA update recovery;
- offline cold start after update;
- rollback to the 13.2.0 baseline;
- project data surviving update and rollback;
- stale-cache cleanup without project-data loss.

Automatic promotion is forbidden.

## Architecture state

The eight-module / seven-bridge application architecture remains frozen. Dev.13–dev.16 add stabilization, packaging and certification infrastructure only; no persistence, schema, geometry, rendering, catalog/application state or command-execution ownership moved.

## Production status

**Production runtime: Atelier 13.2.0.**

- URL: `https://thiepn.github.io/atelier/`
- Release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- PWA cache: `atelier-space-studio-13.2.0`

`CERTIFICATION_MATRIX_13.3.1.json` still records physical evidence **0/5** and `runtimeMayAdvanceToV14: false`.

## Key files

- `ARCHITECTURE_V14.md`
- `src/v14/manifest.json`
- `src/v14/migration-inventory.json`
- `tools/v14_build.py`
- `tools/v14_rc_package.py`
- `acceptance/v14-rc-required-targets.json`
- `acceptance/validate_v14_rc_acceptance.py`
- `acceptance/v14-rc-cutover-plan.json`
- `acceptance/V14_RC_CERTIFICATION.md`
- `CERTIFICATION_MATRIX_14.0.0-rc.json`
- `RELEASE_NOTES_14.0.0-dev.16.md`
- `TEST_REPORT_14.0.0-dev.16.md`
