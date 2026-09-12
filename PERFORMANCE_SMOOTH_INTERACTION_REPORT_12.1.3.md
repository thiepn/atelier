# Atelier Space Studio 12.1.3 — Smooth Interaction Report

## Observed failure after V12.1.2

The previous performance hotfix improved a synthetic software-GPU benchmark but failed the real target machine: perceived FPS did not improve and the scene became visibly low-quality while rotating.

That feedback changed the investigation target from fragment-shader cost alone to the complete interaction transition and main-thread input path.

## Root causes corrected

### 1. WebGL backing-store reallocation on every gesture

V12.1.2 changed `canvas.width` / `canvas.height` when entering and leaving interaction. Reallocating a WebGL drawing buffer is expensive, especially on software/slow graphics backends.

Reproduced forced-SwiftShader switch cost:

- V12.1.2: approximately **463.9 ms**
- V12.1.3: approximately **0.1 ms**

V12.1.3 keeps the same backing size for the complete gesture.

### 2. Quality mode activated on pointer-down

A simple click could immediately trigger the degraded interaction appearance. V12.1.3 does not activate motion rendering until pointer movement exceeds the movement threshold.

### 3. Raw pointer frequency exceeded display frequency

High-frequency pointer events were doing camera work even though only one frame could be displayed per refresh interval. V12.1.3 stores the latest camera pointer event and consumes it on requestAnimationFrame.

### 4. Avoidable second RAF

The coalesced event initially called the normal invalidation path, which would add another animation-frame hop. V12.1.3 renders the camera input directly in the same scheduled frame.

### 5. Cutaway updates during orbit

Crossing camera quadrants could trigger wall/cutaway geometry reconstruction during interaction. V12.1.3 records the pending quadrant and applies the rebuild after release.

## Final motion renderer

The final motion path:

- uses the **same native backing resolution** as idle rendering;
- keeps WebGL `antialias:false` for realtime headroom;
- uses direct object colors with simple sun/hemi/contact lighting;
- samples the **last completed shadow map once** per fragment for depth continuity;
- does **not** regenerate the shadow map while moving;
- skips full material patterns, fixture-light loops, fog/tone-map complexity and other presentation work until release;
- immediately returns to the full renderer on release.

## Stress-test measurements

Forced Chromium SwiftShader WebGL2, 1440 × 900 browser viewport, 768 × 631 3D canvas backing store:

- enter interaction: approximately **0.1 ms**
- orbit motion: approximately **27.8 FPS**
- object transform preview: approximately **21.2 FPS**
- gesture backing-store resize: **none**
- runtime JS errors: **none**

The figures are intentionally treated as stress-test evidence rather than promised end-user FPS.

## Safety boundary

No project-schema change was introduced. Geometry, object identity, project save/recovery, professional tools, full idle rendering, and export formats remain on the existing V10-compatible paths.
