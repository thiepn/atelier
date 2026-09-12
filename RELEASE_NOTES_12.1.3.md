# Atelier Space Studio 12.1.3 — Release Notes

## Release type

Corrective 3D interaction/performance release. No project-schema migration and no feature expansion.

## Why this release exists

V12.1.2 attempted to improve slow 3D interaction by reducing the render resolution while the pointer was down and using a cheaper motion shader. Real-device feedback showed two unacceptable results on the affected machine:

1. rotation still felt roughly as slow as before;
2. the scene became visibly degraded as soon as interaction began.

V12.1.3 removes that strategy rather than tuning it further.

## Fixed

### Gesture-start allocation hitch

V12.1.2 resized the WebGL backing canvas when entering and leaving interaction. On a forced SwiftShader path, entering interaction reproduced a roughly **464 ms** stall. V12.1.3 never changes the backing size for orbit/drag. The same mode switch measures roughly **0.1 ms** in the final stress test.

### Gesture-time visual degradation

The canvas now remains at full backing resolution while moving. Merely clicking does not switch render paths; the motion path begins only after real pointer movement.

### Raw-pointer overwork

Camera movement is coalesced to one update per animation frame. This prevents high-polling-rate mice from triggering redundant camera/render work that the display cannot show.

### Double-frame scheduling

The camera path now renders inside the coalesced input frame rather than scheduling another render one frame later.

### Cutaway geometry churn

Camera quadrant changes no longer rebuild cutaway geometry repeatedly during the gesture. The pending quadrant is applied once the gesture ends.

### Motion shading

The motion shader remains intentionally cheaper than the full idle renderer, but it is full-resolution and reuses the last valid shadow map with one sample. Shadow-map regeneration, material-detail effects, fixtures, and filmic presentation work remain deferred until pointer release.

### WebGL overhead

Realtime MSAA remains disabled and the context still prefers the high-performance adapter. `preserveDrawingBuffer` remains disabled; export paths were previously validated without it.

## Compatibility

- Application version: **12.1.3**
- Project schema: **V10**, unchanged
- Existing V10 projects: compatible without migration
- PWA cache identity: `atelier-space-studio-12.1.3`

## Validation summary

Selected regression checks: **175/175 passed**.

The forced SwiftShader interaction run used the same full 768 × 631 backing resolution before, during, and after the gesture and produced approximately **27.8 FPS orbit** and **21.2 FPS object preview** in the final run.

Firefox/WebKit native-engine acceptance is still outside this environment's executable browser set; browser capability/fallback coverage remains automated in Chromium.
