# Atelier 14.0.0-dev.4 — Modular Command Palette

## Scope

Fourth V14 development milestone. The command-palette search/rendering layer moves into an isolated V14 shell module while existing command execution remains unchanged inside the legacy runtime.

## Added

- Modular command-palette service: `src/v14/shell/commands.js`.
- Exact legacy bridge: `src/v14/patches/commands-bridge.json`.
- Dependency-free command-palette behavior test.
- CI validation for both V14 shell bridges and both behavior suites.
- Development artifact advanced to `14.0.0-dev.4`.

## Migrated behavior

The V14 command service now owns:

- opening the command palette;
- rendering command search results;
- catalog-object search;
- the existing 24-object result cap;
- empty-result rendering;
- command-search autofocus.

Existing `data-command` and `data-command-place` attributes are preserved. The established legacy click/action dispatcher therefore continues to execute the actual commands and object-placement actions.

The original `commandsDialog` and `renderCommands` bodies remain present as fail-safe fallback if the V14 module or required adapter is unavailable.

## Validation

GitHub Actions run `34794079679` completed successfully. The workflow verified:

- source and overlay unit tests;
- notification and command module syntax;
- notification behavior;
- command-palette behavior;
- frozen 13.2.0 baseline integrity;
- byte-for-byte source round-trip;
- exact notification and command bridge matches;
- generated dev.4 artifact structure;
- artifact upload.

Generated artifact: `atelier-v14-dev.4`.

## Production impact

None. `main`, production Atelier 13.2.0, and V13.3.1 physical acceptance are unchanged.
