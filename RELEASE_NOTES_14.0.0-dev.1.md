# Atelier 14.0.0-dev.1 — Source Architecture Bootstrap

## Scope

First V14 development milestone. No production release and no V13.3.1 certification claim.

## Added

- Dedicated `v14-development` branch.
- Runtime source lock for the exact Atelier 13.2.0 baseline.
- Deterministic lossless `index.html` source segmentation tool.
- Byte-for-byte rebuild/check path.
- Per-segment SHA-256 integrity verification.
- Regression tests for round-trip integrity, external scripts, tampering and lock mismatches.
- `src/` workspace contract for incremental V14 modules.
- V14 architecture document separating development status from production certification.

## Runtime impact

None on production. `main`, the live GitHub Pages runtime, and the 13.2.0 production hashes are unchanged by this development milestone.
