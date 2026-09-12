# Atelier Space Studio 12.1.1

Atelier is a local-first browser space-planning studio with a **1,003-object procedural library**, architecture tools, parametric objects, materials, room intelligence, hierarchical layers, reusable room kits, project templates, and realtime 3D.

V12.1.1 is the **cross-browser/PWA hardening** patch on top of the V12.1 workflow-simplification release. It builds on the audited V12.0 Professional Studio candidate without changing the V10 project schema.

## V12.1 workflow simplification retained

### Cleaner primary navigation

The mode bar now keeps only the high-value entries visible:

- Studio
- Advanced
- Arrange

Connected, AI, Ecosystem and Platform still exist, but are grouped inside **Advanced services** instead of competing as parallel primary destinations.

### Workflow-based Studio toolkit

Studio is grouped into:

- **Build & coordinate**
- **Design & present**
- **Review & deliver**
- **Advanced & setup**

No professional subsystem was removed.

### Start here

An optional three-step onboarding path explains:

1. Set the room
2. Furnish & refine
3. Protect & deliver

It also explains when to use quick Room-shell editing versus the professional Architecture graph.

### Save / Backup / Export

These are now explicit separate actions in the top bar:

- `Ctrl/Cmd + S` — **Save** to browser storage
- `Ctrl/Cmd + Shift + S` — **Backup** editable JSON
- `Ctrl/Cmd + E` — **Export** deliverables

For important work, keep downloadable JSON backups; browser storage can be cleared or evicted.

## Compatibility

- Application: **12.1.1**
- Project schema: **V10**
- Catalog: **1,003 objects**
- Categories: **36**
- Active-floor object ceiling: **5,000**
- Migration required from V10/V11/V12.0/V12.1.0 projects: **No**

## Validation

Executed on the exact V12.1.1 source:

- Professional Studio: **26/26**
- final-audit regressions: **20/20**
- V12.1 workflow/usability regressions: **32/32**
- V11.9 project management: **18/18**
- V11.9 lifecycle: **7/7**
- V11.8 visual regression: **19/19**
- forced WebGL2: **7/7**
- browser capability/fallback regression: **17/17**
- service-worker lifecycle contract: **11/11**
- available Chromium cross-browser core: **10/10**

**167/167 executed checks passed.** Firefox and WebKit were attempted by the cross-engine harness but explicitly skipped because their binaries are unavailable in this environment.

See `RELEASE_NOTES_12.1.1.md`, `TEST_REPORT_12.1.1.md`, and `CROSS_BROWSER_PWA_REPORT_12.1.1.md`.

## Acceptance boundary

V12.1.1 adds executable cross-engine and HTTPS/PWA acceptance harnesses. In this environment, Chromium passes the executable core/fallback matrix, while Firefox/WebKit binaries and unrestricted network-origin Chromium are unavailable. Run the included harnesses on those targets before broad cross-browser production certification.
