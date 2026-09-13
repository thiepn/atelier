# Atelier V13.3.1 — Evidence Completion & Sign-off Tooling

V13.3.1 is a certification-tooling release around the frozen Atelier 13.2.0 runtime. It introduces no application-runtime feature changes.

## Added

- Final Sign-off Center for importing all five physical-device evidence files at once.
- Browser-side evidence fingerprint verification and raw-file SHA-256 binding.
- Per-target PASS/PENDING dashboard.
- Duplicate-target and tamper detection.
- Final sign-off JSON export only after a complete valid evidence set.
- Validation-report export for incomplete/failed evidence sets.
- Enhanced Python validator with `--write-signoff` and `--write-report`.
- Deterministic final sign-off schema `atelier-final-production-signoff-v1`.

## Compatibility

V13.3.0 physical evidence files remain the accepted input format. Production runtime remains Atelier 13.2.0, schema V10, with unchanged runtime hashes.

## Current sign-off state

BLOCKED: no real physical-device evidence files were supplied during this implementation run.
