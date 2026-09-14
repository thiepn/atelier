# Atelier 14.0.0-dev.8 Test Report

## Result

**PASS — cross-browser, responsive and controlled-offline integration gate**

GitHub Actions run: `34815078492`

## Deterministic baseline/build gates

- Source-tool unit tests: PASS
- V14 overlay-build / exact-patch tests: PASS
- V14 module and browser-test JavaScript syntax: PASS
- Notification module behavior: PASS
- Dialog module behavior: PASS
- Command-palette module behavior: PASS
- File-utility module behavior: PASS
- Frozen Atelier 13.2.0 baseline lock: PASS
- Byte-for-byte source extraction/rebuild round trip: PASS
- V14 development artifact build: PASS
- Overlay artifact structure and bridge validation: PASS

## Integrated browser matrix

The generated V14 development artifact passed the shell integration test in:

| Project | Viewport / mode | Result |
| --- | --- | --- |
| Chromium desktop | 1280×800 | PASS |
| Chromium mobile | 390×844, touch + mobile context | PASS |
| Firefox desktop | 1280×800 | PASS |
| WebKit desktop | 1280×800 | PASS |

Integrated assertions include:

- V14 shell-service registration;
- development diagnostics availability and labelling;
- <= 1 px horizontal document overflow;
- mobile touch capability under the mobile project;
- diagnostics keyboard activation and Escape close;
- `aria-expanded` / `aria-controls` / `aria-labelledby` relationships;
- legacy `Ctrl+K` shortcut through the V14 command/dialog bridges;
- dialog `aria-modal` state;
- command-search accessible name and autofocus;
- native Escape dialog cancellation;
- invoking-focus restoration;
- preserved `data-command="export"` action contract;
- notification rendering;
- safe filename normalization;
- zero uncaught page errors;
- zero console errors.

## Controlled offline/PWA development test

Chromium desktop: PASS

Validated sequence:

- online warm load: PASS
- service worker ready and controlling: PASS
- service-worker release identity `13.2.0`: PASS
- core cache `atelier-space-studio-13.2.0`: PASS
- core cache complete before offline transition: PASS
- V14 overlay assets observed during controlled online load: PASS
- browser context offline transition: PASS
- cached navigation reload: PASS
- V14 shell services restored offline: PASS
- application shell visible offline: PASS
- diagnostics network state `offline`: PASS
- diagnostics service-worker state `controlled`: PASS
- diagnostics baseline `Atelier 13.2.0`: PASS
- core cache complete after offline reload: PASS

## Certification boundary

These results are automated V14 development validation. They do not satisfy or replace any V13.3.1 physical-device production evidence target. Production remains Atelier 13.2.0 on `main`.
