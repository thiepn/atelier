# Atelier V13.3 — Physical Device Acceptance & Final Release Sign-off

## Sign-off state

**FINAL SIGN-OFF: PENDING PHYSICAL DEVICE EVIDENCE**

V13.3 is a certification milestone for the production Atelier **13.2.0 runtime**. Runtime bytes are intentionally frozen during this phase.

### Frozen runtime
- Production URL: `https://thiepn.github.io/atelier/`
- Runtime release: `13.2.0`
- Production release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- Final documentation sign-off commit: `373d7db8221a97c71515341fe63d75bc01c077cd`
- `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`
- PWA cache: `atelier-space-studio-13.2.0`

## Already proven
- GitHub Pages deployment succeeded for the exact production release commit.
- 458 automated checks PASS / 2 environment skips from V13.2.
- Full inherited application matrix: 325/325 PASS.
- Touch target gate: 37/37 visible targets at least 32 px.
- Interrupted service-worker update rollback/roll-forward protocol PASS.
- Presentation-quality WebGL export PASS.

## Required physical evidence before final PASS
- Firefox Desktop
- Safari macOS
- Safari iPhone / Home Screen Web App
- Safari iPad / Home Screen Web App
- Chrome Android Installed PWA

The evidence validator must return:

`SIGNOFF_READY=true`

against all five real-device evidence files. Simulators, emulators, responsive-mode viewports and Chromium device emulation do not count as physical-device acceptance.

## Why sign-off is still pending

No actual Firefox executable, Mac/Safari device, iPhone/iPad, or Android device is exposed to this execution environment. The external E2E connector is present but unauthenticated. V13.3 therefore adds a deterministic physical-acceptance runner and evidence validator instead of fabricating those passes.
