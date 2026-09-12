# Atelier Space Studio 12.1.4 — Release Notes

## Release type

Adaptive performance diagnostics and software-WebGL interaction optimization. No project-schema migration and no feature expansion outside performance/support tooling.

## Why this release exists

V12.1.3 removed the visible resolution degradation and interaction-start allocation hitch from V12.1.2. The remaining problem was that a machine could still feel slow without Atelier exposing whether the bottleneck came from input work, scene rebuilds, CPU submission, the graphics backend, or a software WebGL rasterizer.

V12.1.4 makes those costs measurable in the running app and adds a conservative optimization only for known software-WebGL backends.

## Added

### Live device profiler

The Performance panel now reports:

- recent interaction FPS;
- average/p50/p95 frame interval;
- render submission timing;
- pointer processing and input latency;
- pick timing;
- incremental object-patch timing;
- scene rebuild timing;
- selection-buffer timing;
- estimated dropped frames;
- draw calls and triangle count;
- WebGL backing-buffer size;
- browser-exposed graphics vendor/renderer;
- current renderer preference and selected backend.

The same snapshot is exposed through `window.Atelier.getPerformanceTelemetry()` and included in diagnostics export.

### Graphics backend inspection

Atelier probes a separate WebGL2 context for vendor/renderer metadata without altering the main scene canvas. Known software rasterizers are flagged, including SwiftShader, llvmpipe, softpipe and lavapipe families when exposed by the browser.

### Software-WebGL interaction optimization

When a known software rasterizer is detected, Atelier keeps the same full-resolution WebGL scene and:

- enables backface culling only during motion;
- skips the cached shadow texture lookup during motion;
- restores the normal renderer immediately on release.

This avoids the V12.1.2 strategy of lowering canvas resolution.

### Renderer troubleshooting override

- `?renderer=webgl` forces WebGL when available.
- `?renderer=software` forces the CPU compatibility renderer.
- default `auto` keeps WebGL when available and only applies backend-specific interaction optimizations.

## Performance validation

On forced SwiftShader WebGL2 at a 768 × 631 backing buffer, final runs measured approximately:

- orbit: **35 FPS** in the dedicated smooth-interaction benchmark;
- real pointer gesture: **~39 FPS** in the live-profiler test;
- object transform preview: **~28 FPS**;
- interaction mode switch: **~0.2 ms**;
- no backing-buffer resize during the gesture.

A separate 3D PNG capture test produced a valid approximately 3.9M-character PNG data URL with no runtime faults.

## Compatibility

- Application: **12.1.4**
- Project schema: **V10**, unchanged
- Existing V10 projects: no migration required
- PWA cache identity: `atelier-space-studio-12.1.4`

## Validation summary

**193/193 selected checks passed.** Native Firefox/WebKit engine execution remains outside this environment; Chromium automation still verifies capability fallbacks and mobile/touch behavior.
