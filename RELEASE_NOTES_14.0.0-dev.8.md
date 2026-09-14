# Atelier 14.0.0-dev.8 — Cross-Browser, Responsive & Offline Integration Gate

## Scope

Eighth V14 development milestone. This milestone adds no new product subsystem. It hardens the generated V14 development artifact across browser engines, responsive/touch conditions, keyboard/focus behavior, accessibility semantics, and service-worker offline recovery before further legacy extraction.

## Added

- Manifest version advanced to `14.0.0-dev.8`.
- Shared Playwright configuration: `tools/v14-playwright.config.js`.
- Integrated browser matrix:
  - Chromium desktop — 1280×800;
  - Chromium mobile/touch — 390×844;
  - Firefox desktop — 1280×800;
  - WebKit desktop — 1280×800.
- Responsive horizontal-overflow gate.
- Integrated development-diagnostics accessibility checks.
- Keyboard open/close checks for the development diagnostics panel.
- Native Escape/cancel verification for the command dialog.
- Focus restoration verification from the modular dialog shell back to the invoking control.
- Command-search accessible-name and preserved action-contract checks.
- Generated-artifact offline/PWA smoke test in controlled Chromium.
- Service-worker status verification before and after offline reload.
- Verification that V14 overlay assets survive a warmed controlled offline reload.

## Browser integration contract

The generated artifact must now satisfy the same migrated-shell integration path in Chromium, Firefox and WebKit. The mobile Chromium project additionally runs with touch enabled at a 390×844 viewport and must remain free of meaningful horizontal page overflow.

The shell test verifies that:

1. all four V14 shell services register;
2. the development-only diagnostics surface is present and correctly labelled;
3. diagnostics can be opened by keyboard and closed with Escape;
4. focus remains deterministic through diagnostics and dialog interactions;
5. `Ctrl+K` reaches the existing legacy keyboard handler and modular command/dialog bridges;
6. the command search receives focus and exposes its accessible name;
7. native dialog Escape closes through the existing cancel path and restores invoking focus;
8. `Export deliverables` retains the legacy `data-command="export"` contract;
9. notifications and filename normalization still work in the integrated runtime;
10. uncaught page and console errors remain zero.

## Offline development-artifact gate

The Chromium offline test performs a real service-worker-controlled sequence:

1. load the generated V14 artifact online;
2. wait for the inherited Atelier 13.2.0 service worker to become active and controlling;
3. verify `GET_STATUS` reports the complete 13.2.0 core cache;
4. confirm V14 overlay assets were fetched under service-worker control;
5. place the browser context offline;
6. reload the application from cache;
7. verify the Atelier application shell and all V14 shell services return;
8. verify diagnostics report `offline`, `controlled`, and baseline `Atelier 13.2.0`;
9. re-query service-worker status and require the core cache to remain complete.

This is automated development-artifact validation only. It is not a substitute for V13.3.1 physical-device production acceptance.

## Validation

GitHub Actions run `34815078492` passed:

- source-tool unit tests;
- overlay-build and exact-patch tests;
- JavaScript syntax gates;
- all four isolated shell-module behavior suites;
- frozen 13.2.0 baseline verification;
- byte-for-byte source round trip;
- V14 development artifact build and structure validation;
- Playwright installation for Chromium, Firefox and WebKit;
- generated-artifact shell integration matrix;
- generated-artifact controlled offline/PWA smoke.

## Production impact

None. `main` remains Atelier 13.2.0. V14 remains an uncertified development line, and V13.3.1 physical-device sign-off remains a separate unresolved production gate.
