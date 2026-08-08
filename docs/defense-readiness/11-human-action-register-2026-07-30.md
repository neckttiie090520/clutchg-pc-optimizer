# ClutchG Human Action Register

**Date:** 2026-07-30  
**Purpose:** assign every remaining human or external gate to a real role, prerequisite, and retained exit artifact  
**Rule:** an item is not complete because a draft exists. It closes only when the named evidence is retained and reviewed.

## 1. Status and ownership model

- `READY` — prerequisites are available; a human owner may start.
- `BLOCKED` — a prerequisite, authority, environment, or decision is missing.
- `IN REVIEW` — work exists but the designated reviewer has not accepted it.
- `EXTERNAL GATE` — requires OAuth, institution, VM/hardware, certificate, or another authority.
- `DONE` — exit evidence is retained, linked, dated, and accepted.

Roles used below are responsibilities, not fabricated assignees:

- **Researcher:** owns the thesis argument, source selection, participant work, evidence retention, and oral defense.
- **Advisor:** approves research scope, claims, method, and submission readiness.
- **Statistician/method reviewer:** validates design, sample-size rationale, interaction analysis, and fallback model.
- **Ethics authority/program:** issues approval, exemption, or documented non-review determination.
- **VM operator/reviewer:** executes privileged tests on disposable Windows environments and signs the record.
- **Repository reviewer:** reviews and merges GitHub changes; does not certify research results.
- **Document reviewer/program staff:** verifies institutional format and final rendered output.

## 2. Ordered closure register

| ID | Human/external action | Owner role | Prerequisites | Retained exit evidence | Related GitHub item | Initial state |
|---|---|---|---|---|---|---|
| H-01 | Authorize GitHub Project scope and run the reconciler | Researcher/repository owner | Review requested OAuth scope; authenticated `gh` account | `gh auth status`, Project URL, reconciler JSON report, screenshot/export of fields/items | PR #12; local task #50 | `EXTERNAL GATE` |
| H-02 | Review and merge the governance-only PR | Repository reviewer | PR #12 diff reviewed; no sensitive paths/data; unit tests 7/7 | merged PR URL and merge commit | PR #12 | `IN REVIEW` |
| H-03 | Freeze a reviewable product/evidence baseline | Researcher + repository reviewer | Classify all dirty/untracked files; remove secrets/private material; decide included change set | reviewed commit/tag or archive SHA-256, clean-or-explained status, environment record | #5 | `BLOCKED` |
| H-04 | Choose one canonical thesis chapter set | Researcher + advisor | Compare root `output/*.md` with organized `output/chapters/**`; identify newer passages | signed source decision, chapter inventory, source hashes, archived/superseded mirror list | #11 | `READY` |
| H-05 | Decide the measured construct and title wording | Researcher + advisor | Review current title/objectives against actual outcomes | approved Thai/English title, objectives, outcome definitions, decision note | #10 | `READY` |
| H-06 | Obtain formal human-research determination | Researcher + advisor + ethics/program authority | Final participant protocol, risks, compensation, consent, data handling | approval/exemption/non-review letter or reference number, approved consent materials | #10 | `EXTERNAL GATE` |
| H-07 | Validate experimental design and statistical plan | Statistician/method reviewer + advisor | Resolve construct; draft machine assignment, difficulty order, sample-size rationale, exclusions | signed/reviewed method note covering confounding, interaction model, assumptions, fallback, effect sizes and CIs | #10 | `BLOCKED` by H-05 |
| H-08 | Correct the participant protocol before collection | Researcher + advisor | H-06 and H-07; reconcile A/B wording, timing, randomization/counterbalancing, safety and reset steps | versioned protocol, run sheet, randomization/counterbalancing schedule, pilot record | #10 | `BLOCKED` by H-06/H-07 |
| H-09 | Conduct an approved pilot | Researcher + participant/observer | H-08; prepared machines and instruments | pilot consent, anonymized run log, timing record, deviations and protocol revision decision | #10 | `BLOCKED` by H-08 |
| H-10 | Collect participant evidence | Researcher | approved protocol; successful pilot; participant recruitment | consent records stored privately, participant-code register, raw CapFrameX/LatencyMon/resource logs, environment metadata, exclusions/deviations | #10 | `BLOCKED` by H-09 |
| H-11 | Analyze participant data and review interpretation | Researcher + statistician/advisor | complete and quality-checked H-10 dataset | analysis script/workbook, immutable input hash, outputs, assumption checks, effect sizes/CIs, reviewer disposition | #10 | `BLOCKED` by H-10 |
| H-12 | Run current-source privileged Sandbox/VM V&V | VM operator + reviewer | H-03 source hash; disposable default/no-GPU/no-network environments; approved test plan | raw text/JSON logs, environment details, source hash, FAIL/WARN/SKIP disposition, signed summary | #8 | `BLOCKED` by H-03 |
| H-13 | Verify apply, cancellation, rollback and state restoration | VM operator + reviewer | H-12 environment; recovery plan; before-state capture | before/apply/cancel/rollback evidence, backup/journal IDs, final-state comparison, anomalies | #8 | `BLOCKED` by H-12 |
| H-14 | Decide and close the coverage requirement | Researcher + advisor/reviewer | H-03 baseline; current measured 39%; NFR wording | either meaningful tests meeting the agreed metric, or approved Change Request defining justified scope/threshold and limitation | #9 | `BLOCKED` by H-03 |
| H-15 | Reconcile every active numeric and safety claim | Researcher + advisor | H-03, H-11, H-13, H-14; one current evidence set | claim register showing source/date/scope/status; stale numbers removed or marked historical | #6 | `BLOCKED` by H-03/H-11/H-13/H-14 |
| H-16 | Refresh bidirectional traceability | Researcher + software reviewer | H-03 and H-15 | objective/FR → design → code → exact test/manual case → result → thesis section matrix, with explicit gaps | #7 | `BLOCKED` by H-15 |
| H-17 | Apply evidence-first thesis revisions | Researcher; advisor reviews | H-04, H-05, H-11, H-15, H-16 | editorial decision log, verified citations, accepted prose, zero fabricated values, preserved limitations | #11 | `BLOCKED` by H-04/H-11/H-16 |
| H-18 | Run Thai/English editorial and responsible-AI review | Researcher + language/advisor reviewer | H-17 facts and citations stable | before/after change log, residual-risk list, tool-use disclosure, researcher acceptance | #11 | `BLOCKED` by H-17 |
| H-19 | Generate and inspect final DOCX/PDF | Researcher + document reviewer/program staff | H-18 canonical sources frozen; correct university template confirmed | source hash, generated DOCX/PDF hashes, zero intentional TBDs, page-by-page A4/font/Thai-wrap/table/figure/pagination checklist | #11 | `BLOCKED` by H-18 |
| H-20 | Conduct mock defense and close answer gaps | Researcher + advisor/review panel | H-19 candidate submission and current question bank | rehearsal record, unanswered-question log, revised answers/slides, advisor disposition | #11 | `BLOCKED` by H-19 |
| H-21 | Final submission/defense authorization | Advisor/program authority | all institution-required items above accepted; no unresolved defense-blocking contradiction | signed submission approval or institutional confirmation | #11 | `BLOCKED` |

## 3. Immediate researcher queue

These are the next actions that do not require invented data:

1. Review the OAuth request and, if accepted, run `gh auth refresh -h github.com -s project`; then run `.github/tools/setup_github_project.py --apply` (H-01).
2. Review PR #12 and request/perform merge through normal repository review (H-02).
3. Classify the dirty working tree and choose a freeze strategy; do not use `git add .` (H-03).
4. With the advisor, select the canonical chapter set and decide whether the work is formally a Thesis or Independent Study under the current program rules (H-04).
5. Ask the advisor/program for the ethics route and obtain written determination before participant work (H-06).
6. Book a statistical/method review for machine-treatment confounding, difficulty order, interaction analysis, and sample-size rationale (H-07).

Do not begin participant collection merely to fill Chapter 6 before H-06–H-09 close.

## 4. Evidence package convention

For each completed item, retain a small package rather than a narrative-only statement:

```text
evidence/<gate-id>/<YYYY-MM-DD>/
  README.md          # scope, owner role, environment, source revision
  raw/               # immutable raw outputs or controlled external URI
  summary.md         # result and limitations
  hashes.sha256      # hashes of retained local artifacts
  sign-off.md        # reviewer, disposition, date; no fabricated signature
```

Private participant/ethics material must not be committed to the public repository. Store it in an approved controlled location and place only a sanitized reference/identifier in public evidence.

## 5. Definition of closure

A human action closes only when:

1. the prerequisite source/method version is identified;
2. the responsible role actually performed or reviewed the action;
3. raw or institutional evidence is retained;
4. result, exceptions, and limitations are recorded;
5. affected ISO 29110 work products, GitHub issue, traceability, and thesis claims are updated;
6. no unresolved contradiction is hidden by prose, formatting, or an automated score.

No checklist, tool, issue, PR, or AI review can guarantee a defense result. This register reduces preventable risk and makes the remaining decisions auditable; the committee and university retain final authority.
