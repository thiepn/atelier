# Atelier 14.0.0-dev.5 — Browser File Utilities

## Scope

Fifth V14 development milestone. Generic browser file delivery and filename normalization move behind an isolated shell service without changing export payloads, project data, or production runtime behavior.

## Added

- Modular file service: `src/v14/shell/files.js`.
- Exact legacy bridge: `src/v14/patches/files-bridge.json`.
- Dependency-free file-utility behavior test.
- CI coverage for notification, command-palette and file shell services together.

## Migrated behavior

The V14 file service now owns post-bootstrap:

- creating downloadable `Blob` payloads when needed;
- object-URL creation and delayed revocation;
- temporary download-anchor activation;
- safe export filename normalization.

Existing `Blob` objects are reused, the default MIME type remains `application/octet-stream`, object URLs are revoked after 1000 ms, and the original 80-character lowercase filename normalization remains unchanged.

The original `downloadFile` and `safeName` implementations remain as fail-safe fallback.

## Validation

GitHub Actions run `34794229852` completed successfully, including file-service behavior testing, frozen-baseline verification, all three exact shell bridges, real artifact generation, structure verification and artifact upload.

Generated artifact: `atelier-v14-dev.5`.

## Production impact

None. `main`, production Atelier 13.2.0 and V13.3.1 physical acceptance remain unchanged.
