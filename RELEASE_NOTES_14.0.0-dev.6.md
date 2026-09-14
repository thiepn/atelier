# Atelier 14.0.0-dev.6 — Modular Dialog Shell

## Scope

Sixth V14 development milestone. Core modal opening, closing and confirmation-dialog composition move into an isolated V14 shell service while IIFE-owned application state remains private behind explicit adapters.

## Added

- Modular dialog service: `src/v14/shell/dialogs.js`.
- Exact legacy bridge: `src/v14/patches/dialogs-bridge.json`.
- Dependency-free dialog behavior test.
- CI coverage for four modular shell services and four exact bridge groups.

## Migrated behavior

The V14 dialog service now owns post-bootstrap:

- modal title, kicker and content rendering;
- wide-dialog class state;
- `aria-modal` state;
- `showModal()` invocation;
- preferred initial focus;
- modal closing;
- restoration of pre-modal focus;
- confirmation-dialog markup composition.

The legacy IIFE continues to own `exportBusy`, `modalReturn` and `confirmCallback`. The bridge exposes only narrow getter/setter callbacks required by the service; these variables are not made global.

The original `openDialog`, `closeDialog` and `confirmAction` bodies remain as fallback if the module or required adapters are unavailable.

## Validation

GitHub Actions run `34794378836` completed successfully, including dialog behavior testing, all previous shell-service suites, frozen-baseline verification, all four exact bridge groups, real dev.6 artifact generation, structure validation and artifact upload.

Generated artifact: `atelier-v14-dev.6`.

## Production impact

None. `main`, production Atelier 13.2.0 and V13.3.1 physical acceptance remain unchanged.
