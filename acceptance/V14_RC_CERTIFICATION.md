# Atelier V14 RC Certification

## Purpose

This directory now contains a V14 release-candidate certification layer that is separate from the unresolved V13.3.1 production sign-off.

It is designed to let real V14 RC physical evidence be collected and validated later without implying that production promotion is authorized.

## Inputs

A V14 RC evidence set is bound to the generated `v14-rc-status.json` from the exact candidate package being tested.

Each evidence file must match:

- RC version;
- RC `index.html` SHA-256;
- RC `sw.js` SHA-256;
- RC cache identity;
- one normalized HTTPS candidate origin;
- one required physical target.

The evidence schema is `atelier-v14-rc-physical-acceptance-evidence-v1`.

## Required physical targets

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Target-specific required checks are defined in `v14-rc-required-targets.json`.

Synthetic fixtures are permitted only to verify the validator. They never satisfy the physical gate.

## Validation

Run:

```bash
python acceptance/validate_v14_rc_acceptance.py \
  --rc-status /path/to/v14-rc-status.json \
  --evidence-dir /path/to/physical-evidence \
  --write-report v14-rc-physical-report.json \
  --write-signoff v14-rc-physical-signoff.json
```

The validator reports three distinct states:

- `PHYSICAL_READY` — all five real physical targets are valid and PASS;
- `PRIOR_RELEASE_GATE_READY` — the candidate's certification metadata says the unresolved prior-release gate is satisfied;
- `PROMOTION_READY` — both conditions above are true.

A physical sign-off file may be generated when the V14 physical gate is complete even if promotion remains blocked by the prior-release gate. This separation prevents valid V14 testing from being confused with authorization to deploy it.

## Candidate origin

Physical evidence must come from one normalized HTTPS origin in the form:

`https://host[:port]/`

All five files in one evidence set must reference the same origin.

The current cutover plan does not provision a staging origin and explicitly forbids using the production origin for V14 until the prior-release sign-off allows runtime advancement.

## Cutover and rollback

`v14-rc-cutover-plan.json` defines the later production gates. Even after V14 RC physical acceptance passes, production still requires:

- prior-release final sign-off;
- exact production artifact hash matching;
- production-origin verification;
- installed-PWA update recovery;
- offline cold start after update;
- rollback to the 13.2.0 baseline;
- project data surviving both update and rollback;
- stale-cache cleanup without project-data loss.

Automatic promotion is forbidden.

## Current state

Real V14 RC physical evidence: **0/5**.

Staging origin: **not provisioned**.

Production cutover: **blocked**.

V13.3.1 prior-release physical sign-off: **blocked**.
