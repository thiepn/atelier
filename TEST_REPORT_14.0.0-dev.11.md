# Atelier 14.0.0-dev.11 Test Report

## Result

**PASS — machine-validated migration/dependency inventory**

GitHub Actions run: `34816530041`

## New dev.11 gates

- Migration inventory schema validation: PASS
- Unique boundary IDs: PASS
- Excluded ownership enforcement: PASS
- Exactly one `selected-next` candidate: PASS
- Selected candidate low state risk: PASS
- Selected candidate non-mutating: PASS
- Selected candidate high testability: PASS
- Selected candidate browser coupling within policy: PASS
- Selected candidate has explicit target milestone: PASS
- Duplicate-boundary rejection test: PASS
- Multiple-selection rejection test: PASS
- Excluded-boundary selection rejection test: PASS
- Mutating-candidate selection rejection test: PASS
- Manifest/inventory/artifact version synchronization: PASS
- Selected candidate `dimension-formatting`: PASS
- Target milestone `14.0.0-dev.12`: PASS

## Existing regression gates

- Source-tool unit tests: PASS
- Overlay-build / exact-patch tests: PASS
- Notification behavior: PASS
- Dialog behavior: PASS
- Command-palette behavior: PASS
- File-utility behavior: PASS
- Icon-renderer behavior: PASS
- Text-escaping behavior: PASS
- Frozen 13.2.0 baseline lock: PASS
- Byte-for-byte source round trip: PASS
- Generated artifact structure validation: PASS

## Integrated browser matrix

| Project | Result |
| --- | --- |
| Chromium desktop | PASS |
| Chromium mobile/touch 390×844 | PASS |
| Firefox desktop | PASS |
| WebKit desktop | PASS |

Controlled Chromium offline/PWA reload: **PASS**.

## Migration decision

Dev.12 is authorized to migrate only the pure `fmtDim` dimension-formatting boundary. Persistence, schema, geometry and rendering remain blocked by default.

## Certification boundary

This report covers the V14 development branch only. It does not satisfy any V13.3.1 physical-device production target. Production remains Atelier 13.2.0 on `main`.
