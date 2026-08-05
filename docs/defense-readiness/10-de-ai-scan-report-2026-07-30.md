# Thesis De-AI Scan Report — Editorial Signals Only

**Scan date:** 2026-07-30  
**Source:** intended canonical root chapters under `C:\Users\nextzus\Documents\thesis\thesis-doc\output\chapter1.md` through `chapter7.md`  
**Mode:** read-only scan; no thesis file was changed  
**Raw result:** `docs/defense-readiness/10-de-ai-scan-raw-2026-07-30.json`

## Interpretation boundary

This scan detects text patterns that may merit editorial review. It does **not** determine authorship, prove that a passage was written by a person or AI, validate citations, or repair research design. A low score cannot override a factual contradiction, missing participant evidence, unresolved ethics review, or unsupported claim.

The required repair order remains:

1. evidence and source provenance;
2. methodology and ethics;
3. claim scope and results;
4. citations;
5. prose and terminology;
6. formatting.

## Results

| Chapter | Heuristic score | Label | Main editorial signals | Disposition |
|---|---:|---|---|---|
| 1 | 0.200 | human-like | low vocabulary diversity; 13 bold-in-body markers; one filler occurrence | Minimal edit only after objective/title/evidence alignment |
| 2 | 0.268 | mixed | low vocabulary diversity; 2 em dashes; 11 bold-in-body markers; one marketing phrase (`ครบวงจร`) | Review synthesis and source attribution before sentence polishing |
| 3 | 0.252 | mixed | low vocabulary diversity; 4 em dashes; 14 bold-in-body markers | Do not polish until design, confounding, timing, statistics, and ethics are resolved |
| 4 | 0.217 | human-like | low vocabulary diversity; 1 em dash; 57 bold-in-body markers | Verify architecture/evidence mapping; then normalize typography selectively |
| 5 | 0.167 | human-like | low vocabulary diversity; 3 em dashes; 18 bold-in-body markers | Separate automated, historical, external, and human evidence before editing |
| 6 | 0.224 | human-like | low vocabulary diversity; 3 em dashes; 44 bold-in-body markers | Participant `[TBD]` and stale test claims are blockers; no inferred replacement values |
| 7 | 0.069 | human-like | no flagged vocabulary/filler/typography pattern in this heuristic | Rewrite conclusions only after supported results and limitations are fixed |

All seven scan commands exited successfully. Sentence-length variation passed the tool's burstiness check for every chapter. The raw component named `burstiness` is a normalized risk contribution; the detailed `burstiness.cv` is the directly interpretable sentence-length statistic.

## Findings that matter more than the score

- Chapters 2 and 3 are the only files labelled `mixed`, but Chapter 3 is the highest editorial priority because its methodology has unresolved causal, statistical, timing, and ethics issues—not because its score is 0.252.
- Chapters 6 and 7 have low heuristic scores but remain defense blockers because participant results are incomplete and conclusions cannot outrun evidence.
- Bold-in-body counts may include deliberate Markdown emphasis. They require contextual review; automatic removal would damage technical meaning in tables, identifiers, or definition passages.
- Low type-token ratio in long technical chapters can result from necessary terminology reuse. Forced synonym replacement is prohibited where it reduces terminological consistency.
- Em dashes are editorial candidates, not automatic errors. Replace only where punctuation or sentence division improves clarity.

## Chapter remediation matrix

| Area | Evidence repair | Method/claim repair | Editorial pass | Human exit gate |
|---|---|---|---|---|
| Abstracts | use one dated 765/762/3/0, 39% baseline | disclose participant/external validation status | remove completed-study tense and generic claims | researcher + advisor approve both languages |
| Chapter 1 | reconcile title, objectives, and measured variables | narrow “player skill” unless a skill measure exists | remove inflated contribution language | advisor accepts construct and scope |
| Chapter 2 | verify every source and corpus inclusion rule | distinguish prior evidence from ClutchG evidence | synthesize by claim/trade-off rather than repository summaries | citation audit has no orphan/mismatch |
| Chapter 3 | retain approved protocol/version and environment | resolve machine-treatment and order confounding, timing, power/model, ethics | edit only after protocol approval | advisor + statistician + ethics determination |
| Chapter 4 | map requirements/design/code to current symbols | distinguish implementation from runtime validation | reduce repeated implementation narration | traceability reviewer signs off |
| Chapter 5 | attach dated logs and skipped-test dispositions | separate automated/historical/external/human classes | replace categorical “all passed” wording where unsupported | evidence owner approves claim matrix |
| Chapter 6 | collect and retain real participant/raw system data | run approved analysis; keep unavailable results marked pending | no prose synthesis before valid analysis | researcher + statistician verify tables |
| Chapter 7 | trace every conclusion to a completed objective/result | state limitations and unresolved gates explicitly | remove universal or causal wording not supported by design | advisor approves conclusion scope |
| Front matter/appendices | synchronize numbers, terms, tables, figures, approvals | preserve historical records as dated evidence | format only after content freeze | final DOCX/PDF visual sign-off |

## Approved next editorial workflow

1. Select and hash one canonical chapter set.
2. Resolve Issue #10 (participant design/statistics/ethics) before participant work or Chapter 3 polishing.
3. Resolve Issue #6 (numeric and safety claims) before revising abstracts, testing, results, or conclusions.
4. Run citation reconciliation against original sources.
5. Apply minimal Thai/English edits with a before/after decision log.
6. Re-run this heuristic only as a diagnostic comparison, not a pass/fail authorship gate.
7. Format DOCX/PDF last and inspect page by page.

## Prohibited actions

- Do not run `--fix-write` on the read-only thesis workspace in this task.
- Do not optimize wording solely to reduce an AI score.
- Do not replace `[TBD]`, `[VERIFY REQUIRED]`, or `[CITATION NEEDED]` with generated content.
- Do not add anecdotes, “personal observations,” or synthetic specificity to make prose appear human.
- Do not describe the scan label as evidence that a chapter is human-authored.
