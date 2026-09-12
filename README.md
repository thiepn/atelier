# Atelier Space Studio 12.1.4

Atelier is a local-first browser space-planning studio with a **1,003-object procedural library**, architecture tools, parametric objects, materials, room intelligence, hierarchical layers, reusable room kits, project templates, and realtime 3D.

V12.1.4 is an **adaptive performance + live-profiler release**. It keeps the V12.1.3 full-resolution interaction path and adds measured, device-specific telemetry so slow machines can be diagnosed from actual frame/input/render timings instead of guessed at from project size.

## What changed in 12.1.4

- **Live interaction profiler** for recent FPS, average/p95 frame timing, render submission time, pointer processing, input latency, picking, object patching, scene rebuilds, selection uploads, dropped-frame estimates, draw calls, triangles and backing-buffer size.
- **Graphics backend detection** reports the WebGL vendor/renderer string when the browser exposes it, including known software rasterizers such as SwiftShader/llvmpipe.
- **Adaptive software-WebGL interaction path.** When a known software rasterizer is detected, Atelier keeps full-resolution WebGL but enables interaction-only backface culling and skips the cached shadow texture lookup while moving. Idle rendering and exported output remain unchanged.
- **No gesture-time canvas resize.** Rotation/dragging keeps the same backing resolution.
- **No quality change on click.** The motion path still begins only after actual movement.
- **Animation-frame input coalescing** remains in place so raw high-polling mouse events cannot trigger redundant camera work.
- **Deferred cutaway rebuilds** remain in place until the gesture ends.
- **Compatibility renderer override** is available for troubleshooting with `?renderer=software`; `?renderer=webgl` forces WebGL.
- Diagnostics JSON now includes the live performance snapshot.

## Stress-test result

On intentionally hostile Chromium + SwiftShader WebGL2:

- full-resolution interaction: roughly **35–40 FPS** in the final adaptive test runs;
- object transform preview: roughly **28 FPS** in the smooth-interaction suite;
- backing buffer during gesture: **768 × 631, unchanged**;
- interaction-mode switch: roughly **0.2 ms** in the final run;
- no runtime JavaScript errors.

These measurements are environment-specific stress-test results, not a guaranteed FPS for every device.

## Using the profiler

Open **Advanced → Platform & performance → Performance**. Rotate or drag for a few seconds, then reopen the panel. It reports the actual device/browser timings and graphics backend used for that session.

The same snapshot is available to diagnostics through `window.Atelier.getPerformanceTelemetry()` and is included in exported diagnostics JSON.

## Compatibility

- Application: **12.1.4**
- Project schema: **V10**, unchanged
- Catalog: **1,003 objects**
- Categories: **36**
- Project migration required: **No**

## Validation

Executed against the exact V12.1.4 source:

- Professional Studio: **26/26**
- final-audit regressions: **20/20**
- V12.1 workflow/usability: **32/32**
- browser capability/fallback: **17/17**
- V11.9 project management: **18/18**
- V11.9 lifecycle/data safety: **7/7**
- V11.8 visual regression: **19/19**
- forced WebGL2/GPU: **7/7**
- V12.1.4 smooth interaction: **18/18**
- service-worker lifecycle contract: **11/11**
- V12.1.4 live profiler: **18/18**

**193/193 selected checks passed.** The suites overlap and should not be interpreted as 193 independent product requirements.

See `RELEASE_NOTES_12.1.4.md`, `PERFORMANCE_ADAPTIVE_PROFILER_REPORT_12.1.4.md`, and `TEST_REPORT_12.1.4.md`.
