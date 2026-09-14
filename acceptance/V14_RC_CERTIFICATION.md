# Atelier V14 RC Certification

## Live physical-testing entry point

Use the physical evidence runner on each real device/browser:

`https://thiepn.github.io/atelier/v14-rc-staging/acceptance.html`

The exact candidate under test is:

`https://thiepn.github.io/atelier/v14-rc-staging/app/`

The runner verifies the staged `index.html` and `sw.js` SHA-256 values before evidence can become ready.

## Candidate identity

Current RC:

- version: `14.0.0-dev.17`
- cache: `atelier-v14-rc-14.0.0-dev.17`
- index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- service-worker SHA-256: `bf668c12ecf58f3d7c11cf0ceb98dada3edf6408947ab42caf5aff56802c7043`

Staging status is published at:

`https://thiepn.github.io/atelier/v14-rc-staging/staging-status.json`

## Required physical targets

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Every target must complete its required checklist on the actual browser/device.

## Evidence contract

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v2`.

Each file binds:

- acceptance milestone;
- RC version;
- RC index hash;
- RC service-worker hash;
- RC cache identity;
- HTTPS staging host origin;
- exact staged candidate URL;
- exact runner URL;
- target identity;
- tester/device/OS/browser metadata;
- all required test outcomes;
- explicit attestation;
- deterministic evidence fingerprint.

The runner keeps evidence blocked unless candidate identity verifies, every required result is PASS, metadata is complete and the tester attests the run.

Synthetic CI evidence tests the tooling only. It never satisfies the physical gate.

## Validation

Validate exported real evidence with:

```bash
python acceptance/validate_v14_rc_acceptance.py \
  --rc-status /path/to/v14-rc-status.json \
  --evidence-dir /path/to/physical-evidence \
  --write-report v14-rc-physical-report.json \
  --write-signoff v14-rc-physical-signoff.json
```

The validator reports:

- `PHYSICAL_READY`
- `PRIOR_RELEASE_GATE_READY`
- `PROMOTION_READY`

These are deliberately separate. V14 physical testing can complete while promotion remains blocked by the prior-release gate.

## Staging safety

Dev.17 publishes only the `v14-rc-staging/**` subtree on `main`.

The publication workflow verifies before and after copying that production root files retain the frozen Atelier 13.2.0 hashes. An independent HTTPS workflow then downloads the public staging RC and production root and verifies both identities again.

The staged service worker lives under `v14-rc-staging/app/`, so its normal service-worker scope is limited to that path and does not replace the root production worker.

## Cutover and rollback

Staging availability is not production authorization.

`v14-rc-cutover-plan.json` still requires:

- prior-release final sign-off;
- V14 RC physical sign-off;
- exact V14 production artifact identity;
- V14 production-origin verification;
- installed-PWA update recovery;
- offline cold start after update;
- rollback to Atelier 13.2.0;
- project data surviving update and rollback;
- stale-cache cleanup without project-data loss.

Automatic promotion is forbidden.

## Current state

- HTTPS staging: **LIVE / VERIFIED**
- V14 RC automated/tooling validation: **PASS**
- Real V14 RC physical evidence: **0/5**
- V13.3.1 prior-release gate: **BLOCKED**
- V14 promotion ready: **FALSE**
- Production runtime: **Atelier 13.2.0**
