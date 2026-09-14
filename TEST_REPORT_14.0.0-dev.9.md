# Atelier 14.0.0-dev.9 Test Report

## Result

**PASS — modular SVG icon renderer migration**

GitHub Actions run: `34815530617`

## New dev.9 gates

- `src/v14/shell/icons.js` syntax: PASS
- Icon service registration on `AtelierV14Shell.icons`: PASS
- Service version `14.0.0-dev.9`: PASS
- Exact SVG serialization for a registered icon: PASS
- Unknown-icon fallback through `cube`: PASS
- Invalid/missing registry fails safely for legacy fallback: PASS
- `atelier:v14:icons-ready` event: PASS
- Exact legacy icon bridge occurrence count: PASS
- Generated artifact contains the icon bridge: PASS

## Integrated browser matrix

The generated dev.9 artifact passed in:

| Project | Result |
| --- | --- |
| Chromium desktop | PASS |
| Chromium mobile/touch 390×844 | PASS |
| Firefox desktop | PASS |
| WebKit desktop | PASS |

Integrated icon assertions:

- all five V14 shell services register: PASS
- command-palette result continues to render one SVG icon: PASS
- direct V14 icon-renderer browser probe: PASS
- icon module version identity: PASS
- zero uncaught page errors: PASS
- zero console errors: PASS

All dev.8 responsive, keyboard, focus-restoration and accessibility assertions remain PASS.

## Controlled offline/PWA development test

Chromium desktop: PASS

- generated artifact warm load: PASS
- inherited Atelier 13.2.0 service worker controls page: PASS
- V14 overlay resources warmed under service-worker control: PASS
- offline reload: PASS
- all five V14 shell services restored: PASS
- icon service version `14.0.0-dev.9` restored offline: PASS
- inherited core cache remains complete: PASS

## Existing regression gates

- Source-tool unit tests: PASS
- Overlay-build / exact-patch tests: PASS
- Notification behavior: PASS
- Dialog behavior: PASS
- Command-palette behavior: PASS
- File-utility behavior: PASS
- Frozen 13.2.0 baseline lock: PASS
- Byte-for-byte source round trip: PASS
- Generated artifact structure validation: PASS
- Artifact upload: PASS

## Certification boundary

This report covers the V14 development artifact only. It does not satisfy any V13.3.1 physical-device production target. Production remains Atelier 13.2.0 on `main`.
