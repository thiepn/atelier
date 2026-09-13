# Atelier V13.3 Physical Device Acceptance

V13.3 is a **certification milestone** for the already-deployed Atelier **13.2.0 runtime**. The runtime is intentionally frozen during physical acceptance.

## Runtime lock

- Production: `https://thiepn.github.io/atelier/`
- Runtime release: `13.2.0`
- `index.html` SHA-256: `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256: `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`

If either runtime hash changes, previously collected V13.3 device evidence is invalid until the changed runtime is re-tested.

## Required real targets

1. Firefox Desktop
2. Safari macOS
3. Safari iPhone / Home Screen Web App
4. Safari iPad / Home Screen Web App
5. Chrome Android Installed PWA

Automated Chromium simulation does **not** satisfy these physical targets.

## How to collect evidence

1. Open `DEVICE_ACCEPTANCE_13.3.0.html` on the target device.
2. Choose the target profile.
3. Open Atelier using the provided production link.
4. Execute every required checklist item.
5. Mark PASS / FAIL and add notes for any unexpected behavior.
6. Enter tester name/initials and enable the attestation checkbox.
7. Export the evidence JSON.
8. Place exported evidence files in one folder and run:

```bash
python validate_acceptance.py --evidence-dir ./evidence
```

The validator refuses final sign-off when:
- a required target is absent,
- a required step is not PASS,
- the runtime hash is wrong,
- the evidence fingerprint was modified,
- the tester attestation is missing,
- or evidence is structurally invalid.

## Sign-off rule

`FINAL_RELEASE_SIGNOFF_13.3.0.md` may be changed to **FINAL SIGN-OFF: PASS** only after the validator returns `SIGNOFF_READY=true` against evidence from all required physical targets.
