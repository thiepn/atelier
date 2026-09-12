# Atelier Space Studio 12.1.4 — Adaptive Performance & Profiler Report

## Goal

Measure the actual interaction bottleneck on the running device without reintroducing gesture-time resolution reduction or broad visual degradation.

## Runtime telemetry

`Scene3D.performanceTelemetry()` keeps bounded rolling samples for:

- render duration;
- interaction frame interval;
- pointer processing duration;
- input-to-RAF latency;
- object picking;
- incremental object patching;
- selection-buffer updates;
- full scene updates;
- dropped-frame estimate;
- last completed gesture FPS and duration.

The profiler is read-only: it does not mutate project data or change renderer settings.

## Backend detection

A small probe context reads WebGL vendor/renderer metadata when available. It flags common software paths such as SwiftShader and llvmpipe.

The primary scene still prefers WebGL in Auto mode. Known software-WebGL paths receive only interaction-specific optimizations; Atelier does not automatically replace WebGL with the CPU renderer because full-quality CPU rendering was measured slower for the default 37-object scene in this environment.

## Adaptive interaction changes

For a detected software-WebGL backend while the camera/object is moving:

1. backface culling is enabled;
2. the fast full-resolution shader skips shadow-map sampling;
3. no shadow map is regenerated;
4. the canvas backing size remains unchanged;
5. the normal full renderer returns at pointer release.

The interaction shader still uses full-resolution geometry and direct object colors rather than the V12.1.2 low-resolution path.

## Stress-test observations

Forced Chromium SwiftShader, default Sienna café scene:

- detected backend: `ANGLE ... SwiftShader ...`;
- scene triangles: approximately 15.3k;
- backing buffer: 768 × 631;
- V12.1.4 orbit: approximately 35 FPS in the dedicated benchmark;
- real pointer gesture: approximately 39 FPS in the profiler acceptance run;
- object transform preview: approximately 28 FPS;
- interaction switch: approximately 0.2 ms;
- runtime errors: none.

These values vary between runs and machines. The important acceptance criteria are full-resolution interaction, bounded input work, correct backend reporting, no runtime faults, and measurable device-specific telemetry.

## Support workflow

If a real device still performs poorly:

1. rotate/drag for several seconds;
2. open Performance profiler;
3. inspect backend, FPS, frame p95, render p95, input p95, scene-update p95 and triangle count;
4. export diagnostics JSON if needed.

This separates CPU/input/scene-rebuild bottlenecks from GPU/backend bottlenecks before another optimization is attempted.
