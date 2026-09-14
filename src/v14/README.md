# V14 modules

This directory is the home for authored V14 code.

## Build

The root `index.html` remains the locked Atelier 13.2.0 baseline. V14 modules are injected only into a separate development artifact:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir dist --force
```

The builder:

- verifies the frozen baseline through `src/source.lock.json`;
- rejects duplicate V14 injection markers;
- validates module paths and blocks path traversal;
- injects V14 styles before `</head>` and modules before `</body>`;
- copies declared V14 and passthrough assets;
- writes `v14-build-manifest.json` with baseline, artifact and asset hashes;
- never modifies the root `index.html`.

## Current first module

`dev-status/` is a deliberately isolated development diagnostics module. It exposes network, display-mode, service-worker, touch and viewport state and clearly labels the artifact as an uncertified V14 development build. It does not mutate projects, persistence, geometry or rendering state.

## Rules

1. Keep new functionality isolated here until the deterministic build path integrates it.
2. Prefer small subsystem boundaries over another monolithic script.
3. Do not move persistence, backup, project-schema, geometry, or rendering-core code first; begin with low-risk shell/UI modules.
4. Every migrated subsystem needs regression coverage before the old inline implementation is removed.
5. `main` remains the production/certification line until an explicit V14 release cutover.
