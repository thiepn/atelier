# Atelier Physical Acceptance

This directory contains two separate real-device certification tracks:

1. **V13.3 / V13.3.1** — certification of the deployed Atelier 13.2.0 production runtime.
2. **V14 RC** — physical testing of the staged V14 release candidate. This does not authorize production promotion by itself.

## V14 RC — dev.17

### Live runner

`https://thiepn.github.io/atelier/v14-rc-staging/acceptance.html`

### Exact staged candidate

`https://thiepn.github.io/atelier/v14-rc-staging/app/`

Current identity:

- version: `14.0.0-dev.17`
- cache: `atelier-v14-rc-14.0.0-dev.17`
- index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- service-worker SHA-256: `bf668c12ecf58f3d7c11cf0ceb98dada3edf6408947ab42caf5aff56802c7043`

The live runner verifies the index and service-worker hashes itself before evidence can become ready.

### Required V14 targets

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

For each real target:

1. open the live V14 runner;
2. confirm automatic candidate identity verification passes;
3. open the staged RC using the runner link;
4. perform every target-specific check on the actual browser/device;
5. record PASS or FAIL truthfully;
6. fill tester/device/OS/browser metadata;
7. attest the run;
8. export the evidence JSON.

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v2`.

Validate a completed evidence folder with:

```bash
python validate_v14_rc_acceptance.py \
  --rc-status /path/to/v14-rc-status.json \
  --evidence-dir /path/to/evidence \
  --write-report v14-rc-physical-report.json \
  --write-signoff v14-rc-physical-signoff.json
```

The V14 validator distinguishes `PHYSICAL_READY`, `PRIOR_RELEASE_GATE_READY` and `PROMOTION_READY`. Five genuine V14 passes may complete the physical gate while production promotion remains blocked by V13.3.1 or later cutover gates.

**Current genuine V14 physical evidence: 0/5.** Synthetic CI fixtures test tooling only.

See:

- `v14-rc-required-targets.json`
- `validate_v14_rc_acceptance.py`
- `v14-rc-cutover-plan.json`
- `V14_RC_CERTIFICATION.md`

---

## V13.3 / V13.3.1 — production 13.2.0

V13.3 and V13.3.1 certify the already-deployed Atelier **13.2.0** runtime. The production root remains byte-frozen.

### Runtime lock

- Production: `https://thiepn.github.io/atelier/`
- Runtime release: `13.2.0`
- Release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`
- PWA cache: `atelier-space-studio-13.2.0`

### Recommended V13 runner

Use `DEVICE_ACCEPTANCE_13.3.1.html`. It wraps the original V13.3.0 evidence generator with local per-target draft recovery. Attestation is deliberately never restored and must be checked again after a reload.

Supported target query values:

- `firefox-desktop`
- `safari-macos`
- `safari-ios-iphone`
- `safari-ipados-ipad`
- `chrome-android-installed-pwa`

### V13 final sign-off

Use `SIGNOFF_CENTER_13.3.1.html` or:

```bash
python validate_acceptance.py --evidence-dir ./evidence
```

V13 production sign-off is complete only when the validator reports:

`SIGNOFF_READY=true`

with five distinct genuine physical targets.

**Current V13.3.1 physical evidence: 0/5.**

Do not infer, simulate or fabricate a physical-device pass in either certification track.
