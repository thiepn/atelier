# V14 modules

## Current checkpoint

**14.0.0-dev.17** is the current validated V14 checkpoint.

The application architecture remains frozen at eight modules and seven exact legacy bridges. Dev.17 adds HTTPS staging and physical-evidence capture infrastructure only.

## Build pipeline

Development artifact:

```bash
python tools/v14_build.py --repo-root . --manifest src/v14/manifest.json --output-dir v14-dist --force
```

Release-candidate artifact:

```bash
python tools/v14_rc_package.py --repo-root . --source-dir v14-dist --output-dir v14-rc --force
```

Staging subtree:

```bash
python tools/v14_staging_package.py --repo-root . --rc-dir v14-rc --output-dir v14-staging --force
```

`v14_staging_package.py` copies the exact stripped RC into `v14-rc-staging/app/`, verifies its index/SW hashes, generates the physical acceptance runner, and writes `staging-status.json`.

## Frozen module surface

1. `shell/notifications.js`
2. `shell/dialogs.js`
3. `shell/commands.js`
4. `shell/files.js`
5. `shell/icons.js`
6. `shell/text.js`
7. `shell/units.js`
8. `dev-status/dev-status.js` — development packaging only

Seven exact legacy bridges remain frozen under `patches/`.

## Staging policy

The stabilization inventory requires:

- `phase: stabilization`;
- no new legacy bridges;
- no production cutover;
- isolated development cache `atelier-v14-dev-*`;
- isolated RC cache `atelier-v14-rc-*`;
- RC diagnostics stripped;
- staging path `v14-rc-staging/` only;
- production root runtime immutable;
- path-scoped staging service worker;
- exact HTTPS candidate and runner URLs;
- five real physical targets before physical readiness.

## Live staging

- Runner: `https://thiepn.github.io/atelier/v14-rc-staging/acceptance.html`
- Candidate: `https://thiepn.github.io/atelier/v14-rc-staging/app/`
- Status: `https://thiepn.github.io/atelier/v14-rc-staging/staging-status.json`

Candidate identity:

- version `14.0.0-dev.17`;
- cache `atelier-v14-rc-14.0.0-dev.17`;
- index SHA-256 `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`;
- service-worker SHA-256 `bf668c12ecf58f3d7c11cf0ceb98dada3edf6408947ab42caf5aff56802c7043`.

## Evidence contract

The runner cannot export evidence until its automatic identity check passes and every target-specific required test is marked PASS with complete tester/device metadata and attestation.

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v2`.

The five required targets remain Firefox Desktop, Safari macOS, Safari iPhone, Safari iPad and Chrome Android installed PWA.

Synthetic CI evidence validates tooling only and never counts as physical evidence.

## Validation

- dev.17 workflow `34885183276`: PASS
- independent public HTTPS verification `34885579138`: PASS
- genuine physical evidence: **0/5**
- production promotion: **blocked**

## Ownership boundary

Legacy runtime ownership still includes command execution, project persistence/backups, schema/validation, geometry/project math, identity generation, catalog/application state, numeric editing/project unit state, domain export semantics and 2D/3D rendering.

Do not resume stateful extraction during stabilization merely to increase modularization count.
