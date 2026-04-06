# 07 — คำขอเปลี่ยนแปลง (Software Change Request)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2:2011 — PM.O3, Table 23
> **เวอร์ชันเอกสาร:** v2.1
> **ETVX:** Entry = Change identified + Impact assessed; Task = Analyze, approve, implement, verify; Verification = Regression tests pass; Exit = CR closed + Traceability updated
> **อ้างอิง SE:** SE 702 (Configuration Management — Change Control), SE 721 (Requirements Management — Change Control process)
> **Cross-ref:** SRS v3.1 (`02-SRS.md`), SDD v3.2 (`03-SDD.md`), Traceability v2.0 (`06-Traceability-Record.md`)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **วันที่อัปเดตล่าสุด:** 2026-04-06

---

## กระบวนการควบคุมการเปลี่ยนแปลง (Change Control Process)

### Change Control Board (CCB)

ตามแนวปฏิบัติ Configuration Management (SE 702) การเปลี่ยนแปลงทุกรายการต้องผ่านกระบวนการควบคุมโดย Change Control Board (CCB) ซึ่งทำหน้าที่ประเมินผลกระทบและอนุมัติ/ปฏิเสธคำขอเปลี่ยนแปลง

**องค์ประกอบ CCB ของโครงงาน ClutchG:**

| บทบาท | ผู้รับผิดชอบ | หน้าที่ |
|--------|-------------|---------|
| ประธาน CCB | อาจารย์ที่ปรึกษา | อนุมัติ/ปฏิเสธ CR ระดับ HIGH |
| สมาชิก CCB / ผู้ดำเนินการ | nextzus (นักศึกษา) | วิเคราะห์ผลกระทบ, เสนอ CR, ดำเนินการแก้ไข |

> **หมายเหตุ:** เนื่องจากเป็นโครงงานวิทยานิพนธ์ขนาดเล็ก (VSE profile) CCB จึงมีเพียง 2 คน โดย CR ระดับ LOW/MEDIUM นักศึกษาสามารถอนุมัติและดำเนินการได้เอง ส่วน CR ระดับ HIGH ต้องได้รับความเห็นชอบจากอาจารย์ที่ปรึกษาก่อนดำเนินการ

### ขั้นตอนการควบคุมการเปลี่ยนแปลง (ISO 29110 — PM.2.2, PM.2.3, PM.3.3)

```
ระบุการเปลี่ยนแปลง → วิเคราะห์ผลกระทบ → เสนอ CCB → อนุมัติ/ปฏิเสธ → ดำเนินการ → ทดสอบ Regression → ปิด CR
     (PM.O3)          (PM.2.2)        (PM.2.3)    (PM.2.3)     (SI.5)      (SI.4/SI.5)    (PM.3.3)
```

| ขั้นตอน | กิจกรรม | ผลลัพธ์ |
|---------|---------|---------|
| 1. ระบุ | บันทึกคำขอเปลี่ยนแปลงลงใน CR Form | CR document พร้อม ID |
| 2. วิเคราะห์ | ประเมินผลกระทบทางเทคนิค, กำหนดการ, ต้นทุน, เอกสาร | Impact Analysis (§9 ของแต่ละ CR) |
| 3. อนุมัติ | CCB พิจารณาอนุมัติ — LOW/MED: นักศึกษา, HIGH: อาจารย์ | Acceptance status |
| 4. ดำเนินการ | แก้ไขโค้ดตาม CR, อัปเดตเอกสารที่เกี่ยวข้อง | Modified source + docs |
| 5. ทดสอบ | Run regression tests ให้ผ่านทั้งหมด | Test results (05-Test-Record.md) |
| 6. ปิด | บันทึกสถานะ closed, อัปเดต Traceability | CR closed + Traceability updated |

---

## สรุป Change Request ทั้งหมด

| CR No. | ชื่อการเปลี่ยนแปลง | วันที่ขอ | ระดับความสำคัญ | สถานะ |
|--------|-------------------|---------|---------------|-------|
| CR-001 | Unified Backup & Restore Center | 2025-08-15 | MEDIUM | Closed |
| CR-002 | Export/Import Presets | 2025-10-01 | LOW | Closed |
| CR-003 | Multi-Theme System | 2026-01-20 | LOW | Closed |
| CR-004 | Security Audit & Test Expansion | 2026-03-12 | HIGH | Closed |

---

## CR-001 — Unified Backup & Restore Center

### 1. ข้อมูลคำขอ (Request Information)

| รายการ | รายละเอียด |
|--------|-----------|
| **CR Number** | CR-001 |
| **Project** | ClutchG PC Optimizer v2.0 |
| **Change Name** | เปลี่ยนจาก Legacy Backup View เป็น Unified Backup & Restore Center |
| **Date of Request** | 2025-08-15 |
| **Date Needed** | 2025-09-30 (สิ้นสุด Phase 9) |
| **Criticality** | MEDIUM |
| **Request Status** | `[closed]` |

### 2. ข้อมูลผู้ขอ (Requester Contact Information)

| รายการ | รายละเอียด |
|--------|-----------|
| **Requested by** | nextzus |
| **Role** | นักศึกษา / Developer |
| **Contact** | GitHub: nextzus |

### 3. วัตถุประสงค์ของการเปลี่ยนแปลง (Purpose of Change)

ปรับปรุง UX ของระบบ Backup & Restore โดยรวม backup, restore, และ rollback ไว้ในหน้าเดียว พร้อม timeline visualization เพื่อลดความซับซ้อนในการใช้งานของผู้ใช้ทั่วไป

### 4. คำอธิบายการเปลี่ยนแปลง (Description of Change)

แทนที่ `backup_minimal.py` (backup view แบบเดิม) ด้วย `backup_restore_center.py` ที่รวม backup, restore, และ rollback ไว้ในหน้าเดียว พร้อม timeline visualization แสดงประวัติ operations ทั้งหมด รองรับ per-tweak rollback (undo ทีละรายการ)

### 5. เหตุผลของการเปลี่ยนแปลง (Reason for Change)

- UI เดิมแยก backup กับ restore เป็นคนละหน้า ทำให้ใช้งานยาก
- ต้องการ timeline แสดงประวัติ operations ทั้งหมด
- ต้องการ per-tweak rollback (undo ทีละรายการ แทนทั้ง session)

### 6. ระบบที่ได้รับผลกระทบ (Impacted System(s))

| ระบบ | ผลกระทบ |
|------|---------|
| GUI Layer — Backup View (`backup_minimal.py`) | แทนที่ด้วย view ใหม่ |
| GUI Layer — App Router (`app_minimal.py`) | ต้องอัปเดต routing |
| Core Layer — Backup Manager (`backup_manager.py`) | ไม่กระทบโดยตรง |

### 7. ผลต่อการทำงานของระบบปัจจุบัน (Impact to Operations of Existing System(s))

- ผู้ใช้ที่เคยใช้ backup flow เดิมจะพบ UI ใหม่ที่รวมทุกอย่างไว้ในที่เดียว
- Legacy view (`backup_minimal.py`) ยังคงอยู่ในโค้ดแต่ไม่ได้ route ไปแล้ว — ไม่มี breaking change
- Backup data เดิมทั้งหมดยังคงใช้งานได้ตามปกติ

### 8. ผลต่อเอกสารที่เกี่ยวข้อง (Impact to Associated Documentation)

| เอกสาร | ผลกระทบ |
|--------|---------|
| SRS | เพิ่ม/อัปเดต FR ที่เกี่ยวกับ backup UI |
| SDD | อัปเดต component diagram — backup_restore_center |
| Test Plan | เพิ่ม test cases สำหรับ timeline view |

### 9. การวิเคราะห์ผลกระทบ (Impact Analysis — PM.2.2)

| มิติ | การประเมิน |
|------|-----------|
| **ผลกระทบทางเทคนิค** | ต่ำ — เป็น UI layer เท่านั้น, core logic ไม่เปลี่ยน |
| **ผลกระทบต่อกำหนดการ** | ไม่กระทบ — เป็น Phase 9 ตามแผน |
| **ผลกระทบต่อต้นทุน** | ไม่มี — งานทั้งหมดอยู่ใน scope เดิม |

### 10. การอนุมัติ (Acceptance — PM.2.3)

| รายการ | รายละเอียด |
|--------|-----------|
| **ผู้อนุมัติ** | nextzus |
| **บทบาท** | Project Owner / Lead Developer |
| **วันที่อนุมัติ** | 2025-08-15 |
| **สถานะการอนุมัติ** | `[accepted]` |

### 11. การปิด CR (Closure — PM.3.3)

| รายการ | รายละเอียด |
|--------|-----------|
| **วันที่ปิด** | 2025-09-30 |
| **สถานะการปิด** | `[closed]` — Implemented ใน Phase 9 |
| **หมายเหตุ** | `backup_restore_center.py` เสร็จสมบูรณ์และรวมเข้า main app แล้ว |

---

## CR-002 — Export/Import Presets

### 1. ข้อมูลคำขอ (Request Information)

| รายการ | รายละเอียด |
|--------|-----------|
| **CR Number** | CR-002 |
| **Project** | ClutchG PC Optimizer v2.0 |
| **Change Name** | เพิ่มระบบ Export/Import Presets |
| **Date of Request** | 2025-10-01 |
| **Date Needed** | 2025-11-30 (สิ้นสุด Phase 10) |
| **Criticality** | LOW |
| **Request Status** | `[closed]` |

### 2. ข้อมูลผู้ขอ (Requester Contact Information)

| รายการ | รายละเอียด |
|--------|-----------|
| **Requested by** | nextzus |
| **Role** | นักศึกษา / Developer |
| **Contact** | GitHub: nextzus |

### 3. วัตถุประสงค์ของการเปลี่ยนแปลง (Purpose of Change)

เพิ่ม feature ให้ผู้ใช้สามารถแชร์ preset configurations กันได้โดยการ export/import JSON file เพื่อเพิ่ม flexibility และ community sharing

### 4. คำอธิบายการเปลี่ยนแปลง (Description of Change)

เพิ่มความสามารถ export custom presets เป็น JSON file และ import กลับเข้ามา เพื่อให้ผู้ใช้แชร์ presets กันได้ ใช้ standard JSON format ที่อ่านได้ง่าย

### 5. เหตุผลของการเปลี่ยนแปลง (Reason for Change)

- ผู้ใช้ต้องการแชร์ preset configurations กัน
- เพิ่ม flexibility ในการจัดการ custom presets
- รองรับ use case backup/restore presets ข้าม machine

### 6. ระบบที่ได้รับผลกระทบ (Impacted System(s))

| ระบบ | ผลกระทบ |
|------|---------|
| Core Layer — Profile Manager (`profile_manager.py`) | เพิ่ม 2 methods ใหม่ |
| SRS Document | เพิ่ม functional requirement FR-PM-06 |

### 7. ผลต่อการทำงานของระบบปัจจุบัน (Impact to Operations of Existing System(s))

- ไม่กระทบ existing preset management workflow
- เพิ่มเป็น additive feature — ไม่มี breaking change
- Import จาก external file อาจ trigger validation ก่อน apply

### 8. ผลต่อเอกสารที่เกี่ยวข้อง (Impact to Associated Documentation)

| เอกสาร | ผลกระทบ |
|--------|---------|
| SRS | เพิ่ม FR-PM-06: Export/Import Presets |
| SDD | อัปเดต ProfileManager class description |

### 9. การวิเคราะห์ผลกระทบ (Impact Analysis — PM.2.2)

| มิติ | การประเมิน |
|------|-----------|
| **ผลกระทบทางเทคนิค** | ต่ำ — เพิ่ม 2 methods ใน `profile_manager.py` เท่านั้น |
| **ผลกระทบต่อกำหนดการ** | ไม่กระทบ — อยู่ใน Phase 10 ตามแผน |
| **ผลกระทบต่อต้นทุน** | ไม่มี — งานอยู่ใน scope เดิม |

### 10. การอนุมัติ (Acceptance — PM.2.3)

| รายการ | รายละเอียด |
|--------|-----------|
| **ผู้อนุมัติ** | nextzus |
| **บทบาท** | Project Owner / Lead Developer |
| **วันที่อนุมัติ** | 2025-10-01 |
| **สถานะการอนุมัติ** | `[accepted]` |

### 11. การปิด CR (Closure — PM.3.3)

| รายการ | รายละเอียด |
|--------|-----------|
| **วันที่ปิด** | 2025-11-30 |
| **สถานะการปิด** | `[closed]` — Implemented ใน Phase 10 |
| **หมายเหตุ** | `export_preset_to_file()` และ `import_preset_from_file()` เสร็จสมบูรณ์ |

---

## CR-003 — Multi-Theme System (Dark/Light + Accent Colors)

### 1. ข้อมูลคำขอ (Request Information)

| รายการ | รายละเอียด |
|--------|-----------|
| **CR Number** | CR-003 |
| **Project** | ClutchG PC Optimizer v2.0 |
| **Change Name** | เพิ่ม Multi-Theme System (Dark/Light + Accent Colors) |
| **Date of Request** | 2026-01-20 |
| **Date Needed** | 2026-02-28 (สิ้นสุด Phase 10) |
| **Criticality** | LOW |
| **Request Status** | `[closed]` |

### 2. ข้อมูลผู้ขอ (Requester Contact Information)

| รายการ | รายละเอียด |
|--------|-----------|
| **Requested by** | nextzus |
| **Role** | นักศึกษา / Developer |
| **Contact** | GitHub: nextzus |

### 3. วัตถุประสงค์ของการเปลี่ยนแปลง (Purpose of Change)

เพิ่ม UI customization และ accessibility โดยรองรับ dark/light mode พร้อม accent colors หลากหลาย เพื่อให้ผู้ใช้ปรับ UI ตามความต้องการและสภาพแวดล้อม

### 4. คำอธิบายการเปลี่ยนแปลง (Description of Change)

เปลี่ยนจาก single dark theme เป็น multi-theme system ที่รองรับ dark/light mode และ accent colors (cyan, purple, green, orange, pink) โดยใช้ ThemeManager class ใหม่ใน `theme.py`

### 5. เหตุผลของการเปลี่ยนแปลง (Reason for Change)

- ผู้ใช้ต้องการ UI customization
- รองรับ accessibility (light mode สำหรับการใช้งานในที่สว่าง)
- เพิ่ม visual appeal และ brand identity

### 6. ระบบที่ได้รับผลกระทบ (Impacted System(s))

| ระบบ | ผลกระทบ |
|------|---------|
| GUI Layer — Theme System (`theme.py`) | Refactor เป็น ThemeManager class |
| GUI Layer — Settings View (`settings_minimal.py`) | เพิ่มหน้า Settings ใหม่ |
| SRS Document | เพิ่ม FR-UI-06 |

### 7. ผลต่อการทำงานของระบบปัจจุบัน (Impact to Operations of Existing System(s))

- Default theme ยังคงเป็น dark mode — ไม่กระทบ existing users
- Views ทั้งหมดต้องอ่าน theme จาก ThemeManager แทน hardcoded colors
- การเปลี่ยน theme จะ apply ทันที (live reload) ไม่ต้อง restart app

### 8. ผลต่อเอกสารที่เกี่ยวข้อง (Impact to Associated Documentation)

| เอกสาร | ผลกระทบ |
|--------|---------|
| SRS | เพิ่ม FR-UI-06: Multi-Theme Support |
| SDD | อัปเดต ThemeManager class, เพิ่ม Settings view component |

### 9. การวิเคราะห์ผลกระทบ (Impact Analysis — PM.2.2)

| มิติ | การประเมิน |
|------|-----------|
| **ผลกระทบทางเทคนิค** | ปานกลาง — ต้องอัปเดต color references ใน views ทั้งหมด |
| **ผลกระทบต่อกำหนดการ** | ไม่กระทบ — อยู่ใน Phase 10 ตามแผน |
| **ผลกระทบต่อต้นทุน** | ไม่มี — งานอยู่ใน scope เดิม |

### 10. การอนุมัติ (Acceptance — PM.2.3)

| รายการ | รายละเอียด |
|--------|-----------|
| **ผู้อนุมัติ** | nextzus |
| **บทบาท** | Project Owner / Lead Developer |
| **วันที่อนุมัติ** | 2026-01-20 |
| **สถานะการอนุมัติ** | `[accepted]` |

### 11. การปิด CR (Closure — PM.3.3)

| รายการ | รายละเอียด |
|--------|-----------|
| **วันที่ปิด** | 2026-02-28 |
| **สถานะการปิด** | `[closed]` — Implemented ใน Phase 10 |
| **หมายเหตุ** | ThemeManager class เสร็จสมบูรณ์, Settings view เพิ่มแล้ว |

---

## CR-004 — Security Audit & Test Expansion

### 1. ข้อมูลคำขอ (Request Information)

| รายการ | รายละเอียด |
|--------|-----------|
| **CR Number** | CR-004 |
| **Project** | ClutchG PC Optimizer v2.0 |
| **Change Name** | Security Audit & Test Expansion |
| **Date of Request** | 2026-03-12 |
| **Date Needed** | 2026-03-12 (ทำเสร็จวันเดียวกัน) |
| **Criticality** | HIGH |
| **Request Status** | `[closed]` |

### 2. ข้อมูลผู้ขอ (Requester Contact Information)

| รายการ | รายละเอียด |
|--------|-----------|
| **Requested by** | nextzus |
| **Role** | นักศึกษา / Developer |
| **Contact** | GitHub: nextzus |

### 3. วัตถุประสงค์ของการเปลี่ยนแปลง (Purpose of Change)

แก้ไขช่องโหว่ด้านความปลอดภัยที่ตรวจพบใน security audit ครอบคลุม 10 source files เพื่อให้โค้ดเหมาะสมกับระดับวิทยานิพนธ์ด้านความปลอดภัย ลบ dependency ที่ขัดแย้ง (GPUtil) และขยาย test coverage ให้ครอบคลุมกว่าเดิม

### 4. คำอธิบายการเปลี่ยนแปลง (Description of Change)

ดำเนินการ Security Audit ครบถ้วน 28 รายการครอบคลุม 10 source files เพื่อแก้ไขช่องโหว่ด้านความปลอดภัย ลบ dependency ที่ไม่จำเป็น (GPUtil) และขยาย unit test suite จาก 125 → 285 tests โดยเพิ่ม test files ใหม่ 5 ไฟล์

### 5. เหตุผลของการเปลี่ยนแปลง (Reason for Change)

- `batch_parser.py` ตรวจสอบ dangerous patterns ไม่ครอบคลุม (เดิม 3 patterns → เพิ่มเป็น 18 patterns)
- `admin.py` ใช้ string concatenation แทน `subprocess.list2cmdline()` — เสี่ยง command injection
- `batch_executor.py` ไม่ reset `_cancelled` flag ที่ start of execution — race condition
- `backup_manager.py` ไม่ sanitize restore point name — อาจ crash บน Windows
- GPUtil เป็น dependency ที่ไม่จำเป็นและขัดแย้งกับ Python 3.12+
- Coverage ของ safety modules ต่ำเกินไปสำหรับงานระดับวิทยานิพนธ์

### 6. ระบบที่ได้รับผลกระทบ (Impacted System(s))

| ระบบ | ผลกระทบ |
|------|---------|
| Core — Batch Parser (`batch_parser.py`) | เพิ่ม dangerous patterns, encoding fix |
| Core — Batch Executor (`batch_executor.py`) | wiring validator, race condition fix |
| Core — Backup Manager (`backup_manager.py`) | sanitize method, BackupInfo fix |
| Core — Flight Recorder (`flight_recorder.py`) | full rewrite (616 lines) |
| Core — Profile Manager (`profile_manager.py`) | duration tracking |
| Core — System Info (`system_info.py`) | storage strategy, GPUtil removed |
| Utils — Admin (`admin.py`) | list2cmdline, logger |
| GUI — Theme (`theme.py`) | TYPOGRAPHY alias |
| App — Main (`app_minimal.py`) | logger, print() removed |
| App — Help Manager (`help_manager.py`) | logger, print() removed |
| Test Suite (unit) | +5 new test files, +160 tests |
| Dependencies (`requirements.txt`) | GPUtil removed |

### 7. ผลต่อการทำงานของระบบปัจจุบัน (Impact to Operations of Existing System(s))

- การลบ GPUtil: `system_info.py` เปลี่ยนไปใช้ WMI + psutil แทน — ผลลัพธ์เหมือนเดิม แต่ compatibility ดีขึ้น
- Dangerous pattern detection เข้มข้นขึ้น: batch scripts ที่ไม่ปลอดภัยจะถูก reject แทนที่จะผ่านการตรวจสอบ — เป็น security improvement ที่ตั้งใจ
- `_cancelled` flag reset: eliminates race condition ที่อาจทำให้ execution ถูก skip
- ไม่มี breaking change ต่อ user-facing behavior

### 8. ผลต่อเอกสารที่เกี่ยวข้อง (Impact to Associated Documentation)

| เอกสาร | เวอร์ชัน | รายละเอียดการเปลี่ยนแปลง |
|--------|---------|------------------------|
| SDD | v3.0 → v3.1 | FlightRecorder LOC updated, storage strategy updated, GPUtil removed |
| Test Plan | v2.0 → v2.1 | Test Pyramid counts updated, 5 new UT sections added |
| Test Record | v3.0 → v3.1 | 5 new test sections (§2.8–§2.12) added |
| Traceability Record | v2.0 → v2.1 | §2.1 updated (12 unit test files), coverage 59.6% → 88.1% |
| Project Plan | v2.0 → v2.1 | Phase 11a added, Q-09 quality criterion added |
| Configuration Plan | v2.0 → v2.1 | CI-TEST-02 updated, BL-9 added |
| Progress Status | v2.2 → v2.3 | Phase 11a added, quality metrics updated |

### 9. Security Audit Items (28/28 Resolved)

| # | Module | รายการแก้ไข | ประเภท |
|---|--------|------------|--------|
| 1–18 | `batch_parser.py` | เพิ่ม 15 dangerous patterns (cmd injection, powershell bypass, etc.), utf-8 encoding | Security |
| 19–21 | `admin.py` | `subprocess.list2cmdline()`, เพิ่ม logger, ลบ `print()` | Security |
| 22–24 | `batch_executor.py` | wiring validator, reset `_cancelled` ที่ start, thread join timeout | Correctness |
| 25–26 | `backup_manager.py` | `_sanitize_restore_point_name()`, `BackupInfo._success` field + `success` property | Robustness |
| 27 | `profile_manager.py` | เพิ่ม `time.time()` duration tracking | Quality |
| 28 | `theme.py` | `TYPOGRAPHY = FONTS` alias แทน duplicate | Maintainability |
| — | `flight_recorder.py` | Rewrite ครบถ้วน 616 lines (เดิม 589) | Quality |
| — | `system_info.py` | 3-strategy storage detection, ลบ GPUtil | Robustness |
| — | `app_minimal.py`, `help_manager.py` | `print()` → logger | Quality |

### 10. Test Files Added

| ไฟล์ | จำนวน Tests | หมายเหตุ |
|------|------------|---------|
| `clutchg/tests/unit/test_admin.py` | 16 | NEW |
| `clutchg/tests/unit/test_backup_manager.py` | 35 | NEW |
| `clutchg/tests/unit/test_flight_recorder.py` | 36 | NEW |
| `clutchg/tests/unit/test_tweak_registry_integrity.py` | 61 | NEW |
| `clutchg/tests/unit/test_help_system.py` | 12 | MOVED from root |
| `clutchg/tests/unit/test_core_coverage.py` | 1 | Regression fix |
| **รวม unit tests** | **285** | เดิม 125 (+160) |
| **รวม integration tests** | **23** | ไม่เปลี่ยน |
| **รวม E2E tests** | **64** | ไม่เปลี่ยน |
| **รวมทั้งหมด** | **372** | เดิม 212 (+160) |

### 11. การวิเคราะห์ผลกระทบ (Impact Analysis — PM.2.2)

| มิติ | การประเมิน |
|------|-----------|
| **ผลกระทบทางเทคนิค** | สูง — แก้ไข 10 source files, rewrite flight_recorder.py, เปลี่ยน dependency strategy |
| **ผลกระทบต่อกำหนดการ** | ไม่กระทบ — ดำเนินการภายใน Phase 11 (Documentation) ตามแผน |
| **ผลกระทบต่อต้นทุน** | ไม่มี — งานทั้งหมดอยู่ใน scope โครงงานวิทยานิพนธ์ |

### 12. การอนุมัติ (Acceptance — PM.2.3)

| รายการ | รายละเอียด |
|--------|-----------|
| **ผู้อนุมัติ** | nextzus |
| **บทบาท** | Project Owner / Lead Developer |
| **วันที่อนุมัติ** | 2026-03-12 |
| **สถานะการอนุมัติ** | `[accepted]` |

### 13. การปิด CR (Closure — PM.3.3)

| รายการ | รายละเอียด |
|--------|-----------|
| **วันที่ปิด** | 2026-03-12 |
| **สถานะการปิด** | `[closed]` — Security audit และ test expansion เสร็จสมบูรณ์ |
| **หมายเหตุ** | ทั้ง 28 security items resolved, test count 125 → 285, GPUtil dependency removed |

---

## สรุปค่าใช้จ่ายแรงงาน (Effort Estimation Summary)

| CR No. | ชื่อ | ระดับ | ชั่วโมงประมาณการ | ชั่วโมงจริง | Phase | หมายเหตุ |
|--------|------|-------|-----------------|------------|-------|---------|
| CR-001 | Unified Backup & Restore Center | MEDIUM | 40 | 38 | Phase 9 | UI refactor, timeline component |
| CR-002 | Export/Import Presets | LOW | 8 | 6 | Phase 10 | 2 methods เพิ่มใน profile_manager |
| CR-003 | Multi-Theme System | LOW | 24 | 22 | Phase 10 | ThemeManager class + Settings view |
| CR-004 | Security Audit & Test Expansion | HIGH | 48 | 44 | Phase 11 | 28 audit items + 160 new tests |
| | **รวม** | | **120** | **110** | | Variance = −10 hrs (ดีกว่าประมาณการ 8.3%) |

> **หมายเหตุ:** ค่าประมาณการคำนวณจาก expert judgment ร่วมกับ historical data ของโครงงาน ส่วนชั่วโมงจริงบันทึกผ่าน flight recorder log และ git commit timestamps

---

## ตารางเชื่อมโยง CR กับ Functional Requirements (CR-to-FR Traceability)

| CR No. | FR ที่ได้รับผลกระทบ | ประเภทผลกระทบ | เอกสารอ้างอิง |
|--------|---------------------|---------------|--------------|
| CR-001 | FR-BK-01 (Create Backup), FR-BK-02 (Restore Backup), FR-BK-03 (Timeline View), FR-BK-04 (Per-tweak Rollback) | Modified / Added | SRS v3.1 §3.6 |
| CR-002 | FR-PM-06 (Export/Import Presets) | Added | SRS v3.1 §3.4 |
| CR-003 | FR-UI-06 (Multi-Theme Support), FR-UI-07 (Accent Color Selection) | Added | SRS v3.1 §3.7 |
| CR-004 | FR-SF-01 (Dangerous Pattern Detection), FR-SF-02 (Input Sanitization), NFR-SE-01 (Security Hardening) | Modified / Strengthened | SRS v3.1 §3.8, §4.2 |

| สรุป | จำนวน |
|------|-------|
| FR ที่ถูกเพิ่มใหม่ (Added) | 5 |
| FR ที่ถูกแก้ไข (Modified) | 4 |
| FR ที่ถูกลบ (Removed) | 0 |
| NFR ที่ได้รับผลกระทบ | 1 |
| **รวม Requirements ที่เกี่ยวข้อง** | **10** |

> **Cross-reference:** ดูรายละเอียด Forward/Backward Traceability ใน `06-Traceability-Record.md` v2.0 §3–§4

---

## ประวัติการแก้ไขเอกสาร (Revision History)

| เวอร์ชัน | วันที่ | ผู้แก้ไข | รายละเอียด |
|----------|--------|---------|-----------|
| v1.0 | 2025-09-30 | nextzus | สร้างเอกสารเริ่มต้น พร้อม CR-001 |
| v2.0 | 2026-03-12 | nextzus | เพิ่ม CR-002, CR-003, CR-004, อัปเดตตารางสรุป |
| v2.1 | 2026-04-06 | nextzus | เพิ่มกระบวนการ CCB (SE 702), ตาราง Effort Estimation, CR-to-FR Traceability, ETVX header |
