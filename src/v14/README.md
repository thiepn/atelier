# V14 modules

This directory is the home for authored V14 code.

Rules:

1. Keep new functionality isolated here until the deterministic build path integrates it.
2. Prefer small subsystem boundaries over another monolithic script.
3. Do not move persistence, backup, project-schema, geometry, or rendering-core code first; begin with low-risk shell/UI modules.
4. Every migrated subsystem needs regression coverage before the old inline implementation is removed.
5. `main` remains the production/certification line until an explicit V14 release cutover.
