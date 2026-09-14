# Atelier 14.0.0-dev.10 — Modular Text Escaping Service

## Scope

Tenth V14 development milestone. Dev.10 centralizes repeated HTML/SVG/XML escaping behind a small deterministic shell service without moving project state, persistence, geometry, catalog ownership, or rendering.

## Added

- `src/v14/shell/text.js` — modular HTML/XML escaping service.
- `src/v14/patches/text-bridge.json` — four fail-closed exact bridges for the existing escaping helpers.
- `tools/test_v14_text.mjs` — isolated behavior suite.
- Integrated text-service probes in the Chromium/Firefox/WebKit browser matrix.
- Text-service restoration verification in the controlled offline/PWA gate.

## Preserved behavior

`escapeHtml(value)` preserves the legacy generic HTML/SVG contract:

- null/undefined -> empty string;
- other values converted through `String(...)`;
- `&` -> `&amp;`;
- `<` -> `&lt;`;
- `>` -> `&gt;`;
- `"` -> `&quot;`;
- `'` -> `&#39;`.

`escapeXml(value)` preserves the dedicated XML contract, using `&apos;` for apostrophes.

The migration retains single-pass legacy behavior: existing entity text is escaped again rather than decoded.

## Bridge strategy

The bridge deliberately patches only unique helper prefixes rather than duplicating each complete regex/map expression. The untouched remainder of every legacy expression remains the exact fallback branch in the locked runtime.

Migrated helpers:

1. generic `esc` -> `escapeHtml`;
2. `svgEsc` -> `escapeHtml`;
3. plan XML helper `xml` -> `escapeHtml` to preserve its existing `&#39;` behavior;
4. dedicated `escXML` -> `escapeXml`.

If the V14 service is unavailable, each original legacy `.replace(...)` implementation continues to execute.

## Validation

GitHub Actions run `34816085941` completed successfully.

Passed gates include:

- source/build unit tests;
- JavaScript syntax validation;
- isolated text escaping behavior;
- exact baseline lock verification;
- byte-for-byte source round trip;
- all four text bridge occurrence checks;
- generated artifact build and structure verification;
- Chromium desktop integration;
- Chromium mobile/touch integration;
- Firefox desktop integration;
- WebKit desktop integration;
- direct HTML and XML escape probes;
- controlled offline/PWA reload with the text service restored;
- artifact upload.

Generated artifact: `atelier-v14-dev.10`.

## Production impact

None. Production remains Atelier 13.2.0 on `main`. V14 remains an uncertified development branch. Automated V14 browser/PWA checks do not satisfy the outstanding V13.3.1 physical-device evidence requirement.
