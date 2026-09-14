# Atelier 14.0.0-dev.17 — Test Report

## Result

**PASS — staging and physical-evidence infrastructure validated.**

This result certifies the dev.17 tooling and staged RC identity only. It does not count as physical-device acceptance and does not authorize production promotion.

## Primary workflow

Run `34885183276` completed successfully.

Passed gates:

- deterministic source/build tests;
- frozen architecture and migration policy;
- shell/helper behavior suites;
- exact 13.2.0 baseline round trip;
- dev.17 development artifact generation;
- stripped RC packaging;
- staging package generation;
- exact RC index/SW identity checks;
- V14 RC evidence-validator synthetic self-test;
- fail-closed production-promotion check;
- Chromium desktop;
- Chromium mobile/touch;
- Firefox desktop automated;
- WebKit desktop automated;
- development offline reload;
- stripped RC Chromium startup/offline reload;
- physical evidence runner browser smoke;
- runner-generated evidence accepted by the V14 validator;
- development, RC and staging artifact upload;
- isolated staging subtree publication to `main`.

## Live HTTPS verification

Independent run `34885579138` completed successfully.

It verified the public HTTPS staging endpoints and required:

- public `staging-status.json` to equal the committed staging status;
- public staged `index.html` SHA-256 to equal `e80221516956cd03edb2f92914505fd1ccacbb07ef52fcaa49a5e4ae93d0b89f`;
- public staged `sw.js` SHA-256 to equal `bf668c12ecf58f3d7c11cf0ceb98dada3edf6408947ab42caf5aff56802c7043`;
- public physical runner to contain the v2 evidence contract and identity-verification logic;
- public production `index.html` to remain the frozen 13.2.0 hash;
- public production `sw.js` to remain the frozen 13.2.0 hash.

## Production immutability

The staging publication commit on `main` is `d66b5fd08c71cd461eedb1f0925e491372641978`.

Compared with its parent, every changed file is under `v14-rc-staging/**`; no production root runtime file changed.

## Physical evidence state

- Firefox Desktop: pending
- Safari macOS: pending
- Safari iPhone / Home Screen Web App: pending
- Safari iPad / Home Screen Web App: pending
- Chrome Android Installed PWA: pending

**Valid genuine evidence: 0/5.**

Synthetic CI evidence validates tooling only and is not accepted as physical evidence.

## Promotion state

Still blocked by:

1. `prior-final-signoff-not-pass`
2. `runtime-advance-not-authorized`
3. `physical-evidence-incomplete`

Production remains Atelier 13.2.0.
