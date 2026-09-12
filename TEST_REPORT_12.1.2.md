# Atelier Space Studio 12.1.2 — Test Report

## Performance-specific regression

`TEST_PERFORMANCE_HOTFIX_12_1_2.py`: **11/11 PASS**

Coverage:

- WebGL renderer active under forced SwiftShader;
- high-performance adapter request present;
- preserved backbuffer disabled;
- fast interaction shader present;
- shader uniform locations cached;
- dynamic resolution actually drops below 1× DPR during interaction;
- interaction diagnostics report active state;
- continuous orbit >= 18 FPS in the deliberately slow SwiftShader environment;
- continuous object transform >= 18 FPS in the same environment;
- full-quality resolution restores after interaction;
- no runtime errors.

Observed benchmark in final run:

- orbit: ~28–30 FPS;
- object transform: ~25–27 FPS.

V12.1.1 comparison in the same benchmark harness:

- orbit: ~2.7 FPS;
- object transform: ~3.3 FPS.

## Functional regression suites

- Professional Studio: **26/26 PASS**
- final-audit regression: **20/20 PASS**
- V12.1 workflow/usability: **32/32 PASS**
- V11.9 project management: **18/18 PASS**
- V11.9 lifecycle/data safety: **7/7 PASS**
- V11.8 visual regression: **19/19 PASS**
- forced WebGL2 renderer: **7/7 PASS**
- browser capability/fallback regression: **17/17 PASS**
- service-worker lifecycle contract: **11/11 PASS**

## Export verification

With `preserveDrawingBuffer:false`, synchronous WebGL 3D capture still produced:

- `data:image/png;base64,...`
- ~4.2 million-character PNG data URL in the forced-GPU test scene;
- no captured runtime faults.

## Compatibility

- project schema remains V10;
- no project migration introduced;
- existing V12.1.1 projects remain valid;
- PWA cache identity is `atelier-space-studio-12.1.2`.
