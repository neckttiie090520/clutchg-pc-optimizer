# 06 — บันทึกความสอดคล้อง (Traceability Record)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O3 (Software Traceability)
> **เวอร์ชัน:** 2.0
> **ETVX:** Entry = SRS v3.1 + SDD v3.2 approved; Task = Map FR→Design→Code→Test for all requirements; Verification = Coverage ≥ 85%; Exit = All P0 FRs traced, gaps documented
> **อ้างอิง SE:** SE 721 (Requirements Engineering — Traceability), SE 725 (V&V — Requirements-based Testing)
> **Cross-ref:** SRS v3.1 (`02-SRS.md`), SDD v3.2 (`03-SDD.md`), Test Plan v3.0 (`04-Test-Plan.md`), Test Record v2.1 (`05-Test-Record.md`)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **วันที่:** 2026-03-12 | **ผู้จัดทำ:** nextzus

---

## ทฤษฎี Traceability (SE 721)

Requirements Traceability คือความสามารถในการติดตามความสัมพันธ์ระหว่าง requirement กับ work products อื่นตลอดวงจรชีวิตซอฟต์แวร์ แบ่งเป็น 3 ประเภท:

| ประเภท | ทิศทาง | จุดประสงค์ | ส่วน |
|--------|--------|-----------|------|
| **Forward Traceability** | FR → Design → Code → Test | ตรวจว่า requirement ทุกข้อถูก implement และทดสอบ | §1 |
| **Backward Traceability** | Test → Code → Design → FR | ตรวจว่า test/code ทุกชิ้นมี requirement รองรับ (ไม่มี gold plating) | §2 |
| **Horizontal Traceability** | SRS ↔ SDD ↔ Test Plan ↔ Test Record | ตรวจความสอดคล้องระหว่างเอกสาร ISO 29110 | §4 |

> **หลักการ:** Traceability ที่ดีต้องติดตามได้ทั้งสองทิศทาง (bi-directional) และข้ามเอกสาร (horizontal) เพื่อให้มั่นใจว่าไม่มี requirement ที่ตกหล่นและไม่มี code ที่ไม่จำเป็น

---

## 1. Forward Traceability: Requirements → Design → Code → Test

### 1.1 FR-SD: System Detection

| FR | Component (SDD) | Source File (Line) | Test Case |
|----|-----------------|-------------------|-----------|
| FR-SD-01 CPU detection | SystemDetector | `core/system_info.py` L172-222 | UT-SD-01 |
| FR-SD-02 GPU detection | SystemDetector | `core/system_info.py` L224-283 | UT-SD-02 |
| FR-SD-03 RAM detection | SystemDetector | `core/system_info.py` L285-303 | UT-SD-03 |
| FR-SD-04 Storage detection | SystemDetector | `core/system_info.py` L305-334 | — |
| FR-SD-05 System score | SystemDetector | `core/system_info.py` L115-148 | UT-SD-04, UT-BM-01~05 |
| FR-SD-06 Tier classification | SystemDetector | `core/system_info.py` L349-358 | UT-SD-05 |
| FR-SD-07 Profile recommendation | SystemDetector | `core/system_info.py` L360-380 | — |
| FR-SD-08 Form factor | SystemDetector | `core/system_info.py` L336-347 | UT-SD-06 |
| FR-SD-09 Async detection | ClutchGApp | `app_minimal.py` L117-145 | — |

### 1.2 FR-PM: Profile Management

| FR | Component | Source File (Line) | Test Case |
|----|-----------|-------------------|-----------|
| FR-PM-01 3 preset profiles | ProfileManager | `core/profile_manager.py` L61-128 | UT-PM-01 |
| FR-PM-02 SAFE = 17 tweaks | TweakRegistry | `core/tweak_registry.py` (preset_safe) | UT-PM-02 |
| FR-PM-03 COMPETITIVE = 35 | TweakRegistry | `core/tweak_registry.py` (preset_competitive) | UT-PM-03 |
| FR-PM-04 EXTREME = 48 | TweakRegistry | `core/tweak_registry.py` (preset_extreme) | UT-PM-04 |
| FR-PM-05 Risk + FPS display | Profile dataclass | `core/profile_manager.py` L28-40 | UT-PM-05 |
| FR-PM-06 Apply profile workflow | ProfileManager | `core/profile_manager.py` L146-257 | IT-CI-01 |
| FR-PM-07 Per-tweak progress | ProfileManager | `core/profile_manager.py` L284-419 | — |
| FR-PM-08 Custom presets | ProfileManager | `core/profile_manager.py` L421-451 | UT-PM-06 |
| FR-PM-09 Export preset JSON | ProfileManager | `core/profile_manager.py` L453-490 | — |
| FR-PM-10 Import preset JSON | ProfileManager | `core/profile_manager.py` L492-527 | — |
| FR-PM-11 Verify scripts | ProfileManager | `core/profile_manager.py` L263-278 | UT-PM-07 |

### 1.3 FR-TW: Tweak Registry

| FR | Component | Source File (Line) | Test Case |
|----|-----------|-------------------|-----------|
| FR-TW-01 48 tweaks registry | TweakRegistry | `core/tweak_registry.py` L884-1012 | UT-AC-01 |
| FR-TW-02 17 fields per tweak | Tweak dataclass | `core/tweak_registry.py` L13-36 | UT-AC-02 |
| FR-TW-03 10 categories | TWEAK_CATEGORIES | `core/tweak_registry.py` L39-51 | E2E-SCR-01 |
| FR-TW-04 Filter by category | TweakRegistry | `core/tweak_registry.py` L899-933 | — |
| FR-TW-05 Risk distribution | TweakRegistry | `core/tweak_registry.py` L968-973 | — |
| FR-TW-06 Suggest preset | TweakRegistry | `core/tweak_registry.py` L935-959 | — |
| FR-TW-07 Build custom preset | TweakRegistry | `core/tweak_registry.py` L975-1001 | — |

### 1.4 FR-SF: Safety & Rollback

| FR | Component | Source File (Line) | Test Case |
|----|-----------|-------------------|-----------|
| FR-SF-01 Auto backup | BackupManager | `core/backup_manager.py` L73-140 | IT-BR-01 |
| FR-SF-02 6 registry key backup | BackupManager | `core/backup_manager.py` L209-248 | IT-BR-01 |
| FR-SF-03 Restore point | BackupManager | `core/backup_manager.py` L142-207 | IT-BR-02 |
| FR-SF-04 Max 10 backups | BackupManager | `core/backup_manager.py` L261-281 | — |
| FR-SF-05 TweakChange recording | FlightRecorder | `core/flight_recorder.py` L198-256 | IT-FR-01 |
| FR-SF-06 SystemSnapshot | FlightRecorder | `core/flight_recorder.py` L79-123 | IT-FR-01 |
| FR-SF-07 Per-tweak rollback | FlightRecorder | `core/flight_recorder.py` L521-540 | IT-FR-02 |
| FR-SF-08 Snapshot rollback | FlightRecorder | `core/flight_recorder.py` L411-463 | IT-FR-03 |
| FR-SF-09 Generate .bat script | FlightRecorder | `core/flight_recorder.py` L411-463 | IT-FR-03 |
| FR-SF-10 List 50 snapshots | FlightRecorder | `core/flight_recorder.py` L360-383 | — |
| FR-SF-11 Compare snapshots | FlightRecorder | `core/flight_recorder.py` L385-409 | — |
| FR-SF-12 Cleanup >30 days | FlightRecorder | `core/flight_recorder.py` L542-570 | — |
| FR-SF-13 Never-Disable policy | Safety Policy | ไม่มีในโค้ด (by design) | Manual |

### 1.5 FR-UI: User Interface

| FR | Component | Source File | Test Case |
|----|-----------|------------|-----------|
| FR-UI-01 Dashboard | DashboardView | `gui/views/dashboard_minimal.py` | E2E-NAV-01 |
| FR-UI-02 Profiles | ProfilesView | `gui/views/profiles_minimal.py` | E2E-PRF-01 |
| FR-UI-03 Scripts | ScriptsView | `gui/views/scripts_minimal.py` | E2E-SCR-01 |
| FR-UI-04 Backup Center | BackupRestoreCenter | `gui/views/backup_restore_center.py` | E2E-NAV-04 |
| FR-UI-05 Help | HelpView + HelpMgr | `gui/views/help_minimal.py` | IT-HS-01~02 |
| FR-UI-06 Settings | SettingsView | `gui/views/settings_minimal.py` | E2E-SET-01~03, IT-CI-02~03 |
| FR-UI-07 Welcome | WelcomeOverlay | `gui/views/welcome_overlay.py` | — |
| FR-UI-08 Risk Badge | RiskBadge | `gui/components/risk_badge.py` | E2E-PRF-02 |
| FR-UI-09 Toast | ToastManager | `gui/components/toast.py` | — |
| FR-UI-10 Sidebar | EnhancedSidebar | `gui/components/enhanced_sidebar.py` | E2E-NAV-07 |
| FR-UI-11 Transition | ViewTransition | `gui/components/view_transition.py` | E2E-NAV-08 |
| FR-UI-12 Execution Dialog | ExecutionDialog | `gui/components/execution_dialog.py` | — |
| FR-UI-13 Context Help | ContextHelpButton | `gui/components/context_help_button.py` | — |

### 1.6 FR-BS: Batch Script Execution

| FR | Component | Source File | Test Case |
|----|-----------|------------|-----------|
| FR-BS-01 Parse scripts | BatchParser | `core/batch_parser.py` | UT-BP-01~06 |
| FR-BS-02 Execute with Admin | BatchExecutor | `core/batch_executor.py` | IT-CI-01 |
| FR-BS-03 Real-time output | BatchExecutor | `core/batch_executor.py` | — |
| FR-BS-04 Validate before exec | ProfileManager | `core/profile_manager.py` L263-278 | UT-PM-07 |

---

## 2. Backward Traceability: Test → Code → Design → Requirement

### 2.1 Unit Tests → Requirements

| Test File | Tests | FRs Covered |
|-----------|-------|-------------|
| test_profile_manager.py | 11 | FR-PM-01~05, FR-PM-08, FR-PM-11 |
| test_batch_parser.py | 18 | FR-BS-01, FR-BS-04 |
| test_system_detection.py | 12 | FR-SD-01~03, FR-SD-05~06, FR-SD-08 |
| test_action_catalog.py | 5 | FR-TW-01~04 |
| test_benchmark_database.py | 22 | FR-SD-05 |
| test_execution_dialog.py | 3 | FR-UI-12 |
| test_core_coverage.py | 54 | FR-PM-06, FR-SD-07, FR-BS-02, FR-SF-05~08, FR-UI-05~06 |
| test_admin.py | 16 | FR-AD-01~02, FR-SF-13 |
| test_backup_manager.py | 35 | FR-SF-01~04 |
| test_flight_recorder.py | 36 | FR-SF-05~12 |
| test_tweak_registry_integrity.py | 61 | FR-TW-01~07, FR-SF-13, NFR-01~03 |
| test_help_system.py | 12 | FR-UI-05, FR-UI-08, NFR-06, NFR-08 |

### 2.2 Integration Tests → Requirements

| Test File | Tests | FRs Covered |
|-----------|-------|-------------|
| test_backup_restore.py | 3 | FR-SF-01~04 |
| test_clutchg_integration.py | 2 | FR-PM-06 |
| test_config_integration.py | 2 | FR-UI-06 |
| test_flight_recorder_integration.py | 3 | FR-SF-05~09 |
| test_help_system_integration.py | 2 | FR-UI-05, NFR-06 |

---

## 3. สรุปความครอบคลุม (Coverage Summary)

### 3.1 Requirements Coverage

| Group | Total FRs | With Test | Without Test | Coverage |
|-------|----------|----------|-------------|---------|
| FR-SD (System Detection) | 9 | 7 | 2 | 77.8% |
| FR-PM (Profile Mgmt) | 11 | 9 | 2 | 81.8% |
| FR-TW (Tweak Registry) | 7 | 7 | 0 | 100.0% |
| FR-SF (Safety/Rollback) | 13 | 13 | 0 | 100.0% |
| FR-UI (User Interface) | 13 | 10 | 3 | 76.9% |
| FR-BS (Batch Scripts) | 4 | 4 | 0 | 100.0% |
| FR-AD (Admin Utilities) | 2 | 2 | 0 | 100.0% |
| **รวม** | **59** | **52** | **7** | **88.1%** |

> **หมายเหตุ:** FR-AD เป็น requirement ที่เพิ่มขึ้นโดยนัยจาก Security Audit (CR-004)
> ตัวเลขปรับจาก 57 → 59 FRs (เพิ่ม FR-AD-01, FR-AD-02)

### 3.2 FRs Without Automated Tests

| FR | เหตุผล | ทดสอบวิธีอื่น |
|----|-------|-------------|
| FR-SD-04 Storage | Hardware-dependent | Manual |
| FR-SD-09 Async | Threading timing | Manual observation |
| FR-PM-09 Export preset | File I/O | Manual |
| FR-PM-10 Import preset | File I/O + validation | Manual |
| FR-UI-07 Welcome | UI component | Visual + E2E |
| FR-UI-09 Toast | UI component | Visual + E2E |
| FR-UI-11 Transition | UI component | Visual + E2E |

### 3.3 NFR Coverage

| NFR | ทดสอบได้ | วิธีทดสอบ |
|-----|---------|---------|
| NFR-01 Never disable security | Yes | Code review + grep |
| NFR-02 HIGH risk warnings ≥2 | Yes | Unit test on registry |
| NFR-03 Reversible | Yes | Check reversible=True |
| NFR-14 Coverage ≥ 70% | Yes | pytest-cov |
| NFR-05~07 Usability | Partial | Manual UX test |
| NFR-08 Async UI | Partial | Observation |

---

## 4. Horizontal Traceability: ความสอดคล้องระหว่างเอกสาร ISO 29110

> ตรวจว่าข้อมูลที่ปรากฏในเอกสาร ISO หนึ่งสอดคล้องกับเอกสาร ISO อื่นที่อ้างอิงข้อมูลเดียวกัน

| รายการตรวจ | เอกสารต้นทาง | เอกสารปลายทาง | สอดคล้อง? | หมายเหตุ |
|-----------|-------------|--------------|-----------|---------|
| จำนวน FR ทั้งหมด | SRS: 63 FRs (MoSCoW) | Traceability: 59 FRs | ⚠️ ต่าง | SRS นับรวม Won't=5 + admin FRs ที่เพิ่มภายหลัง — ตัวเลข reconcile ได้ |
| จำนวน NFR | SRS: 17 NFRs | Test Plan: 17 NFRs | ✅ ตรง | |
| จำนวน Test Cases | Test Plan: 308 planned | Test Record: 308 executed | ✅ ตรง | |
| Coverage target | Test Plan: ≥ 60% core | Test Record: ~65% core | ✅ ผ่าน | |
| DRE target | Test Plan: ≥ 85% | Test Record: 100% (pre-release) | ✅ ผ่าน | |
| 10 Risk items | Project Plan: 10 risks | Progress Status: 10 risks | ✅ ตรง | 8 resolved, 2 monitoring |
| 3 Profiles | SRS: SAFE/COMPETITIVE/EXTREME | SDD: 3 profiles in architecture | ✅ ตรง | |
| Tweak count | SRS: 48 tweaks | SDD: 48 tweaks in registry | ✅ ตรง | |
| Change Requests | CR-001~004 | Traceability: CR impacts traced | ✅ ตรง | |
| Architecture pattern | SDD: Layered + MVC hybrid | Test Plan: test by layer | ✅ ตรง | |

### 4.1 Cross-Document Version Alignment

| เอกสาร | เวอร์ชันปัจจุบัน | อ้างอิงใน Traceability Record |
|--------|----------------|------------------------------|
| SRS | v3.1 | ✅ อ้างอิงถูกต้อง |
| SDD | v3.2 | ✅ อ้างอิงถูกต้อง |
| Test Plan | v3.0 | ✅ อ้างอิงถูกต้อง |
| Test Record | v2.1 | ✅ อ้างอิงถูกต้อง |

---

## 5. Consolidated RTM Summary

| Metric | ค่า | เป้าหมาย | สถานะ |
|--------|-----|---------|-------|
| Total FRs traced | 52/59 | ≥ 85% | ✅ 88.1% |
| FRs with automated tests | 52 | — | |
| FRs with manual tests only | 7 | ≤ 10 | ✅ |
| NFRs testable | 4/6 groups | — | ⚠️ Partial (usability/async = manual) |
| Horizontal consistency issues | 1 minor (FR count reconciliation) | 0 critical | ✅ |
| Gold plating detected | 0 | 0 | ✅ ไม่มี code ที่ไม่มี FR รองรับ |

> **สรุป:** ระบบ traceability ของ ClutchG ครอบคลุม 88.1% ของ FRs ด้วย automated tests ส่วนที่เหลือ 7 FRs มีการทดสอบด้วยวิธี manual ทั้งหมด ไม่พบ gold plating

---

## 6. ประวัติการแก้ไข (Revision History)

| เวอร์ชัน | วันที่ | ผู้แก้ไข | รายละเอียด |
|----------|--------|---------|------------|
| 1.0 | 2026-03-12 | nextzus | สร้างเอกสารเริ่มต้น — Forward/Backward traceability, coverage summary |
| 2.0 | 2026-04-06 | nextzus | เสริม SE academic content: ทฤษฎี Traceability (SE 721), §4 Horizontal Traceability, §5 Consolidated RTM Summary, header ETVX + cross-refs |
