# Thesis Toolchain Integration Plan

**Date:** 2026-07-30  
**Mode:** planning and controlled use only; `thesis-doc` remains read-only in this repository task

## 1. Verified local capabilities

| Capability | Located artifact | Intended controlled use |
|---|---|---|
| A4 page setup | `thesis-doc/Skill จัดหน้า A4-วิทยานิพนธ์-หนังสือ/page-setup.skill` | Final DOCX/PDF margins, paper size, sections and pagination |
| Academic document formatting | `academic-document.skill`, `thesis-format.skill` in the same directory | CMU-format render and visual QA |
| Thai academic writing | `thesis-doc/.opencode/skills/thai-thesis-writing/SKILL.md` | Researcher-led chapter revision |
| Thai de-AI editing | `thai-de-ai`, `writing-anti-ai`, `deai-fix` skills | Detect and revise generic, repetitive, unsupported prose |
| Thesis quality gate | `thesis-quality-gate`, `peer-review`, `thesis-orchestrator` | Structural and evidence consistency checks |
| ISO/IEC 29110 | `iso29110-docs`, `software-process-iso29110` | Work-product and traceability review |
| Requirements/V&V/PM | `requirements-engineering`, `software-testing-vv`, `project-management-pmbok` | FR mapping, test design and project controls |
| Review agents | `thesis-reviewer.md`, `Tester.md`, `Code-Reviewer.md`, `analyzer.md` | Independent review roles, never evidence generators |

`C:/Users/nextzus/Documents/thesis/thai-thesis-mcp` was named as a desired tool source but no file inventory was found during this run. It is therefore **not recorded as installed or integrated**. Recheck the path before any installation claim.

## 2. Safe integration sequence

1. Freeze one canonical Markdown chapter set and retain source hashes.
2. Run evidence consistency before prose editing; unresolved results remain explicit gaps.
3. Apply Thai de-AI review as an editorial pass, not as an authorship-hiding pass.
4. Researcher accepts/rejects every substantive rewrite and verifies every citation.
5. Run ISO/requirements/traceability checks against exact source and test nodes.
6. Render DOCX using the A4 skills only after canonical content is approved.
7. Render PDF and perform page-by-page human inspection.
8. Retain tool versions, prompts/instructions used, reviewer identity, and deviations.

## 3. Human-in-the-loop controls

- Tools may flag prose, propose wording, compare evidence and automate formatting.
- Tools may not invent participant data, ethics determinations, citations, measurements or sign-off.
- The researcher owns research questions, methodology, acceptance decisions and interpretation.
- Advisor/statistician/ethics authorities own their respective approvals.
- “De-AI” means removing generic or unsupported language and restoring the researcher’s precise voice; it does not mean concealing responsible tool use.

## 4. Installation decision

Do not copy all 174 skill artifacts into this repository. That would duplicate tool code, increase maintenance, and risk unclear licensing/provenance. Use the external skills in place, record exact paths/versions, and promote only small project-specific checklists into `docs/defense-readiness/`.

## 5. Acceptance evidence

- one synchronized chapter source set
- editorial change log with researcher decisions
- citation verification record
- ISO 29110/FR traceability check
- generated DOCX and PDF tied to source hash
- visual A4/Thai typography checklist signed by a human reviewer
