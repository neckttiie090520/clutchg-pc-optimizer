# ClutchG Current Evidence Matrix

**Evidence baseline:** 2026-07-30  
**Purpose:** ใช้เป็นแหล่งอ้างอิงหลักสำหรับการปรับเอกสารวิทยานิพนธ์และเตรียมสอบ  
**Scope:** source และ work products ใน `C:\Users\nextzus\Documents\thesis\bat`  
**Read-only source consulted:** `C:\Users\nextzus\Documents\thesis\thesis-doc`

เอกสารนี้ไม่รับประกันผลสอบและไม่แทนการอนุมัติของอาจารย์ที่ปรึกษา หลักการคือ **กล่าวอ้างเท่าที่หลักฐานรองรับ** และแยกผลอัตโนมัติออกจากผลที่ต้องทดสอบบน Windows จริง

## 1. สถานะหลักฐาน

| สถานะ | ความหมาย | ใช้กล่าวอ้างได้ |
|---|---|---|
| `AUTOMATED_VERIFIED` | ผ่าน unit/integration/static contract และมีผลคำสั่งล่าสุด | ยืนยัน behavior ในขอบเขต mock/static ที่ระบุ |
| `HISTORICAL_VERIFIED` | มีผลทดสอบจริง แต่เป็น source baseline เก่า | ใช้อธิบายประวัติ V&V เท่านั้น |
| `EXTERNAL_VERIFICATION_REQUIRED` | ต้องใช้ Sandbox/VM, hardware, certificate หรือ CI ภายนอก | ยังห้ามกล่าวว่า source ปัจจุบันผ่าน |
| `HUMAN_SIGN_OFF_REQUIRED` | ต้องมีผู้วิจัย/อาจารย์ตรวจและลงนาม | ใช้เป็น draft หรือ supporting evidence เท่านั้น |
| `CONFLICT` | เอกสารหรือค่าหลายแห่งไม่ตรงกัน | ต้องแก้หรืออธิบายก่อนสอบ |

## 2. Current source baseline

| Claim | Status | Current evidence | Defense wording |
|---|---|---|---|
| Python release-equivalent suite ผ่าน | `AUTOMATED_VERIFIED` | รันจาก `clutchg`: 765 collected, 762 passed, 3 skipped, 0 failed, 80.91s | “ชุด unit/integration ที่กำหนดผ่าน 762 tests; 3 tests ถูก skip ตามเงื่อนไข environment” |
| Python total coverage = 39% | `AUTOMATED_VERIFIED` | pytest-cov จาก full suite; `clutchg/src/core/backup_manager.py` 80%, `clutchg/src/core/batch_executor.py` 87% | “39% คือ total measured coverage ไม่ใช่ 70%; โมดูล safety ที่แก้มี 80% และ 87%” |
| Source compiles | `AUTOMATED_VERIFIED` | `python -m compileall clutchg/src -q` exit 0 | ยืนยัน syntax/import compilation เท่านั้น ไม่เท่ากับ runtime validation |
| Patch ไม่มี whitespace error | `AUTOMATED_VERIFIED` | `git diff --check` exit 0; LF→CRLF เป็น warning | ไม่ใช้แทน functional test |
| Product-focused Bug Hunter fixes ผ่าน | `AUTOMATED_VERIFIED` | `.bug-hunter/findings.json`, `.bug-hunter/referee.json`, `.bug-hunter/report.md`; targeted 77/77 | ยืนยัน 4 defects ที่มี regression tests |
| Full repository ถูก audit ทั้งหมด | **ไม่รองรับ** | triage พบ 26,392 scannable files; 26,279 อยู่ใน `research/` ซึ่งเป็น vendored/reference snapshots | “audit เชิงลึกเน้น product trust boundaries; ไม่กล่าวว่าตรวจ third-party snapshots ครบ” |
| Working tree มี immutable release baseline | `HUMAN_SIGN_OFF_REQUIRED` | checkout ปัจจุบันมี modified/untracked files จำนวนมาก | ต้อง review, commit/tag หรือสร้าง archive SHA-256 ก่อนใช้เป็น official evidence |

## 3. Confirmed and fixed defects in the 2026-07-30 pass

| ID | Defect | Fix evidence | Regression evidence | Status |
|---|---|---|---|---|
| BH-2026-01 | Python registry restore ใช้ wildcard และอาจ import ไฟล์แปลกปลอม/รายงาน partial success | `clutchg/src/core/backup_manager.py`: `REGISTRY_BACKUPS`, preflight six files, success only 6/6 | `test_imports_only_fixed_backup_files`, `test_missing_expected_file_fails_before_any_import`, `test_any_failed_import_makes_restore_fail` | Fixed |
| BH-2026-02 | Backup สองรายการในวินาทีเดียวกันใช้ ID/directory ซ้ำ | `_allocate_backup_path()` สร้าง directory แบบ atomic และเติม suffix | `test_same_second_backups_get_unique_ids_and_directories` | Fixed |
| BH-2026-03 | Backup UI ใช้ object truthiness และแสดงสำเร็จแม้ `backup.success=False` | ทั้ง `clutchg/src/gui/views/backup_minimal.py` และ `clutchg/src/gui/views/backup_restore_center.py` ตรวจ `backup and backup.success` | Test selector: `clutchg/tests/unit/test_audit_regressions.py::TestBackupSafetyRegressions::test_backup_views_require_successful_recovery_artifacts` | Fixed |
| BH-2026-04 | `BatchExecutor` สร้างผลลัพธ์ก่อน reader threads drain ทำให้ stdout/stderr ท้ายรายการหาย | `drain_reader_threads()` ก่อนสร้างผลใน success/timeout/error | `test_execute_drains_reader_threads_before_building_result` | Fixed |

หลักฐาน canonical อยู่ใน `.bug-hunter/`; รายงาน Bug Hunter เดิมเดือนมีนาคมถูกแทนด้วยผลรอบปัจจุบันแล้ว

## 4. ISO/IEC 29110 and SDLC evidence map

| SDLC / ISO activity | Work product or evidence | Current assessment | Required action |
|---|---|---|---|
| Requirements | `docs/iso29110-clutchg/02-SRS.md` | มี FR/NFR และ MoSCoW; บาง threshold/count อาจเก่า | ตรวจทุก numeric claim กับ baseline นี้ |
| Design | `docs/iso29110-clutchg/03-SDD.md`, `docs/diagrams/` | layered architecture มีหลักฐาน; line references และ component inventory บางส่วนเก่า | refresh เฉพาะ diagram ที่ใช้ในการสอบ |
| Construction | `clutchg/src`, `src/*.bat` | product source มี regression evidence | freeze reviewed source baseline |
| Integration | `clutchg/tests/integration` | รวมอยู่ใน 762 passed | ระบุว่า mock/host-safe integration ไม่ใช่ privileged VM |
| Verification | unit/integration/static contracts | `AUTOMATED_VERIFIED` | เก็บ raw log, environment และ source hash |
| Validation | Hyper-V/Sandbox, UAT, hardware demo | current source ยังขาด fresh evidence | ทำตาม human checklist และลงนาม |
| Deployment | release workflow + Inno installer | contract tests ผ่าน; real signing ยังไม่ได้รัน | controlled signed tag build + VM smoke test |
| Maintenance | reports 2026-05-29 → remediation → 2026-07-30 | แสดง corrective/preventive maintenance ได้ดี | เก็บ reports เก่าเป็น change history ไม่แก้ทับ |

## 5. External and human gates

| Gate | Existing evidence | Current status | Evidence required to close |
|---|---|---|---|
| Hyper-V batch V&V 20/20 on 2026-04-12 | `docs/iso29110-clutchg/12-Batch-VV-Test-Record.md` | `HISTORICAL_VERIFIED` | ห้ามใช้รับรอง source หลัง remediation โดยตรง |
| Default Windows Sandbox | infrastructure contracts only | `EXTERNAL_VERIFICATION_REQUIRED` | fresh `vv-results` text/JSON + summary; FAIL=0 |
| No-GPU Sandbox | infrastructure contracts only | `EXTERNAL_VERIFICATION_REQUIRED` | fresh evidence + graceful GPU disposition |
| No-network Sandbox | infrastructure contracts only | `EXTERNAL_VERIFICATION_REQUIRED` | fresh evidence + graceful network disposition |
| Apply → verify → rollback | static transaction contracts | `EXTERNAL_VERIFICATION_REQUIRED` | before/after state, backup ID, journal, rollback comparison |
| Signed release | CI contracts pass | `EXTERNAL_VERIFICATION_REQUIRED` | CI URL, exact tag/version parity, SHA-256, valid Authenticode subject |
| Installer upgrade/relaunch | updater unit tests | `EXTERNAL_VERIFICATION_REQUIRED` | disposable-VM transcript and post-upgrade version |
| UAT/demo usability | no current signed record | `HUMAN_SIGN_OFF_REQUIRED` | participant, scenario, result, issues, signature/date |
| Thesis content and formatting | source read-only audit | `HUMAN_SIGN_OFF_REQUIRED` | researcher applies edits; advisor reviews final PDF |

## 6. Claims requiring normalization

1. **Coverage:** current measured total is 39%. Any `>=70%` or `>=85%` statement must specify a different metric with reproducible calculation, or be changed to a target/gap—not a result.
2. **Test counts:** use command, date, scope and result together. Current baseline is 765 collected / 762 passed / 3 skipped / 0 failed in 80.91s for the release-equivalent suite.
3. **Repository corpus:** define “primary repositories” separately from supporting documents/snapshots; do not alternate between 23 and 28 without definition.
4. **Tweak count:** use active registry-derived count and mark older numbers as historical.
5. **Performance gains:** do not state FPS/latency percentages as general results without hardware, workload, repetitions, raw data and uncertainty.
6. **VM evidence:** 20/20 historical Hyper-V results and current-source Sandbox revalidation are different evidence sets.
7. **AI assistance:** disclose tool-assisted search, test generation and review; retain researcher ownership of requirements, acceptance, privileged execution and final interpretation.

## 7. Responsible AI / human-in-the-loop statement

Suggested wording for methodology or acknowledgements:

> ผู้วิจัยใช้เครื่องมือ AI-assisted software engineering เพื่อช่วยค้นหาโค้ดที่เกี่ยวข้อง เสนอกรณีทดสอบ ตรวจความสอดคล้อง และจัดโครงร่างเอกสาร การตัดสินใจด้าน requirement, safety policy, acceptance criteria, การรันคำสั่งที่มีสิทธิ์สูง และการรับรองผลยังอยู่ภายใต้การตรวจและอนุมัติของผู้วิจัย ผลจากเครื่องมือไม่ถูกนับเป็นหลักฐานจนกว่าจะตรวจสอบกับ source, test output หรือผลการทดลองที่เก็บย้อนกลับได้

สิ่งที่ต้องไม่กล่าว: “AI พิสูจน์ว่าระบบถูกต้องทั้งหมด”, “สอบผ่าน 100%”, หรือ “ผ่าน VM แล้ว” หากยังไม่มี fresh artifacts

## 8. Source-of-truth order for thesis updates

1. Raw command/runtime artifacts tied to source hash
2. `.bug-hunter/findings.json` and current test logs
3. Current source and regression tests
4. Current ISO work products
5. Historical audit/remediation reports
6. Narrative claims in README, slides or thesis chapters

เมื่อข้อมูลขัดกัน ให้ใช้ลำดับนี้และเปิด gap แทนการเลือกตัวเลขที่ดูดีที่สุด
