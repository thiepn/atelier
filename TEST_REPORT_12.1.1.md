# Atelier Space Studio 12.1.1 — Validation Report

Test date: 12 September 2026.

## Build under test

- Application version: **12.1.1**
- Project schema: **V10**
- Catalog: **1,003 objects / 36 categories**
- Service-worker cache: `atelier-space-studio-12.1.1`

## Executed regression suites

| Suite | Result |
|---|---:|
| V12.1.1 Professional Studio | **26 / 26** |
| V12.1.1 Final Audit Regression | **20 / 20** |
| V12.1.1 Usability & Workflow | **32 / 32** |
| V11.9 Project Management on V12.1.1 | **18 / 18** |
| V11.9 Lifecycle / Data Safety on V12.1.1 | **7 / 7** |
| V11.8 Visual Interaction on V12.1.1 | **19 / 19** |
| Forced WebGL2 Renderer | **7 / 7** |
| Browser capability/fallback regression | **17 / 17** |
| Service-worker lifecycle contract | **11 / 11** |
| Cross-browser core — Chromium | **10 / 10** |
| **Executed total** | **167 / 167** |

## New acceptance evidence

### Browser capability fallbacks — 17/17

Verified with browser capabilities deliberately removed or constrained:

- application boots without `BroadcastChannel`;
- application boots without `requestIdleCallback` and uses timer paths;
- native save falls back to editable JSON download when `showSaveFilePicker` is unavailable;
- native open falls back to the standard file input when `showOpenFilePicker` is unavailable;
- `Meta+S` exercises the macOS-style save modifier path;
- forced WebGL2 absence selects the software renderer and 3D remains usable;
- a touch-enabled 390 × 844 mobile browser context can select plan objects;
- touch mobile layout has no horizontal overflow;
- no captured runtime faults in these fallback profiles.

### Service-worker contract — 11/11

Executed `sw.js` in an isolated service-worker contract harness and verified:

- install creates the 12.1.1 cache;
- all five core shell resources are precached;
- activation deletes the old 12.1.0 cache;
- activation claims clients;
- `ACTIVATE_UPDATE` invokes `skipWaiting()`;
- unrelated messages do not invoke `skipWaiting()`;
- offline navigation falls back to the cached application shell;
- offline missing assets return an error response, not HTML;
- same-origin runtime responses are cached before the fetch lifecycle resolves;
- non-GET requests are not intercepted.

### Cross-browser core harness

The reusable Playwright harness executed **10/10** core checks in available Chromium:

- V12.1.1 boot;
- V10 project schema;
- 2D switching;
- object selection;
- Ctrl+S;
- command palette;
- export preflight dialog;
- clean desktop runtime;
- 390 px overflow;
- clean 390 px runtime.

The same harness attempted Firefox and WebKit and recorded both as **SKIPPED — engine binary unavailable**, not as passes.

## PWA HTTPS acceptance harness

`PWA_HTTPS_ACCEPTANCE_12_1_1.py` contains the complete browser-origin lifecycle test:

1. load/cache V12.1.0 on HTTPS;
2. validate secure context, service-worker control and manifest installability;
3. stage V12.1.1 as a waiting worker;
4. apply the update using the actual Preferences UI;
5. verify controller change, reload, project/storage preservation and old-cache cleanup;
6. close the browser process;
7. relaunch the same profile offline;
8. verify cached app, manifest and icon availability;
9. verify a missing asset is not replaced by HTML.

The harness could not execute here because Chromium is managed with `URLBlocklist: ["*"]`; network-origin navigation returns `ERR_BLOCKED_BY_ADMINISTRATOR`. `TEST_V12_1_1_PWA_ACCEPTANCE.py` detects this policy and reports an infrastructure skip.

## Browser-engine provisioning attempt

`python -m playwright install firefox webkit` was attempted. Browser provisioning failed before download because Playwright CDN hostnames could not be resolved (`EAI_AGAIN`). No Firefox/WebKit result is therefore claimed.

## Remaining acceptance boundary

Not executed in this environment:

- Firefox / Gecko runtime;
- Safari / WebKit runtime;
- iOS Safari hardware;
- trusted/public HTTPS PWA install UI and standalone launch;
- real-origin service-worker update/offline lifecycle;
- human NVDA / VoiceOver session.

No known P0/P1 application defect remains in the executed Chromium/static/contract matrix after the V12.1.1 PWA fixes.
