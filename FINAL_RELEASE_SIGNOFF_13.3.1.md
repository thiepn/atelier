# Atelier V13.3.1 — Physical Evidence Completion & Final Production Sign-off

## Current result

**FINAL PRODUCTION SIGN-OFF: BLOCKED — 0/5 PHYSICAL TARGETS**

V13.3.1 completes the evidence collection, ingestion, and final-signoff machinery. It does not fabricate or infer physical-device acceptance. The production application runtime remains byte-frozen at Atelier 13.2.0.

## Frozen runtime identity

- Production URL: `https://thiepn.github.io/atelier/`
- Runtime release: `13.2.0`
- Release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`
- PWA cache: `atelier-space-studio-13.2.0`

## V13.3.1 completion layer

- `acceptance/DEVICE_ACCEPTANCE_13.3.1.html` is the recommended resumable entry point for physical testing.
- The resumable runner wraps the unchanged `DEVICE_ACCEPTANCE_13.3.0.html` evidence generator, preserving the accepted evidence schema and fingerprint semantics.
- Per-target checklist drafts are stored locally on the testing device; restored drafts deliberately require fresh attestation before export.
- `acceptance/SIGNOFF_CENTER_13.3.1.html` imports all evidence files locally in the browser.
- Existing V13.3.0 evidence remains valid; testers do not have to repeat tests merely because the completion tooling moved to V13.3.1.
- `acceptance/validate_acceptance.py` supports final sign-off generation and validation reports.
- Each accepted evidence file is bound into the final manifest by both its raw file SHA-256 and its internal evidence fingerprint.
- Duplicate target files, tampered evidence, wrong production hashes, missing attestation, missing tester identity, or any non-PASS required result block final sign-off.
- The final sign-off JSON is generated only when all five distinct physical targets are valid.

## Required evidence still missing

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

No genuine physical-device acceptance JSON files were supplied in the current conversation during this phase.

## Gate

The release is final only when the validator prints:

`SIGNOFF_READY=true`

and the final manifest uses schema:

`atelier-final-production-signoff-v1`

Until then, V14 feature development should not be treated as a production-certified successor.
