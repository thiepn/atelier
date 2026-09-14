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
- Resumable `DEVICE_ACCEPTANCE_13.3.1.html` wrapper around the unchanged V13.3.0 evidence generator.
- Per-target local draft recovery for interrupted/reloaded physical acceptance runs.
- Direct target selection through the `?target=` query parameter.
- Restored drafts deliberately require fresh tester attestation before evidence export.

## Compatibility

V13.3.0 physical evidence files remain the accepted input format. The V13.3.1 resumable runner delegates final evidence generation to the original V13.3.0 generator, so evidence schema and fingerprint semantics remain unchanged.

Production runtime remains Atelier 13.2.0, schema V10, with unchanged runtime hashes.

## Current sign-off state

BLOCKED: no complete set of five genuine physical-device evidence files has been supplied. Automated or simulated browser tests do not substitute for the required physical targets.
