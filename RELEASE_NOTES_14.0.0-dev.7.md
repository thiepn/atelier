# Atelier 14.0.0-dev.7 — Browser Shell Integration Gate

## Scope

Seventh V14 development milestone. No new production feature is promoted in this milestone. Instead, the generated V14 development artifact is now exercised in a real Chromium browser so the legacy runtime, exact bridges, V14 shell modules, and application DOM are validated together.

## Added

- Playwright integration smoke test: `tools/v14-shell-smoke.spec.js`.
- Real Chromium execution against the generated `v14-dist` artifact.
- Runtime page-error and console-error capture.
- Manifest-driven CI validation and artifact naming.
- CI concurrency cancellation for superseded V14 runs.
- Documentation-only commits excluded from the expensive browser workflow.

## Browser integration path

The smoke test exercises the actual application path rather than calling only isolated module functions:

1. Load the generated V14 artifact in Chromium.
2. Wait for all four V14 shell services to register.
3. Normalize any first-run modal state.
4. Press `Ctrl+K` through Atelier's existing keyboard handler.
5. Verify the legacy `commandsDialog` bridge opens the modular dialog shell.
6. Verify the command-search input receives focus.
7. Search for `Export deliverables` and confirm the existing `data-command="export"` contract.
8. Close the modal through Atelier's existing dialog action path.
9. Exercise V14 notification rendering.
10. Exercise V14 safe filename normalization.
11. Assert no uncaught page errors or console errors occurred.

## CI hardening

The workflow now derives the development version, ordered modules, styles, patch sources, and artifact name from `src/v14/manifest.json` instead of duplicating milestone numbers in the workflow.

Documentation-only changes no longer reinstall Chromium or rerun the browser suite, and newer commits cancel obsolete in-progress runs on the same branch.

## Validation

GitHub Actions run `34794583346` completed successfully. Every deterministic/unit test, exact bridge check, real artifact build, Chromium integration smoke, dynamic artifact-name resolution, and artifact upload passed.

Generated artifact: `atelier-v14-dev.7`.

## Production impact

None. Production remains Atelier 13.2.0 on `main`. V13.3.1 physical-device sign-off remains a separate unresolved production gate.
