# Atelier V13 Production Architecture

V13 keeps Atelier's public deployment deliberately simple: a static PWA with one generated `index.html`, a manifest, icons, and a service worker. The maintainability change is in the **development source**, not in adding a runtime bundler or server dependency.

## Build boundary

`index.html` remains the authoritative tested deployment artifact. `tools/extract_source_modules.py` deterministically splits it into:

- `src/shell.html`
- `src/styles/app.css`
- ordered logical runtime modules in `src/runtime/`
- `src/modules.json`

`tools/build_single_file.py --verify-index` concatenates those modules and must reproduce `index.html` byte-for-byte. This allows focused code review and future module extraction while retaining GitHub Pages/offline compatibility.

## Runtime boundaries

The existing runtime sections are treated as explicit architectural boundaries: architecture, connected services, studio model, core validation, ecosystem, platform, catalog, presets, assets, realism, intelligence, precision, commands, spatial tools, geometry, 3D scene, plan architecture, 2D plan, project lifecycle, storage, durable storage, exports, exchange, professional tools, AI, icons, advanced UI, and app orchestration.

V13 adds a production-foundation boundary with:

- centralized release metadata;
- project schema compatibility contract;
- performance budgets;
- render-stage isolation;
- runtime fault aggregation;
- safe-mode recovery (`?safe=1`);
- production health/release gating.

## Fault containment

High-level render stages are guarded independently. A failure in sidebar, inspector, metrics, selection tools, controls, extension chrome, or the view renderer is captured instead of automatically terminating the full render call. Repeated view-render faults isolate 3D and preserve the 2D editor/project data path.

Safe mode bypasses 3D initialization entirely while retaining project library, recovery, 2D editing, diagnostics, backup, and non-3D exports.

## Project compatibility

V13 does **not** introduce a V13 document schema. Projects remain V10. The accepted compatibility window remains V1–V10, normalized through the existing strict `validateProject` pipeline. This avoids migration risk in a foundation release.

## Release gates

`production.config.json` is the machine-readable release contract. `tools/release_gate.py` verifies:

- modular build determinism;
- JavaScript syntax;
- manifest validity;
- version/cache consistency;
- artifact size budget;
- service-worker update contract;
- required production-foundation APIs and safe-mode hooks.

Runtime Production Health adds real-device budget measurements once interaction telemetry exists.
