# Atelier 14.0.0-dev.7 — Test Report

## Result

**PASS — development milestone only**

This report validates the generated V14 development artifact and its browser-shell integration. It is not a production certification result and does not replace V13.3.1 physical-device acceptance.

## Automated coverage

- V14 source-tool unit tests: PASS
- V14 overlay-build unit tests: PASS
- Notification, dialog, command, file and diagnostics module syntax: PASS
- Notification behavior test: PASS
- Dialog-shell behavior test: PASS
- Command-palette behavior test: PASS
- File-utility behavior test: PASS
- Frozen Atelier 13.2.0 source lock: PASS
- Lossless source extraction: PASS
- Byte-for-byte source round-trip: PASS
- Real V14 development artifact build: PASS
- Exact bridge application for notifications, dialogs, commands and files: PASS
- Manifest-driven artifact structure verification: PASS
- Playwright Chromium installation: PASS
- Generated-artifact browser smoke: PASS
  - V14 shell registration
  - development diagnostics presence
  - real `Ctrl+K` legacy keyboard path
  - command-dialog bridge
  - modular dialog open/focus behavior
  - command search and `data-command="export"` preservation
  - existing dialog close-action path
  - notification rendering
  - filename normalization
  - uncaught page errors: 0
  - console errors: 0
- Dynamic artifact-name resolution: PASS
- Artifact upload: PASS

## CI evidence

- Workflow run: `34794583346`
- Conclusion: `success`
- Artifact: `atelier-v14-dev.7`
- Artifact ID: `10328823572`
- Artifact digest: `sha256:3ee3d0ea32cd39558d42b0f38a1a4695ae6002d524780d412911d2e7e1f813dc`

## CI efficiency

The final workflow is manifest-driven, cancels superseded runs on the same branch, and ignores Markdown-only commits. The Chromium gate therefore runs for development changes that can affect the artifact without being repeatedly triggered by release-note/test-report edits.

## Runtime isolation

All V14 changes remain on `v14-development` and in separately generated artifacts. Root production `index.html` on `main` remains Atelier 13.2.0.
