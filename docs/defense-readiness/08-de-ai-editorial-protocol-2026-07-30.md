# ClutchG Thesis Editorial and De-AI Protocol

**Date:** 2026-07-30  
**Scope:** controlled editorial workflow for `thesis-doc`; this document does not modify the thesis source  
**Principle:** improve precision and restore the researcher's voice. Do not conceal tool use, invent evidence, or optimize prose merely to evade an AI detector.

## 1. Definition

“De-AI” in this project means removing generic, repetitive, inflated, marketing-like, or mechanically structured prose while preserving facts, citations, limitations, uncertainty, and technical terminology. It is an editorial quality activity with human approval, not proof of authorship and not a substitute for research evidence.

## 2. Approved capability chain

| Stage | Capability | Output | Human control |
|---|---|---|---|
| Evidence lock | current evidence matrix and source hash | allowed claims and prohibited claims | researcher approves baseline |
| Structural review | `thesis-reviewer`, `thesis-quality-gate` | argument and consistency findings | advisor/researcher disposition |
| Thai scan/edit | `thai-de-ai`, `deai-fix`, `thai-thesis-writing` | marked passages and proposed edits | researcher accepts each substantive edit |
| English scan/edit | `writing-anti-ai` | revised abstract/English passages | researcher verifies meaning |
| Citation check | `thai-citation-manager` plus source inspection | citation reconciliation list | researcher checks original sources |
| ISO check | `iso29110-docs` and current addendum | work-product impact list | document owner approves changes |
| Formatting | packaged A4 skills after content freeze | DOCX/PDF candidate | human page-by-page inspection |

No automated score is evidence that text is “human-written.” Scores are diagnostics only.

## 3. Non-negotiable safeguards

1. Preserve `[TBD]`, `[VERIFY REQUIRED]`, and `[CITATION NEEDED]` until real evidence closes them.
2. Never create participant values, quotations, citations, approvals, measurements, screenshots, or dates.
3. Never remove limitations merely to make a claim stronger.
4. Do not rewrite a technically correct sentence only to lower an AI score.
5. Keep a before/after change log for every accepted substantive revision.
6. Use the researcher's own explanation from notes, experiments, and defense rehearsal where available.
7. Disclose material AI/tool assistance according to CMU/advisor policy.

## 4. Controlled workflow

### Phase A — Freeze and classify

- Select one canonical chapter set.
- Record SHA-256 for every source chapter.
- Classify each paragraph as `evidence`, `interpretation`, `method`, `limitation`, or `administrative`.
- Resolve factual contradictions before stylistic editing.

**Exit:** no passage is edited against an ambiguous evidence baseline.

### Phase B — Diagnostic scan

For each chapter, record:

- inflated significance and marketing phrases;
- filler and excessive nominalization;
- repeated paragraph openers;
- uniform sentence rhythm;
- vague attribution;
- unsupported synthesis or optimistic endings;
- English AI vocabulary and em-dash overuse;
- factual or citation risk discovered during reading.

Use severity `low`, `medium`, or `high`. A factual/citation risk always outranks a style issue.

### Phase C — Minimal edit

Apply edits in this order:

1. correct claim scope;
2. preserve or restore citation linkage;
3. replace inflated language with observed facts;
4. shorten filler;
5. improve paragraph logic;
6. vary rhythm only where natural;
7. retain discipline-specific terms consistently.

Each edit entry must contain: source path, paragraph identifier, reason, before, after, facts/citations checked, researcher decision, reviewer/date.

### Phase D — Independent verification

- Recompare every number, version, test count, hypothesis, and limitation with the evidence matrix.
- Confirm citations against original sources, not only bibliography metadata.
- Confirm that `[TBD]` and external gates remain visible.
- Read the passage aloud; revise only if it is unclear or unnatural.
- Run a second reviewer pass for meaning drift.

### Phase E — Human acceptance

The researcher signs off that:

- the revised wording expresses their intended argument;
- no evidence was added or removed without a traceable source;
- tool assistance is disclosed as required;
- the final text can be defended orally in their own words.

## 5. Chapter-by-chapter rewrite brief

| Area | Rewrite objective | Must preserve | Must not claim yet |
|---|---|---|---|
| Thai/English abstracts | use current software evidence and explicitly state participant-study status | 765/762/3/0 and 39% only when tied to date/scope | completed participant experiment or improved player skill |
| Chapter 1 | align title, problem, objectives, and measured construct | safety/traceability contribution | universal performance gain |
| Chapter 2 | synthesize sources by claim and evidence quality | inclusion/exclusion criteria and source provenance | repository count without canonical definition |
| Chapter 3 | correct machine-treatment, order, timing, ethics, and analysis plan | approved method and limitations | ethics exemption or interaction validity without approval |
| Chapter 4/implementation | describe actual architecture and contract boundaries | code/test traceability | complete runtime validation from mocks/static tests |
| Chapter 5/testing | separate automated, historical, external, and human evidence | raw result scope and skipped-test disposition | current VM/signing pass without artifacts |
| Chapter 6/results | keep participant tables as explicit pending structures | real raw data and approved analysis only | inferred, synthetic, or forecast participant results |
| Chapter 7/conclusion | answer only objectives supported by evidence | limitations and next work | causal player-skill improvement before data |
| Appendices/front matter | synchronize terminology, versions, tables/figures, biography and approvals | institutional wording and retained signatures | administrative completion without sign-off |

## 6. Natural-writing standard

A passage is acceptable when it is direct, specific, evidence-bounded, terminologically stable, and explainable by the researcher. Natural variation is desirable, but forced synonym changes, decorative anecdotes, emotional language, and artificial “soul injection” are prohibited in academic results.

## 7. Editorial acceptance record

Use this row for each changed passage:

| Field | Value |
|---|---|
| File / section / paragraph | |
| Evidence baseline | |
| Detected problem | |
| Edit mode (`minimal`/`rewrite`) | |
| Facts and citations preserved | |
| Residual risk | |
| Researcher decision | Accept / Revise / Reject |
| Reviewer and date | |

## 8. Exit criteria

- zero unresolved factual contradictions in active chapters;
- zero invented or inferred research results;
- zero high-risk AI-style passages after human review;
- all citations verified or visibly marked for verification;
- all substantive edits accepted by the researcher;
- final prose can be defended without relying on generated scripts;
- tool-use disclosure reviewed by the advisor.
