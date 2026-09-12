# V12.1.1 Cross-Browser / PWA Acceptance Report

## Verdict

**CONDITIONAL PASS — concrete PWA defect fixed; external engine/origin acceptance still required.**

The V12.1.1 patch fixes a reproducible service-worker update defect and hardens cache lifecycle behavior. All executable regression, fallback, touch, software-renderer and service-worker contract checks passed.

The environment cannot honestly certify Firefox, WebKit/iOS Safari, or network-origin installed-PWA behavior because those engines/origins are blocked or unavailable here.

## Fixed during this iteration

1. Waiting PWA updates now respond to `ACTIVATE_UPDATE` and call `skipWaiting()`.
2. `controllerchange` is armed before the activation message is sent.
3. Update requests with no waiting worker now surface an explicit message.
4. Same-origin runtime caching is awaited inside the fetch lifecycle.
5. Offline navigation and missing-asset behavior remain separated.
6. Version and cache identity are aligned at 12.1.1.

## Cross-browser posture

- Chromium: executed core, fallback, touch and forced WebGL2/software paths — PASS.
- Firefox: not executed; browser binary unavailable.
- WebKit/Safari: not executed; browser binary unavailable.
- Firefox/WebKit provisioning: attempted, blocked by DNS/network restrictions.

The source package includes a cross-engine Playwright harness so the exact build can be tested without writing new test logic once those browsers are available.

## PWA posture

- service-worker install/activate/message/fetch contract: PASS;
- update UI/source wiring: PASS;
- exact local HTTPS lifecycle harness: provided;
- execution of that harness here: blocked by managed Chromium URL policy;
- trusted HTTPS install/standalone UI: not executed;
- real offline relaunch on a registered network origin: not executed here.

## Release recommendation

Use V12.1.1 instead of V12.1.0 because it contains a real PWA update fix. Keep the label **cross-browser/PWA acceptance RC** until the included harnesses are run on Firefox, WebKit/Safari, and an unrestricted HTTPS browser host. If those runs are clean, no additional feature work is needed before release.
