# Read-only Thesis Audit Appendix — 2026-07-30

**Audited source (read-only):** `C:\Users\nextzus\Documents\thesis\thesis-doc`  
**Repository evidence baseline:** 765 collected, 762 passed, 3 skipped, 0 failed; total Python coverage 39%  
**Boundary:** This appendix records observations and required actions. No file under `thesis-doc` was modified.

## 1. Disposition

The software repository has a current automated baseline, but the thesis package is **not yet suitable for a final-submission claim**. The remaining blockers are primarily research-method, human-subject, document-integration, external V&V, and final-formatting work. They cannot be closed by generating prose or additional mocked tests.

Use these evidence classes consistently:

- `AUTOMATED_VERIFIED`: current unit/integration/static-contract evidence only.
- `HISTORICAL_VERIFIED`: evidence valid for an earlier identified baseline.
- `EXTERNAL_VERIFICATION_REQUIRED`: privileged Windows, hardware, certificate, or release execution still required.
- `HUMAN_SIGN_OFF_REQUIRED`: researcher, participant, statistician, advisor, ethics authority, or document reviewer must act.

## 2. Source inventory and canonical-source problem

| Area | Observation | Disposition |
|---|---|---|
| Root chapter Markdown | `thesis-doc/output/*.md` is declared canonical by `.opencode/skills/thesis-ops-standard/SKILL.md` and `build-combined.ps1`. | Treat as intended canonical source, not yet synchronized. |
| Organized chapter mirror | `thesis-doc/output/chapters/` contains newer Chapter 3, 6, and 7 edits, while root Chapter 1, 2, 4, and 5 have later edits. | `HUMAN_SIGN_OFF_REQUIRED`: perform a chapter-by-chapter merge; do not overwrite by timestamp alone. |
| `chapters v2` | Contains the superseded four-condition Baseline/SAFE/COMPETITIVE/EXTREME design. | Archive/label historical; exclude from current defense build. |
| Current combined DOCX | `output/chapters/combined/thesis-final.docx` predates later source edits, contains stale test evidence and 254 `[TBD]` occurrences. | Not a final artifact. Regenerate only after source reconciliation. |
| Current PDF | `output/thesis-clutchg-preview.pdf` is a short April preview with TBD text. | Not a final-submission PDF. |
| Knowledge base | `thesis-doc/knowledge-base` is correctly treated as read-only reference material. | Do not cite external theses or AI reports as ClutchG experimental evidence. |
| Improvement plans | `improval_plan_suggestion/last_improval_plan_spec_tasks/README.md` points to a master plan. | Use for change history and backlog, not current test evidence. |

Because `thesis-doc` is not a Git repository, freeze its final source with a dated file-hash manifest (SHA-256), file list, and reviewer identity rather than relying on Git history.

## 3. P0 defense blockers

### P0-01 — Participant experiment and Objective 3 are incomplete

Evidence:

- `output/chapters/ch06/chapter6.md:202-206` says real participant data have not been collected.
- Tables beginning around lines 216, 234, 252, 274, 282, 300, and 308 contain unresolved `[TBD]` cells.
- Thai/English abstracts and Chapter 7 begin with completed-study language despite later admitting collection is pending.

Required action: the researcher must complete approved participant work, retain consent/raw logs, analyze the data, and have the interpretation reviewed. Until then, conclusions must be limited to software development and automated verification; do not claim improved player skill or participant outcomes.

### P0-02 — Current evidence baseline is not propagated

Current defensible statement:

```text
765 collected
762 passed
3 skipped
0 failed
39% total Python coverage
```

Conflicting current-draft locations include:

- `output/chapters/ch06/chapter6.md` — 576 passed, zero skipped, 34%.
- `output/chapters/front-matter/abstract-thai.md` and `abstract-english.md` — 576/34% plus older performance-run counts.
- `output/chapters/ch07/chapter7.md` and `ch04/chapter4.md` — stale counts.
- `output/chapters/combined/thesis-final.docx` — stale 576/34% evidence.

Required action: after canonical-source reconciliation, update every current chapter, abstract, table, figure, and final output from one retained test log. Historical counts (474, 484, 477/64, 496, 576) must be explicitly dated and labeled historical or removed from the defense package.

### P0-03 — Machine identity is confounded with treatment

`output/chapters/ch03/chapter3.md` permanently assigns Machine A as Based and Machine B as Optimized. Counterbalancing participant order does not separate the optimization effect from machine-specific firmware, silicon, cooling, storage, driver, or background-state differences.

Required advisor/statistician decision:

1. Use a within-machine reversible design (baseline and optimized state on each machine, restored between conditions), or
2. Cross the treatment across both machines with controlled reimaging/state restoration, or
3. Narrow the causal claim to a comparison of the two configured systems and state machine confounding as a major limitation.

Do not describe the current arrangement as isolating the ClutchG treatment effect.

### P0-04 — Human-research determination is not documented

Chapter 3 states that formal human-research review is unnecessary while the study recruits participants, records consent and health/safety information, and may reimburse travel. An informal or historical advisor statement is not institutional evidence.

Required action: obtain written determination from the advisor/program/CMU ethics authority (approval, exemption, or documented non-review) before participant collection or final reporting. Retain the letter/reference number and approved consent materials.

### P0-05 — No current submission artifact

The latest combined DOCX predates later Markdown edits and contains 254 TBD markers; no current full PDF exists for page-level verification.

Required action: reconcile canonical sources, clear all intentional placeholders, regenerate DOCX/PDF, then perform human visual review of margins, page numbers, approval pages, table breaks, figures, fonts, Thai line wrapping, searchable text, and copy/paste behavior.

### P0-06 — Privileged and release evidence is overstated in thesis prose

Historical Hyper-V V&V (20/20 on 2026-04-12) is evidence for that baseline only. Current-source Sandbox/admin execution and real code-signing/release verification remain external gates.

Required wording: separate automated contracts, historical V&V, current-source privileged revalidation, and signed-release verification. Do not merge manual/security checks into pytest totals.

## 4. P1 methodology and consistency corrections

| ID | Gap | Evidence / action |
|---|---|---|
| P1-01 | Counterbalanced vs fixed A–B contradiction | `ch03` and `ch06` specify counterbalancing; `ch07` says fixed A–B. Select one actual procedure and align all chapters. |
| P1-02 | Difficulty-order confounding | Easy→Medium→Hard is fixed for every run. Randomize/counterbalance, or explicitly treat warm-up/fatigue as a limitation. |
| P1-03 | Session arithmetic | One-hour participant protocol conflicts with 40-minute pair blocks and five-hour total. Recalculate setup, run, rest, questionnaire, and reset time. |
| P1-04 | Statistical fallback | A basic Friedman test does not estimate Machine × Difficulty interaction. Predefine an interaction-capable robust/nonparametric alternative with a statistician. |
| P1-05 | Power analysis | The assumed effect size and simplified n=8 calculation do not establish interaction power. Recalculate and document assumptions/sensitivity. |
| P1-06 | Construct/title mismatch | Titles claim player “skill,” but outcomes are frametime, DPC/ISR latency, resource use, and satisfaction. Change to system/game performance or add a valid skill measure. |
| P1-07 | Canonical corpus cleanup | Label `chapters v2`, old combined documents, and old readiness reports as historical; exclude them from build/search inputs. |
| P1-08 | Manual evidence detail | Add date, exact hardware/GPU/driver/OS, source hash, raw logs, operator, expected/actual result, and disposition. |
| P1-09 | Document type | Confirm with program/advisor whether the official term is Independent Study or thesis; align cover, approval, abstracts, and metadata. |

## 5. P2 final-package work

1. Complete biography, graduation year, researcher contact, committee, and administrative fields.
2. Replace the ten Appendix F screenshot placeholders with current, captioned evidence.
3. Regenerate TOC, list of tables, and list of figures after final pagination.
4. Remove Word lock/temp files from the submission package.
5. Recheck Thai ZWSP line breaking and font embedding in final PDF.
6. Standardize the Thai author-name spelling across all artifacts.
7. Correct stale four-condition entries in list-of-tables and missing/jumped figure numbering.

## 6. Formatting/output observations

- `thesis-final.docx` is the most advanced full DOCX but is not current/final.
- Older `thesis-complete.docx` and `thesis-combined.docx` still contain the superseded four-condition design.
- `front-matter/toc.md` contains page placeholders and omits a current Chapter 7 section.
- `list-of-tables.md` describes the old four-condition design.
- `list-of-figures.md` lacks page numbers and has numbering gaps.
- `appendix-f.md` contains screenshot placeholders despite completion wording.

These are human document-production findings, not software defects.

## 7. Ownership matrix

| Owner | Required work | Exit evidence |
|---|---|---|
| Researcher | Participant collection, consent, raw CapFrameX/LatencyMon/resource logs, environment records, data cleaning | De-identified dataset, data dictionary, raw-log manifest, signed collection record |
| Researcher + advisor | Title/construct decision; actual experimental procedure; limitation wording | Approved chapter changes and meeting record |
| Ethics authority/advisor/program | Human-research determination | Written approval/exemption/non-review record |
| Statistician/advisor | Power, interaction model, assumptions, fallback, multiplicity, CI/effect-size plan | Reviewed statistical analysis plan |
| External VM operator | Current-source default/no-GPU/no-network and apply→rollback runs | Timestamped machine-readable artifacts, source hash, operator/reviewer disposition |
| Release owner | Controlled signed build and installer upgrade/relaunch | CI URL, tag/version parity, hashes, Authenticode output, VM transcript |
| Program secretary/advisor | Official document type/template/approval/front matter | Written confirmation and approved template |
| Human document reviewer | Page-by-page final DOCX/PDF inspection | Signed checklist with issues closed |

## 8. Recommended evidence wording

### Automated baseline

> สถานะหลักฐานการทดสอบ ณ วันที่ 2026-07-30 สำหรับ working tree ที่ระบุในบันทึกการทดสอบ: ชุดทดสอบอัตโนมัติรวบรวมได้ 765 รายการ ผ่าน 762 รายการ ข้าม 3 รายการ และไม่พบรายการล้มเหลว ความครอบคลุมซอร์สโค้ด Python รวมเท่ากับร้อยละ 39 รายการที่ข้ามไม่ถือว่าเป็นรายการผ่าน ผลนี้ไม่รวมการทดสอบที่ต้องใช้สิทธิ์ Administrator ใน Sandbox ภายนอกหรือการตรวจสอบลายเซ็นซอฟต์แวร์จริง

### Participant status before collection is complete

> ตารางผลการทดลองกับผู้เข้าร่วมเป็นโครงสร้างสำหรับบันทึกผลและยังไม่ถือเป็นผลการวิจัยจนกว่าจะเก็บข้อมูลครบ ตรวจสอบคุณภาพ วิเคราะห์ตามแผน และได้รับการทวนสอบจากผู้วิจัยกับอาจารย์ที่ปรึกษา ในระหว่างนี้ งานวิจัยสรุปได้เฉพาะผลการพัฒนาและการทดสอบซอฟต์แวร์ที่มีหลักฐานแนบ และยังไม่สรุปว่า ClutchG เพิ่มทักษะหรือประสิทธิภาพของผู้เล่นเกม

## 9. Required closure sequence

1. Obtain ethics determination and advisor decisions on construct/design.
2. Reconcile canonical chapter sources; archive stale mirrors.
3. Correct methodology before participant collection.
4. Freeze software and thesis-source baselines with hashes.
5. Execute current-source external V&V and retain artifacts.
6. Collect participant data and run the approved analysis.
7. Replace all TBD/stale claims from retained evidence only.
8. Regenerate DOCX/PDF and complete visual/administrative review.
9. Rehearse answers using `docs/defense-readiness/02-defense-question-bank-2026-07-30.md`.
10. Obtain advisor sign-off; no checklist or automated tool guarantees the committee outcome.
