# Atelier Space Studio 12.1.2 — Interaction Performance Report

## Problem reproduced

The V12.1.1 interaction path could become severely frame-limited during camera orbit and object transforms. A deliberately slow WebGL2/SwiftShader benchmark reproduced roughly 2.7 FPS orbit and 3.3 FPS transform performance.

## Root causes

### 1. Wrong GPU preference

The WebGL2 context explicitly requested `powerPreference: 'low-power'`. On systems with multiple adapters this can select the slower GPU for the most graphics-intensive part of Atelier.

### 2. Interactive resolution scaling was ineffective at DPR 1

The previous formula applied its interaction factor before `min(devicePixelRatio, ...)`. On a normal 1× DPR monitor the result was clamped back to 1.0, so the intended dynamic-resolution optimization did nothing.

### 3. Full fragment shader remained active during interaction

Even though shadow-map regeneration was deferred, each interactive fragment still executed the full material/tone-map/shadow-capable shader path. That included branches and calculations not required while the scene is in motion.

### 4. Graphics-driver uniform lookups occurred every frame

`gl.getUniformLocation()` was called repeatedly for the same program uniforms on every rendered frame, including all point-light arrays.

### 5. Object transform preview had an extra FPS throttle

The GPU path imposed an additional 24 ms preview interval (~42 FPS maximum) on top of `requestAnimationFrame`.

### 6. Smart snapping ran on every pointer event

Continuous object movement recalculated several placement-assistance systems at pointer-event frequency, even though screen rendering was already animation-frame coalesced.

## Fix architecture

V12.1.2 adds a dedicated interaction path rather than permanently reducing quality:

- high-performance WebGL adapter preference;
- no preserved back buffer during normal rendering;
- correctly applied temporary dynamic-resolution scale;
- lightweight interaction-only fragment shader;
- no shadow sampling/material patterns/fixture-light loops while moving;
- cached uniform locations;
- requestAnimationFrame-driven GPU transform preview;
- ~30 Hz smart-snap calculation throttle;
- automatic full-quality restoration after interaction.

## Benchmark results

SwiftShader software-GPU benchmark:

- V12.1.1 orbit: **~2.74 FPS**
- V12.1.2 orbit: **~29.5 FPS**
- V12.1.1 object transform: **~3.28 FPS**
- V12.1.2 object transform: **~26.2 FPS**

The hotfix therefore improves the reproduced worst-case path by approximately 8–11×.

## Quality boundary

The reduced-resolution/simple-shader path exists only while interaction is active. The idle/final frame remains the existing high-quality renderer. PNG export and panorama capture remain full-quality synchronous renders.
