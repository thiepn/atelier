# Atelier Space Studio

**Current release: 13.2.0 — Production Deployment & Real-Device Acceptance**

Atelier is a local-first browser space-planning studio with a static PWA deployment. V13.2 hardens production deployment, touch accessibility and interrupted-update recovery while retaining V10 project compatibility.

## Release focus

V13 does not expand Atelier horizontally. It hardens the application that already exists: runtime boundaries, deterministic builds, schema/version contracts, performance budgets, crash containment, production diagnostics, and release certification tooling.

### Modular development, static deployment

Atelier remains deployable as a static GitHub Pages PWA with a single self-contained `index.html`, but development source is now split into ordered logical modules under `src/`.

- `src/shell.html` — document shell
- `src/styles/app.css` — application styles
- `src/runtime/*.js` — ordered runtime modules
- `src/modules.json` — deterministic module order
- `tools/build_single_file.py` — rebuilds the deployable single-file app
- `tools/extract_source_modules.py` — regenerates modular development sources

`python tools/build_single_file.py --verify-index` must reproduce the checked-in `index.html` byte-for-byte.

### Production runtime contract

V13 centralizes release and compatibility assumptions:

- Application: **13.2.0**
- Project schema: **V10**
- Accepted schemas: **V1–V10** through the existing strict normalization path
- PWA cache: `atelier-space-studio-13.2.0`
- Deploy HTML budget: **2 MB**
- Active-floor object ceiling: **5,000**

No project migration is required.

### Crash containment and safe mode

Runtime rendering is split into guarded stages. A failure in a specialist panel or render stage is recorded in diagnostics instead of automatically taking down the entire editor.

If 3D initialization or a critical view stage fails, Atelier can preserve the project and fall back to 2D. The explicit recovery URL is:

`?safe=1`

Safe mode bypasses 3D initialization while retaining project access, recovery, diagnostics, and export tools.

### Production Health

**Advanced → Platform & performance → Production health** exposes:

- release/schema contract
- runtime fault count and degraded stages
- performance-budget status
- boot/runtime health
- safe-mode state
- project serialization/preflight status

Production Health can be exported as JSON for release/debugging evidence.

### Performance budgets

V13 converts the V12 profiler into release gates. The runtime tracks interaction, render, input-latency, picking, geometry-patch, selection-upload, and scene-rebuild timings. Startup shader compilation and the first scene build are excluded from interaction-budget failure classification.

### Release tooling

`tools/release_gate.py` verifies the deployable artifact before release, including deterministic rebuild, release/cache identity, manifest/service-worker contract, JavaScript syntax, module inventory, and deployment size.

GitHub CI configuration is included at `.github/workflows/release-gate.yml`.

## Validation

- Inherited V12/V11 regression matrix: **325/325 PASS**
- V13 production-foundation checks: **27/27 PASS**
- V13.2 production deployment release gate: pending final run
- V13.2 runtime/browser/keyboard/touch certification: pending final run
- PWA worker lifecycle/protocol: **15/15 PASS**
- Available-engine browser matrix: **11 PASS / 2 SKIP**
- Aggregate automated result: **428 PASS / 2 SKIP**
- Separate full-quality WebGL PNG export: **PASS**

Firefox and WebKit are **not claimed as certified** in this environment because their executable browser binaries are unavailable and browser-engine downloads are blocked by sandbox network policy. Real served-origin installed-PWA integration is also pending because this environment blocks navigation to HTTP/HTTPS test origins. Physical Safari/iOS/Android PWA acceptance remains external release work.

See:

- `RELEASE_NOTES_13.2.0.md`
- `CROSS_ENGINE_PWA_CERTIFICATION_13.2.0.md`
- `CERTIFICATION_MATRIX_13.2.0.json`
- `EXTERNAL_ACCEPTANCE_13.2.0.md`
- `TEST_REPORT_13.2.0.md`
- `ARCHITECTURE_V13.md`
