# Atelier V14 Development Architecture

## Status

V14 is an **uncertified successor-development cycle** on branch `v14-development`.

Current validated checkpoint: **14.0.0-dev.16**.

Production remains Atelier **13.2.0** on `main`. V13.3.1 physical-device sign-off remains unresolved and continues to block runtime advancement to V14.

## Architecture objective

V14 incrementally extracted small, deterministic, low-state boundaries from the locked Atelier 13.2.0 monolith while preserving exact legacy fallback behavior.

That extraction program is now closed for stabilization. The application architecture is frozen at:

- 8 V14 modules;
- 7 exact legacy bridges;
- unchanged project schema;
- unchanged persistence ownership;
- unchanged geometry and renderer ownership;
- unchanged catalog/application-state ownership.

Further application ownership may move only after a new explicit architecture decision.

## Frozen source architecture

### Modules

1. `shell/notifications.js`
2. `shell/dialogs.js`
3. `shell/commands.js`
4. `shell/files.js`
5. `shell/icons.js`
6. `shell/text.js`
7. `shell/units.js`
8. `dev-status/dev-status.js` — development packaging only

### Legacy bridges

1. notifications
2. dialogs
3. commands
4. files
5. icons
6. text escaping
7. dimension formatting

`dev-status` is intentionally stripped from release-candidate packaging; that is a packaging transformation, not another application migration.

## Build, RC and certification flow

```text
index.html + sw.js
locked Atelier 13.2.0 baseline
        │
        ├── source-lock verification
        ├── byte-for-byte source round trip
        │
        ▼
tools/v14_build.py
        │
        ├── 7 exact bridges
        ├── frozen 8-module development surface
        ├── atelier-v14-dev-<version> worker/cache
        │
        ▼
v14-dist
validated development artifact
        │
        ▼
tools/v14_rc_package.py
        │
        ├── strip V14 DEV diagnostics
        ├── remove diagnostics from offline core
        ├── switch to atelier-v14-rc-<version>
        ├── evaluate prior-release certification state
        │
        ▼
v14-rc
release-candidate artifact
        │
        ├── v14-build-manifest.json
        ├── v14-rc-status.json
        │
        ▼
V14 RC physical acceptance
        │
        ├── candidate version
        ├── index SHA-256
        ├── service-worker SHA-256
        ├── RC cache identity
        ├── one normalized HTTPS candidate origin
        │
        ▼
5 genuine physical targets
        │
        ▼
physical sign-off
        │
        ├── prior-release gate
        ├── production-origin verification
        ├── update recovery
        ├── rollback recovery
        ├── project-data preservation
        │
        ▼
production promotion eligibility
```

No stage in this flow rewrites production automatically.

## Exact bridge policy

`atelier-v14-exact-patch-v1` remains the controlled boundary for helpers hidden inside the legacy IIFE.

1. Every bridge declares exact source text and occurrence count.
2. Missing or duplicate matches fail the build.
3. Patch inputs and replacements are hash-bound in the build manifest.
4. Original legacy behavior remains available as fallback.
5. Application-owned state remains private to the legacy runtime.
6. Stabilization forbids new bridges unless this architecture phase is explicitly reopened.

## Milestone history

### dev.1 — Reproducible source boundary

Added the source lock, lossless extraction/rebuild tooling and byte-for-byte baseline invariant.

### dev.2 — Deterministic module overlay

Added ordered V14 modules, exact patches and deterministic build manifests.

### dev.3 — Shell notifications

Moved announcements, toasts and status presentation into a low-state V14 service.

### dev.4 — Command palette

Moved palette presentation/search while leaving command execution legacy-owned.

### dev.5 — Browser file utilities

Moved browser download delivery and safe filename normalization.

### dev.6 — Dialog shell

Moved modal DOM and focus behavior through narrow adapters.

### dev.7 — Real-browser shell integration

Added generated-artifact Chromium integration.

### dev.8 — Cross-browser, responsive and offline gate

Added Chromium desktop/mobile, Firefox, WebKit and controlled offline validation.

### dev.9 — SVG icon renderer

Moved pure SVG serialization while leaving icon registry data legacy-owned.

### dev.10 — Text escaping

Centralized HTML/SVG/XML escaping behind exact fallback bridges.

### dev.11 — Migration/dependency inventory

Introduced machine-readable risk policy and blocked opportunistic migration of high-risk ownership boundaries.

Validated workflow: `34816530041`.

### dev.12 — Dimension formatting

Moved pure `fmtDim` presentation formatting without moving unit state, numeric editing or geometry.

Validated workflow: `34871518856`.

### dev.13 — Stabilization freeze

Enforced:

- `phase: stabilization`;
- frozen module/patch lists;
- no new legacy bridges;
- no selected-next migration;
- production cutover disabled.

Validated workflow: `34872208603`.

### dev.14 — Isolated V14 development offline shell

Activated generated V14-specific service-worker identity and isolated `atelier-v14-dev-*` caches while preserving the 13.2.0 production cache namespace.

Validated workflow: `34872824160`.

### dev.15 — Release-candidate packaging boundary

Added `tools/v14_rc_package.py` and a separate stripped RC artifact.

RC packaging:

- removes development diagnostics;
- uses `atelier-v14-rc-*`;
- emits RC status metadata;
- reads the prior-release certification state;
- fails closed when production eligibility is requested while blockers remain.

Validated workflow: `34882066210`.

### dev.16 — RC certification infrastructure

Dev.16 adds V14-specific certification without changing the frozen application architecture.

#### Physical acceptance plan

`acceptance/v14-rc-required-targets.json` defines five genuine targets:

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Every evidence file is bound to the exact candidate by:

- RC version;
- RC `index.html` SHA-256;
- RC `sw.js` SHA-256;
- RC cache identity;
- one normalized HTTPS candidate origin.

#### Physical evidence validator

`acceptance/validate_v14_rc_acceptance.py` verifies:

- evidence fingerprints;
- exact RC identity;
- target identity;
- tester/device/browser metadata;
- required PASS results;
- duplicate-target rejection;
- single candidate-origin consistency.

It exposes three independent readiness states:

- `PHYSICAL_READY`
- `PRIOR_RELEASE_GATE_READY`
- `PROMOTION_READY`

This intentionally permits genuine V14 RC testing before the prior-release gate is resolved without allowing that testing to authorize production promotion.

The validator can emit a V14 RC physical sign-off after 5/5 real evidence is valid even when `PROMOTION_READY=false`.

Synthetic fixtures are accepted only by the validator self-test and never count as physical-device evidence.

#### Cutover and rollback plan

`acceptance/v14-rc-cutover-plan.json` requires all of the following before production promotion:

- prior-release final sign-off;
- V14 RC physical sign-off;
- exact production index/SW/cache identity;
- production HTTPS-origin verification;
- existing-project survival after update;
- installed-PWA update recovery;
- offline cold start after update;
- rollback to Atelier 13.2.0;
- existing-project survival after rollback;
- stale-cache cleanup without project-data loss.

Automatic promotion is forbidden.

#### V14 certification matrix

`CERTIFICATION_MATRIX_14.0.0-rc.json` now records V14's own certification state instead of inferring it from V13 files.

Validated workflow: **`34883134671`**.

## Current validation layers

### 1. Deterministic source/build

- baseline hash lock;
- byte-for-byte source round trip;
- exact bridge matching;
- hashed assets and build manifests;
- deterministic development worker generation.

### 2. Stabilization and packaging policy

- frozen architecture;
- isolated development and RC caches;
- mandatory diagnostic stripping in RC;
- mandatory prior-signoff gate before promotion;
- mandatory V14 RC physical/cutover plans.

### 3. Isolated behavior

Independent tests cover all migrated shell/helper services.

### 4. Integrated development runtime

Validated in:

- Chromium desktop;
- Chromium mobile/touch;
- Firefox desktop;
- WebKit desktop;
- controlled Chromium offline mode.

### 5. RC runtime

Validated for:

- diagnostic-free startup;
- RC cache identity;
- service-worker control;
- offline reload;
- preserved V14 shell/helper services.

### 6. Certification tooling

Validated for:

- five-target positive synthetic fixture;
- identity-tamper rejection;
- duplicate-target rejection;
- sign-off fingerprint generation;
- physical/promotion gate separation;
- fail-closed promotion.

## Current V14 RC certification state

Automated/tooling state: **PASS**.

Real-world state:

- real V14 RC physical evidence: **0/5**;
- HTTPS staging candidate origin: **not provisioned**;
- V13.3.1 prior-release sign-off: **blocked**;
- production-origin V14 verification: **not run**;
- update recovery against production origin: **not run**;
- rollback recovery: **not run**;
- V14 promotion ready: **false**.

Current V14-specific state is recorded in `CERTIFICATION_MATRIX_14.0.0-rc.json`.

## Production boundary

Production remains Atelier **13.2.0** on `main`.

The V14 branch must not be merged, deployed as the production successor or described as production-certified while any promotion prerequisite remains unresolved.

## Next milestone

The next legitimate milestone is **dev.17 — HTTPS Staging Origin & Physical Evidence Capture Runner**.

Dev.17 should not alter application ownership. Its purpose should be to make real RC evidence collection practical:

1. establish or prepare a non-production HTTPS candidate origin for the exact RC artifact;
2. keep the production origin untouched;
3. provide a browser-based evidence runner that loads `v14-rc-status.json`, verifies candidate identity and presents the target-specific checklist;
4. export evidence matching `atelier-v14-rc-physical-acceptance-evidence-v1`;
5. never auto-mark physical tests PASS;
6. keep promotion blocked until both the prior-release and V14 RC physical/cutover gates genuinely pass.
