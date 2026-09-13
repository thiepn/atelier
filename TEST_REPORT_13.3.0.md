# Atelier V13.3 — Acceptance Tooling Test Report

## Runtime regression policy
The application runtime is unchanged from the certified/deployed V13.2.0 runtime:
- `index.html` SHA-256 `561d258b10835af1a8dc6719ce411cd05eff53e31713bc73fb733169649cfc46`
- `sw.js` SHA-256 `e8767e445516647851fe5053a3b5c9dd140e0c04ecc719fbfe5eb801094f5236`

Therefore V13.2's **458 PASS / 2 SKIP** automated certification remains the runtime baseline.

## V13.3 tooling validation
The V13.3 acceptance tooling is validated separately for:
- required target inventory,
- checklist rendering,
- environment capture,
- export blocking until all required checks pass,
- tester attestation requirement,
- deterministic evidence fingerprint generation,
- fingerprint tamper detection,
- runtime hash mismatch detection,
- missing target detection,
- failed required step detection,
- duplicate evidence detection,
- all-target sign-off readiness.

Physical target results are not fabricated by this report. They remain pending until evidence is created on the actual devices/browsers.

## Tooling execution result in this environment
- Validator self-test (complete evidence set -> ready): **PASS**
- Validator negative self-test (required FAIL -> blocked): **PASS**
- Desktop acceptance-runner browser smoke: **PASS**
- 390×844 touch/mobile acceptance-runner smoke: **PASS**
- Runner evidence JSON -> Python validator round-trip: **PASS**
- Partial evidence set remains blocked: **PASS** (`2/5 valid`, `SIGNOFF_READY=false`)
- Horizontal overflow in 390×844 runner viewport: **PASS**
- Mobile action control minimum height in runner: **PASS** (>=44 px)

The two generated smoke-test evidence files are synthetic fixtures only and are **not** included as physical acceptance evidence.
