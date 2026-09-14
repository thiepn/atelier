# Atelier 14.0.0-dev.10 Test Report

## Result

**PASS — modular text escaping migration**

GitHub Actions run: `34816085941`

## New dev.10 gates

- `src/v14/shell/text.js` syntax: PASS
- Text service registration on `AtelierV14Shell.text`: PASS
- Service version `14.0.0-dev.10`: PASS
- Null/undefined conversion behavior: PASS
- Numeric/string conversion behavior: PASS
- HTML entity escaping: PASS
- Legacy apostrophe encoding `&#39;`: PASS
- XML apostrophe encoding `&apos;`: PASS
- Legacy single-pass/double-escape behavior: PASS
- `atelier:v14:text-ready` event: PASS
- Four exact legacy text bridges: PASS
- Generated artifact contains text-service bridge references: PASS

## Integrated browser matrix

The generated dev.10 artifact passed in:

| Project | Result |
| --- | --- |
| Chromium desktop | PASS |
| Chromium mobile/touch 390×844 | PASS |
| Firefox desktop | PASS |
| WebKit desktop | PASS |

Integrated dev.10 assertions:

- all six V14 shell services register: PASS
- direct HTML escaping probe: PASS
- direct XML escaping probe: PASS
- text service version identity: PASS
- zero uncaught page errors: PASS
- zero console errors: PASS

All earlier responsive, keyboard, modal focus/Escape, command, notification, file and icon assertions remain PASS.

## Controlled offline/PWA development test

Chromium desktop: PASS

- generated artifact warm load: PASS
- inherited Atelier 13.2.0 service worker controls page: PASS
- V14 overlay assets warmed under service-worker control: PASS
- offline reload: PASS
- all six V14 shell services restored: PASS
- icon service dev.9 restored offline: PASS
- text service dev.10 restored offline: PASS
- inherited core cache remains complete: PASS

## Existing regression gates

- Source-tool unit tests: PASS
- Overlay-build / exact-patch tests: PASS
- Notification behavior: PASS
- Dialog behavior: PASS
- Command-palette behavior: PASS
- File-utility behavior: PASS
- Icon-renderer behavior: PASS
- Frozen 13.2.0 baseline lock: PASS
- Byte-for-byte source round trip: PASS
- Generated artifact structure validation: PASS
- Artifact upload: PASS

## Certification boundary

This report covers the V14 development artifact only. It does not satisfy any V13.3.1 physical-device production target. Production remains Atelier 13.2.0 on `main`.
