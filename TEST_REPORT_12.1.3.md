# Atelier Space Studio 12.1.3 — Test Report

## Result

**PASS — 175/175 selected executed checks.**

These checks come from overlapping release/regression suites and are not 164 independent product requirements.

## Suites

| Suite | Result |
| --- | ---: |
| Professional Studio | 26/26 |
| Final-audit regression | 20/20 |
| V12.1 workflow/usability | 32/32 |
| Browser capability/fallback | 17/17 |
| V11.9 project management | 18/18 |
| V11.9 lifecycle/data safety | 7/7 |
| V11.8 visual regression | 19/19 |
| Forced WebGL2/GPU | 7/7 |
| V12.1.3 smooth interaction | 18/18 |
| Service-worker lifecycle contract | 11/11 |

## Performance-specific acceptance

The smooth-interaction suite verifies:

- no gesture-time resolution factor;
- no interaction-triggered `resize()`;
- crisp motion shader without the old washed-out gamma path;
- cached-shadow reuse during motion;
- requestAnimationFrame-coalesced pointer input;
- deferred cutaway geometry rebuild;
- MSAA disabled for realtime headroom;
- forced SwiftShader WebGL2 remains active;
- canvas dimensions do not change during interaction;
- interaction-mode switch stays below 30 ms (approximately 0.1 ms in final run);
- mouse-down alone preserves idle rendering;
- actual movement enters the motion path;
- actual movement remains full resolution;
- pointer release restores the full renderer;
- forced SwiftShader full-resolution orbit stays above the 20 FPS acceptance floor (approximately 27.8 FPS final run);
- object transform preview remains interactive (approximately 21.2 FPS final run);
- no captured runtime JavaScript errors.

## Compatibility and data safety

- Application: 12.1.3
- Project schema: V10
- Catalog identity: 1,003/1,003 unique valid objects
- Cross-floor duplicate identifiers rejected
- Relationship cycles rejected
- Healthy architecture retained during salvage recovery
- Browser save, JSON backup, import repair, recovery snapshots and project lifecycle regressions passed
- Mobile horizontal-overflow and primary touch-target regressions passed

## Browser scope

Native Firefox/WebKit binaries are not available in this execution environment. The browser fallback suite verifies feature-detection and graceful behavior for unavailable WebGL2, File System Access, BroadcastChannel, requestIdleCallback and touch/mobile contexts using Chromium-based automation.
