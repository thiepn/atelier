# Atelier 14.0.0-dev.3 — Test Report

## Result

**PASS — development milestone only**

This report validates the V14 shell-notification migration. It is not a V13.3.1 physical-device certification result and does not change production status.

## Automated coverage

- V14 source-tool unit tests: PASS
- V14 overlay-build unit tests: PASS
- Notification module JavaScript syntax: PASS
- Development diagnostics JavaScript syntax: PASS
- Notification behavior test: PASS
  - service registration
  - duplicate announcement suppression
  - toast visibility and 4300 ms lifetime
  - previous-toast timer cancellation
  - save/status rendering
  - error announcement
  - readiness event
- Frozen Atelier 13.2.0 source lock: PASS
- Lossless source extraction: PASS
- Byte-for-byte source round-trip: PASS
- Real V14 development artifact build: PASS
- `shell-notifications-bridge` patch count: 1
- Notification bridge changes: 3/3 matched exactly once
- V14 artifact structure validation: PASS
- GitHub Actions artifact upload: PASS

## CI evidence

- Workflow run: `34793861206`
- Conclusion: `success`
- Artifact: `atelier-v14-dev.3`
- Artifact ID: `10328518728`
- Artifact digest: `sha256:31382b60176993c217453131e9b22c5b3c81bfc0e1300126f391db2bf365301c`

## Runtime isolation

The root `index.html` remains the locked Atelier 13.2.0 baseline. Notification delegation exists only in the separately generated V14 development artifact.
