# Atelier Space Studio 12.1.3

Atelier is a local-first browser space-planning studio with a **1,003-object procedural library**, architecture tools, parametric objects, materials, room intelligence, hierarchical layers, reusable room kits, project templates, and realtime 3D.

V12.1.3 is a **smooth-interaction corrective release**. It replaces the V12.1.2 gesture-time dynamic-resolution strategy after real-device feedback showed that the resolution drop made motion visibly worse without solving the lag on the affected machine.

## What changed in 12.1.3

- **No gesture-time canvas resize.** Orbiting and dragging keep the same WebGL backing resolution from pointer-down through pointer-up.
- **No quality change on click.** The lightweight motion path activates only after actual pointer movement.
- **No half-second backing-store reallocation stall.** The reproduced SwiftShader mode-switch cost fell from roughly **464 ms** in V12.1.2 to roughly **0.1 ms** in V12.1.3.
- **Animation-frame input coalescing.** Camera pointer events are consumed once per display frame instead of performing redundant camera work at raw mouse-polling frequency.
- **Same-frame camera rendering.** Camera input no longer creates an avoidable second requestAnimationFrame hop.
- **Deferred cutaway rebuilds.** Expensive wall-quadrant geometry updates wait until the gesture ends.
- **Crisp full-resolution motion shader.** Motion keeps native backing resolution and reuses the last valid shadow map with one cheap sample for spatial depth.
- **No shadow-map regeneration while moving.** The cached map is reused during the gesture; full material/shadow/presentation rendering resumes immediately on release.
- **MSAA disabled for the realtime WebGL canvas** to recover rendering headroom without lowering backing resolution.

Saved project geometry, V10 serialization, professional tools, normal idle rendering, and exports are unchanged by the motion optimization.

## Performance validation

On an intentionally hostile Chromium + SwiftShader WebGL2 path:

- interaction mode switch: **~464 ms → ~0.1 ms**
- orbit: **~27.8 FPS** at full 768 × 631 backing resolution in the final run
- object transform preview: **~21.2 FPS** at full backing resolution in the final run
- canvas backing size during gesture: **unchanged**

These numbers are environment-specific stress-test measurements, not a guaranteed device-independent FPS claim. The purpose is to verify that the V12.1.2 resize stall is gone and that the full-resolution motion path remains usable even on a software-rendered WebGL backend.

## Workflow retained from V12.1

The primary mode bar remains **Studio / Advanced / Arrange**. Studio is grouped into Build & coordinate, Design & present, Review & deliver, and Advanced & setup. Start here remains available for the shortest room → furnish → save/export workflow.

Save / Backup / Export remain distinct:

- `Ctrl/Cmd + S` — save to browser storage
- `Ctrl/Cmd + Shift + S` — download editable JSON backup
- `Ctrl/Cmd + E` — export deliverables

## Compatibility

- Application: **12.1.3**
- Project schema: **V10**
- Catalog: **1,003 objects**
- Categories: **36**
- Active-floor object ceiling: **5,000**
- Project migration required: **No**

## Validation

Executed against the exact V12.1.3 source:

- Professional Studio: **26/26**
- final-audit regressions: **20/20**
- V12.1 workflow/usability: **32/32**
- browser capability/fallback: **17/17**
- V11.9 project management: **18/18**
- V11.9 lifecycle/data safety: **7/7**
- V11.8 visual regression: **19/19**
- forced WebGL2/GPU: **7/7**
- V12.1.3 smooth-interaction suite: **18/18**
- service-worker lifecycle contract: **11/11**

**175/175 selected checks passed.** These suites overlap and should not be interpreted as 164 unique product requirements.

See `RELEASE_NOTES_12.1.3.md`, `PERFORMANCE_SMOOTH_INTERACTION_REPORT_12.1.3.md`, and `TEST_REPORT_12.1.3.md`.
