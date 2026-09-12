# Atelier Space Studio 12.1.1 — Cross-Browser & PWA Hardening

## Purpose

V12.1.1 is a release-acceptance patch on top of V12.1.0. It does not expand product scope or change the V10 project schema. The work is limited to cross-browser capability fallbacks, service-worker lifecycle correctness, PWA update safety, and release evidence.

## Defects fixed

### P1 — “Apply app update” could not activate a waiting service worker

**Root cause:** the V12.1.0 UI sent an `ACTIVATE_UPDATE` message to `registration.waiting`, but `sw.js` did not listen for that message and therefore never called `skipWaiting()`.

**Fix:**

- added an `ACTIVATE_UPDATE` message handler in `sw.js`;
- the waiting worker now calls `self.skipWaiting()` inside the message event lifetime;
- the application now registers its `controllerchange` listener **before** posting the activation message, eliminating a small reload race;
- the update action now reports when no waiting worker is present instead of silently doing nothing.

### P2 — Runtime cache writes were not lifecycle-bound

**Root cause:** same-origin runtime responses started `cache.put()` asynchronously but returned the network response without awaiting the write. A worker termination at the wrong moment could prevent the resource from being committed.

**Fix:** the fetch handler is now an async lifecycle-bound operation. It checks the cache, performs the network request, awaits same-origin cache writes, and only then resolves the response.

### PWA fallback hardening

- offline navigations continue to fall back to cached `index.html`;
- failed non-navigation assets return an error response rather than the application HTML shell;
- obsolete Atelier caches are removed on activation;
- cache identity is now `atelier-space-studio-12.1.1`.

## Cross-browser compatibility work

The release keeps optional/browser-variable APIs behind fallbacks:

- File System Access save/open → JSON download / standard file input fallback;
- `BroadcastChannel` → optional local cross-tab channel;
- `requestIdleCallback` → timer fallbacks;
- WebGL2 → software 3D renderer;
- Ctrl and Meta keyboard paths are both exercised;
- a touch-enabled 390 px browser context is exercised independently of desktop mouse tests.

## Compatibility

- Application: **12.1.1**
- Project schema: **V10**
- Catalog: **1,003 objects**
- Categories: **36**
- Active-floor object ceiling: **5,000**
- Migration from V10/V11/V12.0/V12.1.0: **none**

## Validation summary

### Inherited exact-build regressions

- Professional Studio: **26/26**
- Final-audit regressions: **20/20**
- V12.1 usability: **32/32**
- V11.9 project management: **18/18**
- V11.9 lifecycle/data safety: **7/7**
- V11.8 visual interaction: **19/19**
- forced WebGL2: **7/7**

Inherited subtotal: **129/129**.

### New V12.1.1 checks

- Browser capability/fallback regression: **17/17**
- Service-worker lifecycle contract: **11/11**
- Cross-browser core harness on available Chromium: **10/10**

New executed subtotal: **38/38**.

**Total executed checks: 167/167 passed.**

## Acceptance boundary

This environment could not execute two requested external acceptance surfaces:

1. **Firefox / WebKit:** Playwright browser binaries are absent. An explicit provisioning attempt failed because the runtime cannot resolve the Playwright download hosts (`EAI_AGAIN`). The included `TEST_V12_1_1_CROSS_BROWSER.py` will execute these engines automatically when installed.
2. **Network-origin HTTPS PWA lifecycle:** installed Chromium is enterprise-managed with `URLBlocklist: ["*"]`, causing `ERR_BLOCKED_BY_ADMINISTRATOR` for all HTTP/HTTPS navigation. The exact HTTPS install/update/offline harness is included as `PWA_HTTPS_ACCEPTANCE_12_1_1.py` for execution on a normal browser host or CI runner.

Therefore V12.1.1 is a stronger release candidate and fixes the concrete PWA defect found here, but this package does **not** claim that Firefox, Safari/WebKit, iOS Safari, or real-origin installed-PWA acceptance has been executed in this environment.
