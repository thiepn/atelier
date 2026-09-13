# Atelier Space Studio 13.2.0 — Test Report

## Exact application regression matrix
**325/325 PASS** on the frozen V13.2 application bytes:
- core/recovery 26/26
- browser compatibility 17/17
- responsive usability 32/32
- catalog/assets 47/47
- Editing Feel 31/31
- Space-Planning Workflow 34/34
- Real-Device Performance Closure 20/20
- Live Profiler 18/18
- Smooth Interaction 18/18
- Final Audit 20/20
- V11.8 visuals 19/19
- forced WebGL/GPU 7/7
- project management 18/18
- lifecycle/recovery 7/7
- legacy service-worker contract 11/11

## V13/V13.2 gates
- Production foundation & containment: **37/37 PASS**
- Production release gate: **28/28 PASS**
- Runtime keyboard/touch/deployment certification: **30/30 PASS**
- PWA lifecycle/offline/update protocol: **16/16 PASS**
- Interrupted-update roll-forward/rollback: **11/11 PASS**
- Available browser matrix: **11 PASS / 2 SKIP**

## Aggregate automated result
**458 PASS / 2 SKIP**, plus a separate presentation-quality WebGL PNG export PASS.

The two skips are Firefox and WebKit because their browser binaries are not installed in the execution environment. They are not counted as certified.

## Touch acceptance
The 390×844 touch-capable Chromium acceptance viewport reports **37 visible targets / 0 targets below 32 px**.
