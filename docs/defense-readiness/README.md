# ClutchG Defense Readiness Pack

**Current evidence date:** 2026-08-06 (เอกสารหมายเลข 13–15; หมายเลข 01–12 ที่ลงวันที่ 2026-07-30 เป็น snapshot ของรอบนั้น อ่านเป็น historical change evidence)  
**Purpose:** ชุดอ้างอิงสำหรับเตรียมสอบที่แยกข้อเท็จจริงที่ตรวจอัตโนมัติ หลักฐานภายนอก และงานที่ผู้วิจัยต้องลงนามเอง

## เอกสารในชุด

1. [Current Evidence Matrix](01-current-evidence-matrix-2026-07-30.md) — claim → evidence → status → allowed wording
2. [Defense Question Bank](02-defense-question-bank-2026-07-30.md) — คำถามที่คาดว่าจะพบและคำตอบตามหลักฐาน
3. [Human Validation Checklist](03-human-validation-checklist-2026-07-30.md) — งาน VM, signed release, UAT, thesis review และ advisor sign-off
4. [GitHub Project Backlog Draft](04-github-project-backlog-draft-2026-07-30.md) — planning history ก่อน publish; ใช้ runbook หมายเลข 10 เป็นสถานะปัจจุบัน
5. [ISO 29110 Current Evidence Addendum](../iso29110-clutchg/13-Current-Evidence-Addendum-2026-07-30.md) — baseline ปัจจุบันและขอบเขตคำกล่าวอ้างที่อนุญาต
6. [Read-only Thesis Audit Appendix](05-read-only-thesis-audit-appendix-2026-07-30.md) — P0/P1/P2 gaps จาก `thesis-doc` พร้อม human owners โดยไม่มีการแก้ต้นฉบับ
7. [Evidence Manifest](06-evidence-manifest-2026-07-30.json) — SHA-256 และขนาดของ current defense artifacts
8. [Thesis Toolchain Integration Plan](07-thesis-toolchain-integration-plan-2026-07-30.md) — การใช้ A4, thesis review, ISO และ de-AI tools แบบควบคุม
9. [Editorial and De-AI Protocol](08-de-ai-editorial-protocol-2026-07-30.md) — evidence-first editing และ human acceptance
10. [GitHub SDLC/ISO 29110 Governance](09-github-sdlc-governance-2026-07-30.md) — milestone, Issues #5–#11, PR #12 และ Project setup gate
11. [De-AI Scan Report](10-de-ai-scan-report-2026-07-30.md) — scan-only findings ของ canonical root chapters; raw diagnostics อยู่ที่ `10-de-ai-scan-raw-2026-07-30.json`
12. [Human Action Register](11-human-action-register-2026-07-30.md) — H-01…H-21 พร้อม owner, prerequisite, exit evidence และลำดับปิดงาน
13. [Audit Handoff Record](12-audit-handoff-2026-08-05.md) — สิ่งที่ audit รอบนี้พิสูจน์ได้จริง, security correction, recovery reachability และงานที่เหลือของมนุษย์
14. [Regression and Validation Report](13-regression-validation-report-2026-08-06.md) — closing validation pass, coverage สองสโคป, targeted re-scan, read-only runtime V&V และ residual risk register R-01…R-09
15. [Evidence Manifest (current)](14-evidence-manifest-2026-08-06.json) — SHA-256 ของ artifact ปัจจุบันพร้อม revision, ตัวเลข validation และ residual risks แบบ machine-readable; สร้างใหม่ด้วย `python docs/defense-readiness/build-evidence-manifest.py`

## Source-of-truth order

เมื่อเอกสารขัดกัน ให้ใช้ลำดับนี้:

1. raw command output ที่ระบุวันที่ environment และ source revision/hash
2. source code และ regression tests ปัจจุบัน
3. `.bug-hunter/findings.json`, `.bug-hunter/skeptic.json`, `.bug-hunter/referee.json` และ `.bug-hunter/report.md` ของรอบ 2026-07-30
4. ISO/IEC 29110 work products ที่ปรับฐานหลักฐานแล้ว
5. เอกสาร audit เก่า ใช้เป็น historical change evidence เท่านั้น

ผลล่าสุดที่ใช้ในชุดนี้คือ revision `8359915` วันที่ 2026-08-06: **unit 1055 passed, integration 23 passed, combined 1078 passed, 0 failed; core-layer coverage 81% (target ≥70%), repository-wide 40%** — ดูรายละเอียดและวิธี reproduce ที่เอกสารหมายเลข 14. ตัวเลข **765 collected / 39%** ของ 2026-07-30 เป็น baseline เก่า ห้ามอ้างเป็นผลปัจจุบัน. ผล Hyper-V 20/20 วันที่ 2026-04-12 เป็น historical V&V และไม่ใช้แทน current-source Sandbox revalidation

## Status vocabulary

- `AUTOMATED_VERIFIED` — มี unit/integration/static-contract evidence ปัจจุบัน
- `HISTORICAL_VERIFIED` — เคยตรวจผ่านกับ baseline ก่อนหน้า แต่ต้อง revalidate สำหรับ source ปัจจุบัน
- `EXTERNAL_VERIFICATION_REQUIRED` — ต้องใช้ disposable VM, hardware, certificate หรือ CI credential
- `HUMAN_SIGN_OFF_REQUIRED` — ต้องมีผู้วิจัย ผู้ใช้ หรืออาจารย์ตรวจและลงนาม

## Usage before defense

1. Freeze source revision หรือ archive SHA-256
2. ทำรายการ human/external gates ในเอกสารหมายเลข 3
3. อัปเดต matrix เฉพาะจาก retained evidence ใหม่
4. ซ้อมตอบตาม question bank โดยไม่ขยาย claim เกิน matrix
5. ให้ผู้วิจัยและอาจารย์ตรวจ final thesis/PDF; เอกสารชุดนี้ไม่รับประกันผลสอบ

## Scope boundary

- `C:\Users\nextzus\Documents\thesis\thesis-doc` ถูก audit แบบ read-only; ไม่มีไฟล์ต้นฉบับถูกแก้ในงานนี้
- `research/` เป็น reference/vendor corpus และไม่ถูกนับเป็น product deep-scan coverage
- GitHub milestone `Defense Readiness 2026`, Issues #5–#11 และ PR #12 ถูก publish แล้ว; PR ยังเปิดและ mergeable โดย repository ไม่รายงาน CI checks สำหรับ branch นี้
- GitHub Project ยังไม่ถูกสร้าง เพราะ active token ขาด `project` scope; ใช้ `.github/tools/setup_github_project.py` แบบ dry-run-first หลัง human OAuth authorization
- การ merge PR, การปิด Issues และการให้ Project scope เป็น outward-facing/human-authorized actions แยกจากการจัดทำหลักฐานนี้
