# Atelier Space Studio 12.1.4 — Test Report

## Result

**PASS — 193/193 selected executed checks.**

The suites overlap and are regression surfaces, not 193 independent product requirements.

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
| V12.1.4 smooth interaction | 18/18 |
| Service-worker lifecycle contract | 11/11 |
| V12.1.4 live profiler | 18/18 |

## New V12.1.4 acceptance

The live-profiler suite verifies:

- graphics backend probe exists;
- renderer preference override is bounded to Auto/WebGL/Software;
- telemetry API is exposed read-only;
- pointer processing and input latency are measured;
- render, pick, patch, selection and scene-update paths are timed;
- SwiftShader is detected as software WebGL;
- Auto mode retains WebGL;
- backend identity is exposed;
- real orbit populates pointer and frame telemetry;
- last-gesture FPS is recorded;
- full backing resolution is retained;
- forced SwiftShader remains above the 20 FPS stress-test floor;
- forced compatibility renderer still works;
- no captured runtime JavaScript errors.

## Export acceptance

A separate full-quality 3D PNG capture check returned a valid `data:image/png;base64,...` result of approximately 3.9 million characters with no runtime faults.

## Data / compatibility safety

- Application version: 12.1.4
- Project schema: V10
- Catalog identity: 1,003/1,003 valid unique objects
- Cross-floor duplicate IDs rejected
- Relationship cycles rejected
- Healthy architecture preserved during salvage recovery
- Browser save, JSON backup, repair import, recovery snapshots and project lifecycle regressions passed
- Mobile horizontal-overflow and primary touch-target regressions passed
- Service-worker install/activate/update/offline/runtime-cache paths passed
