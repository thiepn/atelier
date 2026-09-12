# Atelier Space Studio 12.1.2 — Performance Hotfix

V12.1.2 is a focused interaction-performance release. It preserves the V10 project schema and the V12.1.1 feature set while removing expensive work from orbiting, dragging, rotating, panning, and other live 3D manipulation paths.

## Main fixes

- requests a **high-performance WebGL adapter** instead of explicitly preferring the low-power adapter;
- disables continuous `preserveDrawingBuffer`, while preserving synchronous 3D PNG/panorama capture;
- fixes interactive dynamic resolution so it actually reduces render pixels on ordinary 1× DPR desktop displays;
- adds a dedicated lightweight **interaction shader** used only while manipulating the scene;
- skips shadow sampling, detailed material shading, and fixture-light loops while interaction is active;
- restores the full material/shadow/presentation renderer immediately after interaction ends;
- caches all WebGL uniform locations instead of querying the graphics driver on every frame;
- removes the artificial ~42 FPS cap on active GPU object transforms; requestAnimationFrame is now the primary frame cap;
- throttles expensive smart-placement snapping calculations to ~30 Hz while object position rendering can continue every animation frame;
- avoids repeated DOM writes for an unchanged zoom readout;
- reduces split-view background 3D refresh pressure while retaining responsive editing.

## Interaction quality strategy

The lower interaction resolution is temporary. On pointer-down the renderer prioritizes latency and frame rate. After pointer-up, full-quality pixel density, shadows, material detail, point lights, and presentation shading return automatically.

No project geometry, object fidelity, export resolution, or saved project data is downgraded.

## Compatibility

- Application version: **12.1.2**
- Project schema: **V10**
- Existing V10 / V11 / V12 projects: compatible
- Catalog: unchanged
- Project data migration: none

## Performance benchmark

Deliberately slow Chromium + SwiftShader regression environment, same scene and viewport:

| Interaction | V12.1.1 | V12.1.2 | Improvement |
|---|---:|---:|---:|
| Continuous orbit | ~2.7 FPS | ~29.5 FPS | ~10.7× |
| Continuous object transform | ~3.3 FPS | ~26.2 FPS | ~8.0× |

These numbers are environment-specific and are not universal FPS guarantees. The benchmark intentionally uses a software GPU to make interaction-path regressions visible.

## Export safety

The 3D capture path was explicitly tested after disabling `preserveDrawingBuffer`. It still returns a valid PNG data URL with a multi-megabyte image payload and no captured runtime error.
