# Atelier V13.3 — Physical Device Acceptance & Final Release Sign-off

V13.3 is a **certification-only milestone**. The deployed Atelier runtime remains 13.2.0 and is deliberately byte-frozen.

## Added
- Physical-device acceptance runner for Firefox Desktop, Safari macOS, Safari iPhone, Safari iPad and Chrome Android Installed PWA.
- Per-target applicability rules and critical workflow checklist.
- Automatic environment capture (UA/platform/screen/touch/display mode/service-worker control).
- PASS/FAIL notes per acceptance item.
- Evidence JSON export with deterministic SHA-256 fingerprint.
- Offline evidence validator that refuses sign-off on missing/failed/mutated evidence.
- Machine-readable V13.3 certification matrix.
- Explicit final release sign-off gate.

## Runtime policy
No application/runtime changes are permitted during this acceptance milestone without invalidating previously collected device evidence and restarting acceptance for affected targets.

## Current result
Automated production evidence remains valid from V13.2. Physical-device final sign-off is **PENDING** until all required real-device evidence is collected.
