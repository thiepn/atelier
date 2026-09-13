# Atelier Space Studio 13.2.0 — Remaining External Device Acceptance

Production deployment verification is automated against the GitHub Pages HTTPS origin. Physical-device engine certification still requires the actual target devices.

## Pending physical targets
- Safari macOS
- Safari iPhone / iPad
- Chrome Android installed PWA

## Required physical-device pass
1. Open `https://thiepn.github.io/atelier/` and confirm 13.2.0 in Release certification.
2. Open an existing V10 project and confirm no migration or data loss.
3. Build a room, place/move/replace an object, orbit 3D, undo/redo, save, backup JSON, and re-import.
4. Verify Library search, previews, collections, imported assets, and replacement.
5. Verify keyboard-only workflow on desktop targets and touch editing on mobile targets.
6. Install the PWA where supported; close all windows, go offline, cold-start, and confirm the local project/editor loads.
7. Restore network, apply a waiting update, and confirm project data survives the controller transition.
8. Export the Release certification JSON and record browser/OS/device.

A physical target remains pending until those checks are executed on that actual browser/device.
