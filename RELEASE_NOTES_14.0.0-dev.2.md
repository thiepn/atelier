# Atelier 14.0.0-dev.2 — Deterministic Module Overlay

## Scope

Second V14 development milestone. This is an uncertified development artifact, not a production release and not a substitute for V13.3.1 physical-device sign-off.

## Added

- Deterministic V14 overlay builder: `tools/v14_build.py`.
- Ordered module manifest: `src/v14/manifest.json`.
- Path validation and traversal rejection for V14 assets.
- Duplicate-injection marker rejection.
- Separate hashed `v14-build-manifest.json` for generated artifacts.
- Passthrough copying for runtime/PWA assets without mutating their source files.
- Five overlay-build regression tests.
- First isolated module: `src/v14/dev-status/`.
- CI build of the real Atelier baseline plus V14 overlay.
- CI upload of the generated `atelier-v14-dev.2` artifact.

## Development diagnostics

The dev-status module provides an isolated shell-level diagnostic surface for:

- online/offline state;
- browser vs standalone display mode;
- service-worker controller state;
- touch-point count;
- viewport and pixel ratio;
- locked Atelier 13.2.0 baseline identity.

It can be opened from the `V14 DEV` control or with `Ctrl/Cmd+Shift+D` and closed with Escape.

## Runtime impact

- Production `main`: unchanged.
- Production Atelier 13.2.0: unchanged.
- Root `index.html` on `v14-development`: remains the locked 13.2.0 baseline.
- V14 code exists only in the separately generated development artifact.
