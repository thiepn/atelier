# Atelier Space Studio

**Current release: 13.2.0 — Production Deployment & Real-Device Acceptance**

Atelier is a local-first browser space-planning studio with a static PWA deployment. V13.2 closes the automated production-deployment phase while retaining V10 project compatibility and the full V12 feature set.

## Production status

V13.2 is deployed from `main` on GitHub Pages.

- Production URL: `https://thiepn.github.io/atelier/`
- Production release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- Clean release tree: `858762f96799ff6ae522174c5e4bedc701f7df94`
- GitHub Pages deployment run: `34777414838` — **SUCCESS**
- Production `index.html` blob: `324884caabe3e52963ac3c7a081c627372ccff71`
- Production `sw.js` blob: `cd920b34f76528b0779e87d19c14e01a111841fd`
- PWA cache: `atelier-space-studio-13.2.0`

The Pages deployment succeeded for the exact release commit. The assistant browsing environment could not independently fetch the public Pages URL because of its safe-open policy, so no separate HTTP-content verification is claimed.

## Release focus

V13 does not expand Atelier horizontally. It hardens the application: runtime boundaries, deterministic builds, schema/version contracts, performance budgets, crash containment, release diagnostics, PWA recovery and certification.

### Modular development, static deployment

Atelier remains deployable as a static GitHub Pages PWA with a self-contained `index.html`, while development source is organized into logical modules under `src/`. The deterministic build must reproduce the deployable HTML byte-for-byte.

### Production runtime contract

- Application: **13.2.0**
- Project schema: **V10**
- Accepted schemas: **V1–V10**
- Deploy HTML budget: **2 MB**
- Active-floor object ceiling: **5,000**
- No project migration required

### Crash containment and safe mode

High-level render stages are guarded independently. Runtime faults are aggregated in diagnostics rather than automatically taking down the whole editor. `?safe=1` bypasses 3D initialization while preserving project access, recovery, diagnostics and compatible exports.

### Production Health and Release certification

**Advanced → Platform & performance** exposes Production Health and Release certification, including runtime faults, performance budgets, current release/cache, browser/platform data, accessibility results, PWA status and exportable JSON diagnostics.

## V13.2 acceptance

- Full inherited application regression matrix: **325/325 PASS**
- Production foundation & containment: **37/37 PASS**
- Production release gate: **28/28 PASS**
- Runtime keyboard/touch/deployment certification: **30/30 PASS**
- PWA lifecycle/offline/update protocol: **16/16 PASS**
- Interrupted-update rollback/roll-forward: **11/11 PASS**
- Available browser matrix: **11 PASS / 2 SKIP**
- Aggregate automated result: **458 PASS / 2 SKIP**
- Mobile touch targets: **37/37 ≥ 32 px**
- Presentation-quality WebGL PNG export: **PASS**
- GitHub Pages deployment: **PASS**

The two browser skips are Firefox and WebKit because their executable binaries are unavailable in the current sandbox. Physical Safari/macOS, Safari iPhone/iPad and Chrome Android installed-PWA acceptance remain pending and are not claimed as certified.

## Release documents

- `RELEASE_NOTES_13.2.0.md`
- `TEST_REPORT_13.2.0.md`
- `CERTIFICATION_MATRIX_13.2.0.json`
- `EXTERNAL_ACCEPTANCE_13.2.0.md`
- `ARCHITECTURE_V13.md`
- `production.config.json`
