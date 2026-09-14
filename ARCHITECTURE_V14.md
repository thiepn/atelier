# Atelier V14 Development Architecture

## Status

Current validated checkpoint: **14.0.0-dev.17**.

V14 is an uncertified successor-development line on `v14-development`. Production remains Atelier **13.2.0** at `https://thiepn.github.io/atelier/`.

The application architecture is frozen. Dev.13–dev.17 are stabilization, packaging and certification milestones; they do not move additional application ownership.

## Frozen application boundary

### V14 modules

1. `shell/notifications.js`
2. `shell/dialogs.js`
3. `shell/commands.js`
4. `shell/files.js`
5. `shell/icons.js`
6. `shell/text.js`
7. `shell/units.js`
8. `dev-status/dev-status.js` — development packaging only

### Exact legacy bridges

Seven bridges remain frozen: notifications, dialogs, commands, files, icons, text escaping and dimension formatting.

Legacy Atelier 13.2.0 remains authoritative for persistence/backups, schema/normalization, geometry/precision, 2D/3D rendering, catalog/application state, command execution, project identity, numeric editing/stored unit state and domain export semantics.

## Artifact pipeline

```text
frozen Atelier 13.2.0 index.html + sw.js
        │
        ├── source-lock verification
        └── byte-for-byte reconstruction
        ▼
tools/v14_build.py
        │
        ├── exact bridge application
        ├── frozen development modules
        └── atelier-v14-dev-* worker/cache
        ▼
v14-dist
        │
        ▼
tools/v14_rc_package.py
        │
        ├── remove dev-status
        ├── remove diagnostics from offline core
        └── atelier-v14-rc-* worker/cache
        ▼
v14-rc
        │
        ▼
tools/v14_staging_package.py
        │
        ├── verify exact RC index/SW hashes
        ├── copy exact RC to v14-rc-staging/app/
        ├── generate physical acceptance runner
        └── emit staging-status.json
        ▼
HTTPS staging subtree on GitHub Pages
```

None of these steps replaces the production root runtime.

## Dev.17 HTTPS staging topology

Production and staging share the GitHub Pages host but use different paths:

- production: `https://thiepn.github.io/atelier/`
- staged RC: `https://thiepn.github.io/atelier/v14-rc-staging/app/`
- physical runner: `https://thiepn.github.io/atelier/v14-rc-staging/acceptance.html`
- staging identity: `https://thiepn.github.io/atelier/v14-rc-staging/staging-status.json`

The staging service worker is physically located below `v14-rc-staging/app/`; its normal scope is therefore the candidate subtree, not the production root.

Staging publication changes only `v14-rc-staging/**` on `main`. Before and after publication CI checks the production root against the frozen 13.2.0 hashes.

## Exact dev.17 candidate

- version: `14.0.0-dev.17`
- cache: `atelier-v14-rc-14.0.0-dev.17`
- index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- service-worker SHA-256: `bf668c12ecf58f3d7c11cf0ceb98dada3edf6408947ab42caf5aff56802c7043`

The physical runner independently fetches the staged index/SW and requires both hashes to match before evidence can be exported.

## Physical acceptance contract

The acceptance plan is `acceptance/v14-rc-required-targets.json`.

Required targets:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v2`.

Every real evidence file binds the candidate version, index hash, service-worker hash, RC cache identity, staging host origin, exact staged candidate URL, exact runner URL, device/browser metadata, target results and tester attestation. A deterministic fingerprint detects modification after export.

The runner never auto-marks a physical test PASS. CI-generated synthetic evidence is tooling-only and never counts toward physical readiness.

## Readiness separation

V14 deliberately keeps these states independent:

- **PHYSICAL_READY** — all five genuine V14 RC targets pass.
- **PRIOR_RELEASE_GATE_READY** — V13.3.1 allows runtime advancement to V14.
- **PROMOTION_READY** — physical, prior-release and later production cutover gates all permit promotion.

Staging is allowed before prior-release sign-off. Production promotion is not.

## Cutover and rollback boundary

`acceptance/v14-rc-cutover-plan.json` still requires before production promotion:

- V13.3.1 final sign-off;
- V14 RC physical sign-off;
- exact V14 production artifact identity;
- production HTTPS-origin verification;
- installed-PWA update recovery;
- offline cold start after update;
- rollback to frozen 13.2.0;
- project data surviving both update and rollback;
- safe stale-cache cleanup.

Automatic promotion is forbidden.

## Validation layers

1. **Source/build** — source lock, byte-for-byte round trip, exact bridges and deterministic packaging.
2. **Architecture policy** — frozen modules/patches; stateful migration blocked.
3. **Module behavior** — independent shell/helper tests.
4. **Development runtime** — Chromium desktop/mobile, Firefox, WebKit and offline Chromium.
5. **RC runtime** — diagnostics absent, isolated RC worker/cache, offline RC reload.
6. **Physical-runner tooling** — automatic candidate hash verification, checklist gating, JSON export and validator compatibility.
7. **Live HTTPS staging** — public candidate/runner/status fetch, exact RC hash verification and frozen production-root verification.

Primary dev.17 workflow: **`34885183276` — PASS**.

Independent live HTTPS verification: **`34885579138` — PASS**.

## Milestone history

- dev.1: reproducible source boundary
- dev.2: deterministic module overlay
- dev.3: notifications
- dev.4: command palette
- dev.5: browser file utilities
- dev.6: dialog shell
- dev.7: real-browser shell integration
- dev.8: cross-browser/responsive/offline gate
- dev.9: SVG icon renderer
- dev.10: text escaping
- dev.11: migration/dependency inventory
- dev.12: dimension formatting
- dev.13: stabilization freeze
- dev.14: isolated V14 development offline shell
- dev.15: release-candidate packaging boundary
- dev.16: RC certification infrastructure
- **dev.17: HTTPS staging origin & physical evidence capture runner**

## Current certification state

Automated/tooling: **PASS**.

HTTPS staging: **LIVE / VERIFIED**.

Real V14 RC physical evidence: **0/5**.

V13.3.1 prior-release gate: **BLOCKED**.

V14 promotion ready: **FALSE**.

Production runtime: **Atelier 13.2.0**.

The next legitimate activity is genuine physical-device evidence capture. Do not invent a dev.18 architecture migration merely to continue the version sequence.
