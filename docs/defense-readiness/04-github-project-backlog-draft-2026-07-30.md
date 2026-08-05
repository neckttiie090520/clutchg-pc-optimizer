# GitHub Project Backlog Draft — ClutchG Defense Readiness

**Status:** Draft only — not published  
**Reason:** working tree is not yet a reviewed frozen baseline; Issue/PR creation is outward-facing and requires human approval

## Board fields

- **Status:** Triage / Ready / In Progress / Review / External Gate / Done
- **Priority:** P0 / P1 / P2 / P3
- **Type:** Defect / Test / Documentation / Experiment / Release / Governance
- **Evidence state:** Automated / Historical / External required / Human sign-off
- **Owner:** Researcher / Reviewer / Advisor / CI
- **Target:** Before defense / Before release / Post-thesis

## Milestone 1 — Freeze and reconcile evidence

### GH-DRAFT-01 — Freeze a reviewable source baseline
- Priority: P0
- Type: Governance
- Acceptance:
  - reviewed branch/commit or archive SHA-256
  - dirty files classified as product/evidence/tool/local
  - secrets and PII scan complete
  - baseline metadata retained

### GH-DRAFT-02 — Reconcile test and coverage claims
- Priority: P0
- Type: Documentation
- Evidence: 765 collected, 762 passed, 3 skipped, 0 failed, coverage 39% on 2026-07-30
- Acceptance:
  - README, SRS, Test Plan, Test Record, traceability, thesis and slides use dated/specified scope
  - 70%/85% claim is met or changed through approved change request
  - skipped tests have dispositions

### GH-DRAFT-03 — Define research corpus count
- Priority: P1
- Type: Documentation
- Acceptance:
  - primary repos and supporting sources defined separately
  - 23/28 conflict removed from active narrative and diagrams
  - inclusion/exclusion criteria documented

### GH-DRAFT-04 — Refresh requirements traceability
- Priority: P0
- Type: Documentation/Test
- Acceptance:
  - each P0 FR maps to current symbol/file and exact test node or manual/VM case
  - stale line numbers and test counts removed
  - untested requirements listed as gaps

## Milestone 2 — Current-source external validation

### GH-DRAFT-05 — Run default Windows Sandbox V&V
- Priority: P0
- Type: Experiment
- Evidence state: External required
- Acceptance: fresh text/JSON/summary, FAIL=0, WARN/SKIP disposition, source hash

### GH-DRAFT-06 — Run no-GPU Sandbox V&V
- Priority: P1
- Type: Experiment
- Acceptance: graceful degradation evidence; no safety/transaction skip

### GH-DRAFT-07 — Run no-network Sandbox V&V
- Priority: P1
- Type: Experiment
- Acceptance: graceful degradation evidence; no uncontrolled network dependency

### GH-DRAFT-08 — Verify apply/cancel/rollback transaction
- Priority: P0
- Type: Experiment
- Acceptance:
  - before/apply/after/rollback evidence
  - backup ID and journal retained
  - cancellation before admission and during process verified
  - safety invariants unchanged

### GH-DRAFT-09 — Reconcile historical Hyper-V 20/20 record
- Priority: P1
- Type: Governance
- Acceptance:
  - original source hash/raw evidence linked, or record marked narrative-only
  - explicitly labelled historical baseline

## Milestone 3 — Meaningful quality closure

### GH-DRAFT-10 — Close coverage requirement gap
- Priority: P1
- Type: Test/Change Request
- Do not solve by superficial tests or excluding difficult code without rationale
- Acceptance option A: measured agreed scope reaches threshold with behavior-focused tests
- Acceptance option B: approved change request defines a justified metric/scope and limitations

### GH-DRAFT-11 — Add high-risk branch tests
- Priority: P1
- Type: Test
- Targets: updater external/error branches, backup failure cleanup, process termination fallbacks, profile rollback/cancellation, GUI orchestration
- Acceptance: each test linked to FR/risk and demonstrates a failure mode

### GH-DRAFT-12 — Refresh defense-critical diagrams
- Priority: P2
- Type: Documentation
- Minimum diagrams:
  - GUI → action catalog → batch execution contract
  - backup/mutation/rollback decision flow
  - automated vs Sandbox/VM/UAT coverage boundary
  - evidence traceability overview
- Acceptance: editable source + exported image + verified date

## Milestone 4 — Thesis and defense

### GH-DRAFT-13 — Audit thesis chapters against current evidence
- Priority: P0
- Type: Documentation
- Scope: read-only audit first; researcher applies edits
- Acceptance: chapter/section finding, proposed wording, evidence link, human owner

### GH-DRAFT-13A — Synchronize canonical thesis chapter sources
- Priority: P0
- Type: Documentation/Governance
- Acceptance: one reviewed canonical set; root/organized chapter drift resolved; generated DOCX/PDF identify source revision

### GH-DRAFT-13B — Resolve participant-study design and ethics gates
- Priority: P0
- Type: Experiment/Governance
- Acceptance: written ethics determination; title/construct alignment; machine-treatment and difficulty-order controls approved by advisor

### GH-DRAFT-13C — Validate the statistical analysis plan
- Priority: P0
- Type: Experiment
- Acceptance: statistician/advisor sign-off on interaction power, repeated-measures model, fallback method, confidence intervals and multiplicity handling

### GH-DRAFT-13D — Collect and verify participant evidence
- Priority: P0
- Type: Experiment
- Acceptance: consent and raw logs retained; Chapter 6 tables completed from traceable data; no synthetic values; exclusions documented

### GH-DRAFT-13E — Regenerate and inspect the submission artifact
- Priority: P0
- Type: Documentation
- Acceptance: no unresolved TBD; current baseline; TOC/table/figure lists regenerated; final DOCX/PDF visually inspected and signed off

### GH-DRAFT-14 — Prepare defense Q&A and mock defense
- Priority: P1
- Type: Governance
- Acceptance: question bank reviewed; mock session held; unanswered questions converted to tasks

### GH-DRAFT-15 — Add responsible AI assistance disclosure
- Priority: P1
- Type: Governance
- Acceptance:
  - conforms to university/advisor policy
  - distinguishes assistance from researcher decisions
  - no claim that AI output is evidence without verification

### GH-DRAFT-16 — Final PDF/A4 human inspection
- Priority: P0
- Type: Documentation
- Acceptance: fonts, Thai line breaking, figures, captions, tables, references, pagination and appendices manually reviewed

## Milestone 5 — Controlled release (not required merely to defend unless advisor says so)

### GH-DRAFT-17 — Execute signed pre-release pipeline
- Priority: P1 before release
- Type: Release
- Acceptance: exact version parity, CI URL, hashes, Authenticode publisher, exact asset

### GH-DRAFT-18 — Installer upgrade and relaunch smoke test
- Priority: P1 before release
- Type: Release/Experiment
- Acceptance: prior-version upgrade in disposable VM, relaunch/version verified, failure paths recorded

## Proposed PR sequence

1. Proposed branch `docs/evidence-baseline-2026-07-30` — current matrix, claim reconciliation, no product code
2. `test/coverage-risk-branches` — behavior-focused tests only
3. Proposed branch `docs/traceability-refresh` — FR ↔ symbol ↔ test/manual gate
4. `evidence/sandbox-current-baseline` — evidence metadata; avoid committing huge/raw sensitive artifacts unless repository policy permits
5. Proposed branch `docs/thesis-defense-pack` — reviewed Q&A, limitations, diagrams
6. `release/signed-preflight` — only after explicit authorization and secrets provisioned

## Issue template body

```markdown
## Problem / evidence gap

## Current evidence
- Source baseline:
- Test/runtime artifact:
- Requirement/risk:

## Scope

## Acceptance criteria
- [ ]

## Validation

## Human sign-off required

## Out of scope
```

## Publication rule

Before creating any Issue, Project, PR or release:

1. Researcher reviews title/body and removes local paths or sensitive data
2. Confirm repository visibility and intended audience
3. Link only artifacts suitable for publication
4. Create branch and stage specific files
5. Never push directly to `main`
6. Preserve CI/hooks and require review for evidence-changing PRs

This draft intentionally avoids fabricated assignees, dates, estimates and completed statuses.
