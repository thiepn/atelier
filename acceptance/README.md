# Atelier Physical Acceptance

This directory contains two separate real-device certification tracks:

1. **V13.3 / V13.3.1** — certification of deployed production runtime Atelier 13.2.0.
2. **V14 RC** — physical testing of the staged V14 release candidate. This does not authorize production promotion by itself.

## V14 RC — dev.19

### Live runner

`https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/acceptance.html?v=14.0.0-dev.19`

### Exact staged candidate

`https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/app/`

### Staging status

`https://thiepn.github.io/atelier/v14-rc-staging/14.0.0-dev.19/staging-status.json`

Identity:

- version: `14.0.0-dev.19`
- cache: `atelier-v14-rc-14.0.0-dev.19`
- index SHA-256: `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`
- service-worker SHA-256: `796f11fe4d8a5142b94a28600a5fb7cccf24039c6f73fc4f77879121121aa7e3`

The runner verifies live RC status and staged index/SW bytes before evidence can become ready.

### Required V14 targets

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

For each real target:

1. open the exact dev.19 runner;
2. confirm identity verification passes;
3. open the staged RC from the runner;
4. perform every target-specific check on the actual browser/device;
5. record PASS/FAIL truthfully;
6. fill tester/device/OS/browser metadata;
7. attest the run;
8. export evidence JSON.

Evidence schema: `atelier-v14-rc-physical-acceptance-evidence-v3`.

### Validate evidence

```bash
python validate_v14_rc_acceptance.py \
  --rc-status /path/to/v14-rc-status.json \
  --evidence-dir /path/to/evidence \
  --write-report /path/to/evidence/v14-rc-physical-report.json \
  --write-signoff /path/to/evidence/v14-rc-physical-signoff.json
```

The validator is strict about the exact immutable candidate and complete result set. Its own specified report/signoff outputs are excluded from later evidence scans, so rerunning the command with outputs in the evidence directory is safe.

The V14 physical gate requires five genuine device/browser evidence files. Synthetic CI fixtures validate tooling only.

**Current genuine V14 physical evidence: 0/5.**

### Audit hardening

The dev.18/dev.19 audit additionally verifies:

- V14 service workers read only their own cache namespace;
- cross-cache poisoning from the frozen production cache is rejected;
- candidates are immutable/versioned;
- prior candidates are preserved;
- WebKit desktop/phone/tablet automated coverage passes;
- publication is separated from read-only validation;
- live HTTPS identity and production-root hashes are checked after publish;
- final production eligibility remains false until later cutover certification.

See:

- `v14-rc-required-targets.json`
- `validate_v14_rc_acceptance.py`
- `v14-rc-cutover-plan.json`
- `V14_RC_CERTIFICATION.md`
- `../CERTIFICATION_MATRIX_14.0.0-rc.json`

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

Use `DEVICE_ACCEPTANCE_13.3.1.html` for V13 physical evidence and `SIGNOFF_CENTER_13.3.1.html` or `python validate_acceptance.py --evidence-dir ./evidence` for final aggregation.

V13 final sign-off is complete only when `SIGNOFF_READY=true` with five distinct genuine physical targets.

**Current V13.3.1 physical evidence: 0/5.**

Do not infer, simulate or fabricate a physical-device pass in either certification track.
