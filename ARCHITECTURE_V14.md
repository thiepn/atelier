# Atelier V14 Development Architecture

## Status

V14 is an **uncertified development cycle** on branch `v14-development`. Production remains Atelier 13.2.0 on `main`; V13.3.1 physical-device sign-off is a separate gate and is not implied by V14 development.

## Milestone 1 — Reproducible source boundary

The V13 architecture described a deterministic `src/` + `tools/` development model, while the deployed repository ultimately retained only the generated monolithic `index.html`. V14 makes that development boundary concrete without rewriting the application runtime.

### Components

- `src/source.lock.json` — pins the exact 13.2.0 runtime used as the V14 baseline.
- `tools/v14_source.py` — losslessly extracts inline HTML/CSS/JS/data segments and rebuilds them byte-for-byte.
- `tools/test_v14_source.py` — regression tests for round-trip integrity, external-script handling, tamper rejection and runtime-lock enforcement.
- `src/generated/` — reproducible local source snapshot generated from the current runtime; not required to be committed.
- `src/v14/` — home for new or migrated V14 modules in later milestones.

### Invariants

1. V14 work does not mutate the certified/frozen production artifacts on `main`.
2. A source extraction followed by a build must reproduce `index.html` exactly.
3. Every generated segment is SHA-256 bound in its manifest.
4. The baseline lock must fail closed if the starting runtime changes unexpectedly.
5. Existing code migrates incrementally; there is no big-bang rewrite.
6. V14 development status must never be presented as V13.3.1 production certification.

## Development flow

```text
index.html (13.2.0 baseline)
        │
        ├── verify source.lock.json
        │
        ▼
tools/v14_source.py extract
        │
        ▼
src/generated/manifest.json + lossless segments
        │
        ├── V14 incremental migration / modules
        │
        ▼
deterministic build
        │
        ▼
V14 development artifact
```

## Next V14 milestone

Milestone 2 should introduce the first real `src/v14/` module boundary and deterministic injection/build step, then migrate one low-risk subsystem out of the monolith. Candidate selection should prioritize isolated UI/application-shell code with strong regression coverage rather than core project persistence or geometry first.
