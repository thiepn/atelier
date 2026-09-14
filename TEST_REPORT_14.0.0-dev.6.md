# Atelier 14.0.0-dev.6 — Test Report

## Result

**PASS — development milestone only**

This validates the modular dialog-shell migration on `v14-development`. It does not change production certification.

## Automated coverage

- V14 source-tool unit tests: PASS
- V14 overlay-build unit tests: PASS
- Notification, dialog, command, file and diagnostics module syntax: PASS
- Notification behavior test: PASS
- Dialog-shell behavior test: PASS
  - active-element capture
  - context-menu close adapter
  - title/kicker/content rendering
  - wide modal state
  - `aria-modal` state
  - `showModal()` behavior
  - preferred initial focus
  - close behavior
  - confirm-callback clearing
  - modal-return focus restoration
  - escaped confirmation markup
  - invalid-adapter fallback signals
  - readiness event
- Command-palette behavior test: PASS
- File-utility behavior test: PASS
- Frozen Atelier 13.2.0 source lock: PASS
- Lossless extraction and byte-for-byte round-trip: PASS
- Real V14 artifact build: PASS
- Notification bridge: 3/3 exact matches
- Dialog bridge: 3/3 exact matches
- Command bridge: 2/2 exact matches
- File bridge: 2/2 exact matches
- Artifact structure verification: PASS
- Artifact upload: PASS

## CI evidence

- Workflow run: `34794378836`
- Conclusion: `success`
- Artifact: `atelier-v14-dev.6`
- Artifact ID: `10329665436`
- Artifact digest: `sha256:283e01cf5b9523e868910f6fec2f0ab33f596780542816b4eae549861da97072`

## Runtime isolation

`exportBusy`, `modalReturn` and `confirmCallback` remain private to the legacy IIFE and are accessed only through narrow bridge adapters. The production branch is unchanged.
