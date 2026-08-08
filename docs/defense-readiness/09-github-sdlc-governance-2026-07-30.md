# GitHub SDLC and ISO 29110 Governance Runbook

**Date:** 2026-07-30
**Repository:** `neckttiie090520/clutchg-pc-optimizer`
**Scope:** truthful project governance for defense-readiness work; no invented dates, assignees, or completed states

## 1. Published governance baseline

- Milestone: [Defense Readiness 2026](https://github.com/neckttiie090520/clutchg-pc-optimizer/milestone/1)
- [#5 Freeze a traceable source and evidence baseline](https://github.com/neckttiie090520/clutchg-pc-optimizer/issues/5)
- [#6 Reconcile all test, coverage, and safety claims](https://github.com/neckttiie090520/clutchg-pc-optimizer/issues/6)
- [#7 Refresh bidirectional requirements traceability](https://github.com/neckttiie090520/clutchg-pc-optimizer/issues/7)
- [#8 Run current-source Sandbox apply and rollback V&V](https://github.com/neckttiie090520/clutchg-pc-optimizer/issues/8)
- [#9 Close the 39% coverage requirement gap](https://github.com/neckttiie090520/clutchg-pc-optimizer/issues/9)
- [#10 Resolve participant-study design, statistics, and ethics](https://github.com/neckttiie090520/clutchg-pc-optimizer/issues/10)
- [#11 Synchronize thesis sources and regenerate final artifacts](https://github.com/neckttiie090520/clutchg-pc-optimizer/issues/11)

These issues represent real P0/P1 gaps. They are not placeholders for activity that has already happened and are not evidence by themselves.

## 2. Label model

| Label | Meaning |
|---|---|
| `priority:P0` | blocks a defense/release claim |
| `priority:P1` | high-priority evidence or quality gap |
| `type:evidence` | verification, validation, traceability, or retained result |
| `type:governance` | ISO 29110, SDLC, ethics, or project-control decision |
| `external-gate` | requires VM, hardware, credential, institution, or human action |
| `human-signoff` | requires a named reviewer/authority decision |
| `thesis` | affects thesis or defense readiness |

Use existing `bug`, `documentation`, and `enhancement` labels only when their normal GitHub meaning applies. Do not encode workflow state in labels when a Project field is available.

## 3. Issue-to-SDLC/ISO mapping

| Issue | SDLC activity | ISO/IEC 29110 work product/control | Exit evidence |
|---|---|---|---|
| #5 | Configuration/maintenance | Configuration Management Plan, baseline control | reviewed commit/archive hash and inventory |
| #6 | Verification/documentation | Test Record, Change Request, Progress Record | one dated claim baseline across active documents |
| #7 | Requirements/design/testing | SRS, SDD, Test Plan/Record, Traceability | bidirectional FR→design→code→test/result map |
| #8 | System validation | Test Plan/Record, V&V evidence | fresh Sandbox results tied to source hash |
| #9 | Testing/change control | NFR, Test Plan/Record, Change Request | meaningful coverage closure or approved requirement change |
| #10 | Research governance | research protocol, consent, ethics/statistical review | written determinations and approved method |
| #11 | Deployment/documentation | controlled thesis source and generated artifacts | synchronized source plus reviewed DOCX/PDF |

## 4. Proposed GitHub Project

Project creation is currently blocked because the active `gh` token lacks `read:project`/`project` scopes. After the researcher authorizes those scopes, run:

```bash
gh auth refresh -h github.com -s read:project,project
```

In this CLI session, the user can run:

```text
! gh auth refresh -h github.com -s read:project,project
```

Create one repository-linked Project named `ClutchG Defense Readiness`. Recommended fields:

| Field | Values |
|---|---|
| Status | Triage, Ready, In Progress, Review, External Gate, Done |
| Priority | P0, P1, P2, P3 |
| Evidence state | Planned, Automated, Historical, External Required, Human Sign-off, Accepted |
| SDLC phase | Requirements, Design, Implementation, Integration, Testing, Deployment, Maintenance |
| ISO work product | Project Plan, SRS, SDD, Test Plan, Test Record, Traceability, Change Request, Progress, Configuration, User Manual, Research Protocol |
| Owner role | Researcher, Reviewer, Advisor, Statistician, Ethics Authority, CI, VM Operator |

Initial placement:

- #5–#7, #9–#11: `Ready`
- #8: `External Gate`
- nothing is `Done` until its acceptance evidence is retained and reviewed

Do not assign a due date until the researcher and advisor approve one.

### 4.1 Idempotent setup utility

The tracked utility `.github/tools/setup_github_project.py` prints the desired state without network mutation by default:

```bash
python .github/tools/setup_github_project.py
```

Run its offline tests with:

```bash
python -m unittest discover -s tests/unit -p "test_setup_github_project.py" -v
```

After browser authorization, reconcile the Project, fields, repository link, Issues #5–#11, and PR #12:

```bash
gh auth refresh -h github.com -s read:project,project
python .github/tools/setup_github_project.py --apply
```

Apply mode reads the existing Project, fields, and items before each create/add operation. A repeated run adds only missing resources. If the token lacks Project scope, the first list operation fails before any mutation.

## 5. Branch and PR policy

- Never push directly to `main`.
- One PR should close one coherent evidence/change set.
- Stage specific files; do not use `git add .` in a dirty evidence workspace.
- PR body must state requirement/risk, validation scope, evidence class, limitations, and human sign-off.
- Product behavior and evidence documentation may share a PR only when the evidence was produced from exactly that code revision.
- A documentation PR must not turn a planned or external result into a completed claim.
- Preserve hooks and CI. Do not use `--no-verify` unless explicitly approved and documented.

Suggested sequence:

1. GitHub templates/governance only.
2. Reviewed product bug fixes with focused regressions.
3. Current evidence baseline and ISO addendum after source freeze.
4. Traceability refresh.
5. Sandbox evidence metadata after external execution.
6. Thesis source changes remain in the thesis workspace and are not copied into the public repository without approval.

## 6. Issue state transitions

`Triage → Ready` requires clear scope, acceptance criteria, evidence owner, and dependencies.

`Ready → In Progress` requires an owner and identified source baseline.

`In Progress → Review` requires implementation/draft plus validation output.

`Review → External Gate` applies when automated work is complete but a VM, credential, participant, advisor, statistician, or institution must act.

`Review/External Gate → Done` requires retained evidence, reviewer disposition, updated traceability, and no unresolved P0 result.

Reopen an issue when evidence becomes stale because source, method, or document content changes.

## 7. Closure and rollback rules

- A failed deployment/release PR is reverted by a new commit, not history rewriting.
- Incorrect evidence is superseded with a dated correction; historical records remain traceable.
- If a requirement changes, create/approve a Change Request before editing the claimed acceptance threshold.
- If a participant method changes, obtain advisor/statistical/ethics disposition before data collection continues.
- Closing an issue does not imply the thesis or release is fully ready.

## 8. Public-repository hygiene

Before publishing any artifact:

1. remove absolute local paths, usernames, participant identifiers, credentials, consent forms, and private advisor correspondence;
2. publish summaries and hashes rather than sensitive raw data;
3. verify repository visibility and license/provenance;
4. retain large or restricted evidence outside Git with a controlled URI/reference;
5. ensure generated prose is researcher-reviewed and no unsupported result is present.

## 9. Governance acceptance criteria

- reusable Issue and PR templates are merged;
- milestone and seven real P0/P1 issues remain visible;
- Project exists after scope authorization, or the authorization blocker remains documented;
- every issue has ISO/SDLC mapping and evidence-based exit criteria;
- no ticket is closed merely because a document was drafted;
- no public artifact contains private thesis or participant data.
