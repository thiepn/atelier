# Atelier V13.3 / V13.3.1 Physical Device Acceptance

V13.3 and V13.3.1 are **certification milestones** for the already-deployed Atelier **13.2.0 runtime**. The production runtime is intentionally byte-frozen while real-device evidence is collected.

## Runtime lock

- Production: `https://thiepn.github.io/atelier/`
- Runtime release: `13.2.0`
- Release commit: `1151f66e58ff4950d7c8ba265834c59d1a46bf5e`
- `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`
- PWA cache: `atelier-space-studio-13.2.0`

If either runtime hash changes, previously collected evidence is invalid for the changed runtime until the affected targets are re-tested.

## Required real targets

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Automated browser simulation does **not** satisfy these physical targets.

## 1. Collect evidence on each physical target

### Recommended runner

Open `DEVICE_ACCEPTANCE_13.3.1.html` on the target device. It wraps the unchanged V13.3.0 evidence generator and adds local per-target draft recovery, so a reload or interrupted test does not erase checklist progress.

The wrapper does **not** persist the attestation checkbox. After a reload or restored draft, the tester must review the restored results and attest again before export.

Direct target links are supported with the `target` query parameter:

- `DEVICE_ACCEPTANCE_13.3.1.html?target=firefox-desktop`
- `DEVICE_ACCEPTANCE_13.3.1.html?target=safari-macos`
- `DEVICE_ACCEPTANCE_13.3.1.html?target=safari-ios-iphone`
- `DEVICE_ACCEPTANCE_13.3.1.html?target=safari-ipados-ipad`
- `DEVICE_ACCEPTANCE_13.3.1.html?target=chrome-android-installed-pwa`

### Test procedure

1. Open the recommended V13.3.1 runner on the real target device/browser.
2. Confirm the matching target profile is selected.
3. Open Atelier using the provided production link.
4. Execute every required checklist item on the real device/browser.
5. Mark each item PASS or FAIL and add notes for unexpected behavior.
6. Enter tester name or initials and the environment details requested by the runner.
7. Review the restored/current results, enable the attestation checkbox, and export the evidence JSON.

`DEVICE_ACCEPTANCE_13.3.0.html` remains available as the original generator. V13.3.1 deliberately continues to accept genuine V13.3.0 evidence, so previously completed physical tests do not need to be repeated merely because the completion tooling changed.

## 2. Complete final sign-off

Two supported paths use the same validation rules.

### Browser path

Open `SIGNOFF_CENTER_13.3.1.html` and import the five exported evidence JSON files. Final sign-off unlocks only when all five distinct required targets validate.

### Python / CI path

Place the exported JSON files in one folder and run:

```bash
python validate_acceptance.py --evidence-dir ./evidence
```

The validator blocks final sign-off when:

- a required target is absent,
- a required step is not PASS,
- the production URL or runtime release is wrong,
- `index.html` or `sw.js` hashes do not match the frozen runtime,
- the internal evidence fingerprint was modified,
- tester identity or attestation is missing,
- two files claim the same required target,
- or an evidence file is structurally invalid.

## Final sign-off rule

The release is production-certified only when the validator reports:

`SIGNOFF_READY=true`

and the generated final manifest uses schema:

`atelier-final-production-signoff-v1`

Only then may `FINAL_RELEASE_SIGNOFF_13.3.1.md` be changed from BLOCKED to PASS and the V14 feature-development cycle be treated as the certified successor path.

Until all five real-device evidence files exist and validate, the correct state remains **BLOCKED**. Do not infer, simulate, or fabricate a physical-device pass.
